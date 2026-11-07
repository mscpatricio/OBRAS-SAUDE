#!/bin/bash
# Uso: abnt_pipeline.sh <md> <cfg.json> <saida.docx>  — gera DOCX ABNT com sumário paginado (até 4 passagens) e PDF
set -e
MD="$1"; CFG="$2"; OUTDOCX="$3"
SCR=/tmp/claude-0/-home-user-OBRAS-SAUDE/c712070a-2954-5409-93ab-21cafbd2988b/scratchpad
S=$(cd "$(dirname "$0")" && pwd); W=$SCR/abnt_$$; mkdir -p "$W"
PAGES=""
for i in 1 2 3 4; do
  python3 "$S/build_docx_abnt.py" "$MD" "$W/pass$i.docx" 1 "$PAGES" "$CFG" >/dev/null
  ( cd "$W" && timeout 240 soffice --headless --convert-to pdf --outdir . pass$i.docx >/dev/null 2>&1 )
  python3 "$S/pagina.py" "$W/pass$i.pdf" "$MD" "$W/pages$i.json" >/dev/null
  if [ -n "$PAGES" ] && python3 - "$PAGES" "$W/pages$i.json" <<'PY'
import json,sys;a=json.load(open(sys.argv[1]));b=json.load(open(sys.argv[2]));sys.exit(0 if all(a[k]==b.get(k) for k in a) else 1)
PY
  then echo "paginacao estavel na passagem $i"; cp "$W/pass$i.docx" "$OUTDOCX"; cp "$W/pass$i.pdf" "${OUTDOCX%.docx}.pdf"; pdfinfo "$W/pass$i.pdf" | grep Pages; exit 0; fi
  PAGES="$W/pages$i.json"
done
echo "AVISO: paginacao nao convergiu; usando ultima passagem"; cp "$W/pass4.docx" "$OUTDOCX"; cp "$W/pass4.pdf" "${OUTDOCX%.docx}.pdf"
