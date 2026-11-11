set -e
cd out_abnt
(zip -d Estudo_Autismo_Amapa_Censo2022.docx '*/' >/dev/null 2>&1 || true)
rm -f Estudo_Autismo_Amapa_Censo2022.pdf
timeout 300 python3 ../uno_pdf.py Estudo_Autismo_Amapa_Censo2022.docx Estudo_Autismo_Amapa_Censo2022.pdf
pdftotext -layout Estudo_Autismo_Amapa_Censo2022.pdf texto.txt
python3 - <<'PY'
import json,re
pages=open('texto.txt',encoding='utf-8').read().split('\f')
caps=json.load(open('captions.json'))
# página de início do texto: primeira página (após a capa) cujo texto contém o título "1 INTRODUÇÃO" como linha (não no sumário)
start=None
for i,p in enumerate(pages):
    if re.search(r'^\s*1 INTRODUÇÃO\s*$',p,re.M) and 'SUMÁRIO' not in p: start=i; break
out={}
norm=lambda s: re.sub(r'\s+',' ',s)
for label,items in [('Gráfico',caps['graf']),('Tabela',caps['tab'])]:
    for t in items:
        key=t.split(' - ')[0]  # "Tabela 3"
        found=None
        for i in range(start,len(pages)):
            if re.search(r'^\s*'+re.escape(key)+r' - ',pages[i],re.M): found=i; break
        num=''
        if found is not None:
            first=[l.strip() for l in pages[found].split('\n') if l.strip()]
            num=first[0] if first and first[0].isdigit() else str(found)
        out[t]=num
print(json.dumps(out,ensure_ascii=False,indent=0)[:600]); json.dump(out,open('pages.json','w'),ensure_ascii=False)
print('start page idx',start,'total pages',len(pages)-1)
PY
