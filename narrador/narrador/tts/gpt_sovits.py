"""GPT-SoVITS (RVC-Boss, MIT) via servidor HTTP `api_v2.py`.

Funciona com qualquer instalacao do GPT-SoVITS: pacote integrado do Windows,
Linux, Colab. O Narrador apenas conversa com o servidor:

    python api_v2.py -a 127.0.0.1 -p 9880 -c GPT_SoVITS/configs/tts_infer.yaml

IDIOMAS: o GPT-SoVITS oficial fala zh, en, ja, ko e yue. NAO ha frontend de
portugues publicado (ha apenas um modelo pt-BR experimental sem o codigo do
frontend). Com `text_lang=pt` o servidor recusa; este motor avisa com clareza.
Para pt-BR use chatterbox-ptbr / chatterbox-online ate existir suporte.

Opcoes (-o chave=valor ou opcoes_motor no YAML):
  url             http://127.0.0.1:9880
  text_lang       en | zh | ja | ko | yue | auto | pt (quando houver frontend)
  prompt_lang     idioma do audio de referencia (padrao = text_lang)
  gpt_weights     caminho .ckpt do GPT ajustado para a sua voz (no servidor)
  sovits_weights  caminho .pth do SoVITS ajustado (no servidor)
  ref_remoto      caminho do audio de referencia NO SERVIDOR (se for remoto)
  speed_factor    1.0   top_k 15   top_p 1.0   temperature 1.0
  text_split_method cut5   repetition_penalty 1.35   sample_steps 32
"""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

import requests

from ..util import ErroNarrador, console, duracao_audio, exigir_binario
from .base import MotorTTS, VozReferencia

IDIOMAS_OFICIAIS = {"auto", "auto_yue", "en", "zh", "ja", "yue", "ko", "all_zh", "all_ja", "all_yue", "all_ko"}


class MotorGPTSoVITS(MotorTTS):
    nome = "gpt-sovits"

    def __init__(self, voz: VozReferencia | None, **opcoes):
        super().__init__(voz, **opcoes)
        o = self.opcoes
        self.url = str(o.get("url") or os.getenv("GPT_SOVITS_URL") or "http://127.0.0.1:9880").rstrip("/")
        self.text_lang = str(o.get("text_lang", "pt" if self.idioma == "pt" else self.idioma)).lower()
        self.prompt_lang = str(o.get("prompt_lang", self.text_lang)).lower()
        self.gpt_weights = o.get("gpt_weights") or os.getenv("GPT_SOVITS_GPT")
        self.sovits_weights = o.get("sovits_weights") or os.getenv("GPT_SOVITS_SOVITS")
        self.ref_remoto = o.get("ref_remoto")
        self.speed_factor = float(o.get("speed_factor", 1.0))
        self.top_k = int(float(o.get("top_k", 15)))
        self.top_p = float(o.get("top_p", 1.0))
        self.temperature = float(o.get("temperature", 1.0))
        self.text_split_method = str(o.get("text_split_method", "cut5"))
        self.repetition_penalty = float(o.get("repetition_penalty", 1.35))
        self.sample_steps = int(float(o.get("sample_steps", 32)))
        self.timeout = int(float(o.get("timeout", 600)))
        self.taxa_amostragem = 32000
        self._ref_path: str | None = None

    # ------------------------------------------------------------------ #
    def _get(self, rota: str, **params) -> requests.Response:
        try:
            return requests.get(f"{self.url}{rota}", params=params, timeout=self.timeout)
        except requests.ConnectionError as e:
            raise ErroNarrador(
                f"Nao consegui falar com o GPT-SoVITS em {self.url}.\n"
                "Inicie o servidor (Windows: iniciar_gpt_sovits.bat; Linux/Colab: python api_v2.py -a 127.0.0.1 -p 9880) "
                "ou informe a URL com -o url=http://host:porta"
            ) from e

    def _preparar_referencia(self) -> str:
        """GPT-SoVITS exige referencia de 3 a 10 s. Recorta se precisar."""
        if self.ref_remoto:
            return str(self.ref_remoto)
        origem = Path(self.voz.audio)
        dur = duracao_audio(origem)
        if 3.0 <= dur <= 10.0:
            return str(origem.resolve())
        exigir_binario("ffmpeg")
        destino = Path(tempfile.gettempdir()) / f"narrador_ref_gsv_{origem.stem}.wav"
        if dur > 10.0:
            console.print(f"[yellow]Referencia tem {dur:.1f}s; GPT-SoVITS aceita 3-10 s. Usando os primeiros 9,5 s.[/]")
            subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(origem), "-t", "9.5",
                            "-ac", "1", "-ar", "32000", str(destino)], check=True)
        else:
            raise ErroNarrador(f"Referencia muito curta ({dur:.1f}s): GPT-SoVITS precisa de 3 a 10 segundos.")
        return str(destino.resolve())

    def carregar(self) -> None:
        if self.text_lang not in IDIOMAS_OFICIAIS:
            console.print(
                f"[bold yellow]Aviso:[/] idioma '{self.text_lang}' nao faz parte do GPT-SoVITS oficial "
                f"({', '.join(sorted(IDIOMAS_OFICIAIS))}). So funciona se o servidor tiver um frontend desse idioma instalado."
            )
        # servidor no ar?
        r = self._get("/control", command="")  # qualquer resposta serve como ping
        if r.status_code >= 500:
            raise ErroNarrador(f"GPT-SoVITS respondeu {r.status_code} em {self.url}.")
        if self.gpt_weights:
            r = self._get("/set_gpt_weights", weights_path=self.gpt_weights)
            if r.status_code != 200:
                raise ErroNarrador(f"Falha ao carregar GPT weights '{self.gpt_weights}': {r.text[:200]}")
        if self.sovits_weights:
            r = self._get("/set_sovits_weights", weights_path=self.sovits_weights)
            if r.status_code != 200:
                raise ErroNarrador(f"Falha ao carregar SoVITS weights '{self.sovits_weights}': {r.text[:200]}")
        self._ref_path = self._preparar_referencia()

    def sintetizar(self, texto: str, destino: Path) -> Path:
        self.garantir_carregado()
        corpo = {
            "text": texto,
            "text_lang": self.text_lang,
            "ref_audio_path": self._ref_path,
            "prompt_text": self.voz.transcricao or "",
            "prompt_lang": self.prompt_lang,
            "text_split_method": self.text_split_method,
            "batch_size": 1,
            "speed_factor": self.speed_factor,
            "top_k": self.top_k,
            "top_p": self.top_p,
            "temperature": self.temperature,
            "repetition_penalty": self.repetition_penalty,
            "sample_steps": self.sample_steps,
            "media_type": "wav",
            "streaming_mode": False,
            "parallel_infer": True,
        }
        erro = None
        for tentativa in range(3):
            try:
                r = requests.post(f"{self.url}/tts", json=corpo, timeout=self.timeout)
            except requests.RequestException as e:
                erro = e
                time.sleep(3 * (tentativa + 1))
                continue
            if r.status_code == 200 and r.headers.get("content-type", "").startswith("audio"):
                destino.parent.mkdir(parents=True, exist_ok=True)
                destino.write_bytes(r.content)
                return destino
            detalhe = r.text[:400]
            if "text_lang" in detalhe or "language" in detalhe.lower():
                raise ErroNarrador(
                    f"O servidor GPT-SoVITS recusou o idioma '{self.text_lang}': {detalhe}\n"
                    "O GPT-SoVITS oficial nao tem portugues. Use -o text_lang=en/zh/ja/ko/yue, "
                    "ou troque para --motor chatterbox-ptbr / chatterbox-online para narrar em pt-BR."
                )
            if "ref_audio" in detalhe or "reference" in detalhe.lower():
                raise ErroNarrador(f"Problema com o audio de referencia no servidor: {detalhe}\n"
                                   "Se o servidor for remoto, envie o wav para la e informe -o ref_remoto=/caminho/no/servidor.wav")
            erro = RuntimeError(f"HTTP {r.status_code}: {detalhe}")
            time.sleep(2)
        raise ErroNarrador(f"GPT-SoVITS falhou ao sintetizar: {erro}")

    def identidade(self) -> str:
        return (super().identidade() + f"|{self.url}|{self.text_lang}|{self.gpt_weights}|{self.sovits_weights}"
                f"|{self.speed_factor}|{self.top_k}|{self.top_p}|{self.temperature}")
