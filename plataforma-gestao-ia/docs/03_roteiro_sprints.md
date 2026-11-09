# 03 – Roteiro de sprints e ordem de construção

Sprints de duas semanas. Marque o estado de cada história aqui (`[ ]` a fazer, `[~]` parcial, `[x]` pronto) ao fim de cada sessão do Claude Code. Dependências: nada começa antes da Fase 0; P1–P3 dependem dos marts financeiros e de produção; P4–P6 dependem de identidade e eventos; P7–P9 dependem de conectores específicos.

## Fase 0 – Fundação (sprints 1–3)

- [ ] Monorepo, `pyproject` (uv), `package.json` (pnpm), Makefile, Compose (postgres, minio, keycloak, prefect, redis), CI (lint, testes, build).
- [ ] `packages/core`: modelos de `facility`, `municipality`, `user`, `audit_event`, `event_bus`; serviço de identidade com `person_key` e `redact()`.
- [ ] `packages/connectors`: base `Connector`, conectores SICONFI, SIOPS Anexo 12, CGU emendas, IBGE (portados dos scripts existentes com testes usando fixtures de `estudo-saude-ap/dados`).
- [ ] `packages/connectors`: DATASUS SIH RD, SIA PA, CNES (ST, LT, PF, HB) via pysus; validação com totais do TABNET.
- [ ] dbt: staging para as fontes acima; `dim_facility`, `dim_municipality`, `dim_procedure`, `fct_hospital_admission`, `fct_ambulatory_production`, `fct_budget_execution`, `fct_revenue`, `fct_transfer`, `fct_amendment`.
- [ ] `apps/api` com autenticação Keycloak, `apps/web` com layout, navegação por módulo e componente de painel (ECharts) reutilizável.
- [ ] `packages/llm`: gateway, redação, prompts versionados, `evals` básico.

## Fase 1 – P0 e P1 (sprints 4–7)

- [ ] P0 sala de situação: painéis de produção, estrutura, finanças e vigilância com dados 2022–2026; catálogo de indicadores (20 iniciais); painel de qualidade de dados.
- [ ] P0 copiloto: text-to-SQL validado sobre `rpt_*`, citações, 50 perguntas no eval.
- [ ] P1 carga do sistema contábil (adaptador fictício + CSV real quando disponível), `fct_budget_execution` detalhado por empenho.
- [ ] P1 classificador de empenhos (subfunção, centro de custo, natureza) com revisão em lote.
- [ ] P1 apuração e projeção do mínimo constitucional (regra LC 141 + Constituição Estadual 15%), alertas com dois bimestres.
- [ ] P1 painel de investimentos e emendas (prazos, saldos, situação física).
- [ ] P1 restos a pagar: estoque por exercício, credor, risco de cancelamento.

## Fase 2 – P2, P3, P10 (carteira) e censo de leitos de P4 (sprints 8–11)

- [ ] P2 cadastro de contratos, metas e comissões; apuração automática a partir de `fct_*` de produção.
- [ ] P2 extração de relatórios de prestadores (LLM/visão) e conciliação produção × contrato × pagamento.
- [ ] P3 ingestão de AIH/APAC/BPA das unidades (arquivos de remessa) e crítica SIGTAP.
- [ ] P3 codificação assistida a partir de resumo de alta (prontuário sintético) e recuperação de procedimentos não faturados.
- [ ] P3 detecção de atipicidades (procedimentos vasculares, trombectomias, oncologia em unidade sem perfil) com fila de auditoria.
- [ ] P4 censo eletrônico de leitos (FHIR Encounter/Location) e painel de ocupação em tempo real.
- [ ] P10 carteira de contratos administrativos (cadastro, fiscal/gestor, saldo, vigência, alertas de 90/180 dias) e integração PNCP; portal de dados abertos.
- [ ] P10 conciliação nota fiscal → medição → contrato → empenho (P1) e painel de passivo com fornecedores por idade.

## Fase 3 – P4, P5, P7 e P10 (planejamento e fiscalização) (sprints 12–16)

- [ ] P4 fila única ambulatorial e de exames, protocolos, classificação de risco assistida, devolução de solicitações incompletas.
- [ ] P4 previsão de ocupação e de demanda de urgência; TFD; mensagens ao paciente.
- [ ] P5 registro longitudinal, população elegível, convocação, prazos de 60 dias, navegação.
- [ ] P7 ingestão SINAN semanal + GAL + clima; nowcasting; alertas; boletim assistido; risco de abandono de TB.
- [ ] P10 planejamento assistido (DFD/ETP/TR/edital), pesquisa de preços com PNCP e Painel de Preços, risco de fornecedores (CEIS/CNEP, vínculos societários), fiscalização e conformidade trabalhista de terceirizados.

## Fase 4 – P6, P8, P9 e copiloto completo (sprints 17–22)

- [ ] P6 painel de gestantes e crianças, vinculação ao parto, indicadores por equipe, assistente dos gestores municipais.
- [ ] P8 estoque, programação, previsão de demanda, triagem de demandas judiciais com minuta de parecer.
- [ ] P9 cadastro único de profissionais, conciliação CNES/folha/escala, escalas otimizadas, previsão de absenteísmo.
- [ ] P0 copiloto com todos os módulos; relatórios automatizados (quadrimestral, boletins).

## Fase 5 – Endurecimento (sprints 23–26)

- [ ] Segurança (pentest, SAST/DAST), desempenho, acessibilidade, documentação de transferência de tecnologia, treinamento.
- [ ] Modelos fora da sombra após aprovação do comitê; parcela por resultado instrumentada (P3, P2, P4).

## Como conduzir cada sprint com o Claude Code

1. Abra a sessão com o prompt de arranque do produto (seção final de `docs/produtos/P<n>.md`) e peça um plano para a história escolhida.
2. Revise o plano (arquivos, migrações, testes, riscos LGPD). Aprove ou ajuste.
3. Deixe o Claude Code implementar com testes; exija `make test` verde e demonstração via Playwright.
4. Peça a atualização deste roteiro, do `CHANGELOG.md` e da documentação do módulo.
5. Revise o PR com `/code-review`; mescle apenas com revisão humana.
