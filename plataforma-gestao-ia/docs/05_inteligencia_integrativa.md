# 05 – Inteligência Integrativa: eventos, alertas e orientações de ação

Nenhum módulo é uma ilha. Todo módulo (P1 a P10) publica eventos de domínio e expõe indicadores para o núcleo (P0), que correlaciona informações entre módulos e devolve ao gestor painéis, relatórios, alertas priorizados e orientações de ação com responsável e prazo. Este documento define o contrato técnico dessa integração; a especificação funcional está em `docs/produtos/P0.md`.

## Arquitetura da integração

```
módulos P1..P10 ──publish──▶ core.events (outbox transacional → barramento) ──▶ consumidores:
                                                                     ├─ plataforma.alert_engine (regras + correlação + priorização)
                                                                     ├─ plataforma.recommendation_engine (orientações de ação)
                                                                     ├─ plataforma.timeline (linha do tempo por entidade)
                                                                     ├─ marts (dbt incremental) → painéis e copiloto
                                                                     └─ core.audit (trilha)
orientações de ação ──assign──▶ módulo executor (tarefa no módulo, com prazo) ──done/ignored──▶ core.events (feedback)
```

- **Outbox transacional:** cada módulo grava o evento na tabela `core.event_outbox` na mesma transação da mudança de estado; um publicador envia ao barramento (PostgreSQL LISTEN/NOTIFY em dev; Redis Streams em prod) com entrega ao menos uma vez e chave de idempotência.
- **Esquema do evento (CloudEvents 1.0):** `id`, `source` (`sesa.<modulo>`), `type` (`sesa.<modulo>.<entidade>.<acao>.v1`), `time`, `subject` (chave da entidade: `facility_key`, `contract_id`, `person_key`...), `data` (payload sem dados identificados), `dataschema` (JSON Schema versionado em `packages/core/events/schemas/`).
- **Catálogo de eventos:** `packages/core/events/catalog.yaml` é a fonte única; o CI falha se um módulo publicar tipo não catalogado ou payload fora do schema.
- **Consumidores idempotentes:** processam por `id`; reprocessamento seguro.

## Catálogo inicial de eventos (v1)

| Módulo | Tipo de evento | Payload mínimo |
|---|---|---|
| P1 | `financas.commitment.classified`, `financas.minimum.risk_changed`, `financas.investment.stalled`, `financas.unpaid.aging_crossed`, `financas.amendment.deadline_near` | ids, valores, nível de risco, prazo |
| P2 | `contratos.target.missed`, `contratos.reconciliation.divergence`, `contratos.risk.changed`, `contratos.contestation.opened` | contract_id, competência, meta, realizado, divergência |
| P3 | `faturamento.batch.critiqued`, `faturamento.recovery.found`, `faturamento.anomaly.flagged`, `faturamento.ceiling.near` | unidade, competência, valor, regra/modelo |
| P4 | `regulacao.bed.occupied/released`, `regulacao.occupancy.threshold_crossed`, `regulacao.request.created/triaged/scheduled/returned`, `regulacao.time_window.at_risk` (AVC/IAM), `regulacao.tfd.requested` | facility_key, tipo de leito, taxa, request_id, prioridade |
| P5 | `linhas.case.deadline_at_risk`, `linhas.case.deadline_missed`, `linhas.campaign.completed`, `linhas.screening.ratio_updated` | case_id, linha, dias restantes, município |
| P6 | `materno.pregnancy.gap_detected` (sem pré-natal, sem vinculação, sífilis não tratada), `materno.delivery.forecast_updated`, `materno.death.investigation_due` | pregnancy_id (pseudônimo), município, equipe, tipo de lacuna |
| P7 | `vigilancia.alert.raised` (agravo, nível, horizonte), `vigilancia.outbreak.detected`, `vigilancia.case.dropout_risk`, `vigilancia.bulletin.drafted` | agravo, território, semana, estimativa, intervalo |
| P8 | `farmacia.stock.rupture_risk`, `farmacia.stock.expiring`, `farmacia.lawsuit.received`, `farmacia.opinion.drafted` | item, unidade, dias de cobertura, processo |
| P9 | `pessoas.schedule.uncovered`, `pessoas.reconciliation.issue`, `pessoas.overtime.threshold_crossed`, `pessoas.absence.forecast_updated` | unidade, setor, turno, categoria |
| P10 | `compras.contract.expiring`, `compras.contract.balance_low`, `compras.invoice.without_attest`, `compras.supplier.sanctioned`, `compras.price.overprice_detected`, `compras.emergency.opened` | contract_id, fornecedor_key, dias, valor |
| P0 | `plataforma.alert.raised/acknowledged/escalated/closed`, `plataforma.action.assigned/completed/ignored`, `plataforma.report.generated` | alert_id, action_id, responsável, prazo, resultado |

## Motor de alertas (`plataforma.alert_engine`)

- Regras declarativas em YAML (`modules/plataforma/rules/*.yaml`): condição sobre eventos e indicadores (com janelas temporais e correlação entre módulos), gravidade (informativo, atenção, crítico), destinatários por perfil/território, prazo padrão.
- Correlação: regras podem combinar eventos de módulos diferentes (ex.: `vigilancia.alert.raised[dengue, nível alto]` + `regulacao.occupancy.threshold_crossed[>85%]` nas mesmas unidades → alerta crítico "capacidade sob pressão epidêmica").
- Priorização: pontuação = gravidade × impacto (financeiro, assistencial, prazo) × urgência, ajustada por modelo que aprende com o tratamento dado a alertas anteriores (aceito, ignorado, escalado), com explicação.
- Deduplicação, agrupamento por causa raiz e silenciamento com justificativa.

## Motor de orientações de ação (`plataforma.recommendation_engine`)

- Para cada regra de alerta, um **playbook** (`modules/plataforma/playbooks/*.yaml`) define ações sugeridas: descrição, módulo executor, tipo de tarefa a abrir (ex.: `regulacao.open_beds`, `compras.start_renewal`, `financas.anticipate_liquidation`), responsável padrão por perfil, prazo, norma ou protocolo de referência, impacto estimado e pré-condições.
- O LLM (via gateway) adapta o texto da orientação ao contexto (números do alerta, unidade, histórico) e sugere priorização entre ações, citando o playbook e as fontes; não cria ações fora do playbook sem marcação explícita de "sugestão não protocolada".
- Simulação de impacto quando houver modelo (ex.: efeito de antecipar liquidações no percentual aplicado; efeito de abrir leitos na ocupação prevista).
- Cada orientação vira uma **tarefa** no módulo executor com prazo e responsável; o fechamento (feito, não aplicável, ignorado com justificativa) retorna como evento e alimenta a avaliação dos playbooks (taxa de adoção, tempo até ação, resultado observado).

## Centro de comando e relatórios

- Painel executivo: estado dos indicadores-chave por eixo, alertas abertos por gravidade, ações em atraso, mudanças desde o último acesso; filtros por região, município e unidade.
- Briefing diário (06h): texto curto gerado a partir de eventos e indicadores das últimas 24 h, com links; enviado por e-mail e exibido no painel; números rastreáveis a views.
- Relatórios periódicos: quadrimestral de gestão (Lei Complementar 141, art. 36), prestação de contas ao Conselho e ao Tribunal, boletins; geração automática em rascunho a partir de templates e marts, com revisão e assinatura humanas.
- Linha do tempo por entidade (hospital, contrato, município, paciente para perfis assistenciais) que reúne eventos de todos os módulos.

## Modelo de dados (schema `plataforma`, complemento ao P0.md)

`event_outbox` (core), `event_log`, `alert_rule` (yaml versionado + estado), `alert` (regra, gravidade, score, entidades, eventos de origem, status, responsável, prazo), `playbook`, `action` (alert_id, playbook_id, módulo executor, tarefa, responsável, prazo, status, resultado, justificativa), `briefing`, `report_template`, `report_run`, `entity_timeline`.

## APIs (prefixo `/api/v1/plataforma`)

`GET /events?type=&subject=&since=`, `GET /alerts?severity=&status=&territory=`, `POST /alerts/{id}/acknowledge|escalate|silence`, `GET /alerts/{id}/actions`, `POST /actions/{id}/complete|ignore`, `GET /briefing/today`, `POST /reports/{template}/run`, `GET /timeline/{entity_type}/{key}`, `GET /rules`, `POST /rules` (versionado, com aprovação).

## Critérios de aceite da integração

- Todo módulo publica ao menos seus eventos do catálogo com schema validado (teste de contrato no CI).
- Regra de correlação entre dois módulos dispara alerta em teste de integração com eventos sintéticos (ex.: dengue + ocupação).
- Playbook gera orientação com responsável e prazo, abre tarefa no módulo executor e registra fechamento; relatório de adoção calculado.
- Briefing diário gerado em dev com dados de fixtures; todos os números com rastreabilidade a views.
- Nenhum dado identificado em eventos, alertas, briefings ou relatórios (teste de redação).

## Prompt de arranque para o Claude Code

```
Leia CLAUDE.md, docs/00, docs/02, docs/05_inteligencia_integrativa.md e docs/produtos/P0.md. Vamos implementar "<história>" da Inteligência Integrativa (modules/plataforma e packages/core/events). O catálogo de eventos (catalog.yaml) e os JSON Schemas são a fonte única; crie testes de contrato que falhem para eventos fora do catálogo. Regras e playbooks são YAML versionados; o LLM só adapta texto e prioriza dentro do playbook. Apresente o plano, aguarde aprovação, implemente com testes (inclusive integração com eventos sintéticos de dois módulos), rode `make test` e atualize roteiro, CHANGELOG e docs/demos/plataforma.md.
```
