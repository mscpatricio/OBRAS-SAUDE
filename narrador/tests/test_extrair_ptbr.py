import importlib
import pytest

from narrador import extrair


def test_markdown_para_fala_tabela_e_listas():
    md = "# Obras\n\n| Obra | Valor |\n| --- | --- |\n| Hospital | 12 |\n\n- item um\n- item dois\n"
    txt = extrair.markdown_para_fala(md)
    assert "Obras." in txt
    assert "Obra: Hospital, Valor: 12." in txt
    assert "item um." in txt and "item dois." in txt


def test_secoes_pptx_usa_notas():
    md = "<!-- Slide number: 1 -->\n# Titulo\nTexto visivel\n### Notes:\nFala do orador.\n<!-- Slide number: 2 -->\n# Dois\nSo texto\n"
    secoes = extrair._secoes_pptx(md)
    assert [s.origem for s in secoes] == ["slide 1", "slide 2"]
    assert secoes[0].texto == "Fala do orador." and secoes[0].titulo == "Titulo"
    assert "So texto." in secoes[1].texto


def test_frontend_ptbr_normaliza_e_mapeia_arpabet():
    pt = importlib.import_module("narrador.gptsovits_ptbr.portuguese")
    norm = pt.text_normalize("Hoje são 12 obras, R$ 1.500,00 até 30/09/2026.")
    assert "doze obras" in norm and "mil e quinhentos reais" in norm and "trinta de setembro" in norm
    pytest.importorskip("espeakng_loader")
    pytest.importorskip("phonemizer")
    fones = pt.g2p("Olá, bom dia.")
    assert fones[-1] == "." and "," in fones
    # todos os fonemas devem existir na tabela ARPAbet do GPT-SoVITS (ou ser pontuacao)
    arpa = {"AA", "AE", "AH", "AO", "AW", "AY", "EH", "ER", "EY", "IH", "IY", "OW", "OY", "UH", "UW"}
    cons = {"B", "CH", "D", "DH", "F", "G", "HH", "JH", "K", "L", "M", "N", "NG", "P", "R", "S", "SH", "T", "TH", "V", "W", "Y", "Z", "ZH"}
    for f in fones:
        if f in {",", ".", "!", "?", "…"}:
            continue
        assert f in cons or (f[:-1] in arpa and f[-1] in "012"), f
