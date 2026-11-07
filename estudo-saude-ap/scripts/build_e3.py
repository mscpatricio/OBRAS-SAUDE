# -*- coding: utf-8 -*-
"""Estudo 3 - Violências, causas externas e saúde mental."""
import sys, os, json, re
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from lib_estudo import *
RAW='/tmp/claude-0/-home-user-OBRAS-SAUDE/c712070a-2954-5409-93ab-21cafbd2988b/scratchpad/raw'
T2=RAW+'/tab2/'; T1=RAW+'/tab/'
OUT='/home/user/OBRAS-SAUDE/estudo-saude-ap/estudos-complementares/e3_violencias_saude_mental'; GR=OUT+'/graficos'
L=lambda n: load(T2+n+'.csv'); L1=lambda n: load(T1+n+'.csv')
pop_uf={}
for r in json.load(open(RAW+'/sidra_pop_uf_all.json'))[1:]: pop_uf.setdefault(r['D1N'],{})[int(r['D3N'])]=int(r['V'])
pop=pop_uf['Amapá']; popbr=pop_uf['Brasil']
pop_mun={}
for r in json.load(open(RAW+'/sidra_pop_mun.json'))[1:]: pop_mun.setdefault(unaccent(r['D1N'].replace(' - AP','')).upper(),{})[int(r['D3N'])]=int(r['V'])
def ufname(s): return re.sub(r'^\d\d ','',s)
K={}; S={}
def add(name,df,title,note=''):
    if df is not None: S[name]=(recorte(df),title,note)
yrs=['2022','2023','2024','2025']; yrs6=yrs+['2026']
# ---------- SIM causas externas ----------
gg=L('e3_ext_gg_ano'); add('SIM_ext_grande_grupo_ano',gg,'Óbitos de residentes por causas externas segundo grande grupo da CID-10 e ano')
def g(df,prefix):
    r=[i for i in df.index if i.startswith(prefix)]; return df.loc[r[0]] if r else None
agr=g(gg,'X85-Y09'); leg=g(gg,'Y35-Y36'); sui=g(gg,'X60-X84'); tra=g(gg,'V01-V99'); aci=g(gg,'W00-X59'); ind=g(gg,'Y10-Y34')
K['ext']={y:gg.loc['Total',y] for y in yrs6}; K['agr']={y:agr[y] for y in yrs6}; K['leg']={y:leg[y] for y in yrs6}; K['sui']={y:sui[y] for y in yrs6}; K['tra']={y:tra[y] for y in yrs6}; K['aci']={y:aci[y] for y in yrs6}; K['ind']={y:ind[y] for y in yrs6}
K['mvi']={y:agr[y]+leg[y] for y in yrs6}  # mortes violentas intencionais (agressões + intervenções legais)
K['tx_agr']={y:agr[y]/pop[int(y)]*1e5 for y in ('2024','2025')}; K['tx_mvi']={y:(agr[y]+leg[y])/pop[int(y)]*1e5 for y in ('2024','2025')}; K['tx_sui']={y:sui[y]/pop[int(y)]*1e5 for y in ('2024','2025')}; K['tx_tra']={y:tra[y]/pop[int(y)]*1e5 for y in ('2024','2025')}; K['tx_ext']={y:gg.loc['Total',y]/pop[int(y)]*1e5 for y in ('2024','2025')}
gr=L('e3_ext_grupo_ano'); add('SIM_ext_grupo_ano',gr,'Óbitos por causas externas segundo grupo da CID-10 e ano')
K['afog']={y:g(gr,'... Afogamento')[y] for y in yrs6}; K['quedas']={y:g(gr,'... Quedas')[y] for y in yrs6}; K['moto']={y:g(gr,'... Motociclista')[y] for y in yrs6}; K['pedestre']={y:g(gr,'... Pedestre')[y] for y in yrs6}; K['tx_afog_2024']=K['afog']['2024']/pop[2024]*1e5
add('SIM_ext_categoria_ano',L('e3_ext_cat_ano'),'Óbitos por causas externas segundo categoria da CID-10 e ano')
mun=L('e3_ext_mun_ano'); add('SIM_ext_mun_ano',mun,'Óbitos por causas externas por município de residência e ano')
gm=L('e3_ext_gg_mun_2024'); add('SIM_ext_mun_grande_grupo_2024',gm,'Óbitos por causas externas por município e grande grupo, 2024')
def col(df,prefix):
    c=[x for x in df.columns if x.startswith(prefix)]; return c[0] if c else None
cm={}
for i in gm.index:
    if i=='Total': continue
    k=unaccent(nome_mun(i)).upper(); p=pop_mun[k][2024]
    cm[nome_mun(i)]={'População 2024':p,'Óbitos por causas externas 2024':gm.loc[i,'Total'],'Taxa causas externas (por 100 mil)':gm.loc[i,'Total']/p*1e5,'Agressões 2024':gm.loc[i,col(gm,'X85')],'Intervenções legais 2024':gm.loc[i,col(gm,'Y35')] if col(gm,'Y35') else 0,'Taxa de mortes violentas intencionais (por 100 mil)':(gm.loc[i,col(gm,'X85')]+(gm.loc[i,col(gm,'Y35')] if col(gm,'Y35') else 0))/p*1e5,'Suicídios 2024':gm.loc[i,col(gm,'X60')],'Acidentes de transporte 2024':gm.loc[i,col(gm,'V01')]}
cmdf=pd.DataFrame(cm).T; cmdf.loc['Amapá']=[pop[2024],gm.loc['Total','Total'],gm.loc['Total','Total']/pop[2024]*1e5,gm.loc['Total',col(gm,'X85')],gm.loc['Total',col(gm,'Y35')],(gm.loc['Total',col(gm,'X85')]+gm.loc['Total',col(gm,'Y35')])/pop[2024]*1e5,gm.loc['Total',col(gm,'X60')],gm.loc['Total',col(gm,'V01')]]
cmdf.index.name='Município'; S['SIM_ext_taxas_mun_2024']=(cmdf,'Mortalidade por causas externas por município de residência, 2024 (taxas por 100 mil habitantes)','Mortes violentas intencionais = agressões + intervenções legais.')
K['mun24']=cmdf
fx=L('e3_ext_gg_fx_2024'); add('SIM_ext_grande_grupo_fx_2024',fx,'Óbitos por causas externas por grande grupo e faixa etária, 2024')
def fxsum(row,cols_): return sum(fx.loc[row,c] for c in cols_)
r_agr=[i for i in fx.index if i.startswith('X85')][0]; r_leg=[i for i in fx.index if i.startswith('Y35')][0]; r_sui=[i for i in fx.index if i.startswith('X60')][0]
K['agr_1529']=fxsum(r_agr,['15 a 19 anos','20 a 29 anos']); K['agr_1529_pct']=K['agr_1529']/fx.loc[r_agr,'Total']*100; K['leg_1529']=fxsum(r_leg,['15 a 19 anos','20 a 29 anos']); K['leg_1529_pct']=K['leg_1529']/fx.loc[r_leg,'Total']*100; K['sui_1539']=fxsum(r_sui,['15 a 19 anos','20 a 29 anos','30 a 39 anos']); K['sui_1539_pct']=K['sui_1539']/fx.loc[r_sui,'Total']*100
sx=L('e3_ext_gg_sexo_2024'); add('SIM_ext_grande_grupo_sexo_2024',sx,'Óbitos por causas externas por grande grupo e sexo, 2024'); K['ext_masc_pct_2024']=sx.loc['Total','Masc']/sx.loc['Total','Total']*100; K['agr_masc_pct']=sx.loc[r_agr,'Masc']/sx.loc[r_agr,'Total']*100
ra=L('e3_ext_gg_raca_2024'); add('SIM_ext_grande_grupo_raca_2024',ra,'Óbitos por causas externas por grande grupo e cor/raça, 2024'); K['ext_parda_pct']=ra.loc['Total','Parda']/ra.loc['Total','Total']*100; K['agr_negra_pct']=(ra.loc[r_agr,'Parda']+ra.loc[r_agr,'Preta'])/ra.loc[r_agr,'Total']*100
add('SIM_ext_sexo_ano',L('e3_ext_sexo_ano'),'Óbitos por causas externas por sexo e ano'); add('SIM_ext_fx_ano',L('e3_ext_fx_ano'),'Óbitos por causas externas por faixa etária e ano'); add('SIM_ext_raca_ano',L('e3_ext_raca_ano'),'Óbitos por causas externas por cor/raça e ano')
# bench UF
bench={}
for yr in ('2023','2024'):
    b=L(f'e3_bench_ext_uf_gg_{yr}')
    rows={}
    for i in b.index:
        if i=='Total': continue
        u=ufname(i); p=pop_uf[u].get(int(yr),pop_uf[u][2024])
        rows[u]={f'Agressões {yr}':b.loc[i,col(b,'X85')],f'Intervenções legais {yr}':b.loc[i,col(b,'Y35')] if col(b,'Y35') else 0,f'MVI por 100 mil {yr}':(b.loc[i,col(b,'X85')]+(b.loc[i,col(b,'Y35')] if col(b,'Y35') else 0))/p*1e5,f'Suicídios por 100 mil {yr}':b.loc[i,col(b,'X60')]/p*1e5,f'Acid. transporte por 100 mil {yr}':b.loc[i,col(b,'V01')]/p*1e5,f'Causas externas por 100 mil {yr}':b.loc[i,'Total']/p*1e5}
    rows['BRASIL']={f'Agressões {yr}':b.loc['Total',col(b,'X85')],f'Intervenções legais {yr}':b.loc['Total',col(b,'Y35')],f'MVI por 100 mil {yr}':(b.loc['Total',col(b,'X85')]+b.loc['Total',col(b,'Y35')])/popbr.get(int(yr),popbr[2024])*1e5,f'Suicídios por 100 mil {yr}':b.loc['Total',col(b,'X60')]/popbr.get(int(yr),popbr[2024])*1e5,f'Acid. transporte por 100 mil {yr}':b.loc['Total',col(b,'V01')]/popbr.get(int(yr),popbr[2024])*1e5,f'Causas externas por 100 mil {yr}':b.loc['Total','Total']/popbr.get(int(yr),popbr[2024])*1e5}
    bench[yr]=pd.DataFrame(rows).T
bd=pd.concat([bench['2023'],bench['2024']],axis=1).sort_values('MVI por 100 mil 2024',ascending=False); bd.index.name='UF'
S['BENCH_CAUSAS_EXTERNAS_UF']=(bd,'Mortalidade por causas externas por UF, 2023 e 2024 (taxas por 100 mil habitantes)','MVI = mortes violentas intencionais (agressões + intervenções legais).')
for k in ['MVI por 100 mil 2024','Suicídios por 100 mil 2024','Acid. transporte por 100 mil 2024','Causas externas por 100 mil 2024']:
    K['bench_'+k]=(bd.loc['Amapá',k],bd.loc['BRASIL',k],int(bd.drop('BRASIL')[k].rank(ascending=False)['Amapá']))
K['leg_share_br_2024']=bd.loc['Amapá','Intervenções legais 2024']/bd.loc['BRASIL','Intervenções legais 2024']*100; K['leg_br_2024']=bd.loc['BRASIL','Intervenções legais 2024']
# ---------- SIH causas externas ----------
fg=L('e3_fi_gg_ano'); add('SIH_ext_grande_grupo_ano',fg,'Internações por causas externas segundo grande grupo e ano (local de internação)')
fgr=L('e3_fi_grupo_ano'); add('SIH_ext_grupo_ano',fgr,'Internações por causas externas segundo grupo e ano')
K['int_ext']={y:fg.loc['Total',y] for y in yrs6}; K['int_tra']={y:g(fg,'V01')[y] for y in yrs6}; K['int_moto']={y:g(fgr,'V20-V29')[y] for y in yrs6}; K['int_quedas']={y:g(fgr,'W00-W19')[y] for y in yrs6}; K['int_agr']={y:g(fg,'X85')[y] for y in yrs6}; K['int_venen']={y:g(fgr,'X20-X29')[y] for y in yrs6}; K['int_compl']={y:g(fg,'Y40')[y] for y in yrs6}; K['int_w85']={y:g(fgr,'W85-W99')[y] for y in yrs6}; K['int_sui']={y:g(fg,'X60')[y] for y in yrs6}
f25=L('e3_fi_gg_2025'); add('SIH_ext_grande_grupo_2025',f25,'Internações por causas externas: quantidade, valor, permanência e óbitos por grande grupo, 2025'); K['int_ext_valor_2025']=f25.loc['Total','Valor total']; K['int_ext_ob_2025']=f25.loc['Total','Óbitos']; K['int_ext_perm_2025']=f25.loc['Total','Média permanência']
fe=L('e3_fi_estab_gg_2025'); add('SIH_ext_estab_2025',fe,'Internações por causas externas por estabelecimento e grande grupo, 2025'); K['int_he_2025']=fe.loc[[i for i in fe.index if 'EMERGENCIA' in i][0],'Total']; K['int_he_pct']=K['int_he_2025']/fe.loc['Total','Total']*100; K['int_laranjal']=fe.loc[[i for i in fe.index if 'LARANJAL' in i][0],'Total']; K['int_ml']=fe.loc[[i for i in fe.index if 'MARIA LUCIA' in i][0],'Total']
add('SIH_ext_fx_ano',L('e3_fi_fx_ano'),'Internações por causas externas por faixa etária e ano'); add('SIH_ext_sexo_ano',L('e3_fi_sexo_ano'),'Internações por causas externas por sexo e ano')
# ---------- SINAN violência ----------
vm=L('e3_viol_mun_ano'); add('SINAN_viol_mun_ano',vm,'Notificações de violência interpessoal/autoprovocada por município de residência e ano')
K['viol']={y:vm.loc['Total',y] for y in yrs}; K['viol_tx_2025']=vm.loc['Total','2025']/pop[2025]*1e5
for n,t in [('fx','faixa etária'),('sexo','sexo'),('fisica','violência física'),('sexual','violência sexual'),('psico','violência psicológica/moral'),('negl','negligência/abandono'),('autoprov','lesão autoprovocada'),('local','local de ocorrência'),('repet','violência de repetição'),('raca','raça/cor'),('armafogo','uso de arma de fogo'),('estupro','estupro (entre violências sexuais)')]:
    add('SINAN_viol_'+n+'_ano',L(f'e3_viol_{n}_ano'),'Notificações de violência por '+t+' e ano')
add('SINAN_viol_fx_sexo_2025',L('e3_viol_fx_sexo_2025'),'Notificações de violência por faixa etária e sexo, 2025'); add('SINAN_viol_sexual_fx_2025',L('e3_viol_sexual_fx_2025'),'Notificações de violência sexual por faixa etária, 2025'); add('SINAN_viol_autoprov_fx_2025',L('e3_viol_autoprov_fx_2025'),'Notificações de lesão autoprovocada por faixa etária, 2025')
vs=L('e3_viol_sexo_ano'); K['viol_fem_pct_2025']=vs.loc['Feminino','2025']/vs.loc['Total','2025']*100
va=L('e3_viol_autoprov_ano'); K['autoprov']={y:va.loc['Sim',y] for y in yrs}
vx=L('e3_viol_sexual_ano'); K['vsex']={y:vx.loc['Sim',y] for y in yrs}; ve=L('e3_viol_estupro_ano'); K['estupro']={y:ve.loc['Sim',y] for y in yrs}
vf=L('e3_viol_fisica_ano'); K['vfis']={y:vf.loc['Sim',y] for y in yrs}; vp=L('e3_viol_psico_ano'); K['vpsi']={y:vp.loc['Sim',y] for y in yrs}; vn=L('e3_viol_negl_ano'); K['vneg']={y:vn.loc['Sim',y] for y in yrs}
vl=L('e3_viol_local_ano'); K['viol_resid_pct_2025']=vl.loc['Residência','2025']/vl.loc['Total','2025']*100; vr=L('e3_viol_repet_ano'); K['viol_repet_pct_2025']=vr.loc['Sim','2025']/vr.loc['Total','2025']*100
vfx=L('e3_viol_fx_ano'); K['viol_1019_2025']=vfx.loc['10-14','2025']+vfx.loc['15-19','2025']; K['viol_0019_pct_2025']=(vfx.loc['<1 Ano','2025']+vfx.loc['1-4','2025']+vfx.loc['5-9','2025']+vfx.loc['10-14','2025']+vfx.loc['15-19','2025'])/vfx.loc['Total','2025']*100
sfx=L('e3_viol_sexual_fx_2025'); K['vsex_crianca_2025']=sum(sfx.loc[r,'Sim'] for r in ('<1 Ano','1-4','5-9','10-14') if r in sfx.index); K['vsex_1019_2025']=sum(sfx.loc[r,'Sim'] for r in ('10-14','15-19') if r in sfx.index); K['vsex_total_2025']=sfx.loc['Total','Sim']
afx=L('e3_viol_autoprov_fx_2025'); K['autoprov_1019_2025']=afx.loc['10-14','Sim']+afx.loc['15-19','Sim']; K['autoprov_1029_pct']=(afx.loc['10-14','Sim']+afx.loc['15-19','Sim']+afx.loc['20-29','Sim'])/afx.loc['Total','Sim']*100
K['viol_mun_2025']={nome_mun(i):vm.loc[i,'2025'] for i in vm.index if i!='Total'}; K['viol_pb_2024']=vm.loc['160015 PEDRA BRANCA DO AMAPARI','2024']
vra=L('e3_viol_raca_ano'); K['viol_indig']={y:vra.loc['Indigena',y] for y in yrs}
bv=L('e3_bench_viol_uf_ano'); bvd=pd.DataFrame({'Notificações 2025':{ufname(i):bv.loc[i,'2025'] for i in bv.index if i!='Total'}}); bvd['Notificações por 100 mil hab. 2025']=[bvd.loc[u,'Notificações 2025']/pop_uf[u][2025]*1e5 for u in bvd.index]; bvd.loc['BRASIL']=[bv.loc['Total','2025'],bv.loc['Total','2025']/popbr[2025]*1e5]; bvd=bvd.sort_values('Notificações por 100 mil hab. 2025',ascending=False)
S['BENCH_VIOLENCIA_UF_2025']=(bvd,'Notificações de violência interpessoal/autoprovocada por UF, 2025','UF de notificação.'); K['bench_viol_ap']=bvd.loc['Amapá','Notificações por 100 mil hab. 2025']; K['bench_viol_br']=bvd.loc['BRASIL','Notificações por 100 mil hab. 2025']; K['bench_viol_rank']=int(list(bvd.drop('BRASIL').index).index('Amapá')+1)
# intoxicação / tentativa de suicídio
ic=L('e1_intox_circ_ano'); K['intox_suic']={y:ic.loc['Tentativa de suicídio',y] for y in yrs6}; add('SINAN_intox_circunstancia_ano',ic,'Intoxicações exógenas por circunstância e ano (inclui tentativas de suicídio)')
# ---------- Saúde mental ----------
cv=L('e3_nih_lista_capV_ano'); add('SIH_transtornos_mentais_lista_ano',cv,'Internações por transtornos mentais e comportamentais (cap. V) segundo lista de morbidade e ano')
K['int_capV']={y:cv.loc['Total',y] for y in yrs6}; K['int_esquiz']={y:g(cv,'.. Esquizofrenia')[y] for y in yrs6}; K['int_subst']={y:g(cv,'.. Transt ment comport dev uso outr subst')[y]+g(cv,'.. Transt mentais e comportamentais dev uso álcool')[y] for y in yrs6}
ce=L('e3_nih_capV_estab_ano'); add('SIH_transtornos_mentais_estab_ano',ce,'Internações por transtornos mentais por estabelecimento e ano'); K['int_capV_hcal']={y:ce.loc[[i for i in ce.index if 'ALBERTO LIMA' in i][0],y] for y in yrs6}
add('SIH_transtornos_mentais_fx_sexo_2025',L('e3_nih_capV_fx_2025'),'Internações por transtornos mentais por faixa etária e sexo, 2025')
hb=L('e2_hab_latest'); caps={i.strip('.'):hb.loc[i,'Qtde Estabelec. Habilitados'] for i in hb.index if 'CAPS' in i}; K['caps']=caps; K['caps_total']=sum(caps.values())
et=L1('cnes_estab_tipo_ano'); K['caps_cnes']={c:et.loc['CENTRO DE ATENCAO PSICOSSOCIAL',c] for c in ('2022/Dez','2026/Set')}
ld=L1('cnes_leitos_espdet_latest'); K['leitos_psiq']=ld.loc['..Psiquiatria','Qtd SUS']; K['leitos_acolh']=ld.loc['..Acolhimento Noturno','Qtd SUS'] if '..Acolhimento Noturno' in ld.index else 0
sf=L('e2_sia_forma_ano_qtd'); K['sia_psico']={y:g(sf,'030108')[y] for y in yrs6}; K['sia_reab']={y:g(sf,'030107')[y] for y in yrs6}
eq=L('e2_equipe_tipo_ano'); K['ecr']={c:g(eq,'73')[c] for c in ('2022/Dez','2026/Set')}; K['emad']={c:g(eq,'22')[c] for c in ('2022/Dez','2026/Set')}
sm=L1('sim_cap_ano'); K['ob_capV']={y:sm.loc['V.   Transtornos mentais e comportamentais',y] for y in yrs}
raps=pd.DataFrame([['CAPS habilitados pelo MS (todos os tipos)',K['caps_total'],'CAPS I: %d; CAPS i: %d; CAPS AD: %d; CAPS AD III: %d'%(caps.get('0616-CAPS I',0),caps.get('0620-CAPS INFANTIL',0),caps.get('0619-CAPS ALCOOL E DROGAS',0),caps.get('0635-CAPS AD III',0))],['CAPS cadastrados no CNES (set/2026)',K['caps_cnes']['2026/Set'],'%d em dez/2022'%int(K['caps_cnes']['2022/Dez'])],['Leitos SUS de psiquiatria (CNES, set/2026)',K['leitos_psiq'],'Hospital de Emergência'],['Leitos de acolhimento noturno (CNES, set/2026)',K['leitos_acolh'],''],['Equipes de Consultório na Rua (set/2026)',K['ecr']['2026/Set'],'%d em dez/2022'%int(K['ecr']['2022/Dez'])],['Equipes multidisciplinares de atenção domiciliar (EMAD, set/2026)',K['emad']['2026/Set'],''],['Atendimentos psicossociais no SIA (030108), 2025',K['sia_psico']['2025'],'%s em 2022'%fmt_int(K['sia_psico']['2022'])],['Internações por transtornos mentais, 2025',K['int_capV']['2025'],'%d em 2022'%int(K['int_capV']['2022'])]],columns=['Componente da RAPS','Quantidade','Observação']).set_index('Componente da RAPS')
S['RAPS_componentes']=(raps,'Componentes da Rede de Atenção Psicossocial do Amapá (CNES, SIA, SIH), 2022–2026','')
# ---------- Painel ----------
pr=pd.DataFrame([
 ['Óbitos por causas externas']+[K['ext'][y] for y in yrs6]+['Taxa 2024: %s/100 mil'%fmt_br(K['tx_ext']['2024'],1)],
 ['Agressões (homicídios)']+[K['agr'][y] for y in yrs6]+['Taxa 2024: %s/100 mil'%fmt_br(K['tx_agr']['2024'],1)],
 ['Intervenções legais']+[K['leg'][y] for y in yrs6]+['%s%% do total nacional em 2024'%fmt_br(K['leg_share_br_2024'],1)],
 ['Lesões autoprovocadas (suicídios)']+[K['sui'][y] for y in yrs6]+['Taxa 2025: %s/100 mil'%fmt_br(K['tx_sui']['2025'],1)],
 ['Acidentes de transporte']+[K['tra'][y] for y in yrs6]+['Taxa 2024: %s/100 mil'%fmt_br(K['tx_tra']['2024'],1)],
 ['Afogamentos']+[K['afog'][y] for y in yrs6]+['Taxa 2024: %s/100 mil'%fmt_br(K['tx_afog_2024'],1)],
 ['Internações por causas externas (SIH)']+[K['int_ext'][y] for y in yrs6]+['Motociclistas 2025: %d'%int(K['int_moto']['2025'])],
 ['Notificações de violência (SINAN)']+[K['viol'][y] for y in yrs]+[None,'%s%% mulheres (2025)'%fmt_br(K['viol_fem_pct_2025'],0)],
 ['Lesões autoprovocadas notificadas (SINAN)']+[K['autoprov'][y] for y in yrs]+[None,''],
 ['Violência sexual notificada (SINAN)']+[K['vsex'][y] for y in yrs]+[None,''],
 ['Internações por transtornos mentais (SIH)']+[K['int_capV'][y] for y in yrs6]+['Leitos SUS de psiquiatria: %d'%int(K['leitos_psiq'])],
],columns=['Indicador','2022','2023','2024','2025','2026 (parcial)','Observação']).set_index('Indicador')
S={'00_Painel_Violencias':(pr,'Painel-resumo: violências, causas externas e saúde mental, Amapá, 2022–2026','SIM, SIH, SINAN, CNES/DATASUS. 2025 preliminar; 2026 parcial.'),**S}
fontes=[('SIM – causas externas (TABNET)','sim/cnv/ext10ap.def; sim/cnv/ext10uf.def','Óbitos por residência; 2025 preliminar; 2026 parcial.'),('SIH/SUS – internações por causas externas e por transtornos mentais','sih/cnv/fiap.def; sih/cnv/niap.def (cap. V)','Local de internação; 2026 até agosto.'),('SINAN – violência interpessoal/autoprovocada e intoxicações exógenas','sinannet/cnv/violeap.def; violebr.def; intoxap.def','Notificações por município de residência e ano de notificação.'),('CNES – CAPS, leitos e equipes','cnes/cnv/habap.def; estabap.def; leiintap.def; equipeap.def','Competência set/2026.'),('IBGE','SIDRA 6579','Denominadores.'),('Limitações','RAAS (produção dos CAPS), SAMU e dados de segurança pública (SSP/Atlas da Violência) não acessíveis.','Solicitar à SESA e à SEJUSP.')]
write_workbook(OUT+'/Tabelas_Violencias_SaudeMental_Amapa_2022_2026.xlsx',S,'Violências, causas externas e saúde mental no Amapá, 2022–2026','Estudo complementar para a transição 2026/2027. Extração em 07/11/2026.',fontes)
# gráficos
xs=['2022','2023','2024','2025','2026*']
stacked(xs,{'Agressões':[K['agr'][y] for y in yrs6],'Intervenções legais':[K['leg'][y] for y in yrs6],'Suicídios':[K['sui'][y] for y in yrs6],'Acidentes de transporte':[K['tra'][y] for y in yrs6],'Outros acidentes':[K['aci'][y] for y in yrs6],'Intenção indeterminada/outros':[K['ind'][y]+(gg.loc['Total',y]-K['agr'][y]-K['leg'][y]-K['sui'][y]-K['tra'][y]-K['aci'][y]-K['ind'][y]) for y in yrs6]},GR+'/f01_ext_grupos.png','Óbitos de residentes')
mv=bd.drop('BRASIL')['MVI por 100 mil 2024'].sort_values(); hbars(list(mv.index)+['BRASIL'],list(mv.values)+[bd.loc['BRASIL','MVI por 100 mil 2024']],GR+'/f02_bench_mvi.png','Mortes violentas intencionais por 100 mil hab., 2024',highlight=['Amapá','BRASIL'],figsize=(9,6.5),fmt=lambda v:fmt_br(v,1),fs=8)
fxg=fx.loc[r_agr,[c for c in fx.columns if c!='Total']]; bars(list(fxg.index),list(fxg.values),GR+'/f03_agressoes_idade.png','Óbitos por agressão, 2024',rot=45)
tm=cmdf.drop('Amapá')['Taxa de mortes violentas intencionais (por 100 mil)'].sort_values(); hbars(list(tm.index),list(tm.values),GR+'/f04_mvi_mun.png','MVI por 100 mil hab., 2024 (números pequenos nos municípios menores)',fmt=lambda v:fmt_br(v,1))
lines(xs,{'Quedas':[K['int_quedas'][y] for y in yrs6],'Motociclistas':[K['int_moto'][y] for y in yrs6],'Animais/plantas venenosos':[K['int_venen'][y] for y in yrs6],'Agressões':[K['int_agr'][y] for y in yrs6],'Complicações da assistência':[K['int_compl'][y] for y in yrs6]},GR+'/f05_int_ext.png','Internações (SIH)',legend_cols=3)
lines(['2022','2023','2024','2025'],{'Notificações de violência (total)':[K['viol'][y] for y in yrs],'Lesão autoprovocada':[K['autoprov'][y] for y in yrs],'Violência sexual':[K['vsex'][y] for y in yrs],'Violência física':[K['vfis'][y] for y in yrs]},GR+'/f06_sinan_viol.png','Notificações (SINAN)',legend_cols=2)
vfs=L('e3_viol_fx_sexo_2025'); vfs=vfs.drop('Total'); stacked(list(vfs.index),{'Feminino':list(vfs['Feminino']),'Masculino':list(vfs['Masculino'])},GR+'/f07_viol_fx_sexo.png','Notificações de violência, 2025')
bars(xs,[K['int_capV'][y] for y in yrs6],GR+'/f08_int_mental.png','Internações por transtornos mentais (SIH)')
bv2=bvd.drop('BRASIL')['Notificações por 100 mil hab. 2025'].sort_values(); hbars(list(bv2.index)+['BRASIL'],list(bv2.values)+[bvd.loc['BRASIL','Notificações por 100 mil hab. 2025']],GR+'/f09_bench_viol.png','Notificações de violência por 100 mil hab., 2025',highlight=['Amapá','BRASIL'],figsize=(9,6.5),fmt=lambda v:fmt_br(v,0),fs=8)
json.dump({k:v for k,v in K.items() if not isinstance(v,pd.DataFrame)},open(RAW+'/kpi_e3.json','w'),ensure_ascii=False,indent=1,default=lambda o:o.item() if hasattr(o,'item') else str(o))
for k,v in K.items():
    if isinstance(v,pd.DataFrame): continue
    print(k,'=',v if not isinstance(v,dict) else {a:(round(b,2) if isinstance(b,float) else b) for a,b in v.items()})
print(cmdf.round(1).to_string())
