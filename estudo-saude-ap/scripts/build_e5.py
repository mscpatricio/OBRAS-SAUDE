# -*- coding: utf-8 -*-
"""Estudo 5 - Financiamento, recursos e gastos em saúde no Amapá (SIOPS, SICONFI, CGU, SIH/SIA, IBGE)."""
import sys, os, json, re, csv, collections
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from lib_estudo import *
import numpy as np
SCR='/tmp/claude-0/-home-user-OBRAS-SAUDE/c712070a-2954-5409-93ab-21cafbd2988b/scratchpad'
RAW=SCR+'/raw'; SC=RAW+'/siconfi/'; SI=RAW+'/siops2/'; EM=SCR+'/dl/emendas/'; T1=RAW+'/tab/'
OUT='/home/user/OBRAS-SAUDE/estudo-saude-ap/estudos-complementares/e5_financiamento'; GR=OUT+'/graficos'
os.makedirs(GR,exist_ok=True)
YRS=[2022,2023,2024,2025,2026]; YRS4=[2022,2023,2024,2025]; YS=[str(y) for y in YRS]
# ---------- população e deflator ----------
pop_uf={}
for r in json.load(open(RAW+'/sidra_pop_uf_all.json'))[1:]: pop_uf.setdefault(r['D1N'],{})[int(r['D3N'])]=int(r['V'])
def popu(uf,y):
    d=pop_uf[uf]; return d.get(y) or d.get(2024)
pop={y:popu('Amapá',y) for y in YRS}
ipca=collections.defaultdict(list)
for r in json.load(open(RAW+'/sidra_ipca_indice.json'))[1:]: ipca[int(r['D3C'][:4])].append(float(r['V']))
IPCA={y:sum(v)/len(v) for y,v in ipca.items()}
def real(v,y,base=2025): return v*IPCA[base]/IPCA[y]
pib={int(r['D3N']):float(r['V'])*1000 for r in json.load(open(RAW+'/../raw/sidra_pib_uf_2022.json'))[1:] if r['D1N']=='Amapá'}
pib_uf={r['D1N']:float(r['V'])*1000 for r in json.load(open(RAW+'/sidra_pib_uf_2022.json'))[1:]}
K={'pop':pop,'ipca':IPCA,'pib_2022':pib_uf['Amapá']}; S={}
MI=1e6
def mi(v): return v/MI
# ---------- SICONFI ----------
def rd(name): return pd.read_csv(SC+name,sep=';',dtype=str).assign(valor=lambda d: d['valor'].astype(float))
r02=rd('rreo02_funcoes.csv'); r01=rd('rreo01_receitas.csv'); r03=rd('rreo03_rcl.csv'); r14=rd('rreo14_simplificado.csv'); dca=rd('dca.csv')
r02['exercicio']=r02['exercicio'].astype(int); r01['exercicio']=r01['exercicio'].astype(int); r03['exercicio']=r03['exercicio'].astype(int); dca['exercicio']=dca['exercicio'].astype(int)
PER26=int(r02[(r02.ente=='Amapá')&(r02.exercicio==2026)]['periodo'].iloc[0]); K['per26']=PER26
C_EMP='DESPESAS EMPENHADAS ATÉ O BIMESTRE (b)'; C_LIQ='DESPESAS LIQUIDADAS ATÉ O BIMESTRE (d)'; C_DI='DOTAÇÃO INICIAL'; C_DA='DOTAÇÃO ATUALIZADA (a)'; C_RP='INSCRITAS EM RESTOS A PAGAR NÃO PROCESSADOS (f)'
def v02(ente,ano,conta,col,cod='RREO2TotalDespesas'):
    d=r02[(r02.ente==ente)&(r02.exercicio==ano)&(r02.conta==conta)&(r02.coluna==col)&(r02.cod_conta==cod)]
    return float(d['valor'].iloc[0]) if len(d) else float('nan')
def v01(ente,ano,cod,col='Até o Bimestre (c)'):
    d=r01[(r01.ente==ente)&(r01.exercicio==ano)&(r01.cod_conta==cod)&(r01.coluna==col)]
    return float(d['valor'].iloc[0]) if len(d) else float('nan')
def rcl(ente,ano):
    d=r03[(r03.ente==ente)&(r03.exercicio==ano)&(r03.conta.str.startswith('RECEITA CORRENTE LÍQUIDA (III)'))&(r03.coluna=='TOTAL (ÚLTIMOS 12 MESES)')]
    return float(d['valor'].iloc[0]) if len(d) else float('nan')
def vdca(ente,ano,conta,col,anexo='DCA-Anexo I-E'):
    d=dca[(dca.ente==ente)&(dca.exercicio==ano)&(dca.anexo==anexo)&(dca.conta==conta)&(dca.coluna==col)]
    return float(d['valor'].iloc[0]) if len(d) else float('nan')
TOT='TOTAL (III) = (I + II)'
# T1 contexto fiscal
t1=pd.DataFrame(index=YS); t1.index.name='Exercício'
t1['Receita corrente líquida (R$ mi)']=[mi(rcl('Amapá',y)) for y in YRS]
t1['Receitas realizadas (R$ mi)']=[mi(v01('Amapá',y,'TotalReceitas')) for y in YRS]
t1['Receita de impostos (R$ mi)']=[mi(v01('Amapá',y,'Impostos')) for y in YRS]
t1['Transferências correntes da União (R$ mi)']=[mi(v01('Amapá',y,'TransferenciasCorrentesDaUniaoEDeSuasEntidades')) for y in YRS]
t1['Despesa total empenhada (R$ mi)']=[mi(v02('Amapá',y,TOT,C_EMP)) for y in YRS]
t1['Despesa total liquidada (R$ mi)']=[mi(v02('Amapá',y,TOT,C_LIQ)) for y in YRS]
t1['População (IBGE)']=[pop[y] for y in YRS]
S['CONTEXTO_FISCAL_AP']=(t1,'Contexto fiscal do Estado do Amapá: receita corrente líquida, receitas realizadas e despesa total, 2022–2026',f'RREO Anexos 01, 02 e 03 (SICONFI). 2026: acumulado até o {PER26}º bimestre.')
K['t1']=t1
# T2 função saúde
t2=pd.DataFrame(index=YS); t2.index.name='Exercício'
t2['Dotação inicial (R$ mi)']=[mi(v02('Amapá',y,'Saúde',C_DI)) for y in YRS]
t2['Dotação atualizada (R$ mi)']=[mi(v02('Amapá',y,'Saúde',C_DA)) for y in YRS]
t2['Empenhada (R$ mi)']=[mi(v02('Amapá',y,'Saúde',C_EMP)) for y in YRS]
t2['Liquidada (R$ mi)']=[mi(v02('Amapá',y,'Saúde',C_LIQ)) for y in YRS]
t2['Paga (R$ mi)']=[mi(vdca('Amapá',y,'10 - Saúde','Despesas Pagas')) if y<2026 else float('nan') for y in YRS]
t2['RP não processados inscritos (R$ mi)']=[mi(v02('Amapá',y,'Saúde',C_RP)) for y in YRS]
t2['Execução (empenhado/dotação atualizada, %)']=t2['Empenhada (R$ mi)']/t2['Dotação atualizada (R$ mi)']*100
t2['Participação no total empenhado (%)']=[v02('Amapá',y,'Saúde',C_EMP)/v02('Amapá',y,TOT,C_EMP)*100 for y in YRS]
t2['% da RCL']=[v02('Amapá',y,'Saúde',C_EMP)/rcl('Amapá',y)*100 for y in YRS]
t2['Empenhada per capita (R$)']=[v02('Amapá',y,'Saúde',C_EMP)/pop[y] for y in YRS]
t2['Empenhada a preços de 2025 (R$ mi)']=[mi(real(v02('Amapá',y,'Saúde',C_EMP),y)) for y in YRS]
S['DESPESA_SAUDE_FUNCAO10_AP']=(t2,'Despesa do Estado do Amapá na função Saúde: dotação, execução, participação e valores per capita, 2022–2026',f'RREO Anexo 02 e DCA Anexo I-E (SICONFI); deflator IPCA (média anual do índice); 2026 parcial ({PER26}º bimestre).')
K['t2']=t2
# T3 subfunções
SUBF=['Atenção Básica','Assistência Hospitalar e Ambulatorial','Suporte Profilático e Terapêutico','Vigilância Sanitária','Vigilância Epidemiológica','Alimentação e Nutrição','FU10 - Administração Geral','FU10 - Demais Subfunções']
t3=pd.DataFrame({str(y):{s.replace('FU10 - ',''):v02('Amapá',y,s,C_EMP) for s in SUBF} for y in YRS}).fillna(0)
t3.loc['Total função Saúde']=[v02('Amapá',y,'Saúde',C_EMP) for y in YRS]
t3.index.name='Subfunção (despesa empenhada, R$)'
t3['Participação 2025 (%)']=t3['2025']/t3.loc['Total função Saúde','2025']*100
S['SAUDE_SUBFUNCAO_AP']=(t3,'Despesa empenhada na função Saúde por subfunção, Estado do Amapá, 2022–2026','RREO Anexo 02 (SICONFI). "Administração Geral" e "Demais Subfunções" referem-se às subfunções 122 e outras lançadas na função 10.')
K['t3']=t3
# T_funcoes 2025 ranking
f25=r02[(r02.ente=='Amapá')&(r02.exercicio==2025)&(r02.coluna==C_EMP)&(r02.cod_conta=='RREO2TotalDespesas')]
funcs={}
for _,x in f25.iterrows():
    c=x['conta']
    if ' - ' in c or c.startswith('FU') or c==TOT or c.startswith('DESPESAS (INTRA') : continue
    funcs[c]=x['valor']
# manter apenas funções (nível 1): as que aparecem na lista oficial
FUNC_NAMES=['Legislativa','Judiciária','Essencial à Justiça','Administração','Defesa Nacional','Segurança Pública','Relações Exteriores','Assistência Social','Previdência Social','Saúde','Trabalho','Educação','Cultura','Direitos da Cidadania','Urbanismo','Habitação','Saneamento','Gestão Ambiental','Ciência e Tecnologia','Agricultura','Organização Agrária','Indústria','Comércio e Serviços','Comunicações','Energia','Transporte','Desporto e Lazer','Encargos Especiais']
tf=pd.DataFrame({'Despesa empenhada 2025 (R$ mi)':{k:mi(v) for k,v in funcs.items() if k in FUNC_NAMES}}).sort_values('Despesa empenhada 2025 (R$ mi)',ascending=False)
tf['Participação (%)']=tf.iloc[:,0]/mi(v02('Amapá',2025,TOT,C_EMP))*100; tf.index.name='Função'
S['FUNCOES_2025_AP']=(tf,'Despesa empenhada do Estado do Amapá por função de governo, 2025','RREO Anexo 02 (SICONFI), 6º bimestre; exclui intraorçamentárias.')
K['tf']=tf
# ---------- SIOPS Anexo 12 ----------
sa=pd.read_csv(SI+'siops_anexo12.csv',sep=';',dtype=str).fillna('')
for k in range(1,13): sa[f'v{k}']=pd.to_numeric(sa[f'v{k}'],errors='coerce')
sa['ano']=sa['ano'].astype(int)
def q(df,secao=None,linha=None,grupo=None,startswith=True):
    d=df
    if secao: d=d[d.secao.str.startswith(secao)]
    if grupo is not None: d=d[d.grupo.str.startswith(grupo)] if grupo else d[d.grupo=='']
    if linha: d=d[d.linha.str.startswith(linha)] if startswith else d[d.linha==linha]
    return d
sa.loc[(sa.esfera=='M')&(sa.municipio=='Amapá'),'municipio']='Amapá (município)'
E=sa[(sa.esfera=='E')]; AP=E[E.uf=='Amapá']; M=sa[sa.esfera=='M']
def val(df,ano,secao,linha,col='v3',grupo=None):
    d=q(df[df.ano==ano],secao,linha,grupo)
    return float(d[col].iloc[0]) if len(d) and pd.notna(d[col].iloc[0]) else float('nan')
SEC_REC='RECEITAS RESULTANTES'; SEC_ASPS='DESPESAS COM AÇÕES'; SEC_AP='APURAÇÃO'; SEC_RP='EXERCÍCIO DO EMPENHO'; SEC_AD='RECEITAS ADICIONAIS'; SEC_NC='DESPESAS COM SAUDE POR SU'; SEC_TOT='DESPESAS TOTAIS'
bim={y:int(AP[AP.ano==y]['bimestre'].iloc[0]) for y in YRS}; K['bim_siops']=bim
# T4 receita base
t4=pd.DataFrame(index=YS); t4.index.name='Exercício'
t4['Receita de impostos (I)']=[mi(val(AP,y,SEC_REC,'RECEITA DE IMPOSTOS (I)')) for y in YRS]
t4['ICMS']=[mi(val(AP,y,SEC_REC,'Receita Resultante do Imposto sobre a Circulação')) for y in YRS]
t4['IRRF']=[mi(val(AP,y,SEC_REC,'Receita Resultante do Imposto sobre a Renda')) for y in YRS]
t4['IPVA']=[mi(val(AP,y,SEC_REC,'Receita Resultante do Imposto sobre a Propriedade de Veículos')) for y in YRS]
t4['ITCD']=[mi(val(AP,y,SEC_REC,'Receita Resultante do Imposto de Transmissão')) for y in YRS]
t4['Transferências constitucionais (II)']=[mi(val(AP,y,SEC_REC,'RECEITA DE TRANSFERÊNCIAS CONSTITUCIONAIS')) for y in YRS]
t4['Cota-parte FPE']=[mi(val(AP,y,SEC_REC,'Cota-Parte FPE')) for y in YRS]
t4['(-) Deduções a municípios (III)']=[mi(val(AP,y,SEC_REC,'DEDUÇÕES DE TRANSFERÊNCIAS')) for y in YRS]
t4['Base de cálculo do mínimo (IV)']=[mi(val(AP,y,SEC_REC,'TOTAL DAS RECEITAS RESULTANTES')) for y in YRS]
t4.columns=[c+' (R$ mi)' for c in t4.columns]
S['SIOPS_RECEITA_BASE_AP']=(t4,'Receitas de impostos e transferências constitucionais que formam a base de cálculo do mínimo em saúde, Estado do Amapá, 2022–2026 (receita realizada)',f'SIOPS, RREO Anexo 12; 2026 até o {bim[2026]}º bimestre.')
K['t4']=t4
# T5 apuração
t5=pd.DataFrame(index=YS); t5.index.name='Exercício'
t5['Base de cálculo (IV) (R$ mi)']=t4['Base de cálculo do mínimo (IV) (R$ mi)']
t5['ASPS empenhadas (R$ mi)']=[mi(val(AP,y,SEC_ASPS,'TOTAL (XII)')) for y in YRS]
t5['ASPS liquidadas (R$ mi)']=[mi(val(AP,y,SEC_ASPS,'TOTAL (XII)','v5')) for y in YRS]
t5['ASPS pagas (R$ mi)']=[mi(val(AP,y,SEC_ASPS,'TOTAL (XII)','v7')) for y in YRS]
t5['Mínimo 15% Constituição Estadual (R$ mi)']=[mi(val(AP,y,SEC_AP,'Despesa Mínima a ser Aplicada em ASPS (XVIII) = (IV) x % (Constituição','v1')) for y in YRS]
t5['Mínimo 12% LC 141 (R$ mi)']=t5['Base de cálculo (IV) (R$ mi)']*0.12
t5['Aplicado acima do mínimo estadual (R$ mi)']=[mi(val(AP,y,SEC_AP,'Diferença entre o Valor Aplicado','v1')) for y in YRS]
t5['% aplicado (empenhado)']=[val(AP,y,SEC_AP,'PERCENTUAL DA RECEITA','v1') for y in YRS]
t5['% aplicado (liquidado)']=[val(AP,y,SEC_AP,'PERCENTUAL DA RECEITA','v2') for y in YRS]
t5['% aplicado (pago)']=[val(AP,y,SEC_AP,'PERCENTUAL DA RECEITA','v3') for y in YRS]
t5['RP não processados inscritos em ASPS (R$ mi)']=[mi(val(AP,y,SEC_ASPS,'TOTAL (XII)','v9')) for y in YRS]
S['SIOPS_ASPS_APURACAO_AP']=(t5,'Apuração do cumprimento do mínimo constitucional em ações e serviços públicos de saúde (ASPS), Estado do Amapá, 2022–2026',f'SIOPS, RREO Anexo 12. O Amapá aplica o mínimo de 15% da Constituição Estadual (superior aos 12% da LC 141/2012). 2026 até o {bim[2026]}º bimestre (acompanhamento pela despesa liquidada).')
K['t5']=t5
# T6 ASPS por subfunção e T9 não computadas e T10 capital
SUBS=['ATENÇÃO BÁSICA','ASSISTÊNCIA HOSPITALAR E AMBULATORIAL','SUPORTE PROFILÁTICO E TERAPÊUTICO','VIGILÂNCIA SANITÁRIA','VIGILÂNCIA EPIDEMIOLÓGICA','ALIMENTAÇÃO E NUTRIÇÃO','OUTRAS SUBFUNÇÕES']
def subtab(sec,col='v3'):
    d=pd.DataFrame({str(y):{s.title():val(AP,y,sec,s,col) for s in SUBS} for y in YRS}).fillna(0); d.index.name='Subfunção'; return d
t6=subtab(SEC_ASPS); t6.loc['Total ASPS']=t5['ASPS empenhadas (R$ mi)'].values*MI
t6b=t6/MI; t6b.columns=[c for c in t6b.columns]; S['SIOPS_ASPS_SUBFUNCAO_AP']=(t6b,'Despesas em ASPS (computadas no mínimo) por subfunção, Estado do Amapá, 2022–2026 (empenhado, R$ milhões)','SIOPS, RREO Anexo 12, seção de despesas com recursos próprios.')
t9=subtab(SEC_NC); t9.loc['Total não computadas']=[val(AP,y,SEC_NC,'TOTAL DAS DESPESAS NÃO COMPUTADAS') for y in YRS]
t9b=t9/MI; S['SIOPS_NAO_COMPUTADAS_SUBFUNCAO_AP']=(t9b,'Despesas com saúde não computadas no mínimo (recursos transferidos e outras fontes) por subfunção, Estado do Amapá, 2022–2026 (empenhado, R$ milhões)','SIOPS, RREO Anexo 12.')
K['t6']=t6b; K['t9']=t9b
# T8 total e fontes
t8=pd.DataFrame(index=YS); t8.index.name='Exercício'
t8['Total despesas com saúde – empenhado (R$ mi)']=[mi(val(AP,y,SEC_TOT,'TOTAL DAS DESPESAS COM SAÚDE')) for y in YRS]
t8['Total – liquidado (R$ mi)']=[mi(val(AP,y,SEC_TOT,'TOTAL DAS DESPESAS COM SAÚDE','v5')) for y in YRS]
t8['Total – pago (R$ mi)']=[mi(val(AP,y,SEC_TOT,'TOTAL DAS DESPESAS COM SAÚDE','v7')) for y in YRS]
t8['Total – RP não processados (R$ mi)']=[mi(val(AP,y,SEC_TOT,'TOTAL DAS DESPESAS COM SAÚDE','v9')) for y in YRS]
def transf_exec(y,col='v3'):
    d=q(AP[AP.ano==y],SEC_TOT); d=d[(d.linha=='3')|(d.linha.str.startswith('(-) Despesas executadas com recursos provenientes'))]
    return float(d[col].iloc[0]) if len(d) else float('nan')
t8['Executado com recursos transferidos de outros entes (R$ mi)']=[mi(transf_exec(y)) for y in YRS]
t8['Executado com recursos próprios (L) (R$ mi)']=[mi(val(AP,y,SEC_TOT,'TOTAL DAS DESPESAS EXECUTADAS COM RECURSOS PRÓPRIOS')) for y in YRS]
t8['Transferências da União para a saúde recebidas (R$ mi)']=[mi(val(AP,y,SEC_AD,'Provenientes da União')) for y in YRS]
t8['Transferências da União previstas (R$ mi)']=[mi(val(AP,y,SEC_AD,'Provenientes da União','v2')) for y in YRS]
t8['Outras receitas vinculadas (R$ mi)']=[mi(val(AP,y,SEC_AD,'OUTRAS RECEITAS')) for y in YRS]
t8['Participação dos recursos transferidos na despesa (%)']=t8.iloc[:,4]/t8.iloc[:,0]*100
t8['Despesa total com saúde per capita (R$)']=[val(AP,y,SEC_TOT,'TOTAL DAS DESPESAS COM SAÚDE')/pop[y] for y in YRS]
t8['Transferências da União per capita (R$)']=[val(AP,y,SEC_AD,'Provenientes da União')/pop[y] for y in YRS]
S['SIOPS_DESPESA_TOTAL_FONTES_AP']=(t8,'Despesa total com saúde do Estado do Amapá por fonte (recursos próprios e transferências) e receitas adicionais para a saúde, 2022–2026','SIOPS, RREO Anexo 12 (seções de receitas adicionais e despesas totais).')
K['t8']=t8
# T10 investimentos (despesas de capital) ASPS + não computadas
def capital(y,col):
    tot=0.0
    for sec in (SEC_ASPS,SEC_NC):
        d=q(AP[AP.ano==y],sec,'Despesas de Capital'); tot+=float(d[col].fillna(0).sum())
    return tot
t10=pd.DataFrame(index=YS); t10.index.name='Exercício'
for lab,col in [('Dotação atualizada','v2'),('Empenhado','v3'),('Liquidado','v5'),('Pago','v7'),('RP não processados inscritos','v9')]:
    t10[lab+' (R$ mi)']=[mi(capital(y,col)) for y in YRS]
t10['Liquidado/dotação atualizada (%)']=t10['Liquidado (R$ mi)']/t10['Dotação atualizada (R$ mi)']*100
t10['Participação do capital na despesa total com saúde (%)']=t10['Empenhado (R$ mi)']/t8.iloc[:,0]*100
cap_aha={y:(val(AP,y,SEC_NC,'ASSISTÊNCIA HOSPITALAR','v2',grupo='ASSISTÊNCIA HOSPITALAR') ) for y in YRS}
def cap_sub(y,sec,sub,col):
    d=q(AP[AP.ano==y],sec,'Despesas de Capital',grupo=sub); return float(d[col].iloc[0]) if len(d) else 0.0
t10['Capital em Assistência Hospitalar com recursos transferidos – empenhado (R$ mi)']=[mi(cap_sub(y,SEC_NC,'ASSISTÊNCIA HOSPITALAR','v3')) for y in YRS]
t10['Idem – liquidado (R$ mi)']=[mi(cap_sub(y,SEC_NC,'ASSISTÊNCIA HOSPITALAR','v5')) for y in YRS]
S['INVESTIMENTOS_CAPITAL_SAUDE_AP']=(t10,'Despesas de capital (investimentos) em saúde do Estado do Amapá: dotação, execução e restos a pagar, 2022–2026','SIOPS, RREO Anexo 12; soma das linhas "Despesas de Capital" das seções de ASPS e de despesas não computadas.')
K['t10']=t10
# T11 restos a pagar ASPS (controle por exercício do empenho) - relatório mais recente (2026 parcial)
rp=q(AP[AP.ano==2026],SEC_RP,'Empenhos de ')
t11=pd.DataFrame({'Exercício do empenho':[l.replace('Empenhos de ','') for l in rp.linha],'Mínimo a aplicar (R$ mi)':mi(rp.v1.values),'Aplicado em ASPS (R$ mi)':mi(rp.v2.values),'Aplicado além do mínimo (R$ mi)':mi(rp.v3.values),'RP inscritos no exercício (R$ mi)':mi(rp.v4.values),'RP pagos (R$ mi)':mi(rp.v7.values),'RP a pagar (R$ mi)':mi(rp.v8.values),'RP cancelados ou prescritos (R$ mi)':mi(rp.v9.values)}).set_index('Exercício do empenho')
t11=t11.loc[[i for i in t11.index if i>='2019']]
S['RESTOS_A_PAGAR_ASPS_AP']=(t11,f'Controle dos restos a pagar de ASPS por exercício do empenho, Estado do Amapá (posição do RREO de 2026, {bim[2026]}º bimestre)','SIOPS, RREO Anexo 12, quadro de controle dos restos a pagar (LC 141/2012, art. 24).')
K['t11']=t11
# T12 indicadores SIOPS AP e benchmark UFs
ind=pd.read_csv('/home/user/OBRAS-SAUDE/estudo-saude-ap/dados/siops/siops_indicadores.csv',sep=';',dtype=str)
IND={'ind_1.1':'1.1 Receita de impostos na receita total (%)','ind_1.2':'1.2 Transferências intergovernamentais na receita total (%)','ind_1.3':'1.3 Transferências SUS no total transferido ao Estado (%)','ind_1.5':'1.5 Transferências SUS da União no total de transferências da União (%)','ind_1.6':'1.6 Receita de impostos e transferências constitucionais na receita total (%)','ind_2.1':'2.1 Despesa total com saúde por habitante (R$)','ind_2.2':'2.2 Despesa com pessoal na despesa com saúde (%)','ind_2.3':'2.3 Despesa com medicamentos (%)','ind_2.4':'2.4 Serviços de terceiros – pessoa jurídica (%)','ind_2.5':'2.5 Investimentos (%)','ind_2.6':'2.6 Instituições privadas sem fins lucrativos (%)','ind_3.1':'3.1 Transferências para a saúde na despesa total com saúde (%)','ind_3.2':'3.2 Receita própria aplicada em ASPS – LC 141/2012 (%)'}
apind=ind[(ind.uf=='Amapá')&(ind.ano.astype(int)>=2022)].copy()
t12=pd.DataFrame({f"{r.ano}{'' if r.bimestre=='6' else ' ('+r.bimestre+'º bim.)'}":{IND[k]:float(r[k]) if r[k] else float('nan') for k in IND} for _,r in apind.iterrows()}); t12.index.name='Indicador SIOPS'
S['SIOPS_INDICADORES_AP']=(t12,'Indicadores SIOPS do Estado do Amapá, 2022–2026','SIOPS, situação de entrega (consdetalhereenvio2uf). Indicadores 2.x calculados pela despesa empenhada.')
K['t12']=t12
def bench_ind(ano):
    d=ind[(ind.ano==str(ano))&(ind.bimestre=='6')].copy()
    b=pd.DataFrame({'Despesa com saúde por habitante (R$)':d.set_index('uf')['ind_2.1'].astype(float),'Pessoal (%)':d.set_index('uf')['ind_2.2'].astype(float),'Serviços de terceiros PJ (%)':d.set_index('uf')['ind_2.4'].astype(float),'Investimentos (%)':d.set_index('uf')['ind_2.5'].astype(float),'Instituições privadas s/ fins lucrativos (%)':d.set_index('uf')['ind_2.6'].astype(float),'Transferências na despesa com saúde (%)':d.set_index('uf')['ind_3.1'].astype(float),'% receita própria aplicada (LC 141)':d.set_index('uf')['ind_3.2'].astype(float)})
    b.index.name='UF'; return b.sort_values('Despesa com saúde por habitante (R$)',ascending=False)
b25=bench_ind(2025); b24=bench_ind(2024)
S['BENCH_UF_SIOPS_INDICADORES_2025']=(b25,'Indicadores SIOPS dos estados, 2025 (6º bimestre)','SIOPS. Per capita calculado pelo SIOPS com a população de referência do sistema.')
S['BENCH_UF_SIOPS_INDICADORES_2024']=(b24,'Indicadores SIOPS dos estados, 2024 (6º bimestre)','SIOPS.')
K['b25']=b25; K['b24']=b24
# T14 benchmark RREO + Anexo 12 por UF
def bench_rreo(ano):
    rows={}
    for uf in pop_uf:
        if uf=='Brasil' or uf not in set(r02.ente): continue
        sau=v02(uf,ano,'Saúde',C_EMP); tot=v02(uf,ano,TOT,C_EMP); p=popu(uf,ano)
        e=E[(E.uf==uf)&(E.ano==ano)]
        pct=val(e,ano,SEC_AP,'PERCENTUAL DA RECEITA','v1'); tr=val(e,ano,SEC_AD,'Provenientes da União'); tds=val(e,ano,SEC_TOT,'TOTAL DAS DESPESAS COM SAÚDE'); asps=val(e,ano,SEC_ASPS,'TOTAL (X'); base=val(e,ano,SEC_REC,'TOTAL DAS RECEITAS RESULTANTES')
        rows[uf]={'Função Saúde empenhada (R$ mi)':mi(sau),'Participação da saúde na despesa total (%)':sau/tot*100,'Função Saúde per capita (R$)':sau/p,'Despesa total com saúde – Anexo 12 (R$ mi)':mi(tds),'Despesa total com saúde per capita (R$)':tds/p,'ASPS com recursos próprios per capita (R$)':asps/p,'Transferências da União para a saúde per capita (R$)':tr/p,'Transferências da União na despesa com saúde (%)':tr/tds*100,'% aplicado em ASPS':pct,'Base de cálculo per capita (R$)':base/p}
    b=pd.DataFrame(rows).T; b.index.name='UF'; return b.sort_values('Função Saúde per capita (R$)',ascending=False)
bb25=bench_rreo(2025); bb24=bench_rreo(2024)
S['BENCH_UF_DESPESA_SAUDE_2025']=(bb25,'Despesa com saúde dos estados: função Saúde (RREO Anexo 02) e Anexo 12 (SIOPS), 2025','SICONFI e SIOPS; população IBGE (estimativas 2025). Per capita pela população total do estado, inclusive a atendida pelos municípios.')
S['BENCH_UF_DESPESA_SAUDE_2024']=(bb24,'Despesa com saúde dos estados: função Saúde (RREO Anexo 02) e Anexo 12 (SIOPS), 2024','SICONFI e SIOPS; população IBGE 2024.')
K['bb25']=bb25; K['bb24']=bb24
# T15 municípios DCA
dca.loc[(dca.cod_ibge=='1600105'),'ente']='Amapá (município)'
muns=[m for m in dca[dca.cod_ibge!='16'].ente.unique()]
t15=pd.DataFrame({str(y):{m:vdca(m,y,'10 - Saúde','Despesas Empenhadas') for m in muns} for y in YRS4}); t15.index.name='Município'
popm={(m,y):float(dca[(dca.ente==m)&(dca.exercicio==y)]['populacao'].iloc[0]) for m in muns for y in YRS4 if len(dca[(dca.ente==m)&(dca.exercicio==y)])}
psid={}
for r_ in json.load(open(RAW+'/sidra_pop_mun.json'))[1:]:
    nm=r_['D1N'].replace(' - AP',''); nm='Amapá (município)' if nm=='Amapá' else nm; psid.setdefault(nm,{})[int(r_['D3N'])]=int(r_['V'])
for m in list(psid):
    for y in YRS4+[2026]:
        if (m,y) not in popm: popm[(m,y)]=psid[m].get(y) or psid[m].get(2024) or psid[m].get(2021)
t15['Per capita 2025 (R$)']=[t15.loc[m,'2025']/popm.get((m,2025),popm.get((m,2024),float('nan'))) for m in muns]
t15['Per capita 2022 (R$)']=[t15.loc[m,'2022']/popm.get((m,2022),float('nan')) for m in muns]
t15['Variação 2022–2025 (%)']=(t15['2025']/t15['2022']-1)*100
t15=t15.sort_values('2025',ascending=False)
t15.loc['Total municípios']=list(t15[[str(y) for y in YRS4]].sum())+[float('nan')]*3
for y in YRS4: t15[str(y)]=t15[str(y)]/MI
t15=t15.rename(columns={str(y):f'{y} (R$ mi)' for y in YRS4})
S['MUNICIPIOS_DESPESA_SAUDE_DCA']=(t15,'Despesa empenhada na função Saúde pelos municípios do Amapá, 2022–2025 (DCA)','SICONFI, DCA Anexo I-E; população de referência do SICONFI.')
K['t15']=t15; K['popm']=popm
# T16 municípios SIOPS
def mun_tab(ano):
    rows={}
    for cod,g in M[M.ano==ano].groupby('cod_mun'):
        m=g.municipio.iloc[0]; b=int(g.bimestre.iloc[0])
        pct=val(g,ano,SEC_AP,'PERCENTUAL DA RECEITA','v1'); base=val(g,ano,SEC_REC,'TOTAL DAS RECEITAS RESULTANTES'); asps=val(g,ano,SEC_ASPS,'TOTAL ('); tr=val(g,ano,SEC_AD,'Provenientes da União'); tre=val(g,ano,SEC_AD,'Provenientes dos Estados'); tds=val(g,ano,SEC_TOT,'TOTAL DAS DESPESAS COM SAÚDE'); ab=val(g,ano,SEC_TOT,'ATENÇÃO BÁSICA')
        p=popm.get((m,min(ano,2025)),popm.get((m,2024),float('nan')))
        rows[m]={'Bimestre':b,'Base de cálculo (R$ mi)':mi(base),'ASPS recursos próprios (R$ mi)':mi(asps),'% aplicado em ASPS (mín. 15%)':pct,'Transferências da União (R$ mi)':mi(tr),'Transferências do Estado (R$ mi)':mi(tre),'Despesa total com saúde (R$ mi)':mi(tds),'Despesa total per capita (R$)':(tds/p if p else float('nan')),'Transferências da União na despesa (%)':(tr/tds*100 if tds else float('nan')),'Atenção básica na despesa total (%)':(ab/tds*100 if tds else float('nan'))}
    d=pd.DataFrame(rows).T; d.index.name='Município'; return d.sort_values('Despesa total per capita (R$)',ascending=False)
m25=mun_tab(2025); m24=mun_tab(2024); m26=mun_tab(2026)
S['MUNICIPIOS_SIOPS_ANEXO12_2025']=(m25,'Financiamento da saúde nos municípios do Amapá, 2025 (RREO Anexo 12/SIOPS)','SIOPS; população do SICONFI. Mínimo municipal: 15% (LC 141/2012).')
S['MUNICIPIOS_SIOPS_ANEXO12_2024']=(m24,'Financiamento da saúde nos municípios do Amapá, 2024 (RREO Anexo 12/SIOPS)','SIOPS.')
S['MUNICIPIOS_SIOPS_ANEXO12_2026_parcial']=(m26,'Financiamento da saúde nos municípios do Amapá, 2026 (parcial, último bimestre homologado)','SIOPS; bimestre indicado por município; % aplicado pela despesa liquidada.')
K['m25']=m25; K['m24']=m24; K['m26']=m26
t17=pd.DataFrame({str(y):{g.municipio.iloc[0]:val(g,y,SEC_AP,'PERCENTUAL DA RECEITA','v1') for _,g in M[M.ano==y].groupby('cod_mun')} for y in YRS}); t17.index.name='Município'
t17.columns=[c if c!='2026' else '2026 (parcial)' for c in t17.columns]
S['MUNICIPIOS_PCT_APLICADO_SERIE']=(t17.sort_values('2025',ascending=False),'Percentual da receita própria aplicado em ASPS pelos municípios do Amapá, 2022–2026','SIOPS, RREO Anexo 12 (empenhado; 2026 liquidado parcial).')
K['t17']=t17
# T18 consolidado estado + municípios
t18=pd.DataFrame(index=[str(y) for y in YRS4]); t18.index.name='Exercício'
t18['Estado – despesa total com saúde (R$ mi)']=[t8.iloc[i,0] for i in range(4)]
t18['Municípios – despesa total com saúde (R$ mi)']=[mi(sum(val(g,y,SEC_TOT,'TOTAL DAS DESPESAS COM SAÚDE') for _,g in M[M.ano==y].groupby('cod_mun'))) for y in YRS4]
t18['Municípios – transferências recebidas do Estado (R$ mi)']=[mi(sum(val(g,y,SEC_AD,'Provenientes dos Estados') for _,g in M[M.ano==y].groupby('cod_mun'))) for y in YRS4]
t18['Gasto público estadual+municipal (R$ mi)']=t18.iloc[:,0]+t18.iloc[:,1]-t18.iloc[:,2]
t18['Gasto público estadual+municipal per capita (R$)']=[t18.iloc[i,3]*MI/pop[y] for i,y in enumerate(YRS4)]
t18['Transferências da União recebidas (Estado+municípios) (R$ mi)']=[t8.iloc[i,6]+mi(sum(val(g,y,SEC_AD,'Provenientes da União') for _,g in M[M.ano==y].groupby('cod_mun'))) for i,y in enumerate(YRS4)]
t18['Participação da União (%)']=t18.iloc[:,5]/t18.iloc[:,3]*100
t18['Gasto estadual+municipal / PIB 2022 (%)']=[t18.iloc[i,3]*MI/pib_uf['Amapá']*100 if y==2022 else float('nan') for i,y in enumerate(YRS4)]
S['GASTO_PUBLICO_CONSOLIDADO_AP']=(t18,'Gasto público em saúde no Amapá: Estado e municípios, 2022–2025','SIOPS, RREO Anexo 12 do Estado e dos 16 municípios; exclui a despesa executada diretamente pela União (hospital universitário, SESAI). Deduzidas as transferências do Estado aos municípios para evitar dupla contagem.')
K['t18']=t18
# ---------- SIH/SIA valores aprovados ----------
def L1(n): return load(T1+n+'.csv')
sihf=L1('sih_financ_ano_valor'); siaf=L1('sia_financ_ano_valor'); sihc=L1('sih_complex_ano_valor'); siac=L1('sia_complex_ano_valor'); sihg=L1('sih_gestao_ano_valor'); siag=L1('sia_gestao_ano_valor')
def row(df,pref):
    r=[i for i in df.index if i.startswith(pref)]; return df.loc[r[0]] if r else None
t19=pd.DataFrame(index=YS); t19.index.name='Ano de processamento'
t19['SIH – MAC (R$ mi)']=[mi(row(sihf,'06')[y]) for y in YS]; t19['SIH – FAEC (R$ mi)']=[mi(row(sihf,'04')[y]) for y in YS]; t19['SIH – total (R$ mi)']=[mi(sihf.loc['Total',y]) for y in YS]
t19['SIA – MAC (R$ mi)']=[mi(row(siaf,'06')[y]) for y in YS]; t19['SIA – FAEC (R$ mi)']=[mi(row(siaf,'04')[y]) for y in YS]; t19['SIA – assistência farmacêutica (R$ mi)']=[mi(row(siaf,'02')[y]) for y in YS]; t19['SIA – total (R$ mi)']=[mi(siaf.loc['Total',y]) for y in YS]
t19['SIH+SIA (R$ mi)']=t19['SIH – total (R$ mi)']+t19['SIA – total (R$ mi)']
t19['SIH+SIA per capita (R$)']=[t19.loc[str(y),'SIH+SIA (R$ mi)']*MI/pop[y] for y in YRS]
t19['Transferências da União ao Estado – Anexo 12 (R$ mi)']=t8['Transferências da União para a saúde recebidas (R$ mi)'].values
S['SIH_SIA_VALORES_APROVADOS_AP']=(t19,'Valor aprovado da produção hospitalar (SIH) e ambulatorial (SIA) no Amapá por tipo de financiamento, 2022–2026 (R$ milhões)','SIH/SUS e SIA/SUS (TABNET, por local de atendimento); 2026 parcial. O valor aprovado é a referência de produção faturada e não coincide com o repasse financeiro (MAC é repassado por teto).')
K['t19']=t19
bsih=L1('bench_sih_uf_ano_valor'); bsia=L1('bench_sia_uf_ano_valor')
def ufn(s): return re.sub(r'^\d\d ','',s)
t20=pd.DataFrame({'SIH 2024 (R$ mi)':{ufn(i):mi(bsih.loc[i,'2024']) for i in bsih.index if i!='Total'},'SIA 2024 (R$ mi)':{ufn(i):mi(bsia.loc[i,'2024']) for i in bsia.index if i!='Total'}})
t20['SIH+SIA 2024 (R$ mi)']=t20.sum(axis=1); t20['SIH+SIA per capita 2024 (R$)']=[t20.loc[u,'SIH+SIA 2024 (R$ mi)']*MI/popu(u,2024) for u in t20.index]
t20['SIH per capita (R$)']=[t20.loc[u,'SIH 2024 (R$ mi)']*MI/popu(u,2024) for u in t20.index]; t20['SIA per capita (R$)']=[t20.loc[u,'SIA 2024 (R$ mi)']*MI/popu(u,2024) for u in t20.index]
t20.loc['BRASIL']=[mi(bsih.loc['Total','2024']),mi(bsia.loc['Total','2024']),mi(bsih.loc['Total','2024']+bsia.loc['Total','2024']),(bsih.loc['Total','2024']+bsia.loc['Total','2024'])/popu('Brasil',2024),bsih.loc['Total','2024']/popu('Brasil',2024),bsia.loc['Total','2024']/popu('Brasil',2024)]
t20.index.name='UF'; t20=t20.sort_values('SIH+SIA per capita 2024 (R$)',ascending=False)
S['BENCH_UF_SIH_SIA_2024']=(t20,'Valor aprovado SIH+SIA por UF de atendimento e per capita, 2024','SIH/SUS e SIA/SUS (TABNET); população IBGE 2024.')
K['t20']=t20
# ---------- Emendas parlamentares (CGU) ----------
csv.field_size_limit(10**8)
UFMAP={unaccent(u).upper():u for u in pop_uf}
def fnum(s): return float(s.replace('.','').replace(',','.')) if s else 0.0
em_all=[]; uf_year=collections.defaultdict(float); uf_tot=collections.defaultdict(float)
with open(EM+'EmendasParlamentares.csv',encoding='latin1',newline='') as f:
    for row_ in csv.DictReader(f,delimiter=';'):
        if row_['Código Função']!='10': continue
        y=int(row_['Ano da Emenda'])
        if y<2022: continue
        ufn_=row_['UF']
        if ufn_ not in ('Sem informação','Múltiplo','MÚLTIPLO',''):
            un=UFMAP.get(unaccent(ufn_).upper(),ufn_.title()); uf_year[(un,y)]+=fnum(row_['Valor Empenhado']); uf_tot[un]+=fnum(row_['Valor Empenhado'])
        if ufn_=='AMAPÁ' or row_['Localidade de aplicação do recurso'].endswith('- AP'): em_all.append(row_)
em=pd.DataFrame(em_all)
for c in ['Valor Empenhado','Valor Liquidado','Valor Pago','Valor Restos A Pagar Inscritos','Valor Restos A Pagar Cancelados','Valor Restos A Pagar Pagos']: em[c]=em[c].map(fnum)
em['Ano']=em['Ano da Emenda'].astype(int)
t21=em.groupby('Ano').agg(**{'Nº de emendas (linhas)':('Código da Emenda','count'),'Empenhado (R$ mi)':('Valor Empenhado',lambda s: s.sum()/MI),'Liquidado (R$ mi)':('Valor Liquidado',lambda s: s.sum()/MI),'Pago (R$ mi)':('Valor Pago',lambda s: s.sum()/MI),'RP inscritos (R$ mi)':('Valor Restos A Pagar Inscritos',lambda s: s.sum()/MI),'RP pagos (R$ mi)':('Valor Restos A Pagar Pagos',lambda s: s.sum()/MI),'RP cancelados (R$ mi)':('Valor Restos A Pagar Cancelados',lambda s: s.sum()/MI)})
t21.index=t21.index.astype(str); t21.index.name='Ano da emenda'
t21['Empenhado per capita (R$)']=[t21.loc[str(y),'Empenhado (R$ mi)']*MI/pop[y] for y in t21.index.astype(int)]
t21.loc['Total 2022–2026']=list(t21.sum()[:-1])+[float('nan')]
S['EMENDAS_SAUDE_AP_ANO']=(t21,'Emendas parlamentares federais na função Saúde destinadas ao Amapá, por ano da emenda, 2022–2026','Portal da Transparência/CGU (base Emendas Parlamentares, extração de 7 nov. 2026). Valores de execução acumulados até a data de extração.')
K['t21']=t21
def piv(col,top=None):
    p=em.pivot_table(index=col,columns='Ano',values='Valor Empenhado',aggfunc='sum',fill_value=0)/MI; p['Total']=p.sum(axis=1); p=p.sort_values('Total',ascending=False)
    if top: p=p.head(top)
    p.columns=[str(c)+' (R$ mi)' for c in p.columns]; return p
t22=piv('Tipo de Emenda'); t22.index.name='Tipo de emenda'; S['EMENDAS_TIPO_ANO']=(t22,'Emendas parlamentares em saúde para o Amapá por tipo e ano (empenhado, R$ milhões)','CGU.')
t23=piv('Nome Subfunção'); t23.index.name='Subfunção'; S['EMENDAS_SUBFUNCAO_ANO']=(t23,'Emendas parlamentares em saúde para o Amapá por subfunção e ano (empenhado, R$ milhões)','CGU.')
em['Localidade']=em['Localidade de aplicação do recurso'].str.replace(' - AP','',regex=False).str.title().str.replace(' Do ',' do ').str.replace(' De ',' de ').str.replace(' Da ',' da ').replace({'Amapá (Uf)':'Amapá (UF – aplicação estadual)','Múltiplo':'Múltiplo (vários municípios)'})
t24=piv('Localidade'); t24.index.name='Localidade de aplicação'; S['EMENDAS_LOCALIDADE_ANO']=(t24,'Emendas parlamentares em saúde para o Amapá por localidade de aplicação e ano (empenhado, R$ milhões)','CGU.')
t25=piv('Nome do Autor da Emenda',top=15); t25.index.name='Autor'; S['EMENDAS_AUTOR']=(t25,'Emendas parlamentares em saúde para o Amapá por autor, 2022–2026 (empenhado, R$ milhões; 15 maiores)','CGU.')
em['Ação']=em['Nome Ação'].str.title()
t26=piv('Ação',top=12); t26.index.name='Ação orçamentária'; S['EMENDAS_ACAO']=(t26,'Emendas parlamentares em saúde para o Amapá por ação orçamentária, 2022–2026 (empenhado, R$ milhões; 12 maiores)','CGU.')
K['t22']=t22; K['t23']=t23; K['t24']=t24; K['t25']=t25; K['t26']=t26
codes=set(em['Código da Emenda'])
fav=collections.defaultdict(float); favnat={}; favuf=collections.defaultdict(float)
with open(EM+'EmendasParlamentares_PorFavorecido.csv',encoding='latin1',newline='') as f:
    for row_ in csv.DictReader(f,delimiter=';'):
        if row_['Código da Emenda'] in codes:
            k=(row_['Favorecido'],row_['Natureza Jurídica'],row_['UF Favorecido']); fav[k]+=fnum(row_['Valor Recebido'])
t27=pd.DataFrame([{'Favorecido':k[0].title(),'Natureza jurídica':k[1],'UF':k[2],'Valor recebido (R$ mi)':v/MI} for k,v in fav.items()]).sort_values('Valor recebido (R$ mi)',ascending=False)
t27['Participação (%)']=t27['Valor recebido (R$ mi)']/t27['Valor recebido (R$ mi)'].sum()*100
K['fav_total']=t27['Valor recebido (R$ mi)'].sum(); K['fav_n']=len(t27)
t27=t27.head(20).set_index('Favorecido'); S['EMENDAS_FAVORECIDOS']=(t27,'Favorecidos finais dos pagamentos de emendas parlamentares em saúde destinadas ao Amapá (emendas 2022–2026; 20 maiores)','CGU, base "Emendas Parlamentares – por favorecido"; pagamentos acumulados até a extração.')
K['t27']=t27
conv=[]
with open(EM+'EmendasParlamentares_Convenios.csv',encoding='latin1',newline='') as f:
    for row_ in csv.DictReader(f,delimiter=';'):
        if row_['Código da Emenda'] in codes: conv.append(row_)
if conv:
    t28=pd.DataFrame(conv)[['Código da Emenda','Convenente','Objeto Convênio','Número Convênio','Data Publicação Convênio','Valor Convênio']]; t28['Valor Convênio']=t28['Valor Convênio'].map(fnum)/MI; t28=t28.rename(columns={'Valor Convênio':'Valor (R$ mi)'}).set_index('Código da Emenda'); S['EMENDAS_CONVENIOS']=(t28,'Convênios vinculados a emendas parlamentares em saúde destinadas ao Amapá, 2022–2026','CGU.'); K['t28']=t28
t29=pd.DataFrame({'Empenhado 2025 (R$ mi)':{u:uf_year.get((u,2025),0)/MI for u in pop_uf if u!='Brasil'},'Empenhado 2022–2026 (R$ mi)':{u:uf_tot.get(u,0)/MI for u in pop_uf if u!='Brasil'}})
t29['Per capita 2025 (R$)']=[t29.loc[u,'Empenhado 2025 (R$ mi)']*MI/popu(u,2025) for u in t29.index]; t29['Per capita 2022–2026 (R$)']=[t29.loc[u,'Empenhado 2022–2026 (R$ mi)']*MI/popu(u,2025) for u in t29.index]
t29.index.name='UF'; t29=t29.sort_values('Per capita 2022–2026 (R$)',ascending=False)
S['BENCH_UF_EMENDAS_SAUDE']=(t29,'Emendas parlamentares federais em saúde por UF de aplicação: valores empenhados e per capita, 2022–2026','CGU; população IBGE 2025. Exclui emendas sem UF definida ("Sem informação"/"Múltiplo" nacional).')
K['t29']=t29
# ---------- gráficos ----------
def grouped(x,series,path,ylabel='',fmt=fmt_int,figsize=(9,4.2)):
    fig,ax=plt.subplots(figsize=figsize); n=len(series); w=0.8/n; xs=np.arange(len(x))
    for i,((k,v),col) in enumerate(zip(series.items(),C)):
        ax.bar(xs+i*w-(n-1)*w/2,v,width=w,color=col,label=k)
    ax.set_xticks(xs); ax.set_xticklabels(x); style(ax,ylabel); ax.legend(frameon=False,fontsize=9); ax.yaxis.set_major_formatter(FuncFormatter(lambda v,p: fmt(v)))
    save(fig,path)
fx=lambda v: fmt_br(v,0)
grouped(YS,{'Empenhado (nominal)':t2['Empenhada (R$ mi)'].values,'Empenhado a preços de 2025':t2['Empenhada a preços de 2025 (R$ mi)'].values},GR+'/f01_despesa_saude_nominal_real.png','R$ milhões',fmt=fx)
lines(YS,{'Participação da saúde na despesa total (%)':t2['Participação no total empenhado (%)'].values,'Despesa com saúde em % da RCL':t2['% da RCL'].values},GR+'/f02_participacao_rcl.png','%',fmt=lambda v: fmt_br(v,0))
parts={'Assistência hospitalar e ambulatorial':t3.loc['Assistência Hospitalar e Ambulatorial',YS].values/MI,'Administração geral (subfunção 122)':t3.loc['Administração Geral',YS].values/MI,'Suporte profilático e terapêutico':t3.loc['Suporte Profilático e Terapêutico',YS].values/MI,'Vigilâncias e atenção básica':(t3.loc['Vigilância Sanitária',YS].values+t3.loc['Vigilância Epidemiológica',YS].values+t3.loc['Atenção Básica',YS].values)/MI,'Demais subfunções':t3.loc['Demais Subfunções',YS].values/MI}
stacked(YS,parts,GR+'/f03_subfuncoes.png','R$ milhões',loc='upper left')
pct_plot=list(t5['% aplicado (empenhado)'].values[:4])+[t5['% aplicado (liquidado)'].values[4]]; K['pct_plot']=pct_plot
fig,ax=plt.subplots(figsize=(9,4.2)); ax.bar(YS[:4]+['2026*'],pct_plot,color=[C[0]]*4+[C[4]],width=0.7); ax.axhline(15,color=C[1],lw=2,ls='--',label='Mínimo estadual (15%)'); ax.axhline(12,color=C[3],lw=1.5,ls=':',label='Mínimo LC 141/2012 (12%)'); ax.legend(frameon=False,fontsize=9,loc='upper left',ncol=2)
for i,v in enumerate(pct_plot): ax.annotate(fmt_br(v,2)+'%',(i,v),ha='center',va='bottom',fontsize=9,color=INK2,xytext=(0,3),textcoords='offset points')
style(ax,'% da receita de impostos e transferências'); ax.set_ylim(0,24); save(fig,GR+'/f04_pct_aplicado_asps.png')
stacked(YS,{'Recursos próprios (ASPS)':t8['Executado com recursos próprios (L) (R$ mi)'].values,'Recursos transferidos de outros entes':t8['Executado com recursos transferidos de outros entes (R$ mi)'].values},GR+'/f05_fontes.png','R$ milhões (empenhado)',loc='upper left')
yrs12=[c for c in t12.columns]
lines(yrs12,{'Pessoal':t12.loc[IND['ind_2.2']].values,'Serviços de terceiros – PJ':t12.loc[IND['ind_2.4']].values,'Instituições privadas sem fins lucrativos':t12.loc[IND['ind_2.6']].values,'Investimentos':t12.loc[IND['ind_2.5']].values,'Transferências na despesa total':t12.loc[IND['ind_3.1']].values},GR+'/f06_composicao_siops.png','% da despesa total com saúde',fmt=lambda v: fmt_br(v,0),legend_cols=2)
grouped(YS,{'Dotação atualizada':t10['Dotação atualizada (R$ mi)'].values,'Empenhado':t10['Empenhado (R$ mi)'].values,'Liquidado':t10['Liquidado (R$ mi)'].values},GR+'/f07_investimentos.png','R$ milhões (despesas de capital)',fmt=fx)
b=bb25.sort_values('Despesa total com saúde per capita (R$)'); hbars(list(b.index),list(b['Despesa total com saúde per capita (R$)']),GR+'/f08_bench_percapita_uf.png','R$ por habitante, 2025',highlight=['Amapá'],fmt=fx,figsize=(9,7))
b=bb25.dropna(subset=['% aplicado em ASPS']).sort_values('% aplicado em ASPS'); hbars(list(b.index),list(b['% aplicado em ASPS']),GR+'/f09_bench_pct_aplicado_uf.png','% da receita de impostos e transferências aplicado em ASPS, 2025',highlight=['Amapá'],fmt=lambda v: fmt_br(v,1),figsize=(9,7))
b=m25.sort_values('Despesa total per capita (R$)'); hbars(list(b.index),list(b['Despesa total per capita (R$)']),GR+'/f10_municipios_percapita.png','R$ por habitante, 2025 (Estado não incluído)',highlight=['Macapá','Santana'],fmt=fx,figsize=(9,5.6))
stacked([str(y) for y in t22.columns[:-1].str.replace(' (R$ mi)','',regex=False)],{i:t22.loc[i].values[:-1] for i in t22.index},GR+'/f12_emendas_tipo_ano.png','R$ milhões (empenhado)',loc='upper left')
stacked(YS,{'SIH (hospitalar)':t19['SIH – total (R$ mi)'].values,'SIA (ambulatorial)':t19['SIA – total (R$ mi)'].values},GR+'/f13_sih_sia_valores.png','R$ milhões (valor aprovado)',loc='upper left')
b=t29.head(27).sort_values('Per capita 2022–2026 (R$)'); hbars(list(b.index),list(b['Per capita 2022–2026 (R$)']),GR+'/f11_bench_emendas_uf.png','R$ por habitante (emendas em saúde empenhadas 2022–2026)',highlight=['Amapá'],fmt=fx,figsize=(9,7))
# ---------- planilha ----------
FONTES=[('SICONFI – Tesouro Transparente (API)','https://apidatalake.tesouro.gov.br/ords/siconfi/tt/rreo e /dca','RREO Anexos 01, 02, 03, 06 e 14 (Estado do Amapá 2022–2026 e 27 UFs 2024–2025) e DCA Anexo I-E (Estado e 16 municípios, 2022–2025).'),('SIOPS – Demonstrativo da LRF (RREO Anexo 12)','http://siops.datasus.gov.br/rel_LRFUF.php e rel_LRF.php','Estado do Amapá 2022–2026, 27 UFs 2024–2025, 16 municípios 2022–2026; dados homologados/transmitidos.'),('SIOPS – indicadores','http://siops.datasus.gov.br/consdetalhereenvio2uf.php','Indicadores 1.1 a 3.2, Amapá 2015–2026 e UFs 2024–2025.'),('Portal da Transparência/CGU – Emendas parlamentares','https://portaldatransparencia.gov.br/download-de-dados/emendas-parlamentares','Base completa (emendas, convênios e favorecidos) filtrada para função 10 e Amapá.'),('SIH/SUS e SIA/SUS (TABNET)','http://tabnet.datasus.gov.br','Valor aprovado por ano de processamento, financiamento, complexidade e UF.'),('IBGE','https://apisidra.ibge.gov.br (tabelas 6579, 1737, 5938)','População, IPCA (número-índice) e PIB estadual 2022.')]
write_workbook(OUT+'/Tabelas_Financiamento_Saude_Amapa_2022_2026.xlsx',S,'Financiamento, recursos e gastos em saúde no Estado do Amapá, 2022–2026','Estudo complementar para a transição de governo 2026/2027 – tabelas de apoio',FONTES)
# ---------- dump para redação ----------
def md(df,d=1,maxrows=40):
    df=df.copy().head(maxrows)
    cols=[str(c) for c in df.columns]; out=['| '+str(df.index.name or '')+' | '+' | '.join(cols)+' |','|'+'---|'*(len(cols)+1)]
    for i,r in df.iterrows():
        cells=[]
        for v in r.values:
            if isinstance(v,(int,float,np.floating,np.integer)):
                cells.append('–' if (isinstance(v,float) and np.isnan(v)) else (fmt_int(v) if abs(v)>=1000 else fmt_br(float(v),d)))
            else: cells.append(str(v))
        out.append('| '+str(i)+' | '+' | '.join(cells)+' |')
    return '\n'.join(out)
with open(SCR+'/dump_e5.txt','w') as f:
    for name,(df,title,note) in S.items():
        f.write(f'\n\n### {name}\n{title}\n{note}\n'); f.write(md(df))
    f.write('\n\nKPIs extra: '+json.dumps({k:(v if not hasattr(v,'to_dict') else None) for k,v in K.items() if k in ('pop','ipca','pib_2022','per26','bim_siops','fav_total','fav_n')},ensure_ascii=False,default=str))
print('OK sheets',len(S))
