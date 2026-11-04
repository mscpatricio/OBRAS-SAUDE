# -*- coding: utf-8 -*-
"""Frontend de portugues do Brasil para o GPT-SoVITS (arquivo: GPT_SoVITS/text/portuguese.py).

Estrategia: texto pt-BR -> fonemas IPA (espeak-ng, voz pt-br) -> simbolos ARPAbet
que JA EXISTEM na tabela do GPT-SoVITS (os mesmos do ingles, com marca de tonicidade
0/1/2). Assim nenhuma linha nova de embedding e necessaria: os modelos pre-treinados
funcionam em zero-shot (com sotaque) e o fine-tune com audio em portugues ensina a
pronuncia correta sem mexer na tabela de simbolos.

Dependencias (instaladas por aplicar_patch.py): phonemizer-fork + espeakng-loader
(espeak-ng embutido, funciona no Windows sem instalar nada) ou o binario espeak-ng.
Opcional: num2words (numeros por extenso).
"""

import os
import re
import shutil
import subprocess

# ----------------------------------------------------------------------------
# Normalizacao de texto (numeros, moeda, datas, siglas)
# ----------------------------------------------------------------------------
try:
    from num2words import num2words as _n2w
except Exception:  # pragma: no cover
    _n2w = None

_MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho",
          "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]

_ABREV = [
    (r"\bDra\.", "Doutora"), (r"\bDr\.", "Doutor"), (r"\bSra\.", "Senhora"), (r"\bSr\.", "Senhor"),
    (r"\bProfa\.", "Professora"), (r"\bProf\.", "Professor"), (r"\bEng\.", "Engenheiro"),
    (r"\b[Aa]rt\.", "artigo"), (r"\bpág\.", "página"), (r"\betc\.", "etcétera"),
    (r"\b[Nn][ºo°]\.?\s*(?=\d)", "número "),
]
_SIGLAS = {"SUS": "sus", "UTI": "u t i", "CNPJ": "c n p j", "CPF": "c p f", "TCU": "t c u", "TCE": "t c e",
           "PDF": "p d f", "RH": "r h", "TI": "t i", "IA": "i a", "UBS": "u b s", "UPA": "u p a", "ONG": "o n g",
           "SESA": "sésa", "PPT": "p p t"}


def _num(n, **kw):
    if _n2w is None:
        return str(n)
    try:
        return _n2w(n, lang="pt_BR", **kw)
    except Exception:
        return str(n)


def _moeda(m):
    inteiro = int(m.group(1).replace(".", ""))
    cent = m.group(2)
    s = _num(inteiro) + (" real" if inteiro == 1 else " reais")
    if cent and int(cent.ljust(2, "0")) > 0:
        c = int(cent.ljust(2, "0"))
        s += " e " + _num(c) + (" centavo" if c == 1 else " centavos")
    return s


def _data(m):
    d, mes, ano = int(m.group(1)), int(m.group(2)), int(m.group(3))
    if not 1 <= mes <= 12:
        return m.group(0)
    return ("primeiro" if d == 1 else _num(d)) + f" de {_MESES[mes - 1]} de " + _num(ano)


def text_normalize(text):
    t = text.replace(" ", " ")
    for pad, sub in _ABREV:
        t = re.sub(pad, sub, t)
    t = re.sub(r"\b(" + "|".join(_SIGLAS) + r")\b", lambda m: _SIGLAS[m.group(1)], t)
    t = re.sub(r"R\$\s*(\d{1,3}(?:\.\d{3})*|\d+)(?:,(\d{1,2}))?", _moeda, t)
    t = re.sub(r"(\d+(?:[.,]\d+)?)\s*%", lambda m: _decimal(m.group(1)) + " por cento", t)
    t = re.sub(r"\b(\d{1,2})/(\d{1,2})/(\d{4})\b", _data, t)
    t = re.sub(r"\b(\d{1,2})h(\d{2})?\b", lambda m: _num(int(m.group(1))) + (" horas" if int(m.group(1)) != 1 else " hora")
               + (" e " + _num(int(m.group(2))) if m.group(2) and int(m.group(2)) else ""), t)
    t = re.sub(r"\b(\d+)\s*[ºª°]", lambda m: _num(int(m.group(1)), to="ordinal"), t)
    t = re.sub(r"\b(\d+),(\d+)\b", lambda m: _decimal(m.group(0)), t)
    t = re.sub(r"\b\d{1,3}(?:\.\d{3})+\b", lambda m: _num(int(m.group(0).replace(".", ""))), t)
    t = re.sub(r"\b\d+\b", lambda m: _num(int(m.group(0))), t)
    t = t.replace("&", " e ").replace("+", " mais ").replace("/", " ou ")
    t = re.sub(r"[“”«»]", '"', t)
    t = re.sub(r"[‘’]", "'", t)
    t = re.sub(r"[\"'*_`#>|\[\]{}()]", " ", t)
    t = re.sub(r"[;:—–]", ",", t)
    t = re.sub(r"\.{3,}", "…", t)
    t = re.sub(r"\s+", " ", t).strip()
    t = re.sub(r"\s+([,.!?…])", r"\1", t)
    return t


def _decimal(s):
    s = s.replace(".", ",")
    if "," in s:
        a, b = s.split(",", 1)
        return _num(int(a)) + " vírgula " + _num(int(b))
    return _num(int(s))


# ----------------------------------------------------------------------------
# G2P: espeak-ng pt-br -> IPA -> ARPAbet (tabela existente do GPT-SoVITS)
# ----------------------------------------------------------------------------
_PUNCT_KEEP = {",": ",", ".": ".", "!": "!", "?": "?", "…": "…"}

# vogais (sem tonicidade; a marca 0/1/2 e acrescentada depois)
_VOGAIS = {
    "a": "AA", "ɐ": "AH", "æ": "AH", "ə": "AH", "ɑ": "AA",
    "e": "EY", "ɛ": "EH", "ɪ": "IH", "i": "IY", "y": "IH",
    "o": "OW", "ɔ": "AO", "ʊ": "UH", "u": "UW", "ʌ": "AH", "ɜ": "ER", "ɚ": "ER",
    # nasais: vogal + N (quando nao houver consoante nasal em seguida)
    "ɐ̃": "AH~", "ã": "AA~", "ẽ": "EH~", "ĩ": "IH~", "õ": "OW~", "ũ": "UW~", "ɔ̃": "AO~", "ɛ̃": "EH~",
    # ditongos
    "aɪ": "AY", "aj": "AY", "aʊ": "AW", "aw": "AW", "eɪ": "EY", "ej": "EY", "oɪ": "OY", "oj": "OY", "ɔɪ": "OY", "ɔj": "OY",
    "iʊ": "IY W", "iw": "IY W", "eʊ": "EH W", "ew": "EH W", "uɪ": "UW Y", "uj": "UW Y", "oʊ": "OW", "ow": "OW",
    "ɐ̃ʊ̃": "AW~", "ɐ̃w̃": "AW~", "ɐ̃ɪ̃": "AY~", "ɐ̃j̃": "AY~", "õɪ̃": "OY~", "õj̃": "OY~", "ũɪ̃": "UW~ Y",
}
_CONSOANTES = {
    "p": "P", "b": "B", "t": "T", "d": "D", "k": "K", "ɡ": "G", "g": "G",
    "f": "F", "v": "V", "s": "S", "z": "Z", "ʃ": "SH", "ʒ": "ZH",
    "m": "M", "n": "N", "ɲ": "N Y", "ŋ": "NG",
    "l": "L", "ʎ": "L Y", "ɫ": "L",
    "ɾ": "R", "r": "R", "ɹ": "R", "x": "HH", "ʁ": "HH", "h": "HH", "χ": "HH", "ħ": "HH",
    "tʃ": "CH", "ʧ": "CH", "dʒ": "JH", "ʤ": "JH",
    "w": "W", "j": "Y", "θ": "T", "ð": "D", "ʔ": "",
}
_NASAIS_CONS = {"m", "n", "ɲ", "ŋ"}
_RE_STRESS = re.compile(r"^([ˈˌ]?)(.*)$")

_backend = None


def _init_backend():
    """Prefere o espeak-ng embutido (espeakng-loader); senao, o binario do sistema."""
    global _backend
    if _backend is not None:
        return _backend
    try:
        import espeakng_loader
        from phonemizer.backend.espeak.wrapper import EspeakWrapper
        EspeakWrapper.set_library(espeakng_loader.get_library_path())
        EspeakWrapper.set_data_path(espeakng_loader.get_data_path())
        from phonemizer.backend import EspeakBackend
        from phonemizer.separator import Separator
        _backend = ("phonemizer", EspeakBackend("pt-br", with_stress=True, preserve_punctuation=True,
                                                 punctuation_marks=",.!?…;:"), Separator(phone=" ", word="|"))
    except Exception:
        exe = shutil.which("espeak-ng") or shutil.which("espeak")
        if not exe:
            raise RuntimeError("espeak-ng nao encontrado. Rode: pip install phonemizer-fork espeakng-loader "
                               "(ou instale o espeak-ng do sistema).")
        _backend = ("binario", exe, None)
    return _backend


def _ipa(text):
    kind, obj, sep = _init_backend()
    if kind == "phonemizer":
        out = obj.phonemize([text], separator=sep, strip=True)
        return out[0] if out else ""
    # binario: ipa com separador de fonemas '_' (--ipa=3) e palavras por espaco
    proc = subprocess.run([obj, "-v", "pt-br", "-q", "--ipa=3"], input=text, capture_output=True, text=True)
    linhas = proc.stdout.strip().replace("\n", " ")
    return "|".join(" ".join(w.split("_")) for w in linhas.split())


def _tokens_ipa(ipa):
    """Devolve lista de tokens: fonemas (com marca de tonicidade) e pontuacao."""
    tokens = []
    for palavra in ipa.split("|"):
        palavra = palavra.strip()
        if not palavra:
            continue
        for ph in palavra.split(" "):
            ph = ph.strip()
            if not ph:
                continue
            # pontuacao colada ao ultimo fonema ("ˈa," ) ou isolada
            while ph and ph[-1] in ",.!?…;:":
                p = ph[-1]
                ph = ph[:-1]
                if ph:
                    tokens.append(ph)
                tokens.append(_PUNCT_KEEP.get(p, ","))
                ph = ""
            if ph:
                tokens.append(ph)
    return tokens


def g2p(text):
    """Texto pt-BR (ja normalizado) -> lista de simbolos ARPAbet/pontuacao do GPT-SoVITS."""
    ipa = _ipa(text)
    tokens = _tokens_ipa(ipa)
    phones = []
    for i, tok in enumerate(tokens):
        if tok in _PUNCT_KEEP.values():
            phones.append(tok)
            continue
        stress, base = _RE_STRESS.match(tok).groups()
        base = base.replace("ː", "").replace("ʲ", "").replace("̪", "").replace("̩", "")
        if not base:
            continue
        nivel = "1" if stress == "ˈ" else "2" if stress == "ˌ" else "0"
        if base in _VOGAIS:
            prox = tokens[i + 1] if i + 1 < len(tokens) else ""
            prox_base = _RE_STRESS.match(prox).group(2) if prox else ""
            for parte in _VOGAIS[base].split(" "):
                nasal = parte.endswith("~")
                parte = parte.rstrip("~")
                if parte in ("W", "Y"):
                    phones.append(parte)
                else:
                    phones.append(parte + nivel)
                if nasal and prox_base not in _NASAIS_CONS:
                    phones.append("N")
        elif base in _CONSOANTES:
            phones.extend(p for p in _CONSOANTES[base].split(" ") if p)
        else:
            # fonema composto nao previsto: tenta caractere a caractere
            for ch in base:
                if ch in _VOGAIS:
                    phones.append(_VOGAIS[ch].split(" ")[0].rstrip("~") + nivel)
                elif ch in _CONSOANTES:
                    phones.extend(p for p in _CONSOANTES[ch].split(" ") if p)
    # o GPT-SoVITS espera ao menos alguns fonemas e pontuacao no fim
    if phones and phones[-1] not in _PUNCT_KEEP.values():
        phones.append(".")
    if len(phones) < 4:
        phones = [","] + phones
    return phones


if __name__ == "__main__":  # teste rapido: python portuguese.py "texto"
    import sys
    txt = " ".join(sys.argv[1:]) or "Olá! Hoje são 12 obras em andamento, com R$ 48.350.000,00 contratados."
    norm = text_normalize(txt)
    print(norm)
    print(" ".join(g2p(norm)))
