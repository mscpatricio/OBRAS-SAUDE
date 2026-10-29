"""Narrador: narra slides com a sua voz clonada e gera um video MP4.

Fluxo:
    slides (PPTX/PDF/imagens) -> roteiro (notas do orador ou arquivo .md)
    -> TTS com voz clonada (Chatterbox, Qwen3-TTS, F5-TTS, XTTS, ElevenLabs)
    -> pos-processamento de audio (ruido, loudness, pausas)
    -> montagem do MP4 com ffmpeg (transicoes, legendas, musica de fundo)
"""

__version__ = "0.1.0"
