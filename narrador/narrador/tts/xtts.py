"""Coqui XTTS v2 via fork mantido `coqui-tts` (licenca CPML: uso nao comercial)."""

from __future__ import annotations

import os
from pathlib import Path

from ..util import ErroNarrador
from .base import MotorTTS, VozReferencia


class MotorXTTS(MotorTTS):
    nome = "xtts"

    def __init__(self, voz: VozReferencia | None, **opcoes):
        super().__init__(voz, **opcoes)
        self.modelo = None

    def carregar(self) -> None:
        os.environ.setdefault("COQUI_TOS_AGREED", "1")
        try:
            from TTS.api import TTS
        except ImportError as e:
            raise ErroNarrador("coqui-tts nao instalado. Rode: pip install coqui-tts") from e
        self.modelo = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(self.dispositivo)
        self.taxa_amostragem = 24000

    def sintetizar(self, texto: str, destino: Path) -> Path:
        self.garantir_carregado()
        destino.parent.mkdir(parents=True, exist_ok=True)
        self.modelo.tts_to_file(
            text=texto,
            speaker_wav=str(self.voz.audio),
            language=self.idioma,
            file_path=str(destino),
            split_sentences=False,
        )
        return destino
