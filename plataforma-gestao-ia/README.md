# Plataforma de Gestão com IA para a SESA/AP – kit de orientação ao desenvolvimento

Este diretório contém a documentação que orienta o Claude Code (e a equipe) a construir as onze soluções do portfólio `../estudo-saude-ap/propostas-sistemas/`. Ainda não há código: o primeiro passo é executar o prompt mestre de `docs/04_guia_sessoes_claude_code.md` a partir desta pasta.

| Arquivo | Conteúdo |
|---|---|
| `CLAUDE.md` | Regras do projeto para o Claude Code: pilha, convenções, segurança/LGPD, dados de desenvolvimento, comandos, definição de pronto |
| `docs/00_visao_e_arquitetura.md` | Princípios, diagrama lógico, ambientes, ADRs iniciais, requisitos não funcionais |
| `docs/01_dados_e_integracoes.md` | Conectores por fonte, modelo canônico (dimensões e fatos), qualidade de dados, catálogo de indicadores |
| `docs/02_ia_e_governanca.md` | Padrões de IA, gateway de LLM, ciclo de vida de modelos, humano no circuito, LGPD, comitê de IA |
| `docs/03_roteiro_sprints.md` | Ordem de construção em fases e sprints, com estado das histórias |
| `docs/04_guia_sessoes_claude_code.md` | Prompt mestre, prompts por história, por modelo e de revisão; boas práticas |
| `docs/05_inteligencia_integrativa.md` | Contrato de integração entre módulos: barramento de eventos (CloudEvents, outbox), catálogo de eventos, motor de alertas, playbooks de orientações de ação, centro de comando, briefing e relatórios |
| `docs/produtos/P0.md` a `P10.md` | Especificação de cada produto: objetivo, personas, épicos e histórias, modelo de dados, APIs, IA, critérios de aceite, prompt de arranque |
| `docs/pendencias.md` | Integrações e definições que dependem da SESA e de outros órgãos |

Dados públicos para desenvolvimento estão em `../estudo-saude-ap/dados/` e os scripts de extração de partida em `../estudo-saude-ap/scripts/`.
