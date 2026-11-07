import sys, os, re
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'_common.py')).read())
OUT='/tmp/claude-0/-home-user-OBRAS-SAUDE/c712070a-2954-5409-93ab-21cafbd2988b/scratchpad/raw/tab2'
log=open(os.path.join(OUT,'_log.txt'),'a')
def yy(a,b): return lambda sel:[v for v,t in sel['Arquivos'] if re.match(r'[a-z_]+(\d\d)\.dbf',v,re.I) and a<=2000+int(re.match(r'[a-z_]+(\d\d)\.dbf',v,re.I).group(1))<=b]
AN='sinannet/cnv/animaisap.def'
for f in ('e1_anim_tipo_ano','e1_anim_evol_ano'):
    p=os.path.join(OUT,f+'.csv')
    if os.path.exists(p) and os.path.getsize(p)==0: os.remove(p)
run('e1_anim_tipo_ano',AN,'Tipo_de_Acidente_','Ano_acidente_',['Notificações'],yy(2019,2026))
run('e1_anim_evol_ano',AN,'Evolução_caso','Ano_acidente_',['Notificações'],yy(2019,2026))
run('e1_anim_tipo_mun_2025',AN,'Município_de_residência','Tipo_de_Acidente_',['Notificações'],yy(2025,2025))
print('DONE_FIX2')
