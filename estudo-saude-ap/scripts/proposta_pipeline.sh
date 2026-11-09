#!/bin/bash
# Uso: proposta_pipeline.sh <md> <cfg.json> <saida.docx> — gera DOCX de proposta com sumário paginado (2 passagens) e PDF
set -e
MD="$1"; CFG="$2"; OUTDOCX="$3"; S=$(cd "$(dirname "$0")" && pwd)
W=/tmp/claude-0/-home-user-OBRAS-SAUDE/c712070a-2954-5409-93ab-21cafbd2988b/scratchpad/prop_$$; mkdir -p "$W"
python3 "$S/build_proposta_docx.py" "$MD" "$W/p1.docx" "$CFG" >/dev/null
( cd "$W" && timeout 240 soffice --headless --convert-to pdf --outdir . p1.docx >/dev/null 2>&1 )
python3 - "$W/p1.pdf" "$MD" "$W/pages.json" <<'PY'
import sys,re,json,subprocess,unicodedata
pdf,md,out=sys.argv[1:4]
def norm(s): return re.sub(r'\s+',' ',''.join(c for c in unicodedata.normalize('NFKD',s) if not unicodedata.combining(c)).lower()).strip()
n=int(re.search(r'Pages:\s+(\d+)',subprocess.run(['pdfinfo',pdf],capture_output=True,text=True).stdout).group(1))
H1=[re.sub(r'^(\d+(\.\d+)*\.?)\s*','',m.group(1)).strip() for m in (re.match(r'^#\s+(.*)$',l) for l in open(md,encoding='utf-8')) if m]
pages={}; start=4
for i in range(start,n+1):
    txt=norm(subprocess.run(['pdftotext','-f',str(i),'-l',str(i),'-layout',pdf,'-'],capture_output=True,text=True).stdout)
    for h in H1:
        if h not in pages and norm(h) in txt: pages[h]=i
json.dump(pages,open(out,'w'),ensure_ascii=False,indent=1); print('headings paginated',len(pages),'of',len(H1))
PY
python3 "$S/build_proposta_docx.py" "$MD" "$OUTDOCX" "$CFG" "$W/pages.json" >/dev/null
D=$(cd "$(dirname "$OUTDOCX")" && pwd); ( cd "$D" && timeout 240 soffice --headless --convert-to pdf --outdir . "$(basename "$OUTDOCX")" >/dev/null 2>&1 )
pdfinfo "${OUTDOCX%.docx}.pdf" | grep Pages
