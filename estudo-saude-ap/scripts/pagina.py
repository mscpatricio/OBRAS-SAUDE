# -*- coding: utf-8 -*-
"""Lê o PDF gerado pelo LibreOffice e localiza a página de cada título, tabela e figura (para sumário e listas ABNT)."""
import sys, re, json, subprocess, unicodedata
pdf,md,out=sys.argv[1:4]
txt=subprocess.run(['pdftotext','-layout',pdf,'-'],capture_output=True,text=True).stdout
pages=txt.split('\f')
def norm(s):
    s=unicodedata.normalize('NFKD',s); s=''.join(c for c in s if not unicodedata.combining(c))
    return '\n'.join(re.sub(r'[ \t]+',' ',l).strip() for l in s.split('\n')).lower()
npages=[norm(p) for p in pages]
# first textual page = page with heading "1 INTRODUCAO" line (not in sumário: sumário has dots/page numbers)
first=None
for i,p in enumerate(npages):
    if re.search(r'^1 introducao$',p,re.M):
        first=i+1; break
res={}
heads=re.findall(r'(?m)^(#{1,2}) (.*)$',open(md,encoding='utf-8').read())
def find(pattern,start=0):
    for i in range(start,len(npages)):
        if re.search(pattern,npages[i],re.M): return i
    return None
cursor=first-1 if first else 0
for h,t in heads:
    key='h_'+re.sub(r'\W+','_',t)[:60]
    tt=re.sub(r'^(\d+)\. ',r'\1 ',t); pat='^'+re.escape(norm(tt if h=='##' else tt.upper()))[:60]+r'(?!.*\.{3})'
    i=find(pat,cursor)
    if i is None: i=find(re.escape(norm(t))[:40],cursor)
    if i is not None: res[key]=i+1-(first-1)+ (0) ; cursor=i
res['h_REF']=(find(r'^referencias$',cursor) or 0)+1-(first-1)
for kind,label in (('tab','Tabela'),('fig','Figura')):
    n=0; cursor=first-1
    while True:
        n+=1; i=find(r'^'+label.lower()+' '+str(n)+' [–-]',cursor)
        if i is None: break
        res[f'{kind}{n}']=i+1-(first-1); cursor=i
res['_first_textual_page']=first
json.dump(res,open(out,'w'),ensure_ascii=False,indent=1); print(json.dumps(res,ensure_ascii=False))
