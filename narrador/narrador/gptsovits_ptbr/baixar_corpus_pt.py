# -*- coding: utf-8 -*-
"""Baixa um recorte do corpus publico MLS (Multilingual LibriSpeech, portugues) com transcricoes.

Serve para treinar o MODELO-BASE de portugues do GPT-SoVITS (pronuncia), sobre o qual
depois se treina a sua voz com poucos minutos de audio:

    python baixar_corpus_pt.py --minutos 60 --saida corpus_pt
    python treinar_ptbr.py --lista corpus_pt/corpus_pt.list --nome ptbr_base --epocas-sovits 0 --epocas-gpt 6
    python treinar_ptbr.py --audio minhas_gravacoes/ --nome minha_voz --base-gpt GPT_weights_v2Pro/ptbr_base-e6.ckpt

Licenca do MLS: CC BY 4.0 (audiolivros do LibriVox). Requer: pip install datasets soundfile
"""

from __future__ import annotations

import argparse
import io
import time
from pathlib import Path


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--minutos", type=float, default=60, help="quantidade de audio a baixar (padrao 60 min)")
    ap.add_argument("--saida", default="corpus_pt", help="pasta de destino")
    ap.add_argument("--min-seg", type=float, default=3.0)
    ap.add_argument("--max-seg", type=float, default=12.0)
    ap.add_argument("--dataset", default="facebook/multilingual_librispeech")
    ap.add_argument("--config", default="portuguese")
    a = ap.parse_args()

    import numpy as np
    import soundfile as sf
    from datasets import Audio, load_dataset

    saida = Path(a.saida)
    (saida / "wavs").mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    ds = load_dataset(a.dataset, a.config, split="train", streaming=True)
    ds = ds.cast_column("audio", Audio(decode=False))  # decodifica com soundfile (sem torchcodec)
    total = 0.0
    n = 0
    linhas = []
    for ex in ds:
        try:
            arr, sr = sf.read(io.BytesIO(ex["audio"]["bytes"]), dtype="float32")
        except Exception:
            continue
        if getattr(arr, "ndim", 1) > 1:
            arr = arr.mean(axis=1)
        dur = len(arr) / sr
        if dur < a.min_seg or dur > a.max_seg:
            continue
        txt = (ex.get("transcript") or ex.get("text") or "").strip()
        if not txt:
            continue
        nome = f"mls_{n:05d}.wav"
        sf.write(saida / "wavs" / nome, np.asarray(arr), sr, subtype="PCM_16")
        linhas.append(f"{(saida / 'wavs' / nome).resolve()}|mls|PT|{txt}")
        total += dur
        n += 1
        if n % 100 == 0:
            print(f"{n} clipes, {total / 60:.1f} min ({time.time() - t0:.0f}s)", flush=True)
        if total >= a.minutos * 60:
            break
    lista = saida / f"{saida.name}.list"
    lista.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    print(f"Pronto: {n} clipes, {total / 60:.1f} min -> {lista}")


if __name__ == "__main__":
    main()
