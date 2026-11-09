# Saúde no Amapá — levantamento de produção e estudo analítico para a transição 2026/2027

Levantamento completo da produção hospitalar (SIH/SUS), ambulatorial (SIA/SUS), rede física e força de trabalho (CNES), indicadores vitais (SIM/SINASC), financiamento (SIOPS, LOA) e demografia (IBGE) do Estado do Amapá, com estudo analítico voltado à transição da Secretaria de Estado da Saúde (SESA/AP). Série histórica 2022–2026 (2022 como ano-base; 2026 parcial). Extração realizada em 06/11/2026 a partir de fontes públicas.

## Arquivos

| Arquivo | Conteúdo |
|---|---|
| `Estudo_Analitico_SESA_AP_Transicao_2026.docx` / `.pdf` | Estudo analítico completo em formato ABNT (NBR 14724): capa, folha de rosto, resumo, listas de figuras, tabelas e siglas, sumário, 11 seções numeradas, referências (NBR 6023) e apêndice. Autor: Patrício Almeida |
| `Estudo_Analitico_SESA_AP_Transicao_2026.md` | Texto-fonte do estudo em Markdown (gera o DOCX via `scripts/build_docx_abnt.py`) |
| `Tabelas_Saude_Amapa_Transicao_2026.xlsx` | 129 abas tabuladas (séries 2022–2026), com índice, painel de indicadores-chave, comparativos entre UFs e fontes |
| `graficos/` | 13 gráficos em PNG usados no estudo |
| `dados/tabnet/` | 127 tabelas brutas extraídas do TABNET/DATASUS (CSV, separador `;`, decimal `,`) e log de extração |
| `dados/siops/` | Indicadores SIOPS do Estado do Amapá (2015–2026) e de todas as UFs (2024–2025) |
| `dados/ibge/` | Estimativas populacionais (SIDRA, tabela 6579) por UF e município |
| `dados/edital/` | Texto extraído do Edital de Concurso Público SESA/AP nº 001/2026 |
| `scripts/` | Scripts Python de extração (`tabnet.py`, `extract_*.py`, `siops.py`), de consolidação (`build.py`) e de editoração ABNT (`build_docx_abnt.py`, `pagina.py`) |

## Reprodução

Os scripts usam diretórios de trabalho definidos nas variáveis `OUT`/`RAW` no topo de cada arquivo; ajuste-os antes de executar. Requisitos: Python 3.10+, `pandas`, `openpyxl`, `matplotlib`. Sequência: `extract_all.py` → `extract_bench.py` → `extract_fix.py` → `extract_bench2.py` → `siops.py` → `build.py`; o DOCX ABNT é gerado em duas passagens: `build_docx_abnt.py` (sumário provisório) → conversão para PDF com LibreOffice → `pagina.py` (páginas de títulos, tabelas e figuras) → `build_docx_abnt.py` novamente com o JSON de páginas.

## Limitações conhecidas

Não foi possível acessar, a partir do ambiente de extração, o ConsultaFNS (repasses fundo a fundo), os portais do Governo do Amapá (transparência, SESA), o e-Gestor AB/SISAB (cobertura da atenção primária) e o SI-PNI (vacinação). Esses dados devem ser solicitados diretamente à SESA na transição (lista na seção 9 do estudo). Valores em reais correntes; 2025 do SIM/SINASC é preliminar; 2026 é parcial (jan–ago no SIH/SIA; set no CNES; 4º bimestre no SIOPS).

## Estudos complementares (pasta `estudos-complementares/`)

Cinco estudos temáticos no mesmo padrão (extração pública, planilha, gráficos e documento ABNT com autoria de Patrício Almeida), série 2022–2026, extração em 07 e 08/11/2026:

| Pasta | Estudo | Principais fontes |
|---|---|---|
| `e1_vigilancia/` | Vigilância em saúde: doenças transmissíveis e agravos de notificação (tuberculose, hanseníase, sífilis, arboviroses, leishmanioses, meningites, animais peçonhentos, intoxicações) | SINAN, SIM, SINASC, IBGE |
| `e2_atencao_primaria/` | Atenção primária, regionalização e saúde materno-infantil (equipes e cobertura, habilitações e UTI, ICSAP, pré-natal, parto, mortalidade materna, fetal e infantil) | CNES, SIH, SIA, SINASC, SIM, IBGE |
| `e3_violencias_saude_mental/` | Violências, causas externas e saúde mental (homicídios e intervenções legais, suicídio, trânsito, afogamentos, internações por causas externas, notificações de violência, RAPS) | SIM, SIH, SINAN, CNES, SIA |
| `e4_oncologia_cronicas/` | Oncologia, rastreamento e doenças crônicas (mortalidade por câncer e DCNT, quimioterapia e radioterapia, mamografia e citopatológico, AVC, infarto, diabetes, diálise) | SIM, SIA, SIH, CNES, IBGE |
| `e5_financiamento/` | Financiamento, recursos e gastos em saúde (despesa da função Saúde e ASPS, mínimo constitucional, fontes e transferências da União, composição da despesa, investimentos e restos a pagar, emendas parlamentares, municípios e gasto consolidado, comparação entre estados) | SIOPS (RREO Anexo 12), SICONFI (RREO/DCA), CGU (emendas), SIH/SIA, IBGE |

Cada pasta contém `Estudo_*.md` (texto-fonte), `Estudo_*.docx` e `Estudo_*.pdf` (ABNT), `Tabelas_*.xlsx` (planilha com índice, painel-resumo, tabelas e fontes) e `graficos/`. Os arquivos `cfg_e*.json` guardam título, resumo, siglas e referências de cada estudo. Os dados brutos estão em `dados/tabnet2/` (TABNET), `dados/siconfi/` (RREO e DCA em formato longo), `dados/siops/anexo12/` (Anexo 12 de estados e municípios, formato longo) e `dados/emendas/` (emendas da CGU filtradas para o Amapá); os scripts em `scripts/` (`extract_estudos2*.py`, `extract_siconfi.py`, `extract_siops_anexo12.py`, `build_e1.py` a `build_e5.py`, `lib_estudo.py`).

Temas pertinentes que não puderam ser desenvolvidos com dados públicos acessíveis e devem ser levantados internamente na transição: assistência farmacêutica e judicialização (SISMEDEX/Hórus, estoques, demandas judiciais), regulação e filas (SISREG e sistema estadual), recursos humanos por vínculo e folha, contratos e execução financeira por unidade e credor (balancete do FES, saldos de emendas, passivo com fornecedores; o estudo 5 cobre o que é público no SIOPS, SICONFI e CGU), imunização (SI-PNI) e indicadores da APS por cadastro (SISAB/e-Gestor).

## Propostas de sistemas de gestão com IA (pasta `propostas-sistemas/`)

Portfólio comercial com onze soluções de gestão com inteligência artificial para a SESA/AP (P0 inteligência integrativa (plataforma de dados, barramento de eventos, alertas, orientações de ação, centro de comando e copiloto); P1 governança financeira do FES; P2 contratos assistenciais e organizações sociais; P3 faturamento e auditoria SUS; P4 regulação de acesso e leitos; P5 linhas de cuidado em oncologia e crônicas; P6 rede materno-infantil e apoio à APS; P7 vigilância preditiva; P8 assistência farmacêutica e judicialização; P9 força de trabalho e escalas; P10 contratos administrativos, compras e fornecedores), cada uma ancorada em um problema medido nos estudos, com uso da IA, integrações, indicadores de resultado, implantação e investimento indicativo, além de arquitetura, governança de IA, modelo de contratação (Lei 14.133/2021, CPSI, encomenda tecnológica) e roteiro 2027–2028. Arquivos: `Propostas_Sistemas_Gestao_IA_SESA_AP.md/.docx/.pdf` e `cfg_propostas.json`; geração por `scripts/proposta_pipeline.sh` (`build_proposta_docx.py`).
