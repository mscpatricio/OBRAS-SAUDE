"""F5-TTS com checkpoint ajustado para portugues brasileiro.

Modelo: firstpixel/F5-TTS-pt-br (CC-BY-NC 4.0 -> uso nao comercial).
Dicas do autor: texto em minusculas, numeros por extenso (ja fazemos),
referencia de 5-9 s COM transcricao.
"""

from __future__ import annotations

import os
from pathlib import Path

from ..util import ErroNarrador, console
from .base import MotorTTS, VozReferencia

REPO_PTBR = "firstpixel/F5-TTS-pt-br"
CANDIDATOS_CKPT = ["model_last.safetensors", "pt-br/model_last.safetensors", "model_last.pt"]


class MotorF5(MotorTTS):
    nome = "f5-ptbr"

    def __init__(self, voz: VozReferencia | None, **opcoes):
        super().__init__(voz, **opcoes)
        if not self.voz.transcricao:
            console.print("[yellow]Aviso:[/] F5-TTS funciona muito melhor com a transcricao da referencia "
                          "(arquivo .txt ao lado do wav). Sem ela, a transcricao sera estimada pelo proprio F5 (Whisper).")
        self.ckpt = self.opcoes.get("ckpt")
        self.vocab = self.opcoes.get("vocab", "")
        self.nfe = int(self.opcoes.get("nfe_step", 32))
        self.velocidade = float(self.opcoes.get("speed", 1.0))
        self.modelo = None

    def _baixar_ckpt(self) -> str:
        from huggingface_hub import hf_hub_download

        ultimo_erro = None
        for nome in CANDIDATOS_CKPT:
            try:
                return hf_hub_download(REPO_PTBR, nome, token=os.getenv("HF_TOKEN"))
            except Exception as e:  # tenta o proximo nome
                ultimo_erro = e
        raise ErroNarrador(f"Nao foi possivel baixar o checkpoint pt-BR de {REPO_PTBR}: {ultimo_erro}\n"
                           "Baixe manualmente e passe --opcao ckpt=/caminho/model_last.safetensors")

    def carregar(self) -> None:
        try:
            from f5_tts.api import F5TTS
        except ImportError as e:
            raise ErroNarrador("f5-tts nao instalado. Rode: pip install f5-tts") from e
        ckpt = self.ckpt or self._baixar_ckpt()
        # O checkpoint pt-BR foi treinado sobre a arquitetura F5TTS_Base (vocoder vocos).
        self.modelo = F5TTS(model="F5TTS_Base", ckpt_file=str(ckpt), vocab_file=str(self.vocab or ""),
                            device=self.dispositivo)

    def sintetizar(self, texto: str, destino: Path) -> Path:
        self.garantir_carregado()
        destino.parent.mkdir(parents=True, exist_ok=True)
        wav, sr, _ = self.modelo.infer(
            ref_file=str(self.voz.audio),
            ref_text=self.voz.transcricao.lower() if self.voz.transcricao else "",
            gen_text=texto.lower(),
            nfe_step=self.nfe,
            speed=self.velocidade,
            remove_silence=False,
            show_info=lambda *a, **k: None,
            progress=None,
        )
        return self._salvar(destino, wav, int(sr))
