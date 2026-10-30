"""Fish Audio (API online). Plano gratuito com clonagem no site (confira limites em fish.audio).

1. Crie a voz em fish.audio (Voice Clone, 15-30 s de audio) e copie o ID do modelo.
2. Gere uma chave de API em fish.audio (Developers / API keys).
3. export FISH_AUDIO_API_KEY=...  FISH_VOICE_ID=...

Opcoes: -o modelo=s2.1-pro-free | s2.1-pro | s1  (modelo do cabecalho "model")
"""

from __future__ import annotations

import os
from pathlib import Path

import requests

from ..util import ErroNarrador, ffmpeg
from .base import MotorTTS, VozReferencia


class MotorFish(MotorTTS):
    nome = "fish"
    precisa_clonagem = False  # a clonagem e feita no site; aqui usamos o reference_id

    def __init__(self, voz: VozReferencia | None, **opcoes):
        super().__init__(voz, **opcoes)
        self.api_key = self.opcoes.get("api_key") or os.getenv("FISH_AUDIO_API_KEY")
        self.voice_id = self.opcoes.get("voice_id") or os.getenv("FISH_VOICE_ID")
        self.modelo = str(self.opcoes.get("modelo", "s2.1-pro-free"))
        if not self.api_key or not self.voice_id:
            raise ErroNarrador("Defina FISH_AUDIO_API_KEY e FISH_VOICE_ID para usar o motor fish.")
        self.taxa_amostragem = 44100

    def carregar(self) -> None:
        pass

    def sintetizar(self, texto: str, destino: Path) -> Path:
        resp = requests.post(
            "https://api.fish.audio/v1/tts",
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json", "model": self.modelo},
            json={"text": texto, "reference_id": self.voice_id, "format": "wav", "language": "pt",
                  "prosody": {"speed": 1.0, "volume": 0, "normalize_loudness": True}},
            timeout=180,
        )
        if resp.status_code != 200:
            raise ErroNarrador(f"Fish Audio retornou {resp.status_code}: {resp.text[:300]}")
        destino.parent.mkdir(parents=True, exist_ok=True)
        bruto = destino.with_name(destino.stem + "_fish.wav")
        bruto.write_bytes(resp.content)
        ffmpeg(["-i", bruto, "-ac", "1", "-ar", str(self.taxa_amostragem), destino])
        bruto.unlink(missing_ok=True)
        return destino

    def identidade(self) -> str:
        return f"fish|{self.voice_id}|{self.modelo}"
