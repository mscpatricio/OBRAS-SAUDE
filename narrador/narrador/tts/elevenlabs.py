"""ElevenLabs (API comercial). Clone a voz no painel e informe o VOICE_ID.

Variaveis: ELEVENLABS_API_KEY, ELEVENLABS_VOICE_ID (ou --opcao voice_id=...).
Modelo padrao: eleven_multilingual_v2 (excelente em pt-BR).
"""

from __future__ import annotations

import os
from pathlib import Path

import requests

from ..util import ErroNarrador, ffmpeg
from .base import MotorTTS, VozReferencia


class MotorElevenLabs(MotorTTS):
    nome = "elevenlabs"
    precisa_clonagem = False  # a clonagem acontece no painel; aqui so usamos o voice_id

    def __init__(self, voz: VozReferencia | None, **opcoes):
        super().__init__(voz, **opcoes)
        self.api_key = self.opcoes.get("api_key") or os.getenv("ELEVENLABS_API_KEY")
        self.voice_id = self.opcoes.get("voice_id") or os.getenv("ELEVENLABS_VOICE_ID")
        self.modelo_id = self.opcoes.get("modelo", "eleven_multilingual_v2")
        if not self.api_key or not self.voice_id:
            raise ErroNarrador("Defina ELEVENLABS_API_KEY e ELEVENLABS_VOICE_ID para usar o motor elevenlabs.")
        self.taxa_amostragem = 44100

    def carregar(self) -> None:
        pass

    def sintetizar(self, texto: str, destino: Path) -> Path:
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}?output_format=mp3_44100_192"
        resp = requests.post(
            url,
            headers={"xi-api-key": self.api_key, "Content-Type": "application/json"},
            json={
                "text": texto,
                "model_id": self.modelo_id,
                "voice_settings": {"stability": 0.5, "similarity_boost": 0.8, "style": 0.2, "use_speaker_boost": True},
            },
            timeout=120,
        )
        if resp.status_code != 200:
            raise ErroNarrador(f"ElevenLabs retornou {resp.status_code}: {resp.text[:300]}")
        destino.parent.mkdir(parents=True, exist_ok=True)
        mp3 = destino.with_suffix(".mp3")
        mp3.write_bytes(resp.content)
        ffmpeg(["-i", mp3, "-ac", "1", "-ar", str(self.taxa_amostragem), destino])
        mp3.unlink(missing_ok=True)
        return destino

    def identidade(self) -> str:
        return f"elevenlabs|{self.voice_id}|{self.modelo_id}"
