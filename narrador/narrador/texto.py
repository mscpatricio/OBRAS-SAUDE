"""Normalizacao de texto em pt-BR para TTS e divisao em trechos curtos.

Modelos de clonagem zero-shot (Chatterbox, F5, XTTS...) produzem resultado
melhor e mais estavel com frases curtas, numeros escritos por extenso e
sem simbolos estranhos. Este modulo cuida disso.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

try:
    from num2words import num2words
except Exception:  # pragma: no cover - dependencia opcional em runtime
    num2words = None  # type: ignore

ABREVIACOES = {
    r"\bDr\.": "Doutor",
    r"\bDra\.": "Doutora",
    r"\bSr\.": "Senhor",
    r"\bSra\.": "Senhora",
    r"\bProf\.": "Professor",
    r"\bProfa\.": "Professora",
    r"\bEng\.": "Engenheiro",
    r"\bart\.": "artigo",
    r"\bArt\.": "Artigo",
    r"\binc\.": "inciso",
    r"\bn[ºo°]\.?\s*(?=\d)": "numero ",
    r"\bN[ºo°]\.?\s*(?=\d)": "Numero ",
    r"\bpág\.": "pagina",
    r"\betc\.": "etcetera",
    r"\bex\.": "exemplo",
    r"\bR\$\s*": "R$ ",
    r"\bSESA\b": "SESA",
    r"\bSUS\b": "S U S",
    r"\bUTI\b": "U T I",
    r"\bCNPJ\b": "C N P J",
    r"\bCPF\b": "C P F",
    r"\bTCU\b": "T C U",
    r"\bTCE\b": "T C E",
    r"\bONG\b": "O N G",
    r"\bPDF\b": "P D F",
    r"\bKPI\b": "K P I",
    r"\bRH\b": "R H",
    r"\bTI\b": "T I",
    r"\bIA\b": "I A",
    r"\bUBS\b": "U B S",
    r"\bUPA\b": "U P A",
}

_RE_MOEDA = re.compile(r"R\$\s*(\d{1,3}(?:\.\d{3})*|\d+)(?:,(\d{1,2}))?")
_RE_PORCENTO = re.compile(r"(\d+(?:[.,]\d+)?)\s*%")
_RE_ORDINAL = re.compile(r"\b(\d+)\s*[ºª°]")
_RE_DATA = re.compile(r"\b(\d{1,2})/(\d{1,2})/(\d{4})\b")
_RE_HORA = re.compile(r"\b(\d{1,2})h(\d{2})?\b")
_RE_DECIMAL = re.compile(r"\b(\d+),(\d+)\b")
_RE_MILHAR = re.compile(r"\b\d{1,3}(?:\.\d{3})+\b")
_RE_NUMERO = re.compile(r"\b\d+\b")

MESES = [
    "janeiro", "fevereiro", "marco", "abril", "maio", "junho",
    "julho", "agosto", "setembro", "outubro", "novembro", "dezembro",
]


def _n2w(valor: int | float, **kw) -> str:
    if num2words is None:
        return str(valor)
    try:
        return num2words(valor, lang="pt_BR", **kw)
    except Exception:
        return str(valor)


def _moeda(m: re.Match) -> str:
    inteiro = int(m.group(1).replace(".", ""))
    centavos = m.group(2)
    reais = _n2w(inteiro) + (" real" if inteiro == 1 else " reais")
    if centavos and int(centavos.ljust(2, "0")) > 0:
        c = int(centavos.ljust(2, "0"))
        reais += " e " + _n2w(c) + (" centavo" if c == 1 else " centavos")
    return reais


def _porcento(m: re.Match) -> str:
    bruto = m.group(1).replace(".", ",")
    if "," in bruto:
        a, b = bruto.split(",")
        return f"{_n2w(int(a))} virgula {_n2w(int(b))} por cento"
    return f"{_n2w(int(bruto))} por cento"


def _data(m: re.Match) -> str:
    d, mes, ano = int(m.group(1)), int(m.group(2)), int(m.group(3))
    if not 1 <= mes <= 12:
        return m.group(0)
    dia = "primeiro" if d == 1 else _n2w(d)
    return f"{dia} de {MESES[mes - 1]} de {_n2w(ano)}"


def _hora(m: re.Match) -> str:
    h = int(m.group(1))
    mi = m.group(2)
    texto = _n2w(h) + (" hora" if h == 1 else " horas")
    if mi and int(mi) > 0:
        texto += " e " + _n2w(int(mi))
    return texto


def normalizar(texto: str) -> str:
    """Converte numeros, moedas, datas e abreviacoes para forma falada."""
    t = texto.replace(" ", " ")
    t = re.sub(r"[*_`#>|]", " ", t)  # restos de markdown
    t = re.sub(r"\[(.*?)\]\((.*?)\)", r"\1", t)  # links markdown
    t = re.sub(r"https?://\S+", "", t)
    for padrao, subst in ABREVIACOES.items():
        t = re.sub(padrao, subst, t)
    t = _RE_MOEDA.sub(_moeda, t)
    t = _RE_PORCENTO.sub(_porcento, t)
    t = _RE_DATA.sub(_data, t)
    t = _RE_HORA.sub(_hora, t)
    t = _RE_ORDINAL.sub(lambda m: _n2w(int(m.group(1)), to="ordinal"), t)
    t = _RE_DECIMAL.sub(
        lambda m: f"{_n2w(int(m.group(1)))} virgula {_n2w(int(m.group(2)))}", t
    )
    t = _RE_MILHAR.sub(lambda m: _n2w(int(m.group(0).replace('.', ''))), t)
    t = _RE_NUMERO.sub(lambda m: _n2w(int(m.group(0))), t)
    t = t.replace("&", " e ").replace("/", " ou ").replace("+", " mais ")
    t = re.sub(r"[“”]", '"', t)
    t = re.sub(r"[‘’]", "'", t)
    t = re.sub(r"\s*\.\.\.\s*", "... ", t)
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r" +([,.;:!?])", r"\1", t)
    return t.strip()


_FIM_FRASE = re.compile(r"(?<=[.!?…])\s+|(?<=[.!?…])$|\n+")


@dataclass
class Trecho:
    texto: str
    pausa_depois: float  # segundos de silencio apos o trecho


def dividir(texto: str, max_chars: int = 220, pausa_frase: float = 0.35,
            pausa_paragrafo: float = 0.7) -> list[Trecho]:
    """Divide o texto em frases curtas, preservando paragrafos como pausas maiores.

    Trechos muito longos sao quebrados em virgulas/ponto-e-virgula para ficar
    abaixo de `max_chars` (modelos zero-shot alucinam em textos longos).
    """
    trechos: list[Trecho] = []
    paragrafos = [p.strip() for p in re.split(r"\n\s*\n", texto) if p.strip()]
    for pi, par in enumerate(paragrafos):
        frases = [f.strip() for f in _FIM_FRASE.split(par.replace("\n", " ")) if f and f.strip()]
        for fi, frase in enumerate(frases):
            partes = _quebrar(frase, max_chars)
            for pj, parte in enumerate(partes):
                ultima_do_par = fi == len(frases) - 1 and pj == len(partes) - 1
                pausa = pausa_paragrafo if ultima_do_par else pausa_frase
                if pj < len(partes) - 1:
                    pausa = pausa_frase * 0.6
                trechos.append(Trecho(parte, pausa))
    if trechos:
        trechos[-1].pausa_depois = 0.0
    return trechos


def _quebrar(frase: str, max_chars: int) -> list[str]:
    if len(frase) <= max_chars:
        return [frase]
    partes: list[str] = []
    atual = ""
    for pedaco in re.split(r"(?<=[,;:])\s+", frase):
        if atual and len(atual) + len(pedaco) + 1 > max_chars:
            partes.append(atual.strip())
            atual = pedaco
        else:
            atual = f"{atual} {pedaco}".strip()
    if atual:
        partes.append(atual.strip())
    # Ultimo recurso: quebra por palavras
    saida: list[str] = []
    for p in partes:
        if len(p) <= max_chars:
            saida.append(p)
            continue
        palavras = p.split()
        buf = ""
        for w in palavras:
            if buf and len(buf) + len(w) + 1 > max_chars:
                saida.append(buf)
                buf = w
            else:
                buf = f"{buf} {w}".strip()
        if buf:
            saida.append(buf)
    return saida


def garantir_pontuacao(texto: str) -> str:
    t = texto.strip()
    if t and t[-1] not in ".!?…":
        t += "."
    return t
