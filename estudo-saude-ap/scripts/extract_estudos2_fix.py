import sys, os, re
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'_common.py')).read())
OUT='/tmp/claude-0/-home-user-OBRAS-SAUDE/c712070a-2954-5409-93ab-21cafbd2988b/scratchpad/raw/tab2'
log=open(os.path.join(OUT,'_log.txt'),'a')
def yy(a,b): return lambda sel:[v for v,t in sel['Arquivos'] if re.match(r'[a-z_]+(\d\d)\.dbf',v,re.I) and a<=2000+int(re.match(r'[a-z_]+(\d\d)\.dbf',v,re.I).group(1))<=b]
H='sinannet/cnv/hanswap.def'
run('e1_hans_mun_ano',H,'Município_de_residência','Ano_Diagnóstico',['Frequência'],yy(2019,2026))
run('e1_hans_classe_ano',H,'Classe_Operac._Diag.','Ano_Diagnóstico',['Frequência'],yy(2022,2026))
run('e1_hans_incap_ano',H,'Aval_Incap_Notif','Ano_Diagnóstico',['Frequência'],yy(2022,2026))
run('e1_hans_fx_ano',H,'Faixa_Etária_Hans','Ano_Diagnóstico',['Frequência'],yy(2022,2026))
run('e1_hans_deteccao_ano',H,'Modo_Detecção','Ano_Diagnóstico',['Frequência'],yy(2022,2026))
run('e1_hans_saida_ano',H,'Tipo_de_Saída','Ano_Diagnóstico',['Frequência'],yy(2022,2026))
run('e1_bench_hans_uf_ano','sinannet/cnv/hanswuf.def','UF_de_notificação','Ano_Diagnóstico',['Frequência'],yy(2022,2026))
for nm,d in (('chik','sinannet/cnv/chikunap.def'),('zika','sinannet/cnv/zikaap.def')):
    run(f'e1_{nm}_mun_ano',d,'Município_de_residência','Ano_1º_Sintoma(s)',['Todos_os_casos'],yy(2019,2026))
    run(f'e1_{nm}_ano',d,'Ano_1º_Sintoma(s)','--Não-Ativa--',['Todos_os_casos'],yy(2019,2026))
    run(f'e1_{nm}_class_ano',d,'Classificação','Ano_1º_Sintoma(s)',['Todos_os_casos'],yy(2019,2026))
AN='sinannet/cnv/animaisap.def'
for cand in ('Tipo_de_Acidente','Tipo_de_acidente','Tipo_Acidente'):
    run('e1_anim_tipo_ano',AN,cand,'Ano_acidente_',['Notificações'],yy(2019,2026))
print('DONE_FIX')
