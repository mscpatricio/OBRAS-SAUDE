# -*- coding: utf-8 -*-
"""Funções comuns aos estudos: leitura das tabelas TABNET, recorte temporal, planilha e gráficos."""
import csv, os, re, math, json
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
C=['#2a78d6','#eb6834','#1baf7a','#eda100','#e87ba4','#008300','#6250d6','#e34948']
INK='#0b0b0b'; INK2='#52514e'; MUTED='#898781'; GRID='#e1e0d9'; SURF='#fcfcfb'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.edgecolor':'#c3c2b7','axes.labelcolor':INK2,'xtick.color':INK2,'ytick.color':INK2,'axes.spines.top':False,'axes.spines.right':False,'figure.facecolor':SURF,'axes.facecolor':SURF})
YMIN=2022
def num(x):
    s=str(x).strip()
    if s in ('-','','...'): return 0.0
    s=s.replace('.','').replace(',','.')
    try: return float(s)
    except: return float('nan')
def load(path):
    if not os.path.exists(path): return None
    rows=list(csv.reader(open(path,encoding='utf-8'),delimiter=';'))
    if not rows: return None
    hdr=rows[0]; body=[]
    for r in rows[1:]:
        if len(r)>len(hdr): k=len(r)-len(hdr); r=[';'.join(r[:k+1])]+r[k+1:]
        if len(r)<len(hdr): r=r+['']*(len(hdr)-len(r))
        body.append(r)
    df=pd.DataFrame(body,columns=hdr)
    for c in hdr[1:]: df[c]=df[c].map(num)
    return df.set_index(hdr[0])
def _yr(label):
    m=re.match(r'^\s*(?:\.\.)?\s*(?:[A-Za-zç]+/)?(\d{4})(?:/[A-Za-z]{3})?(?:\s*\(.*\))?\s*$',str(label))
    return int(m.group(1)) if m else None
def recorte(df,ymin=YMIN):
    cols=[c for c in df.columns if (_yr(c) is None or _yr(c)>=ymin)]
    df=df[cols]; idx=[i for i in df.index if (_yr(i) is None or _yr(i)>=ymin)]
    return df.loc[idx]
def fmt_int(v): return f'{int(round(v)):,}'.replace(',','.')
def fmt_br(v,d=1):
    s=f'{v:,.{d}f}'; return s.replace(',','X').replace('.',',').replace('X','.')
def total(df):
    return df.loc['Total'] if 'Total' in df.index else df.sum()
def sem_total(df): return df.drop('Total',errors='ignore')
import unicodedata
def unaccent(s): return ''.join(c for c in unicodedata.normalize('NFKD',str(s)) if not unicodedata.combining(c))
def nome_mun(s): return re.sub(r'^\d{6}\s+','',str(s)).title().replace(' Do ',' do ').replace(' De ',' de ').replace(' Da ',' da ')
# ---------- planilha ----------
def write_workbook(path,sheets,titulo,subtitulo,fontes):
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment
    from openpyxl.utils import get_column_letter
    wb=Workbook(); ws0=wb.active; ws0.title='Indice'
    ws0['A1']=titulo; ws0['A1'].font=Font(bold=True,size=14); ws0['A2']=subtitulo
    ws0['A4']='Aba'; ws0['B4']='Conteúdo'; ws0['C4']='Observações'
    for c in ('A4','B4','C4'): ws0[c].font=Font(bold=True)
    hdr_fill=PatternFill('solid',fgColor='1F4E79'); hdr_font=Font(bold=True,color='FFFFFF'); tot_font=Font(bold=True)
    rown=5; used=set()
    for name,(df,title,note) in sheets.items():
        if df is None: continue
        sn=name[:31]; k=2
        while sn in used: sn=name[:28]+'_'+str(k); k+=1
        used.add(sn)
        ws0.cell(row=rown,column=1,value=sn).hyperlink=f"#'{sn}'!A1"; ws0.cell(row=rown,column=1).font=Font(color='0563C1',underline='single')
        ws0.cell(row=rown,column=2,value=title); ws0.cell(row=rown,column=3,value=note); rown+=1
        ws=wb.create_sheet(sn); ws['A1']=title; ws['A1'].font=Font(bold=True,size=12); ws['A2']=note; ws['A2'].font=Font(italic=True,color='595959')
        d=df.reset_index()
        for j,col in enumerate(d.columns,1):
            c=ws.cell(row=4,column=j,value=str(col)); c.fill=hdr_fill; c.font=hdr_font; c.alignment=Alignment(wrap_text=True,vertical='center')
        for i,row in enumerate(d.itertuples(index=False),5):
            for j,v in enumerate(row,1):
                if isinstance(v,float) and math.isnan(v): v=None
                if hasattr(v,'item'): v=v.item()
                c=ws.cell(row=i,column=j,value=v)
                if isinstance(v,(int,float)): c.number_format='#,##0.00' if (isinstance(v,float) and abs(v-round(v))>1e-9) else '#,##0'
                if str(row[0]).strip() in ('Total','BRASIL','Brasil'): c.font=tot_font
        ws.freeze_panes='B5'; ws.row_dimensions[4].height=42
        for j,col in enumerate(d.columns,1):
            w=max([len(str(col))]+[len(str(x)) for x in d.iloc[:,j-1].head(200)])
            ws.column_dimensions[get_column_letter(j)].width=min(max(10,w+2),70 if j==1 else 22)
    ws0.column_dimensions['A'].width=34; ws0.column_dimensions['B'].width=110; ws0.column_dimensions['C'].width=70
    wsf=wb.create_sheet('Fontes_Notas'); wsf['A1']='Fontes e notas metodológicas'; wsf['A1'].font=Font(bold=True,size=12)
    for j,h in enumerate(['Fonte','Endereço / tabulação','Notas'],1):
        c=wsf.cell(row=3,column=j,value=h); c.fill=hdr_fill; c.font=hdr_font
    for i,f in enumerate(fontes,4):
        for j,v in enumerate(f,1): wsf.cell(row=i,column=j,value=v).alignment=Alignment(wrap_text=True,vertical='top')
    wsf.column_dimensions['A'].width=45; wsf.column_dimensions['B'].width=80; wsf.column_dimensions['C'].width=80
    wb.save(path)
# ---------- gráficos ----------
def style(ax,ylabel=''):
    ax.grid(axis='y',color=GRID,linewidth=0.8); ax.set_axisbelow(True); ax.set_ylabel(ylabel,color=INK2)
def save(fig,path): fig.tight_layout(); fig.savefig(path,dpi=160); plt.close(fig)
def bars(x,y,path,ylabel='',labels=True,color=C[0],fmt=fmt_int,figsize=(9,4.2),rot=0):
    fig,ax=plt.subplots(figsize=figsize); ax.bar(x,y,color=color,width=0.7); style(ax,ylabel)
    if labels:
        for xi,yi in zip(x,y): ax.annotate(fmt(yi),(xi,yi),ha='center',va='bottom',fontsize=9,color=INK2,xytext=(0,3),textcoords='offset points')
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v,p: fmt_int(v))); 
    if rot: plt.setp(ax.get_xticklabels(),rotation=rot,ha='right')
    save(fig,path)
def lines(x,series,path,ylabel='',figsize=(9,4.2),fmt=None,legend_cols=1):
    fig,ax=plt.subplots(figsize=figsize)
    for (k,v),col in zip(series.items(),C):
        ax.plot(x,v,lw=2,marker='o',ms=5,color=col,label=k)
    style(ax,ylabel); ax.legend(frameon=False,ncol=legend_cols,fontsize=9)
    if fmt: ax.yaxis.set_major_formatter(FuncFormatter(lambda v,p: fmt(v)))
    save(fig,path)
def hbars(labels,values,path,xlabel='',highlight=None,figsize=(9,5.6),fmt=fmt_int,fs=9):
    fig,ax=plt.subplots(figsize=figsize)
    cols=[(C[1] if highlight and l in highlight else C[0]) for l in labels]
    ax.barh(labels,values,color=cols,height=0.7)
    for i,v in enumerate(values): ax.text(v+max(values)*0.01,i,fmt(v),va='center',fontsize=fs,color=INK2)
    ax.grid(axis='x',color=GRID); ax.set_axisbelow(True); ax.set_xlabel(xlabel,color=INK2); ax.set_xlim(0,max(values)*1.15); ax.tick_params(axis='y',labelsize=fs)
    save(fig,path)
def stacked(x,parts,path,ylabel='',figsize=(9,4.2),loc='best',ncol=1):
    fig,ax=plt.subplots(figsize=figsize); bottom=[0]*len(x)
    for (k,v),col in zip(parts.items(),C):
        ax.bar(x,v,bottom=bottom,color=col,width=0.7,label=k); bottom=[b+vv for b,vv in zip(bottom,v)]
    style(ax,ylabel); ax.legend(frameon=False,fontsize=9,loc=loc,ncol=ncol); ax.yaxis.set_major_formatter(FuncFormatter(lambda v,p: fmt_int(v)))
    save(fig,path)
