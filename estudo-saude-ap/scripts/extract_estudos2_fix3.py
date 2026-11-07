import sys, os, re
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'_common.py')).read())
OUT='/tmp/claude-0/-home-user-OBRAS-SAUDE/c712070a-2954-5409-93ab-21cafbd2988b/scratchpad/raw/tab2'
log=open(os.path.join(OUT,'_log.txt'),'a')
def yy(a,b): return lambda sel:[v for v,t in sel['Arquivos'] if re.match(r'[a-z_]+(\d\d)\.dbf',v,re.I) and a<=2000+int(re.match(r'[a-z_]+(\d\d)\.dbf',v,re.I).group(1))<=b]
for f in ['e1_bench_deng_uf_ano']:
    p=os.path.join(OUT,f+'.csv')
    if os.path.exists(p) and os.path.getsize(p)==0: os.remove(p)
run('e1_bench_deng_uf_2024','sinannet/cnv/denguebr.def','UF_de_notificação','--Não-Ativa--',['Casos_Prováveis'],yy(2024,2024))
run('e1_bench_deng_uf_2025','sinannet/cnv/denguebr.def','UF_de_notificação','--Não-Ativa--',['Casos_Prováveis'],yy(2025,2025))
print('DONE_FIX3')
