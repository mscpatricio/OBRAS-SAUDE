# 00 – Visão e arquitetura

## Objetivo

Entregar, em 18 meses, uma plataforma modular que torne o gasto da SESA/AP legível, o acesso regulado, o cuidado contínuo e a vigilância antecipada, com IA assistiva e humano no circuito. Os problemas de origem e as metas estão em `../../estudo-saude-ap/propostas-sistemas/Propostas_Sistemas_Gestao_IA_SESA_AP.md`.

## Princípios de arquitetura

1. **Monólito modular, não microsserviços.** Um deploy de API e um de web, com módulos isolados por schema de banco e por pacote Python; extraímos serviços apenas quando houver necessidade medida (ex.: inferência pesada).
2. **Lake primeiro.** Toda origem externa aterrissa em `raw/` (imutável, particionada por origem e competência), é validada para `trusted/` (tipada, deduplicada, pseudonimizada) e modelada em `marts/` (fatos e dimensões por domínio). Os módulos transacionais leem marts via views; nunca leem `raw`.
3. **Identidade separada do dado.** `core.identity` guarda identificadores diretos criptografados e emite `person_key`, `professional_key`, `facility_key`; pareamento probabilístico (Splink) roda no serviço de identidade.
4. **Eventos de domínio e Inteligência Integrativa.** Módulos publicam eventos CloudEvents (`regulacao.bed.occupied`, `financas.commitment.classified`, `linhas.case.deadline_at_risk`) por outbox transacional em um barramento leve (PostgreSQL LISTEN/NOTIFY em dev, Redis Streams em prod); o núcleo correlaciona eventos entre módulos, gera alertas priorizados e orientações de ação com responsável e prazo, e alimenta painéis, briefing, relatórios e auditoria (`docs/05_inteligencia_integrativa.md`).
5. **IA como serviço interno.** `packages/ml` (modelos tabulares e séries) e `packages/llm` (linguagem) expõem interfaces estáveis: `predict(model_id, features) -> Prediction(value, confidence, explanation, model_version)` e `ask(agent_id, question, context) -> Answer(text, citations, sql, warnings)`.

## Diagrama lógico

```
[Origens] DATASUS (SIH, SIA, CNES, SINAN, SIM, SINASC) | SIOPS | SICONFI | CGU | e-SUS/SISAB | SISREG | Prontuários (FHIR) | Contábil | Folha | Hórus | GAL | Clima
    │  conectores Prefect (packages/connectors)
[Lake] raw/ ─▶ trusted/ (GX, pseudonimização) ─▶ marts/ (dbt)
    │                                   │
[Core] identity · audit · auth · events (outbox, catálogo CloudEvents) │
[P0]  alert_engine · recommendation_engine (playbooks) · centro de comando · briefing · relatórios │
    │                                   ▼
[Módulos] P1 finanças · P2 contratos assistenciais · P3 faturamento · P4 regulação · P5 linhas · P6 materno · P7 vigilância · P8 farmácia · P9 pessoas · P10 compras e contratos
    │         ▲                 ▲
[IA] packages/ml (LightGBM, nowcasting, anomalias) · packages/llm (copiloto, text-to-SQL, extração de documentos, classificador de empenhos)
    ▼
[Apps] apps/api (FastAPI) · apps/web (React) · notificações (e-mail, SMS, WhatsApp via provedor) · exportações (CSV, Parquet, PDF)
```

## Ambientes

| Ambiente | Infra | Dados | Uso |
|---|---|---|---|
| dev | Docker Compose local | fixtures públicas + sintéticos | desenvolvimento diário |
| homolog | Kubernetes (namespace `hml`) | cópia pseudonimizada de produção | validação com usuários |
| prod | Kubernetes (nuvem governamental ou provedor contratado, região Brasil) | reais | operação |

## Decisões registradas (ADR)

- ADR-0001 Monólito modular com schemas por módulo.
- ADR-0002 DuckDB + Parquet + dbt para a camada analítica; PostgreSQL para transacional.
- ADR-0003 Gateway único de LLM com pseudonimização obrigatória e prompts versionados.
- ADR-0004 Prefect como orquestrador; conectores idempotentes particionados por competência.
- ADR-0005 Keycloak como provedor de identidade; perfis por módulo e por estabelecimento.

Novas decisões: criar `docs/adr/NNNN-titulo.md` e parar para revisão.

## Não funcionais

- Disponibilidade 99,5%; RPO 24 h (lake) e 1 h (transacional); RTO 4 h.
- Latência p95 de API < 500 ms para consultas de painel (servidas de marts materializados); respostas do copiloto < 15 s.
- Volumetria inicial: ~2 milhões de registros SIA/ano, ~60 mil AIH/ano, ~800 mil habitantes no cadastro, 16 municípios, ~30 estabelecimentos hospitalares.
- Retenção: raw por 10 anos; logs de auditoria por 5 anos.
