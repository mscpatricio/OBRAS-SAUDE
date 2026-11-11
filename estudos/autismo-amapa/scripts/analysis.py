import pandas as pd, numpy as np, json, statsmodels.api as sm
from scipy import stats
np.random.seed(2022)
R={}  # results
pop=pd.read_csv('data/pop_sexo_idade.csv',dtype={'cod':str})
pop=pop[pop.idade!='Total'].copy()
AGE_ORDER=['0 a 4 anos','5 a 9 anos','10 a 14 anos','15 a 19 anos','20 a 24 anos','25 a 29 anos','30 a 34 anos','35 a 39 anos','40 a 44 anos','45 a 49 anos','50 a 54 anos','55 a 59 anos','60 a 64 anos','65 a 69 anos','70 a 74 anos','75 a 79 anos','80 a 84 anos','85 a 89 anos','90 a 94 anos','95 a 99 anos','100 anos ou mais']
pop['tea']=pop['tea'].fillna(0)
pop['ag']=pop['idade'].map({a:i for i,a in enumerate(AGE_ORDER)})
# collapse 80+ to reduce noise
def ag80(a): return a if a<16 else 16
pop['ag16']=pop['ag'].map(ag80)
LAB16=AGE_ORDER[:16]+['80 anos ou mais']
def wilson(x,n,z=1.96):
    x=np.asarray(x,float); n=np.asarray(n,float); p=x/n
    d=1+z*z/n; c=p+z*z/(2*n); h=z*np.sqrt(p*(1-p)/n+z*z/(4*n*n))
    return (c-h)/d,(c+h)/d

# ---------- 1. UF comparison with direct standardization (standard = Brazil pop by sex x age16)
sex=pop[pop.sexo.isin(['Homens','Mulheres'])]
std=sex[sex.nivel=='BR'].groupby(['sexo','ag16'])['pop'].sum(); std=std/std.sum()
def direct(df):
    g=df.groupby(['sexo','ag16'])[['pop','tea']].sum(); r=(g.tea/g['pop'])
    return float((r*std.reindex(r.index)).sum()*100)
ufs=[]
for cod,g in sex[sex.nivel=='UF'].groupby('cod'):
    t=g[['pop','tea']].sum(); ufs.append(dict(cod=cod,nome=g.nome.iloc[0],pop=t['pop'],tea=t.tea,bruta=t.tea/t['pop']*100,padronizada=direct(g)))
ufs=pd.DataFrame(ufs).sort_values('padronizada',ascending=False); ufs['rank_pad']=range(1,len(ufs)+1)
ufs=ufs.sort_values('bruta',ascending=False); ufs['rank_bruta']=range(1,len(ufs)+1)
brt=sex[sex.nivel=='BR'][['pop','tea']].sum()
R['br']=dict(pop=float(brt['pop']),tea=float(brt.tea),pct=float(brt.tea/brt['pop']*100))
regs=[]
for cod,g in sex[sex.nivel=='REG'].groupby('cod'):
    t=g[['pop','tea']].sum(); regs.append(dict(cod=cod,nome=g.nome.iloc[0],pop=t['pop'],tea=t.tea,bruta=t.tea/t['pop']*100,padronizada=direct(g)))
regs=pd.DataFrame(regs)
ufs.to_csv('data/out_uf_ranking.csv',index=False); regs.to_csv('data/out_regioes.csv',index=False)
R['uf_ranking']=ufs.to_dict('records'); R['regioes']=regs.to_dict('records')
ap_row=ufs[ufs.cod=='16'].iloc[0]; R['ap']=dict(pop=float(ap_row['pop']),tea=float(ap_row.tea),pct=float(ap_row.bruta),pad=float(ap_row.padronizada),rank_bruta=int(ap_row.rank_bruta),rank_pad=int(ap_row.rank_pad))
R['ap']['razao_br']=R['ap']['pct']/R['br']['pct']; R['ap']['razao_br_pad']=R['ap']['pad']/R['br']['pct']
R['ap']['um_em']=1/(R['ap']['pct']/100)

# ---------- 2. AP age-sex profile vs Brazil
def profile(df):
    g=df.groupby(['ag16','sexo'])[['pop','tea']].sum().reset_index()
    g['pct']=g.tea/g['pop']*100; lo,hi=wilson(g.tea,g['pop']); g['lo']=lo*100; g['hi']=hi*100; g['idade']=g.ag16.map(lambda i:LAB16[i]); return g
prof_ap=profile(pop[(pop.nivel=='UF')&(pop.cod=='16')]); prof_br=profile(pop[pop.nivel=='BR'])
prof_ap['nivel']='AP'; prof_br['nivel']='BR'
prof=pd.concat([prof_ap,prof_br]); prof.to_csv('data/out_perfil_idade_sexo.csv',index=False)
R['perfil']=prof.to_dict('records')
# M:F ratio
def mf(df):
    w=df.pivot(index='ag16',columns='sexo',values='pct'); return (w['Homens']/w['Mulheres'])
R['mf_ap']=mf(prof_ap).round(2).to_dict(); R['mf_br']=mf(prof_br).round(2).to_dict()
tot_ap=prof_ap[prof_ap.sexo=='Total'].set_index('idade'); R['ap_idade_total']=tot_ap[['pop','tea','pct','lo','hi']].to_dict('index')
tot_br=prof_br[prof_br.sexo=='Total'].set_index('idade'); R['br_idade_total']=tot_br[['pop','tea','pct']].to_dict('index')
sx=prof_ap[prof_ap.ag16>=0].groupby('sexo')[['pop','tea']].sum(); sx['pct']=sx.tea/sx['pop']*100; R['ap_sexo']=sx.to_dict('index')
sxb=prof_br.groupby('sexo')[['pop','tea']].sum(); sxb['pct']=sxb.tea/sxb['pop']*100; R['br_sexo']=sxb.to_dict('index')
# broad groups
def broad(df,bins):
    out={}
    for name,(a,b) in bins.items():
        s=df[(df.sexo=='Total')&(df.ag16>=a)&(df.ag16<=b)][['pop','tea']].sum(); out[name]=dict(pop=float(s['pop']),tea=float(s.tea),pct=float(s.tea/s['pop']*100))
    return out
BINS={'0-4':(0,0),'5-9':(1,1),'10-14':(2,2),'15-19':(3,3),'0-14':(0,2),'0-19':(0,3),'20-59':(4,11),'60+':(12,16)}
R['ap_broad']=broad(prof_ap,BINS); R['br_broad']=broad(prof_br,BINS)
# share of cases by broad group
R['ap_share_0_19']=R['ap_broad']['0-19']['tea']/R['ap']['tea']*100

# ---------- 3. race
raca=pd.read_csv('data/raca.csv',dtype={'cod':str})
rc=raca[((raca.nivel=='UF')&(raca.cod=='16'))|(raca.nivel=='BR')].copy(); rc['pct_calc']=rc.tea/rc['pop']*100
lo,hi=wilson(rc.tea.fillna(0),rc['pop']); rc['lo']=lo*100; rc['hi']=hi*100
R['raca']=rc.to_dict('records'); rc.to_csv('data/out_raca.csv',index=False)

# ---------- 4. municipalities: indirect standardization + empirical Bayes
mun=pop[pop.nivel=='MUN']
apr=sex[(sex.nivel=='UF')&(sex.cod=='16')].groupby(['sexo','ag16'])[['pop','tea']].sum(); apr['rate']=apr.tea/apr['pop']
m=mun[mun.sexo.isin(['Homens','Mulheres'])].copy(); m=m.merge(apr['rate'].reset_index(),on=['sexo','ag16']); m['esp']=m['pop']*m['rate']
M=m.groupby(['cod','nome']).agg(pop=('pop','sum'),obs=('tea','sum'),esp=('esp','sum')).reset_index()
M['nome']=M.nome.str.replace(' - AP','',regex=False)
M['bruta']=M.obs/M['pop']*100; M['spr']=M.obs/M.esp
# exact Poisson CI for SPR
M['spr_lo']=stats.chi2.ppf(0.025,2*M.obs)/2/M.esp; M['spr_hi']=stats.chi2.ppf(0.975,2*(M.obs+1))/2/M.esp
# empirical Bayes gamma-Poisson (method of moments, Marshall 1991 / Clayton-Kaldor)
mu=M.obs.sum()/M.esp.sum(); s2=((M.obs/M.esp-mu)**2*M.esp).sum()/M.esp.sum(); phi=max(s2-mu/M.esp.mean(),1e-6)
alpha=mu*mu/phi; beta=mu/phi
M['spr_eb']=(M.obs+alpha)/(M.esp+beta)
M['eb_lo']=stats.gamma.ppf(0.025,M.obs+alpha,scale=1/(M.esp+beta)); M['eb_hi']=stats.gamma.ppf(0.975,M.obs+alpha,scale=1/(M.esp+beta))
ap_rate=R['ap']['pct']
M['taxa_eb']=M.spr_eb*ap_rate; M['taxa_eb_lo']=M.eb_lo*ap_rate; M['taxa_eb_hi']=M.eb_hi*ap_rate
M['padronizada']=M.spr*ap_rate
M['share_casos']=M.obs/M.obs.sum()*100; M['share_pop']=M['pop']/M['pop'].sum()*100
# children by municipality
k=mun[(mun.sexo=='Total')].copy(); k['nome']=k.nome.str.replace(' - AP','',regex=False)
kids=k[k.ag16<=2].groupby('nome').agg(pop_0_14=('pop','sum'),tea_0_14=('tea','sum')).reset_index(); kids['pct_0_14']=kids.tea_0_14/kids.pop_0_14*100
k59=k[k.ag16==1].groupby('nome').agg(pop_5_9=('pop','sum'),tea_5_9=('tea','sum')).reset_index(); k59['pct_5_9']=k59.tea_5_9/k59.pop_5_9*100
M=M.merge(kids,on='nome').merge(k59,on='nome')
est=pd.read_csv('data/estudantes.csv',dtype={'cod':str}); em=est[(est.nivel=='MUN')&(est.sexo=='Total')&(est.idade=='Total')][['nome','est','tea','pct']].copy(); em['nome']=em.nome.str.replace(' - AP','',regex=False); em.columns=['nome','estudantes','estudantes_tea','pct_estudantes_tea']
M=M.merge(em,on='nome',how='left')
M=M.sort_values('taxa_eb',ascending=False); M.to_csv('data/out_municipios.csv',index=False)
R['mun']=M.to_dict('records'); R['eb_params']=dict(mu=float(mu),phi=float(phi),alpha=float(alpha),beta=float(beta))
# heterogeneity test
chi=((M.obs-M.esp)**2/M.esp).sum(); R['mun_hetero']=dict(chi2=float(chi),df=len(M)-1,p=float(1-stats.chi2.cdf(chi,len(M)-1)))

# ---------- 5. education
tx=pd.read_csv('data/tx_escolarizacao_sexo.csv',dtype={'cod':str}); txs=tx[((tx.nivel=='UF')&(tx.cod=='16'))|(tx.nivel=='BR')]
R['tx_escolarizacao']=txs.to_dict('records'); txs.to_csv('data/out_tx_escolarizacao.csv',index=False)
txr=pd.read_csv('data/tx_escolarizacao_raca.csv',dtype={'cod':str}); R['tx_escolarizacao_raca']=txr[((txr.nivel=='UF')&(txr.cod=='16'))|(txr.nivel=='BR')].to_dict('records')
e=est[((est.nivel=='UF')&(est.cod=='16'))|(est.nivel=='BR')]; R['estudantes']=e.to_dict('records')
ins=pd.read_csv('data/instrucao25.csv',dtype={'cod':str}); i2=ins[((ins.nivel=='UF')&(ins.cod=='16'))|(ins.nivel=='BR')].copy()
# distribution of education among TEA 25+ vs general
def dist(df,col):
    t=df[(df.sexo=='Total')&(df.instrucao!='Total')]; tot=df[(df.sexo=='Total')&(df.instrucao=='Total')][col].iloc[0]; return dict(zip(t.instrucao,(t[col]/tot*100).round(1)))
R['instrucao']={}
for lvl,g in i2.groupby('nivel'):
    R['instrucao'][lvl]=dict(tea=dist(g,'tea'),geral=dist(g,'pop25'))
# UF ranking of schooling rate for autism
txu=tx[(tx.nivel=='UF')&(tx.sexo=='Total')&(tx.idade=='Total')].sort_values('tx_tea',ascending=False); txu['rank']=range(1,len(txu)+1)
R['tx_uf_rank']=txu[['nome','tx_tea','tx_total','rank']].to_dict('records')

# ---------- 6. cohort analysis (Poisson GLM on log prevalence ~ birth cohort), ages 10-59 (born 1963-2012)
def cohort_fit(df,label):
    g=df[(df.sexo=='Total')&(df.ag16>=2)&(df.ag16<=11)].copy()
    g['coorte']=2022-(g.ag16*5+2.5)  # birth-year midpoint
    X=sm.add_constant(g.coorte-2000); mod=sm.GLM(g.tea,X,family=sm.families.Poisson(),offset=np.log(g['pop'])).fit(scale='X2')
    b=mod.params.iloc[1]; se=mod.bse.iloc[1]
    return dict(label=label,beta=float(b),se=float(se),growth_pct=float((np.exp(b)-1)*100),ci=[float((np.exp(b-1.96*se)-1)*100),float((np.exp(b+1.96*se)-1)*100)],doubling=float(np.log(2)/b),
                points=g[['idade','coorte','pop','tea']].assign(pct=g.tea/g['pop']*100).to_dict('records'),pred=[float(np.exp(mod.params.iloc[0]+b*(c-2000))*100) for c in range(1960,2023)])
R['coorte_ap']=cohort_fit(prof_ap,'Amapá'); R['coorte_br']=cohort_fit(prof_br,'Brasil')
# also fit for ages 10-39 (recent cohorts) to capture recent acceleration
def cohort_fit2(df,lo,hi):
    g=df[(df.sexo=='Total')&(df.ag16>=lo)&(df.ag16<=hi)].copy(); g['coorte']=2022-(g.ag16*5+2.5)
    X=sm.add_constant(g.coorte-2000); mod=sm.GLM(g.tea,X,family=sm.families.Poisson(),offset=np.log(g['pop'])).fit(scale='X2'); b=mod.params.iloc[1]; se=mod.bse.iloc[1]
    return dict(growth_pct=float((np.exp(b)-1)*100),ci=[float((np.exp(b-1.96*se)-1)*100),float((np.exp(b+1.96*se)-1)*100)],beta=float(b),se=float(se))
R['coorte_ap_10_39']=cohort_fit2(prof_ap,2,7); R['coorte_br_10_39']=cohort_fit2(prof_br,2,7)
R['coorte_ap_5_39']=cohort_fit2(prof_ap,1,7); R['coorte_br_5_39']=cohort_fit2(prof_br,1,7)

# ---------- 7. projections
pr=pd.read_csv('data/projecao2024_ap_br.csv'); prA=pr[pr.sigla=='AP']
years=list(range(2022,2041))
def popmat(sexo):  # ages 0..90 x years
    d=prA[prA.sexo==sexo].sort_values('idade'); return d[[str(y) for y in years]].to_numpy(float)
P={'Homens':popmat('Homens'),'Mulheres':popmat('Mulheres')}
R['proj_pop_total']={y:float(P['Homens'][:,i].sum()+P['Mulheres'][:,i].sum()) for i,y in enumerate(years)}
R['proj_pop_2022_vs_censo']=dict(proj=R['proj_pop_total'][2022],censo=R['ap']['pop'],ratio=R['proj_pop_total'][2022]/R['ap']['pop'])
# 2022 rates by sex & age16 -> single ages
rate22={s:prof_ap[prof_ap.sexo==s].set_index('ag16')['pct'].to_numpy()/100 for s in ['Homens','Mulheres']}
def age16_of(a): return min(a//5,16)
F04=np.array([0.30,0.55,0.80,0.95,1.0])  # ascertainment ramp ages 0..4 (mean ~0.72 ~ observed 0-4/5-9 ratio)
R['f04_mean']=float(F04.mean()); R['obs_ratio_04_59']=float(R['ap_broad']['0-4']['pct']/R['ap_broad']['5-9']['pct'])
def project(scn, rates=rate22, r=None, K=None, catchup=0.0):
    """returns dict year-> array[age] of cases by sex; scn: 'S1' constant; 'S2' cohort model"""
    out={}
    for s in ['Homens','Mulheres']:
        rt=rates[s]; cases=np.zeros((91,len(years)))
        mature_04=rt[0]/F04.mean()  # mature level of 2018-2022 cohort
        for j,t in enumerate(years):
            for a in range(91):
                if scn=='S1': rate=rt[age16_of(a)]
                else:
                    a22=a-(t-2022)  # age in 2022
                    if a22>=5:  # observed cohort: carry 2022 rate forward (+ optional adult catch-up)
                        base=rt[age16_of(a22)]
                        if catchup>0 and a22>=20:
                            target=rt[1]  # converge toward 5-9 level
                            base=base+(target-base)*(1-np.exp(-catchup*(t-2022)))
                        rate=base
                    else:
                        c=t-a  # birth year
                        if c<=2022: mat=mature_04
                        else: mat=K/(1+((K-mature_04)/mature_04)*np.exp(-r*(c-2020)))
                        rate=mat*(F04[a] if a<5 else 1.0)
                cases[a,j]=P[s][a,j]*rate
        out[s]=cases
    return out
def summarize(cs):
    tot=cs['Homens']+cs['Mulheres']; return dict(total=tot.sum(0),a0_4=tot[0:5].sum(0),a5_9=tot[5:10].sum(0),a10_14=tot[10:15].sum(0),a15_19=tot[15:20].sum(0),a0_14=tot[0:15].sum(0),a4_17=tot[4:18].sum(0),a6_14=tot[6:15].sum(0),a15_17=tot[15:18].sum(0),a18_24=tot[18:25].sum(0),a20_59=tot[20:60].sum(0),a60p=tot[60:].sum(0),a18p=tot[18:].sum(0))
g_full=R['coorte_ap']['beta']; g_rec=R['coorte_ap_10_39']['beta']
SCN={'S1':dict(scn='S1'),
     'S2':dict(scn='S2',r=0.0,K=0.05),
     'S3':dict(scn='S2',r=g_full,K=0.06),
     'S4':dict(scn='S2',r=g_full,K=0.06,catchup=0.05)}
R['scn_params']={k:{kk:(float(vv) if isinstance(vv,(int,float,np.floating)) else vv) for kk,vv in v.items()} for k,v in SCN.items()}
proj={}
for k,v in SCN.items():
    s=summarize(project(**v)); proj[k]={kk:[float(x) for x in vv] for kk,vv in s.items()}
R['proj']=proj; R['proj_years']=years
# prevalence per year
R['proj_prev']={k:[proj[k]['total'][i]/R['proj_pop_total'][y]*100 for i,y in enumerate(years)] for k in SCN}
# mature levels by sex
R['mature_04']={s:float(rate22[s][0]/F04.mean()*100) for s in rate22}
# ---- Monte Carlo on S3-type cohort model (uncertainty: sampling (deff=2), growth rate, ceiling)
NS=600; sims=np.zeros((NS,len(years))); sims_014=np.zeros((NS,len(years))); sims_59=np.zeros((NS,len(years)))
cnt={s:prof_ap[prof_ap.sexo==s].set_index('ag16') for s in ['Homens','Mulheres']}
for i in range(NS):
    rs={}
    for s in cnt:
        n=cnt[s]['pop'].to_numpy()/2.0; x=cnt[s]['tea'].to_numpy()/2.0  # design effect 2
        p=np.random.beta(x+0.5,n-x+0.5); rs[s]=p
    r=np.random.normal(g_full,R['coorte_ap']['se']); K=np.random.uniform(0.04,0.07); cu=np.random.uniform(0,0.05)
    sm_=summarize(project('S2',rates=rs,r=max(r,0),K=K,catchup=cu)); sims[i]=sm_['total']; sims_014[i]=sm_['a0_14']; sims_59[i]=sm_['a5_9']
def q(a): return {k:[float(x) for x in np.percentile(a,p,axis=0)] for k,p in [('p5',5),('p10',10),('p25',25),('p50',50),('p75',75),('p90',90),('p95',95)]}
R['mc']=dict(total=q(sims),a0_14=q(sims_014),a5_9=q(sims_59),n=NS)
# students projection (schooling rates AP for TEA by age group, held constant)
txap=txs[(txs.nivel=='UF')&(txs.sexo=='Total')].set_index('idade')['tx_tea']/100
R['proj_estudantes']={k:[float(proj[k]['a6_14'][i]*txap['6 a 14 anos']+proj[k]['a15_17'][i]*txap['15 a 17 anos']+proj[k]['a18_24'][i]*txap['18 a 24 anos']) for i in range(len(years))] for k in SCN}
# municipal indicative projection 2030/2040 (share of state pop by age16 constant; SPR_eb applied)
share=m.groupby(['nome','ag16'])['pop'].sum()/m.groupby('ag16')['pop'].sum()
S1c=project('S1'); S3c=project(**SCN['S3'])
def mun_proj(cases,yr):
    j=years.index(yr); tot=cases['Homens']+cases['Mulheres']; by16=np.array([tot[a,j] for a in range(91)]); 
    g=pd.Series(by16).groupby([age16_of(a) for a in range(91)]).sum()
    out={}
    for nm in M.nome:
        sh=share.loc[nm+' - AP']; out[nm]=float(sum(g[i]*sh.get(i,0) for i in g.index))
    return out
mp={}
for yr in [2022,2030,2040]:
    a=mun_proj(S1c,yr); b=mun_proj(S3c,yr)
    for nm in a: mp.setdefault(nm,{})[f'S1_{yr}']=a[nm]*float(M.set_index('nome').loc[nm,'spr_eb']); mp[nm][f'S3_{yr}']=b[nm]*float(M.set_index('nome').loc[nm,'spr_eb'])
R['mun_proj']=mp
json.dump(R,open('data/results.json','w'),ensure_ascii=False,indent=1,default=float)
# prints
print('AP',R['ap']); print('BR',R['br'])
print(ufs[['nome','bruta','padronizada','rank_bruta','rank_pad']].head(8).to_string())
print('coorte AP',{k:R['coorte_ap'][k] for k in ['growth_pct','ci','doubling']},'BR',{k:R['coorte_br'][k] for k in ['growth_pct','ci']})
print('coorte 10-39 AP',R['coorte_ap_10_39'],'BR',R['coorte_br_10_39'])
print('mature04',R['mature_04'],'obs ratio',R['obs_ratio_04_59'])
for k in SCN: print(k,[round(proj[k]['total'][years.index(y)]) for y in [2022,2025,2030,2035,2040]], [round(R['proj_prev'][k][years.index(y)],2) for y in [2022,2030,2040]])
print('MC p50',[round(R['mc']['total']['p50'][years.index(y)]) for y in [2022,2030,2040]],'p5',[round(R['mc']['total']['p5'][years.index(y)]) for y in [2030,2040]],'p95',[round(R['mc']['total']['p95'][years.index(y)]) for y in [2030,2040]])
print(M[['nome','pop','obs','esp','bruta','spr','spr_eb','taxa_eb','taxa_eb_lo','taxa_eb_hi','pct_5_9','estudantes_tea']].round(2).to_string())
print('hetero',R['mun_hetero'],'eb',R['eb_params'])
print('mf',R['mf_ap']); print('sexo',R['ap_sexo'])
