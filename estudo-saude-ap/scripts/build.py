# -*- coding: utf-8 -*-
"""Consolida os dados extraídos (TABNET/DATASUS, SIOPS, IBGE) em planilha, gráficos e KPIs."""
import csv, json, os, re, glob, math
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

RAW='/tmp/claude-0/-home-user-OBRAS-SAUDE/c712070a-2954-5409-93ab-21cafbd2988b/scratchpad/raw'
TAB=RAW+'/tab'
OUT='/home/user/OBRAS-SAUDE/estudo-saude-ap'
GR=OUT+'/graficos'
os.makedirs(GR,exist_ok=True)

# ---------- paleta (dataviz reference palette) ----------
C=['#2a78d6','#eb6834','#1baf7a','#eda100','#e87ba4','#008300','#6250d6','#e34948']
INK='#0b0b0b'; INK2='#52514e'; MUTED='#898781'; GRID='#e1e0d9'; SURF='#fcfcfb'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.edgecolor':'#c3c2b7','axes.labelcolor':INK2,
    'xtick.color':INK2,'ytick.color':INK2,'axes.spines.top':False,'axes.spines.right':False,'figure.facecolor':SURF,'axes.facecolor':SURF})

def num(x):
    if x is None: return float('nan')
    s=str(x).strip()
    if s in ('-','','...'): return 0.0
    s=s.replace('.','').replace(',','.')
    try: return float(s)
    except: return float('nan')

def load(name, index=True):
    p=f'{TAB}/{name}.csv'
    if not os.path.exists(p): return None
    rows=list(csv.reader(open(p,encoding='utf-8'),delimiter=';'))
    hdr=rows[0]; body=[]
    for r in rows[1:]:
        if len(r)>len(hdr): k=len(r)-len(hdr); r=[';'.join(r[:k+1])]+r[k+1:]
        if len(r)<len(hdr): r=r+['']*(len(hdr)-len(r))
        body.append(r)
    df=pd.DataFrame(body,columns=hdr)
    for c in hdr[1:]: df[c]=df[c].map(num)
    df=df.set_index(hdr[0]) if index else df
    return df

def fmt_int(v): return f'{int(round(v)):,}'.replace(',','.')
def fmt_br(v,d=1): 
    s=f'{v:,.{d}f}'; return s.replace(',','X').replace('.',',').replace('X','.')
def mi(v): return fmt_br(v/1e6,1)

KPI={}
sheets={}  # name -> (df, title, note)

# ---------- população ----------
pop_uf={}
for r in json.load(open(RAW+'/sidra_pop_uf_all.json'))[1:]:
    pop_uf.setdefault(r['D1N'],{})[int(r['D3N'])]=int(r['V'])
pop_ap=pop_uf['Amapá']; pop_br=pop_uf['Brasil']
pop_mun=[]
for r in json.load(open(RAW+'/sidra_pop_mun.json'))[1:]:
    pop_mun.append((r['D1N'].replace(' - AP',''),int(r['D3N']),int(r['V'])))
dfpm=pd.DataFrame(pop_mun,columns=['Município','Ano','População']).pivot(index='Município',columns='Ano',values='População')
dfpm.loc['Amapá (UF)']=[pop_ap.get(a) for a in dfpm.columns]
sheets['POP_Municipios']=(dfpm,'População residente estimada por município (IBGE, SIDRA tabela 6579)','2021: estimativa pré-Censo; 2024/2025: estimativas pós-Censo 2022.')
dfpuf=pd.DataFrame(pop_uf).T; dfpuf.index.name='UF'
sheets['POP_UF']=(dfpuf,'População residente estimada por UF e Brasil (IBGE, SIDRA 6579)','')
KPI['pop_ap_2025']=pop_ap[2025]; KPI['pop_ap_2024']=pop_ap[2024]; KPI['pop_ap_2021']=pop_ap[2021]

# ---------- SIH ----------
sih=load('sih_ano'); sheets['SIH_01_Ano']=(sih,'Internações SUS no Amapá por ano de processamento (SIH/SUS, local de internação)','2026 = janeiro a agosto (parcial). Valor em R$ correntes.')
for y in range(2018,2027):
    r=sih.loc[str(y)]; KPI[f'sih_aih_{y}']=r['AIH aprovadas']; KPI[f'sih_valor_{y}']=r['Valor total']; KPI[f'sih_obitos_{y}']=r['Óbitos']; KPI[f'sih_tm_{y}']=r['Taxa mortalidade']; KPI[f'sih_mp_{y}']=r['Média permanência']
KPI['sih_aih_var_2019_2025']=(sih.loc['2025','AIH aprovadas']/sih.loc['2019','AIH aprovadas']-1)*100
KPI['sih_valor_var_2019_2025']=(sih.loc['2025','Valor total']/sih.loc['2019','Valor total']-1)*100
KPI['sih_valor_medio_2019']=sih.loc['2019','Valor total']/sih.loc['2019','AIH aprovadas']
KPI['sih_valor_medio_2025']=sih.loc['2025','Valor total']/sih.loc['2025','AIH aprovadas']
KPI['sih_aih_por_100hab_2025']=sih.loc['2025','AIH aprovadas']/pop_ap[2025]*100
KPI['sih_aih_por_100hab_2024']=sih.loc['2024','AIH aprovadas']/pop_ap[2024]*100
sihm=load('sih_anomes'); sheets['SIH_02_AnoMes']=(sihm,'Internações por mês de processamento 2022-2026 (SIH/SUS)','')
for n,t in [('sih_estab_ano_aih','AIH aprovadas por estabelecimento e ano'),('sih_estab_ano_valor','Valor total (R$) por estabelecimento e ano'),('sih_estab_ano_obitos','Óbitos hospitalares por estabelecimento e ano'),('sih_estab_2025','Produção hospitalar por estabelecimento, 2025'),('sih_estab_2026','Produção hospitalar por estabelecimento, jan-ago/2026'),('sih_estab_carater_2025','AIH por estabelecimento e caráter de atendimento, 2025'),('sih_estab_complex_2025','AIH por estabelecimento e complexidade, 2025'),('sih_mun_ano_aih','AIH por município de internação e ano'),('sih_mun_ano_valor','Valor (R$) por município de internação e ano'),('sih_cir_mun_2025','AIH e valor por Região de Saúde/município de internação, 2025'),('sihres_cir_mun_2025','AIH e valor por Região de Saúde/município de RESIDÊNCIA, 2025'),('sihres_mun_ano_aih','AIH por município de residência e ano (inclui internações fora do AP)'),('sih_carater_ano','AIH por caráter de atendimento e ano'),('sih_gestao_ano_aih','AIH por gestão e ano'),('sih_gestao_ano_valor','Valor (R$) por gestão e ano'),('sih_esfera_ano_aih','AIH por esfera jurídica do prestador e ano'),('sih_esfera_ano_valor','Valor (R$) por esfera jurídica do prestador e ano'),('sih_regime_ano_aih','AIH por regime e ano'),('sih_natureza_ano_valor','Valor (R$) por natureza do prestador e ano'),('sih_complex_ano_aih','AIH por complexidade e ano'),('sih_complex_ano_valor','Valor (R$) por complexidade e ano'),('sih_grupo_ano_aih','AIH por grupo de procedimento e ano'),('sih_grupo_ano_valor','Valor (R$) por grupo de procedimento e ano'),('sih_subgrupo_2025','Produção por subgrupo de procedimento, 2025'),('sih_proc_2025','Produção por procedimento (todos), 2025'),('sih_financ_ano_valor','Valor (R$) por tipo de financiamento (MAC/FAEC) e ano')]:
    d=load(n)
    if d is not None: sheets['SIH_'+n.replace('sih_','').replace('sihres_','RES_')]=(d,t+' (SIH/SUS, Amapá)','2026 parcial (jan-ago).')
est=load('sih_estab_2025')
KPI['sih_estab_top']=est.drop('Total').sort_values('AIH aprovadas',ascending=False)[['AIH aprovadas','Valor total','Média permanência','Óbitos','Taxa mortalidade']]
car=load('sih_carater_ano'); KPI['sih_eletivo_2019']=car.loc['Eletivo','2019']; KPI['sih_eletivo_2025']=car.loc['Eletivo','2025']; KPI['sih_urg_2025']=car.loc['Urgência','2025']
esf=load('sih_esfera_ano_valor'); KPI['sih_valor_filantropico_2025']=esf.loc['Entidades sem Fins Lucrativos','2025']; KPI['sih_valor_estadual_2025']=esf.loc['.. Estadual ou Distrito Federal','2025']; KPI['sih_valor_hu_2025']=esf.loc['.. Empresa Pública ou Sociedade de Economia Mista','2025']
fin=load('sih_financ_ano_valor'); KPI['sih_faec_2025']=fin.loc['04 Fundo de Ações Estratégicas e Compensações FAEC','2025']; KPI['sih_faec_2026']=fin.loc['04 Fundo de Ações Estratégicas e Compensações FAEC','2026']; KPI['sih_mac_2025']=fin.loc['06 Média e Alta Complexidade (MAC)','2025']
cx=load('sih_complex_ano_aih'); KPI['sih_alta_2025']=cx.loc['Alta complexidade','2025']; KPI['sih_alta_pct_2025']=cx.loc['Alta complexidade','2025']/cx.loc['Total','2025']*100
# Residência x internação (evasão/importação)
resuf=load('bench_sihres_uf_ano_aih'); intuf=load('bench_sih_uf_ano_aih')
resv=load('bench_sihres_uf_ano_valor'); intv=load('bench_sih_uf_ano_valor')
ev=pd.DataFrame({'AIH de residentes do AP (onde quer que internados)':resuf.loc['16 Amapá'],'AIH realizadas em hospitais do AP':intuf.loc['16 Amapá'],'Valor AIH residentes AP (R$)':resv.loc['16 Amapá'],'Valor AIH realizadas no AP (R$)':intv.loc['16 Amapá']})
ev.index.name='Ano'; ev['Saldo AIH (realizadas no AP - residentes)']=ev.iloc[:,1]-ev.iloc[:,0]; ev['Saldo valor (R$)']=ev.iloc[:,3]-ev.iloc[:,2]
sheets['SIH_Residencia_x_Local']=(ev.drop('Total',errors='ignore'),'Internações de residentes do Amapá vs internações realizadas no Amapá (SIH/SUS)','Saldo negativo de valor indica que residentes do AP consomem internações fora do estado (TFD interestadual) de maior valor médio.')
KPI['ev_saldo_aih_2025']=ev.loc['2025','Saldo AIH (realizadas no AP - residentes)']; KPI['ev_saldo_valor_2025']=ev.loc['2025','Saldo valor (R$)']
KPI['ev_res_2025']=ev.iloc[:,0]['2025']; KPI['ev_int_2025']=ev.iloc[:,1]['2025']; KPI['ev_resval_2025']=ev.iloc[:,2]['2025']; KPI['ev_intval_2025']=ev.iloc[:,3]['2025']
# Morbidade
for n,t in [('nih_cap_ano','Internações por capítulo CID-10 e ano'),('nih_cap_2025','Internações, valor, permanência e óbitos por capítulo CID-10, 2025'),('nih_cap_2026','Internações por capítulo CID-10, jan-ago/2026'),('nih_cap_ano_obitos','Óbitos hospitalares por capítulo CID-10 e ano'),('nih_lista_2025','Internações por Lista de Morbidade CID-10, 2025'),('nih_fxet_ano','Internações por faixa etária e ano'),('nih_sexo_ano','Internações por sexo e ano'),('nih_cap_fxet_2025','Internações por capítulo CID-10 e faixa etária, 2025'),('nih_estab_cap_2025','Internações por estabelecimento e capítulo CID-10, 2025'),('nih_cap_mun_2025','Internações por município de internação e capítulo CID-10, 2025')]:
    d=load(n)
    if d is not None: sheets['MORB_'+n.replace('nih_','')]=(d,t+' (SIH/SUS - Morbidade hospitalar, Amapá)','')
cap=load('nih_cap_ano'); KPI['cap_circ_2022']=cap.loc['IX.  Doenças do aparelho circulatório','2022']; KPI['cap_circ_2023']=cap.loc['IX.  Doenças do aparelho circulatório','2023']; KPI['cap_circ_2025']=cap.loc['IX.  Doenças do aparelho circulatório','2025']
KPI['cap_grav_2025']=cap.loc['XV.  Gravidez parto e puerpério','2025']; KPI['cap_resp_2025']=cap.loc['X.   Doenças do aparelho respiratório','2025']; KPI['cap_inf_2025']=cap.loc['I.   Algumas doenças infecciosas e parasitárias','2025']; KPI['cap_ext_2025']=cap.loc['XIX. Lesões enven e alg out conseq causas externas','2025']; KPI['cap_dig_2025']=cap.loc['XI.  Doenças do aparelho digestivo','2025']
proc=load('sih_proc_2025'); 
KPI['tromb_aih_2025']=proc.loc['0406020590 TROMBECTOMIA DO SISTEMA VENOSO','AIH aprovadas']; KPI['tromb_val_2025']=proc.loc['0406020590 TROMBECTOMIA DO SISTEMA VENOSO','Valor total']
KPI['pneumo_aih_2025']=proc.loc['0303140151 TRATAMENTO DE PNEUMONIAS OU INFLUENZA (GRIPE)','AIH aprovadas']; KPI['pneumo_ob_2025']=proc.loc['0303140151 TRATAMENTO DE PNEUMONIAS OU INFLUENZA (GRIPE)','Óbitos']
KPI['parto_normal_2025']=proc.loc['0310010039 PARTO NORMAL','AIH aprovadas']; KPI['cesaria_2025']=proc.loc['0411010034 OPERACAO CESARIANA','AIH aprovadas']+proc.loc['0411010042 OPERACAO CESARIANA COM LAQUEADURA TUBARIA','AIH aprovadas']
fx=load('nih_fxet_ano'); KPI['fx_menor1_2025']=fx.loc['Menor 1 ano','2025']; KPI['fx_1a4_2025']=fx.loc['1 a 4 anos','2025']

# ---------- SIA ----------
sia=load('sia_ano'); sheets['SIA_01_Ano']=(sia,'Produção ambulatorial SUS no Amapá por ano de processamento (SIA/SUS, local de atendimento)','2026 = jan-ago (parcial). Valor em R$ correntes.')
for y in range(2018,2027):
    KPI[f'sia_qtd_{y}']=sia.loc[str(y),'Qtd.aprovada']; KPI[f'sia_val_{y}']=sia.loc[str(y),'Valor aprovado']
KPI['sia_val_var_2019_2025']=(sia.loc['2025','Valor aprovado']/sia.loc['2019','Valor aprovado']-1)*100
KPI['sia_qtd_var_2019_2025']=(sia.loc['2025','Qtd.aprovada']/sia.loc['2019','Qtd.aprovada']-1)*100
KPI['sia_val_por_hab_2025']=sia.loc['2025','Valor aprovado']/pop_ap[2025]
for n,t in [('sia_anomes','Produção ambulatorial por mês 2022-2026'),('sia_grupo_ano_qtd','Quantidade aprovada por grupo de procedimento e ano'),('sia_grupo_ano_valor','Valor aprovado (R$) por grupo e ano'),('sia_subgrupo_2025','Quantidade e valor por subgrupo, 2025'),('sia_subgrupo_2026','Quantidade e valor por subgrupo, jan-ago/2026'),('sia_subgrupo_ano_valor','Valor aprovado (R$) por subgrupo e ano'),('sia_complex_ano_qtd','Quantidade por complexidade e ano'),('sia_complex_ano_valor','Valor (R$) por complexidade e ano'),('sia_gestao_ano_qtd','Quantidade por gestão e ano'),('sia_gestao_ano_valor','Valor (R$) por gestão e ano'),('sia_financ_ano_valor','Valor (R$) por tipo de financiamento e ano'),('sia_doc_ano_valor','Valor (R$) por instrumento de registro (BPA-C, BPA-I, APAC) e ano'),('sia_carater_ano_qtd','Quantidade por caráter de atendimento e ano'),('sia_mun_ano_qtd','Quantidade por município de atendimento e ano'),('sia_mun_ano_valor','Valor (R$) por município de atendimento e ano'),('sia_cir_mun_2025','Quantidade e valor por Região de Saúde/município, 2025'),('sia_cir_ano_valor','Valor (R$) por Região de Saúde e ano'),('sia_grupo_mun_2025_valor','Valor (R$) por município e grupo de procedimento, 2025'),('sia_forma_2025','Quantidade e valor por forma de organização, 2025'),('sia_proc_2025','Quantidade e valor por procedimento (todos), 2025'),('sia_cbo_2025','Quantidade e valor por CBO do profissional executante, 2025')]:
    d=load(n)
    if d is not None: sheets['SIA_'+n.replace('sia_','')]=(d,t+' (SIA/SUS, Amapá)','2026 parcial (jan-ago).')
sub=load('sia_subgrupo_ano_valor')
KPI['angio_2019']=sub.loc['0309 Terapias especializadas','2019']; KPI['angio_2023']=sub.loc['0309 Terapias especializadas','2023']; KPI['angio_2025']=sub.loc['0309 Terapias especializadas','2025']; KPI['angio_2026']=sub.loc['0309 Terapias especializadas','2026']
KPI['nefro_2025']=sub.loc['0305 Tratamento em nefrologia','2025']; KPI['onco_2025']=sub.loc['0304 Tratamento em oncologia','2025']; KPI['tfd_2025']=sub.loc['0803 Autorizacao / Regulacao','2025']; KPI['consultas_2025']=sub.loc['0301 Consultas / Atendimentos / Acompanhamentos','2025']; KPI['lab_2025']=sub.loc['0202 Diagnostico em laboratorio clinico','2025']; KPI['tomo_2025']=sub.loc['0206 Diagnostico por tomografia','2025']; KPI['oftalmo_2021']=sub.loc['0405 Cirurgia do aparelho da visao','2021']; KPI['oftalmo_2025']=sub.loc['0405 Cirurgia do aparelho da visao','2025']
sp=load('sia_proc_2025'); KPI['escler_qtd_2025']=sp.loc['0309070015 TRATAMENTO ESCLEROSANTE NAO ESTETICO DE VARIZES DOS MEMBROS INFERIORES (UNILATERAL)','Qtd.aprovada']; KPI['escler_val_2025']=sp.loc['0309070015 TRATAMENTO ESCLEROSANTE NAO ESTETICO DE VARIZES DOS MEMBROS INFERIORES (UNILATERAL)','Valor aprovado']
KPI['hemod_sessoes_2025']=sp.loc['0305010107 HEMODIALISE (MAXIMO 3 SESSOES POR SEMANA)','Qtd.aprovada']
cbo=load('sia_cbo_2025'); KPI['cbo_vasc_2025']=cbo.loc['225203 Medico em cirurgia vascular','Valor aprovado']; KPI['cbo_vasc_pct']=KPI['cbo_vasc_2025']/cbo.loc['Total','Valor aprovado']*100
gest=load('sia_gestao_ano_valor'); KPI['sia_estado_2025']=gest.loc['Estado Pleno','2025']; KPI['sia_pacto_2025']=gest.loc['Pacto de Gestão','2025']
smun=load('sia_mun_ano_valor'); KPI['sia_macapa_pct_2025']=smun.loc['160030 MACAPA','2025']/smun.loc['Total','2025']*100
hmun=load('sih_mun_ano_aih'); KPI['sih_macapa_pct_2025']=hmun.loc['160030 MACAPA','2025']/hmun.loc['Total','2025']*100
cxs=load('sia_complex_ano_valor'); KPI['sia_alta_2025']=cxs.loc['Alta complexidade','2025']; KPI['sia_media_2025']=cxs.loc['Média complexidade','2025']
sfin=load('sia_financ_ano_valor'); KPI['sia_faec_2025']=sfin.loc['04 Fundo de Ações Estratégicas e Compensações FAEC','2025']; KPI['sia_mac_2025']=sfin.loc['06 Média e Alta Complexidade (MAC)','2025']

# ---------- CNES ----------
for n,t in [('cnes_leitos_esp_ano','Leitos de internação existentes por especialidade (dez. de cada ano; set/2026)'),('cnes_leitos_esp_ano_sus','Leitos de internação SUS por especialidade (dez. de cada ano; set/2026)'),('cnes_leitos_mun_latest','Leitos existentes/SUS/não SUS por município, set/2026'),('cnes_leitos_mun_esp_latest','Leitos SUS por município e especialidade, set/2026'),('cnes_leitos_esfjur_latest','Leitos por esfera jurídica do estabelecimento, set/2026'),('cnes_leitos_esp_esfjur_latest','Leitos SUS por especialidade e esfera jurídica, set/2026'),('cnes_leitos_tipoestab_latest','Leitos por tipo de estabelecimento, set/2026'),('cnes_leitos_espdet_latest','Leitos por especialidade detalhada, set/2026'),('cnes_uti_tipo_ano','Leitos complementares (UTI/UCI/isolamento) existentes por tipo e ano'),('cnes_uti_tipo_ano_sus','Leitos complementares SUS por tipo e ano'),('cnes_uti_mun_latest','Leitos complementares SUS por município e tipo, set/2026'),('cnes_uti_esfjur_latest','Leitos complementares existentes por tipo e esfera jurídica, set/2026'),('cnes_estab_tipo_ano','Estabelecimentos por tipo e ano'),('cnes_estab_tipo_esfjur_latest','Estabelecimentos por tipo e esfera jurídica, set/2026'),('cnes_estab_gestao_latest','Estabelecimentos por tipo e gestão (estadual/municipal), set/2026'),('cnes_estab_mun_tipo_latest','Estabelecimentos por município e tipo, set/2026'),('cnes_equip_sel_latest','Equipamentos selecionados: existentes, em uso e estabelecimentos com equipamento SUS, set/2026'),('cnes_equip_sel_esfjur_latest','Equipamentos selecionados em uso por esfera jurídica, set/2026'),('cnes_equip_grupo_ano','Equipamentos em uso por grupo e ano'),('cnes_prof_medicos_ano','Médicos (indivíduos) por especialidade e ano'),('cnes_prof_medicos_latest','Médicos (indivíduos) por especialidade e atendimento ao SUS, set/2026'),('cnes_prof_medicos_mun_latest','Médicos (indivíduos) por município e especialidade, set/2026'),('cnes_prof_sup_ano','Profissionais de nível superior (indivíduos) por ocupação e ano'),('cnes_prof_sup_latest','Profissionais de nível superior por ocupação e atendimento ao SUS, set/2026'),('cnes_prof_sup_esfjur_latest','Profissionais de nível superior por ocupação e esfera jurídica, set/2026'),('cnes_prof_tec_latest','Profissionais de nível técnico/auxiliar por ocupação e atendimento ao SUS, set/2026'),('cnes_prof_geral_ano','Profissionais (indivíduos) em geral por ocupação e ano')]:
    d=load(n)
    if d is not None: sheets['CNES_'+n.replace('cnes_','')]=(d,t+' (CNES, Amapá)','Indivíduos podem ter mais de um vínculo; contagem por indivíduo. Competência set/2026 = última disponível.')
le=load('cnes_leitos_esp_ano'); ls=load('cnes_leitos_esp_ano_sus')
KPI['leitos_exist_2026']=le.loc['Total','2026/Set']; KPI['leitos_sus_2026']=ls.loc['Total','2026/Set']; KPI['leitos_sus_2019']=ls.loc['Total','2019/Dez']; KPI['leitos_sus_2024']=ls.loc['Total','2024/Dez']
KPI['leitos_sus_por_1000_2026']=KPI['leitos_sus_2026']/pop_ap[2026]*1000
uti=load('cnes_uti_tipo_ano'); KPI['uti_adulto_2019']=uti.loc['UTI adulto I','2019/Dez']+uti.loc['UTI adulto II','2019/Dez']; KPI['uti_adulto_2026']=uti.loc['UTI adulto II','2026/Set']+uti.loc['UTI adulto III','2026/Set']; KPI['uti_ped_2026']=uti.loc['UTI pediátrica II','2026/Set']; KPI['uti_neo_2026']=uti.loc['UTI neonatal II','2026/Set']
utis=load('cnes_uti_tipo_ano_sus'); KPI['uti_adulto_sus_2026']=utis.loc['UTI adulto II','2026/Set']; KPI['uti_ped_sus_2026']=utis.loc['UTI pediátrica II','2026/Set']; KPI['uti_neo_sus_2026']=utis.loc['UTI neonatal II','2026/Set']
lm=load('cnes_leitos_mun_latest'); KPI['leitos_macapa_sus']=lm.loc['160030 MACAPA','Qtd SUS']; KPI['leitos_santana_sus']=lm.loc['160060 SANTANA','Qtd SUS']
med=load('cnes_prof_medicos_ano'); KPI['medicos_2015']=med.loc['Total','2015/Dez']; KPI['medicos_2019']=med.loc['Total','2019/Dez']; KPI['medicos_2026']=med.loc['Total','2026/Set']
KPI['medicos_por_1000_2026']=KPI['medicos_2026']/pop_ap[2026]*1000
mm=load('cnes_prof_medicos_mun_latest'); KPI['medicos_macapa']=mm.loc['160030 MACAPA','Total']; KPI['medicos_macapa_pct']=KPI['medicos_macapa']/mm.loc['Total','Total']*100
ps=load('cnes_prof_sup_ano'); KPI['enf_2019']=ps.loc['Enfermeiro','2019/Dez']; KPI['enf_2026']=ps.loc['Enfermeiro','2026/Set']
pg=load('cnes_prof_geral_ano'); KPI['prof_total_2019']=pg.loc['Total','2019/Dez']; KPI['prof_total_2026']=pg.loc['Total','2026/Set']
pe=load('cnes_prof_sup_esfjur_latest'); KPI['prof_sup_estadual']=pe.loc['Total','Administração Pública Estadual ou Distrito Federal']; KPI['prof_sup_total']=pe.loc['Total','Total']
et=load('cnes_estab_tipo_ano'); KPI['hosp_geral_2026']=et.loc['HOSPITAL GERAL','2026/Set']; KPI['hosp_esp_2026']=et.loc['HOSPITAL ESPECIALIZADO','2026/Set']; KPI['ubs_2026']=et.loc['CENTRO DE SAUDE/UNIDADE BASICA','2026/Set']; KPI['estab_2026']=et.loc['Total','2026/Set']
eq=load('cnes_equip_sel_latest'); KPI['tomografos']=eq.loc['Tomógrafo Computadorizado','Equipamentos em Uso']; KPI['tomografos_sus']=eq.loc['Tomógrafo Computadorizado','Estab c/ Equip SUS']; KPI['rm']=eq.loc['Ressonância Magnética','Equipamentos em Uso']; KPI['mamografos']=eq.loc['Mamógrafo','Equipamentos em Uso']; KPI['mamografos_sus']=eq.loc['Mamógrafo','Estab c/ Equip SUS']
eqe=load('cnes_equip_sel_esfjur_latest'); KPI['tomo_estadual']=eqe.loc['Tomógrafo Computadorizado','Administração Pública Estadual ou Distrito Federal']; KPI['rm_estadual']=eqe.loc['Ressonância Magnética','Administração Pública Estadual ou Distrito Federal']; KPI['mamo_estadual']=eqe.loc['Mamógrafo','Administração Pública Estadual ou Distrito Federal']

# ---------- SIM / SINASC ----------
for n,t in [('sim_cap_ano','Óbitos de residentes por capítulo CID-10 e ano (SIM)'),('sim_fxet_ano','Óbitos de residentes por faixa etária e ano (SIM)'),('sim_mun_ano','Óbitos por município de residência e ano (SIM)'),('sim_local_ano','Óbitos por local de ocorrência e ano (SIM)'),('sim_maldef_ano','Óbitos por causas mal definidas e ano (SIM)'),('sim_causabr_2024','Óbitos por causa CID-BR-10, 2024 (SIM)'),('sim_causabr_2023','Óbitos por causa CID-BR-10, 2023 (SIM)'),('siminf_fxet_ano','Óbitos infantis (<1 ano) por componente e ano (SIM)'),('siminf_mun_ano','Óbitos infantis por município de residência e ano (SIM)'),('siminf_evit_ano','Óbitos infantis por causas evitáveis (0 a 4 anos) e ano (SIM)'),('sinasc_ano','Nascidos vivos por ano: residência da mãe e ocorrência (SINASC)'),('sinasc_mun_ano','Nascidos vivos por município de residência e ano (SINASC)'),('sinasc_parto_ano','Nascidos vivos por tipo de parto e ano (SINASC)'),('sinasc_prenatal_ano','Nascidos vivos por nº de consultas de pré-natal e ano (SINASC)'),('sinasc_peso_ano','Nascidos vivos por peso ao nascer e ano (SINASC)'),('sinasc_idademae_ano','Nascidos vivos por idade da mãe e ano (SINASC)'),('sinasc_gest_ano','Nascidos vivos por duração da gestação e ano (SINASC)'),('sinasc_local_ano','Nascidos vivos por local de ocorrência e ano (SINASC)'),('sinasc_robson_2024','Nascidos vivos por Grupo de Robson e tipo de parto, 2024 (SINASC)')]:
    d=load(n)
    if d is not None: sheets['VITAL_'+n]=(d,t+' - Amapá','2025 preliminar; 2026 parcial.')
sim=load('sim_cap_ano'); nv=load('sinasc_ano'); inf=load('siminf_fxet_ano')
KPI['obitos_2019']=sim.loc['Total','2019']; KPI['obitos_2021']=sim.loc['Total','2021']; KPI['obitos_2024']=sim.loc['Total','2024']; KPI['obitos_2025']=sim.loc['Total','2025']
KPI['nv_2015']=nv.loc['2015','Nascim p/resid.mãe']; KPI['nv_2019']=nv.loc['2019','Nascim p/resid.mãe']; KPI['nv_2024']=nv.loc['2024','Nascim p/resid.mãe']; KPI['nv_2025']=nv.loc['2025','Nascim p/resid.mãe']
tmi={y: inf.loc['Total',str(y)]/nv.loc[str(y),'Nascim p/resid.mãe']*1000 for y in range(2015,2026)}
KPI['tmi']=tmi
par=load('sinasc_parto_ano'); KPI['ces_pct_2015']=par.loc['Cesário','2015']/par.loc['Total','2015']*100; KPI['ces_pct_2025']=par.loc['Cesário','2025']/par.loc['Total','2025']*100
pn=load('sinasc_prenatal_ano'); KPI['pn7_pct_2015']=pn.loc['7 ou mais consultas','2015']/pn.loc['Total','2015']*100; KPI['pn7_pct_2025']=pn.loc['7 ou mais consultas','2025']/pn.loc['Total','2025']*100
im=load('sinasc_idademae_ano'); KPI['adol_pct_2015']=(im.loc['10 a 14 anos','2015']+im.loc['15 a 19 anos','2015'])/im.loc['Total','2015']*100; KPI['adol_pct_2025']=(im.loc['10 a 14 anos','2025']+im.loc['15 a 19 anos','2025'])/im.loc['Total','2025']*100
md=load('sim_maldef_ano'); KPI['maldef_pct_2024']=md.loc['Total','2024']/sim.loc['Total','2024']*100
cb=load('sim_causabr_2024'); KPI['agress_2024']=cb.loc['. 110 Agressões','Óbitos p/Residênc']; cb23=load('sim_causabr_2023'); KPI['agress_2023']=cb23.loc['. 110 Agressões','Óbitos p/Residênc']
ev5=load('siminf_evit_ano'); KPI['inf_evit_2024']=ev5.loc['1. Causas evitáveis','2024']; KPI['inf_evit_pct_2024']=ev5.loc['1. Causas evitáveis','2024']/ev5.loc['Total','2024']*100
# Tabela indicadores vitais por ano
vit=pd.DataFrame({'Nascidos vivos (res.)':[nv.loc[str(y),'Nascim p/resid.mãe'] for y in range(2015,2026)],
 'Óbitos infantis (<1 ano)':[inf.loc['Total',str(y)] for y in range(2015,2026)],
 'Taxa de mortalidade infantil (por mil NV)':[tmi[y] for y in range(2015,2026)],
 'Óbitos totais (res.)':[sim.loc['Total',str(y)] for y in range(2015,2026)],
 '% partos cesáreos':[par.loc['Cesário',str(y)]/par.loc['Total',str(y)]*100 for y in range(2015,2026)],
 '% NV com 7+ consultas pré-natal':[pn.loc['7 ou mais consultas',str(y)]/pn.loc['Total',str(y)]*100 for y in range(2015,2026)],
 '% NV de mães de 10-19 anos':[(im.loc['10 a 14 anos',str(y)]+im.loc['15 a 19 anos',str(y)])/im.loc['Total',str(y)]*100 for y in range(2015,2026)],
 '% óbitos por causas mal definidas':[md.loc['Total',str(y)]/sim.loc['Total',str(y)]*100 for y in range(2015,2026)]},index=[str(y) for y in range(2015,2026)])
vit.index.name='Ano'
sheets['VITAL_00_Indicadores']=(vit,'Indicadores vitais sintéticos do Amapá, 2015-2025 (SINASC/SIM)','Cálculo próprio a partir dos dados de residência. 2025 preliminar.')

# ---------- Benchmarks UF ----------
def ufname(s): return re.sub(r'^\d\d ','',s)
bh=load('bench_sih_uf_2025'); bhv=load('bench_sih_uf_ano_valor'); bha=load('bench_sih_uf_ano_aih')
bs=load('bench_sia_uf_ano_valor'); bsq=load('bench_sia_uf_ano_qtd')
bl=load('bench_cnes_leitos_uf_latest'); bu=load('bench_cnes_uti_uf_latest'); bm0=load('bench_cnes_medicos_uf_latest')
SIGLA={'RO':'11 Rondônia','AC':'12 Acre','AM':'13 Amazonas','RR':'14 Roraima','PA':'15 Pará','AP':'16 Amapá','TO':'17 Tocantins','MA':'21 Maranhão','PI':'22 Piauí','CE':'23 Ceará','RN':'24 Rio Grande do Norte','PB':'25 Paraíba','PE':'26 Pernambuco','AL':'27 Alagoas','SE':'28 Sergipe','BA':'29 Bahia','MG':'31 Minas Gerais','ES':'32 Espírito Santo','RJ':'33 Rio de Janeiro','SP':'35 São Paulo','PR':'41 Paraná','SC':'42 Santa Catarina','RS':'43 Rio Grande do Sul','MS':'50 Mato Grosso do Sul','MT':'51 Mato Grosso','GO':'52 Goiás','DF':'53 Distrito Federal'}
bm=None
if bm0 is not None:
    t=bm0.loc['Total']; bm=pd.DataFrame({'Total':{SIGLA[k]:v for k,v in t.items() if k in SIGLA}}); bm.loc['Total','Total']=t['Total']
binf=load('bench_siminf_uf_ano'); bnv=load('bench_sinasc_uf_ano'); bsim=load('bench_sim_uf_ano'); bmd=load('bench_sim_uf_maldef')
rows=[]
for idx in bha.index:
    if idx=='Total': continue
    u=ufname(idx); p25=pop_uf.get(u,{}).get(2025); p24=pop_uf.get(u,{}).get(2024)
    if not p25: continue
    r={'UF':u,'População 2025':p25,
       'AIH 2025':bha.loc[idx,'2025'],'AIH por 100 hab 2025':bha.loc[idx,'2025']/p25*100,
       'Valor SIH 2025 (R$)':bhv.loc[idx,'2025'],'Valor SIH por hab 2025 (R$)':bhv.loc[idx,'2025']/p25,
       'Valor médio AIH 2025 (R$)':bh.loc[idx,'Valor médio AIH'],'Média permanência 2025':bh.loc[idx,'Média permanência'],'Taxa mortalidade hosp. 2025 (%)':bh.loc[idx,'Taxa mortalidade'],
       'Valor SIA 2024 (R$)':bs.loc[idx,'2024'] if bs is not None and idx in bs.index else None,'Valor SIA por hab 2024 (R$)':(bs.loc[idx,'2024']/p24) if bs is not None and idx in bs.index else None}
    if bl is not None and idx in bl.index: r['Leitos SUS (set/2026)']=bl.loc[idx,'Qtd SUS']; r['Leitos SUS por mil hab']=bl.loc[idx,'Qtd SUS']/pop_uf[u].get(2026,p25)*1000; r['Leitos existentes']=bl.loc[idx,'Qtd existente']
    if bu is not None and idx in bu.index: r['Leitos complementares SUS (UTI/UCI)']=bu.loc[idx,'Quantidade SUS']
    if bm is not None and idx in bm.index: r['Médicos (indivíduos) set/2026']=bm.loc[idx,'Total']; r['Médicos por mil hab']=bm.loc[idx,'Total']/pop_uf[u].get(2026,p25)*1000
    if binf is not None and bnv is not None and idx in binf.index:
        r['TMI 2024 (por mil NV)']=binf.loc[idx,'2024']/bnv.loc[idx,'2024']*1000; r['TMI 2023']=binf.loc[idx,'2023']/bnv.loc[idx,'2023']*1000
    if bmd is not None and bsim is not None and idx in bmd.index: r['% óbitos mal definidos 2024']=bmd.loc[idx,'Total']/bsim.loc[idx,'2024']*100
    rows.append(r)
bench=pd.DataFrame(rows).set_index('UF')
# Brasil
pb=pop_br[2025]; tot={'População 2025':pb,'AIH 2025':bha.loc['Total','2025'],'AIH por 100 hab 2025':bha.loc['Total','2025']/pb*100,'Valor SIH 2025 (R$)':bhv.loc['Total','2025'],'Valor SIH por hab 2025 (R$)':bhv.loc['Total','2025']/pb,'Valor médio AIH 2025 (R$)':bh.loc['Total','Valor médio AIH'],'Média permanência 2025':bh.loc['Total','Média permanência'],'Taxa mortalidade hosp. 2025 (%)':bh.loc['Total','Taxa mortalidade']}
if bs is not None: tot['Valor SIA 2024 (R$)']=bs.loc['Total','2024']; tot['Valor SIA por hab 2024 (R$)']=bs.loc['Total','2024']/pop_br[2024]
if bl is not None: tot['Leitos SUS (set/2026)']=bl.loc['Total','Qtd SUS']; tot['Leitos SUS por mil hab']=bl.loc['Total','Qtd SUS']/pop_br[2026]*1000; tot['Leitos existentes']=bl.loc['Total','Qtd existente']
if bu is not None: tot['Leitos complementares SUS (UTI/UCI)']=bu.loc['Total','Quantidade SUS']
if bm is not None: tot['Médicos (indivíduos) set/2026']=bm.loc['Total','Total']; tot['Médicos por mil hab']=bm.loc['Total','Total']/pop_br[2026]*1000
if binf is not None and bnv is not None: tot['TMI 2024 (por mil NV)']=binf.loc['Total','2024']/bnv.loc['Total','2024']*1000; tot['TMI 2023']=binf.loc['Total','2023']/bnv.loc['Total','2023']*1000
if bmd is not None and bsim is not None: tot['% óbitos mal definidos 2024']=bmd.loc['Total','Total']/bsim.loc['Total','2024']*100
bench.loc['BRASIL']=pd.Series(tot)
# ranks for AP
for col in ['AIH por 100 hab 2025','Valor SIH por hab 2025 (R$)','Valor médio AIH 2025 (R$)','Valor SIA por hab 2024 (R$)','Leitos SUS por mil hab','Médicos por mil hab','TMI 2024 (por mil NV)','% óbitos mal definidos 2024','Taxa mortalidade hosp. 2025 (%)']:
    if col in bench.columns:
        s=bench.drop('BRASIL')[col].dropna()
        KPI['rank_'+col]=(int((s.rank(ascending=False))['Amapá']),len(s))
        KPI['ap_'+col]=bench.loc['Amapá',col]; KPI['br_'+col]=bench.loc['BRASIL',col]
sheets['BENCH_UF']=(bench,'Comparativo entre UFs e Brasil: produção hospitalar e ambulatorial, leitos, médicos e mortalidade infantil','Cálculo próprio. SIA por UF disponível até 2024 completo. TMI = óbitos <1 ano / nascidos vivos (residência).')
for n,t in [('bench_sih_uf_ano_aih','AIH aprovadas por UF de internação e ano'),('bench_sih_uf_ano_valor','Valor total SIH (R$) por UF de internação e ano'),('bench_sihres_uf_ano_aih','AIH por UF de residência e ano'),('bench_sihres_uf_ano_valor','Valor SIH (R$) por UF de residência e ano'),('bench_sih_uf_2025','Produção hospitalar por UF, 2025'),('bench_sia_uf_ano_qtd','Quantidade ambulatorial aprovada por UF e ano'),('bench_sia_uf_ano_valor','Valor ambulatorial aprovado (R$) por UF e ano'),('bench_cnes_leitos_uf_latest','Leitos de internação por UF, set/2026'),('bench_cnes_uti_uf_latest','Leitos complementares por UF, set/2026'),('bench_cnes_medicos_uf_latest','Médicos por UF e atendimento ao SUS, set/2026'),('bench_siminf_uf_ano','Óbitos infantis por UF e ano'),('bench_sinasc_uf_ano','Nascidos vivos por UF e ano'),('bench_sim_uf_ano','Óbitos por UF e ano'),('bench_sim_uf_maldef','Óbitos por causas mal definidas por UF, 2024')]:
    d=load(n)
    if d is not None: sheets['BENCH_'+n.replace('bench_','')]=(d,t,'')

# ---------- SIOPS ----------
srows=list(csv.DictReader(open(RAW+'/siops/siops_indicadores.csv',encoding='utf-8'),delimiter=';'))
labels={'ind_1.1':'1.1 Part. receita de impostos na receita total (%)','ind_1.2':'1.2 Part. transferências intergov. na receita total (%)','ind_1.3':'1.3 Part. transf. SUS no total transferido ao Estado (%)','ind_1.4':'1.4 Part. transf. União p/ saúde no total transf. p/ saúde (%)','ind_1.5':'1.5 Part. transf. União SUS no total transf. União (%)','ind_1.6':'1.6 Part. impostos+transf. constitucionais na receita total (%)','ind_2.1':'2.1 Despesa total com saúde por habitante (R$)','ind_2.2':'2.2 Part. despesa com pessoal na despesa total c/ saúde (%)','ind_2.3':'2.3 Part. despesa com medicamentos (%)','ind_2.4':'2.4 Part. serviços de terceiros - pessoa jurídica (%)','ind_2.5':'2.5 Part. investimentos (%)','ind_2.6':'2.6 Despesas c/ instituições privadas sem fins lucrativos (%)','ind_3.1':'3.1 Part. transferências p/ saúde na despesa total c/ saúde (%)','ind_3.2':'3.2 % receita própria aplicada em ASPS (LC 141/2012; mín. 12%)'}
ap=[r for r in srows if r['uf']=='Amapá']
si=pd.DataFrame({f"{r['ano']} ({r['bimestre']}º bim.)":{labels[k]:float(r[k]) for k in labels if r.get(k)} for r in ap})
si=si.reindex([labels[k] for k in labels]); si.index.name='Indicador'
sheets['SIOPS_AP_Serie']=(si,'SIOPS - Indicadores do Estado do Amapá, 2015-2026 (6º bimestre = anual; 2026 = 4º bimestre, parcial)','Fonte: SIOPS/MS, consulta de indicadores de estados. Despesa empenhada. Ind. 3.2 = aplicação mínima constitucional (12%).')
for r in ap: 
    KPI[f"siops_32_{r['ano']}"]=float(r['ind_3.2']); KPI[f"siops_21_{r['ano']}"]=float(r['ind_2.1']); KPI[f"siops_22_{r['ano']}"]=float(r['ind_2.2']); KPI[f"siops_24_{r['ano']}"]=float(r['ind_2.4']); KPI[f"siops_25_{r['ano']}"]=float(r['ind_2.5']); KPI[f"siops_31_{r['ano']}"]=float(r['ind_3.1']); KPI[f"siops_13_{r['ano']}"]=float(r['ind_1.3']) if r.get('ind_1.3') else None
    KPI[f"siops_23_{r['ano']}"]=float(r['ind_2.3']) if r.get('ind_2.3') else None
for ano in ('2024','2025'):
    rk=[(r['uf'],float(r['ind_3.2']),float(r['ind_2.1']),float(r['ind_2.2']),float(r['ind_2.4']),float(r['ind_2.5']),float(r['ind_3.1'])) for r in srows if r['ano']==ano and r['bimestre']=='6']
    d=pd.DataFrame(rk,columns=['UF','% receita própria em ASPS (3.2)','Despesa c/ saúde por hab (R$) (2.1)','% pessoal (2.2)','% serviços terceiros PJ (2.4)','% investimentos (2.5)','% transferências na despesa (3.1)']).set_index('UF').sort_values('% receita própria em ASPS (3.2)',ascending=False)
    d['Posição (3.2)']=range(1,len(d)+1); d['Posição (desp./hab)']=d['Despesa c/ saúde por hab (R$) (2.1)'].rank(ascending=False).astype(int)
    sheets[f'SIOPS_UF_{ano}']=(d,f'SIOPS - Indicadores dos Estados, exercício {ano} (anual)','Fonte: SIOPS/MS.')
    KPI[f'siops_rank32_{ano}']=int(d.loc['Amapá','Posição (3.2)']); KPI[f'siops_rank21_{ano}']=int(d.loc['Amapá','Posição (desp./hab)']); KPI[f'siops_median32_{ano}']=d['% receita própria em ASPS (3.2)'].median(); KPI[f'siops_median21_{ano}']=d['Despesa c/ saúde por hab (R$) (2.1)'].median()
    KPI[f'siops_despesa_total_{ano}']=float(d.loc['Amapá','Despesa c/ saúde por hab (R$) (2.1)'])*pop_ap[int(ano)]

# ---------- Edital concurso ----------
ed=pd.DataFrame([['Região I - Central (Macapá, Cutias, Itaubal, Ferreira Gomes, Porto Grande, Pedra Branca do Amapari, Serra do Navio)',2552,2409,143],['Região II - Norte (Oiapoque, Calçoene, Amapá, Pracuúba, Tartarugalzinho)',637,600,37],['Região III - Sudoeste (Santana, Mazagão, Laranjal do Jari, Vitória do Jari)',1021,962,59],['Total',4210,3971,239]],columns=['Região de Saúde','Vagas (cadastro de reserva)','Ampla concorrência','PcD']).set_index('Região de Saúde')
sheets['RH_Concurso_2026']=(ed,'Concurso Público SESA/AP - Edital nº 001/2026 (Instituto AOCP): vagas de cadastro de reserva por Região de Saúde','Fonte: Edital de Abertura nº 001/2026 (publicado 11/09/2026). Maiores quantitativos: Técnico em Enfermagem (904 na Região I), Enfermeiro (786 na Região I). Vencimento básico: NS R$ 11.116,42 (médicos) / R$ 5.520,64 (demais NS) / R$ 3.363,43 (NM).')

# ---------- Indicadores-chave (resumo) ----------
resumo=[
 ('Demografia','População residente (IBGE 2025)',pop_ap[2025],'hab.'),
 ('Produção hospitalar','AIH aprovadas 2025',KPI['sih_aih_2025'],'AIH'),
 ('Produção hospitalar','Valor total SIH 2025',KPI['sih_valor_2025'],'R$'),
 ('Produção hospitalar','Internações por 100 hab 2025',KPI['sih_aih_por_100hab_2025'],'/100 hab'),
 ('Produção hospitalar','Valor médio da AIH 2025',KPI['sih_valor_medio_2025'],'R$'),
 ('Produção hospitalar','Taxa de mortalidade hospitalar 2025',KPI['sih_tm_2025'],'%'),
 ('Produção hospitalar','Média de permanência 2025',KPI['sih_mp_2025'],'dias'),
 ('Produção hospitalar','% AIH eletivas 2025',KPI['sih_eletivo_2025']/KPI['sih_aih_2025']*100,'%'),
 ('Produção hospitalar','% AIH de alta complexidade 2025',KPI['sih_alta_pct_2025'],'%'),
 ('Produção ambulatorial','Procedimentos aprovados 2025',KPI['sia_qtd_2025'],'proc.'),
 ('Produção ambulatorial','Valor aprovado SIA 2025',KPI['sia_val_2025'],'R$'),
 ('Produção ambulatorial','Valor SIA por habitante 2025',KPI['sia_val_por_hab_2025'],'R$/hab'),
 ('Rede física','Leitos de internação existentes (set/2026)',KPI['leitos_exist_2026'],'leitos'),
 ('Rede física','Leitos de internação SUS (set/2026)',KPI['leitos_sus_2026'],'leitos'),
 ('Rede física','Leitos SUS por mil habitantes',KPI['leitos_sus_por_1000_2026'],'/mil hab'),
 ('Rede física','Leitos UTI adulto existentes (set/2026)',KPI['uti_adulto_2026'],'leitos'),
 ('Rede física','Leitos UTI pediátrica (set/2026)',KPI['uti_ped_2026'],'leitos'),
 ('Rede física','Leitos UTI neonatal (set/2026)',KPI['uti_neo_2026'],'leitos'),
 ('Rede física','Hospitais gerais / especializados (set/2026)',KPI['hosp_geral_2026']+KPI['hosp_esp_2026'],'estab.'),
 ('Recursos humanos','Médicos (indivíduos) cadastrados no CNES (set/2026)',KPI['medicos_2026'],'médicos'),
 ('Recursos humanos','Médicos por mil habitantes',KPI['medicos_por_1000_2026'],'/mil hab'),
 ('Recursos humanos','Enfermeiros (indivíduos) (set/2026)',KPI['enf_2026'],'enfermeiros'),
 ('Financiamento','% receita própria aplicada em ASPS 2025 (SIOPS)',KPI['siops_32_2025'],'%'),
 ('Financiamento','Despesa estadual com saúde por habitante 2025 (SIOPS)',KPI['siops_21_2025'],'R$/hab'),
 ('Financiamento','Despesa estadual total com saúde 2025 (estimada = 2.1 x pop.)',KPI['siops_despesa_total_2025'],'R$'),
 ('Indicadores vitais','Nascidos vivos 2025 (residência)',KPI['nv_2025'],'NV'),
 ('Indicadores vitais','Taxa de mortalidade infantil 2024',tmi[2024],'/mil NV'),
 ('Indicadores vitais','Taxa de mortalidade infantil 2025 (prelim.)',tmi[2025],'/mil NV'),
 ('Indicadores vitais','% partos cesáreos 2025',KPI['ces_pct_2025'],'%'),
 ('Indicadores vitais','% NV com 7+ consultas de pré-natal 2025',KPI['pn7_pct_2025'],'%'),
 ('Indicadores vitais','Óbitos totais 2025 (prelim.)',KPI['obitos_2025'],'óbitos'),
]
res=pd.DataFrame(resumo,columns=['Dimensão','Indicador','Valor','Unidade']).set_index(['Dimensão','Indicador'])
sheets={'00_Indicadores_Chave':(res,'Painel-resumo de indicadores-chave da saúde no Amapá (ver fontes em cada aba)','Valores de 2025/2026 sujeitos a atualização nas bases DATASUS.'),**sheets}

# ---------- Recorte temporal 2022-2026 ----------
import re as _re
YMIN=2022
def _yr(label):
    m=_re.match(r'^\s*(?:\.\.)?\s*(?:[A-Za-zç]+/)?(\d{4})(?:/[A-Za-z]{3})?(?:\s*\(.*\))?\s*$',str(label))
    return int(m.group(1)) if m else None
def recorte(df):
    cols=[c for c in df.columns if (_yr(c) is None or _yr(c)>=YMIN)]
    df=df[cols]
    idx=[i for i in df.index if (_yr(i) is None or _yr(i)>=YMIN)]
    return df.loc[idx]
sheets={k:(recorte(df),t,n) for k,(df,t,n) in sheets.items()}
# ---------- Workbook ----------
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
wb=Workbook(); ws0=wb.active; ws0.title='Indice'
ws0['A1']='Levantamento da produção hospitalar, ambulatorial e indicadores de saúde - Estado do Amapá (SESA/AP)'; ws0['A1'].font=Font(bold=True,size=14)
ws0['A2']='Estudo analítico para transição de governo 2026/2027. Série histórica 2022-2026 (2026 parcial). Dados públicos: DATASUS/TABNET (SIH, SIA, CNES, SIM, SINASC), SIOPS/MS, IBGE/SIDRA, Edital SESA 001/2026. Extração em 06/11/2026.'
ws0['A4']='Aba'; ws0['B4']='Conteúdo'; ws0['C4']='Observações'
for c in ('A4','B4','C4'): ws0[c].font=Font(bold=True)
rown=5
hdr_fill=PatternFill('solid',fgColor='1F4E79'); hdr_font=Font(bold=True,color='FFFFFF'); tot_font=Font(bold=True)
def short(name): return name[:31]
used=set()
for name,(df,title,note) in sheets.items():
    sn=short(name)
    while sn in used: sn=sn[:29]+'_2'
    used.add(sn)
    ws0.cell(row=rown,column=1,value=sn).hyperlink=f"#'{sn}'!A1"; ws0.cell(row=rown,column=1).font=Font(color='0563C1',underline='single')
    ws0.cell(row=rown,column=2,value=title); ws0.cell(row=rown,column=3,value=note); rown+=1
    ws=wb.create_sheet(sn)
    ws['A1']=title; ws['A1'].font=Font(bold=True,size=12)
    ws['A2']=note; ws['A2'].font=Font(italic=True,color='595959')
    d=df.reset_index()
    for j,col in enumerate(d.columns,1):
        c=ws.cell(row=4,column=j,value=str(col)); c.fill=hdr_fill; c.font=hdr_font; c.alignment=Alignment(wrap_text=True,vertical='center')
    for i,row in enumerate(d.itertuples(index=False),5):
        for j,v in enumerate(row,1):
            if isinstance(v,float) and math.isnan(v): v=None
            if hasattr(v,'item'): v=v.item()
            c=ws.cell(row=i,column=j,value=v)
            if isinstance(v,(int,float)):
                c.number_format='#,##0.00' if (isinstance(v,float) and abs(v-round(v))>1e-9) else '#,##0'
            if str(row[0]).strip()=='Total' or str(row[0]).strip()=='BRASIL': c.font=tot_font
    ws.freeze_panes='B5'
    for j,col in enumerate(d.columns,1):
        w=max([len(str(col))]+[len(str(x)) for x in d.iloc[:,j-1].head(200)])
        ws.column_dimensions[get_column_letter(j)].width=min(max(10,w+2),70 if j==1 else 22)
    ws.row_dimensions[4].height=42
ws0.column_dimensions['A'].width=34; ws0.column_dimensions['B'].width=110; ws0.column_dimensions['C'].width=70
# Fontes
wsf=wb.create_sheet('Fontes_Notas')
fontes=[('SIH/SUS - Sistema de Informações Hospitalares (TABNET)','http://tabnet.datasus.gov.br/cgi/deftohtm.exe?sih/cnv/qiap.def (local de internação); sih/cnv/qrap.def (residência); sih/cnv/niap.def (morbidade); sih/cnv/qiuf.def e qruf.def (UFs)','AIH aprovadas por ano/mês de processamento. 2026 até competência ago/2026.'),
('SIA/SUS - Sistema de Informações Ambulatoriais (TABNET)','http://tabnet.datasus.gov.br/cgi/deftohtm.exe?sia/cnv/qaap.def; sia/cnv/qauf.def','Quantidade e valor aprovados por ano de processamento. Não há dimensão "estabelecimento" na tabulação estadual do SIA.'),
('CNES - Cadastro Nacional de Estabelecimentos de Saúde (TABNET)','cnes/cnv/leiintap.def (leitos); leiutiap.def (complementares); estabap.def; equipoap.def; prid02ap.def (profissionais); versões *br.def para UFs','Competência set/2026 (última disponível). Dezembro de cada ano para séries.'),
('SIM - Sistema de Informações sobre Mortalidade (TABNET)','sim/cnv/obt10ap.def; sim/cnv/inf10ap.def; sim/cnv/obt10uf.def; inf10uf.def','Óbitos por residência. 2025 preliminar; 2026 parcial.'),
('SINASC - Sistema de Informações sobre Nascidos Vivos (TABNET)','sinasc/cnv/nvap.def; sinasc/cnv/nvuf.def','Nascidos vivos por residência da mãe. 2025 preliminar.'),
('SIOPS - Sistema de Informações sobre Orçamentos Públicos em Saúde (MS)','http://siops.datasus.gov.br/consdetalhereenvio2uf.php (UF=16)','Indicadores dos estados, despesa empenhada, 6º bimestre (anual). 2026 = 4º bimestre.'),
('IBGE - Estimativas populacionais (SIDRA, tabela 6579)','https://apisidra.ibge.gov.br/values/t/6579/...','2024-2026: estimativas pós-Censo 2022. 2019-2021: estimativas pré-Censo (não comparáveis diretamente).'),
('Edital de Concurso Público SESA/AP nº 001/2026','Instituto AOCP / SEAD-AP, publicado em 11/09/2026','4.210 vagas de cadastro de reserva por Região de Saúde.'),
('LOA 2026 e PLOA 2027 do Estado do Amapá','Assembleia Legislativa do Amapá (Alap) e imprensa local (Diário do Amapá, De Bubuia)','LOA 2026: R$ 12,425 bi; Fundo Estadual de Saúde 2026: R$ 1,72 bi; PLOA 2027: R$ 13,47 bi, FES R$ 1,98 bi (+15,26%). Valores de fonte secundária, a confirmar na LOA publicada.'),
('Limitações','ConsultaFNS (repasses fundo a fundo) e portais estaduais (transparencia.ap.gov.br, saude.ap.gov.br) não acessíveis a partir do ambiente de extração; e-Gestor AB/SISAB (cobertura APS) e SI-PNI (vacinação) não tabulados.','Recomenda-se complementar na transição com dados internos da SESA: filas de regulação (SISREG), TFD, estoque de medicamentos, contratos, restos a pagar e folha.')]
wsf['A1']='Fontes e notas metodológicas'; wsf['A1'].font=Font(bold=True,size=12)
for j,h in enumerate(['Fonte','Endereço / tabulação','Notas'],1):
    c=wsf.cell(row=3,column=j,value=h); c.fill=hdr_fill; c.font=hdr_font
for i,f in enumerate(fontes,4):
    for j,v in enumerate(f,1): wsf.cell(row=i,column=j,value=v).alignment=Alignment(wrap_text=True,vertical='top')
wsf.column_dimensions['A'].width=45; wsf.column_dimensions['B'].width=80; wsf.column_dimensions['C'].width=80
wb.save(OUT+'/Tabelas_Saude_Amapa_Transicao_2026.xlsx')
print('workbook ok', len(sheets))

# ---------- Gráficos ----------
def save(fig,name): fig.tight_layout(); fig.savefig(f'{GR}/{name}.png',dpi=160); plt.close(fig)
def style(ax,ylabel=''):
    ax.grid(axis='y',color=GRID,linewidth=0.8); ax.set_axisbelow(True); ax.set_ylabel(ylabel,color=INK2)
def brl(x,pos): return f'{x/1e6:,.0f}'.replace(',','.')
years=[str(y) for y in range(2022,2027)]
# G1: AIH e valor SIH
fig,ax=plt.subplots(figsize=(9,4.2))
ax.bar(years,[sih.loc[y,'AIH aprovadas'] for y in years],color=C[0],width=0.7)
style(ax,'Internações (AIH aprovadas)'); ax.set_title('Internações SUS no Amapá, 2022-2026* (SIH/SUS; *jan-ago)',loc='left',color=INK,fontweight='bold')
for y in years: ax.annotate(fmt_int(sih.loc[y,'AIH aprovadas']),(y,sih.loc[y,'AIH aprovadas']),ha='center',va='bottom',fontsize=9,color=INK2,xytext=(0,3),textcoords='offset points')
ax.yaxis.set_major_formatter(FuncFormatter(lambda x,p: fmt_int(x)))
save(fig,'g01_sih_aih_ano')
fig,ax=plt.subplots(figsize=(9,4.2))
ax.plot(years,[sih.loc[y,'Valor total']/1e6 for y in years],color=C[0],lw=2,marker='o',ms=5,label='Hospitalar (SIH)')
ax.plot(years,[sia.loc[y,'Valor aprovado']/1e6 for y in years],color=C[1],lw=2,marker='o',ms=5,label='Ambulatorial (SIA)')
style(ax,'R$ milhões (valores correntes)'); ax.set_title('Valor aprovado da produção SUS no Amapá, 2022-2026* (*jan-ago)',loc='left',color=INK,fontweight='bold'); ax.legend(frameon=False)
ax.annotate(f"R$ {mi(sia.loc['2025','Valor aprovado'])} mi",('2025',sia.loc['2025','Valor aprovado']/1e6),xytext=(-40,8),textcoords='offset points',fontsize=9,color=INK2)
ax.annotate(f"R$ {mi(sih.loc['2025','Valor total'])} mi",('2025',sih.loc['2025','Valor total']/1e6),xytext=(-40,8),textcoords='offset points',fontsize=9,color=INK2)
save(fig,'g02_valor_sih_sia')
# G3: estabelecimentos 2025
top=KPI['sih_estab_top'].copy(); top.index=[re.sub(r'^\d+ ','',i).replace('SES AP ','').replace('SESA AP ','').replace('SES ','').title() for i in top.index]
top=top[top['AIH aprovadas']>0].head(14).iloc[::-1]
fig,ax=plt.subplots(figsize=(9,5.6))
ax.barh(top.index,top['AIH aprovadas'],color=C[0],height=0.7)
for i,(k,v) in enumerate(top['AIH aprovadas'].items()): ax.text(v+150,i,fmt_int(v),va='center',fontsize=9,color=INK2)
ax.grid(axis='x',color=GRID); ax.set_axisbelow(True); ax.set_title('Internações (AIH) por estabelecimento, Amapá, 2025',loc='right',color=INK,fontweight='bold'); ax.set_xlabel('AIH aprovadas',color=INK2)
ax.xaxis.set_major_formatter(FuncFormatter(lambda x,p: fmt_int(x))); ax.set_xlim(0,top['AIH aprovadas'].max()*1.15)
save(fig,'g03_sih_estab_2025')
# G4: leitos SUS por especialidade
cols=[c for c in ls.columns if c!='Total' and _yr(c)>=YMIN]
fig,ax=plt.subplots(figsize=(9,4.4))
lab={'Clínicos':C[0],'Cirúrgicos':C[1],'Obstétrico':C[2],'Pediátrico':C[3],'Outras Especialidades':C[4]}
for k,col in lab.items(): ax.plot([c.replace('/Dez','').replace('/Set','*') for c in cols],[ls.loc[k,c] for c in cols],lw=2,marker='o',ms=4,color=col,label=k)
style(ax,'Leitos SUS'); ax.set_title('Leitos de internação SUS por especialidade, Amapá, 2022-2026 (CNES, dez. de cada ano; *set/2026)',loc='left',color=INK,fontweight='bold',fontsize=10); ax.legend(frameon=False,ncol=3,fontsize=9)
save(fig,'g04_leitos_sus')
# G5: UTI
fig,ax=plt.subplots(figsize=(9,4.2))
series={'UTI adulto (I+II+III)':[uti.loc['UTI adulto I',c]+uti.loc['UTI adulto II',c]+uti.loc['UTI adulto III',c] for c in cols],'UTI pediátrica':[uti.loc['UTI pediátrica II',c] for c in cols],'UTI neonatal (I+II)':[uti.loc['UTI neonatal I',c]+uti.loc['UTI neonatal II',c] for c in cols]}
for (k,v),col in zip(series.items(),C[:3]): ax.plot([c.replace('/Dez','').replace('/Set','*') for c in cols],v,lw=2,marker='o',ms=4,color=col,label=k)
style(ax,'Leitos existentes'); ax.set_title('Leitos de UTI existentes no Amapá (CNES; exclui leitos COVID temporários; *set/2026)',loc='left',color=INK,fontweight='bold',fontsize=10); ax.legend(frameon=False)
save(fig,'g05_uti')
# G6: SIOPS
yrs=[r['ano'] for r in ap if r['bimestre']=='6' and int(r['ano'])>=YMIN]
fig,ax=plt.subplots(figsize=(9,4.2))
ax.bar(yrs,[float(r['ind_3.2']) for r in ap if r['bimestre']=='6' and int(r['ano'])>=YMIN],color=C[0],width=0.7)
ax.axhline(12,color=C[7],lw=1.5,ls='--'); ax.text(yrs[-1],11.0,'mínimo constitucional: 12%',color=C[7],fontsize=9,ha='right',va='top')
for r in ap:
    if r['bimestre']=='6' and int(r['ano'])>=YMIN: ax.text(r['ano'],float(r['ind_3.2'])+0.2,fmt_br(float(r['ind_3.2']),1)+'%',ha='center',fontsize=8.5,color=INK2)
style(ax,'% da receita própria (LC 141/2012)'); ax.set_title('Aplicação de receita própria em ASPS - Estado do Amapá, 2022-2025 (SIOPS)',loc='left',color=INK,fontweight='bold',fontsize=10); ax.set_ylim(0,24)
save(fig,'g06_siops_32')
fig,ax=plt.subplots(figsize=(9,4.2))
ax.plot(yrs,[float(r['ind_2.1']) for r in ap if r['bimestre']=='6' and int(r['ano'])>=YMIN],color=C[0],lw=2,marker='o')
for r in ap:
    if r['bimestre']=='6' and int(r['ano'])>=YMIN: ax.annotate('R$ '+fmt_br(float(r['ind_2.1']),0),(r['ano'],float(r['ind_2.1'])),xytext=(0,6),textcoords='offset points',ha='center',fontsize=8.5,color=INK2)
style(ax,'R$ por habitante (empenhado)'); ax.set_title('Despesa do Estado com saúde por habitante - Amapá, 2022-2025 (SIOPS ind. 2.1)',loc='left',color=INK,fontweight='bold',fontsize=10)
save(fig,'g07_siops_21')
# G8: TMI AP vs Brasil
fig,ax=plt.subplots(figsize=(9,4.2))
yv=[y for y in years if int(y) in tmi]
ax.plot(yv,[tmi[int(y)] for y in yv],color=C[0],lw=2,marker='o',label='Amapá')
if binf is not None and bnv is not None:
    ax.plot(yv,[binf.loc['Total',y]/bnv.loc['Total',y]*1000 for y in yv],color=C[1],lw=2,marker='o',label='Brasil')
style(ax,'Óbitos < 1 ano por mil nascidos vivos'); ax.set_title('Taxa de mortalidade infantil, 2022-2025 (SIM/SINASC; 2025 preliminar)',loc='left',color=INK,fontweight='bold',fontsize=10); ax.legend(frameon=False); ax.set_ylim(0,25)
save(fig,'g08_tmi')
# G9: nascidos vivos e cesárea
fig,ax=plt.subplots(figsize=(9,4.2))
yv=[y for y in years if int(y)<=2025]
ax.bar(yv,[par.loc['Vaginal',y] for y in yv],color=C[0],width=0.7,label='Parto vaginal')
ax.bar(yv,[par.loc['Cesário',y] for y in yv],bottom=[par.loc['Vaginal',y] for y in yv],color=C[1],width=0.7,label='Cesárea')
for y in yv: ax.text(y,par.loc['Total',y]+150,fmt_br(par.loc['Cesário',y]/par.loc['Total',y]*100,0)+'% ces.',ha='center',fontsize=8,color=INK2)
style(ax,'Nascidos vivos (residência da mãe)'); ax.set_title('Nascidos vivos por tipo de parto, Amapá, 2022-2025 (SINASC; 2025 preliminar)',loc='left',color=INK,fontweight='bold'); ax.legend(frameon=False,loc='lower left'); ax.yaxis.set_major_formatter(FuncFormatter(lambda x,p: fmt_int(x)))
save(fig,'g09_nv_parto')
# G10: médicos e enfermeiros
fig,ax=plt.subplots(figsize=(9,4.2))
xs=[c.replace('/Dez','').replace('/Set','*') for c in cols]
ax.plot(xs,[med.loc['Total',c] for c in cols],color=C[0],lw=2,marker='o',label='Médicos')
ax.plot(xs,[ps.loc['Enfermeiro',c] for c in cols],color=C[1],lw=2,marker='o',label='Enfermeiros')
style(ax,'Indivíduos cadastrados (CNES)'); ax.set_title('Médicos e enfermeiros cadastrados no CNES, Amapá, 2022-2026 (dez. de cada ano; *set/2026)',loc='left',color=INK,fontweight='bold',fontsize=10); ax.legend(frameon=False)
save(fig,'g10_rh')
# G11: anomalia vascular (dois painéis, mesma escala temporal)
yrs2=[str(y) for y in range(2022,2027)]
fig,(a1,a2)=plt.subplots(1,2,figsize=(10,4))
a1.bar(yrs2,[sub.loc['0309 Terapias especializadas',y]/1e6 for y in yrs2],color=C[1],width=0.7)
style(a1,'R$ milhões'); a1.set_title('SIA: terapias especializadas (angiologia /\nesclerose de varizes), valor aprovado',loc='left',fontsize=9.5,color=INK,fontweight='bold')
a2.bar(yrs2,[cap.loc['IX.  Doenças do aparelho circulatório',y] for y in yrs2],color=C[0],width=0.7)
style(a2,'Internações (AIH)'); a2.set_title('SIH: internações por doenças do aparelho\ncirculatório (cap. IX CID-10)',loc='left',fontsize=9.5,color=INK,fontweight='bold')
a2.yaxis.set_major_formatter(FuncFormatter(lambda x,p: fmt_int(x)))
for a in (a1,a2): a.tick_params(axis='x',labelsize=9)
fig.suptitle('Salto de procedimentos vasculares no Amapá a partir de 2023 (2022-2026; 2026 = jan-ago)',x=0.01,ha='left',fontsize=10,color=INK2)
save(fig,'g11_vascular')
# G12: capítulos CID 2025
c25=load('nih_cap_2025').drop('Total').sort_values('Internações',ascending=False).head(10).iloc[::-1]
fig,ax=plt.subplots(figsize=(9,4.8))
ax.barh([re.sub(r'^[IVX]+\.\s*','',i) for i in c25.index],c25['Internações'],color=C[0],height=0.7)
for i,v in enumerate(c25['Internações']): ax.text(v+100,i,fmt_int(v),va='center',fontsize=9,color=INK2)
ax.grid(axis='x',color=GRID); ax.set_axisbelow(True); ax.set_title('Internações por capítulo CID-10, Amapá, 2025 (10 maiores)',loc='left',color=INK,fontweight='bold'); ax.set_xlim(0,c25['Internações'].max()*1.15); ax.xaxis.set_major_formatter(FuncFormatter(lambda x,p: fmt_int(x)))
save(fig,'g12_cid_2025')
# G13: benchmark AIH/100hab
bb=bench['AIH por 100 hab 2025'].dropna().sort_values()
fig,ax=plt.subplots(figsize=(9,6.5))
colors=[C[1] if u=='Amapá' else (C[3] if u=='BRASIL' else C[0]) for u in bb.index]
ax.barh(bb.index,bb.values,color=colors,height=0.7)
for i,v in enumerate(bb.values): ax.text(v+0.05,i,fmt_br(v,1),va='center',fontsize=8,color=INK2)
ax.grid(axis='x',color=GRID); ax.set_axisbelow(True); ax.set_title('Internações SUS por 100 habitantes, por UF de internação, 2025',loc='left',color=INK,fontweight='bold'); ax.tick_params(axis='y',labelsize=8)
save(fig,'g13_bench_aih')
if 'Leitos SUS por mil hab' in bench.columns:
    bb=bench['Leitos SUS por mil hab'].dropna().sort_values()
    fig,ax=plt.subplots(figsize=(9,6.5))
    colors=[C[1] if u=='Amapá' else (C[3] if u=='BRASIL' else C[0]) for u in bb.index]
    ax.barh(bb.index,bb.values,color=colors,height=0.7)
    for i,v in enumerate(bb.values): ax.text(v+0.01,i,fmt_br(v,2),va='center',fontsize=8,color=INK2)
    ax.grid(axis='x',color=GRID); ax.set_axisbelow(True); ax.set_title('Leitos de internação SUS por mil habitantes, por UF, set/2026 (CNES)',loc='left',color=INK,fontweight='bold'); ax.tick_params(axis='y',labelsize=8)
    save(fig,'g14_bench_leitos')
print('charts ok')

# ---------- KPIs dump ----------
def ser(o):
    if isinstance(o,pd.DataFrame): return o.to_dict()
    if hasattr(o,'item'): return o.item()
    return str(o)
json.dump(KPI,open(RAW+'/kpi.json','w'),ensure_ascii=False,indent=1,default=ser)
for k,v in KPI.items():
    if not isinstance(v,(pd.DataFrame,dict)): print(k,'=',v)
print('TMI',{k:round(v,1) for k,v in tmi.items()})
