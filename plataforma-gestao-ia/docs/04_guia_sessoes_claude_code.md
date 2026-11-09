# 04 – Guia de sessões com o Claude Code

## Prompt mestre (primeira sessão do repositório)

```
Você vai iniciar a construção da Plataforma de Gestão com IA da SESA/AP. Leia CLAUDE.md e todos os arquivos de docs/ (00 a 04 e docs/produtos/P0–P10). Depois:
1. Crie a estrutura do monorepo descrita em CLAUDE.md (uv + pyproject com workspaces, pnpm + Vite, Makefile, docker compose com postgres/postgis, minio, keycloak, redis, prefect; CI no GitHub Actions com lint, testes e build).
2. Implemente packages/core (modelos base, auditoria, barramento de eventos, serviço de identidade com person_key e redact()) com testes.
3. Porte os conectores SICONFI, SIOPS Anexo 12, CGU e IBGE a partir de ../estudo-saude-ap/scripts (tipagem, idempotência, partições, testes com os CSVs de ../estudo-saude-ap/dados).
4. Crie o projeto dbt com staging dessas fontes e as dimensões dim_municipality e dim_budget_account.
5. Suba apps/api (FastAPI com autenticação Keycloak) e apps/web (layout, navegação por módulo, componente de gráfico ECharts) com um painel mínimo de execução orçamentária da função Saúde 2022–2026.
Apresente primeiro um plano por etapa com arquivos e testes; implemente etapa a etapa, rodando `make test` ao fim de cada uma; registre ADRs para decisões não cobertas pela documentação; atualize docs/03_roteiro_sprints.md.
```

## Prompt por história (modelo)

```
Contexto: CLAUDE.md, docs/produtos/P<n>.md, docs/01 e docs/02. História: "<texto da história>" (épico "<épico>").
Entregue: plano → implementação → testes → demonstração.
Restrições: dados identificados só em core.identity; recomendações de IA com confiança, racional e model_version; interface em português; sem ação automática sobre paciente, pagamento, contrato ou servidor.
Ao terminar: `make test` verde, OpenAPI atualizado, docs/demos/<modulo>.md com capturas (Playwright), roteiro e CHANGELOG atualizados. Se algo ficar fora, marque [~] no roteiro e descreva o que falta.
```

## Prompt para modelos de IA

```
Vamos construir o modelo <nome> (docs/produtos/P<n>.md, seção IA). Siga docs/02: escreva primeiro o model card (docs/model_cards/<nome>.md) com uso pretendido, dados, exclusões, métrica-alvo e limiar; prepare o dataset versionado a partir das fixtures; divisão temporal; treine com rastreio MLflow; avalie global e por subgrupo (sexo, raça/cor, faixa etária, município); escreva o teste de regressão de desempenho; exponha via packages/ml com Prediction(value, confidence, explanation, model_version). Não exiba recomendações na interface antes do período de sombra; registre no inventário de modelos (P0).
```

## Prompt para revisão

```
Revise o diff desta história com foco em: vazamento de dados identificados (logs, prompts, fixtures), ações automáticas indevidas, SQL gerado por LLM sem validação, migrações destrutivas, testes ausentes para regras de domínio, acessibilidade e idioma da interface. Use /code-review e liste achados por severidade.
```

## Boas práticas específicas

- Peça sempre o plano antes de alterar mais de três arquivos; aprove explicitamente.
- Mantenha as sessões por módulo; não misture P1 e P4 na mesma sessão.
- Quando o Claude Code propuser biblioteca nova, exija ADR e checagem de licença.
- Para integrações sem especificação (SISREG, contábil, folha, Hórus, GAL, e-SUS), aceite apenas adaptadores fictícios documentados e registre em `docs/pendencias.md`.
- Exija `make test` e capturas de tela antes de considerar a história pronta; nada de "deve funcionar".
- Use `/security-review` ao fim de cada fase e antes de homologação.
- Mantenha `docs/03_roteiro_sprints.md` como fonte única do estado do projeto.
