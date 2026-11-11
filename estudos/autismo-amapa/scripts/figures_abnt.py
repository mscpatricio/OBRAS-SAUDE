import json, pandas as pd, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
R=json.load(open('data/results.json'))
C={'ap':'#2a78d6','br':'#eb6834','c3':'#1baf7a','c4':'#eda100','ink':'#0b0b0b','ink2':'#52514e','grid':'#e6e5e1','light':'#9ec5f4','surf':'#fcfcfb','band':'#cde2fb','band2':'#86b6ef'}
plt.rcParams.update({'font.family':'Liberation Sans','font.size':9,'axes.edgecolor':C['ink2'],'axes.labelcolor':C['ink2'],'xtick.color':C['ink2'],'ytick.color':C['ink2'],'axes.spines.top':False,'axes.spines.right':False,'axes.grid':True,'grid.color':C['grid'],'grid.linewidth':0.6,'axes.axisbelow':True,'figure.facecolor':'white','axes.facecolor':'white','legend.frameon':False})
def save(fig,name): fig.tight_layout(); fig.savefig(f'fig_abnt/{name}.png',dpi=200); plt.close(fig)
def fmt(x,d=1): return f'{x:,.{d}f}'.replace(',','X').replace('.',',').replace('X','.')
years=R['proj_years']
# 1 UF ranking
uf=pd.DataFrame(R['uf_ranking']).sort_values('padronizada')
fig,ax=plt.subplots(figsize=(7.2,6.2))
cols=[C['ap'] if c=='16' else C['light'] for c in uf.cod]
ax.barh(uf.nome,uf.padronizada,color=cols,height=0.72)
ax.axvline(R['br']['pct'],color=C['ink2'],lw=1,ls='--'); ax.text(R['br']['pct']+0.01,-0.9,f"Brasil {fmt(R['br']['pct'],2)}%",color=C['ink2'],fontsize=8,va='center')
for i,(v,b) in enumerate(zip(uf.padronizada,uf.bruta)):
    ax.text(v+0.01,i,f"{fmt(v,2)}%  (bruta {fmt(b,2)}%)",va='center',fontsize=7,color=C['ink2'] if uf.cod.iloc[i]!='16' else C['ink'])
ax.set_xlim(0,1.75); ax.set_xlabel('Prevalência padronizada por idade e sexo (%) — padrão: Brasil 2022'); ax.grid(axis='y',visible=False)
save(fig,'fig01_uf_ranking')
# 2 age-sex profile
prof=pd.DataFrame(R['perfil']); lab=[l.replace(' anos','').replace(' a ','–').replace(' ou mais','+') for l in prof[prof.nivel=='AP'][prof.sexo=='Total'].idade]
fig,axs=plt.subplots(1,3,figsize=(10,3.6),sharey=True)
for ax,s in zip(axs,['Total','Homens','Mulheres']):
    a=prof[(prof.nivel=='AP')&(prof.sexo==s)].sort_values('ag16'); b=prof[(prof.nivel=='BR')&(prof.sexo==s)].sort_values('ag16')
    x=np.arange(len(a)); ax.fill_between(x,a.lo,a.hi,color=C['band'],alpha=0.8,lw=0)
    ax.plot(x,a.pct,color=C['ap'],lw=2,marker='o',ms=3.5,label='Amapá (IC95%)'); ax.plot(x,b.pct,color=C['br'],lw=2,label='Brasil')
    ax.set_xticks(x); ax.set_xticklabels(lab,rotation=90,fontsize=7); ax.grid(axis='x',visible=False)
    ax.text(0.5,a.pct.iloc[1]+0.3,f"{fmt(a.pct.iloc[1])}%",color=C['ap'],fontsize=8)
axs[0].set_ylabel('% da população com diagnóstico de autismo'); axs[0].legend(loc='upper right',fontsize=8)
save(fig,'fig02_perfil_idade_sexo')
# 3 M:F ratio
fig,ax=plt.subplots(figsize=(7.2,3.2))
mf_ap=[R['mf_ap'][str(i)] for i in range(17)]; mf_br=[R['mf_br'][str(i)] for i in range(17)]
x=np.arange(17); ax.bar(x-0.2,mf_ap,0.38,color=C['ap'],label='Amapá'); ax.bar(x+0.2,mf_br,0.38,color=C['br'],label='Brasil')
ax.axhline(1,color=C['ink2'],lw=0.8); ax.set_xticks(x); ax.set_xticklabels(lab,rotation=90,fontsize=7); ax.set_ylabel('Razão de prevalência homens/mulheres'); ax.grid(axis='x',visible=False); ax.legend(fontsize=8)
save(fig,'fig03_razao_sexo')
# 4 race
rc=pd.DataFrame(R['raca']); order=['Branca','Preta','Parda','Amarela','Indígena','Total']
fig,ax=plt.subplots(figsize=(7.2,3.4)); x=np.arange(len(order))
a=rc[rc.nivel=='UF'].set_index('raca').loc[order]; b=rc[rc.nivel=='BR'].set_index('raca').loc[order]
ax.bar(x-0.2,a.pct_calc,0.38,color=C['ap'],label='Amapá'); ax.errorbar(x-0.2,a.pct_calc,yerr=[a.pct_calc-a.lo,a.hi-a.pct_calc],fmt='none',ecolor=C['ink2'],lw=1,capsize=2)
ax.bar(x+0.2,b.pct_calc,0.38,color=C['br'],label='Brasil')
for i,(v,w) in enumerate(zip(a.pct_calc,b.pct_calc)): ax.text(i-0.2,v+0.12,fmt(v,2),ha='center',fontsize=7,color=C['ink']); ax.text(i+0.2,w+0.05,fmt(w,2),ha='center',fontsize=7,color=C['ink2'])
ax.set_xticks(x); ax.set_xticklabels(order); ax.set_ylabel('% com diagnóstico de autismo'); ax.grid(axis='x',visible=False); ax.legend(fontsize=8)
save(fig,'fig04_raca')
# 5 municipalities EB
M=pd.DataFrame(R['mun']).sort_values('taxa_eb'); M['nome']=M.nome.replace({'Amapá':'Amapá (município)'})
fig,ax=plt.subplots(figsize=(7.2,5.2)); y=np.arange(len(M))
ax.hlines(y,M.taxa_eb_lo,M.taxa_eb_hi,color=C['band2'],lw=3)
ax.scatter(M.bruta,y,facecolors='white',edgecolors=C['ink2'],s=28,zorder=3,label='Taxa bruta')
ax.scatter(M.taxa_eb,y,color=C['ap'],s=34,zorder=4,label='Taxa suavizada (Bayes empírico) e IC95%')
ax.axvline(R['ap']['pct'],color=C['br'],lw=1.2,ls='--'); ax.text(R['ap']['pct']+0.02,len(M)-0.6,f"Amapá {fmt(R['ap']['pct'],2)}%",color=C['br'],fontsize=8)
ax.set_yticks(y); ax.set_yticklabels(M.nome); ax.set_xlabel('% com diagnóstico de autismo (padronizada indiretamente por idade e sexo)'); ax.grid(axis='y',visible=False); ax.legend(loc='lower right',fontsize=8)
save(fig,'fig05_municipios')
# 6 cases by municipality
M2=pd.DataFrame(R['mun']).sort_values('obs'); M2['nome']=M2.nome.replace({'Amapá':'Amapá (município)'})
fig,ax=plt.subplots(figsize=(7.2,4.6)); ax.barh(M2.nome,M2.obs,color=C['ap'],height=0.7)
for i,(v,s) in enumerate(zip(M2.obs,M2.share_casos)): ax.text(v+40,i,f"{fmt(v,0)}  ({fmt(s,1)}%)",va='center',fontsize=7.5,color=C['ink2'])
ax.set_xlim(0,M2.obs.max()*1.25); ax.set_xlabel('Pessoas com diagnóstico de autismo (número e % do total estadual)'); ax.grid(axis='y',visible=False)
save(fig,'fig06_mun_casos')
# 7 schooling
tx=pd.DataFrame(R['tx_escolarizacao']); ages=['6 a 14 anos','15 a 17 anos','18 a 24 anos','25 anos ou mais']
a=tx[(tx.nivel=='UF')&(tx.sexo=='Total')].set_index('idade').loc[ages]; b=tx[(tx.nivel=='BR')&(tx.sexo=='Total')].set_index('idade').loc[ages]
fig,ax=plt.subplots(figsize=(7.2,3.6)); x=np.arange(4)
ax.bar(x-0.27,a.tx_tea,0.26,color=C['ap'],label='Amapá — pessoas com autismo'); ax.bar(x,a.tx_total,0.26,color=C['light'],label='Amapá — população geral'); ax.bar(x+0.27,b.tx_tea,0.26,color=C['br'],label='Brasil — pessoas com autismo')
for xi,v in zip(x-0.27,a.tx_tea): ax.text(xi,v+1.5,fmt(v),ha='center',fontsize=7)
for xi,v in zip(x,a.tx_total): ax.text(xi,v+1.5,fmt(v),ha='center',fontsize=7,color=C['ink2'])
for xi,v in zip(x+0.27,b.tx_tea): ax.text(xi,v+1.5,fmt(v),ha='center',fontsize=7,color=C['ink2'])
ax.set_xticks(x); ax.set_xticklabels([s.replace(' anos','') for s in ages]); ax.set_ylabel('Taxa de escolarização (%)'); ax.set_ylim(0,110); ax.grid(axis='x',visible=False); ax.legend(fontsize=7.5,loc='upper right')
save(fig,'fig07_escolarizacao')
# 8 cohort
fig,ax=plt.subplots(figsize=(7.2,3.8))
for key,col,lab_ in [('coorte_ap',C['ap'],'Amapá'),('coorte_br',C['br'],'Brasil')]:
    d=R[key]; pts=pd.DataFrame(d['points']); ax.scatter(pts.coorte,pts.pct,color=col,s=30,zorder=3,label=f"{lab_} — observado (idades 10–59)")
    ax.plot(range(1960,2023),d['pred'],color=col,lw=1.8,ls='--',label=f"{lab_} — tendência ajustada: +{fmt(d['growth_pct'])}%/ano")
pa=pd.DataFrame(R['perfil']); yo=pa[(pa.nivel=='AP')&(pa.sexo=='Total')&(pa.ag16<=1)]
ax.scatter([2015,2020],yo.sort_values('ag16').pct,facecolors='white',edgecolors=C['ap'],s=36,zorder=3,label='Amapá — coortes 2013–2022 (detecção ainda incompleta nos 0–4)')
ax.set_xlabel('Coorte de nascimento (ponto médio)'); ax.set_ylabel('% com diagnóstico de autismo em 2022'); ax.legend(fontsize=7.5,loc='upper left'); ax.set_ylim(0,4)
save(fig,'fig08_coorte')
# 9 projections
fig,ax=plt.subplots(figsize=(7.6,4.2)); mc=R['mc']['total']
ax.fill_between(years,mc['p5'],mc['p95'],color=C['band'],alpha=0.7,lw=0,label='Monte Carlo — intervalo 90%')
ax.fill_between(years,mc['p25'],mc['p75'],color=C['band2'],alpha=0.6,lw=0,label='Monte Carlo — intervalo 50%')
names={'S1':'S1 Prevalência constante (efeito demográfico)','S2':'S2 Estabilização nas coortes recentes','S3':'S3 Tendência de coorte plena','S4':'S4 Tendência plena + diagnóstico tardio em adultos'}
for k,col in zip(['S1','S2','S3','S4'],[C['ink2'],C['c3'],C['ap'],C['br']]):
    ax.plot(years,R['proj'][k]['total'],color=col,lw=2,label=names[k]); ax.text(2040.3,R['proj'][k]['total'][-1],fmt(R['proj'][k]['total'][-1],0),fontsize=7.5,color=col,va='center')
ax.scatter([2022],[R['ap']['tea']],color=C['ink'],zorder=5,s=30); ax.text(2022.3,R['ap']['tea']-900,f"Censo 2022: {fmt(R['ap']['tea'],0)}",fontsize=7.5)
ax.set_xlim(2022,2042); ax.set_xticks(range(2022,2041,2)); ax.set_ylabel('Pessoas com diagnóstico de autismo'); ax.legend(fontsize=7.5,loc='upper left'); ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v,p: fmt(v,0)))
save(fig,'fig09_projecoes')
# 10 age composition S3
fig,ax=plt.subplots(figsize=(7.2,3.8)); grp=[('a0_4','0–4'),('a5_9','5–9'),('a10_14','10–14'),('a15_19','15–19'),('a20_59','20–59'),('a60p','60+')]
seq=['#cde2fb','#9ec5f4','#6da7ec','#3987e5','#256abf','#184f95']; yrs=[2022,2025,2030,2035,2040]; x=np.arange(len(yrs)); bottom=np.zeros(len(yrs))
for (k,l),col in zip(grp,seq):
    v=np.array([R['proj']['S3'][k][years.index(y)] for y in yrs]); ax.bar(x,v,0.6,bottom=bottom,color=col,label=l,edgecolor='white',lw=1)
    for xi,b_,vv in zip(x,bottom,v): 
        if vv>900: ax.text(xi,b_+vv/2,fmt(vv,0),ha='center',va='center',fontsize=7,color='white' if col in seq[3:] else C['ink'])
    bottom+=v
ax.set_xticks(x); ax.set_xticklabels(yrs); ax.set_ylabel('Pessoas com diagnóstico de autismo'); ax.grid(axis='x',visible=False); ax.legend(title='Idade',fontsize=7.5,title_fontsize=8,ncol=6,loc='upper left'); ax.set_ylim(0,bottom.max()*1.15)
ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v,p: fmt(v,0)))
save(fig,'fig10_composicao_etaria')
# 11 students
fig,ax=plt.subplots(figsize=(7.2,3.6))
for k,col in zip(['S1','S2','S3','S4'],[C['ink2'],C['c3'],C['ap'],C['br']]):
    ax.plot(years,R['proj_estudantes'][k],color=col,lw=2,label=k); ax.text(2040.3,R['proj_estudantes'][k][-1],fmt(R['proj_estudantes'][k][-1],0),fontsize=7.5,color=col,va='center')
ax.set_xlim(2022,2042); ax.set_xticks(range(2022,2041,2)); ax.set_ylabel('Estudantes (6–24 anos) com diagnóstico de autismo'); ax.legend(fontsize=8,loc='upper left'); ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v,p: fmt(v,0)))
save(fig,'fig11_estudantes')
print('ok')
