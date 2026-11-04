# -*- coding: utf-8 -*-
"""Treina (fine-tune) o GPT-SoVITS com a SUA voz em portugues do Brasil, sem a WebUI.

Rode DE DENTRO da pasta do GPT-SoVITS, com o Python dele, depois de aplicar_patch.py:

    python treinar_ptbr.py --audio gravacoes/ --nome minha_voz
    (Windows, pacote integrado):  runtime\\python.exe treinar_ptbr.py --audio C:\\voz --nome minha_voz

Entrada: um arquivo ou pasta com 3 a 20 minutos da sua voz lendo texto em portugues
(wav/mp3/m4a), sem musica. Etapas (as mesmas da WebUI oficial, em ordem):
  1. fatiar em trechos de 3-10 s        (tools/slice_audio.py)
  2. transcrever com Whisper em pt       (tools/asr/fasterwhisper_asr.py -l pt)
  3. texto -> fonemas pt-BR              (prepare_datasets/1-get-text.py, via o patch)
  4. HuBERT + wav 32k (+ speaker vec)    (2-get-hubert-wav32k.py, 2-get-sv.py)
  5. tokens semanticos                   (3-get-semantic.py)
  6. treinar SoVITS (timbre)             (s2_train.py)
  7. treinar GPT (pronuncia/ritmo)       (s1_train.py)

Saida: SoVITS_weights_v2Pro/<nome>_e<N>_s<M>.pth e GPT_weights_v2Pro/<nome>-e<N>.ckpt.
Use-os no Narrador: -o gpt_weights=... -o sovits_weights=... (ou no narrador.yaml).
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

RAIZ = Path.cwd()
PY = sys.executable


def run(cmd: list[str], env: dict | None = None) -> None:
    print("\n$ " + " ".join(str(c) for c in cmd), flush=True)
    e = dict(os.environ)
    if env:
        e.update({k: str(v) for k, v in env.items()})
    e.setdefault("version", "v2")
    # os scripts importam "tools.*" e "GPT_SoVITS.*" relativos a raiz do repositorio
    e["PYTHONPATH"] = os.pathsep.join([str(RAIZ), str(RAIZ / "GPT_SoVITS"), e.get("PYTHONPATH", "")]).rstrip(os.pathsep)
    subprocess.run([str(c) for c in cmd], check=True, env=e, cwd=RAIZ)


def etapa(n: str) -> None:
    print(f"\n{'=' * 70}\n  {n}\n{'=' * 70}", flush=True)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--audio", help="arquivo ou pasta com a sua voz (pt-BR)")
    ap.add_argument("--lista", help="dataset ja transcrito: arquivo .list com linhas 'caminho.wav|locutor|PT|texto' (pula fatiar e ASR)")
    ap.add_argument("--nome", required=True, help="nome do experimento/voz (sem espacos)")
    ap.add_argument("--versao", default="v2Pro", choices=["v2", "v2Pro", "v2ProPlus"])
    ap.add_argument("--gpu", default="0", help="indice da GPU (ex.: 0). Use 'cpu' so para testar a preparacao.")
    ap.add_argument("--batch", type=int, default=0, help="batch size (0 = automatico)")
    ap.add_argument("--epocas-sovits", type=int, default=8)
    ap.add_argument("--epocas-gpt", type=int, default=15)
    ap.add_argument("--lr-texto", type=float, default=0.4, help="text_low_lr_rate (0.4 padrao; 1.0 para idioma novo)")
    ap.add_argument("--whisper", default="large-v3-turbo", choices=["medium", "large-v2", "large-v3", "large-v3-turbo"],
                    help="modelo Whisper para transcrever (large-v3-turbo: rapido e bom)")
    ap.add_argument("--sem-fatiar", action="store_true", help="os arquivos ja sao trechos curtos")
    ap.add_argument("--so-preparar", action="store_true", help="para antes do treino (gera o dataset)")
    ap.add_argument("--so-treinar", action="store_true", help="pula a preparacao (dataset ja pronto)")
    ap.add_argument("--continuar", action="store_true", help="retoma um treino anterior em vez de comecar do zero")
    a = ap.parse_args()

    if not (RAIZ / "GPT_SoVITS" / "text" / "portuguese.py").exists():
        sys.exit("Rode primeiro: python aplicar_patch.py .   (e execute este script de dentro da pasta do GPT-SoVITS)")
    cpu = a.gpu.lower() == "cpu"
    is_half = "False" if cpu else "True"
    gpu = "0" if cpu else a.gpu
    exp = a.nome.strip().replace(" ", "_")
    exp_dir = RAIZ / "logs" / exp
    exp_dir.mkdir(parents=True, exist_ok=True)
    pm = "GPT_SoVITS/pretrained_models"
    s2G = {"v2": f"{pm}/gsv-v2final-pretrained/s2G2333k.pth", "v2Pro": f"{pm}/v2Pro/s2Gv2Pro.pth",
           "v2ProPlus": f"{pm}/v2Pro/s2Gv2ProPlus.pth"}[a.versao]
    s2D = s2G.replace("s2G", "s2D")
    s1 = f"{pm}/gsv-v2final-pretrained/s1bert25hz-5kh-longer-epoch=12-step=369668.ckpt" if a.versao == "v2" else f"{pm}/s1v3.ckpt"
    for p in (s2G, s1, f"{pm}/chinese-hubert-base", f"{pm}/chinese-roberta-wwm-ext-large"):
        if not (RAIZ / p).exists():
            sys.exit(f"Modelo pre-treinado ausente: {p}. Baixe os modelos (install.sh / pacote integrado).")

    if not a.so_treinar and a.lista:
        # dataset pronto (ex.: corpus publico com transcricoes): normaliza os textos e segue para a etapa 3
        etapa("1-2/7 usando a lista pronta (sem fatiar/ASR)")
        sys.path.insert(0, str(RAIZ / "GPT_SoVITS"))
        from text import portuguese  # type: ignore

        fatias = exp_dir / "fatias"
        fatias.mkdir(exist_ok=True)
        asr_dir = exp_dir / "asr"
        asr_dir.mkdir(exist_ok=True)
        lista = asr_dir / "fatias.list"
        corrigidas = []
        for l in Path(a.lista).read_text(encoding="utf-8").splitlines():
            partes = l.split("|")
            if len(partes) < 4 or not Path(partes[0]).exists():
                continue
            destino_wav = fatias / Path(partes[0]).name
            if not destino_wav.exists():
                shutil.copy(partes[0], destino_wav)
            corrigidas.append("|".join([str(destino_wav), exp, "PT", portuguese.text_normalize("|".join(partes[3:]).strip())]))
        lista.write_text("\n".join(corrigidas) + "\n", encoding="utf-8")
        print(f"{len(corrigidas)} trechos na lista")
        a.audio = a.audio or str(fatias)
    if not a.so_treinar and not a.lista:
        if not a.audio:
            sys.exit("Informe --audio (gravacoes) ou --lista (dataset transcrito).")
        audio = Path(a.audio).expanduser().resolve()
        if not audio.exists():
            sys.exit(f"Audio nao encontrado: {audio}")
        etapa("1/7 fatiando o audio em trechos de 3-10 s")
        fatias = exp_dir / "fatias"
        if a.sem_fatiar:
            fatias.mkdir(exist_ok=True)
            for f in ([audio] if audio.is_file() else sorted(audio.iterdir())):
                if f.suffix.lower() in {".wav", ".mp3", ".m4a", ".flac", ".ogg", ".oga", ".opus", ".aac", ".wma", ".mp4"}:
                    shutil.copy(f, fatias / f.name)
        else:
            if fatias.exists():
                shutil.rmtree(fatias)
            # normaliza a entrada: qualquer formato (inclusive .opus do WhatsApp) -> wav 32 kHz mono
            entrada_wav = exp_dir / "entrada_wav"
            if entrada_wav.exists():
                shutil.rmtree(entrada_wav)
            entrada_wav.mkdir()
            arquivos = [audio] if audio.is_file() else sorted(audio.iterdir())
            n_conv = 0
            for f in arquivos:
                if f.suffix.lower() in {".wav", ".mp3", ".m4a", ".flac", ".ogg", ".oga", ".opus", ".aac", ".wma", ".mp4", ".amr", ".3gp"}:
                    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(f), "-ac", "1",
                                    "-ar", "32000", "-af", "highpass=f=70,loudnorm=I=-20:TP=-2", str(entrada_wav / (f.stem + ".wav"))],
                                   check=True)
                    n_conv += 1
            if n_conv == 0:
                sys.exit("Nenhum arquivo de audio reconhecido na entrada.")
            run([PY, "tools/slice_audio.py", entrada_wav, fatias, "-34", "4000", "300", "10", "500", "0.9", "0.25", "0", "1"])
        n = len(list(fatias.iterdir()))
        if n == 0:
            sys.exit("Nenhum trecho gerado. O audio tem fala? Tente --sem-fatiar com arquivos curtos.")
        print(f"{n} trechos em {fatias}")

        etapa("2/7 transcrevendo em portugues (faster-whisper)")
        asr_dir = exp_dir / "asr"
        run([PY, "tools/asr/fasterwhisper_asr.py", "-i", fatias, "-o", asr_dir, "-s", a.whisper, "-l", "pt",
             "-p", "int8" if cpu else "float16"])
        lista = asr_dir / f"{fatias.name}.list"
        linhas = [l for l in lista.read_text(encoding="utf-8").splitlines() if l.strip()]
        # garante o codigo de idioma PT (o Whisper pode detectar outro em trechos curtos)
        # e normaliza numeros/siglas por extenso com o mesmo frontend usado na inferencia
        sys.path.insert(0, str(RAIZ / "GPT_SoVITS"))
        from text import portuguese  # type: ignore

        corrigidas = []
        for l in linhas:
            partes = l.split("|")
            if len(partes) >= 4:
                partes[2] = "PT"
                partes[3] = portuguese.text_normalize("|".join(partes[3:]).strip())
                partes = partes[:4]
            corrigidas.append("|".join(partes))
        lista.write_text("\n".join(corrigidas) + "\n", encoding="utf-8")
        print(f"{len(corrigidas)} trechos transcritos. Revise se quiser: {lista}")

    if not a.so_treinar:
        fatias = exp_dir / "fatias"
        lista = exp_dir / "asr" / "fatias.list"
        base_env = {"inp_text": str(lista), "inp_wav_dir": str(fatias), "exp_name": exp, "opt_dir": str(exp_dir),
                    "i_part": "0", "all_parts": "1", "_CUDA_VISIBLE_DEVICES": gpu, "is_half": is_half,
                    "bert_pretrained_dir": f"{pm}/chinese-roberta-wwm-ext-large",
                    "cnhubert_base_dir": f"{pm}/chinese-hubert-base",
                    "sv_path": f"{pm}/sv/pretrained_eres2netv2w24s4ep4.ckpt",
                    "pretrained_s2G": s2G, "s2config_path": f"GPT_SoVITS/configs/s2{a.versao if 'Pro' in a.versao else ''}.json"}
        if cpu:
            base_env["CUDA_VISIBLE_DEVICES"] = ""

        etapa("3/7 texto -> fonemas pt-BR")
        run([PY, "-s", "GPT_SoVITS/prepare_datasets/1-get-text.py"], base_env)
        parte = exp_dir / "2-name2text-0.txt"
        (exp_dir / "2-name2text.txt").write_text(parte.read_text(encoding="utf-8"), encoding="utf-8")
        parte.unlink()

        etapa("4/7 HuBERT + wav 32k" + (" + vetor de locutor" if "Pro" in a.versao else ""))
        run([PY, "-s", "GPT_SoVITS/prepare_datasets/2-get-hubert-wav32k.py"], base_env)
        if "Pro" in a.versao:
            run([PY, "-s", "GPT_SoVITS/prepare_datasets/2-get-sv.py"], base_env)

        etapa("5/7 tokens semanticos")
        run([PY, "-s", "GPT_SoVITS/prepare_datasets/3-get-semantic.py"], base_env)
        parte = exp_dir / "6-name2semantic-0.tsv"
        (exp_dir / "6-name2semantic.tsv").write_text("item_name\tsemantic_audio\n" + parte.read_text(encoding="utf-8"),
                                                     encoding="utf-8")
        parte.unlink()
        if a.so_preparar:
            print("\nDataset pronto em", exp_dir)
            return

    batch = a.batch
    if batch <= 0:
        batch = 2 if cpu else 6
    tmp = RAIZ / "TEMP"
    tmp.mkdir(exist_ok=True)
    # a WebUI cria estas pastas ao iniciar; sem elas o treino falha na hora de salvar
    (RAIZ / f"SoVITS_weights_{a.versao}").mkdir(exist_ok=True)
    (RAIZ / f"GPT_weights_{a.versao}").mkdir(exist_ok=True)

    if not a.continuar:  # treino do zero: apaga checkpoints de execucoes anteriores do mesmo nome
        for d in (exp_dir / f"logs_s2_{a.versao}", exp_dir / f"logs_s1_{a.versao}", exp_dir / "logs_s1"):
            if d.exists():
                shutil.rmtree(d)

    etapa(f"6/7 treinando SoVITS ({a.epocas_sovits} epocas)")
    cfg_s2 = json.loads((RAIZ / f"GPT_SoVITS/configs/s2{a.versao if 'Pro' in a.versao else ''}.json").read_text())
    s2_dir = str(exp_dir)
    (exp_dir / f"logs_s2_{a.versao}").mkdir(exist_ok=True)
    if cpu:
        cfg_s2["train"]["fp16_run"] = False
    cfg_s2["train"].update({"batch_size": batch, "epochs": a.epocas_sovits, "text_low_lr_rate": a.lr_texto,
                            "pretrained_s2G": s2G, "pretrained_s2D": s2D, "if_save_latest": True,
                            "if_save_every_weights": True, "save_every_epoch": max(1, a.epocas_sovits // 2),
                            "gpu_numbers": gpu, "grad_ckpt": False, "lora_rank": 32})
    cfg_s2["model"]["version"] = a.versao
    cfg_s2["data"]["exp_dir"] = cfg_s2["s2_ckpt_dir"] = s2_dir
    cfg_s2["save_weight_dir"] = f"SoVITS_weights_{a.versao}"
    cfg_s2["name"] = exp
    cfg_s2["version"] = a.versao
    (tmp / "tmp_s2.json").write_text(json.dumps(cfg_s2))
    run([PY, "-s", "GPT_SoVITS/s2_train.py", "--config", tmp / "tmp_s2.json"],
        {"_CUDA_VISIBLE_DEVICES": gpu, **({"CUDA_VISIBLE_DEVICES": ""} if cpu else {})})

    etapa(f"7/7 treinando GPT ({a.epocas_gpt} epocas)")
    cfg_s1 = yaml.safe_load((RAIZ / "GPT_SoVITS/configs/s1longer-v2.yaml").read_text())
    (exp_dir / "logs_s1").mkdir(exist_ok=True)
    if cpu:
        cfg_s1["train"]["precision"] = "32"
    cfg_s1["train"].update({"batch_size": batch, "epochs": a.epocas_gpt, "save_every_n_epoch": max(1, a.epocas_gpt // 3),
                            "if_save_every_weights": True, "if_save_latest": True, "if_dpo": False,
                            "half_weights_save_dir": f"GPT_weights_{a.versao}", "exp_name": exp})
    cfg_s1["pretrained_s1"] = s1
    cfg_s1["train_semantic_path"] = f"{s2_dir}/6-name2semantic.tsv"
    cfg_s1["train_phoneme_path"] = f"{s2_dir}/2-name2text.txt"
    cfg_s1["output_dir"] = f"{s2_dir}/logs_s1_{a.versao}"
    (tmp / "tmp_s1.yaml").write_text(yaml.dump(cfg_s1, default_flow_style=False))
    run([PY, "-s", "GPT_SoVITS/s1_train.py", "--config_file", tmp / "tmp_s1.yaml"],
        {"_CUDA_VISIBLE_DEVICES": gpu, "hz": "25hz", **({"CUDA_VISIBLE_DEVICES": ""} if cpu else {})})

    sov = sorted((RAIZ / f"SoVITS_weights_{a.versao}").glob(f"{exp}_e*.pth"), key=os.path.getmtime)
    gpt = sorted((RAIZ / f"GPT_weights_{a.versao}").glob(f"{exp}-e*.ckpt"), key=os.path.getmtime)
    print("\nPRONTO. Pesos da sua voz:")
    print("  SoVITS:", sov[-1] if sov else "(nao encontrado)")
    print("  GPT   :", gpt[-1] if gpt else "(nao encontrado)")
    print("\nNo Narrador:  narrador gerar apresentacao.pptx --motor gpt-sovits --voz voz/minha_voz.wav "
          f"-o text_lang=pt -o gpt_weights=\"{gpt[-1] if gpt else '...'}\" -o sovits_weights=\"{sov[-1] if sov else '...'}\"")


if __name__ == "__main__":
    main()
