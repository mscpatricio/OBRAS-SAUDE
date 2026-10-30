"""Chatterbox pt-BR ONLINE, gratis, via Hugging Face Space (ZeroGPU).

Usa a demo oficial da Resemble AI (ResembleAI/Chatterbox-Multilingual-TTS-pt-br)
pela API do Gradio: envia a sua amostra de voz + cada frase e recebe o audio
clonado, sem precisar de GPU local. Precisa de internet.

Limites: cada chamada aceita ~300 caracteres (o Narrador ja divide em frases);
a cota de GPU gratuita e por usuario/IP e renova com o tempo. Crie uma conta
gratuita em huggingface.co e defina HF_TOKEN para ter mais cota.

Opcoes: -o space=ResembleAI/Chatterbox-Multilingual-TTS   (modelo multilingue; usa language_id)
        -o exaggeration=0.45 -o cfg_weight=0.5 -o temperature=0.75 -o seed=0
"""

from __future__ import annotations

import os
import re
import shutil
import time
from pathlib import Path

from ..util import ErroNarrador, console
from .base import MotorTTS, VozReferencia

SPACE_PTBR = "ResembleAI/Chatterbox-Multilingual-TTS-pt-br"
SPACE_MULTI = "ResembleAI/Chatterbox-Multilingual-TTS"


class MotorChatterboxOnline(MotorTTS):
    nome = "chatterbox-online"

    def __init__(self, voz: VozReferencia | None, **opcoes):
        super().__init__(voz, **opcoes)
        self.space = str(self.opcoes.get("space", SPACE_PTBR))
        self.exaggeration = float(self.opcoes.get("exaggeration", 0.45))
        self.cfg_weight = float(self.opcoes.get("cfg_weight", 0.5))
        self.temperature = float(self.opcoes.get("temperature", 0.75))
        self.seed = int(float(self.opcoes.get("seed", 0)))
        self.tentativas = int(self.opcoes.get("tentativas", 4))
        self.cliente = None
        self._ref = None

    def carregar(self) -> None:
        try:
            from gradio_client import Client, handle_file
        except ImportError as e:
            raise ErroNarrador("gradio_client nao instalado. Rode: pip install gradio_client") from e
        token = os.getenv("HF_TOKEN")
        if not token:
            console.print("[yellow]Dica:[/] defina HF_TOKEN (conta gratuita em huggingface.co) para ter mais cota de GPU.")
        self.cliente = Client(self.space, token=token, verbose=False)
        self._ref = handle_file(str(self.voz.audio))
        self.taxa_amostragem = 24000

    def sintetizar(self, texto: str, destino: Path) -> Path:
        self.garantir_carregado()
        if len(texto) > 300:
            texto = texto[:300]
        kwargs = dict(
            text_input=texto,
            audio_prompt_path_input=self._ref,
            exaggeration_input=self.exaggeration,
            temperature_input=self.temperature,
            seed_num_input=self.seed,
            cfgw_input=self.cfg_weight,
            api_name="/generate_tts_audio",
        )
        if self.space == SPACE_MULTI or "pt-br" not in self.space.lower():
            kwargs["language_id"] = self.idioma
        erro = None
        for tentativa in range(1, self.tentativas + 1):
            try:
                resultado = self.cliente.predict(**kwargs)
                break
            except Exception as e:  # cota de GPU, fila cheia, queda de rede
                erro = e
                msg = str(e)
                espera = self._espera_para(msg, tentativa)
                console.print(f"[yellow]Space indisponivel ({msg[:110]}). Nova tentativa em {espera:.0f}s[/]")
                time.sleep(espera)
        else:
            raise ErroNarrador(f"O Space {self.space} nao respondeu apos {self.tentativas} tentativas: {erro}\n"
                               "Cota de GPU gratuita esgotada? Defina HF_TOKEN ou tente mais tarde.")
        caminho = resultado[0] if isinstance(resultado, (list, tuple)) else resultado
        destino.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(caminho, destino)
        return destino

    def _espera_para(self, msg: str, tentativa: int) -> float:
        """Quanto esperar antes de tentar de novo; levanta erro claro se for cota sem token."""
        if "ZeroGPU quota" in msg or "quota" in msg.lower():
            if not os.getenv("HF_TOKEN"):
                raise ErroNarrador(
                    "Cota anonima de GPU do Hugging Face esgotada.\n"
                    "Crie uma conta gratuita, gere um token em https://huggingface.co/settings/tokens "
                    "e rode:  export HF_TOKEN=hf_...   (a cota com login e bem maior)."
                )
            m = re.search(r"Try again in (\d+):(\d+):(\d+)", msg)
            if m:
                h, mi, se = map(int, m.groups())
                return min(h * 3600 + mi * 60 + se + 5, 1800)
            return 120 * tentativa
        return 15 * tentativa

    def identidade(self) -> str:
        return super().identidade() + f"|{self.space}|{self.exaggeration}|{self.cfg_weight}|{self.temperature}|{self.seed}"
