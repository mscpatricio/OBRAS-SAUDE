"""Motores de sintese de voz (TTS) com clonagem zero-shot.

Todos implementam a mesma interface (`MotorTTS`) e sao carregados sob
demanda, para que o usuario instale apenas o motor que vai usar.

Motores disponiveis (todos gratuitos exceto ElevenLabs):

  chatterbox      Resemble AI Chatterbox Multilingual V3 (MIT). Melhor custo/beneficio:
                  clonagem com 6-10 s de audio, 23 idiomas incl. portugues, roda em CPU
                  (lento) ou GPU. PADRAO.
  chatterbox-ptbr Mesmo motor com o pacote dedicado de portugues brasileiro
                  (ResembleAI/Chatterbox-Multilingual-pt-br): sotaque e prosodia mais naturais.
  chatterbox-online  Chatterbox pt-BR rodando de graca no Hugging Face (ZeroGPU), via API do Space.
                  Clonagem com a sua voz SEM GPU local; precisa so de internet.
  fish            Fish Audio (API online; clonagem no site, plano gratuito limitado).
  qwen3           Alibaba Qwen3-TTS 1.7B Base (Apache 2.0). Qualidade muito alta,
                  precisa de GPU com ~8 GB.
  f5-ptbr         F5-TTS ajustado para pt-BR (firstpixel/F5-TTS-pt-br, CC-BY-NC: nao comercial).
  xtts            Coqui XTTS v2 (licenca CPML, nao comercial). Classico, bom em pt.
  elevenlabs      API paga/freemium (voz clonada no painel da ElevenLabs). Maxima qualidade.
  piper           Piper TTS: vozes neurais pt-BR offline e leves (SEM clonagem). Otimo para
                  gerar o video com voz real em CPU, sem internet.
  edge            Microsoft Edge TTS (vozes neurais pt-BR, SEM clonagem). Para testes rapidos.
  silencio        Gera silencio proporcional ao texto. Para testar a montagem do video.
"""

from __future__ import annotations

from .base import MotorTTS, VozReferencia

MOTORES: dict[str, str] = {
    "chatterbox": "Chatterbox Multilingual V3 (MIT, gratis, clonagem) - padrao",
    "chatterbox-ptbr": "Chatterbox com pacote pt-BR dedicado (MIT, gratis, clonagem)",
    "chatterbox-online": "Chatterbox pt-BR no Hugging Face Space (gratis, online, clonagem, sem GPU local)",
    "fish": "Fish Audio API (freemium, clonagem no site fish.audio)",
    "qwen3": "Qwen3-TTS 1.7B Base (Apache 2.0, gratis, clonagem, precisa GPU)",
    "f5-ptbr": "F5-TTS pt-BR (gratis, clonagem, uso nao comercial)",
    "xtts": "Coqui XTTS v2 (gratis, clonagem, uso nao comercial)",
    "elevenlabs": "ElevenLabs API (pago/freemium, clonagem no painel)",
    "piper": "Piper TTS pt-BR offline (gratis, SEM clonagem; voz real sem GPU)",
    "edge": "Edge TTS pt-BR (gratis, SEM clonagem; apenas testes)",
    "silencio": "Silencio (teste de montagem do video)",
}

INSTALACAO: dict[str, str] = {
    "chatterbox": "pip install 'narrador[chatterbox]'   (ou: pip install chatterbox-tts)",
    "chatterbox-ptbr": "pip install 'narrador[chatterbox]'",
    "chatterbox-online": "pip install 'narrador[online]'   (ou: pip install gradio_client)  + HF_TOKEN opcional",
    "fish": "export FISH_AUDIO_API_KEY=...  e  export FISH_VOICE_ID=...",
    "qwen3": "pip install 'narrador[qwen3]'   (ou: pip install qwen-tts)",
    "f5-ptbr": "pip install 'narrador[f5]'   (ou: pip install f5-tts)",
    "xtts": "pip install 'narrador[xtts]'   (ou: pip install coqui-tts)  + export COQUI_TOS_AGREED=1",
    "elevenlabs": "export ELEVENLABS_API_KEY=...  e  export ELEVENLABS_VOICE_ID=...",
    "piper": "pip install 'narrador[piper]'   (ou: pip install piper-tts)",
    "edge": "pip install 'narrador[edge]'   (ou: pip install edge-tts)",
    "silencio": "(nada a instalar)",
}


def criar_motor(nome: str, voz: VozReferencia | None, **opcoes) -> MotorTTS:
    nome = (nome or "chatterbox").lower()
    if nome == "chatterbox":
        from .chatterbox_tts import MotorChatterbox
        return MotorChatterbox(voz, pacote=None, **opcoes)
    if nome == "chatterbox-ptbr":
        from .chatterbox_tts import MotorChatterbox
        return MotorChatterbox(voz, pacote="ResembleAI/Chatterbox-Multilingual-pt-br", **opcoes)
    if nome in {"chatterbox-online", "online", "hf"}:
        from .hf_space import MotorChatterboxOnline
        return MotorChatterboxOnline(voz, **opcoes)
    if nome == "fish":
        from .fish import MotorFish
        return MotorFish(voz, **opcoes)
    if nome == "qwen3":
        from .qwen3_tts import MotorQwen3
        return MotorQwen3(voz, **opcoes)
    if nome == "f5-ptbr":
        from .f5_tts import MotorF5
        return MotorF5(voz, **opcoes)
    if nome == "xtts":
        from .xtts import MotorXTTS
        return MotorXTTS(voz, **opcoes)
    if nome == "elevenlabs":
        from .elevenlabs import MotorElevenLabs
        return MotorElevenLabs(voz, **opcoes)
    if nome == "piper":
        from .piper import MotorPiper
        return MotorPiper(voz, **opcoes)
    if nome == "edge":
        from .edge import MotorEdge
        return MotorEdge(voz, **opcoes)
    if nome == "silencio":
        from .base import MotorSilencio
        return MotorSilencio(voz, **opcoes)
    raise ValueError(f"Motor desconhecido: {nome}. Opcoes: {', '.join(MOTORES)}")


__all__ = ["MotorTTS", "VozReferencia", "MOTORES", "INSTALACAO", "criar_motor"]
