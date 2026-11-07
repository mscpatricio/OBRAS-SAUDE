# -*- coding: utf-8 -*-
"""Gera o DOCX do estudo em formato ABNT (NBR 14724, 6024, 6023, 10520, 6027, 6028) a partir do Markdown.
Uso: python3 build_docx_abnt.py <md> <docx> [pagina_inicial_textual] [toc.json]
Passo 1 gera com sumário provisório; o LibreOffice converte para PDF; o script pagina.py extrai páginas; passo 2 regrava com páginas corretas."""
import re, sys, json, os
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING, WD_BREAK
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.section import WD_SECTION
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

MD=sys.argv[1]; OUT=sys.argv[2]
START=int(sys.argv[3]) if len(sys.argv)>3 else 1
PAGES=json.load(open(sys.argv[4])) if len(sys.argv)>4 and sys.argv[4] and os.path.exists(sys.argv[4]) else {}
# numeração ABNT: conta a partir da folha de rosto (capa excluída); o passo 1 devolve páginas relativas ao 1º texto
if PAGES:
    _off=PAGES.get('_first_textual_page',1)-2
    PAGES={k:(v+_off if isinstance(v,int) and not k.startswith('_') else v) for k,v in PAGES.items()}
    START=PAGES['_first_textual_page']-1
BASE=os.path.dirname(os.path.abspath(MD))
CFG=json.load(open(sys.argv[5],encoding='utf-8')) if len(sys.argv)>5 and sys.argv[5] else {}
AUTOR=CFG.get('autor','Patrício Almeida')
TITULO=CFG.get('titulo','SAÚDE NO ESTADO DO AMAPÁ: LEVANTAMENTO DA PRODUÇÃO HOSPITALAR E AMBULATORIAL E ESTUDO ANALÍTICO PARA A TRANSIÇÃO DE GOVERNO 2026/2027')
SUBTITULO=CFG.get('subtitulo','Série histórica 2022–2026 com base em dados públicos (DATASUS, SIOPS, IBGE)')
LOCAL=CFG.get('local','Macapá'); ANO=CFG.get('ano','2026')
FONT='Arial'

doc=Document()
sec=doc.sections[0]
sec.page_height=Cm(29.7); sec.page_width=Cm(21.0)
sec.top_margin=Cm(3); sec.left_margin=Cm(3); sec.bottom_margin=Cm(2); sec.right_margin=Cm(2)
sec.header_distance=Cm(1.5)

def set_font(run,size=12,bold=None,italic=None):
    run.font.name=FONT; run.font.size=Pt(size)
    rpr=run._element.get_or_add_rPr(); rf=rpr.find(qn('w:rFonts'))
    if rf is None: rf=OxmlElement('w:rFonts'); rpr.append(rf)
    for a in ('w:ascii','w:hAnsi','w:cs','w:eastAsia'): rf.set(qn(a),FONT)
    if bold is not None: run.bold=bold
    if italic is not None: run.italic=italic
st=doc.styles['Normal']; st.font.name=FONT; st.font.size=Pt(12)
st.element.rPr.rFonts.set(qn('w:eastAsia'),FONT)
pf=st.paragraph_format; pf.line_spacing=1.5; pf.space_after=Pt(0); pf.space_before=Pt(0); pf.alignment=WD_ALIGN_PARAGRAPH.JUSTIFY

def para(text='',align=WD_ALIGN_PARAGRAPH.JUSTIFY,size=12,bold=False,italic=False,indent_first=True,spacing=1.5,before=0,after=0,left=0,hanging=0,keep=False):
    p=doc.add_paragraph(); p.alignment=align
    f=p.paragraph_format; f.line_spacing=spacing; f.space_before=Pt(before); f.space_after=Pt(after)
    if indent_first: f.first_line_indent=Cm(1.25)
    if left: f.left_indent=Cm(left)
    if hanging: f.first_line_indent=Cm(-hanging); f.left_indent=Cm(left+hanging)
    if keep: f.keep_with_next=True
    if text: add_inline(p,text,size,bold,italic)
    return p

INL=re.compile(r'(\*\*.+?\*\*|\*[^*]+?\*|`[^`]+`)')
def add_inline(p,text,size=12,bold=False,italic=False):
    for tok in INL.split(text):
        if not tok: continue
        b,i,t=bold,italic,tok
        if tok.startswith('**'): b=True; t=tok[2:-2]
        elif tok.startswith('`'): i=True; t=tok[1:-1]
        elif tok.startswith('*'): i=True; t=tok[1:-1]
        t=t.replace('\\*','*')
        r=p.add_run(t); set_font(r,size,b,i)

def page_break(): doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)

def heading(text,level,numbered=True):
    # ABNT 6024: seção primária caixa alta negrito; secundária negrito; terciária itálico negrito
    p=doc.add_paragraph(); f=p.paragraph_format; f.line_spacing=1.5; f.keep_with_next=True
    f.space_before=Pt(18 if level==1 else 12); f.space_after=Pt(12); p.alignment=WD_ALIGN_PARAGRAPH.LEFT
    text=re.sub(r'^(\d+)\. ',r'\1 ',text)
    t=text.upper() if level==1 else text
    r=p.add_run(t); set_font(r,12,True,level==3)
    return p

def pretext_title(text):
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_after=Pt(18); p.paragraph_format.line_spacing=1.5
    r=p.add_run(text); set_font(r,12,True)

def set_cell_borders(cell,top=None,bottom=None):
    tcPr=cell._tc.get_or_add_tcPr(); b=OxmlElement('w:tcBorders')
    for side in ('top','left','bottom','right'):
        el=OxmlElement(f'w:{side}')
        val={'top':top,'bottom':bottom}.get(side)
        if val: el.set(qn('w:val'),'single'); el.set(qn('w:sz'),str(val)); el.set(qn('w:color'),'000000')
        else: el.set(qn('w:val'),'nil')
        b.append(el)
    tcPr.append(b)

def shade(cell,hexcolor):
    tcPr=cell._tc.get_or_add_tcPr(); s=OxmlElement('w:shd'); s.set(qn('w:val'),'clear'); s.set(qn('w:color'),'auto'); s.set(qn('w:fill'),hexcolor); tcPr.append(s)

def is_num(s):
    return bool(re.fullmatch(r'[−\-+]?[\d\.]+(,\d+)?%?|—|-|\*?[\d\.,]+%?|×[\d\.]+|\([^)]*\)|\(2022\)',s.strip()))

def add_table(rows,aligns):
    ncol=len(rows[0])
    t=doc.add_table(rows=len(rows),cols=ncol); t.alignment=WD_TABLE_ALIGNMENT.CENTER; t.autofit=False
    size=8 if ncol>=8 else (9 if ncol>=6 or len(rows)>18 else 10)
    # larguras: colunas numéricas dimensionadas pelo texto mais longo (sem quebra); 1ª coluna recebe o restante
    fac=size*0.021
    lens=[max(len(re.sub(r'\*','',r[j]).strip()) for r in rows[1:]) for j in range(ncol)]
    hdrw=[max(len(w) for w in rows[0][j].split()) for j in range(ncol)]
    others=[max(min(lens[j],12)*fac+0.55, hdrw[j]*fac+0.7, 1.25) for j in range(1,ncol)]
    first=16-sum(others)
    if first<3.4:
        k=(16-3.4)/sum(others); others=[o*k for o in others]; first=3.4
    widths=[first]+others
    for i,row in enumerate(rows):
        total=row[0].replace('*','').strip().lower() in ('total','amapá','brasil') or row[0].startswith('**')
        for j,val in enumerate(row):
            c=t.cell(i,j); c.text=''; c.width=Cm(widths[j])
            p=c.paragraphs[0]; p.paragraph_format.line_spacing=1.0; p.paragraph_format.space_after=Pt(1); p.paragraph_format.space_before=Pt(1); p.paragraph_format.first_line_indent=Cm(0)
            v=val.strip()
            bold = i==0 or total
            if v.startswith('**') and v.endswith('**'): v=v[2:-2]; bold=True
            v=v.replace('\\*','*')
            add_inline(p,v,size,bold)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if i==0 else (WD_ALIGN_PARAGRAPH.RIGHT if (aligns[j]=='r' or (j>0 and is_num(v))) else WD_ALIGN_PARAGRAPH.LEFT)
            if i==0: set_cell_borders(c,top=12,bottom=6); shade(c,'EDEDED')
            elif i==len(rows)-1: set_cell_borders(c,bottom=12)
            else: set_cell_borders(c)
            c.vertical_alignment=1
    for j,w in enumerate(widths): t.columns[j].width=Cm(w)
    trPr=t.rows[0]._tr.get_or_add_trPr(); h=OxmlElement('w:tblHeader'); h.set(qn('w:val'),'true'); trPr.append(h)
    return t

def caption(label,n,text):
    p=para(f'{label} {n} – {text}',align=WD_ALIGN_PARAGRAPH.LEFT,size=12,indent_first=False,spacing=1.0,before=12,after=6,keep=True)
    return p
def source(text):
    p=para(text,align=WD_ALIGN_PARAGRAPH.LEFT,size=10,indent_first=False,spacing=1.0,before=4,after=12)
    return p

def add_page_number_field(section,start):
    section.header.is_linked_to_previous=False
    hp=section.header.paragraphs[0]; hp.alignment=WD_ALIGN_PARAGRAPH.RIGHT
    r=hp.add_run(); set_font(r,10)
    for tag,txt in (('begin',None),(None,'PAGE'),('end',None)):
        if tag:
            fc=OxmlElement('w:fldChar'); fc.set(qn('w:fldCharType'),tag); r._r.append(fc)
        else:
            it=OxmlElement('w:instrText'); it.set(qn('xml:space'),'preserve'); it.text=txt; r._r.append(it)
    sectPr=section._sectPr; pg=OxmlElement('w:pgNumType'); pg.set(qn('w:start'),str(start)); sectPr.append(pg)

# ---------------- parse markdown ----------------
src=open(MD,encoding='utf-8').read().split('\n')
blocks=[]; i=0
while i<len(src):
    l=src[i]
    if not l.strip(): i+=1; continue
    if l.startswith('# '): blocks.append(('h1',l[2:].strip())); i+=1; continue
    if l.startswith('## '): blocks.append(('h2',l[3:].strip())); i+=1; continue
    if l.startswith('### '): blocks.append(('h3',l[4:].strip())); i+=1; continue
    if l.startswith('|'):
        rows=[]
        while i<len(src) and src[i].startswith('|'):
            rows.append([c for c in src[i].strip().strip('|').split('|')]); i+=1
        sep=rows[1]; aligns=['r' if c.strip().endswith(':') else 'l' for c in sep]
        blocks.append(('table',[rows[0]]+rows[2:],aligns)); continue
    m=re.match(r'!\[\]\((.+)\)',l.strip())
    if m: blocks.append(('img',m.group(1))); i+=1; continue
    if l.startswith('Tabela: '): blocks.append(('tcap',l[8:].strip())); i+=1; continue
    if l.startswith('Figura: '): blocks.append(('fcap',l[8:].strip())); i+=1; continue
    if l.startswith('- '):
        items=[]
        while i<len(src) and src[i].startswith('- '): items.append(src[i][2:].strip()); i+=1
        blocks.append(('ul',items)); continue
    if re.match(r'^\d+\. ',l):
        items=[]
        while i<len(src) and re.match(r'^\d+\. ',src[i]): items.append(re.sub(r'^\d+\. ','',src[i]).strip()); i+=1
        blocks.append(('ol',items)); continue
    # paragraph (may span lines)
    buf=[l.strip()]; i+=1
    while i<len(src) and src[i].strip() and not src[i].startswith(('#','|','- ','!','Tabela: ','Figura: ')) and not re.match(r'^\d+\. ',src[i]):
        buf.append(src[i].strip()); i+=1
    text=' '.join(buf)
    if text.startswith(('Fonte:','\\* preliminar','* preliminar')): blocks.append(('src',text))
    else: blocks.append(('p',text))

# numbering of tables/figures and collect lists
tabs=[];figs=[]
tn=fn=0
for b in blocks:
    if b[0]=='tcap': tn+=1; tabs.append((tn,b[1]))
    if b[0]=='fcap': fn+=1; figs.append((fn,b[1]))
heads=[(b[0],b[1]) for b in blocks if b[0] in ('h1','h2')]

# ---------------- pré-textuais ----------------
# CAPA
for _ in range(2): para('',indent_first=False)
p=para(AUTOR.upper(),align=WD_ALIGN_PARAGRAPH.CENTER,bold=True,indent_first=False)
for _ in range(8): para('',indent_first=False)
para(TITULO,align=WD_ALIGN_PARAGRAPH.CENTER,bold=True,indent_first=False)
para(SUBTITULO,align=WD_ALIGN_PARAGRAPH.CENTER,indent_first=False,before=12)
for _ in range(14): para('',indent_first=False)
para(LOCAL.upper(),align=WD_ALIGN_PARAGRAPH.CENTER,bold=True,indent_first=False)
para(ANO,align=WD_ALIGN_PARAGRAPH.CENTER,bold=True,indent_first=False)
page_break()
# FOLHA DE ROSTO
for _ in range(2): para('',indent_first=False)
para(AUTOR.upper(),align=WD_ALIGN_PARAGRAPH.CENTER,bold=True,indent_first=False)
for _ in range(7): para('',indent_first=False)
para(TITULO,align=WD_ALIGN_PARAGRAPH.CENTER,bold=True,indent_first=False)
para(SUBTITULO,align=WD_ALIGN_PARAGRAPH.CENTER,indent_first=False,before=12)
for _ in range(4): para('',indent_first=False)
nat=para(CFG.get('natureza','Estudo analítico elaborado como subsídio técnico à equipe de transição de governo do Estado do Amapá, área da saúde (Secretaria de Estado da Saúde – SESA/AP), com base em dados públicos extraídos em 6 de novembro de 2026.'),align=WD_ALIGN_PARAGRAPH.JUSTIFY,indent_first=False,spacing=1.0,left=8)
for _ in range(9): para('',indent_first=False)
para(LOCAL.upper(),align=WD_ALIGN_PARAGRAPH.CENTER,bold=True,indent_first=False)
para(ANO,align=WD_ALIGN_PARAGRAPH.CENTER,bold=True,indent_first=False)
page_break()
# RESUMO
pretext_title('RESUMO')
resumo=CFG.get('resumo') or ('Este estudo apresenta o levantamento da produção hospitalar e ambulatorial, da rede física, da força de trabalho, do financiamento e dos indicadores vitais da saúde no Estado do Amapá na série histórica 2022–2026, com a finalidade de subsidiar a transição de governo 2026/2027 na Secretaria de Estado da Saúde (SESA/AP). Os dados foram extraídos de bases públicas (DATASUS/TABNET: SIH, SIA, CNES, SIM e SINASC; SIOPS; IBGE/SIDRA; edital do concurso SESA 001/2026) e tabulados em planilha com 129 tabelas. Entre 2022 e 2025, as internações SUS cresceram 40,1% (41.312 para 57.873 AIH) e o valor ambulatorial 93,3% (R$ 77,0 milhões para R$ 148,7 milhões); os leitos SUS aumentaram 14,8% e o número de médicos cadastrados 54%; a despesa estadual com saúde por habitante subiu 84,5% e é a maior do país. Permanecem, contudo, o menor valor médio de internação entre as unidades da federação, apenas 2,3% de internações de alta complexidade, mortalidade infantil de 17,8 por mil nascidos vivos (3ª maior do Brasil em 2024) e dependência de prestadores externos. Identificou-se crescimento atípico do faturamento de procedimentos vasculares (de R$ 15 mil em 2022 para R$ 25,6 milhões em 2025 no SIA, com 7.375 internações de trombectomia venosa de permanência zero em 2025) e divergência entre leitos de UTI existentes (139) e cadastrados como SUS (19). O estudo conclui com pontos de atenção, lista de documentos a requisitar e agenda de prioridades para os primeiros cem dias da nova gestão.')
para(resumo,indent_first=False,spacing=1.0)
para('',indent_first=False)
para('**Palavras-chave:** '+CFG.get('palavras_chave','Sistema Único de Saúde; Amapá; produção hospitalar; produção ambulatorial; financiamento da saúde; transição de governo.'),indent_first=False,spacing=1.0)
page_break()
# LISTA DE FIGURAS
def dotline(label,page,bold=False):
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.LEFT; f=p.paragraph_format; f.line_spacing=1.5; f.space_after=Pt(0)
    tab_stops=f.tab_stops; from docx.enum.text import WD_TAB_ALIGNMENT, WD_TAB_LEADER
    tab_stops.add_tab_stop(Cm(16),WD_TAB_ALIGNMENT.RIGHT,WD_TAB_LEADER.DOTS)
    f.left_indent=Cm(0); f.first_line_indent=Cm(0)
    r=p.add_run(label); set_font(r,12,bold); r2=p.add_run('\t'+str(page)); set_font(r2,12,bold)
pretext_title('LISTA DE FIGURAS')
for n,t in figs: dotline(f'Figura {n} – {t}',PAGES.get(f'fig{n}','000'))
page_break()
pretext_title('LISTA DE TABELAS')
for n,t in tabs: dotline(f'Tabela {n} – {t}',PAGES.get(f'tab{n}','000'))
page_break()
pretext_title('LISTA DE ABREVIATURAS E SIGLAS')
siglas=CFG.get('siglas') or [('AIH','Autorização de Internação Hospitalar'),('Alap','Assembleia Legislativa do Estado do Amapá'),('APAC','Autorização de Procedimentos de Alta Complexidade'),('ASPS','Ações e Serviços Públicos de Saúde'),('BPA','Boletim de Produção Ambulatorial'),('CBO','Classificação Brasileira de Ocupações'),('CID-10','Classificação Estatística Internacional de Doenças, 10ª revisão'),('CNES','Cadastro Nacional de Estabelecimentos de Saúde'),('DATASUS','Departamento de Informática do SUS'),('DENASUS','Departamento Nacional de Auditoria do SUS'),('Ebserh','Empresa Brasileira de Serviços Hospitalares'),('FAEC','Fundo de Ações Estratégicas e Compensação'),('FES','Fundo Estadual de Saúde'),('FNS','Fundo Nacional de Saúde'),('HCA','Hospital da Criança e do Adolescente'),('HCAL','Hospital de Clínicas Dr. Alberto Lima'),('HE','Hospital de Emergência'),('HU-UNIFAP','Hospital Universitário da Universidade Federal do Amapá'),('IBGE','Instituto Brasileiro de Geografia e Estatística'),('LOA','Lei Orçamentária Anual'),('MAC','Média e Alta Complexidade'),('OCI','Oferta de Cuidados Integrados'),('PCCS','Plano de Cargos, Carreiras e Salários'),('PLOA','Projeto de Lei Orçamentária Anual'),('SESA/AP','Secretaria de Estado da Saúde do Amapá'),('SIA/SUS','Sistema de Informações Ambulatoriais do SUS'),('SIH/SUS','Sistema de Informações Hospitalares do SUS'),('SIM','Sistema de Informações sobre Mortalidade'),('SINASC','Sistema de Informações sobre Nascidos Vivos'),('SIOPS','Sistema de Informações sobre Orçamentos Públicos em Saúde'),('SUS','Sistema Único de Saúde'),('TCE-AP','Tribunal de Contas do Estado do Amapá'),('TFD','Tratamento Fora de Domicílio'),('TMI','Taxa de mortalidade infantil'),('UCI','Unidade de Cuidados Intermediários'),('UF','Unidade da Federação'),('UPA','Unidade de Pronto Atendimento'),('UTI','Unidade de Terapia Intensiva')]
for s,d in siglas:
    p=para('',indent_first=False,spacing=1.5,left=0,hanging=3); r=p.add_run(s); set_font(r,12,True); r2=p.add_run('\t'+d); set_font(r2,12)
    p.paragraph_format.tab_stops.add_tab_stop(Cm(3))
page_break()
pretext_title('SUMÁRIO')
hn=0
for kind,t in heads:
    key='h_'+re.sub(r'\W+','_',t)[:60]
    tt=re.sub(r'^(\d+)\. ',r'\1 ',t)
    if kind=='h1': dotline(tt.upper(),PAGES.get(key,'000'),bold=True)
    else: dotline(t,PAGES.get(key,'000'))
dotline('REFERÊNCIAS',PAGES.get('h_REF','000'),bold=True)
# ---------------- textuais ----------------
sec2=doc.add_section(WD_SECTION.NEW_PAGE)
sec2.top_margin=Cm(3); sec2.left_margin=Cm(3); sec2.bottom_margin=Cm(2); sec2.right_margin=Cm(2); sec2.header_distance=Cm(1.5)
add_page_number_field(sec2,START)
tn=fn=0
first_h1=True
for b in blocks:
    k=b[0]
    if k=='h1':
        if not first_h1: page_break()
        first_h1=False
        heading(b[1],1)
    elif k=='h2': heading(b[1],2)
    elif k=='h3': heading(b[1],3)
    elif k=='p': para(b[1])
    elif k=='src': source(b[1].replace('\\*','*'))
    elif k=='tcap': tn+=1; caption('Tabela',tn,b[1])
    elif k=='fcap': fn+=1; caption('Figura',fn,b[1])
    elif k=='table': add_table(b[1],b[2])
    elif k=='img':
        p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.first_line_indent=Cm(0); p.paragraph_format.space_after=Pt(0)
        p.add_run().add_picture(os.path.join(BASE,b[1]),width=Cm(15.5))
    elif k=='ul':
        for it in b[1]:
            p=para('',indent_first=False,left=0,hanging=0.75,spacing=1.5); add_inline(p,'– '+it)
    elif k=='ol':
        for n,it in enumerate(b[1],1):
            p=para('',indent_first=False,left=0,hanging=0.75,spacing=1.5); add_inline(p,f'{n}) '+it)
# ---------------- REFERÊNCIAS (NBR 6023) ----------------
page_break()
pretext_title('REFERÊNCIAS')
refs=CFG.get('referencias') or [
 'AMAPÁ. Assembleia Legislativa. **Alap aprova Lei Orçamentária Anual para o exercício financeiro de 2026**. Macapá: Alap, 27 dez. 2025. Disponível em: https://www.diariodoamapa.com.br/cadernos/politica/alap-aprova-lei-orcamentaria-anual-para-o-exercicio-financeiro-de-2026/. Acesso em: 6 nov. 2026.',
 'AMAPÁ. Secretaria de Estado da Administração; Secretaria de Estado da Saúde. **Edital de Concurso Público nº 001/2026**: abertura de inscrições para cargos do Quadro de Pessoal da Saúde Estadual. Macapá: SEAD; SESA; Instituto AOCP, 11 set. 2026.',
 'BRASIL. Instituto Brasileiro de Geografia e Estatística. **Estimativas da população residente para os municípios e para as unidades da federação**: tabela 6579. Rio de Janeiro: IBGE, 2026. Disponível em: https://apisidra.ibge.gov.br/values/t/6579. Acesso em: 6 nov. 2026.',
 'BRASIL. Ministério da Saúde. DATASUS. **Cadastro Nacional de Estabelecimentos de Saúde (CNES)**: recursos físicos (leitos de internação e complementares, equipamentos), estabelecimentos e recursos humanos – Amapá. Brasília, DF: Ministério da Saúde, 2026a. Disponível em: http://tabnet.datasus.gov.br/cgi/deftohtm.exe?cnes/cnv/leiintap.def. Acesso em: 6 nov. 2026.',
 'BRASIL. Ministério da Saúde. DATASUS. **Sistema de Informações Ambulatoriais do SUS (SIA/SUS)**: produção ambulatorial por local de atendimento – Amapá e Brasil por UF. Brasília, DF: Ministério da Saúde, 2026b. Disponível em: http://tabnet.datasus.gov.br/cgi/deftohtm.exe?sia/cnv/qaap.def. Acesso em: 6 nov. 2026.',
 'BRASIL. Ministério da Saúde. DATASUS. **Sistema de Informações Hospitalares do SUS (SIH/SUS)**: produção hospitalar por local de internação e por local de residência; morbidade hospitalar – Amapá e Brasil por UF. Brasília, DF: Ministério da Saúde, 2026c. Disponível em: http://tabnet.datasus.gov.br/cgi/deftohtm.exe?sih/cnv/qiap.def. Acesso em: 6 nov. 2026.',
 'BRASIL. Ministério da Saúde. DATASUS. **Sistema de Informações sobre Mortalidade (SIM)**: óbitos por residência e óbitos infantis – Amapá e Brasil por UF. Brasília, DF: Ministério da Saúde, 2026d. Disponível em: http://tabnet.datasus.gov.br/cgi/deftohtm.exe?sim/cnv/obt10ap.def. Acesso em: 6 nov. 2026.',
 'BRASIL. Ministério da Saúde. DATASUS. **Sistema de Informações sobre Nascidos Vivos (SINASC)**: nascidos vivos por residência da mãe – Amapá e Brasil por UF. Brasília, DF: Ministério da Saúde, 2026e. Disponível em: http://tabnet.datasus.gov.br/cgi/deftohtm.exe?sinasc/cnv/nvap.def. Acesso em: 6 nov. 2026.',
 'BRASIL. Ministério da Saúde. **Sistema de Informações sobre Orçamentos Públicos em Saúde (SIOPS)**: consulta de indicadores dos estados, Amapá, 2015–2026. Brasília, DF: Ministério da Saúde, 2026f. Disponível em: http://siops.datasus.gov.br/consdetalhereenvio2uf.php. Acesso em: 6 nov. 2026.',
 'BRASIL. Tribunal Superior Eleitoral. **No Amapá, Dr. Furlan (PSD) é o novo governador do estado**. Brasília, DF: TSE, out. 2026. Disponível em: https://www.tse.jus.br/comunicacao/noticias/2026/Outubro/no-amapa-dr-furlan-psd-e-o-novo-governador-do-estado. Acesso em: 6 nov. 2026.',
 'CONASS. **Centro de Radioterapia do Amapá mantém fluxo constante de atendimentos e reforça cuidado humanizado**. Brasília, DF: Conselho Nacional de Secretários de Saúde, 2026. Disponível em: https://www.conass.org.br/centro-de-radioterapia-do-amapa-mantem-fluxo-constante-de-atendimentos-e-reforca-cuidado-humanizado/. Acesso em: 6 nov. 2026.',
 'CONECTAMAPÁ. **Governo do Amapá decreta emergência em saúde pública por avanço de síndromes respiratórias**. Macapá, jun. 2026. Disponível em: https://conectamapa.com/governo-do-amapa-decreta-emergencia-em-saude-publica-por-avanco-de-sindromes-respiratorias/. Acesso em: 6 nov. 2026.',
 'CORREIO DA MANHÃ. **Amapá amplia assistência clínica com entrega de 30 novos leitos**. Rio de Janeiro, jun. 2026. Disponível em: https://www.correiodamanha.com.br/nacional/norte/2026/06/296563-amapa-amplia-assistencia-clinica-com-entrega-de-30-novos-leitos.html. Acesso em: 6 nov. 2026.',
 'DIÁRIO DO AMAPÁ. **Mensagem do governador Clécio prevê Orçamento de mais de R$ 13 bilhões para 2027**. Macapá, 2026. Disponível em: https://www.diariodoamapa.com.br/cadernos/politica/mensagem-do-governador-clecio-preve-orcamento-de-mais-de-r-13-bilhoes-para-2027/. Acesso em: 6 nov. 2026.',
 'DIÁRIO DO PODER. **Decisão judicial freia ruptura hospitalar no Amapá; Governo acusa sabotagem**. Brasília, DF, 2025. Disponível em: https://diariodopoder.com.br/brasil-e-regioes/decisao-judicial-freia-ruptura-hospitalar-no-amapa-governo-acusa-sabotagem. Acesso em: 6 nov. 2026.',
 'EMPRESA BRASILEIRA DE SERVIÇOS HOSPITALARES. Hospital Universitário da Universidade Federal do Amapá. **Carta de Serviços ao Usuário**: abril de 2026. Macapá: Ebserh, 2026. Disponível em: https://www.gov.br/hubrasil/pt-br/hospitais-universitarios/regiao-norte/hu-unifap/acesso-a-informacao/acoes-e-programas/CartadeServiosHUUNIFAPAbrilde2026.pdf. Acesso em: 6 nov. 2026.',
]
for r in refs:
    p=para(r,align=WD_ALIGN_PARAGRAPH.LEFT,indent_first=False,spacing=1.0,after=12)
doc.save(OUT); print('saved',OUT,'tabelas',len(tabs),'figuras',len(figs),'headings',len(heads))
