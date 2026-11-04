# -*- coding: utf-8 -*-
"""Aplica o suporte a portugues do Brasil numa instalacao do GPT-SoVITS.

    python aplicar_patch.py /caminho/para/GPT-SoVITS
    (Windows, pacote integrado):  runtime\\python.exe aplicar_patch.py .

O patch e idempotente (pode rodar de novo) e faz backup *.orig dos arquivos alterados:
  - copia text/portuguese.py (frontend pt-BR -> ARPAbet)
  - cleaner.py: registra "pt" -> portuguese
  - TTS.py: aceita text_lang/prompt_lang "pt" e "all_pt" (api_v2 e WebUI)
  - TextPreprocessor.py: trata "pt"/"all_pt" sem segmentar por idioma
  - prepare_datasets/1-get-text.py: aceita "PT"/"pt" nas listas de treino
  - inference_webui.py: adiciona "Português (pt-BR)" ao seletor de idioma
  - instala phonemizer-fork, espeakng-loader e num2words no Python do GPT-SoVITS
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent


def _patch(caminho: Path, trocas: list[tuple[str, str]], marcador: str) -> None:
    if not caminho.exists():
        print(f"  [pulado] {caminho} nao existe")
        return
    src = caminho.read_text(encoding="utf-8")
    if marcador in src:
        print(f"  [ok] {caminho.name} ja tinha o patch")
        return
    novo = src
    for antigo, novo_trecho in trocas:
        if antigo not in novo:
            raise SystemExit(f"Nao encontrei o trecho esperado em {caminho}:\n{antigo}\n"
                             "A versao do GPT-SoVITS mudou; abra uma issue ou ajuste o patch.")
        novo = novo.replace(antigo, novo_trecho, 1)
    shutil.copy(caminho, caminho.with_suffix(caminho.suffix + ".orig"))
    caminho.write_text(novo, encoding="utf-8")
    print(f"  [patch] {caminho.name}")


def aplicar(raiz: Path) -> None:
    raiz = raiz.resolve()
    gs = raiz / "GPT_SoVITS"
    if not (gs / "text" / "cleaner.py").exists():
        raise SystemExit(f"{raiz} nao parece ser a pasta do GPT-SoVITS (falta GPT_SoVITS/text/cleaner.py).")
    print(f"Aplicando suporte pt-BR em {raiz}")

    print("  [copia] text/portuguese.py")
    shutil.copy(AQUI / "portuguese.py", gs / "text" / "portuguese.py")

    _patch(gs / "text" / "cleaner.py", [
        ('"ko": "korean", "yue": "cantonese"}', '"ko": "korean", "yue": "cantonese", "pt": "portuguese"}  # pt-BR patch'),
    ], '"pt": "portuguese"')

    _patch(gs / "TTS_infer_pack" / "TTS.py", [
        ('v2_languages: list = ["auto", "auto_yue", "en", "zh", "ja", "yue", "ko", "all_zh", "all_ja", "all_yue", "all_ko"]',
         'v2_languages: list = ["auto", "auto_yue", "en", "zh", "ja", "yue", "ko", "all_zh", "all_ja", "all_yue", "all_ko", "pt", "all_pt"]  # pt-BR patch'),
    ], '"all_pt"]')

    _patch(gs / "TTS_infer_pack" / "TextPreprocessor.py", [
        ('            elif language == "en":\n                langlist.append("en")\n                textlist.append(text)\n',
         '            elif language == "en":\n                langlist.append("en")\n                textlist.append(text)\n'
         '            elif language in ("pt", "all_pt"):  # pt-BR patch: texto inteiro em portugues\n'
         '                langlist.append("pt")\n                textlist.append(text)\n'),
    ], '("pt", "all_pt")')

    _patch(gs / "prepare_datasets" / "1-get-text.py", [
        ('        "yue": "yue",\n        "YUE": "yue",\n        "Yue": "yue",\n    }',
         '        "yue": "yue",\n        "YUE": "yue",\n        "Yue": "yue",\n        "pt": "pt",  # pt-BR patch\n        "PT": "pt",\n        "Pt": "pt",\n    }'),
    ], '"PT": "pt"')

    _patch(gs / "inference_webui.py", [
        ('    i18n("多语种混合(粤语)"): "auto_yue",  # 多语种启动切分识别语种\n}',
         '    i18n("多语种混合(粤语)"): "auto_yue",  # 多语种启动切分识别语种\n    "Português (pt-BR)": "all_pt",  # pt-BR patch\n}'),
    ], '"Português (pt-BR)": "all_pt"')

    # api_v2 nao precisa de patch: le os idiomas de TTS_Config.

    print("  [pip] phonemizer-fork espeakng-loader num2words")
    pacotes = ["phonemizer-fork", "espeakng-loader", "num2words"]
    rc = subprocess.run([sys.executable, "-m", "pip", "install", "-q", *pacotes], check=False).returncode
    if rc != 0 and shutil.which("uv"):  # ambientes criados com uv nao tem pip
        subprocess.run(["uv", "pip", "install", "-q", "-p", sys.executable, *pacotes], check=False)

    # teste rapido do frontend
    sys.path.insert(0, str(gs))
    try:
        from text import portuguese  # type: ignore
        frase = portuguese.text_normalize("Olá! Hoje são 12 obras em andamento.")
        print("  [teste]", frase, "->", " ".join(portuguese.g2p(frase)))
    except Exception as e:  # noqa: BLE001
        print(f"  [aviso] frontend carregou com erro: {e}")
    print("Pronto. Use text_lang=pt (api_v2) ou 'Português (pt-BR)' na WebUI.")


if __name__ == "__main__":
    alvo = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    aplicar(alvo)
