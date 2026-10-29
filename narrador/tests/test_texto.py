from narrador import texto


def test_normaliza_numeros_moeda_datas():
    t = texto.normalizar("Hoje são 12 obras, R$ 48.350.000,00. Até 30/09/2026, 63,5% executado às 14h30. Dr. Silva, nº 5.")
    assert "doze obras" in t
    assert "quarenta e oito milhões" in t and "reais" in t
    assert "trinta de setembro de dois mil e vinte e seis" in t
    assert "sessenta e três virgula cinco por cento" in t
    assert "catorze horas e trinta" in t
    assert "Doutor Silva" in t and "numero cinco" in t


def test_nao_confunde_palavra_com_abreviacao_numero():
    assert texto.normalizar("Novo plano. No entanto.") == "Novo plano. No entanto."


def test_dividir_respeita_paragrafos_e_limite():
    longo = ("palavra " * 80).strip() + ", depois disso, fim."
    trechos = texto.dividir("Primeira. Segunda!\n\n" + longo, max_chars=200)
    assert trechos[0].texto == "Primeira." and trechos[0].pausa_depois == 0.35
    assert trechos[1].pausa_depois == 0.7  # fim de paragrafo
    assert all(len(t.texto) <= 200 for t in trechos)
    assert trechos[-1].pausa_depois == 0.0
