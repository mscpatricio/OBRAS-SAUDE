# -*- coding: utf-8 -*-
"""Estudo 1 - Vigilância em saúde: planilha, gráficos e indicadores."""
import sys, os, json, re
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from lib_estudo import *
RAW='/tmp/claude-0/-home-user-OBRAS-SAUDE/c712070a-2954-5409-93ab-21cafbd2988b/scratchpad/raw'
T2=RAW+'/tab2/'; T1=RAW+'/tab/'
OUT='/home/user/OBRAS-SAUDE/estudo-saude-ap/estudos-complementares/e1_vigilancia'; GR=OUT+'/graficos'
L=lambda n: load(T2+n+'.csv')
pop_uf={}
for r in json.load(open(RAW+'/sidra_pop_uf_all.json'))[1:]: pop_uf.setdefault(r['D1N'],{})[int(r['D3N'])]=int(r['V'])
pop=pop_uf['Amapá']; popbr=pop_uf['Brasil']
pop_mun={}
for r in json.load(open(RAW+'/sidra_pop_mun.json'))[1:]: pop_mun.setdefault(r['D1N'].replace(' - AP','').upper(),{})[int(r['D3N'])]=int(r['V'])
def ufname(s): return re.sub(r'^\d\d ','',s)
K={}; S={}
def add(name,df,title,note='2026 parcial; dados do SINAN sujeitos a atualização.'):
    if df is not None: S[name]=(recorte(df),title,note)
def col(df,y): 
    y=str(y); return df[y] if y in df.columns else None
yrs=['2022','2023','2024','2025']
# ---- Tuberculose ----
tb=L('e1_tb_mun_ano'); add('TB_mun_ano',tb,'Tuberculose: casos (todas as formas) por município de residência e ano de diagnóstico')
for n,t in [('e1_tb_fx_ano','por faixa etária'),('e1_tb_sexo_ano','por sexo'),('e1_tb_entrada_ano','por tipo de entrada'),('e1_tb_forma_ano','por forma clínica'),('e1_tb_hiv_ano','por resultado do teste de HIV'),('e1_tb_encerr_ano','por situação de encerramento'),('e1_tb_ppl_ano','entre população privada de liberdade (PPL)')]:
    add('TB_'+n[6:],L(n),'Tuberculose: casos '+t+' e ano de diagnóstico')
K['tb']={y:tb.loc['Total',y] for y in yrs}
K['tb_inc']={y:tb.loc['Total',y]/pop[int(y)]*1e5 for y in ('2024','2025')}
enc=L('e1_tb_encerr_ano'); K['tb_cura_2024']=enc.loc['Cura','2024']/enc.loc['Total','2024']*100; K['tb_aband_2024']=enc.loc['Abandono','2024']/enc.loc['Total','2024']*100; K['tb_cura_2023']=enc.loc['Cura','2023']/enc.loc['Total','2023']*100; K['tb_aband_2023']=enc.loc['Abandono','2023']/enc.loc['Total','2023']*100; K['tb_obito_2024']=enc.loc['Óbito por tuberculose','2024']
hiv=L('e1_tb_hiv_ano'); K['tb_hiv_2024']=hiv.loc['Positivo','2024']; K['tb_hiv_2025']=hiv.loc['Positivo','2025']; K['tb_hiv_pct_2025']=hiv.loc['Positivo','2025']/hiv.loc['Total','2025']*100; K['tb_hivnr_2022']=hiv.loc['Não realizado','2022']; K['tb_hivnr_2025']=hiv.loc['Não realizado','2025']
ppl=L('e1_tb_ppl_ano'); K['tb_ppl_2025']=ppl.loc['Sim','2025']; K['tb_ppl_pct_2025']=ppl.loc['Sim','2025']/ppl.loc['Total','2025']*100
ent=L('e1_tb_entrada_ano'); K['tb_novos_2025']=ent.loc['CASO NOVO','2025']; K['tb_reingresso_2025']=ent.loc['REINGRESSO APÓS ABANDONO','2025']; K['tb_reingresso_2022']=ent.loc['REINGRESSO APÓS ABANDONO','2022']
K['tb_macapa_2025']=tb.loc['160030 MACAPA','2025']; K['tb_macapa_pct']=K['tb_macapa_2025']/tb.loc['Total','2025']*100; K['tb_macapa_inc_2025']=K['tb_macapa_2025']/pop_mun['MACAPÁ'][2025]*1e5
K['tb_santana_inc_2025']=tb.loc['160060 SANTANA','2025']/pop_mun['SANTANA'][2025]*1e5 if '160060 SANTANA' in tb.index else None
btb=L('e1_bench_tb_uf_ano')
bt=pd.DataFrame({'Casos 2025':{ufname(i):btb.loc[i,'2025'] for i in btb.index if i!='Total'}}); bt['Incidência 2025 (por 100 mil hab.)']=[bt.loc[u,'Casos 2025']/pop_uf[u][2025]*1e5 for u in bt.index]; bt.loc['BRASIL']=[btb.loc['Total','2025'],btb.loc['Total','2025']/popbr[2025]*1e5]
bt=bt.sort_values('Incidência 2025 (por 100 mil hab.)',ascending=False); K['tb_rank']=int(list(bt.drop('BRASIL').index).index('Amapá')+1); K['tb_br_inc']=bt.loc['BRASIL','Incidência 2025 (por 100 mil hab.)']
# ---- Hanseníase ----
hs=L('e1_hans_mun_ano'); add('HANS_mun_ano',hs,'Hanseníase: casos novos por município de residência e ano de diagnóstico')
for n,t in [('e1_hans_classe_ano','classe operacional'),('e1_hans_incap_ano','grau de incapacidade física no diagnóstico'),('e1_hans_fx_ano','faixa etária'),('e1_hans_deteccao_ano','modo de detecção'),('e1_hans_saida_ano','tipo de saída')]:
    add('HANS_'+n[8:],L(n),'Hanseníase: casos novos por '+t+' e ano de diagnóstico')
K['hans']={y:hs.loc['Total',y] for y in yrs}; K['hans_det_2025']=hs.loc['Total','2025']/pop[2025]*1e5; K['hans_det_2024']=hs.loc['Total','2024']/pop[2024]*1e5
inc=L('e1_hans_incap_ano'); K['hans_g2_2025']=inc.loc['GRAU II','2025']; K['hans_g2_pct_2025']=inc.loc['GRAU II','2025']/(inc.loc['Total','2025']-inc.loc['Não AVALIADO','2025']-inc.loc['Em Branco','2025'])*100
cl=L('e1_hans_classe_ano'); K['hans_mb_pct_2025']=cl.loc['MULTIBACILAR','2025']/cl.loc['Total','2025']*100
fx=L('e1_hans_fx_ano'); K['hans_crianca_2025']=fx.loc['0 a 14 anos','2025']
det=L('e1_hans_deteccao_ano'); K['hans_contatos_2025']=det.loc['EXAME CONTATOS','2025']
bh=L('e1_bench_hans_uf_ano')
if bh is not None:
    bhd=pd.DataFrame({'Casos novos 2025':{ufname(i):bh.loc[i,'2025'] for i in bh.index if i!='Total'}}); bhd['Detecção 2025 (por 100 mil hab.)']=[bhd.loc[u,'Casos novos 2025']/pop_uf[u][2025]*1e5 for u in bhd.index]; bhd.loc['BRASIL']=[bh.loc['Total','2025'],bh.loc['Total','2025']/popbr[2025]*1e5]
    bhd=bhd.sort_values('Detecção 2025 (por 100 mil hab.)',ascending=False); K['hans_rank']=int(list(bhd.drop('BRASIL').index).index('Amapá')+1); K['hans_br']=bhd.loc['BRASIL','Detecção 2025 (por 100 mil hab.)']
else: bhd=None
# ---- Sífilis ----
sc=L('e1_sifc_mun_ano'); add('SIFC_mun_ano',sc,'Sífilis congênita: casos por município de residência e ano de diagnóstico')
for n,t in [('e1_sifc_prenatal_ano','realização de pré-natal pela mãe'),('e1_sifc_classif_ano','classificação final'),('e1_sifc_fxmae_ano','faixa etária da mãe'),('e1_sifc_parceiro_ano','tratamento do parceiro')]:
    add('SIFC_'+n[8:],L(n),'Sífilis congênita: casos por '+t+' e ano')
sg=L('e1_sifg_mun_ano'); add('SIFG_mun_ano',sg,'Sífilis em gestantes: casos por município de residência e ano de diagnóstico')
add('SIFG_fx_ano',L('e1_sifg_fx_ano'),'Sífilis em gestantes: casos por faixa etária e ano'); add('SIFG_classif_ano',L('e1_sifg_classif_ano'),'Sífilis em gestantes: casos por classificação clínica e ano')
nv=load(T1+'sinasc_ano.csv'); nvy={y:nv.loc[y,'Nascim p/resid.mãe'] for y in yrs}
K['sifc']={y:sc.loc['Total',y] for y in yrs}; K['sifc_tx']={y:sc.loc['Total',y]/nvy[y]*1000 for y in yrs}
K['sifg']={y:sg.loc['Total',y] for y in yrs}; K['sifg_tx']={y:sg.loc['Total',y]/nvy[y]*1000 for y in yrs}
pn=L('e1_sifc_prenatal_ano'); K['sifc_pn_sim_2024']=pn.loc['Sim','2024']/pn.loc['Total','2024']*100
pa=L('e1_sifc_parceiro_ano'); K['sifc_parc_2024']=pa.loc['Sim','2024']/pa.loc['Total','2024']*100
fm=L('e1_sifc_fxmae_ano'); K['sifc_mae_adol_2024']=(fm.loc['10-14','2024']+fm.loc['15-19','2024'])/fm.loc['Total','2024']*100
sfx=L('e1_sifg_fx_ano'); K['sifg_adol_2024']=(sfx.loc['10-14','2024']+sfx.loc['15-19','2024'])/sfx.loc['Total','2024']*100
K['sifc_macapa_2024']=sc.loc['160030 MACAPA','2024']
bs=L('e1_bench_sifc_uf_ano'); bnv=load(T1+'bench_sinasc_uf_ano.csv')
bsd=pd.DataFrame({'Casos 2024':{ufname(i):bs.loc[i,'2024'] for i in bs.index if i!='Total'}})
bsd['Nascidos vivos 2024']=[bnv.loc[[j for j in bnv.index if ufname(j)==u][0],'2024'] for u in bsd.index]
bsd['Incidência 2024 (por mil NV)']=bsd['Casos 2024']/bsd['Nascidos vivos 2024']*1000
bsd.loc['BRASIL']=[bs.loc['Total','2024'],bnv.loc['Total','2024'],bs.loc['Total','2024']/bnv.loc['Total','2024']*1000]
bsd=bsd.sort_values('Incidência 2024 (por mil NV)',ascending=False); K['sifc_rank']=int(list(bsd.drop('BRASIL').index).index('Amapá')+1); K['sifc_br']=bsd.loc['BRASIL','Incidência 2024 (por mil NV)']
# ---- Arboviroses ----
dg=L('e1_deng_mun_ano'); add('DENGUE_mun_ano',dg,'Dengue: casos prováveis por município de residência e ano de início dos sintomas')
for n,t in [('e1_deng_class_ano','classificação final'),('e1_deng_evol_ano','evolução'),('e1_deng_hosp_ano','ocorrência de hospitalização'),('e1_deng_fx_ano','faixa etária')]:
    add('DENGUE_'+n[8:],L(n),'Dengue: casos prováveis por '+t+' e ano')
K['deng']={y:dg.loc['Total',y] for y in yrs+['2026']}; K['deng_inc_2024']=dg.loc['Total','2024']/pop[2024]*1e5
ev=L('e1_deng_evol_ano'); K['deng_ob_2024']=ev.loc['Óbito pelo agravo notificado','2024']; K['deng_ob_2025']=ev.loc['Óbito pelo agravo notificado','2025']
ho=L('e1_deng_hosp_ano'); K['deng_hosp_2024']=ho.loc['Sim','2024']
cf=L('e1_deng_class_ano'); K['deng_alarme_2024']=cf.loc['Dengue com sinais de alarme','2024']; K['deng_grave_2024']=cf.loc['Dengue grave','2024']
K['deng_mun_2024']={nome_mun(i):dg.loc[i,'2024'] for i in dg.index if i!='Total'}
ch=L('e1_chik_class_ano'); zk=L('e1_zika_class_ano')
add('CHIK_class_ano',ch,'Chikungunya: casos notificados por classificação final e ano'); add('ZIKA_class_ano',zk,'Zika: casos notificados por classificação final e ano'); add('CHIK_mun_ano',L('e1_chik_mun_ano'),'Chikungunya: casos notificados por município de residência e ano'); add('ZIKA_mun_ano',L('e1_zika_mun_ano'),'Zika: casos notificados por município de residência e ano')
K['chik_conf']={y:ch.loc['Chikungunya',y] for y in yrs+['2026']} if ch is not None else {}
K['zika_conf']={y:zk.loc['Confirmado',y] for y in yrs+['2026']} if zk is not None else {}
arbo=pd.DataFrame({'Dengue (casos prováveis)':K['deng'],'Chikungunya (confirmados)':K['chik_conf'],'Zika (confirmados)':K['zika_conf']}).T
# ---- Leishmanioses / meningite / malária ----
lta=L('e1_lta_mun_ano'); add('LTA_mun_ano',lta,'Leishmaniose tegumentar: casos confirmados por município de residência e ano de notificação'); add('LTA_forma_ano',L('e1_lta_forma_ano'),'Leishmaniose tegumentar: casos por forma clínica e ano')
add('LV_mun_ano',L('e1_lv_mun_ano'),'Leishmaniose visceral: casos confirmados por município e ano')
K['lta']={y:lta.loc['Total',y] for y in yrs}; K['lta_inc_2024']=lta.loc['Total','2024']/pop[2024]*1e5; K['lta_inc_2025']=lta.loc['Total','2025']/pop[2025]*1e5
K['lta_mun_2024']={nome_mun(i):lta.loc[i,'2024'] for i in lta.index if i!='Total'}
K['lta_oiap_inc_2024']=lta.loc['160050 OIAPOQUE','2024']/pop_mun['OIAPOQUE'][2024]*1e5
mn=L('e1_men_etio_ano'); me=L('e1_men_evol_ano'); add('MENING_etio_ano',mn,'Meningites: casos confirmados por etiologia e ano'); add('MENING_evol_ano',me,'Meningites: casos por evolução e ano')
K['men']={y:mn.loc['Total',y] for y in yrs+['2026']}; K['men_ob']={y:me.loc['Óbito por meningite',y] for y in yrs+['2026']}
add('MALARIA_SINAN_mun_ano',L('e1_mal_mun_ano'),'Malária (SINAN, registros residuais): casos por município e ano','A malária na Amazônia Legal é registrada no SIVEP-Malária, não disponível no TABNET; o SINAN capta apenas registros residuais.')
# ---- Animais peçonhentos / intoxicações ----
an=L('e1_anim_tipo_ano'); add('ANIMAIS_tipo_ano',an,'Acidentes por animais peçonhentos: notificações por tipo de animal e ano')
add('ANIMAIS_mun_ano',L('e1_anim_mun_ano'),'Acidentes por animais peçonhentos: notificações por município de residência e ano'); add('ANIMAIS_tipo_mun_2025',L('e1_anim_tipo_mun_2025'),'Acidentes por animais peçonhentos por município e tipo, 2025'); add('ANIMAIS_evol_ano',L('e1_anim_evol_ano'),'Acidentes por animais peçonhentos: evolução por ano'); add('ANIMAIS_tempo_ano',L('e1_anim_tempo_ano'),'Acidentes por animais peçonhentos: tempo entre picada e atendimento, por ano'); add('ANIMAIS_fx_ano',L('e1_anim_fx_ano'),'Acidentes por animais peçonhentos por faixa etária e ano')
K['anim']={y:an.loc['Total',y] for y in yrs+['2026']}; K['anim_serp_2025']=an.loc['Serpente','2025']; K['anim_esc_2025']=an.loc['Escorpião','2025']; K['anim_esc_2022']=an.loc['Escorpião','2022']
ae=L('e1_anim_evol_ano'); K['anim_ob_2025']=ae.loc['Óbito pelo agravo notificado','2025']; K['anim_ob_2224']=sum(ae.loc['Óbito pelo agravo notificado',y] for y in yrs)
at=L('e1_anim_tempo_ano'); K['anim_24h_2025']=at.loc['24 e + horas','2025']; K['anim_6h_pct_2025']=(at.loc['6 a 12 horas','2025']+at.loc['12 a 24 horas','2025']+at.loc['24 e + horas','2025'])/at.loc['Total','2025']*100
am=L('e1_anim_tipo_mun_2025'); K['anim_laranjal_2025']=am.loc['160027 LARANJAL DO JARI','Total']; K['anim_laranjal_esc']=am.loc['160027 LARANJAL DO JARI','Escorpião']; K['anim_laranjal_inc']=K['anim_laranjal_2025']/pop_mun['LARANJAL DO JARI'][2025]*1e5
K['anim_oiap_outros']=am.loc['160050 OIAPOQUE','Outros']
ix=L('e1_intox_circ_ano'); add('INTOX_circ_ano',ix,'Intoxicações exógenas: notificações por circunstância e ano'); add('INTOX_agente_ano',L('e1_intox_agente_ano'),'Intoxicações exógenas: notificações por grupo do agente tóxico e ano'); add('INTOX_evol_ano',L('e1_intox_evol_ano'),'Intoxicações exógenas: evolução por ano'); add('INTOX_mun_ano',L('e1_intox_mun_ano'),'Intoxicações exógenas por município de residência e ano'); add('INTOX_fx_ano',L('e1_intox_fx_ano'),'Intoxicações exógenas por faixa etária e ano'); add('INTOX_circ_fx_2025',L('e1_intox_circ_fx_2025'),'Intoxicações exógenas por circunstância e faixa etária, 2025')
K['intox']={y:ix.loc['Total',y] for y in yrs+['2026']}; K['intox_suic']={y:ix.loc['Tentativa de suicídio',y] for y in yrs+['2026']}; K['intox_amb_2024']=ix.loc['Ambiental','2024']
ag=L('e1_intox_agente_ano'); K['intox_metal_2024']=ag.loc['Metal','2024']; K['intox_med_2024']=ag.loc['Medicamento','2024']
im=L('e1_intox_mun_ano'); K['intox_oiap_2024']=im.loc['160050 OIAPOQUE','2024']
hp=L('e1_hep_etio_ano'); add('HEPATITES_etio_ano',hp,'Hepatites virais: casos confirmados por classificação etiológica e ano (até 2023)','Base do SINAN para o Amapá sem classificação etiológica preenchida (100% ignorado/branco).')
K['hep_2023']=hp.loc['Total','2023'] if hp is not None else None
# ---- SIM ----
sg_=L('e1_sim_grupo_ano'); add('SIM_grupo_ano',sg_,'Óbitos de residentes por grupo da CID-10 e ano (capítulos I e II em destaque)')
sc_=L('e1_sim_cat_ano'); add('SIM_cat_ano',sc_,'Óbitos de residentes por categoria da CID-10 e ano')
def g(label): 
    r=[i for i in sg_.index if i.startswith(label)]; return sg_.loc[r[0]] if r else None
simsel={'Tuberculose (A15-A19)':g('A15-A19'),'HIV/aids (B20-B24)':g('B20-B24'),'Outras doenças bacterianas, incl. sepse (A30-A49)':g('A30-A49'),'Arboviroses (A90-A99)':g('A90-A99'),'Hepatites virais (B15-B19)':g('B15-B19'),'Protozooses, incl. malária (B50-B64)':g('B50-B64'),'Doenças infecciosas intestinais (A00-A09)':g('A00-A09'),'IST (A50-A64)':g('A50-A64')}
simt=pd.DataFrame({k:v for k,v in simsel.items() if v is not None}).T[[c for c in ['2022','2023','2024','2025','2026'] if c in sg_.columns]]
simt.index.name='Grupo de causas'; S['SIM_infecciosas_sel']=(simt,'Óbitos de residentes por doenças infecciosas selecionadas, 2022–2026 (SIM)','2025 preliminar; 2026 parcial.')
K['sim_tb']={y:simt.loc['Tuberculose (A15-A19)',y] for y in yrs}; K['sim_hiv']={y:simt.loc['HIV/aids (B20-B24)',y] for y in yrs}; K['sim_hiv_tx_2025']=simt.loc['HIV/aids (B20-B24)','2025']/pop[2025]*1e5; K['sim_mal']={y:simt.loc['Protozooses, incl. malária (B50-B64)',y] for y in yrs}; K['sim_arbo_2024']=simt.loc['Arboviroses (A90-A99)','2024']
# ---- Painel resumo ----
pr=pd.DataFrame([
 ['Tuberculose (casos, todas as formas)',K['tb']['2022'],K['tb']['2023'],K['tb']['2024'],K['tb']['2025'],None,'Incidência 2025: %s/100 mil (Brasil %s)'%(fmt_br(K['tb_inc']['2025'],1),fmt_br(K['tb_br_inc'],1))],
 ['Hanseníase (casos novos)',K['hans']['2022'],K['hans']['2023'],K['hans']['2024'],K['hans']['2025'],hs.loc['Total','2026'] if '2026' in hs.columns else None,'Detecção 2025: %s/100 mil'%fmt_br(K['hans_det_2025'],1)],
 ['Sífilis congênita (casos)',K['sifc']['2022'],K['sifc']['2023'],K['sifc']['2024'],K['sifc']['2025'],None,'Incidência 2024: %s por mil NV (Brasil %s)'%(fmt_br(K['sifc_tx']['2024'],1),fmt_br(K['sifc_br'],1))],
 ['Sífilis em gestantes (casos)',K['sifg']['2022'],K['sifg']['2023'],K['sifg']['2024'],K['sifg']['2025'],None,'Taxa 2024: %s por mil NV'%fmt_br(K['sifg_tx']['2024'],1)],
 ['Dengue (casos prováveis)',K['deng']['2022'],K['deng']['2023'],K['deng']['2024'],K['deng']['2025'],K['deng']['2026'],'Epidemia 2024: %s/100 mil; %d óbitos'%(fmt_br(K['deng_inc_2024'],0),int(K['deng_ob_2024']))],
 ['Chikungunya (confirmados)']+[K['chik_conf'].get(y) for y in yrs+['2026']]+[''],
 ['Zika (confirmados)']+[K['zika_conf'].get(y) for y in yrs+['2026']]+[''],
 ['Leishmaniose tegumentar (casos)',K['lta']['2022'],K['lta']['2023'],K['lta']['2024'],K['lta']['2025'],None,'Incidência 2024: %s/100 mil'%fmt_br(K['lta_inc_2024'],1)],
 ['Meningites (casos confirmados)']+[K['men'][y] for y in yrs+['2026']]+['Óbitos 2022–2026: %d'%int(sum(K['men_ob'].values()))],
 ['Acidentes por animais peçonhentos']+[K['anim'][y] for y in yrs+['2026']]+['%d óbitos em 2022–2025'%int(K['anim_ob_2224'])],
 ['Intoxicações exógenas (notificações)']+[K['intox'][y] for y in yrs+['2026']]+['Tentativas de suicídio: %d (2024), %d (2025)'%(int(K['intox_suic']['2024']),int(K['intox_suic']['2025']))],
 ['Óbitos por tuberculose (SIM)']+[K['sim_tb'][y] for y in yrs]+[None,''],
 ['Óbitos por HIV/aids (SIM)']+[K['sim_hiv'][y] for y in yrs]+[None,'Taxa 2025: %s/100 mil'%fmt_br(K['sim_hiv_tx_2025'],1)],
],columns=['Agravo','2022','2023','2024','2025','2026 (parcial)','Observação']).set_index('Agravo')
S={'00_Painel_Vigilancia':(pr,'Painel-resumo da vigilância epidemiológica do Amapá, 2022–2026','Fontes: SINAN e SIM/DATASUS; taxas calculadas com população IBGE.'),**S}
S['BENCH_TB_UF_2025']=(bt,'Tuberculose: casos e incidência por UF, 2025 (casos por UF de notificação)','')
if bhd is not None: S['BENCH_HANS_UF_2025']=(bhd,'Hanseníase: casos novos e taxa de detecção por UF, 2025','')
S['BENCH_SIFC_UF_2024']=(bsd,'Sífilis congênita: casos e incidência por mil nascidos vivos por UF, 2024','')
S['ARBO_resumo']=(arbo,'Arboviroses no Amapá, 2022–2026','')
bd24=L('e1_bench_deng_uf_2024')
if bd24 is not None:
    bdd=pd.DataFrame({'Casos prováveis 2024':{ufname(i):bd24.loc[i,'Casos Prováveis'] for i in bd24.index if i!='Total'}}); bdd['Incidência 2024 (por 100 mil hab.)']=[bdd.loc[u,'Casos prováveis 2024']/pop_uf[u][2024]*1e5 for u in bdd.index]; bdd.loc['BRASIL']=[bd24.loc['Total','Casos Prováveis'],bd24.loc['Total','Casos Prováveis']/popbr[2024]*1e5]
    bdd=bdd.sort_values('Incidência 2024 (por 100 mil hab.)',ascending=False); S['BENCH_DENGUE_UF_2024']=(bdd,'Dengue: casos prováveis e incidência por UF, 2024',''); K['deng_rank_2024']=int(list(bdd.drop('BRASIL').index).index('Amapá')+1); K['deng_br_2024']=bdd.loc['BRASIL','Incidência 2024 (por 100 mil hab.)']
fontes=[('SINAN – Sistema de Informação de Agravos de Notificação (TABNET)','sinannet/cnv/tubercap, hanswap, sifilisap, sifilisgestanteap, hepaap, denguebap, chikunap, zikaap, leishvap, ltaap, meninap, animaisap, intoxap, malaap; versões *br/*uf para UFs','Casos por ano de diagnóstico/notificação/sintomas e município de residência. 2025 e 2026 sujeitos a atualização.'),('SIM – Sistema de Informações sobre Mortalidade','sim/cnv/obt10ap.def','Óbitos por residência; 2025 preliminar; 2026 parcial.'),('IBGE – estimativas populacionais (SIDRA 6579) e SINASC (nascidos vivos)','apisidra.ibge.gov.br; sinasc/cnv/nvap.def, nvuf.def','Denominadores das taxas.'),('Limitações','Malária: SIVEP-Malária (não disponível no TABNET); HIV/aids: painel do DCCI (não acessível); vacinação: SI-PNI (não acessível); hepatites: base estadual sem etiologia.','Dados a complementar com a SVS/SESA.')]
write_workbook(OUT+'/Tabelas_Vigilancia_Amapa_2022_2026.xlsx',S,'Vigilância em saúde no Amapá: doenças transmissíveis e agravos de notificação, 2022–2026','Estudo complementar para a transição 2026/2027. Extração em 07/11/2026.',fontes)
# ---- gráficos ----
bars(yrs,[K['tb'][y] for y in yrs],GR+'/f01_tb_casos.png','Casos de tuberculose (todas as formas)')
enc2=enc[yrs]; parts={'Cura':[enc.loc['Cura',y] for y in yrs],'Abandono (incl. primário)':[enc.loc['Abandono',y]+enc.loc['Abandono Primário',y] for y in yrs],'Óbito (TB e outras causas)':[enc.loc['Óbito por tuberculose',y]+enc.loc['Óbito por outras causas',y] for y in yrs],'Transferência/outros':[enc.loc['Transferência',y]+enc.loc['TB-DR',y]+enc.loc['Mudança de Esquema',y]+enc.loc['Falência',y] for y in yrs],'Sem encerramento':[enc.loc['Ign/Branco',y] for y in yrs]}
stacked(yrs,parts,GR+'/f02_tb_encerramento.png','Casos')
lines(yrs,{'Casos novos de hanseníase':[K['hans'][y] for y in yrs],'Com grau II de incapacidade no diagnóstico':[inc.loc['GRAU II',y] for y in yrs]},GR+'/f03_hanseniase.png','Casos')
lines(yrs,{'Sífilis em gestantes':[K['sifg'][y] for y in yrs],'Sífilis congênita':[K['sifc'][y] for y in yrs]},GR+'/f04_sifilis.png','Casos')
bars(yrs+['2026'],[K['deng'][y] for y in yrs+['2026']],GR+'/f05_dengue.png','Casos prováveis de dengue')
dm=sorted(K['deng_mun_2024'].items(),key=lambda x:x[1])[-10:]; hbars([k for k,v in dm],[v for k,v in dm],GR+'/f06_dengue_mun.png','Casos prováveis, 2024')
lm=sorted(K['lta_mun_2024'].items(),key=lambda x:x[1])[-10:]; hbars([k for k,v in lm],[v for k,v in lm],GR+'/f07_lta_mun.png','Casos confirmados, 2024')
stacked(yrs+['2026'],{t:[an.loc[t,y] for y in yrs+['2026']] for t in ['Serpente','Escorpião','Aranha','Abelha','Outros']},GR+'/f08_animais.png','Notificações')
bt2=bt.drop('BRASIL')['Incidência 2025 (por 100 mil hab.)'].sort_values(); hbars(list(bt2.index)+['BRASIL'],list(bt2.values)+[bt.loc['BRASIL','Incidência 2025 (por 100 mil hab.)']],GR+'/f09_bench_tb.png','Casos por 100 mil habitantes, 2025',highlight=['Amapá','BRASIL'],figsize=(9,6.5),fmt=lambda v:fmt_br(v,1),fs=8)
bs2=bsd.drop('BRASIL')['Incidência 2024 (por mil NV)'].sort_values(); hbars(list(bs2.index)+['BRASIL'],list(bs2.values)+[bsd.loc['BRASIL','Incidência 2024 (por mil NV)']],GR+'/f10_bench_sifc.png','Casos por mil nascidos vivos, 2024',highlight=['Amapá','BRASIL'],figsize=(9,6.5),fmt=lambda v:fmt_br(v,1),fs=8)
json.dump(K,open(RAW+'/kpi_e1.json','w'),ensure_ascii=False,indent=1,default=lambda o:o.item() if hasattr(o,'item') else str(o))
for k,v in K.items(): print(k,'=',v if not isinstance(v,dict) else {a:(round(b,2) if isinstance(b,float) else b) for a,b in v.items()})
