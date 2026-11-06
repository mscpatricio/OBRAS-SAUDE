import sys, os, re
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'_common.py')).read())
for f in ['bench_cnes_leitos_uf_latest','bench_cnes_medicos_uf_latest']:
    p=os.path.join(OUT,f+'.csv')
    if os.path.exists(p) and os.path.getsize(p)==0: os.remove(p)
run('bench_cnes_leitos_uf_latest','cnes/cnv/leiintbr.def','Unidade_da_Federação','--Não-Ativa--',['Qtd_existente','Qtd_SUS'],lambda sel:['ltbr2512.dbf'])
run('bench_cnes_leitos_uf_set26','cnes/cnv/leiintbr.def','Região/Unidade_da_Federação','--Não-Ativa--',['Qtd_existente','Qtd_SUS'],lambda sel:[sel['Arquivos'][0][0]])
run('bench_cnes_medicos_uf_latest','cnes/cnv/prid02br.def','Médicos','Unidade_da_Federação',['Quantidade'],latest('pfbr'))
print('DONE4')
