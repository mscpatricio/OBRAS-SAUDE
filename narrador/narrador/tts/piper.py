"""Piper TTS: vozes neurais pt-BR offline, leves (ONNX, roda em CPU), SEM clonagem.

Serve para gerar o video com voz real em segundos, sem GPU e sem internet
(depois de baixar a voz uma vez). Vozes pt-BR: pt_BR-faber-medium (padrao),
pt_BR-cadu-medium, pt_BR-jeff-medium, pt_BR-edresson-low.

Opcoes: -o voz_piper=pt_BR-cadu-medium  -o velocidade=1.0 (menor = mais rapido)
"""

from __future__ import annotations

import os
import wave
from pathlib import Path

from ..util import ErroNarrador, console
from .base import MotorTTS, VozReferencia

VOZ_PADRAO = "pt_BR-faber-medium"


class MotorPiper(MotorTTS):
    nome = "piper"
    precisa_clonagem = False

    def __init__(self, voz: VozReferencia | None, **opcoes):
        super().__init__(voz, **opcoes)
        self.voz_piper = str(self.opcoes.get("voz_piper", VOZ_PADRAO))
        self.velocidade = float(self.opcoes.get("velocidade", 1.0))
        self.modelo = None

    def carregar(self) -> None:
        try:
            from piper import PiperVoice
            from piper.download_voices import download_voice
        except ImportError as e:
            raise ErroNarrador("piper-tts nao instalado. Rode: pip install piper-tts") from e
        pasta = Path(os.getenv("NARRADOR_CACHE", Path.home() / ".cache" / "narrador")) / "piper"
        pasta.mkdir(parents=True, exist_ok=True)
        onnx = pasta / f"{self.voz_piper}.onnx"
        if not onnx.exists() or onnx.stat().st_size < 1_000_000:
            console.print(f"[cyan]Baixando voz Piper {self.voz_piper} (~60 MB)...[/]")
            download_voice(self.voz_piper, pasta)
        if not onnx.exists() or onnx.stat().st_size < 1_000_000:
            raise ErroNarrador(f"Nao foi possivel baixar a voz {self.voz_piper}. "
                               "Veja as vozes pt_BR em https://huggingface.co/rhasspy/piper-voices")
        self.modelo = PiperVoice.load(onnx)
        self.taxa_amostragem = int(self.modelo.config.sample_rate)

    def sintetizar(self, texto: str, destino: Path) -> Path:
        self.garantir_carregado()
        from piper.config import SynthesisConfig

        destino.parent.mkdir(parents=True, exist_ok=True)
        cfg = SynthesisConfig(length_scale=self.velocidade)
        with wave.open(str(destino), "wb") as w:
            self.modelo.synthesize_wav(texto, w, syn_config=cfg)
        return destino

    def identidade(self) -> str:
        return f"piper|{self.voz_piper}|{self.velocidade}"
