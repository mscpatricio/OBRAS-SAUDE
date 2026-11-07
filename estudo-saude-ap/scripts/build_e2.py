# -*- coding: utf-8 -*-
"""Estudo 2 - Atenção primária, regionalização e saúde materno-infantil."""
import sys, os, json, re
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from lib_estudo import *
RAW='/tmp/claude-0/-home-user-OBRAS-SAUDE/c712070a-2954-5409-93ab-21cafbd2988b/scratchpad/raw'
T2=RAW+'/tab2/'; T1=RAW+'/tab/'
OUT='/home/user/OBRAS-SAUDE/estudo-saude-ap/estudos-complementares/e2_atencao_primaria'; GR=OUT+'/graficos'
L=lambda n: load(T2+n+'.csv'); L1=lambda n: load(T1+n+'.csv')
pop_uf={}
for r in json.load(open(RAW+'/sidra_pop_uf_all.json'))[1:]: pop_uf.setdefault(r['D1N'],{})[int(r['D3N'])]=int(r['V'])
pop=pop_uf['Amapá']; popbr=pop_uf['Brasil']
pop_mun={}
for r in json.load(open(RAW+'/sidra_pop_mun.json'))[1:]: pop_mun.setdefault(unaccent(r['D1N'].replace(' - AP','')).upper(),{})[int(r['D3N'])]=int(r['V'])
def ufname(s): return re.sub(r'^\d\d ','',s)
def mkey(i): return unaccent(nome_mun(i)).upper()
K={}; S={}
def add(name,df,title,note=''):
    if df is not None: S[name]=(recorte(df),title,note)
yrs=['2022','2023','2024','2025']
# ---------- Equipes ----------
et=L('e2_equipe_tipo_ano'); add('EQUIPES_tipo_ano',et,'Equipes de atenção primária cadastradas no CNES por tipo (dez. de cada ano; set/2026)','Códigos de tipo de equipe mudaram em 2020.')
def row(df,prefix): 
    r=[i for i in df.index if i.startswith(prefix)]; return df.loc[r[0]] if r else None
esf=row(et,'70'); esb=row(et,'71'); enasf=row(et,'72'); ecr=row(et,'73'); eabp=row(et,'74'); eap=row(et,'76'); emad=row(et,'22')
cols=['2022/Dez','2023/Dez','2024/Dez','2025/Dez','2026/Set']
K['esf']={c:esf[c] for c in cols}; K['esb']={c:esb[c] for c in cols}; K['enasf']={c:enasf[c] for c in cols}; K['eap']={c:eap[c] for c in cols}; K['eabp']={c:eabp[c] for c in cols}; K['ecr']={c:ecr[c] for c in cols}; K['emad']={c:emad[c] for c in cols}; K['eq_total']={c:et.loc['Total',c] for c in cols}
em=L('e2_equipe_mun_ano_esf'); add('EQUIPES_ESF_mun_ano',em,'Equipes de Saúde da Família (ESF, incl. ribeirinhas e fluviais) por município (dez. de cada ano; set/2026)')
emb=L('e2_equipe_mun_ano_esb'); add('EQUIPES_ESB_mun_ano',emb,'Equipes de Saúde Bucal por município')
ema=L('e2_equipe_mun_ano_eap'); add('EQUIPES_EAP_mun_ano',ema,'Equipes de Atenção Primária (eAP) por município')
emt=L('e2_equipe_mun_tipo_latest'); add('EQUIPES_mun_tipo_set2026',emt,'Equipes por município e tipo, set/2026')
# cobertura potencial (metodologia e-Gestor: ESF 3.450 pessoas; eAP 3.000 (40h) )
cov=[]
for i in em.index:
    if i=='Total': continue
    k=mkey(i); p25=pop_mun[k][2025]; e22=em.loc[i,'2022/Dez']; e26=em.loc[i,'2026/Set']; a26=ema.loc[i,'2026/Set'] if (ema is not None and i in ema.index) else 0
    cov.append({'Município':nome_mun(i),'População 2025':p25,'ESF dez/2022':e22,'ESF set/2026':e26,'eAP set/2026':a26,'eSB set/2026':emb.loc[i,'2026/Set'] if i in emb.index else 0,'Cobertura potencial ESF 2022 (%)':min(100,e22*3450/pop_mun[k][2024]*100),'Cobertura potencial APS set/2026 (%)':min(100,(e26*3450+a26*3000)/p25*100),'Pessoas por ESF 2026':p25/e26 if e26 else None})
covdf=pd.DataFrame(cov).set_index('Município')
covdf.loc['Amapá']=[pop[2025],em.loc['Total','2022/Dez'],em.loc['Total','2026/Set'],ema.loc['Total','2026/Set'] if ema is not None else 0,emb.loc['Total','2026/Set'],min(100,em.loc['Total','2022/Dez']*3450/pop[2024]*100),min(100,(em.loc['Total','2026/Set']*3450+(ema.loc['Total','2026/Set'] if ema is not None else 0)*3000)/pop[2025]*100),pop[2025]/em.loc['Total','2026/Set']]
S['COBERTURA_APS_mun']=(covdf,'Cobertura potencial da atenção primária por município: equipes e população','Cobertura potencial = (ESF×3.450 + eAP×3.000)/população, limitada a 100% (parâmetro da PNAB/e-Gestor). Não equivale à cobertura efetiva por cadastro (SISAB).')
K['cov_ap_2022']=covdf.loc['Amapá','Cobertura potencial ESF 2022 (%)']; K['cov_ap_2026']=covdf.loc['Amapá','Cobertura potencial APS set/2026 (%)']; K['pess_esf_2026']=covdf.loc['Amapá','Pessoas por ESF 2026']
K['cov_low']=covdf.drop('Amapá').sort_values('Cobertura potencial APS set/2026 (%)').head(5)['Cobertura potencial APS set/2026 (%)'].to_dict()
K['esf_macapa_2022']=em.loc['160030 MACAPA','2022/Dez']; K['esf_macapa_2026']=em.loc['160030 MACAPA','2026/Set']; K['esf_santana_2026']=em.loc['160060 SANTANA','2026/Set']; K['pess_esf_santana']=pop_mun['SANTANA'][2025]/em.loc['160060 SANTANA','2026/Set']
be=L('e2_bench_equipe_uf_latest'); bea=L('e2_bench_equipe_uf_eap_latest')
if be is not None:
    bd=pd.DataFrame({'ESF set/2026':{ufname(i):be.loc[i,'Quantidade'] for i in be.index if i!='Total'}})
    if bea is not None: bd['eAP set/2026']=[bea.loc[[j for j in bea.index if ufname(j)==u][0],'Quantidade'] if any(ufname(j)==u for j in bea.index) else 0 for u in bd.index]
    else: bd['eAP set/2026']=0
    bd['Cobertura potencial (%)']=[min(100,(bd.loc[u,'ESF set/2026']*3450+bd.loc[u,'eAP set/2026']*3000)/pop_uf[u][2026]*100) for u in bd.index]; bd['Habitantes por ESF']=[pop_uf[u][2026]/bd.loc[u,'ESF set/2026'] for u in bd.index]
    bd.loc['BRASIL']=[be.loc['Total','Quantidade'],bea.loc['Total','Quantidade'] if bea is not None else 0,min(100,(be.loc['Total','Quantidade']*3450+(bea.loc['Total','Quantidade'] if bea is not None else 0)*3000)/popbr[2026]*100),popbr[2026]/be.loc['Total','Quantidade']]
    bd=bd.sort_values('Cobertura potencial (%)',ascending=False); S['BENCH_EQUIPES_UF']=(bd,'Equipes de Saúde da Família e cobertura potencial por UF, set/2026','')
    K['bench_cov_ap']=bd.loc['Amapá','Cobertura potencial (%)']; K['bench_cov_br']=bd.loc['BRASIL','Cobertura potencial (%)']; K['bench_hab_esf_ap']=bd.loc['Amapá','Habitantes por ESF']; K['bench_hab_esf_br']=bd.loc['BRASIL','Habitantes por ESF']; K['bench_cov_rank']=int(list(bd.drop('BRASIL').index).index('Amapá')+1)
# ---------- Habilitações ----------
hb=L('e2_hab_latest'); add('HABILITACOES_set2026',hb,'Habilitações de serviços registradas no CNES (estabelecimentos habilitados e leitos), set/2026')
add('HABILITACOES_leitos_ano',L('e2_hab_ano_leitos'),'Leitos habilitados pelo Ministério da Saúde por tipo (dez. de cada ano; set/2026)'); add('HABILITACOES_estab_ano',L('e2_hab_ano_estab'),'Estabelecimentos habilitados por tipo de habilitação (dez. de cada ano; set/2026)'); add('HABILITACOES_mun',L('e2_hab_mun_latest'),'Habilitações por município, set/2026')
hl=L('e2_hab_ano_leitos')
def hrow(df,txt): 
    r=[i for i in df.index if txt in i]; return df.loc[r[0]] if r else None
K['hab_uti_ad']={c:(hrow(hl,'UTI II ADULTO')[c] if hrow(hl,'UTI II ADULTO') is not None else 0)+(hrow(hl,'UTI I ADULTO')[c] if hrow(hl,'UTI I ADULTO') is not None else 0) for c in cols}
K['hab_uti_ped']={c:hrow(hl,'UTI II PEDIATRICA')[c] for c in cols}; K['hab_utin']={c:hrow(hl,'UTIN II')[c] for c in cols}; K['hab_ucinco']={c:hrow(hl,'UCINCO')[c] for c in cols}
ut=L1('cnes_uti_tipo_ano'); K['uti_ad_exist']={c:ut.loc['UTI adulto I',c]+ut.loc['UTI adulto II',c]+ut.loc['UTI adulto III',c] for c in cols}; K['uti_ped_exist']={c:ut.loc['UTI pediátrica II',c] for c in cols}; K['utin_exist']={c:ut.loc['UTI neonatal II',c] for c in cols}
habs=pd.DataFrame({'UTI adulto existentes (CNES)':K['uti_ad_exist'],'UTI adulto habilitadas (MS)':K['hab_uti_ad'],'UTI pediátrica existentes':K['uti_ped_exist'],'UTI pediátrica habilitadas':K['hab_uti_ped'],'UTI neonatal existentes':K['utin_exist'],'UTI neonatal habilitadas':K['hab_utin']}).T
S['UTI_existentes_x_habilitadas']=(habs,'Leitos de UTI existentes (CNES) e habilitados pelo Ministério da Saúde, 2022–2026','')
K['hab_pmae']=hb.loc[[i for i in hb.index if 'MAIS ACESSO' in i][0],'Qtde Estabelec. Habilitados'] if any('MAIS ACESSO' in i for i in hb.index) else None
K['hab_filas']=hb.loc[[i for i in hb.index if 'REDUCAO DE FILAS' in i][0],'Qtde Estabelec. Habilitados'] if any('REDUCAO DE FILAS' in i for i in hb.index) else None
K['hab_caps']=sum(hb.loc[i,'Qtde Estabelec. Habilitados'] for i in hb.index if 'CAPS' in i); K['hab_cer']=sum(hb.loc[i,'Qtde Estabelec. Habilitados'] for i in hb.index if '(CER)' in i); K['hab_ceo']=sum(hb.loc[i,'Qtde Estabelec. Habilitados'] for i in hb.index if 'ODONTOLOGICAS' in i)
# ---------- SIA atenção básica ----------
ab=L('e2_sia_ab_mun_ano_qtd'); add('SIA_AB_mun_ano',ab,'Procedimentos de atenção básica aprovados no SIA/SUS por município e ano','Desde 2021 a produção da APS é registrada no SISAB/e-SUS APS; o SIA capta apenas parte (vigilância, testes rápidos, odontologia especializada etc.).')
add('SIA_AB_forma_ano',L('e2_sia_ab_forma_ano_qtd'),'Procedimentos de atenção básica no SIA/SUS por forma de organização e ano')
sf=L('e2_sia_forma_ano_qtd'); sfv=L('e2_sia_forma_ano_valor'); add('SIA_forma_ano_qtd',sf,'Produção ambulatorial total por forma de organização e ano (quantidade)'); add('SIA_forma_ano_valor',sfv,'Produção ambulatorial total por forma de organização e ano (valor R$)')
K['ab_qtd']={y:ab.loc['Total',y] for y in yrs}
# ---------- ICSAP ----------
nl=L('e2_nr_lista_ano'); add('ICSAP_lista_morbidade_ano',nl,'Internações de residentes por Lista de Morbidade CID-10 e ano (base para ICSAP)')
nr=L('e2_nr_cap_ano'); add('INTERNACOES_res_cap_ano',nr,'Internações de residentes por capítulo CID-10 e ano')
grupos={
 '1. Doenças preveníveis por imunização e condições sensíveis (TB, coqueluche, tétano, sífilis, hepatite B)':['Tuberculose respiratória','Outras tuberculoses','Coqueluche','Outros tétanos','Sífilis congênita','Sífilis precoce','Outras sífilis','Hepatite aguda B'],
 '2. Gastroenterites infecciosas e complicações':['Diarréia e gastroenterite origem infecc presum','Outras doenças infecciosas intestinais','Cólera','Febres tifóide e paratifóide','Shiguelose','Amebíase'],
 '3. Anemia por deficiência de ferro':['Anemia por deficiência de ferro'],
 '4. Deficiências nutricionais':['Desnutrição'],
 '5. Infecções de ouvido, nariz e garganta':['Otite média e outr transt ouvid médio apóf mast','Faringite aguda e amigdalite aguda'],
 '6. Pneumonias bacterianas':['Pneumonia'],
 '7. Asma':['Asma'],
 '8. Doenças pulmonares (bronquite, enfisema, DPOC, bronquiolite)':['Bronquite enfisema e outr doenç pulm obstr crôn','Bronquite aguda e bronquiolite aguda'],
 '9. Hipertensão':['Hipertensão essencial (primária)','Outras doenças hipertensivas'],
 '10. Angina':['Angina pectoris'],
 '11. Insuficiência cardíaca':['Insuficiência cardíaca'],
 '12. Doenças cerebrovasculares':['Acid vascular cerebr não espec hemorrág ou isq','Hemorragia intracraniana','Infarto cerebral','Outras doenças cerebrovasculares','Acid vascular cerebr isquêm transit e síndr cor'],
 '13. Diabetes mellitus':['Diabetes mellitus'],
 '14. Epilepsias':['Epilepsia'],
 '15. Infecção no rim e trato urinário':['Outras doenças do aparelho urinário'],
 '16. Infecção da pele e tecido subcutâneo':['Infecções da pele e do tecido subcutâneo'],
 '17. Doença inflamatória de órgãos pélvicos femininos':['Outras doenças inflamat órgãos pélvicos femin'],
 '18. Úlcera gastrointestinal':['Úlcera gástrica e duodenal'],
}
def find(name):
    r=[i for i in nl.index if i.strip('. ').strip()==name]; return nl.loc[r[0]] if r else None
ic={}; faltas=[]
for g,names in grupos.items():
    tot=None
    for n in names:
        s=find(n)
        if s is None: faltas.append(n); continue
        tot=s.copy() if tot is None else tot+s
    ic[g]=tot if tot is not None else pd.Series(0,index=nl.columns)
icdf=pd.DataFrame(ic).T[['2022','2023','2024','2025','2026']]
icdf.loc['Total ICSAP (aproximação)']=icdf.sum()
tot_int=nr.loc['Total']; parto=nr.loc['XV.  Gravidez parto e puerpério']
icdf.loc['Total de internações de residentes']=[tot_int[c] for c in icdf.columns]; icdf.loc['Internações exceto gravidez, parto e puerpério']=[tot_int[c]-parto[c] for c in icdf.columns]
icdf.loc['% ICSAP sobre internações (exceto obstétricas)']=[icdf.loc['Total ICSAP (aproximação)',c]/(tot_int[c]-parto[c])*100 for c in icdf.columns]
icdf.loc['ICSAP por 10 mil habitantes']=[icdf.loc['Total ICSAP (aproximação)',c]/pop[int(c)]*1e4 if int(c) in pop else None for c in icdf.columns]
icdf.index.name='Grupo de causas (Lista Brasileira de ICSAP, aproximada pela Lista de Morbidade)'
S['ICSAP_grupos_ano']=(icdf,'Internações por condições sensíveis à atenção primária (ICSAP) de residentes do Amapá, por grupo, 2022–2026','Aproximação da Lista Brasileira (Portaria SAS 221/2008) a partir da Lista de Morbidade CID-10 do TABNET; grupos 15 e 19 parcialmente cobertos. Itens não encontrados: '+', '.join(faltas))
K['icsap']={c:icdf.loc['Total ICSAP (aproximação)',c] for c in icdf.columns}; K['icsap_pct']={c:icdf.loc['% ICSAP sobre internações (exceto obstétricas)',c] for c in icdf.columns}; K['icsap_10k']={c:icdf.loc['ICSAP por 10 mil habitantes',c] for c in ('2024','2025')}
K['icsap_top_2025']=icdf.drop([i for i in icdf.index if i.startswith(('Total','Interna','%','ICSAP por'))])['2025'].sort_values(ascending=False).head(6).to_dict()
K['icsap_g']={g:{c:icdf.loc[g,c] for c in ('2022','2025')} for g in ['6. Pneumonias bacterianas','2. Gastroenterites infecciosas e complicações','12. Doenças cerebrovasculares','13. Diabetes mellitus','11. Insuficiência cardíaca','16. Infecção da pele e tecido subcutâneo','15. Infecção no rim e trato urinário','9. Hipertensão','7. Asma','14. Epilepsias']}
nfx=L('e2_nr_lista_fx_2025'); add('ICSAP_lista_fx_2025',nfx,'Internações de residentes por Lista de Morbidade e faixa etária, 2025')
# ---------- Materno-infantil por município ----------
def pct(df,cols_num,label):
    out={}
    for i in df.index:
        if i=='Total': continue
        t=df.loc[i,'Total']; out[nome_mun(i)]=(sum(df.loc[i,c] for c in cols_num if c in df.columns)/t*100) if t else None
    out['Amapá']=sum(df.loc['Total',c] for c in cols_num if c in df.columns)/df.loc['Total','Total']*100
    return pd.Series(out,name=label)
mi={}
for y in ('2022','2025'):
    pn=L(f'e2_nv_mun_prenatal_{y}'); pa=L(f'e2_nv_mun_parto_{y}'); pe=L(f'e2_nv_mun_peso_{y}'); im=L(f'e2_nv_mun_idademae_{y}'); ge=L(f'e2_nv_mun_gest_{y}')
    mi[f'7+ consultas de pré-natal {y} (%)']=pct(pn,['7 ou mais consultas'],'')
    mi[f'Cesáreas {y} (%)']=pct(pa,['Cesário'],'')
    mi[f'Baixo peso ao nascer (<2.500 g) {y} (%)']=pct(pe,['Menos de 500g','500 a 999g','1000 a 1499 g','1500 a 2499 g'],'')
    mi[f'Mães de 10 a 19 anos {y} (%)']=pct(im,['10 a 14 anos','15 a 19 anos'],'')
    mi[f'Prematuros (<37 semanas) {y} (%)']=pct(ge,['Menos de 22 semanas','De 22 a 27 semanas','De 28 a 31 semanas','De 32 a 36 semanas'],'')
    add(f'SINASC_mun_prenatal_{y}',pn,f'Nascidos vivos por município de residência e consultas de pré-natal, {y}'); add(f'SINASC_mun_parto_{y}',pa,f'Nascidos vivos por município e tipo de parto, {y}'); add(f'SINASC_mun_peso_{y}',pe,f'Nascidos vivos por município e peso ao nascer, {y}'); add(f'SINASC_mun_idademae_{y}',im,f'Nascidos vivos por município e idade da mãe, {y}'); add(f'SINASC_mun_gest_{y}',ge,f'Nascidos vivos por município e duração da gestação, {y}')
    add(f'SINASC_mun_robson_{y}',L(f'e2_nv_mun_robson_{y}'),f'Nascidos vivos por município e grupo de Robson, {y}'); add(f'SINASC_mun_local_{y}',L(f'e2_nv_mun_local_{y}'),f'Nascidos vivos por município de residência e local de ocorrência, {y}')
nvm=L1('sinasc_mun_ano'); infm=L1('siminf_mun_ano')
tmi={}
for i in nvm.index:
    if i=='Total' or 'IGNORADO' in i: continue
    n=nome_mun(i); nv3=sum(nvm.loc[i,y] for y in ('2023','2024','2025')); ob3=sum(infm.loc[i,y] for y in ('2023','2024','2025')) if i in infm.index else 0
    tmi[n]={'Nascidos vivos 2025':nvm.loc[i,'2025'],'Óbitos infantis 2024':infm.loc[i,'2024'] if i in infm.index else 0,'TMI 2024 (por mil NV)':(infm.loc[i,'2024']/nvm.loc[i,'2024']*1000) if i in infm.index and nvm.loc[i,'2024'] else 0,'TMI média 2023–2025 (por mil NV)':ob3/nv3*1000 if nv3 else None}
tmi['Amapá']={'Nascidos vivos 2025':nvm.loc['Total','2025'],'Óbitos infantis 2024':infm.loc['Total','2024'],'TMI 2024 (por mil NV)':infm.loc['Total','2024']/nvm.loc['Total','2024']*1000,'TMI média 2023–2025 (por mil NV)':sum(infm.loc['Total',y] for y in ('2023','2024','2025'))/sum(nvm.loc['Total',y] for y in ('2023','2024','2025'))*1000}
midf=pd.concat([pd.DataFrame(tmi).T,pd.DataFrame(mi)],axis=1); midf.index.name='Município'
S['MATERNO_INFANTIL_mun']=(midf,'Indicadores materno-infantis por município de residência, 2022 e 2025 (SINASC) e mortalidade infantil 2023–2025 (SIM)','TMI por município com pequenos números é instável; usar a média trienal.')
K['mi']=midf.loc['Amapá'].to_dict(); K['mi_mun']=midf.drop('Amapá')
K['nv_ocor']=L('e2_nv_ocor_mun_ano'); add('SINASC_ocorrencia_mun_ano',K['nv_ocor'],'Nascidos vivos por município de OCORRÊNCIA do parto e ano')
no=K['nv_ocor']; K['ocor_pg']={y:no.loc['160053 PORTO GRANDE',y] for y in yrs}; K['ocor_santana']={y:no.loc['160060 SANTANA',y] for y in yrs}; K['ocor_macapa_pct_2025']=no.loc['160030 MACAPA','2025']/no.loc['Total','2025']*100; K['ocor_laranjal_2025']=no.loc['160027 LARANJAL DO JARI','2025']; K['ocor_oiap_2025']=no.loc['160050 OIAPOQUE','2025']
inf24=L('e2_inf_mun_fx_2024'); add('SIM_infantil_mun_componente_2024',inf24,'Óbitos infantis por município de residência e componente etário, 2024')
add('SIM_infantil_investigacao_ano',L('e2_inf_invest_ano'),'Óbitos infantis por situação de investigação e ano'); add('SIM_infantil_cap_ano',L('e2_inf_cap_ano'),'Óbitos infantis por capítulo CID-10 e ano')
ii=L('e2_inf_invest_ano'); K['inf_naoinv']={y:ii.loc['Óbito não investigado',y]/ii.loc['Total',y]*100 for y in yrs}
# materna e fetal
ma=L('e2_mat_ano'); add('SIM_materna_ano',ma,'Óbitos de mulheres em idade fértil, óbitos maternos e maternos tardios por ano')
nv=L1('sinasc_ano'); K['rmm']={y:ma.loc[y,'Óbitos maternos']/nv.loc[y,'Nascim p/resid.mãe']*1e5 for y in yrs}; K['mat']={y:ma.loc[y,'Óbitos maternos'] for y in yrs+['2026']}
add('SIM_materna_mun_ano',L('e2_mat_mun_ano'),'Óbitos maternos por município de residência e ano'); add('SIM_materna_tipo_ano',L('e2_mat_tipo_ano'),'Óbitos maternos por tipo de causa obstétrica e ano'); add('SIM_materna_grupo_ano',L('e2_mat_grupo_ano'),'Óbitos maternos por grupo de causas CID-10 e ano'); add('SIM_materna_fx_ano',L('e2_mat_fx_ano'),'Óbitos maternos por faixa etária e ano'); add('SIM_materna_invest_ano',L('e2_mat_invest_ano'),'Óbitos maternos por situação de investigação e ano')
mt=L('e2_mat_tipo_ano'); K['mat_direta_2225']=sum(mt.loc['Morte materna obstétrica direta',y] for y in yrs); K['mat_2225']=sum(mt.loc['Total',y] for y in yrs)
mg=L('e2_mat_grupo_ano'); K['mat_hipert_2225']=sum(mg.loc[[i for i in mg.index if i.startswith('O10-O16')][0],y] for y in yrs); K['mat_aborto_2225']=sum(mg.loc[[i for i in mg.index if i.startswith('O00-O08')][0],y] for y in yrs); K['mat_hemorr_2225']=sum(mg.loc[[i for i in mg.index if i.startswith('O60-O75')][0],y] for y in yrs)
bm=L('e2_bench_mat_uf_ano'); bnv=L('e2_bench_nv_uf_ano')
bmd=pd.DataFrame({'Óbitos maternos 2022–2024':{ufname(i):sum(bm.loc[i,y] for y in ('2022','2023','2024')) for i in bm.index if i!='Total'},'Nascidos vivos 2022–2024':{ufname(i):sum(bnv.loc[i,y] for y in ('2022','2023','2024')) for i in bnv.index if i!='Total'}})
bmd['RMM 2022–2024 (por 100 mil NV)']=bmd.iloc[:,0]/bmd.iloc[:,1]*1e5; bmd.loc['BRASIL']=[sum(bm.loc['Total',y] for y in ('2022','2023','2024')),sum(bnv.loc['Total',y] for y in ('2022','2023','2024')),sum(bm.loc['Total',y] for y in ('2022','2023','2024'))/sum(bnv.loc['Total',y] for y in ('2022','2023','2024'))*1e5]
bmd=bmd.sort_values('RMM 2022–2024 (por 100 mil NV)',ascending=False); S['BENCH_RMM_UF']=(bmd,'Razão de mortalidade materna por UF, triênio 2022–2024','Triênio para reduzir instabilidade de pequenos números.'); K['rmm_tri_ap']=bmd.loc['Amapá','RMM 2022–2024 (por 100 mil NV)']; K['rmm_tri_br']=bmd.loc['BRASIL','RMM 2022–2024 (por 100 mil NV)']; K['rmm_rank']=int(list(bmd.drop('BRASIL').index).index('Amapá')+1)
fe=L('e2_fet_ano'); add('SIM_fetal_ano',fe,'Óbitos fetais por ano'); K['fet']={y:fe.loc[y,'Óbitos p/Residênc'] for y in yrs}; K['fet_tx']={y:fe.loc[y,'Óbitos p/Residênc']/(fe.loc[y,'Óbitos p/Residênc']+nv.loc[y,'Nascim p/resid.mãe'])*1000 for y in yrs}
add('SIM_fetal_mun_ano',L('e2_fet_mun_ano'),'Óbitos fetais por município e ano'); add('SIM_fetal_invest_ano',L('e2_fet_invest_ano'),'Óbitos fetais por situação de investigação e ano'); add('SIM_fetal_gest_ano',L('e2_fet_gest_ano'),'Óbitos fetais por duração da gestação e ano')
fi=L('e2_fet_invest_ano'); K['fet_naoinv_2024']=fi.loc['Óbito não investigado','2024']/fi.loc['Total','2024']*100
# bench infant / cesárea / pré-natal
bi=L('e2_bench_inf_uf_ano'); bpa=L('e2_bench_nv_uf_parto_2024'); bpn=L('e2_bench_nv_uf_prenatal_2024')
bb=pd.DataFrame({'TMI 2024 (por mil NV)':{ufname(i):bi.loc[i,'2024']/bnv.loc[i,'2024']*1000 for i in bi.index if i!='Total'},'Cesáreas 2024 (%)':{ufname(i):bpa.loc[i,'Cesário']/bpa.loc[i,'Total']*100 for i in bpa.index if i!='Total'},'7+ consultas de pré-natal 2024 (%)':{ufname(i):bpn.loc[i,'7 ou mais consultas']/bpn.loc[i,'Total']*100 for i in bpn.index if i!='Total'}})
bb.loc['BRASIL']=[bi.loc['Total','2024']/bnv.loc['Total','2024']*1000,bpa.loc['Total','Cesário']/bpa.loc['Total','Total']*100,bpn.loc['Total','7 ou mais consultas']/bpn.loc['Total','Total']*100]
bb=bb.sort_values('TMI 2024 (por mil NV)',ascending=False); S['BENCH_MATERNO_INFANTIL_UF']=(bb,'Mortalidade infantil, cesáreas e pré-natal por UF, 2024','')
K['bench']={k:(bb.loc['Amapá',k],bb.loc['BRASIL',k],int(bb.drop('BRASIL')[k].rank(ascending=False)['Amapá'])) for k in bb.columns}
# painel
pr=pd.DataFrame([
 ['Equipes de Saúde da Família (ESF)',K['esf']['2022/Dez'],K['esf']['2023/Dez'],K['esf']['2024/Dez'],K['esf']['2025/Dez'],K['esf']['2026/Set'],'Cobertura potencial APS set/2026: %s%%'%fmt_br(K['cov_ap_2026'],1)],
 ['Equipes de Saúde Bucal (eSB)',K['esb']['2022/Dez'],K['esb']['2023/Dez'],K['esb']['2024/Dez'],K['esb']['2025/Dez'],K['esb']['2026/Set'],''],
 ['Equipes multiprofissionais (eNASF/eMulti)',K['enasf']['2022/Dez'],K['enasf']['2023/Dez'],K['enasf']['2024/Dez'],K['enasf']['2025/Dez'],K['enasf']['2026/Set'],''],
 ['UTI adulto habilitadas pelo MS (leitos)',K['hab_uti_ad']['2022/Dez'],K['hab_uti_ad']['2023/Dez'],K['hab_uti_ad']['2024/Dez'],K['hab_uti_ad']['2025/Dez'],K['hab_uti_ad']['2026/Set'],'Existentes set/2026: %d'%int(K['uti_ad_exist']['2026/Set'])],
 ['ICSAP (aproximação) – internações de residentes',K['icsap']['2022'],K['icsap']['2023'],K['icsap']['2024'],K['icsap']['2025'],K['icsap']['2026'],'%s%% das internações não obstétricas em 2025'%fmt_br(K['icsap_pct']['2025'],1)],
 ['Nascidos vivos (residência)',nv.loc['2022','Nascim p/resid.mãe'],nv.loc['2023','Nascim p/resid.mãe'],nv.loc['2024','Nascim p/resid.mãe'],nv.loc['2025','Nascim p/resid.mãe'],nv.loc['2026','Nascim p/resid.mãe'],'2026 parcial'],
 ['Óbitos maternos',K['mat']['2022'],K['mat']['2023'],K['mat']['2024'],K['mat']['2025'],K['mat']['2026'],'RMM 2024: %s por 100 mil NV'%fmt_br(K['rmm']['2024'],1)],
 ['Óbitos fetais',K['fet']['2022'],K['fet']['2023'],K['fet']['2024'],K['fet']['2025'],fe.loc['2026','Óbitos p/Residênc'],''],
 ['Óbitos infantis',infm.loc['Total','2022'],infm.loc['Total','2023'],infm.loc['Total','2024'],infm.loc['Total','2025'],infm.loc['Total','2026'] if '2026' in infm.columns else None,'TMI 2024: %s por mil NV'%fmt_br(K['mi']['TMI 2024 (por mil NV)'],1)],
],columns=['Indicador','2022','2023','2024','2025','2026 (parcial)','Observação']).set_index('Indicador')
S={'00_Painel_APS_MaternoInfantil':(pr,'Painel-resumo: atenção primária e saúde materno-infantil, Amapá, 2022–2026','CNES, SIH, SINASC, SIM/DATASUS.'),**S}
fontes=[('CNES – equipes e habilitações (TABNET)','cnes/cnv/equipeap.def; cnes/cnv/habap.def; cnes/cnv/equipebr.def','Competência set/2026 e dezembro de cada ano.'),('SIH/SUS – morbidade por residência (TABNET)','sih/cnv/nrap.def; sih/cnv/qrap.def','Lista de Morbidade usada para aproximar a Lista Brasileira de ICSAP.'),('SIA/SUS – produção de atenção básica','sia/cnv/qaap.def (complexidade = atenção básica)','Produção da APS migrou para o SISAB; SIA é residual.'),('SINASC e SIM (TABNET)','sinasc/cnv/nvap.def; sim/cnv/inf10ap.def, mat10ap.def, fet10ap.def; versões *uf.def','2025 preliminar; 2026 parcial.'),('IBGE','SIDRA 6579','Denominadores.'),('Limitações','e-Gestor AB/SISAB (cobertura por cadastro, indicadores do Previne/CoAPS) e SI-PNI não acessíveis.','Solicitar à SESA/COSEMS.')]
write_workbook(OUT+'/Tabelas_APS_MaternoInfantil_Amapa_2022_2026.xlsx',S,'Atenção primária, regionalização e saúde materno-infantil no Amapá, 2022–2026','Estudo complementar para a transição 2026/2027. Extração em 07/11/2026.',fontes)
# gráficos
xs=['2022','2023','2024','2025','2026*']
lines(xs,{'ESF':[K['esf'][c] for c in cols],'eSB':[K['esb'][c] for c in cols],'eMulti/eNASF':[K['enasf'][c] for c in cols],'eAP':[K['eap'][c] for c in cols]},GR+'/f01_equipes.png','Equipes cadastradas (CNES)',legend_cols=4)
cv=covdf.drop('Amapá')['Cobertura potencial APS set/2026 (%)'].sort_values(); hbars(list(cv.index),list(cv.values),GR+'/f02_cobertura_mun.png','Cobertura potencial da APS (%), set/2026',fmt=lambda v:fmt_br(v,0))
stacked(xs,{'UTI adulto habilitadas (MS)':[K['hab_uti_ad'][c] for c in cols],'UTI adulto existentes não habilitadas':[K['uti_ad_exist'][c]-K['hab_uti_ad'][c] for c in cols]},GR+'/f03_uti_habilitacao.png','Leitos de UTI adulto')
ic6=icdf.drop([i for i in icdf.index if i.startswith(('Total','Interna','%','ICSAP por'))])['2025'].sort_values().tail(10); hbars([re.sub(r'^\d+\. ','',i)[:55] for i in ic6.index],list(ic6.values),GR+'/f04_icsap_grupos.png','Internações de residentes, 2025',fs=8)
lines(['2022','2023','2024','2025'],{'ICSAP (aproximação)':[K['icsap'][y] for y in yrs],'% ICSAP sobre internações não obstétricas (x100)':[K['icsap_pct'][y]*100 for y in yrs]},GR+'/f05_icsap_serie.png','') if False else bars(['2022','2023','2024','2025'],[K['icsap'][y] for y in yrs],GR+'/f05_icsap_serie.png','Internações sensíveis à APS (residentes)')
mm=midf.drop('Amapá')['7+ consultas de pré-natal 2025 (%)'].sort_values(); hbars(list(mm.index),list(mm.values),GR+'/f06_prenatal_mun.png','% de nascidos vivos com 7+ consultas de pré-natal, 2025',fmt=lambda v:fmt_br(v,0))
tm=midf.drop('Amapá')['TMI média 2023–2025 (por mil NV)'].sort_values(); hbars(list(tm.index),list(tm.values),GR+'/f07_tmi_mun.png','Óbitos < 1 ano por mil nascidos vivos (média 2023–2025)',fmt=lambda v:fmt_br(v,1))
bars(['2022','2023','2024','2025'],[K['rmm'][y] for y in yrs],GR+'/f08_rmm.png','Óbitos maternos por 100 mil nascidos vivos',fmt=lambda v:fmt_br(v,1))
bb2=bb.drop('BRASIL')['7+ consultas de pré-natal 2024 (%)'].sort_values(); hbars(list(bb2.index)+['BRASIL'],list(bb2.values)+[bb.loc['BRASIL','7+ consultas de pré-natal 2024 (%)']],GR+'/f09_bench_prenatal.png','% de nascidos vivos com 7+ consultas de pré-natal, 2024',highlight=['Amapá','BRASIL'],figsize=(9,6.5),fmt=lambda v:fmt_br(v,1),fs=8)
pg=K['nv_ocor']; top=['160030 MACAPA','160060 SANTANA','160027 LARANJAL DO JARI','160053 PORTO GRANDE','160050 OIAPOQUE']; lines(['2022','2023','2024','2025'],{nome_mun(i):[pg.loc[i,y] for y in yrs] for i in top if i!='160030 MACAPA'},GR+'/f10_partos_ocorrencia.png','Nascidos vivos por local de ocorrência (exceto Macapá)',legend_cols=2)
json.dump({k:v for k,v in K.items() if not isinstance(v,pd.DataFrame)},open(RAW+'/kpi_e2.json','w'),ensure_ascii=False,indent=1,default=lambda o:o.item() if hasattr(o,'item') else str(o))
for k,v in K.items():
    if isinstance(v,pd.DataFrame): continue
    print(k,'=',v if not isinstance(v,dict) else {a:(round(b,2) if isinstance(b,float) else b) for a,b in v.items()})
print(midf.round(1).to_string())
