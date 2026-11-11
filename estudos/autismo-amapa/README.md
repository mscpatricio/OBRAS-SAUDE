# Caracterização do Autismo no Amapá — Censo 2022 e Projeções 2022–2040

**Autor:** Dr. Patrício Almeida

Estudo técnico elaborado a partir dos dados do Censo Demográfico 2022 (IBGE) sobre pessoas
com diagnóstico de autismo, com comparação nacional, análise por idade, sexo, cor ou raça,
município e escolarização, modelagem de coortes de nascimento e projeções em quatro cenários
(com simulação de Monte Carlo) até 2040.

O documento segue as normas da ABNT para trabalhos técnico-científicos (NBR 14724: estrutura,
margens 3/3/2/2 cm, Arial 12, entrelinha 1,5, paginação a partir da parte textual; NBR 6024:
numeração progressiva; NBR 6027: sumário; NBR 6028: resumo e abstract; NBR 10520: citações
autor-data; NBR 6023: referências) e as Normas de Apresentação Tabular do IBGE (título com
conteúdo, local e período; fonte e notas no rodapé; laterais abertas; sinais convencionais),
com a estrutura editorial do IBGE (apresentação, notas técnicas com conceitos e definições,
glossário e apêndices).

## Entregáveis

- `Estudo_Autismo_Amapa_Censo2022.docx` — relatório completo (Word)
- `Estudo_Autismo_Amapa_Censo2022.pdf` — mesma versão em PDF (48 páginas)
- `apresentacao/` — slides da apresentação (17 slides, fonte HTML do deck publicado em claude.ai)
- `figuras/` — 11 gráficos em PNG utilizados no relatório (títulos e fontes ficam no documento, conforme ABNT/IBGE)
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
python3 figures_abnt.py       # gráficos em ../fig_abnt
node build_abnt.js && bash pass_abnt.sh   # 1ª passagem: DOCX em ../out_abnt, PDF e números de página (LibreOffice/UNO)
node build_abnt.js && bash pass_abnt.sh   # 2ª passagem: listas de gráficos e tabelas com os números de página
```

Dependências Python: pandas, numpy, scipy, statsmodels, matplotlib, openpyxl.
