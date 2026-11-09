# Plataforma de Gestão com IA para a SESA/AP – kit de orientação ao desenvolvimento

Este diretório contém a documentação que orienta o Claude Code (e a equipe) a construir o SINAPSE, com seus doze módulos, descrito no portfólio `../estudo-saude-ap/propostas-sistemas/`. **O `CLAUDE.md` é o guia mestre, autossuficiente**: visão, pilha, regras, arquitetura, dados, inteligência integrativa, especificação de cada módulo, plano de construção com estado, qualidade, pendências e prompts. Os arquivos em `docs/` são referência estendida e nunca o contradizem. Ainda não há código: o primeiro passo é abrir o Claude Code nesta pasta e usar o prompt mestre da seção 12 do `CLAUDE.md`.

| Arquivo | Conteúdo |
|---|---|
| `CLAUDE.md` | **Guia mestre de construção** (lido automaticamente pelo Claude Code): como usar, visão do SINAPSE, pilha e convenções, regras inegociáveis, arquitetura, dados e conectores, IA e governança, SINAPSE Núcleo (ciclo cognitivo, eventos, alertas, playbooks, níveis de autonomia, executor, aprendizado), especificação dos módulos P1–P11, plano de construção com estado por história, definição de pronto, pendências, prompts e glossário |
| `docs/00_visao_e_arquitetura.md` | Princípios, diagrama lógico, ambientes, ADRs iniciais, requisitos não funcionais |
| `docs/01_dados_e_integracoes.md` | Conectores por fonte, modelo canônico (dimensões e fatos), qualidade de dados, catálogo de indicadores |
| `docs/02_ia_e_governanca.md` | Padrões de IA, gateway de LLM, ciclo de vida de modelos, humano no circuito, LGPD, comitê de IA |
| `docs/03_roteiro_sprints.md` | Ordem de construção em fases e sprints, com estado das histórias |
| `docs/04_guia_sessoes_claude_code.md` | Prompt mestre, prompts por história, por modelo e de revisão; boas práticas |
| `docs/05_inteligencia_integrativa.md` | Contrato de integração entre módulos: barramento de eventos (CloudEvents, outbox), catálogo de eventos, motor de alertas, playbooks de orientações de ação, centro de comando, briefing e relatórios |
| `docs/produtos/P0.md` a `P11.md` | Especificação de cada produto: objetivo, personas, épicos e histórias, modelo de dados, APIs, IA, critérios de aceite, prompt de arranque |
| `docs/pendencias.md` | Integrações e definições que dependem da SESA e de outros órgãos |

Dados públicos para desenvolvimento estão em `../estudo-saude-ap/dados/` e os scripts de extração de partida em `../estudo-saude-ap/scripts/`.
