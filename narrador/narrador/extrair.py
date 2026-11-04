"""Extracao de texto limpo para narracao com o MarkItDown (Microsoft, MIT).

Converte PDF, PowerPoint, Word, Excel (e HTML, CSV...) em Markdown e depois em
"texto falado": tabelas viram frases, listas viram sentencas, cabecalhos viram
pausas. Resultado: um roteiro por slide / pagina / aba.

    narrador roteiro relatorio.pdf          # -> relatorio.roteiro.md
    narrador roteiro planilha.xlsx
    narrador roteiro apresentacao.pptx      # usa as notas do orador quando existirem
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from .util import ErroNarrador, console


@dataclass
class Secao:
    titulo: str
    texto: str
    origem: str = ""  # "slide 3", "pagina 2", "aba Receitas"


@dataclass
class Documento:
    nome: str
    secoes: list[Secao] = field(default_factory=list)


def _markitdown(caminho: Path) -> str:
    try:
        from markitdown import MarkItDown
    except ImportError as e:
        raise ErroNarrador("markitdown nao instalado. Rode: pip install 'markitdown[pdf,pptx,docx,xlsx]'") from e
    md = MarkItDown(enable_plugins=False)
    try:
        return md.convert(str(caminho)).text_content or ""
    except Exception as e:  # noqa: BLE001
        raise ErroNarrador(f"MarkItDown nao conseguiu ler {caminho.name}: {e}") from e


# --------------------------------------------------------------------------- #
# Markdown -> texto falado
# --------------------------------------------------------------------------- #

def _tabela_para_frases(linhas: list[str]) -> str:
    """Tabela markdown -> 'Coluna: valor, coluna: valor.' por linha."""
    celulas = [[c.strip() for c in l.strip().strip("|").split("|")] for l in linhas]
    celulas = [c for c in celulas if c and not all(re.fullmatch(r":?-{2,}:?", x or "-") for x in c)]
    if not celulas:
        return ""
    cab = celulas[0]
    if len(celulas) == 1:
        return ", ".join(x for x in cab if x) + "."
    frases = []
    for linha in celulas[1:]:
        partes = []
        for i, val in enumerate(linha):
            val = val.strip()
            if not val or val.lower() in {"nan", "none", "-"}:
                continue
            nome = cab[i].strip() if i < len(cab) else ""
            if nome and not nome.startswith("Unnamed"):
                partes.append(f"{nome}: {val}")
            else:
                partes.append(val)
        if partes:
            frases.append(", ".join(partes) + ".")
    return "\n".join(frases)


def markdown_para_fala(md: str) -> str:
    """Limpa markdown para leitura em voz alta."""
    saida: list[str] = []
    tabela: list[str] = []
    for linha in md.splitlines():
        l = linha.rstrip()
        if l.strip().startswith("|"):
            tabela.append(l)
            continue
        if tabela:
            saida.append(_tabela_para_frases(tabela))
            tabela = []
        if not l.strip():
            saida.append("")
            continue
        l = re.sub(r"<!--.*?-->", "", l)
        l = re.sub(r"^#{1,6}\s*", "", l)                      # cabecalho -> frase
        l = re.sub(r"^\s*[-*+]\s+", "", l)                   # bullets
        l = re.sub(r"^\s*\d+[.)]\s+", "", l)                 # listas numeradas
        l = re.sub(r"!\[.*?\]\(.*?\)", "", l)                # imagens
        l = re.sub(r"\[(.*?)\]\(.*?\)", r"\1", l)            # links
        l = re.sub(r"[*_`~]+", "", l)
        l = re.sub(r"https?://\S+", "", l)
        l = re.sub(r"\s{2,}", " ", l).strip()
        if l and l[-1] not in ".!?:…":
            l += "."
        if l:
            saida.append(l)
    if tabela:
        saida.append(_tabela_para_frases(tabela))
    texto = "\n".join(saida)
    return re.sub(r"\n{3,}", "\n\n", texto).strip()


# --------------------------------------------------------------------------- #
# Divisao em secoes por tipo de arquivo
# --------------------------------------------------------------------------- #

def _secoes_pptx(md: str) -> list[Secao]:
    blocos = re.split(r"<!--\s*Slide number:\s*(\d+)\s*-->", md)
    secoes = []
    for i in range(1, len(blocos) - 1, 2):
        num, conteudo = int(blocos[i]), blocos[i + 1]
        m = re.search(r"^#+\s*(.+)$", conteudo, re.M)
        titulo = m.group(1).strip() if m else ""
        notas = ""
        mn = re.search(r"###\s*Notes:\s*(.*)$", conteudo, re.S)
        if mn:
            notas = mn.group(1).strip()
            conteudo = conteudo[: mn.start()]
        texto = markdown_para_fala(notas) if notas else markdown_para_fala(conteudo)
        secoes.append(Secao(titulo, texto, f"slide {num}"))
    return secoes


def _secoes_pdf(caminho: Path, md: str) -> list[Secao]:
    paginas = md.split("\x0c") if "\x0c" in md else []
    if len(paginas) <= 1:
        try:
            import pymupdf
            with pymupdf.open(caminho) as doc:
                paginas = [pg.get_text() for pg in doc]
        except Exception:
            paginas = [md]
    secoes = []
    for i, p in enumerate(paginas, start=1):
        texto = markdown_para_fala(p)
        if texto.strip():
            secoes.append(Secao("", texto, f"pagina {i}"))
    return secoes


def _secoes_por_cabecalho(md: str, nivel: str, rotulo: str) -> list[Secao]:
    partes = re.split(rf"^{nivel}\s+(.+)$", md, flags=re.M)
    secoes = []
    if partes[0].strip():
        secoes.append(Secao("", markdown_para_fala(partes[0]), rotulo))
    for i in range(1, len(partes) - 1, 2):
        titulo, corpo = partes[i].strip(), partes[i + 1]
        texto = markdown_para_fala(corpo)
        if titulo or texto:
            secoes.append(Secao(titulo, (titulo + ".\n\n" if titulo else "") + texto, f"{rotulo} {titulo}".strip()))
    return secoes


def extrair(caminho: Path) -> Documento:
    """Le qualquer documento suportado e devolve secoes com texto pronto para narrar."""
    caminho = Path(caminho)
    if not caminho.exists():
        raise ErroNarrador(f"Arquivo nao encontrado: {caminho}")
    suf = caminho.suffix.lower()
    md = _markitdown(caminho)
    doc = Documento(nome=caminho.stem)
    if suf == ".pptx":
        doc.secoes = _secoes_pptx(md)
    elif suf == ".pdf":
        doc.secoes = _secoes_pdf(caminho, md)
    elif suf in {".xlsx", ".xls", ".xlsm"}:
        doc.secoes = _secoes_por_cabecalho(md, "##", "aba")
    elif suf in {".docx", ".doc", ".md", ".html", ".htm", ".txt", ".csv"}:
        doc.secoes = _secoes_por_cabecalho(md, "#{1,2}", "secao")
    if not doc.secoes:
        doc.secoes = [Secao("", markdown_para_fala(md), "documento")]
    vazias = [s.origem for s in doc.secoes if not s.texto.strip()]
    if vazias:
        console.print(f"[yellow]Aviso:[/] sem texto em: {', '.join(vazias[:8])}")
    return doc


def escrever_roteiro(doc: Documento, destino: Path) -> Path:
    linhas = [f"# Roteiro de narracao: {doc.nome}", "",
              "Gerado com MarkItDown. Edite o texto de cada bloco; paragrafos separados geram pausas.", ""]
    for i, s in enumerate(doc.secoes, start=1):
        cab = f"## Slide {i}" + (f" - {s.titulo}" if s.titulo else "") + (f"  <!-- {s.origem} -->" if s.origem else "")
        linhas += [cab, "", s.texto or "(sem texto)", ""]
    destino.write_text("\n".join(linhas), encoding="utf-8")
    return destino
