# 1. Apresentação

## 1.1 Propósito deste documento

Este portfólio reúne onze propostas de sistemas de gestão com inteligência artificial (IA) para a Secretaria de Estado da Saúde do Amapá (SESA/AP), concebidas para a gestão que assume em janeiro de 2027. Cada proposta nasce de um problema medido nos cinco estudos de transição elaborados a partir de dados públicos (produção hospitalar e ambulatorial; vigilância em saúde; atenção primária e saúde materno-infantil; violências e saúde mental; oncologia e doenças crônicas; financiamento e gastos) e descreve a solução, o papel da IA, as integrações, os resultados esperados, o plano de implantação e o investimento indicativo.

O documento tem finalidade comercial: apresentar produtos que podem ser contratados de forma modular ou como plataforma integrada, com argumentos de valor dirigidos ao secretário de Estado, à equipe de transição e aos órgãos de controle.

## 1.2 Por que agora

A SESA/AP gerencia o maior orçamento do Estado (R$ 2,33 bilhões em 2025, 20,4% da despesa estadual e R$ 2.890 por habitante, o maior valor entre os estados), mas opera com informação fragmentada: metade da despesa está classificada em Administração Geral, o faturamento SUS registrado (R$ 203 milhões) equivale a menos de um décimo do gasto público, 139 leitos de UTI existentes convivem com 19 habilitados, o rastreamento de câncer caiu pela metade e as transferências da União, em grande parte emendas de custeio temporário, já financiam um terço da despesa. A transição é o momento em que decisões de arquitetura de dados e de gestão são tomadas para quatro anos.

## 1.3 Princípios comuns das soluções

1. **Dados antes de telas:** todas as soluções compartilham uma camada única de dados (produto P0), integrada aos sistemas nacionais (SIH, SIA, CNES, SINAN, SIM, SINASC, e-SUS APS, SISREG, SIOPS) e estaduais (sistema contábil, folha, regulação, almoxarifado).
2. **IA com humano no circuito:** modelos preditivos, de classificação e de linguagem apoiam a decisão; a decisão clínica, regulatória ou financeira permanece com o profissional habilitado, com registro de quem decidiu e por quê.
3. **Resultado mensurável:** cada produto define indicadores de linha de base (extraídos dos estudos) e metas de 12 e 36 meses, com parcela da remuneração vinculada ao resultado quando couber.
4. **Conformidade:** LGPD (dados de saúde como dados sensíveis, art. 11), Lei 14.133/2021, normas do Ministério da Saúde para interoperabilidade (RNDS, padrões HL7 FHIR e TISS) e trilhas de auditoria completas.
5. **Soberania e continuidade:** código, dados e modelos hospedados em nuvem governamental ou em ambiente contratado pelo Estado, com cláusula de transferência de tecnologia e portabilidade.

# 2. Visão geral do portfólio

Tabela: Portfólio de soluções propostas, problema de origem e eixo de gestão

| Código | Solução | Problema medido nos estudos | Eixo |
|---|---|---|---|
| P0 | Plataforma de Dados e Copiloto do Gestor | Informação dispersa em dez sistemas; ausência de sala de situação integrada | Base |
| P1 | Governança Financeira do FES com IA | 48,5% da despesa em Administração Geral; investimentos com 22% de execução; R$ 110 milhões de RP de 2022 | Governança e finanças |
| P2 | Gestão de Contratos, OS e Metas Assistenciais | Despesa com entidades privadas saltou de 4,9% para 18,3% em um ano; contratos sem monitoramento público | Governança e finanças |
| P3 | Faturamento e Auditoria SUS Inteligente | Faturamento de R$ 216 por habitante (18º do país); R$ 25,6 milhões em procedimentos vasculares atípicos | Governança e finanças |
| P4 | Regulação Inteligente de Acesso e Leitos | 139 leitos de UTI existentes e 19 habilitados; filas e TFD sem visibilidade; AVC de 464 para 1.147 internações | Acesso e assistência |
| P5 | Linhas de Cuidado em Oncologia e Crônicas | Razão de rastreamento 0,15 (mama) e 0,18 (colo); prazo legal de 60 dias não monitorado | Acesso e assistência |
| P6 | Rede Materno-Infantil e Apoio à APS | Mortalidade materna 82,3/100 mil (2ª do país); infantil 17,8 por mil (3ª); cobertura APS desigual | Acesso e assistência |
| P7 | Vigilância em Saúde Preditiva | Dengue 10.693 casos em 2024; tuberculose 77/100 mil (3ª); sífilis congênita 15,6 por mil (4ª) | Vigilância e inteligência |
| P8 | Assistência Farmacêutica e Judicialização com IA | Medicamentos informados como zero no SIOPS; judicialização sem base pública | Vigilância e inteligência |
| P9 | Força de Trabalho e Escalas com IA | Pessoal é 44% da despesa; folha por vínculo e absenteísmo desconhecidos | Vigilância e inteligência |
| P10 | Gestão de Contratos Administrativos, Compras e Fornecedores | Cerca de R$ 900 milhões anuais em terceiros e entidades privadas; obras paradas; passivo com fornecedores desconhecido; contratos em disputa | Governança e finanças |

Fonte: estudos de transição SESA/AP 2022–2026 (ALMEIDA, 2026).

Tabela: Síntese de prazos e investimento indicativo por solução

| Código | Implantação (meses) | Implantação (R$ mil) | Operação mensal (R$ mil) | Modelo de remuneração |
|---|---:|---:|---:|---|
| P0 | 4 a 6 | 900 a 1.400 | 120 a 180 | Licença SaaS + implantação |
| P1 | 3 a 5 | 600 a 900 | 70 a 110 | Licença SaaS + implantação |
| P2 | 3 a 4 | 400 a 600 | 50 a 80 | Licença SaaS + implantação |
| P3 | 4 a 6 | 500 a 800 | 60 a 90 | Licença + parcela por resultado (faturamento recuperado) |
| P4 | 6 a 9 | 1.200 a 1.800 | 150 a 220 | Licença SaaS + implantação |
| P5 | 4 a 6 | 500 a 750 | 60 a 90 | Licença SaaS + implantação |
| P6 | 4 a 6 | 450 a 700 | 55 a 85 | Licença SaaS + cofinanciamento municipal |
| P7 | 3 a 5 | 400 a 650 | 50 a 80 | Licença SaaS + implantação |
| P8 | 4 a 6 | 450 a 700 | 55 a 85 | Licença SaaS + implantação |
| P9 | 3 a 5 | 350 a 550 | 45 a 70 | Licença SaaS + implantação |
| P10 | 4 a 6 | 500 a 800 | 60 a 90 | Licença SaaS + parcela por economia em compras |
| Portfólio completo | 12 a 18 | 6.250 a 9.650 | 775 a 1.180 | Desconto de 15% a 20% para contratação integrada |

Nota: valores indicativos em reais de 2026, estimados pelo proponente para fins de dimensionamento e sujeitos a detalhamento após levantamento de requisitos; não incluem infraestrutura de nuvem, que pode ser contratada pelo Estado em ata própria. O portfólio completo representa cerca de 0,5% a 0,6% da despesa anual da SESA.

# 3. P0 – Plataforma de Dados e Copiloto do Gestor

## 3.1 Problema

A SESA não dispõe de uma visão integrada: produção (SIH, SIA), estrutura (CNES), vigilância (SINAN), mortalidade e nascimentos (SIM, SINASC), atenção primária (e-SUS APS, SISAB), regulação (SISREG e sistema estadual), finanças (sistema contábil, SIOPS) e pessoas (folha) vivem em bases separadas, com extrações manuais e defasagem de meses. Os cinco estudos de transição precisaram de centenas de tabulações para montar o quadro que a gestão deveria ter em tempo real.

## 3.2 Solução

Plataforma de dados (data lake e camada analítica) com conectores para os sistemas nacionais e estaduais, catálogo de indicadores oficiais (Pacto Interfederativo, Previne/cofinanciamento da APS, RREO Anexo 12) e sala de situação com painéis por região, município, unidade e linha de cuidado. Sobre a plataforma, um copiloto de linguagem natural permite ao gestor perguntar, em português, "quantas gestantes de alto risco sem vinculação ao parto há em Santana?" ou "qual a execução do investimento do Hospital de Emergência?" e receber resposta com a fonte, a data de atualização e o caminho para o dado.

## 3.3 Uso da IA

- Copiloto conversacional sobre dados (modelo de linguagem com geração de consultas validadas e citação de fonte; sem acesso a dados identificados sem perfil autorizado).
- Detecção automática de anomalias em séries (produção, despesa, notificações) com alertas explicados.
- Harmonização de cadastros (pacientes, profissionais, estabelecimentos) por pareamento probabilístico.
- Geração assistida de relatórios periódicos (boletins, relatório quadrimestral de gestão, respostas a órgãos de controle) a partir dos indicadores oficiais.

## 3.4 Integrações e dados

TABNET e arquivos de disseminação do DATASUS (SIH, SIA, CNES, SINAN, SIM, SINASC), e-SUS APS e SISAB, SISREG e regulação estadual, sistema contábil e de folha do Estado, SIOPS, SICONFI, RNDS (quando habilitada), prontuários hospitalares (via HL7 FHIR ou extração periódica).

## 3.5 Resultados esperados e indicadores

| Indicador | Linha de base (estudos) | Meta 12 meses | Meta 36 meses |
|---|---|---|---|
| Defasagem média entre o fato e o painel | 3 a 6 meses (TABNET) | 30 dias (bases locais em 24 h) | 7 dias |
| Indicadores oficiais com cálculo automático e auditável | 0 | 60 | 120 |
| Pedidos de informação respondidos com apoio do copiloto | 0 | 70% | 90% |
| Unidades com painel próprio de produção e custo | 0 | 12 hospitais e 16 municípios | Toda a rede |

## 3.6 Implantação e investimento

Quatro a seis meses em três ondas: (1) conectores DATASUS e finanças, sala de situação da transição; (2) regulação, APS e vigilância; (3) prontuários e copiloto em produção. Implantação de R$ 900 mil a R$ 1,4 milhão e operação de R$ 120 mil a R$ 180 mil mensais, incluindo sustentação, evolução e treinamento contínuo.

## 3.7 Argumento de venda

É o alicerce de todos os demais produtos e devolve ao Estado o controle do seu próprio dado: a gestão passa a decidir com evidência diária em vez de tabulações anuais, e o copiloto reduz semanas de trabalho de assessoria técnica a minutos.

# 4. P1 – Governança Financeira do FES com IA

## 4.1 Problema

A despesa da função Saúde cresceu 70% em três anos, mas 48,5% está lançada em Administração Geral, a despesa com medicamentos é informada como zero, as despesas de capital liquidaram 22% da dotação em 2024 (R$ 124 milhões inscritos em restos a pagar) e R$ 110 milhões de ASPS de 2022 ainda constavam a pagar em 2026. O percentual aplicado em saúde caiu de 19,4% para 16,8% e chegou a 15,3% em 2026, no limite do mínimo estadual de 15%. As emendas parlamentares (R$ 606 milhões em 2025) têm prazos de execução e saldos em conta que ninguém consolida.

## 4.2 Solução

Sistema de governança financeira do Fundo Estadual de Saúde (FES) que integra orçamento, execução, fontes, restos a pagar, contas bancárias vinculadas, emendas e convênios, com reclassificação da despesa por subfunção, programa e centro de custo (hospital, unidade, linha de cuidado), projeção do mínimo constitucional e painel de investimentos com situação física e financeira de cada obra e aquisição.

## 4.3 Uso da IA

- Classificador de empenhos: modelo de linguagem treinado no histórico lê o objeto do empenho, o credor e a dotação e sugere subfunção, programa, centro de custo e natureza (pessoal, medicamentos, terceiros), com revisão humana; corrige na origem o problema da Administração Geral.
- Previsão do mínimo constitucional: projeção bimestral da base de cálculo (FPE, ICMS, IRRF) e da despesa própria, com alerta de risco de descumprimento e simulação de medidas.
- Detecção de anomalias e de risco de glosa pelos órgãos de controle em empenhos, liquidações e pagamentos (fracionamento, duplicidade, atipicidade de valores por fornecedor).
- Gestão de prazos de emendas e convênios com alertas de devolução e sugestão de remanejamento.
- Visão computacional opcional para acompanhamento fotográfico de obras (medição versus cronograma).

## 4.4 Integrações e dados

Sistema contábil e orçamentário do Estado, extratos bancários do FES, SIOPS, SICONFI, Portal da Transparência (emendas), Transferegov e Fundo Nacional de Saúde (saldos e prazos), sistema de obras da secretaria de infraestrutura.

## 4.5 Resultados esperados e indicadores

| Indicador | Linha de base | Meta 12 meses | Meta 36 meses |
|---|---|---|---|
| Despesa classificada em Administração Geral | 48,5% | 20% | menos de 10% |
| Execução (liquidado/dotação) das despesas de capital | 22% a 32% | 55% | 80% |
| Restos a pagar de ASPS cancelados por falta de respaldo | R$ 20 a 97 milhões por exercício | menos de R$ 5 milhões | menos de R$ 2 milhões |
| Saldos de emendas sem execução além do prazo | desconhecido | zero devoluções | zero devoluções |
| Antecedência do alerta de risco do mínimo | nenhuma | 2 bimestres | 3 bimestres |

## 4.6 Implantação e investimento

Três a cinco meses: carga histórica 2022–2026, treinamento do classificador, painel do mínimo e dos investimentos, integração bancária. Implantação de R$ 600 mil a R$ 900 mil e operação de R$ 70 mil a R$ 110 mil mensais.

## 4.7 Argumento de venda

Transforma o FES em um fundo legível para o secretário, o Tribunal de Contas e o Conselho de Saúde; cada ponto percentual de execução de investimento recuperado vale R$ 2,5 milhões por ano, e um único cancelamento evitado de restos a pagar paga o sistema.

# 5. P2 – Gestão de Contratos, Organizações Sociais e Metas Assistenciais

## 5.1 Problema

A participação de instituições privadas sem fins lucrativos na despesa com saúde saltou de 4,9% (2024) para 18,3% (2025), cerca de R$ 425 milhões, e os serviços de terceiros pessoa jurídica somam outros 21%. O estudo geral identificou contratos em disputa (Hospital São Camilo) e produção registrada em unidades sem perfil. Não há, no espaço público, metas, relatórios de monitoramento nem conciliação entre produção, metas contratuais e pagamentos.

## 5.2 Solução

Sistema de ciclo de vida de contratos assistenciais (contratos de gestão com organizações sociais, convênios com filantrópicos, prestadores complementares e serviços terceirizados): cadastro de metas quantitativas e qualitativas, apuração automática da produção (SIH, SIA, prontuário), cálculo da parcela variável, comissões de acompanhamento com atas e pendências, e painel de desempenho por unidade.

## 5.3 Uso da IA

- Apuração automática das metas a partir da produção registrada, com conciliação entre o faturado no SUS, o informado pelo prestador e o pago pelo Estado, e sinalização de divergências.
- Leitura de documentos (relatórios mensais, notas fiscais, planilhas de produção) por modelos de linguagem e visão, com extração estruturada e verificação cruzada.
- Pontuação de risco contratual (atraso de entrega, queda de produção, concentração de fornecedor, inconsistências de faturamento) para priorizar a fiscalização.
- Assistente de redação de termos aditivos, notificações e pareceres com base em modelos padronizados e na legislação.

## 5.4 Integrações e dados

P0 (produção e CNES), sistema contábil (P1), sistema de compras e contratos do Estado, Portal Nacional de Contratações Públicas, prontuários das unidades sob gestão terceirizada.

## 5.5 Resultados esperados e indicadores

| Indicador | Linha de base | Meta 12 meses | Meta 36 meses |
|---|---|---|---|
| Contratos assistenciais com metas apuradas automaticamente | 0 | 100% dos contratos de gestão | 100% de todos os contratos |
| Prazo de apuração da parcela variável | desconhecido (manual) | 10 dias após o fechamento | 5 dias |
| Divergência entre produção faturada e produção contratual | não medida | medida e publicada mensalmente | abaixo de 5% |
| Economia por glosa contratual fundamentada | não medida | 2% do valor contratado | 3% a 5% |

## 5.6 Implantação e investimento

Três a quatro meses, iniciando pelos contratos de gestão hospitalar. Implantação de R$ 400 mil a R$ 600 mil e operação de R$ 50 mil a R$ 80 mil mensais.

## 5.7 Argumento de venda

Com R$ 900 milhões anuais em contratos de terceiros e entidades privadas, 2% de economia por glosa fundamentada representa R$ 18 milhões por ano, trinta vezes o custo do sistema, além de blindar a gestão perante os órgãos de controle.

# 6. P3 – Faturamento e Auditoria SUS Inteligente

## 6.1 Problema

O Amapá faturou R$ 216 por habitante em produção SUS em 2024, contra R$ 260 no Brasil (18ª posição), com produção hospitalar per capita (R$ 62) entre as menores do país, enquanto gasta o maior valor per capita em saúde. Ao mesmo tempo, o estudo geral encontrou R$ 25,6 milhões em procedimentos vasculares ambulatoriais atípicos e trombectomias em volume incompatível com a rede, e internações oncológicas em unidades sem perfil. Há subfaturamento de um lado e risco de faturamento indevido do outro.

## 6.2 Solução

Sistema de gestão do faturamento SUS para os hospitais estaduais e de auditoria analítica da produção própria e contratada: codificação assistida de AIH e APAC, crítica prévia às regras do SIGTAP, acompanhamento de tetos e habilitações, identificação de procedimentos realizados e não faturados, e módulo de auditoria com trilhas de risco por prestador, profissional e procedimento.

## 6.3 Uso da IA

- Codificação assistida: modelo de linguagem lê o prontuário e sugere diagnóstico principal, procedimentos e compatibilidades, apontando documentação faltante antes do envio.
- Recuperação de faturamento: cruzamento de prontuário, prescrição e exames com a produção enviada para localizar procedimentos realizados e não cobrados.
- Detecção de atipicidades: modelos estatísticos e de grafos identificam padrões incompatíveis (volume por profissional, procedimentos sem estrutura habilitada, repetições), priorizando a auditoria in loco.
- Simulação de habilitações: estimativa do incremento de teto com novas habilitações (UTI, oncologia, cardiologia) a partir da produção real.

## 6.4 Integrações e dados

SIH e SIA (SISAIH01, BPA, APAC), SIGTAP, CNES, prontuários hospitalares, P0 e P2.

## 6.5 Resultados esperados e indicadores

| Indicador | Linha de base | Meta 12 meses | Meta 36 meses |
|---|---|---|---|
| Valor aprovado SIH+SIA per capita | R$ 252 (2025) | R$ 290 | R$ 340 (média nacional) |
| Leitos de UTI habilitados | 19 de 139 existentes | 60 | 100 |
| AIH rejeitadas ou glosadas | não medida | redução de 30% | redução de 50% |
| Procedimentos atípicos auditados | 0 | 100% dos casos sinalizados | manutenção |

## 6.6 Implantação e investimento

Quatro a seis meses, começando pelo Hospital de Clínicas, Hospital de Emergência e maternidade estadual. Implantação de R$ 500 mil a R$ 800 mil, operação de R$ 60 mil a R$ 90 mil mensais e parcela por resultado de 8% a 12% sobre o faturamento adicional comprovado nos primeiros 24 meses.

## 6.7 Argumento de venda

Elevar o faturamento per capita ao patamar nacional significa cerca de R$ 35 milhões anuais a mais em recursos federais, com a vantagem de remuneração parcialmente vinculada ao resultado: o Estado só paga a parcela variável sobre o que efetivamente receber.

# 7. P4 – Regulação Inteligente de Acesso e Leitos

## 7.1 Problema

O Estado tem 139 leitos de UTI existentes e 19 habilitados, filas de consultas, exames e cirurgias sem visibilidade pública, Tratamento Fora de Domicílio sem rastreabilidade e crescimento acelerado das urgências tempo-dependentes (internações por AVC de 464 para 1.147; infarto de 206 para 380; mortes violentas em 45,2 por 100 mil). A regulação é feita em sistemas desconectados e por telefone, e o paciente não sabe sua posição na fila.

## 7.2 Solução

Central de regulação integrada (ambulatorial, hospitalar, urgência e TFD) com fila única por especialidade e risco, gestão de leitos em tempo real (censo eletrônico), protocolos de encaminhamento, teleconsultoria para a atenção primária, aplicativo e mensagens para o paciente e painel público de filas por município.

## 7.3 Uso da IA

- Classificação de risco e priorização de fila por modelos treinados em protocolos clínicos e no histórico, com explicação dos fatores e revisão do médico regulador.
- Previsão de ocupação de leitos e de demanda de urgência por unidade (sazonalidade, epidemias, eventos), para abrir e fechar capacidade com antecedência.
- Encaminhamento assistido: leitura da solicitação (texto livre) e sugestão de especialidade, prioridade e exames prévios faltantes; devolução automática de solicitações incompletas.
- Otimização de TFD: alocação de passagens, hospedagem e agendas em serviços de referência fora do estado, com previsão de custo.
- Assistente de contato com o paciente (confirmação, reagendamento, orientação) por mensagens, reduzindo absenteísmo.

## 7.4 Integrações e dados

SISREG, sistema estadual de regulação, prontuários e censos hospitalares, e-SUS APS, CNES, SAMU, sistema de TFD, P0.

## 7.5 Resultados esperados e indicadores

| Indicador | Linha de base | Meta 12 meses | Meta 36 meses |
|---|---|---|---|
| Fila única eletrônica por especialidade | parcial | 100% das especialidades e exames | manutenção |
| Tempo mediano de espera para consultas prioritárias | desconhecido | medido e publicado | redução de 40% |
| Absenteísmo em consultas e exames regulados | desconhecido (estimado 25% a 30%) | 15% | 10% |
| Leitos de UTI com censo em tempo real | 0 | 100% | 100% |
| Tempo porta-trombólise/porta-balão monitorado | não | sim, nas unidades de referência | metas por linha de cuidado |

## 7.6 Implantação e investimento

Seis a nove meses: censo de leitos e regulação de urgência (3 meses), ambulatorial e exames (3 meses), TFD e aplicativo do paciente (3 meses). Implantação de R$ 1,2 milhão a R$ 1,8 milhão e operação de R$ 150 mil a R$ 220 mil mensais.

## 7.7 Argumento de venda

É o produto de maior impacto político e assistencial: filas visíveis, leitos geridos em tempo real e o paciente informado no celular. A redução do absenteísmo em dez pontos libera o equivalente a milhares de consultas e exames por ano sem contratar um profissional a mais.

# 8. P5 – Linhas de Cuidado em Oncologia e Doenças Crônicas

## 8.1 Problema

As mamografias de rastreamento em mulheres de 50 a 69 anos caíram de 5.424 para 3.929 (razão 0,15 frente à meta 1,0) e os citopatológicos em mulheres de 25 a 64 anos de 18.393 para 10.702 (razão 0,18); o câncer de colo do útero mata tanto quanto o de mama; a produção oncológica dobrou, mas não há monitoramento público do prazo legal de 60 dias para o início do tratamento (Lei 12.732/2012); as internações por AVC mais que dobraram e cerca de 357 pacientes estão em hemodiálise.

## 8.2 Solução

Sistema de gestão de linhas de cuidado com registro longitudinal do paciente (rastreamento, diagnóstico, tratamento, seguimento) para câncer de mama, colo do útero, próstata e colorretal, e para AVC, infarto, diabetes, hipertensão e doença renal crônica: identificação da população-alvo por município e equipe, convocação ativa, navegação de pacientes com alterações, monitoramento dos prazos e integração com o UNACON e o Centro de Radioterapia.

## 8.3 Uso da IA

- Identificação da população elegível e das faltosas por cruzamento de cadastros (e-SUS, SISCAN, SIA) e priorização por risco (idade, histórico, resultado anterior, tempo desde o último exame).
- Convocação automatizada por mensagens com linguagem adaptada e confirmação de agendamento, com escalonamento para agentes comunitários.
- Alertas de prazo: cada caso com laudo alterado gera linha do tempo com os marcos legais e alerta ao navegador e ao regulador antes do vencimento.
- Apoio à leitura: triagem de laudos e imagens por modelos de visão computacional para dupla checagem e priorização (uso como segunda leitura, não substitutiva).
- Estratificação de risco cardiovascular e renal na APS com sugestão de metas terapêuticas e de intervalo de acompanhamento.

## 8.4 Integrações e dados

e-SUS APS, SISCAN, SIA (mamografia, citopatologia, quimioterapia e radioterapia), SIH, SIM, prontuário do UNACON e dos serviços de diálise, P4 (regulação).

## 8.5 Resultados esperados e indicadores

| Indicador | Linha de base | Meta 12 meses | Meta 36 meses |
|---|---|---|---|
| Razão de mamografia de rastreamento (50 a 69 anos) | 0,15 | 0,30 | 0,60 |
| Razão de citopatológico (25 a 64 anos) | 0,18 | 0,35 | 0,70 |
| Casos com tratamento iniciado em até 60 dias | não medido | medido; 70% | 90% |
| Pacientes com AVC com acesso a trombólise na janela | não medido | medido nas unidades de referência | 20% dos elegíveis |
| Pacientes em diálise peritoneal | 52 registros | 80 | 150 |

## 8.6 Implantação e investimento

Quatro a seis meses, com pilotos em Macapá e Santana (70% da população) e expansão aos demais municípios. Implantação de R$ 500 mil a R$ 750 mil e operação de R$ 60 mil a R$ 90 mil mensais.

## 8.7 Argumento de venda

Cada câncer de colo do útero detectado em fase precoce custa uma fração do tratamento avançado e evita uma morte evitável; o sistema entrega metas verificáveis de rastreamento e prazo de tratamento, que são também indicadores do cofinanciamento federal.

# 9. P6 – Rede Materno-Infantil e Apoio à Atenção Primária dos Municípios

## 9.1 Problema

A razão de mortalidade materna do Amapá é de 82,3 por 100 mil nascidos vivos (segunda do país) e a mortalidade infantil de 17,8 por mil (terceira); a sífilis congênita atinge 15,6 por mil nascidos vivos; a cobertura potencial da atenção primária é desigual entre os municípios e os indicadores de pré-natal, vinculação ao parto e seguimento do recém-nascido não são acompanhados em conjunto por Estado e municípios. Os municípios gastam R$ 944 milhões em saúde, com forte dependência de transferências e capacidade técnica limitada.

## 9.2 Solução

Plataforma estadual de apoio à atenção primária e à rede materno-infantil, compartilhada com os 16 municípios: painel de gestantes por risco, vinculação à maternidade, consultas de pré-natal e exames (incluindo testes de sífilis e HIV), puerpério e primeiro ano de vida; monitoramento dos indicadores do cofinanciamento federal por equipe; apoio técnico remoto (telessaúde, matriciamento) e gestão de metas pactuadas na Comissão Intergestores Bipartite.

## 9.3 Uso da IA

- Estratificação de risco gestacional e neonatal com atualização a cada contato, sinalizando gestantes sem pré-natal adequado, sem vinculação ao parto ou com sífilis não tratada, e orientando a busca ativa.
- Previsão de partos por maternidade e mês para dimensionar leitos obstétricos e neonatais e referências regionais.
- Análise automatizada dos óbitos maternos e infantis (revisão de prontuário assistida) para apoiar os comitês de investigação e identificar evitabilidade.
- Assistente dos gestores municipais: leitura dos relatórios do e-SUS e do financiamento federal com recomendações para melhorar indicadores e evitar perda de recursos.

## 9.4 Integrações e dados

e-SUS APS e SISAB, SINASC, SIM, SINAN (sífilis em gestante e congênita, HIV), SIH (partos), CNES (equipes), sistema de regulação (P4), prontuários das maternidades.

## 9.5 Resultados esperados e indicadores

| Indicador | Linha de base | Meta 12 meses | Meta 36 meses |
|---|---|---|---|
| Gestantes com 7 ou mais consultas de pré-natal | série SINASC 2022–2025 | +10 pontos percentuais | +20 pontos percentuais |
| Gestantes vinculadas à maternidade antes do parto | não medido | 70% | 95% |
| Incidência de sífilis congênita | 15,6 por mil | 12 por mil | menos de 8 por mil |
| Óbitos maternos e infantis investigados em 120 dias | parcial | 90% | 100% |
| Municípios com apoio técnico mensal da SESA | não sistemático | 16 | 16 |

## 9.6 Implantação e investimento

Quatro a seis meses, com adesão municipal por termo de cooperação. Implantação de R$ 450 mil a R$ 700 mil e operação de R$ 55 mil a R$ 85 mil mensais, com possibilidade de cofinanciamento municipal proporcional à população e uso de recursos de emendas de atenção primária.

## 9.7 Argumento de venda

Mortalidade materna e infantil são os indicadores mais visíveis de uma gestão de saúde; a plataforma dá ao Estado o papel de coordenador da rede e aos municípios uma ferramenta que também protege o seu financiamento federal.

# 10. P7 – Vigilância em Saúde Preditiva

## 10.1 Problema

A epidemia de dengue de 2024 (10.693 casos prováveis) não foi antecipada; a tuberculose tem incidência de 77 por 100 mil (terceira do país), com abandono de tratamento elevado; a sífilis adquirida, as hepatites, a malária e as leishmanioses mantêm-se em patamares altos; as violências somam 45,2 mortes por 100 mil. A vigilância opera com boletins manuais e notificações digitadas com atraso.

## 10.2 Solução

Sala de situação de vigilância com ingestão contínua do SINAN, do e-SUS, dos laboratórios (GAL) e de fontes externas (clima, mobilidade, buscas na internet), modelos de alerta precoce por município e semana epidemiológica, gestão de casos de tuberculose, hanseníase e sífilis com busca ativa, e geração automatizada de boletins e informes.

## 10.3 Uso da IA

- Nowcasting e previsão de arboviroses e doenças respiratórias com séries históricas, clima e dados de atendimento, gerando alertas com quatro a oito semanas de antecedência.
- Correção do atraso de notificação (nowcasting estatístico) para que o gestor veja o número provável de casos da semana, não só os digitados.
- Risco de abandono de tratamento de tuberculose e hanseníase a partir do histórico de doses e comparecimentos, com priorização da busca ativa.
- Leitura de laudos e fichas em texto livre para classificação e detecção de surtos (agrupamentos espaço-temporais).
- Redação assistida de boletins epidemiológicos, notas técnicas e respostas à imprensa com os dados validados.

## 10.4 Integrações e dados

SINAN, GAL, e-SUS APS, SIM, SIH, SI-PNI (cobertura vacinal), INMET e satélite (clima), CNES, P0.

## 10.5 Resultados esperados e indicadores

| Indicador | Linha de base | Meta 12 meses | Meta 36 meses |
|---|---|---|---|
| Antecedência do alerta de epidemia de dengue | nenhuma | 4 semanas | 8 semanas |
| Abandono de tratamento de tuberculose | série SINAN 2022–2025 | redução de 20% | abaixo de 5% |
| Oportunidade de encerramento das notificações | parcial | 80% no prazo | 95% no prazo |
| Boletins publicados com periodicidade semanal | irregular | 100% | 100% |

## 10.6 Implantação e investimento

Três a cinco meses, iniciando por arboviroses e tuberculose. Implantação de R$ 400 mil a R$ 650 mil e operação de R$ 50 mil a R$ 80 mil mensais.

## 10.7 Argumento de venda

Antecipar uma epidemia em um mês permite mobilizar agentes, insumos e leitos antes do pico; o custo do sistema equivale a uma fração do que uma epidemia de dengue consome em internações e horas extras.

# 11. P8 – Assistência Farmacêutica e Judicialização com IA

## 11.1 Problema

O Estado informa despesa com medicamentos igual a zero no SIOPS desde 2023, embora empenhe R$ 55 a 60 milhões anuais em suporte profilático e terapêutico e mantenha a assistência farmacêutica especializada; não há base pública de estoques, desabastecimento ou demandas judiciais, apontadas nos estudos como lacuna crítica para a transição. A judicialização consome recursos não planejados e exige pareceres técnicos em prazos curtos.

## 11.2 Solução

Sistema de gestão da assistência farmacêutica (programação, aquisição, estoque em rede, dispensação, rastreabilidade) integrado ao Hórus e ao BNAFAR, com módulo de gestão de demandas judiciais e administrativas (triagem, parecer técnico, cumprimento, custo) e painel de desabastecimento e de custo por paciente e por linha de cuidado.

## 11.3 Uso da IA

- Previsão de demanda por item, unidade e mês, considerando sazonalidade, protocolos e demandas judiciais, com sugestão de programação e de ponto de ressuprimento.
- Alerta de ruptura e de vencimento com remanejamento sugerido entre unidades.
- Triagem de demandas judiciais: leitura da petição e dos laudos, identificação do medicamento, verificação de incorporação (CONITEC, RENAME, protocolos) e alternativas disponíveis no SUS, com minuta de parecer técnico para o farmacêutico e o médico.
- Detecção de padrões (prescritores, advogados, fornecedores) e estimativa do impacto orçamentário das decisões, para subsidiar a Procuradoria e a Secretaria de Fazenda.

## 11.4 Integrações e dados

Hórus e BNAFAR, sistema de almoxarifado e compras do Estado, SISMEDEX, prontuários, tribunais (consulta processual), Procuradoria-Geral do Estado, P1 (financeiro).

## 11.5 Resultados esperados e indicadores

| Indicador | Linha de base | Meta 12 meses | Meta 36 meses |
|---|---|---|---|
| Despesa com medicamentos corretamente informada no SIOPS | 0% | 100% | 100% |
| Itens essenciais em ruptura (média mensal) | desconhecido | medido; redução de 30% | abaixo de 5% |
| Prazo médio do parecer técnico em demandas judiciais | desconhecido | 5 dias úteis | 2 dias úteis |
| Gasto com judicialização por paciente | desconhecido | medido e publicado | redução de 20% |

## 11.6 Implantação e investimento

Quatro a seis meses. Implantação de R$ 450 mil a R$ 700 mil e operação de R$ 55 mil a R$ 85 mil mensais.

## 11.7 Argumento de venda

Medicamento parado vence e medicamento em falta vira ação judicial; o sistema dá controle sobre os dois lados e produz, em dias, os pareceres que hoje a secretaria entrega em semanas, com economia direta em compras emergenciais e sequestros judiciais.

# 12. P9 – Força de Trabalho e Escalas com IA

## 12.1 Problema

Pessoal responde por 44% da despesa com saúde (cerca de R$ 1 bilhão por ano), com participação em queda e migração para contratos com terceiros, mas a folha por vínculo, por unidade e por escala não é pública, e o CNES mostra desequilíbrios de médicos e equipes entre a capital e o interior. Sem gestão de escalas e de absenteísmo, o Estado paga horas extras e plantões extraordinários sem saber onde falta e onde sobra.

## 12.2 Solução

Sistema de gestão da força de trabalho em saúde: cadastro único de profissionais (efetivos, temporários, cedidos, terceirizados e residentes) conciliado com o CNES e a folha, escalas eletrônicas por unidade com controle de frequência, dimensionamento por parâmetros assistenciais e produção, gestão de absenteísmo e afastamentos, e painel de custo de pessoal por unidade e serviço.

## 12.3 Uso da IA

- Dimensionamento preditivo: cálculo da necessidade de profissionais por unidade e turno a partir da demanda prevista (P4), da ocupação de leitos e dos parâmetros normativos, com sugestão de realocação.
- Montagem otimizada de escalas respeitando jornada, descanso, competências e preferências, reduzindo horas extras e lacunas de cobertura.
- Previsão de absenteísmo e de afastamentos por unidade, com apoio a programas de saúde do trabalhador.
- Conciliação automática entre CNES, folha e escala real para identificar profissionais cadastrados sem atuação e atuação sem cadastro, e assistente de pareceres de recursos humanos.

## 12.4 Integrações e dados

Folha de pagamento do Estado, CNES, controle de frequência (ponto eletrônico), sistema de recursos humanos, P1 e P2.

## 12.5 Resultados esperados e indicadores

| Indicador | Linha de base | Meta 12 meses | Meta 36 meses |
|---|---|---|---|
| Profissionais com vínculo, lotação e escala conciliados com o CNES | parcial | 100% dos hospitais | 100% da rede |
| Horas extras e plantões extraordinários | não publicado | redução de 15% | redução de 30% |
| Absenteísmo | não medido | medido e publicado | redução de 20% |
| Unidades com custo de pessoal por serviço | 0 | 12 hospitais | toda a rede |

## 12.6 Implantação e investimento

Três a cinco meses, iniciando pelos hospitais estaduais. Implantação de R$ 350 mil a R$ 550 mil e operação de R$ 45 mil a R$ 70 mil mensais.

## 12.7 Argumento de venda

Com R$ 1 bilhão em pessoal, cada ponto percentual de eficiência em horas extras e realocação vale R$ 10 milhões por ano; o sistema também encerra a dúvida recorrente dos órgãos de controle sobre profissionais pagos e não atuantes.

# 13. P10 – Gestão de Contratos Administrativos, Compras e Fornecedores

## 13.1 Problema

A SESA executa cerca de R$ 900 milhões por ano em contratos com terceiros (serviços de terceiros pessoa jurídica, 21% da despesa) e entidades privadas (18,3%), além de obras, equipamentos, medicamentos, insumos, alimentação, limpeza, vigilância, manutenção e locações. Os estudos encontraram obras e aquisições com execução de 18% a 32% da dotação, contratos hospitalares em disputa, passivo com fornecedores desconhecido (R$ 541 milhões empenhados e não liquidados em 2026) e nenhuma base pública que relacione contrato, fiscal, medição, nota fiscal e pagamento. A Lei 14.133/2021 passou a exigir planejamento anual de contratações, estudo técnico preliminar, gestão de riscos, fiscal e gestor designados e publicação no Portal Nacional de Contratações Públicas, obrigações que hoje são cumpridas de forma manual e dispersa.

## 13.2 Solução

Sistema de ciclo de vida das contratações administrativas da saúde, da demanda ao encerramento: plano anual de contratações; elaboração assistida de documentos de formalização da demanda, estudos técnicos preliminares, termos de referência e editais; pesquisa de preços; acompanhamento das licitações e integração com o PNCP e o sistema de compras do Estado; gestão do contrato (vigência, garantias, reajustes, aditivos, apostilamentos, ocorrências, sanções); fiscalização com medições, atestos e conformidade trabalhista de terceirizados; conciliação de notas fiscais e pagamentos com o módulo financeiro; cadastro e risco de fornecedores; e painel de vencimentos, saldos e execução por unidade.

## 13.3 Uso da IA

- Redação assistida de documentos de formalização da demanda, estudos técnicos preliminares, termos de referência, matrizes de risco e minutas de edital a partir de modelos da Advocacia-Geral da União e do Estado, com verificação de requisitos legais e apontamento de lacunas.
- Pesquisa de preços automatizada no PNCP, no Painel de Preços e em contratos anteriores, com detecção de sobrepreço, jogo de planilha e itens fora da curva.
- Leitura de notas fiscais, medições, relatórios de fiscalização e documentos trabalhistas de terceirizados (folha, guias, certidões), com extração estruturada e cruzamento com o contrato e a frequência (integração com P9).
- Pontuação de risco de fornecedores e de contratos (sanções em CEIS, CNEP e CEPIM; capacidade econômica; histórico de atrasos e glosas; concentração; vínculos societários) para priorizar fiscalização e exigir garantias.
- Alertas inteligentes de vencimento, exaurimento de saldo, reajuste devido, prazo de prorrogação, garantias a renovar e prazos de publicação no PNCP.
- Assistente de legislação e jurisprudência (Lei 14.133/2021, decretos estaduais, acórdãos do TCU e do TCE/AP) para fiscais, gestores e pregoeiros, com citação das fontes.

## 13.4 Integrações e dados

Sistema de compras e licitações do Estado, PNCP e Compras.gov.br, Painel de Preços, SICAF, CEIS/CNEP/CEPIM (Portal da Transparência), Receita Federal (CNPJ), sistema contábil (P1), tribunais de contas, P2 (contratos assistenciais), P8 (medicamentos e insumos), P9 (frequência de terceirizados), P4 e unidades (medições de serviços).

## 13.5 Resultados esperados e indicadores

| Indicador | Linha de base | Meta 12 meses | Meta 36 meses |
|---|---|---|---|
| Contratos vigentes com fiscal, gestor, saldo e vigência cadastrados e monitorados | parcial | 100% | 100% |
| Prazo médio de elaboração de termo de referência | desconhecido (semanas) | redução de 50% | redução de 70% |
| Prorrogações e contratações emergenciais | não medido | medido; redução de 30% | redução de 60% |
| Economia em compras por pesquisa de preços e negociação | não medida | 3% do valor licitado | 5% a 8% |
| Notas fiscais conciliadas com medição e contrato antes do pagamento | não medido | 100% nas unidades-piloto | 100% da rede |
| Fornecedores com risco avaliado antes da contratação | 0 | 100% | 100% |

## 13.6 Implantação e investimento

Quatro a seis meses: cadastro da carteira de contratos vigentes e integração com o PNCP (meses 1 e 2), redação assistida e pesquisa de preços (meses 3 e 4), fiscalização, conciliação e risco de fornecedores (meses 5 e 6). Implantação de R$ 500 mil a R$ 800 mil, operação de R$ 60 mil a R$ 90 mil mensais e parcela por resultado de 10% sobre a economia comprovada em compras nos primeiros 24 meses.

## 13.7 Argumento de venda

Sobre R$ 900 milhões anuais contratados, 3% de economia são R$ 27 milhões por ano; a redução de prorrogações emergenciais e o controle de vencimentos eliminam a principal fonte de apontamentos dos tribunais de contas na saúde. O sistema entrega, na posse, a carteira completa de contratos com saldo, vigência e responsável, informação que a transição hoje não tem.

# 14. Arquitetura, segurança e governança de IA

## 14.1 Arquitetura de referência

Camada de integração (conectores, APIs, padrões HL7 FHIR, TISS e arquivos de disseminação do DATASUS), camada de dados (data lake com zonas bruta, tratada e analítica, catálogo e linhagem), camada de modelos (treinamento, versionamento, monitoramento de desempenho e deriva) e camada de aplicações (painéis, fluxos de trabalho, aplicativos e copiloto). Hospedagem em nuvem governamental ou em provedor contratado pelo Estado, com ambientes separados de produção, homologação e desenvolvimento.

## 14.2 Proteção de dados

Dados de saúde são sensíveis (LGPD, art. 11): pseudonimização por padrão, segregação de perfis, registro de acesso, consentimento ou base legal documentada para cada uso, relatório de impacto à proteção de dados e encarregado designado. Modelos de linguagem operam sobre dados agregados ou pseudonimizados; o acesso a dados identificados exige perfil assistencial e justificativa registrada. Nenhum dado do Estado é usado para treinar modelos de terceiros.

## 14.3 Governança de IA

Comitê de IA da SESA com representantes assistenciais, jurídicos, de controle interno e do Conselho Estadual de Saúde; inventário de modelos com finalidade, dados de treinamento, métricas de desempenho por subgrupo (sexo, raça/cor, município) e revisão periódica de viés; explicabilidade das recomendações; humano no circuito em toda decisão com efeito sobre o paciente ou sobre pagamentos; canal de contestação para cidadãos e profissionais.

## 14.4 Transferência de tecnologia e continuidade

Documentação completa, treinamento de equipe estadual, código das integrações e dos modelos específicos entregue ao Estado ao fim do contrato, exportação de dados em formatos abertos e período de transição assistida de seis meses.

# 15. Modelo de contratação

## 15.1 Caminhos previstos na legislação

1. **Licitação pela Lei 14.133/2021**, preferencialmente pregão ou concorrência com critério de técnica e preço para soluções de tecnologia da informação, com estudo técnico preliminar, termo de referência por resultados e exigência de prova de conceito.
2. **Contrato Público para Solução Inovadora (CPSI)**, previsto no Marco Legal das Startups (Lei Complementar 182/2021), para pilotos de até doze meses prorrogáveis, com posterior contrato de fornecimento sem nova licitação, adequado a P7, P5 e P8.
3. **Encomenda tecnológica** (Lei 10.973/2004 e Decreto 9.283/2018) para componentes de IA com risco tecnológico, como os modelos preditivos de vigilância e de regulação.
4. **Adesão a atas de registro de preços** de outros entes para componentes padronizados (infraestrutura de nuvem, licenças de análise de dados).
5. **Parcerias com universidades e institutos** (UNIFAP, Fiocruz, Instituto Evandro Chagas) para validação científica dos modelos e formação de pessoal.

## 15.2 Condições comerciais propostas

- Contratação modular, com P0 como pré-requisito ou entregue junto com o primeiro produto contratado.
- Desconto de 15% a 20% para contratação integrada do portfólio, com cronograma de 12 a 18 meses.
- Parcela variável por resultado em P3 (faturamento adicional) e P10 (economia em compras) e, opcionalmente, em P2 (economia por glosa fundamentada) e P4 (redução de absenteísmo).
- Garantia de nível de serviço: disponibilidade de 99,5%, atendimento a incidentes críticos em quatro horas, atualização dos modelos ao menos trimestral.
- Treinamento inicial de 200 profissionais e educação continuada mensal.

## 15.3 Fontes de financiamento

Recursos próprios do tesouro estadual (as soluções são despesa de ASPS quando vinculadas à gestão do SUS), recursos de emendas parlamentares de estruturação e de saúde digital (R$ 7,1 milhões já empenhados em telessaúde e saúde digital em 2025), programa SUS Digital do Ministério da Saúde, financiamento do BNDES e do BID para transformação digital em saúde, e cofinanciamento municipal em P6.

# 16. Roteiro de implantação

Tabela: Roteiro sugerido de implantação do portfólio, 2027–2028

| Período | Entregas | Produtos |
|---|---|---|
| Primeiros 100 dias (jan–abr 2027) | Sala de situação da transição com dados 2022–2026; painel do FES e do mínimo constitucional; censo eletrônico de leitos; carteira de contratos administrativos e assistenciais e de obras com saldo, vigência e responsável | P0 (onda 1), P1, P2 (início), P10 (carteira), P4 (censo) |
| Meses 4 a 9 (mai–set 2027) | Regulação ambulatorial e de urgência; faturamento assistido nos três maiores hospitais; redação assistida, pesquisa de preços e fiscalização de contratos; vigilância preditiva de arboviroses e tuberculose; linhas de cuidado oncológicas em Macapá e Santana | P4, P3, P10, P7, P5 |
| Meses 10 a 15 (out 2027–mar 2028) | Plataforma materno-infantil com os 16 municípios; assistência farmacêutica e judicialização; força de trabalho nos hospitais; copiloto do gestor em produção | P6, P8, P9, P0 (onda 3) |
| Meses 16 a 24 (abr–dez 2028) | Expansão a toda a rede, parcela por resultado, auditoria externa dos modelos, transferência de tecnologia inicial | Todos |

Fonte: proposta do proponente.

# 17. Riscos e mitigações

| Risco | Mitigação |
|---|---|
| Qualidade e atraso dos dados de origem | Conectores com validação, nowcasting para atraso de notificação, indicadores de qualidade por fonte publicados no painel |
| Resistência de equipes e prestadores | Cogestão com as unidades, ganhos rápidos visíveis (filas, escalas), treinamento e parcela de resultado compartilhada |
| Dependência do fornecedor | Transferência de tecnologia, dados em formatos abertos, código das integrações entregue ao Estado |
| Viés e erro dos modelos | Métricas por subgrupo, humano no circuito, comitê de IA, contestação e auditoria externa |
| Descontinuidade orçamentária | Contratos plurianuais, uso de emendas e programas federais, modularidade que permite pausar produtos sem perder a plataforma |
| Questionamento de órgãos de controle | Estudo técnico preliminar robusto, prova de conceito, termo de referência por resultado e relatórios de impacto |

# 18. Encerramento

Os cinco estudos de transição mostraram um sistema de saúde que gasta muito, depende de recursos temporários, enxerga pouco e decide tarde. As onze soluções deste portfólio atacam exatamente essas quatro fragilidades: tornam o dinheiro legível, o acesso regulado, o cuidado contínuo e a vigilância antecipada, com inteligência artificial a serviço de gestores e profissionais e com resultados mensuráveis a cada bimestre. A proposta é iniciar pela plataforma de dados e pela governança financeira nos primeiros cem dias, quando a transição ainda dispõe de margem política, e evoluir para a regulação e as linhas de cuidado ao longo de 2027.

# APÊNDICE A – Matriz de aderência aos achados dos estudos

| Achado dos estudos de transição | Produto que o enfrenta | Indicador de acompanhamento |
|---|---|---|
| Metade da despesa em Administração Geral; medicamentos zerados no SIOPS | P1, P8 | % da despesa classificada em subfunções finalísticas |
| Investimentos com 22% de execução; R$ 124 milhões em RP | P1 | Liquidado/dotação de capital |
| Esforço próprio em queda (19,4% para 15,3%) | P1 | Alerta de risco do mínimo com dois bimestres |
| Entidades privadas de 4,9% para 18,3% da despesa | P2 | Metas apuradas automaticamente; divergência produção/contrato |
| Faturamento SUS de R$ 216 per capita (18º); 19 de 139 UTI habilitadas | P3 | Valor aprovado per capita; leitos habilitados |
| R$ 25,6 milhões em procedimentos vasculares atípicos | P3 | Casos sinalizados auditados |
| AVC de 464 para 1.147 internações; MVI 45,2/100 mil | P4, P5 | Tempo porta-trombólise; ocupação de leitos |
| Rastreamento 0,15 e 0,18; prazo de 60 dias não monitorado | P5 | Razão de rastreamento; % tratados em 60 dias |
| Mortalidade materna 82,3; infantil 17,8; sífilis congênita 15,6 | P6, P7 | Vinculação ao parto; incidência de sífilis congênita |
| Dengue 10.693 casos; tuberculose 77/100 mil | P7 | Antecedência do alerta; abandono de tratamento |
| Pessoal 44% da despesa sem folha por vínculo | P9 | Conciliação CNES/folha/escala; horas extras |
| R$ 900 milhões anuais em contratos; obras paradas; passivo com fornecedores; prorrogações emergenciais | P10 | Contratos monitorados; economia em compras; notas conciliadas antes do pagamento |
| Informação dispersa e defasada | P0 | Defasagem fato–painel; indicadores automatizados |
