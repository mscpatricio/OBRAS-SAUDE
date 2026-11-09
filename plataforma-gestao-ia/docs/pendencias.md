# Pendências de especificação com a SESA/AP e outros órgãos

| Item | Módulo | O que falta | Responsável sugerido | Enquanto isso |
|---|---|---|---|---|
| Extração do sistema contábil (empenhos, liquidações, pagamentos, dotações, fontes, credores, contas do FES) | P1 | Layout, periodicidade, acesso (views ou arquivos) | SEFAZ/SEPLAN + FES | Adaptador fictício + carga RREO/DCA do SICONFI |
| Folha de pagamento e ponto eletrônico | P9, P1 | Layout por servidor, vínculo, lotação, rubricas agregadas, frequência | SEAD + SESA/RH | Folha sintética |
| SISREG / regulação estadual | P4 | API ou extração de banco; catálogo de procedimentos e unidades | SESA/Regulação + DATASUS | Adaptador fictício |
| Prontuários hospitalares (FHIR) | P3, P4, P5 | Inventário dos sistemas por hospital; endpoints FHIR ou extrações | Diretores de TI dos hospitais | Eventos FHIR sintéticos |
| e-SUS APS / SISAB municipais | P5, P6 | Exportações do PEC de cada município; termos de cooperação | 16 secretarias municipais + CIB | Dados sintéticos |
| Hórus / BNAFAR | P8 | Credenciais dos web services; cadastro de unidades | CAF/SESA + Ministério da Saúde | Adaptador fictício |
| GAL (laboratório) | P7 | Exportação periódica | LACEN | Adaptador fictício |
| SINAN estadual (DBF semanal) | P7 | Rotina de exportação e envio | Vigilância/SESA | Bases nacionais anuais |
| SI-PNI | P6, P7 | Acesso a cobertura por município | Vigilância/SESA | Indisponível |
| Consulta FNS / Transferegov | P1 | API ou RPA autorizada | FES + Ministério da Saúde | SIOPS (receitas declaradas) e CGU (emendas) |
| Sistema de compras e licitações do Estado; acesso ao PNCP como ente; NF-e (SEFAZ) | P10 | Layout de contratos e licitações vigentes; credenciais PNCP; acesso às NF-e destinadas ao Estado | SEPLAN/Compras + SEFAZ + PGE | API pública do PNCP e contratos sintéticos |
| OuvidorSUS (integração), SISAUD/DenaSUS (exportação de auditorias), DigiSUS Gestor (RDQA/RAG) e secretaria executiva do CES/AP (fluxo de pautas e resoluções) | P11 | Credenciais e layouts de integração; regimento do CES; calendário de reuniões | Ouvidoria do SUS, Auditoria do SUS, CES/AP, Ministério da Saúde | Adaptadores fictícios; portal do conselheiro com dados sintéticos |
| Provedor de mensagens (SMS/WhatsApp) | P4, P5, P6 | Contratação e templates aprovados | SESA/Comunicação | Simulador |
| Nuvem governamental / hospedagem | Todos | Definição do ambiente de produção e políticas | PRODAP | Compose/K8s local |
| Bases legais LGPD e encarregado | Todos | RIPD por módulo, portaria do encarregado, comitê de IA | Gabinete + Procuradoria | Documentos-modelo em docs/lgpd |
