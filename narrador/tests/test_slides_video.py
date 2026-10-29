from pathlib import Path

import numpy as np

from narrador import audio, slides, video


def test_ler_roteiro_markdown(tmp_path: Path):
    md = tmp_path / "r.md"
    md.write_text("# titulo\n\n## Slide 1 - Abertura\nOi.\n\n## Slide 3\nTres.\n", encoding="utf-8")
    assert slides.ler_roteiro(md) == {1: "Oi.", 3: "Tres."}


def test_ler_roteiro_json_e_yaml(tmp_path: Path):
    j = tmp_path / "r.json"
    j.write_text('[{"slide": 2, "texto": "dois"}, {"slide": 3, "texto": "tres"}]', encoding="utf-8")
    assert slides.ler_roteiro(j) == {2: "dois", 3: "tres"}
    y = tmp_path / "r.yaml"
    y.write_text("slides:\n  - um\n  - dois\n", encoding="utf-8")
    assert slides.ler_roteiro(y) == {1: "um", 2: "dois"}


def test_srt_e_montagem_de_video(tmp_path: Path):
    # imagem simples via PyMuPDF (sem depender de PIL)
    import pymupdf

    img = tmp_path / "s.png"
    doc = pymupdf.open()
    pagina = doc.new_page(width=640, height=360)
    pagina.insert_text((50, 100), "slide", fontsize=40)
    pagina.get_pixmap().save(img)

    sr = 48000
    a1 = audio.escrever_wav(tmp_path / "a1.wav", np.zeros(int(sr * 1.5), dtype=np.float32), sr)
    a2 = audio.escrever_wav(tmp_path / "a2.wav", np.zeros(int(sr * 1.5), dtype=np.float32), sr)
    cenas = [video.Cena(img, a1, "Primeira frase. Segunda frase."), video.Cena(img, a2, "Terceira.")]
    op = video.OpcoesVideo(largura=320, altura=180, fps=10, transicao=0.3, preset="ultrafast", crf=30)
    mp4 = video.montar(cenas, tmp_path / "out" / "v.mp4", op, tmp_path / "trab")
    assert mp4.exists() and mp4.stat().st_size > 0
    srt = mp4.with_suffix(".srt").read_text(encoding="utf-8")
    assert "Primeira frase." in srt and "Terceira." in srt
    dur = audio.duracao_audio(mp4)
    assert 2.4 <= dur <= 3.1  # 1.5 + 1.5 - 0.3 de transicao (+ tolerancia do encoder)
