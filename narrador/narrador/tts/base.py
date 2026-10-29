"""Interface comum dos motores de TTS."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from ..util import ErroNarrador, console


@dataclass
class VozReferencia:
    """Amostra da voz a ser clonada.

    audio: wav mono (ideal 24 kHz, 6-15 s, fala limpa).
    transcricao: texto exato do que e dito no audio. Opcional para Chatterbox/XTTS,
                 recomendado para Qwen3 e F5 (melhora muito a similaridade).
    """

    audio: Path
    transcricao: str = ""

    @classmethod
    def de_arquivo(cls, audio: Path, transcricao: Path | str | None = None) -> "VozReferencia":
        audio = Path(audio)
        if not audio.exists():
            raise ErroNarrador(f"Audio de referencia da voz nao encontrado: {audio}")
        texto = ""
        if transcricao is None:
            candidato = audio.with_suffix(".txt")
            if candidato.exists():
                texto = candidato.read_text(encoding="utf-8").strip()
        elif isinstance(transcricao, Path) or (isinstance(transcricao, str) and os.path.exists(transcricao)):
            texto = Path(transcricao).read_text(encoding="utf-8").strip()
        else:
            texto = str(transcricao).strip()
        return cls(audio=audio, transcricao=texto)


def detectar_dispositivo(preferido: str | None = None) -> str:
    if preferido and preferido != "auto":
        return preferido
    try:
        import torch

        if torch.cuda.is_available():
            return "cuda"
        if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
            return "mps"
    except Exception:
        pass
    return "cpu"


class MotorTTS:
    """Contrato: `sintetizar(texto, destino)` grava um WAV e devolve o caminho."""

    nome = "base"
    precisa_clonagem = True
    taxa_amostragem = 24000

    def __init__(self, voz: VozReferencia | None, dispositivo: str = "auto", idioma: str = "pt", **opcoes):
        self.voz = voz
        self.dispositivo = detectar_dispositivo(dispositivo)
        self.idioma = idioma
        self.opcoes = opcoes
        self._carregado = False
        if self.precisa_clonagem and voz is None:
            raise ErroNarrador(f"O motor '{self.nome}' precisa de um audio de referencia (--voz).")

    def carregar(self) -> None:  # pragma: no cover - sobrescrito
        self._carregado = True

    def garantir_carregado(self) -> None:
        if not self._carregado:
            console.print(f"[cyan]Carregando motor de voz '{self.nome}' em {self.dispositivo}...[/]")
            self.carregar()
            self._carregado = True

    def sintetizar(self, texto: str, destino: Path) -> Path:  # pragma: no cover
        raise NotImplementedError

    def identidade(self) -> str:
        """Usado no cache: muda se mudar motor, voz ou parametros."""
        partes = [self.nome, self.idioma, repr(sorted(self.opcoes.items()))]
        if self.voz:
            partes.append(str(self.voz.audio.resolve()))
            partes.append(self.voz.transcricao)
        return "|".join(partes)

    @staticmethod
    def _salvar(destino: Path, dados: np.ndarray, sr: int) -> Path:
        import soundfile as sf

        destino.parent.mkdir(parents=True, exist_ok=True)
        dados = np.asarray(dados, dtype=np.float32).squeeze()
        if dados.ndim > 1:
            dados = dados.mean(axis=0)
        sf.write(str(destino), np.clip(dados, -1, 1), sr, subtype="PCM_16")
        return destino


class MotorSilencio(MotorTTS):
    """Gera silencio com duracao proporcional ao texto (~15 caracteres/segundo)."""

    nome = "silencio"
    precisa_clonagem = False

    def sintetizar(self, texto: str, destino: Path) -> Path:
        seg = max(0.6, len(texto) / 15.0)
        return self._salvar(destino, np.zeros(int(seg * self.taxa_amostragem)), self.taxa_amostragem)
