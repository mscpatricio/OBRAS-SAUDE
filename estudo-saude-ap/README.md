# Saúde no Amapá — levantamento de produção e estudo analítico para a transição 2026/2027

Levantamento completo da produção hospitalar (SIH/SUS), ambulatorial (SIA/SUS), rede física e força de trabalho (CNES), indicadores vitais (SIM/SINASC), financiamento (SIOPS, LOA) e demografia (IBGE) do Estado do Amapá, com estudo analítico voltado à transição da Secretaria de Estado da Saúde (SESA/AP). Extração realizada em 06/11/2026 a partir de fontes públicas.

## Arquivos

| Arquivo | Conteúdo |
|---|---|
| `Estudo_Analitico_SESA_AP_Transicao_2026.md` / `.docx` | Estudo analítico completo (sumário executivo, 9 seções, recomendações e agenda dos 100 primeiros dias) |
| `Tabelas_Saude_Amapa_Transicao_2026.xlsx` | 129 abas tabuladas, com índice, painel de indicadores-chave, comparativos entre UFs e fontes |
| `graficos/` | 13 gráficos em PNG usados no estudo |
| `dados/tabnet/` | 127 tabelas brutas extraídas do TABNET/DATASUS (CSV, separador `;`, decimal `,`) e log de extração |
| `dados/siops/` | Indicadores SIOPS do Estado do Amapá (2015–2026) e de todas as UFs (2024–2025) |
| `dados/ibge/` | Estimativas populacionais (SIDRA, tabela 6579) por UF e município |
| `dados/edital/` | Texto extraído do Edital de Concurso Público SESA/AP nº 001/2026 |
| `scripts/` | Scripts Python de extração (`tabnet.py`, `extract_*.py`, `siops.py`) e de consolidação (`build.py`) |

## Reprodução

Os scripts usam diretórios de trabalho definidos nas variáveis `OUT`/`RAW` no topo de cada arquivo; ajuste-os antes de executar. Requisitos: Python 3.10+, `pandas`, `openpyxl`, `matplotlib`. Sequência: `extract_all.py` → `extract_bench.py` → `extract_fix.py` → `extract_bench2.py` → `siops.py` → `build.py`; o DOCX é gerado com `pandoc Estudo_Analitico_SESA_AP_Transicao_2026.md -o Estudo_Analitico_SESA_AP_Transicao_2026.docx --toc`.

## Limitações conhecidas

Não foi possível acessar, a partir do ambiente de extração, o ConsultaFNS (repasses fundo a fundo), os portais do Governo do Amapá (transparência, SESA), o e-Gestor AB/SISAB (cobertura da atenção primária) e o SI-PNI (vacinação). Esses dados devem ser solicitados diretamente à SESA na transição (lista na seção 9 do estudo). Valores em reais correntes; 2025 do SIM/SINASC é preliminar; 2026 é parcial (jan–ago no SIH/SIA; set no CNES; 4º bimestre no SIOPS).
