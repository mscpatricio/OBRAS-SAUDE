"""Qwen3-TTS (Alibaba) - Apache 2.0, clonagem com 3 s de audio, 10 idiomas incl. portugues.

Requer GPU (bfloat16, ~8 GB para o 1.7B). Com transcricao da referencia o modo ICL
(in-context) copia melhor o timbre e a prosodia; sem transcricao usa apenas o
embedding do falante (x_vector_only_mode).
"""

from __future__ import annotations

from pathlib import Path

from ..util import ErroNarrador
from .base import MotorTTS, VozReferencia

MODELO_PADRAO = "Qwen/Qwen3-TTS-12Hz-1.7B-Base"


class MotorQwen3(MotorTTS):
    nome = "qwen3"

    def __init__(self, voz: VozReferencia | None, **opcoes):
        super().__init__(voz, **opcoes)
        self.modelo_id = str(self.opcoes.get("modelo", MODELO_PADRAO))
        self.temperature = float(self.opcoes.get("temperature", 0.8))
        self.modelo = None
        self._prompt = None

    def carregar(self) -> None:
        try:
            import torch
            from qwen_tts import Qwen3TTSModel
        except ImportError as e:
            raise ErroNarrador("qwen-tts nao instalado. Rode: pip install qwen-tts") from e

        dtype = torch.bfloat16 if self.dispositivo.startswith("cuda") else torch.float32
        kwargs = dict(device_map=self.dispositivo, dtype=dtype)
        try:
            self.modelo = Qwen3TTSModel.from_pretrained(self.modelo_id, attn_implementation="flash_attention_2", **kwargs)
        except Exception:
            self.modelo = Qwen3TTSModel.from_pretrained(self.modelo_id, **kwargs)
        self._prompt = self.modelo.create_voice_clone_prompt(
            ref_audio=str(self.voz.audio),
            ref_text=self.voz.transcricao or None,
            x_vector_only_mode=not bool(self.voz.transcricao),
        )

    def sintetizar(self, texto: str, destino: Path) -> Path:
        self.garantir_carregado()
        wavs, sr = self.modelo.generate_voice_clone(
            text=texto,
            language="Portuguese",
            voice_clone_prompt=self._prompt,
            do_sample=True,
            temperature=self.temperature,
            top_k=50,
            repetition_penalty=1.05,
            max_new_tokens=2048,
        )
        return self._salvar(destino, wavs[0], int(sr))
