# CLAUDE.md – SINAPSE: Plataforma de Gestão com IA para a SESA/AP

Este arquivo orienta o Claude Code (e qualquer pessoa desenvolvedora) no desenvolvimento das doze soluções (marca SINAPSE – Sistema Integrado de Análise, Previsão, Supervisão e Execução em Saúde) descritas em `../estudo-saude-ap/propostas-sistemas/Propostas_Sistemas_Gestao_IA_SESA_AP.md`. Leia-o inteiro antes de qualquer tarefa. As especificações por produto estão em `docs/produtos/P0.md` a `P11.md`; a ordem de construção está em `docs/03_roteiro_sprints.md`.

## 1. O que estamos construindo

Uma plataforma modular (monólito modular, um repositório) para a Secretaria de Estado da Saúde do Amapá, composta por (P2 cobre contratos assistenciais com metas de produção; P10 cobre todos os contratos administrativos, compras e fornecedores e fornece a P2 o cadastro contratual base):

| Código | Módulo | Pasta |
|---|---|---|
| P0 | Inteligência Integrativa: plataforma de dados, barramento de eventos, alertas, orientações de ação, centro de comando e copiloto | `modules/plataforma` |
| P1 | Governança financeira do FES | `modules/financas` |
| P2 | Contratos, OS e metas assistenciais | `modules/contratos` |
| P3 | Faturamento e auditoria SUS | `modules/faturamento` |
| P4 | Regulação de acesso e leitos | `modules/regulacao` |
| P5 | Linhas de cuidado (oncologia e crônicas) | `modules/linhas_cuidado` |
| P6 | Rede materno-infantil e apoio à APS | `modules/materno_infantil` |
| P7 | Vigilância preditiva | `modules/vigilancia` |
| P8 | Assistência farmacêutica e judicialização | `modules/farmacia` |
| P9 | Força de trabalho e escalas | `modules/pessoas` |
| P10 | Contratos administrativos, compras e fornecedores | `modules/compras_contratos` |
| P11 | Controle social (CES/AP), Auditoria do SUS e Ouvidoria do SUS | `modules/cidadao` |

Todos os módulos dependem de P0 (dados, identidade, auditoria, eventos, LLM gateway). Nenhum módulo acessa a base de outro diretamente: usa os serviços do núcleo (`packages/core`) ou os marts analíticos. **Nenhum módulo é uma ilha:** todo módulo publica seus eventos de domínio no barramento (`docs/05_inteligencia_integrativa.md`), expõe indicadores ao catálogo e executa as tarefas geradas pelas orientações de ação do núcleo. Uma história de módulo só está pronta quando seus eventos do catálogo são publicados e testados por contrato.

## 2. Pilha tecnológica (decidida; não trocar sem ADR)

- **Linguagem de backend:** Python 3.12. API com FastAPI + Pydantic v2 + SQLAlchemy 2 (async) + Alembic.
- **Banco transacional:** PostgreSQL 16 com PostGIS. Um schema por módulo (`plataforma`, `financas`, ...) e schema `core` compartilhado.
- **Camada analítica (lake):** arquivos Parquet em object storage (MinIO em dev, S3 compatível em prod) nas zonas `raw/`, `trusted/`, `marts/`; consultas com DuckDB; transformações com dbt-core (adapter duckdb em dev, postgres em prod para marts servidos).
- **Orquestração:** Prefect 3 (fluxos em `pipelines/flows`). Cada conector é um fluxo idempotente com particionamento por competência.
- **ML:** scikit-learn, LightGBM, statsmodels (nowcasting), Prophet opcional; rastreio com MLflow; artefatos versionados.
- **LLM:** acesso somente via `packages/llm` (gateway interno). Provedor padrão Anthropic (`claude-sonnet-5-5` para tarefas de rotina, `claude-opus-5-5` para raciocínio complexo), configurável por variável de ambiente. Nunca chamar SDKs de LLM fora do gateway.
- **Frontend:** React 18 + TypeScript + Vite, Tailwind, componentes shadcn/ui, Apache ECharts para gráficos, TanStack Query e Router. Idioma da interface: português do Brasil.
- **Identidade:** Keycloak (OIDC), perfis por módulo e por unidade; integração futura com gov.br.
- **Infra:** Docker Compose em dev (`infra/compose`), Kubernetes + Helm em prod (`infra/helm`), Terraform para nuvem (`infra/terraform`). Observabilidade com OpenTelemetry, Prometheus, Grafana e Loki.
- **Testes:** pytest (+ pytest-asyncio, hypothesis para regras), Playwright para e2e, dbt tests para dados, Great Expectations para qualidade de dados nas zonas trusted.

## 3. Convenções

- Código, identificadores, nomes de tabelas e de APIs em **inglês**; termos do domínio SUS que não têm tradução consagrada permanecem em português (`aih`, `apac`, `cnes`, `sigtap`, `competencia`). Interface, documentação, mensagens de erro ao usuário e commits em **português**.
- Estrutura do repositório:

```
plataforma-gestao-ia/
  CLAUDE.md  docs/  pyproject.toml  package.json
  packages/core        # domínio compartilhado: entes, estabelecimentos, pacientes (pseudonimizados), usuários, auditoria
  packages/connectors  # conectores de origem (datasus, siops, siconfi, esus, sisreg, contabil, folha)
  packages/ml          # pipelines de treino/predição, registry, avaliação, model cards
  packages/llm         # gateway LLM, prompts versionados, RAG, text-to-SQL validado, guardrails
  modules/<modulo>/    # api/ (routers, services, schemas), domain/, repositories/, pipelines/, web/ (feature do frontend), tests/
  apps/api             # composição FastAPI (monta routers dos módulos)
  apps/web             # app React (monta features dos módulos)
  pipelines/           # fluxos Prefect e projeto dbt (models por módulo)
  infra/               # compose, helm, terraform, scripts
  data/fixtures        # amostras públicas para desenvolvimento (ver seção 5)
```

- Um módulo expõe: `routers.py` (FastAPI), `services.py`, `schemas.py`, `models.py` (ORM), `pipelines/` (fluxos Prefect e models dbt), `web/` (páginas e componentes), `tests/`. Regras de negócio ficam em `domain/`, sem dependência de framework.
- Migrações: Alembic por schema; nunca editar migrações aplicadas.
- Datas e competências: competência SUS como `YYYYMM` (inteiro) e período fiscal como `exercicio` + `bimestre`. Valores monetários em `NUMERIC(18,2)`, nunca float.
- Toda tabela de fato traz `source_system`, `source_version`, `loaded_at`; toda tabela de domínio traz `created_at`, `updated_at`, `created_by`.
- Eventos seguem CloudEvents 1.0 com tipo `sesa.<modulo>.<entidade>.<acao>.v1`, catalogados em `packages/core/events/catalog.yaml` com JSON Schema; publicação via outbox transacional; payload sem dados identificados.
- Logs estruturados (JSON) sem dados pessoais. Auditoria de acesso e de decisão em `core.audit_event` (quem, quando, o quê, por quê, versão do modelo quando houver).

## 4. Regras inegociáveis (segurança, LGPD, IA)

1. **Dados pessoais de saúde são sensíveis (LGPD art. 11).** Identificadores diretos (CPF, CNS, nome, endereço) ficam apenas no schema `core.identity`, criptografados, com acesso por serviço dedicado. Todos os demais schemas usam `person_key` (pseudônimo estável). Nenhum dado identificado entra em prompt de LLM, log, fixture ou teste.
2. **Autonomia graduada com humano no circuito.** Toda saída de modelo traz `explanation`, `confidence` e `model_version`. As ações do núcleo seguem o nível de autonomia do playbook (`docs/05`): 0 informa; 1 alerta e sugere; 2 prepara e executa após aprovação de um responsável; 3 executa automaticamente apenas ações operacionais, reversíveis e de baixo risco listadas no catálogo de ações (abrir tarefa, notificar, agendar, gerar documento revisado, reservar agenda, bloquear pagamento sem atesto até revisão). Decisão clínica, pagamento, assinatura ou rescisão de contrato, punição a servidor e alteração de registro contábil **nunca** são automáticos. Toda ação, humana ou automática, é registrada em `core.audit_event` com ator, base (regra, playbook, modelo) e reversão possível.
3. **LLM com guardrails.** Text-to-SQL só executa consultas somente leitura, em views dos marts, com limite de linhas e validação de schema; toda resposta cita a view, o filtro e a data de atualização. Prompts são versionados em `packages/llm/prompts/` e avaliados com conjuntos de teste em `packages/llm/evals/`.
4. **Sem segredos no código.** Variáveis via `.env` (dev) e secret manager (prod). Nunca comitar `.env`, dumps, chaves ou dados reais.
5. **Reprodutibilidade.** Todo modelo tem model card (`docs/model_cards/`), dataset versionado, métricas por subgrupo (sexo, raça/cor, faixa etária, município) e teste de regressão de desempenho.
6. **Acessibilidade e idioma.** Interface em português, conforme WCAG 2.1 AA, funcional em telas de 1366 px e tablets.

## 5. Dados para desenvolvimento

Use as bases públicas já extraídas no repositório irmão `../estudo-saude-ap/dados/` (TABNET SIH/SIA/CNES/SIM/SINASC/SINAN em `tabnet/` e `tabnet2/`, `siconfi/` RREO e DCA em formato longo, `siops/anexo12/`, `emendas/`, `ibge/`) como fixtures de desenvolvimento. Os scripts `../estudo-saude-ap/scripts/tabnet.py`, `extract_siconfi.py` e `extract_siops_anexo12.py` são o ponto de partida dos conectores em `packages/connectors` (portar, não copiar: adicionar tipagem, testes, idempotência e particionamento). Para dados identificados (prontuário, e-SUS, regulação, folha) use geradores sintéticos em `data/fixtures/synthetic/` (Faker com semente fixa); jamais dados reais.

## 6. Comandos

```bash
make dev            # sobe postgres, minio, keycloak, prefect, api e web (docker compose)
make migrate        # alembic upgrade head em todos os schemas
make seed           # carrega fixtures públicas e sintéticas
make test           # pytest + dbt test + lint (ruff, mypy, eslint, tsc)
make e2e            # playwright
make pipelines      # registra e executa fluxos Prefect locais
make docs           # gera documentação de API (OpenAPI) e model cards
```

Antes de abrir PR: `make test` verde, cobertura de `domain/` acima de 90%, migração revisada, OpenAPI atualizado, e entrada no `CHANGELOG.md`.

## 7. Como trabalhar com o Claude Code neste repositório

- Comece cada sessão lendo este arquivo, o `docs/produtos/P<n>.md` do módulo em questão e o estado do roteiro em `docs/03_roteiro_sprints.md`.
- Use o modo de planejamento para tarefas que criem ou alterem mais de três arquivos; apresente o plano com arquivos, migrações e testes antes de codar.
- Trabalhe por história de usuário (épico → história → tarefas), em ramos `feat/<modulo>/<historia>`, com commits pequenos e mensagens em português no imperativo ("Adiciona conector SIH RD").
- Escreva o teste antes ou junto com o código; para regras de negócio (cálculo do mínimo constitucional, apuração de metas, classificação de risco) o teste é a especificação.
- Quando uma decisão de arquitetura for necessária, crie um ADR em `docs/adr/NNNN-titulo.md` (contexto, decisão, consequências) e pare para revisão humana.
- Não invente integrações: se uma origem (SISREG, sistema contábil, folha) não tiver especificação em `docs/01_dados_e_integracoes.md`, implemente contra um adaptador fictício documentado e registre a pendência em `docs/pendencias.md`.
- Nunca reduza escopo silenciosamente: se algo não couber na sessão, deixe a história em `docs/03_roteiro_sprints.md` marcada como parcial, com o que falta.

## 8. Definição de pronto (DoD) de uma história

Código com testes verdes; migração e seed; eventos do catálogo publicados e testados por contrato; indicadores registrados no catálogo de P0; endpoint documentado no OpenAPI; tela acessível e em português; auditoria de ações; métricas e logs; model card (quando houver modelo); documentação do módulo atualizada; demonstração registrada em `docs/demos/<modulo>.md` com capturas de tela geradas por Playwright.
