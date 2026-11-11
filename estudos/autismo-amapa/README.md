# Caracterização do Autismo no Amapá — Censo 2022 e Projeções 2022–2040

Estudo técnico elaborado a partir dos dados do Censo Demográfico 2022 (IBGE) sobre pessoas
com diagnóstico de autismo, com comparação nacional, análise por idade, sexo, cor ou raça,
município e escolarização, modelagem de coortes de nascimento e projeções em quatro cenários
(com simulação de Monte Carlo) até 2040.

## Entregáveis

- `Estudo_Autismo_Amapa_Censo2022.docx` — relatório completo (Word)
- `Estudo_Autismo_Amapa_Censo2022.pdf` — mesma versão em PDF (31 páginas)
- `figuras/` — 11 figuras em PNG utilizadas no relatório
- `dados/` — bases tratadas (CSV), resultados consolidados (`results.json`) e dados brutos da API do SIDRA (`dados/brutos/`)
- `scripts/` — pipeline reprodutível

## Fontes

- IBGE, Censo Demográfico 2022 — Pessoas com Deficiência e Pessoas Diagnosticadas com TEA
  (resultados preliminares da amostra, maio/2025). Tabelas SIDRA 10145, 10147, 10148, 10150, 10151 e 10153.
- IBGE, Projeções da População 2024 (Brasil e UFs, por sexo e idade simples, 2000–2070).

## Como reproduzir

```bash
cd scripts
python3 fetch_sidra.py        # baixa as tabelas do SIDRA para ../raw (criar a pasta)
python3 prep.py               # gera os CSV tratados em ../data
python3 analysis.py           # indicadores, padronização, Bayes empírico, coortes, projeções -> ../data/results.json
python3 figures.py            # figuras em ../fig
node build_docx.js            # monta o DOCX em ../out (requer o pacote npm `docx`)
python3 uno_pdf.py ../out/Estudo_Autismo_Amapa_Censo2022.docx ../out/Estudo_Autismo_Amapa_Censo2022.pdf  # PDF com sumário atualizado (LibreOffice)
```

Dependências Python: pandas, numpy, scipy, statsmodels, matplotlib, openpyxl.
