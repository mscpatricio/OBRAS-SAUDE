# -*- coding: utf-8 -*-
"""Estudo 4 - Oncologia, rastreamento e doenças crônicas."""
import sys, os, json, re
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from lib_estudo import *
RAW='/tmp/claude-0/-home-user-OBRAS-SAUDE/c712070a-2954-5409-93ab-21cafbd2988b/scratchpad/raw'
T2=RAW+'/tab2/'; T1=RAW+'/tab/'
OUT='/home/user/OBRAS-SAUDE/estudo-saude-ap/estudos-complementares/e4_oncologia_cronicas'; GR=OUT+'/graficos'
L=lambda n: load(T2+n+'.csv'); L1=lambda n: load(T1+n+'.csv')
pop_uf={}
for r in json.load(open(RAW+'/sidra_pop_uf_all.json'))[1:]: pop_uf.setdefault(r['D1N'],{})[int(r['D3N'])]=int(r['V'])
pop=pop_uf['Amapá']; popbr=pop_uf['Brasil']
# população por sexo e idade (Censo 2022) para alvos de rastreamento
cen={}
for r in json.load(open(RAW+'/sidra_idade_sexo_2022.json'))[1:]:
    cen.setdefault(r['D4N'],{})[r['D5N']]=int(r['V']) if r['V'] not in ('-','...','X') else 0
def ages(sexo,labels): return sum(cen[sexo].get(l,0) for l in labels)
mulheres_50_69=ages('Mulheres',['50 a 54 anos','55 a 59 anos','60 a 64 anos','65 a 69 anos']); mulheres_25_64=ages('Mulheres',['25 a 29 anos','30 a 34 anos','35 a 39 anos','40 a 44 anos','45 a 49 anos','50 a 54 anos','55 a 59 anos','60 a 64 anos'])
def ufname(s): return re.sub(r'^\d\d ','',s)
K={'mulheres_50_69':mulheres_50_69,'mulheres_25_64':mulheres_25_64}; S={}
def add(name,df,title,note=''):
    if df is not None: S[name]=(recorte(df),title,note)
yrs=['2022','2023','2024','2025']; yrs6=yrs+['2026']
def g(df,prefix):
    r=[i for i in df.index if i.startswith(prefix)]; return df.loc[r[0]] if r else None
# ---------- SIM: neoplasias e DCNT ----------
sg=L('e4_sim_grupo_ano'); add('SIM_grupo_cid_ano',sg,'Óbitos de residentes por grupo da CID-10 e ano (todas as causas)')
cap=L1('sim_cap_ano')
K['ob_total']={y:cap.loc['Total',y] for y in yrs}; K['ob_neo']={y:cap.loc['II.  Neoplasias (tumores)',y] for y in yrs}; K['ob_circ']={y:cap.loc['IX.  Doenças do aparelho circulatório',y] for y in yrs}; K['ob_endoc']={y:cap.loc['IV.  Doenças endócrinas nutricionais e metabólicas',y] for y in yrs}; K['ob_resp']={y:cap.loc['X.   Doenças do aparelho respiratório',y] for y in yrs}
K['tx_neo_2024']=K['ob_neo']['2024']/pop[2024]*1e5; K['tx_circ_2024']=K['ob_circ']['2024']/pop[2024]*1e5
neo_groups={'Órgãos digestivos (C15-C26)':'C15-C26','Genitais femininos, incl. colo do útero (C51-C58)':'C51-C58','Aparelho respiratório (C30-C39)':'C30-C39','Genitais masculinos, incl. próstata (C60-C63)':'C60-C63','Tecido linfático e hematopoético (C81-C96)':'C81-C96','Mama (C50)':'C50-C50','Mal definidas/secundárias (C76-C80)':'C76-C80','Olhos, encéfalo e SNC (C69-C72)':'C69-C72','Lábio, cavidade oral e faringe (C00-C14)':'C00-C14','Trato urinário (C64-C68)':'C64-C68','Tecido mesotelial e partes moles (C45-C49)':'C45-C49','Pele (C43-C44)':'C43-C44'}
ng=pd.DataFrame({k:{y:g(sg,v)[y] for y in yrs6} for k,v in neo_groups.items()}).T; ng.index.name='Grupo de neoplasias'; S['SIM_neoplasias_grupo_ano']=(ng,'Óbitos por neoplasias malignas segundo grupo de localização, Amapá, 2022–2026','2025 preliminar; 2026 parcial.'); K['neo_groups']=ng
cs=L('e4_sim_cat_sexo_2025'); cs4=L('e4_sim_cat_sexo_2024')
def topsites(df,n=12):
    rows=[i for i in df.index if re.match(r'^[#@&]?C\d\d',i)]
    d=df.loc[rows,['Masc','Fem','Total']].sort_values('Total',ascending=False).head(n); d.index=[re.sub(r'^[#@&]','',i)[:70] for i in d.index]; return d
ts=topsites(cs); ts4=topsites(cs4); S['SIM_neoplasias_categoria_sexo_2025']=(ts,'Óbitos por neoplasias malignas segundo categoria CID-10 e sexo, 2025 (12 maiores)','Preliminar'); S['SIM_neoplasias_categoria_sexo_2024']=(ts4,'Óbitos por neoplasias malignas segundo categoria CID-10 e sexo, 2024 (12 maiores)',''); K['top_sites_2024']=ts4; K['top_sites_2025']=ts
def catsum(df,codes):
    return sum(df.loc[i,'Total'] for i in df.index if re.sub(r'^[#@&]','',i)[:3] in codes)
K['ob_prost_2024']=catsum(cs4,['C61']); K['ob_colo_2024']=catsum(cs4,['C53']); K['ob_mama_2024']=catsum(cs4,['C50']); K['ob_estom_2024']=catsum(cs4,['C16']); K['ob_pulm_2024']=catsum(cs4,['C34']); K['ob_figado_2024']=catsum(cs4,['C22']); K['ob_colorretal_2024']=catsum(cs4,['C18','C19','C20','C21']); K['ob_iam_2024']=catsum(cs4,['I21']); K['ob_avc_2024']=catsum(cs4,['I60','I61','I62','I63','I64','I67','I69']); K['ob_diab_2024']=catsum(cs4,['E10','E11','E12','E13','E14']); K['ob_hipert_2024']=catsum(cs4,['I10','I11','I12','I13','I15']); K['ob_drc_2024']=catsum(cs4,['N18']); K['ob_dpoc_2024']=catsum(cs4,['J40','J41','J42','J43','J44'])
cf=L('e4_sim_cap_fx_2024'); add('SIM_capitulo_fx_2024',cf,'Óbitos por capítulo CID-10 e faixa etária, 2024'); 
def prem(row): return sum(cf.loc[row,c] for c in ['30 a 39 anos','40 a 49 anos','50 a 59 anos','60 a 69 anos'])
K['prem_circ_3069']=prem('IX.  Doenças do aparelho circulatório'); K['prem_circ_pct']=K['prem_circ_3069']/cf.loc['IX.  Doenças do aparelho circulatório','Total']*100; K['prem_neo_3069']=prem('II.  Neoplasias (tumores)'); K['prem_neo_pct']=K['prem_neo_3069']/cf.loc['II.  Neoplasias (tumores)','Total']*100
cm=L('e4_sim_cap_mun_2024'); add('SIM_capitulo_mun_2024',cm,'Óbitos por município de residência e capítulo CID-10, 2024')
bu=L('e4_bench_sim_uf_cap_2024')
def colp(df,p): c=[x for x in df.columns if x.startswith(p)]; return c[0]
bd=pd.DataFrame({'Óbitos por neoplasias 2024':{ufname(i):bu.loc[i,colp(bu,'Cap II')] for i in bu.index if i!='Total'},'Óbitos por doenças circulatórias 2024':{ufname(i):bu.loc[i,colp(bu,'Cap IX')] for i in bu.index if i!='Total'},'Óbitos totais 2024':{ufname(i):bu.loc[i,'Total'] for i in bu.index if i!='Total'}})
bd['Neoplasias por 100 mil hab.']=[bd.loc[u,'Óbitos por neoplasias 2024']/pop_uf[u][2024]*1e5 for u in bd.index]; bd['Circulatórias por 100 mil hab.']=[bd.loc[u,'Óbitos por doenças circulatórias 2024']/pop_uf[u][2024]*1e5 for u in bd.index]; bd['% neoplasias no total de óbitos']=bd.iloc[:,0]/bd.iloc[:,2]*100
bd.loc['BRASIL']=[bu.loc['Total',colp(bu,'Cap II')],bu.loc['Total',colp(bu,'Cap IX')],bu.loc['Total','Total'],bu.loc['Total',colp(bu,'Cap II')]/popbr[2024]*1e5,bu.loc['Total',colp(bu,'Cap IX')]/popbr[2024]*1e5,bu.loc['Total',colp(bu,'Cap II')]/bu.loc['Total','Total']*100]
bd=bd.sort_values('Neoplasias por 100 mil hab.',ascending=False); S['BENCH_MORTALIDADE_UF_2024']=(bd,'Mortalidade por neoplasias e doenças circulatórias por UF, 2024 (taxas brutas por 100 mil habitantes)','Taxas brutas, não padronizadas por idade: o Amapá tem população jovem, o que reduz as taxas brutas.')
K['bench_neo']=(bd.loc['Amapá','Neoplasias por 100 mil hab.'],bd.loc['BRASIL','Neoplasias por 100 mil hab.'],int(bd.drop('BRASIL')['Neoplasias por 100 mil hab.'].rank(ascending=False)['Amapá'])); K['bench_circ']=(bd.loc['Amapá','Circulatórias por 100 mil hab.'],bd.loc['BRASIL','Circulatórias por 100 mil hab.'],int(bd.drop('BRASIL')['Circulatórias por 100 mil hab.'].rank(ascending=False)['Amapá'])); K['bench_neo_pct']=(bd.loc['Amapá','% neoplasias no total de óbitos'],bd.loc['BRASIL','% neoplasias no total de óbitos'])
# ---------- SIA oncologia ----------
of=L('e4_onco_forma_ano_qtd'); ofv=L('e4_onco_forma_ano_valor'); add('SIA_onco_forma_ano_qtd',of,'Procedimentos de oncologia (APAC) por forma de organização e ano: quantidade'); add('SIA_onco_forma_ano_valor',ofv,'Procedimentos de oncologia por forma de organização e ano: valor (R$)')
K['onco_qtd']={y:of.loc['Total',y] for y in yrs6}; K['onco_val']={y:ofv.loc['Total',y] for y in yrs6}; K['radio_qtd']={y:g(of,'030401')[y] for y in yrs6}; K['radio_val']={y:g(ofv,'030401')[y] for y in yrs6}; K['quimio_pal']={y:g(of,'030402')[y] for y in yrs6}; K['quimio_adj']={y:g(of,'030405')[y] for y in yrs6}; K['quimio_inf']={y:g(of,'030407')[y] for y in yrs6}
ofx=L('e4_onco_fx_ano'); add('SIA_onco_fx_ano',ofx,'Procedimentos de oncologia por faixa etária e ano'); K['onco_fx_0_19_2025']=sum(ofx.loc[r,'2025'] for r in ['Menor 1 ano','1 a 4 anos','5 a 9 anos','10 a 14 anos','15 a 19 anos'])
add('SIA_onco_sexo_ano_valor',L('e4_onco_sexo_ano_valor'),'Valor dos procedimentos de oncologia por sexo e ano'); add('SIA_onco_mun_ano',L('e4_onco_mun_ano_qtd'),'Procedimentos de oncologia por município de residência do paciente e ano'); op=L('e4_onco_proc_2025'); add('SIA_onco_proc_2025',op,'Procedimentos de oncologia por procedimento, 2025')
K['onco_top_2025']=op.drop('Total').sort_values('Valor aprovado',ascending=False).head(10)
om=L('e4_onco_mun_ano_qtd'); K['onco_macapa_pct_2025']=om.loc['160030 MACAPA','2025']/om.loc['Total','2025']*100
# rastreamento
mr=L('e4_mamo_rastr_fx_ano'); md=L('e4_mamo_diag_fx_ano'); ci=L('e4_cito_fx_ano')
add('SIA_mamografia_rastreamento_fx_ano',mr,'Mamografias bilaterais para rastreamento por faixa etária e ano'); add('SIA_mamografia_diagnostica_fx_ano',md,'Mamografias diagnósticas por faixa etária e ano'); add('SIA_citopatologico_fx_ano',ci,'Exames citopatológicos cérvico-vaginais por faixa etária e ano')
def rng(df,labels,y): return sum(df.loc[l,y] for l in labels if l in df.index)
K['mamo_5069']={y:rng(mr,['50 a 54 anos','55 a 59 anos','60 a 64 anos','65 a 69 anos'],y) for y in yrs6}; K['mamo_tot']={y:mr.loc['Total',y] for y in yrs6}; K['mamo_4049']={y:rng(mr,['40 a 44 anos','45 a 49 anos'],y) for y in yrs6}
K['cito_2564']={y:rng(ci,['25 a 29 anos','30 a 34 anos','35 a 39 anos','40 a 44 anos','45 a 49 anos','50 a 54 anos','55 a 59 anos','60 a 64 anos'],y) for y in yrs6}; K['cito_tot']={y:ci.loc['Total',y] for y in yrs6}
# razão de rastreamento: exames na faixa-alvo / (população-alvo / periodicidade) -> mamografia bienal (alvo/2), citologia trienal (alvo/3)
K['razao_mamo']={y:K['mamo_5069'][y]/(mulheres_50_69/2) for y in yrs}; K['razao_cito']={y:K['cito_2564'][y]/(mulheres_25_64/3) for y in yrs}
ras=pd.DataFrame({'Mamografias de rastreamento (total)':K['mamo_tot'],'Mamografias de rastreamento em mulheres de 50 a 69 anos':K['mamo_5069'],'Mamografias de rastreamento em mulheres de 40 a 49 anos':K['mamo_4049'],'Razão de mamografias 50–69 (exames / metade da população-alvo)':{**K['razao_mamo'],'2026':None},'Citopatológicos (total)':K['cito_tot'],'Citopatológicos em mulheres de 25 a 64 anos':K['cito_2564'],'Razão de citopatológicos 25–64 (exames / terço da população-alvo)':{**K['razao_cito'],'2026':None}}).T
S['RASTREAMENTO_indicadores']=(ras,'Indicadores de rastreamento do câncer de mama e do colo do útero, Amapá, 2022–2026','População-alvo do Censo 2022: %s mulheres de 50 a 69 anos e %s de 25 a 64 anos. Razão = 1,0 indica cobertura compatível com a periodicidade recomendada.'%(fmt_int(mulheres_50_69),fmt_int(mulheres_25_64)))
# ---------- SIH ----------
ss=L('e4_sih_subgrupo_ano_aih'); ssv=L('e4_sih_subgrupo_ano_valor'); add('SIH_subgrupo_ano_aih',ss,'AIH por subgrupo de procedimento e ano'); add('SIH_subgrupo_ano_valor',ssv,'Valor das AIH por subgrupo de procedimento e ano')
K['sih_onco_clin']={y:g(ss,'0304')[y] for y in yrs6}; K['sih_onco_cir']={y:g(ss,'0416')[y] for y in yrs6}; K['sih_nefro']={y:g(ss,'0305')[y] for y in yrs6}; K['sih_onco_cir_val']={y:g(ssv,'0416')[y] for y in yrs6}
c2=L('e4_nih_lista_capII_2025'); add('SIH_neoplasias_lista_2025',c2,'Internações por neoplasias segundo lista de morbidade, 2025'); c2a=L('e4_nih_lista_capII_ano'); add('SIH_neoplasias_lista_ano',c2a,'Internações por neoplasias segundo lista de morbidade e ano')
K['int_neo']={y:c2a.loc['Total',y] for y in yrs6}; K['int_leio']={y:g(c2a,'.. Leiomioma')[y] for y in yrs6}; K['int_benig_incert']={y:g(c2a,'.. Outr neopl in situ')[y] for y in yrs6}
K['int_malig_2025']=K['int_neo']['2025']-K['int_leio']['2025']-K['int_benig_incert']['2025']-g(c2a,'.. Neoplasia benigna da mama')['2025']-g(c2a,'.. Neoplasia benigna da pele')['2025']-g(c2a,'.. Neoplasia benigna do ovário')['2025']-g(c2a,'.. Neopl benig encéfalo')['2025']-g(c2a,'.. Neoplasia benigna dos órgãos urinários')['2025']
K['int_neo_ob_2025']=c2.loc['Total','Óbitos']; K['int_neo_tm_2025']=c2.loc['Total','Taxa mortalidade']
ce=L('e4_nih_capII_estab_ano'); add('SIH_neoplasias_estab_ano',ce,'Internações por neoplasias por estabelecimento e ano'); 
def est(name): r=[i for i in ce.index if name in i]; return {y:ce.loc[r[0],y] for y in yrs6} if r else None
K['int_neo_hcal']=est('ALBERTO LIMA'); K['int_neo_scamilo']=est('SAO CAMILO'); K['int_neo_hu']=est('UNIVERSITARIO'); K['int_neo_ml']=est('MARIA LUCIA')
c9=L('e4_nih_lista_capIX_ano'); add('SIH_circulatorias_lista_ano',c9,'Internações por doenças do aparelho circulatório segundo lista de morbidade e ano'); K['int_iam']={y:g(c9,'.. Infarto agudo')[y] for y in yrs6}; K['int_avc']={y:g(c9,'.. Acid vascular cerebr não espec')[y]+g(c9,'.. Hemorragia intracraniana')[y]+g(c9,'.. Infarto cerebral')[y] for y in yrs6}; K['int_ic']={y:g(c9,'.. Insuficiência cardíaca')[y] for y in yrs6}; K['int_flebite']={y:g(c9,'.. Flebite')[y] for y in yrs6}; K['int_isq']={y:g(c9,'.. Outras doenças isquêmicas')[y] for y in yrs6}; K['int_arrit']={y:g(c9,'.. Transtornos de condução')[y] for y in yrs6}
c4=L('e4_nih_lista_capIV_ano'); add('SIH_endocrinas_lista_ano',c4,'Internações por doenças endócrinas e metabólicas segundo lista de morbidade e ano'); K['int_diab']={y:g(c4,'.. Diabetes')[y] for y in yrs6}; K['int_obes']={y:g(c4,'.. Obesidade')[y] for y in yrs6}
# ---------- Nefrologia ----------
nf=L('e4_nefro_fx_ano'); npr=L('e4_nefro_proc_ano_qtd'); add('SIA_nefrologia_fx_ano',nf,'Procedimentos de nefrologia (diálise) por faixa etária e ano'); add('SIA_nefrologia_proc_ano',npr,'Procedimentos de nefrologia por procedimento e ano')
K['hd_sessoes']={y:g(npr,'0305010107')[y]+g(npr,'0305010115')[y]+g(npr,'0305010093')[y]+g(npr,'0305010123')[y] for y in yrs6}; K['hd_pacientes_eq']={y:K['hd_sessoes'][y]/156 for y in yrs}; K['dp']={y:g(npr,'0305010166')[y] for y in yrs6}; K['nefro_val']={y:L1('sia_subgrupo_ano_valor').loc['0305 Tratamento em nefrologia',y] for y in yrs6}
K['hd_pmp_2025']=K['hd_pacientes_eq']['2025']/pop[2025]*1e6; K['nefro_60mais_pct_2025']=sum(nf.loc[r,'2025'] for r in ['60 a 64 anos','65 a 69 anos','70 a 74 anos','75 a 79 anos','80 anos e mais'])/nf.loc['Total','2025']*100
eq=L1('cnes_equip_grupo_ano'); K['equip_dialise']={c:eq.loc['Dialise',c] for c in ('2025/Dez','2026/Set')}
hb=L('e2_hab_latest'); K['hab_hd']=sum(hb.loc[i,'Qtde Estabelec. Habilitados'] for i in hb.index if 'HEMODIALISE' in i); K['hab_unacon']=sum(hb.loc[i,'Qtde Estabelec. Habilitados'] for i in hb.index if 'UNACON' in i or 'CACON' in i)
# ---------- Painel ----------
pr=pd.DataFrame([
 ['Óbitos por neoplasias (SIM)']+[K['ob_neo'][y] for y in yrs]+[None,'Taxa bruta 2024: %s/100 mil'%fmt_br(K['tx_neo_2024'],1)],
 ['Óbitos por doenças do aparelho circulatório (SIM)']+[K['ob_circ'][y] for y in yrs]+[None,'Taxa bruta 2024: %s/100 mil'%fmt_br(K['tx_circ_2024'],1)],
 ['Óbitos por doenças endócrinas/diabetes (SIM)']+[K['ob_endoc'][y] for y in yrs]+[None,''],
 ['Procedimentos de oncologia (APAC, SIA)']+[K['onco_qtd'][y] for y in yrs6]+['Valor 2025: R$ %s mi'%fmt_br(K['onco_val']['2025']/1e6,1)],
 ['Radioterapia (procedimentos)']+[K['radio_qtd'][y] for y in yrs6]+['Centro de Radioterapia do Amapá desde dez/2025'],
 ['Mamografias de rastreamento em mulheres de 50–69 anos']+[K['mamo_5069'][y] for y in yrs6]+['Razão 2025: %s'%fmt_br(K['razao_mamo']['2025'],2)],
 ['Citopatológicos em mulheres de 25–64 anos']+[K['cito_2564'][y] for y in yrs6]+['Razão 2025: %s'%fmt_br(K['razao_cito']['2025'],2)],
 ['Internações por neoplasias (SIH)']+[K['int_neo'][y] for y in yrs6]+['Óbitos hospitalares 2025: %d'%int(K['int_neo_ob_2025'])],
 ['Internações por AVC (SIH)']+[K['int_avc'][y] for y in yrs6]+[''],
 ['Internações por infarto agudo do miocárdio (SIH)']+[K['int_iam'][y] for y in yrs6]+[''],
 ['Internações por diabetes (SIH)']+[K['int_diab'][y] for y in yrs6]+[''],
 ['Sessões de hemodiálise (SIA)']+[K['hd_sessoes'][y] for y in yrs6]+['≈ %d pacientes em programa (2025)'%int(K['hd_pacientes_eq']['2025'])],
],columns=['Indicador','2022','2023','2024','2025','2026 (parcial)','Observação']).set_index('Indicador')
S={'00_Painel_Onco_DCNT':(pr,'Painel-resumo: oncologia, rastreamento e doenças crônicas, Amapá, 2022–2026','SIM, SIA, SIH, CNES/DATASUS. 2025 preliminar; 2026 parcial.'),**S}
fontes=[('SIM (TABNET)','sim/cnv/obt10ap.def; obt10uf.def','Óbitos por residência; 2025 preliminar.'),('SIA/SUS por faixa etária e sexo','sia/cnv/qbap.def (procedimentos 0204030188, 0204030030, 0203010086, 0203010019; subgrupos 0304 e 0305)','Local de atendimento.'),('SIH/SUS','sih/cnv/qiap.def; niap.def (capítulos II, IV e IX)','Local de internação.'),('CNES','habap.def; equipoap.def','Habilitações e equipamentos de diálise.'),('IBGE','Censo 2022 (SIDRA 9514) e estimativas (6579)','Populações-alvo e denominadores.'),('Limitações','Painel-Oncologia/SISCAN (tempo até o tratamento, estadiamento), registros de câncer de base populacional e hospitalar, e dados de hipertensos/diabéticos cadastrados (e-SUS APS) não acessíveis.','Solicitar à SESA e ao UNACON.')]
write_workbook(OUT+'/Tabelas_Oncologia_Cronicas_Amapa_2022_2026.xlsx',S,'Oncologia, rastreamento e doenças crônicas não transmissíveis no Amapá, 2022–2026','Estudo complementar para a transição 2026/2027. Extração em 07/11/2026.',fontes)
# gráficos
xs=['2022','2023','2024','2025','2026*']
lines(['2022','2023','2024','2025'],{'Aparelho circulatório':[K['ob_circ'][y] for y in yrs],'Neoplasias':[K['ob_neo'][y] for y in yrs],'Aparelho respiratório':[K['ob_resp'][y] for y in yrs],'Endócrinas (diabetes)':[K['ob_endoc'][y] for y in yrs]},GR+'/f01_obitos_dcnt.png','Óbitos de residentes',legend_cols=2)
t=ts4['Total'].sort_values(); hbars([i[:45] for i in t.index],list(t.values),GR+'/f02_neoplasias_sitio.png','Óbitos, 2024',fs=8)
ngp=ng['2025'].sort_values().tail(8); hbars([i[:48] for i in ngp.index],list(ngp.values),GR+'/f03_neoplasias_grupo.png','Óbitos, 2025 (preliminar)',fs=8)
stacked(xs,{'Quimioterapia paliativa':[K['quimio_pal'][y] for y in yrs6],'Quimioterapia adjuvante':[K['quimio_adj'][y] for y in yrs6],'Quimioterapia infantojuvenil':[K['quimio_inf'][y] for y in yrs6],'Radioterapia':[K['radio_qtd'][y] for y in yrs6],'Outras':[K['onco_qtd'][y]-K['quimio_pal'][y]-K['quimio_adj'][y]-K['quimio_inf'][y]-K['radio_qtd'][y] for y in yrs6]},GR+'/f04_onco_apac.png','Procedimentos (APAC)')
lines(['2022','2023','2024','2025'],{'Mamografias 50–69 anos':[K['mamo_5069'][y] for y in yrs],'Citopatológicos 25–64 anos':[K['cito_2564'][y] for y in yrs]},GR+'/f05_rastreamento.png','Exames (SIA)')
lines(xs,{'AVC':[K['int_avc'][y] for y in yrs6],'Infarto agudo do miocárdio':[K['int_iam'][y] for y in yrs6],'Insuficiência cardíaca':[K['int_ic'][y] for y in yrs6],'Diabetes':[K['int_diab'][y] for y in yrs6],'Arritmias':[K['int_arrit'][y] for y in yrs6]},GR+'/f06_int_cronicas.png','Internações (SIH)',legend_cols=3)
bars(xs,[K['hd_sessoes'][y] for y in yrs6],GR+'/f07_hemodialise.png','Sessões de hemodiálise (SIA)')
b2=bd.drop('BRASIL')['Neoplasias por 100 mil hab.'].sort_values(); hbars(list(b2.index)+['BRASIL'],list(b2.values)+[bd.loc['BRASIL','Neoplasias por 100 mil hab.']],GR+'/f08_bench_neo.png','Óbitos por neoplasias por 100 mil hab. (taxa bruta), 2024',highlight=['Amapá','BRASIL'],figsize=(9,6.5),fmt=lambda v:fmt_br(v,1),fs=8)
json.dump({k:v for k,v in K.items() if not isinstance(v,pd.DataFrame)},open(RAW+'/kpi_e4.json','w'),ensure_ascii=False,indent=1,default=lambda o:o.item() if hasattr(o,'item') else str(o))
for k,v in K.items():
    if isinstance(v,pd.DataFrame): print(k); print(v.round(1).to_string()); continue
    print(k,'=',v if not isinstance(v,dict) else {a:(round(b,2) if isinstance(b,float) else b) for a,b in v.items()})
