# 02 – IA e governança

## Padrões de IA utilizados

| Padrão | Onde | Implementação | Avaliação |
|---|---|---|---|
| Copiloto sobre dados (text-to-SQL validado + RAG de fichas de indicadores) | P0 e todos os módulos | `packages/llm/agents/data_copilot.py`: planejamento → geração de SQL sobre views `rpt_*` → validação (somente SELECT, limite 5.000 linhas, schema permitido) → execução → resposta com citação (view, filtros, `loaded_at`) | conjunto de 150 perguntas/respostas em `packages/llm/evals/copilot.jsonl`; exatidão de SQL e de valores; taxa de recusa correta |
| Classificação de texto (empenhos, laudos, petições, solicitações de regulação) | P1, P3, P8, P4 | LLM com poucos exemplos + classificador supervisionado (LightGBM sobre embeddings) quando houver >2 mil rótulos; saída com `label`, `confidence`, `rationale` | acurácia e F1 por classe; matriz de confusão; revisão humana amostral |
| Extração estruturada de documentos | P2, P8 | LLM com saída em esquema Pydantic (`structured output`), páginas renderizadas para visão quando PDF escaneado | exatidão por campo em 100 documentos anotados |
| Séries temporais e nowcasting | P7, P4, P1, P8 | statsmodels/Prophet/LightGBM com variáveis exógenas (clima, calendário), nowcasting de atraso de notificação (método de triângulo/cadeia) | MAE, cobertura do intervalo, antecedência do alerta em retro-teste 2022–2025 |
| Detecção de anomalias | P0, P1, P3, P2 | regras + isolamento (Isolation Forest) + comparação com pares (unidade/profissional/procedimento); grafos para relações credor–unidade–profissional | precisão nas alertas revisadas; taxa de falsos positivos aceita pelo gestor |
| Estratificação de risco | P4, P5, P6, P7, P9 | modelos tabulares com explicação SHAP; calibração; limiares definidos com a área técnica | AUROC, calibração, métricas por subgrupo, impacto nas filas |
| Otimização (escalas, TFD) | P9, P4 | OR-Tools (CP-SAT) com restrições normativas | viabilidade, horas extras, cobertura |
| Visão computacional (segunda leitura de imagens, fotos de obras) | P5, P1 | modelos de terceiros validados; só como segunda leitura/priorização | sensibilidade/especificidade documentadas; nunca substitui laudo |

## Gateway de LLM (packages/llm)

- Única porta de saída para provedores. Funções: `complete`, `extract(schema)`, `classify(labels)`, `embed`. Provedor padrão Anthropic; modelo por tarefa em `packages/llm/config.yaml`.
- **Pseudonimização obrigatória** na entrada (`core.identity.redact(text)`): remove CPF, CNS, nomes, endereços, telefones. Teste de regressão com 500 textos sintéticos contendo identificadores.
- Prompts em `packages/llm/prompts/<agente>/<versao>.md` com metadados (objetivo, entradas, saída, riscos); mudança de prompt exige rodar `evals` e registrar resultado.
- Caching de respostas determinísticas; limites de custo por módulo; logs sem conteúdo sensível (apenas hash, tokens, latência, modelo).
- Guardrails: recusa de ações (o copiloto não executa escrita), detecção de injeção em documentos lidos (os documentos são dados, não instruções), citação obrigatória.

## Ciclo de vida de modelos (packages/ml)

1. Especificação: problema, população, variáveis, exclusões, métrica-alvo, limiar de aceite, uso pretendido e usos proibidos (`docs/model_cards/<modelo>.md`, seção "pretendido").
2. Dados: dataset versionado (hash do Parquet), divisão temporal (treino até T-1, validação T), sem vazamento.
3. Treino e rastreio com MLflow; artefato assinado.
4. Avaliação: métricas globais e por subgrupo (sexo, raça/cor, faixa etária, município, tipo de unidade); teste de equidade; análise de erros.
5. Revisão humana (área técnica + comitê de IA) e aprovação registrada no model card.
6. Implantação como `model_id@version`; sombra (shadow) por 30 dias antes de exibir recomendações.
7. Monitoramento: deriva de dados e de desempenho; retreino programado; descontinuação documentada.

## Humano no circuito (padrão de produto)

- Toda recomendação é exibida com: valor, confiança, três principais fatores (SHAP ou racional), versão do modelo, link para a ficha.
- O usuário aceita, ajusta ou rejeita; a escolha e a justificativa são gravadas em `core.audit_event` e realimentam a avaliação.
- Pacientes e profissionais podem contestar (canal em P4/P5/P9); contestações geram revisão.

## LGPD e segurança

- Base legal: execução de políticas públicas e tutela da saúde (LGPD art. 7, III e VIII; art. 11, II, b e f). Documentar por módulo em `docs/lgpd/<modulo>.md` com RIPD.
- Minimização: cada perfil vê apenas o necessário; dados identificados apenas em fluxos assistenciais (P4, P5, P6) para profissionais com vínculo com o paciente.
- Criptografia em repouso (banco, object storage) e em trânsito; chaves em KMS; rotação anual.
- Trilhas de acesso a dados identificados consultáveis pelo encarregado; relatórios trimestrais.
- Testes de segurança: SAST (bandit, semgrep), dependências (pip-audit, npm audit), DAST em homologação, pentest anual.

## Comitê de IA e transparência

- Inventário público de modelos (nome, finalidade, dados, métricas, data de revisão) em P0.
- Reuniões bimestrais do comitê com atas; qualquer modelo com impacto em paciente ou pagamento precisa de aprovação antes de sair da sombra.
- Relatório anual de IA ao Conselho Estadual de Saúde.
