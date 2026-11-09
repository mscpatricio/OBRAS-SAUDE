# 01 – Dados e integrações

## Conectores (packages/connectors)

Cada conector implementa `Connector.extract(partition) -> list[Path]` (grava em `raw/<source>/<dataset>/<partition>/`), `Connector.validate()` (Great Expectations) e `Connector.load_trusted()` (DuckDB/dbt). Partição padrão: competência `YYYYMM` ou `exercicio/bimestre`. Reexecução deve ser idempotente (sobrescreve a partição).

| Fonte | Dataset | Acesso | Formato | Periodicidade | Ponto de partida |
|---|---|---|---|---|---|
| DATASUS SIH | RD (AIH reduzida), SP (serviços profissionais), ER (rejeitadas) | FTP `ftp.datasus.gov.br/dissemin/publicos/SIHSUS/200801_/Dados/` | DBC → Parquet (usar `pyreaddbc` ou `read.dbc` via rpy2; preferir biblioteca `pysus`) | mensal | novo |
| DATASUS SIA | PA (produção ambulatorial), AQ/AR (APAC quimio/radio), AM (medicamentos), BI | FTP SIASUS | DBC → Parquet | mensal | novo |
| DATASUS CNES | ST, LT (leitos), PF (profissionais), EQ (equipes), HB (habilitações), SR (serviços) | FTP CNES | DBC → Parquet | mensal | novo |
| DATASUS SIM/SINASC | DO, DN | FTP (preliminar e definitivo) | DBC/CSV | anual + preliminar | novo |
| SINAN | agravos (DENG, TUBE, HANS, SIFC, SIFG, HEPA, MENI, ANIM, IEXO, VIOL, CHIK, ZIKA, LEIV, LTAN, MALA) | FTP SINAN + exportação estadual (DBF) | DBC/DBF | semanal (estadual), anual (nacional) | novo |
| TABNET | tabulações agregadas (validação cruzada) | POST `tabcgi.exe` | PRN | sob demanda | `estudo-saude-ap/scripts/tabnet.py` |
| SIOPS | RREO Anexo 12 estados e municípios; indicadores | POST `rel_LRFUF.php`, `rel_LRF.php`, `consdetalhereenvio2uf.php` | HTML → longo | bimestral | `extract_siops_anexo12.py`, `siops.py` |
| SICONFI | RREO Anexos 01–14, DCA, RGF | API `apidatalake.tesouro.gov.br/ords/siconfi/tt/` | JSON | bimestral/anual | `extract_siconfi.py` |
| CGU | emendas parlamentares (emendas, convênios, favorecidos) | download ZIP | CSV latin1 | mensal | `build_e5.py` (filtro) |
| Transferegov / FNS | repasses fundo a fundo, saldos de emendas | API Transferegov (dados abertos) e consulta FNS (interativa; avaliar RPA) | JSON/CSV | mensal | pendência |
| e-SUS APS / SISAB | cadastros, atendimentos, indicadores do cofinanciamento | exportação do PEC (bases municipais) e relatórios SISAB | CSV/XML | mensal | adaptador fictício + pendência |
| SISREG / regulação estadual | solicitações, agendamentos, filas | API SISREG III (quando disponível) ou extração de banco | JSON/CSV | diário | adaptador fictício |
| Prontuários hospitalares | admissões, altas, censo, prescrições | HL7 FHIR R4 (Encounter, Patient, Condition, Procedure, MedicationRequest) | JSON | tempo quase real | adaptador fictício |
| Sistema contábil do Estado | empenhos, liquidações, pagamentos, dotações, fontes, credores | extração de views ou arquivos; especificar com a SEFAZ | CSV/Parquet | diário | adaptador fictício |
| Folha e RH | servidores, vínculos, lotações, afastamentos, frequência | extração; especificar com a SEAD | CSV | mensal | adaptador fictício |
| Hórus / BNAFAR | estoque, dispensação, programação | web services do Hórus e BNAFAR | XML/JSON | diário | adaptador fictício |
| GAL | exames laboratoriais de vigilância | exportação | CSV | diário | adaptador fictício |
| INMET / satélite | temperatura, chuva, umidade | API INMET | JSON | diário | novo |
| IBGE | população, IPCA, PIB, malhas | API SIDRA e geoftp | JSON/SHP | anual | `build_*.py` |

Adaptador fictício = interface + implementação sintética documentada em `packages/connectors/<fonte>/README.md`, registrada em `docs/pendencias.md` até a SESA fornecer a especificação real.

## Modelo canônico (marts) – dimensões e fatos principais

Dimensões: `dim_facility` (CNES, tipo, gestão, esfera, município, habilitações vigentes), `dim_municipality` (IBGE, região de saúde, população por ano), `dim_procedure` (SIGTAP com histórico), `dim_cid10`, `dim_professional` (`professional_key`, CBO, vínculos), `dim_person` (`person_key`, sexo, data de nascimento, município, raça/cor), `dim_budget_account` (função, subfunção, programa, ação, natureza, fonte), `dim_contract`, `dim_team` (equipes APS), `dim_date`.

Fatos: `fct_hospital_admission` (AIH), `fct_ambulatory_production` (BPA/APAC), `fct_bed_census` (diário), `fct_notification` (SINAN), `fct_death`, `fct_birth`, `fct_budget_execution` (empenho/liquidação/pagamento por dotação, credor, competência), `fct_revenue`, `fct_transfer` (União/Estado), `fct_amendment` (emendas), `fct_contract_target` e `fct_contract_payment`, `fct_regulation_request`, `fct_care_pathway_event`, `fct_prenatal_visit`, `fct_dispensation`, `fct_stock_position`, `fct_lawsuit`, `fct_shift` e `fct_attendance`.

Convenções dbt: `stg_<fonte>__<dataset>` (trusted → staging), `int_<domínio>__<transformação>`, `fct_`/`dim_` em marts, `rpt_` para visões de painel. Testes `not_null`, `unique`, `accepted_values`, `relationships` em toda chave; freshness por fonte.

## Qualidade de dados

- Great Expectations em cada carga trusted: tipos, domínios (CID, SIGTAP, CNES válidos), datas plausíveis, totais conciliados com o TABNET (tolerância 0,5%).
- Painel de qualidade por fonte (completude, atraso, rejeições) exposto em P0.
- Regras de pseudonimização: hash com sal por ambiente de CPF/CNS → `person_key`; nome/endereço nunca saem de `core.identity`.

## Indicadores oficiais a implementar como models dbt (catálogo mínimo)

Pacto interfederativo e Previne/cofinanciamento APS; RREO Anexo 12 (percentual aplicado, por fase); SIOPS 1.1–3.2; cobertura potencial de APS; ICSAP; razão de mamografia e citopatológico; proporção de pré-natal com 7+ consultas; razão de mortalidade materna; TMI; incidência de sífilis congênita, TB, dengue; taxa de ocupação e média de permanência por leito; tempo de espera por fila; valor aprovado SIH/SIA per capita; execução de capital; estoque de restos a pagar. Cada indicador tem ficha em `docs/indicadores/<slug>.md` (definição oficial, fonte, fórmula, periodicidade, limitações).
