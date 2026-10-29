"""Chatterbox Multilingual (Resemble AI) - MIT, gratuito, clonagem zero-shot.

Parametros uteis (passe via config ou --opcao):
  exaggeration  0.3-0.7  expressividade (0.5 neutro; narracao: 0.4-0.5)
  cfg_weight    0.3-0.6  aderencia ao texto/ritmo (0.5 padrao; mais baixo = mais expressivo)
  temperature   0.6-0.9  variacao (0.8 padrao)
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path

from ..util import ErroNarrador, console
from .base import MotorTTS, VozReferencia

REPO_BASE = "ResembleAI/chatterbox"
ARQUIVOS_BASE = [
    "ve.pt", "t3_mtl23ls_v2.safetensors", "s3gen.pt",
    "grapheme_mtl_merged_expanded_v1.json", "conds.pt", "Cangjie5_TC.json",
]


class MotorChatterbox(MotorTTS):
    nome = "chatterbox"

    def __init__(self, voz: VozReferencia | None, pacote: str | None = None, **opcoes):
        super().__init__(voz, **opcoes)
        self.pacote = pacote
        if pacote:
            self.nome = "chatterbox-ptbr" if "pt-br" in pacote.lower() else f"chatterbox:{pacote}"
        self.exaggeration = float(self.opcoes.get("exaggeration", 0.45))
        self.cfg_weight = float(self.opcoes.get("cfg_weight", 0.5))
        self.temperature = float(self.opcoes.get("temperature", 0.75))
        self.repetition_penalty = float(self.opcoes.get("repetition_penalty", 1.6))
        self.modelo = None

    def carregar(self) -> None:
        try:
            from chatterbox.mtl_tts import ChatterboxMultilingualTTS
        except ImportError as e:
            raise ErroNarrador(
                "chatterbox-tts nao instalado. Rode: pip install chatterbox-tts\n"
                "(Python 3.10-3.12 recomendado; em CPU a sintese e lenta, ~5-15x tempo real.)"
            ) from e

        if self.pacote:
            self.modelo = ChatterboxMultilingualTTS.from_local(self._montar_pacote(), self.dispositivo)
        else:
            try:
                # Versoes recentes (GitHub) aceitam t3_model="v3"; a do PyPI 0.1.7 nao.
                self.modelo = ChatterboxMultilingualTTS.from_pretrained(device=self.dispositivo, t3_model="v3")
            except TypeError:
                self.modelo = ChatterboxMultilingualTTS.from_pretrained(self.dispositivo)
        self.taxa_amostragem = int(getattr(self.modelo, "sr", 24000))

    def _montar_pacote(self) -> Path:
        """Combina o checkpoint base com o pacote de idioma num diretorio local.

        O pacote pt-BR publica t3_pt_br.safetensors (+ s3gen_v3 e vocabulario);
        `from_local` espera nomes fixos, entao criamos links com os nomes esperados.
        """
        from huggingface_hub import snapshot_download

        token = os.getenv("HF_TOKEN")
        base = Path(snapshot_download(REPO_BASE, allow_patterns=ARQUIVOS_BASE, token=token))
        pack = Path(snapshot_download(self.pacote, token=token))
        destino = Path(os.getenv("NARRADOR_CACHE", Path.home() / ".cache" / "narrador")) / "chatterbox" / self.pacote.replace("/", "__")
        destino.mkdir(parents=True, exist_ok=True)

        def ligar(origem: Path, nome: str) -> None:
            alvo = destino / nome
            if alvo.exists() or alvo.is_symlink():
                alvo.unlink()
            try:
                os.symlink(origem, alvo)
            except OSError:
                shutil.copy2(origem, alvo)

        for nome in ARQUIVOS_BASE:
            if (base / nome).exists():
                ligar(base / nome, nome)
        # sobrescreve com os arquivos do pacote
        t3 = sorted(pack.glob("t3_*.safetensors"))
        if not t3:
            raise ErroNarrador(f"O pacote {self.pacote} nao contem um checkpoint t3_*.safetensors.")
        ligar(t3[0], "t3_mtl23ls_v2.safetensors")
        for cand in ("s3gen_v3.pt", "s3gen.pt"):
            if (pack / cand).exists():
                ligar(pack / cand, "s3gen.pt")
                break
        if (pack / "grapheme_mtl_merged_expanded_v1.json").exists():
            ligar(pack / "grapheme_mtl_merged_expanded_v1.json", "grapheme_mtl_merged_expanded_v1.json")
        if (pack / "conds.pt").exists():
            ligar(pack / "conds.pt", "conds.pt")
        console.print(f"[dim]pacote de idioma montado em {destino}[/]")
        return destino

    def sintetizar(self, texto: str, destino: Path) -> Path:
        self.garantir_carregado()
        wav = self.modelo.generate(
            texto,
            language_id=self.idioma,
            audio_prompt_path=str(self.voz.audio),
            exaggeration=self.exaggeration,
            cfg_weight=self.cfg_weight,
            temperature=self.temperature,
            repetition_penalty=self.repetition_penalty,
        )
        dados = wav.detach().cpu().numpy() if hasattr(wav, "detach") else wav
        return self._salvar(destino, dados, self.taxa_amostragem)

    def identidade(self) -> str:
        return super().identidade() + f"|{self.pacote}|{self.exaggeration}|{self.cfg_weight}|{self.temperature}"
