# -*- coding: utf-8 -*-
"""Gera documento comercial (DOCX) em estilo de proposta a partir de markdown simples.
Uso: python3 build_proposta_docx.py <md> <docx> <cfg.json>
cfg: titulo, subtitulo, proponente, destinatario, local, data, confidencial, sumario_executivo (lista de parágrafos)."""
import sys, re, json
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.section import WD_ORIENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
MD, OUT, CFGP = sys.argv[1], sys.argv[2], sys.argv[3]
PAGES = json.load(open(sys.argv[4], encoding='utf-8')) if len(sys.argv) > 4 and sys.argv[4] else {}
CFG = json.load(open(CFGP, encoding='utf-8'))
AZUL = RGBColor(0x1F, 0x4E, 0x79); AZUL2 = RGBColor(0x2A, 0x78, 0xD6); CINZA = RGBColor(0x52, 0x51, 0x4E); LARANJA = RGBColor(0xEB, 0x68, 0x34)
doc = Document()
sec = doc.sections[0]; sec.page_width = Cm(21); sec.page_height = Cm(29.7)
sec.left_margin = sec.right_margin = Cm(2.2); sec.top_margin = Cm(2.2); sec.bottom_margin = Cm(2)
st = doc.styles['Normal']; st.font.name = 'Calibri'; st.font.size = Pt(11); st.element.rPr.rFonts.set(qn('w:eastAsia'), 'Calibri')
st.paragraph_format.space_after = Pt(6); st.paragraph_format.line_spacing = 1.15
for lvl, size, color in ((1, 18, AZUL), (2, 13, AZUL2), (3, 11.5, CINZA)):
    h = doc.styles[f'Heading {lvl}']; h.font.name = 'Calibri'; h.font.size = Pt(size); h.font.bold = True; h.font.color.rgb = color
    h.element.rPr.rFonts.set(qn('w:eastAsia'), 'Calibri'); h.paragraph_format.space_before = Pt(14 if lvl == 1 else 10); h.paragraph_format.space_after = Pt(6); h.paragraph_format.keep_with_next = True
def shade(cell, hexcolor):
    tcPr = cell._tc.get_or_add_tcPr(); shd = OxmlElement('w:shd'); shd.set(qn('w:val'), 'clear'); shd.set(qn('w:color'), 'auto'); shd.set(qn('w:fill'), hexcolor); tcPr.append(shd)
def borders(table, color='BFBFBF'):
    tbl = table._tbl; tblPr = tbl.tblPr; b = OxmlElement('w:tblBorders')
    for e in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
        el = OxmlElement(f'w:{e}'); el.set(qn('w:val'), 'single'); el.set(qn('w:sz'), '4'); el.set(qn('w:space'), '0'); el.set(qn('w:color'), color); b.append(el)
    tblPr.append(b)
def runs(par, text, size=None, color=None, bold=None):
    # **negrito** e `código`
    for part in re.split(r'(\*\*[^*]+\*\*|`[^`]+`)', text):
        if not part: continue
        if part.startswith('**'): r = par.add_run(part[2:-2]); r.bold = True
        elif part.startswith('`'): r = par.add_run(part[1:-1]); r.font.name = 'Consolas'; r.font.size = Pt((size or 11) - 1)
        else: r = par.add_run(part)
        if size: r.font.size = Pt(size)
        if color: r.font.color.rgb = color
        if bold is not None and not part.startswith('**'): r.bold = bold
def add_field(run, instr):
    f1 = OxmlElement('w:fldChar'); f1.set(qn('w:fldCharType'), 'begin'); it = OxmlElement('w:instrText'); it.set(qn('xml:space'), 'preserve'); it.text = instr; f2 = OxmlElement('w:fldChar'); f2.set(qn('w:fldCharType'), 'end')
    run._r.append(f1); run._r.append(it); run._r.append(f2)
# ---------- capa ----------
p = doc.add_paragraph(); p.paragraph_format.space_before = Pt(60); runs(p, CFG.get('confidencial', 'PROPOSTA COMERCIAL'), size=11, color=LARANJA, bold=True)
p = doc.add_paragraph(); p.paragraph_format.space_before = Pt(40); runs(p, CFG['titulo'], size=26, color=AZUL, bold=True)
p = doc.add_paragraph(); runs(p, CFG['subtitulo'], size=14, color=CINZA)
p = doc.add_paragraph(); p.paragraph_format.space_before = Pt(80)
for lab, key in (('Destinatário', 'destinatario'), ('Proponente', 'proponente'), ('Local e data', 'data')):
    if CFG.get(key):
        q = doc.add_paragraph(); runs(q, lab + ': ', size=11, color=CINZA, bold=True); runs(q, CFG[key], size=11)
p = doc.add_paragraph(); p.paragraph_format.space_before = Pt(60); runs(p, CFG.get('rodape_capa', ''), size=9, color=CINZA)
doc.add_page_break()
# ---------- sumário executivo ----------
if CFG.get('sumario_executivo'):
    doc.add_heading('Sumário executivo', level=1)
    for par in CFG['sumario_executivo']:
        if par.startswith('- '):
            q = doc.add_paragraph(style='List Bullet'); runs(q, par[2:])
        else:
            q = doc.add_paragraph(); q.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY; runs(q, par)
    doc.add_page_break()
# ---------- sumário (TOC) ----------
doc.add_heading('Sumário', level=1)
def heading_text(raw):
    return re.sub(r'^(\d+(\.\d+)*\.?)\s*', '', raw).strip()
H1 = [heading_text(m.group(2)) for m in (re.match(r'^(#)\s+(.*)$', l) for l in open(MD, encoding='utf-8')) if m]
from docx.enum.text import WD_TAB_ALIGNMENT, WD_TAB_LEADER
for h in H1:
    tp = doc.add_paragraph(); tp.paragraph_format.space_after = Pt(3)
    tp.paragraph_format.tab_stops.add_tab_stop(Cm(16.4), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)
    runs(tp, h, size=11); tp.add_run('\t' + str(PAGES.get(h, '')))
doc.add_page_break()
# ---------- cabeçalho e rodapé ----------
hdr = sec.header.paragraphs[0]; hdr.alignment = WD_ALIGN_PARAGRAPH.RIGHT; runs(hdr, CFG.get('cabecalho', CFG['titulo']), size=8, color=CINZA)
ftr = sec.footer.paragraphs[0]; ftr.alignment = WD_ALIGN_PARAGRAPH.CENTER; runs(ftr, CFG.get('rodape', ''), size=8, color=CINZA); ftr.add_run('   Página '); add_field(ftr.add_run(), 'PAGE')
for r in ftr.runs: r.font.size = Pt(8); r.font.color.rgb = CINZA
# ---------- corpo ----------
lines = open(MD, encoding='utf-8').read().split('\n'); i = 0; caption = None; ntab = 0; figcap = None; nfig = [0]
def table(rows, caption):
    global ntab
    ntab += 1; hdr = rows[0]; body = rows[1:]
    if caption:
        c = doc.add_paragraph(); c.paragraph_format.keep_with_next = True; c.paragraph_format.space_before = Pt(8); runs(c, f'Quadro {ntab} – {caption}', size=10, color=AZUL, bold=True)
    t = doc.add_table(rows=1, cols=len(hdr)); t.alignment = WD_TABLE_ALIGNMENT.CENTER; borders(t); t.autofit = False
    lay = OxmlElement('w:tblLayout'); lay.set(qn('w:type'), 'fixed'); t._tbl.tblPr.append(lay)
    for j, h in enumerate(hdr):
        cell = t.rows[0].cells[j]; shade(cell, '1F4E79'); cell.paragraphs[0].text = ''; runs(cell.paragraphs[0], h, size=9, color=RGBColor(0xFF, 0xFF, 0xFF), bold=True)
    for k, row in enumerate(body):
        cells = t.add_row().cells
        for j, v in enumerate(row):
            if j >= len(cells): break
            cells[j].paragraphs[0].text = ''; runs(cells[j].paragraphs[0], v, size=9)
            if k % 2 == 1: shade(cells[j], 'F2F2F2')
            if re.match(r'^[-–]?[\d.,]+%?$', v.strip()) or v.strip() in ('–', '-'): cells[j].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT
    # larguras: primeira coluna maior
    n = len(hdr); total = 16.6
    w = []
    for j in range(n):
        col = [r[j] for r in body if j < len(r)]
        avg = (sum(min(len(v), 60) for v in col) / len(col)) if col else 0
        w.append(max(min(len(hdr[j]), 18), avg, 6))
    sw = sum(w); widths = [max(2.4 if n >= 4 else 1.8, total * x / sw) for x in w]; sc = total / sum(widths); widths = [x * sc for x in widths]
    for j, col in enumerate(t.columns): col.width = Cm(widths[j])
    for row in t.rows:
        for j, cell in enumerate(row.cells):
            cell.width = Cm(widths[j])
            for pp in cell.paragraphs: pp.paragraph_format.space_after = Pt(1); pp.paragraph_format.space_before = Pt(1); pp.paragraph_format.line_spacing = 1.0
    for row in t.rows:
        trPr = row._tr.get_or_add_trPr(); cs = OxmlElement('w:cantSplit'); trPr.append(cs)
    tr0 = t.rows[0]._tr.get_or_add_trPr(); th = OxmlElement('w:tblHeader'); tr0.append(th)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
while i < len(lines):
    ln = lines[i].rstrip()
    if not ln.strip(): i += 1; continue
    m = re.match(r'^(#{1,3})\s+(.*)$', ln)
    if m:
        lvl = len(m.group(1)); txt = re.sub(r'^(\d+(\.\d+)*\.?|APÊNDICE [A-Z] –)\s*', lambda mm: mm.group(0) if mm.group(0).startswith('APÊNDICE') else '', m.group(2)).strip()
        if lvl == 1 and ntab is not None and i > 0: pass
        doc.add_heading(txt, level=lvl); i += 1; continue
    if ln.startswith('Tabela:') or ln.startswith('Quadro:'):
        caption = ln.split(':', 1)[1].strip(); i += 1; continue
    if ln.startswith('Figura:'):
        figcap = ln.split(':', 1)[1].strip(); i += 1; continue
    m = re.match(r'^!\[[^\]]*\]\(([^)]+)\)$', ln)
    if m:
        import os
        nfig[0] += 1; img = os.path.join(os.path.dirname(os.path.abspath(MD)), m.group(1))
        c = doc.add_paragraph(); c.paragraph_format.keep_with_next = True; c.paragraph_format.space_before = Pt(8); runs(c, f'Figura {nfig[0]} – {figcap or ""}', size=10, color=AZUL, bold=True)
        pic = doc.add_paragraph(); pic.alignment = WD_ALIGN_PARAGRAPH.CENTER; pic.add_run().add_picture(img, width=Cm(16.4)); figcap = None; i += 1; continue
    if ln.startswith('|'):
        rows = []
        while i < len(lines) and lines[i].startswith('|'):
            cells = [c.strip() for c in lines[i].strip().strip('|').split('|')]
            if not all(re.match(r'^:?-+:?$', c) for c in cells): rows.append(cells)
            i += 1
        table(rows, caption); caption = None; continue
    if ln.startswith('Nota:') or ln.startswith('Fonte:'):
        q = doc.add_paragraph(); runs(q, ln, size=9, color=CINZA); i += 1; continue
    if re.match(r'^- ', ln):
        q = doc.add_paragraph(style='List Bullet'); runs(q, ln[2:]); i += 1; continue
    m = re.match(r'^(\d+)\. (.*)$', ln)
    if m:
        q = doc.add_paragraph(); q.paragraph_format.left_indent = Cm(0.9); q.paragraph_format.first_line_indent = Cm(-0.6); q.paragraph_format.space_after = Pt(3); q.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        runs(q, m.group(1) + '.\t'); q.paragraph_format.tab_stops.add_tab_stop(Cm(0.9)); runs(q, m.group(2)); i += 1; continue
    q = doc.add_paragraph(); q.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY; runs(q, ln); i += 1
doc.save(OUT); print('OK', OUT)
