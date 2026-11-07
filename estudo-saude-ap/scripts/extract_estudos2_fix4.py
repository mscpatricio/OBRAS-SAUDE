import sys, os, re
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'_common.py')).read())
import tabnet
OUT='/tmp/claude-0/-home-user-OBRAS-SAUDE/c712070a-2954-5409-93ab-21cafbd2988b/scratchpad/raw/tab2'
log=open(os.path.join(OUT,'_log.txt'),'a')
EQ='cnes/cnv/equipeap.def'; sel=tabnet.getdef(EQ)
idx={t.split(' ')[0]:v for v,t in sel['STipo_da_Equipe'] if t and t[0].isdigit()}
esf=[idx[k] for k in ('01','02','03','12','13','14','70') if k in idx]; eap=[idx[k] for k in ('76',) if k in idx]; esb=[idx[k] for k in ('71',) if k in idx]
print('idx',esf,eap,esb)
for f in ('e2_equipe_mun_ano_esf',):
    p=os.path.join(OUT,f+'.csv'); 
    if os.path.exists(p): os.remove(p)
run('e2_equipe_mun_ano_esf',EQ,'Município','Ano/mês_compet.',['Quantidade'],dec_files('epap',list(range(2019,2026)),['epap2609.dbf']),{'STipo_da_Equipe':esf})
run('e2_equipe_mun_ano_eap',EQ,'Município','Ano/mês_compet.',['Quantidade'],dec_files('epap',list(range(2019,2026)),['epap2609.dbf']),{'STipo_da_Equipe':eap})
run('e2_equipe_mun_ano_esb',EQ,'Município','Ano/mês_compet.',['Quantidade'],dec_files('epap',list(range(2019,2026)),['epap2609.dbf']),{'STipo_da_Equipe':esb})
EB='cnes/cnv/equipebr.def'; selb=tabnet.getdef(EB); idxb={t.split(' ')[0]:v for v,t in selb['STipo_da_Equipe'] if t and t[0].isdigit()}
p=os.path.join(OUT,'e2_bench_equipe_uf_latest.csv'); os.path.exists(p) and os.remove(p)
run('e2_bench_equipe_uf_latest',EB,'Unidade_da_Federação','--Não-Ativa--',['Quantidade'],latest('epbr'),{'STipo_da_Equipe':[idxb[k] for k in ('70',) if k in idxb]})
run('e2_bench_equipe_uf_eap_latest',EB,'Unidade_da_Federação','--Não-Ativa--',['Quantidade'],latest('epbr'),{'STipo_da_Equipe':[idxb[k] for k in ('76',) if k in idxb]})
print('DONE_FIX4')
