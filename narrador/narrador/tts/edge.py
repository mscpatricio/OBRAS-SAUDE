"""Microsoft Edge TTS: vozes neurais pt-BR gratuitas, SEM clonagem.

Util para validar o roteiro e a montagem do video rapidamente (sem GPU),
antes de rodar a clonagem de verdade. Vozes: pt-BR-AntonioNeural, pt-BR-FranciscaNeural,
pt-BR-ThalitaMultilingualNeural.
"""

from __future__ import annotations

import asyncio
from pathlib import Path

from ..util import ErroNarrador, ffmpeg
from .base import MotorTTS, VozReferencia


class MotorEdge(MotorTTS):
    nome = "edge"
    precisa_clonagem = False

    def __init__(self, voz: VozReferencia | None, **opcoes):
        super().__init__(voz, **opcoes)
        self.vozes = str(self.opcoes.get("voz_edge", "pt-BR-AntonioNeural"))
        self.rate = str(self.opcoes.get("rate", "-3%"))
        self.taxa_amostragem = 24000

    def carregar(self) -> None:
        try:
            import edge_tts  # noqa: F401
        except ImportError as e:
            raise ErroNarrador("edge-tts nao instalado. Rode: pip install edge-tts") from e

    def sintetizar(self, texto: str, destino: Path) -> Path:
        self.garantir_carregado()
        import edge_tts

        destino.parent.mkdir(parents=True, exist_ok=True)
        mp3 = destino.with_suffix(".mp3")

        async def _run():
            com = edge_tts.Communicate(texto, self.vozes, rate=self.rate)
            await com.save(str(mp3))

        asyncio.run(_run())
        ffmpeg(["-i", mp3, "-ac", "1", "-ar", str(self.taxa_amostragem), destino])
        mp3.unlink(missing_ok=True)
        return destino

    def identidade(self) -> str:
        return f"edge|{self.vozes}|{self.rate}"
