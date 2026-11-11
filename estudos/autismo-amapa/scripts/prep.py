import json, pandas as pd, numpy as np
def load(n): return pd.DataFrame(json.load(open(f'raw/{n}.json'))[1:])
def num(s): return pd.to_numeric(s.replace({'-':None,'..':None,'...':None,'X':None}), errors='coerce')

VAR={'93':'pop','13267':'tea','13408':'pct'}
def pop_table(names, lvl):
    df=pd.concat([load(n) for n in names])
    df['valor']=num(df['V']); df['var']=df['D2C'].map(VAR)
    out=df.pivot_table(index=['D1C','D1N','D4N','D5C','D5N'],columns='var',values='valor',aggfunc='first').reset_index()
    out.columns=['cod','nome','sexo','idade_cod','idade','pct','pop','tea']
    out['nivel']=lvl; out['idade_cod']=out['idade_cod'].astype(int)
    return out[['nivel','cod','nome','sexo','idade_cod','idade','pop','tea','pct']]
br=pop_table(['t10145_br'],'BR'); reg=pop_table(['t10145_reg'],'REG'); uf=pop_table(['t10145_uf'],'UF'); mun=pop_table(['t10145_mun_ap'],'MUN')
pd.concat([br,reg,uf,mun]).to_csv('data/pop_sexo_idade.csv',index=False)

# race
def race_table(names,lvl):
    df=pd.concat([load(n) for n in names]); df['valor']=num(df['V']); df['var']=df['D2C'].map(VAR)
    out=df.pivot_table(index=['D1C','D1N','D4N'],columns='var',values='valor',aggfunc='first').reset_index()
    out.columns=['cod','nome','raca','pct','pop','tea']; out['nivel']=lvl; return out
pd.concat([race_table(['t10147_br'],'BR'),race_table(['t10147_uf'],'UF'),race_table(['t10147_mun_ap'],'MUN')]).to_csv('data/raca.csv',index=False)

# students 6+
def stud_table(names,lvl):
    df=pd.concat([load(n) for n in names]); df['valor']=num(df['V'])
    vm={v:k for k,v in enumerate(sorted(df['D2N'].unique()))}
    df['var']=df['D2N'].map(lambda s: 'pct' if s.startswith('Percentual') else ('tea' if 'autismo' in s else 'est'))
    out=df.pivot_table(index=['D1C','D1N','D4N','D5N'],columns='var',values='valor',aggfunc='first').reset_index()
    out.columns=['cod','nome','sexo','idade','est','pct','tea']; out['nivel']=lvl; return out
pd.concat([stud_table(['t10148_br'],'BR'),stud_table(['t10148_uf'],'UF'),stud_table(['t10148_mun_ap'],'MUN')]).to_csv('data/estudantes.csv',index=False)

# schooling rate by sex/age (10150) and race/age (10151)
def rate_table(names,lvl,dim):
    df=pd.concat([load(n) for n in names]); df['valor']=num(df['V'])
    df['var']=df['D2N'].map(lambda s: 'tx_tea' if 'autismo' in s else 'tx_total')
    out=df.pivot_table(index=['D1C','D1N','D4N','D5N'],columns='var',values='valor',aggfunc='first').reset_index()
    out.columns=['cod','nome',dim[0],dim[1],'tx_tea','tx_total']; out['nivel']=lvl; return out
pd.concat([rate_table(['t10150_br'],'BR',('sexo','idade')),rate_table(['t10150_uf'],'UF',('sexo','idade'))]).to_csv('data/tx_escolarizacao_sexo.csv',index=False)
pd.concat([rate_table(['t10151_br'],'BR',('idade','raca')),rate_table(['t10151_uf'],'UF',('idade','raca'))]).to_csv('data/tx_escolarizacao_raca.csv',index=False)

# education level 25+
def edu_table(names,lvl):
    df=pd.concat([load(n) for n in names]); df['valor']=num(df['V'])
    df['var']=df['D2N'].map(lambda s: 'pct' if s.startswith('Percentual') else ('tea' if 'autismo' in s else 'pop25'))
    out=df.pivot_table(index=['D1C','D1N','D4N','D5N'],columns='var',values='valor',aggfunc='first').reset_index()
    out.columns=['cod','nome','sexo','instrucao','pct','pop25','tea']; out['nivel']=lvl; return out
pd.concat([edu_table(['t10153_br'],'BR'),edu_table(['t10153_uf'],'UF')]).to_csv('data/instrucao25.csv',index=False)

# projections
pr=pd.read_csv('raw/proj2024_ap_br.csv'); pr.to_csv('data/projecao2024_ap_br.csv',index=False)
print(uf[(uf.cod=='16')&(uf.sexo=='Total')][['idade','pop','tea','pct']].to_string())
print(mun[(mun.sexo=='Total')&(mun.idade=='Total')][['nome','pop','tea','pct']].sort_values('pop',ascending=False).to_string())
