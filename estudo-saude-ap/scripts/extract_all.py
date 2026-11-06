import sys, os, re, json, traceback
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import tabnet
OUT='/tmp/claude-0/-home-user-OBRAS-SAUDE/c712070a-2954-5409-93ab-21cafbd2988b/scratchpad/raw/tab'
os.makedirs(OUT,exist_ok=True)
log=open(os.path.join(OUT,'_log.txt'),'a')
def run(name, d, linha, coluna, incr, arqsel, filtros=None):
    path=os.path.join(OUT,name+'.csv')
    if os.path.exists(path) and os.path.getsize(path)>0: return
    try:
        sel=tabnet.getdef(d)
        arq=arqsel(sel)
        s=tabnet.query(d,linha,coluna,incr,arq,filtros)
        rows=tabnet.parse_prn(s)
        if not rows:
            m=re.search(r'<pre>(.*?)</pre>',s,re.S|re.I)
            log.write(f'{name}: EMPTY {s[:300]!r}\n'); log.flush()
            open(os.path.join(OUT,name+'.err.html'),'w',encoding='latin1').write(s)
            return
        tabnet.tocsv(rows,path)
        log.write(f'{name}: {len(rows)} rows, {len(arq)} files\n'); log.flush()
        print(name,len(rows))
    except Exception as e:
        log.write(f'{name}: ERROR {e}\n{traceback.format_exc()}\n'); log.flush()
        print(name,'ERROR',e)
yrs=lambda p,a,b: (lambda sel: tabnet.files_between(sel,p,a,b))
def dec_files(p, years, extra=None):
    def f(sel):
        vals=[v for v,t in sel['Arquivos']]
        out=[]
        for y in years:
            cand=f'{p}{str(y)[2:]}12.dbf'
            if cand in vals: out.append(cand)
        if extra:
            for e in extra:
                if e in vals: out.append(e)
        return out
    return f
latest=lambda p:(lambda sel:[sel['Arquivos'][0][0]])
SIHM=['AIH_aprovadas','Valor_total','Dias_permanência','Média_permanência','Óbitos','Taxa_mortalidade']
Q='sih/cnv/qiap.def'
run('sih_ano',Q,'Ano_processamento','--Não-Ativa--',SIHM,yrs('qiap',2015,2026))
run('sih_anomes',Q,'Ano/mês_processamento','--Não-Ativa--',['AIH_aprovadas','Valor_total','Óbitos'],yrs('qiap',2022,2026))
run('sih_estab_ano_aih',Q,'Estabelecimento','Ano_processamento',['AIH_aprovadas'],yrs('qiap',2019,2026))
run('sih_estab_ano_valor',Q,'Estabelecimento','Ano_processamento',['Valor_total'],yrs('qiap',2019,2026))
run('sih_estab_2025',Q,'Estabelecimento','--Não-Ativa--',SIHM,yrs('qiap',2025,2025))
run('sih_estab_2026',Q,'Estabelecimento','--Não-Ativa--',SIHM,yrs('qiap',2026,2026))
run('sih_mun_ano_aih',Q,'Município','Ano_processamento',['AIH_aprovadas'],yrs('qiap',2019,2026))
run('sih_mun_ano_valor',Q,'Município','Ano_processamento',['Valor_total'],yrs('qiap',2019,2026))
run('sih_carater_ano',Q,'Caráter_atendimento','Ano_processamento',['AIH_aprovadas'],yrs('qiap',2019,2026))
run('sih_gestao_ano_aih',Q,'Gestão','Ano_processamento',['AIH_aprovadas'],yrs('qiap',2019,2026))
run('sih_gestao_ano_valor',Q,'Gestão','Ano_processamento',['Valor_total'],yrs('qiap',2019,2026))
run('sih_esfera_ano_aih',Q,'Esfera_jurídica','Ano_processamento',['AIH_aprovadas'],yrs('qiap',2019,2026))
run('sih_esfera_ano_valor',Q,'Esfera_jurídica','Ano_processamento',['Valor_total'],yrs('qiap',2019,2026))
run('sih_complex_ano_aih',Q,'Complexidade','Ano_processamento',['AIH_aprovadas'],yrs('qiap',2019,2026))
run('sih_complex_ano_valor',Q,'Complexidade','Ano_processamento',['Valor_total'],yrs('qiap',2019,2026))
run('sih_grupo_ano_aih',Q,'Grupo_procedimento','Ano_processamento',['AIH_aprovadas'],yrs('qiap',2019,2026))
run('sih_grupo_ano_valor',Q,'Grupo_procedimento','Ano_processamento',['Valor_total'],yrs('qiap',2019,2026))
run('sih_subgrupo_2025',Q,'Subgrupo_proced.','--Não-Ativa--',SIHM,yrs('qiap',2025,2025))
run('sih_financ_ano_valor',Q,'Financiamento','Ano_processamento',['Valor_total'],yrs('qiap',2019,2026))
run('sih_proc_2025',Q,'Procedimento','--Não-Ativa--',['AIH_aprovadas','Valor_total','Média_permanência','Óbitos'],yrs('qiap',2025,2025))
run('sih_estab_carater_2025',Q,'Estabelecimento','Caráter_atendimento',['AIH_aprovadas'],yrs('qiap',2025,2025))
run('sih_estab_complex_2025',Q,'Estabelecimento','Complexidade',['AIH_aprovadas'],yrs('qiap',2025,2025))
# residence
R='sih/cnv/qrap.def'
run('sihres_mun_ano_aih',R,'Município','Ano_processamento',['AIH_aprovadas'],yrs('qrap',2019,2026))
# morbidity
N='sih/cnv/niap.def'
NM=['Internações','Valor_total','Média_permanência','Óbitos','Taxa_mortalidade']
run('nih_cap_ano',N,'Capítulo_CID-10','Ano_processamento',['Internações'],yrs('niap',2019,2026))
run('nih_cap_2025',N,'Capítulo_CID-10','--Não-Ativa--',NM,yrs('niap',2025,2025))
run('nih_lista_2025',N,'Lista_Morb__CID-10','--Não-Ativa--',NM,yrs('niap',2025,2025))
run('nih_fxet_ano',N,'Faixa_Etária_1','Ano_processamento',['Internações'],yrs('niap',2019,2026))
run('nih_sexo_ano',N,'Sexo','Ano_processamento',['Internações'],yrs('niap',2019,2026))
run('nih_estab_cap_2025',N,'Estabelecimento','Capítulo_CID-10',['Internações'],yrs('niap',2025,2025))
run('nih_cap_fxet_2025',N,'Capítulo_CID-10','Faixa_Etária_1',['Internações'],yrs('niap',2025,2025))
# SIA
A='sia/cnv/qaap.def'
AM=['Qtd.aprovada','Valor_aprovado']
run('sia_ano',A,'Ano_processamento','--Não-Ativa--',AM+['Qtd.apresentada','Valor_apresentado'],yrs('qaap',2015,2026))
run('sia_anomes',A,'Ano/mês_processamento','--Não-Ativa--',AM,yrs('qaap',2022,2026))
run('sia_grupo_ano_qtd',A,'Grupo_procedimento','Ano_processamento',['Qtd.aprovada'],yrs('qaap',2019,2026))
run('sia_grupo_ano_valor',A,'Grupo_procedimento','Ano_processamento',['Valor_aprovado'],yrs('qaap',2019,2026))
run('sia_subgrupo_2025',A,'Subgrupo_proced.','--Não-Ativa--',AM,yrs('qaap',2025,2025))
run('sia_subgrupo_ano_valor',A,'Subgrupo_proced.','Ano_processamento',['Valor_aprovado'],yrs('qaap',2019,2026))
run('sia_complex_ano_qtd',A,'Complexidade','Ano_processamento',['Qtd.aprovada'],yrs('qaap',2019,2026))
run('sia_complex_ano_valor',A,'Complexidade','Ano_processamento',['Valor_aprovado'],yrs('qaap',2019,2026))
run('sia_gestao_ano_qtd',A,'Gestão','Ano_processamento',['Qtd.aprovada'],yrs('qaap',2019,2026))
run('sia_gestao_ano_valor',A,'Gestão','Ano_processamento',['Valor_aprovado'],yrs('qaap',2019,2026))
run('sia_esfadm_ano_qtd',A,'Esfera_administrat','Ano_processamento',['Qtd.aprovada'],yrs('qaap',2019,2026))
run('sia_esfadm_ano_valor',A,'Esfera_administrat','Ano_processamento',['Valor_aprovado'],yrs('qaap',2019,2026))
run('sia_prestador_ano_valor',A,'Tipo_de_prestador','Ano_processamento',['Valor_aprovado'],yrs('qaap',2019,2026))
run('sia_mun_ano_qtd',A,'Município','Ano_processamento',['Qtd.aprovada'],yrs('qaap',2019,2026))
run('sia_mun_ano_valor',A,'Município','Ano_processamento',['Valor_aprovado'],yrs('qaap',2019,2026))
run('sia_financ_ano_valor',A,'Financiamento','Ano_processamento',['Valor_aprovado'],yrs('qaap',2019,2026))
run('sia_forma_2025',A,'Forma_organização','--Não-Ativa--',AM,yrs('qaap',2025,2025))
run('sia_proc_2025',A,'Procedimento','--Não-Ativa--',AM,yrs('qaap',2025,2025))
run('sia_cbo_2025',A,'Profissional_-_CBO','--Não-Ativa--',AM,yrs('qaap',2025,2025))
run('sia_carater_ano_qtd',A,'Caráter_Atendiment','Ano_processamento',['Qtd.aprovada'],yrs('qaap',2019,2026))
run('sia_doc_ano_valor',A,'Documento_registro','Ano_processamento',['Valor_aprovado'],yrs('qaap',2019,2026))
# CNES
YEARS=list(range(2015,2026))
L='cnes/cnv/leiintap.def'
run('cnes_leitos_esp_ano',L,'Especialidade','Ano/mês_compet.',['Qtd_existente'],dec_files('ltap',YEARS,['ltap2609.dbf']))
run('cnes_leitos_esp_ano_sus',L,'Especialidade','Ano/mês_compet.',['Qtd_SUS'],dec_files('ltap',YEARS,['ltap2609.dbf']))
run('cnes_leitos_mun_latest',L,'Município','--Não-Ativa--',['Qtd_existente','Qtd_SUS','Quantidade_Não_SUS'],latest('ltap'))
run('cnes_leitos_esfera_latest',L,'Esfera_Administrativa','--Não-Ativa--',['Qtd_existente','Qtd_SUS','Quantidade_Não_SUS'],latest('ltap'))
run('cnes_leitos_tipoestab_latest',L,'Tipo_de_Estabelecimento','--Não-Ativa--',['Qtd_existente','Qtd_SUS'],latest('ltap'))
run('cnes_leitos_natureza_esp_latest',L,'Especialidade','Esfera_Administrativa',['Qtd_SUS'],latest('ltap'))
run('cnes_leitos_espdet_latest',L,'Especialidade_detalhada','--Não-Ativa--',['Qtd_existente','Qtd_SUS'],latest('ltap'))
run('cnes_leitos_gestao_latest',L,'Tipo_de_Gestão','--Não-Ativa--',['Qtd_existente','Qtd_SUS'],latest('ltap'))
U='cnes/cnv/leiutiap.def'
run('cnes_uti_tipo_ano',U,'Leitos_complementares','Ano/mês_compet.',['Quantidade_existente'],dec_files('luap',YEARS,['luap2609.dbf']))
run('cnes_uti_tipo_ano_sus',U,'Leitos_complementares','Ano/mês_compet.',['Quantidade_SUS'],dec_files('luap',YEARS,['luap2609.dbf']))
run('cnes_uti_mun_latest',U,'Município','Leitos_complementares',['Quantidade_SUS'],latest('luap'))
run('cnes_uti_esfera_latest',U,'Leitos_complementares','Esfera_Administrativa',['Quantidade_existente'],latest('luap'))
E='cnes/cnv/estabap.def'
run('cnes_estab_tipo_esfera_latest',E,'Tipo_de_Estabelecimento','Esfera_Administrativa',['Quantidade'],latest('stap'))
run('cnes_estab_mun_latest',E,'Município','Esfera_Administrativa',['Quantidade'],latest('stap'))
run('cnes_estab_tipo_ano',E,'Tipo_de_Estabelecimento','Ano/mês_compet.',['Quantidade'],dec_files('stap',YEARS,['stap2609.dbf']))
run('cnes_estab_gestao_latest',E,'Tipo_de_Estabelecimento','Tipo_de_Gestão',['Quantidade'],latest('stap'))
Qp='cnes/cnv/equipoap.def'
run('cnes_equip_sel_latest',Qp,'Equipamento_selecionado','--Não-Ativa--',['Equipamentos_Existentes','Equipamentos_em_Uso','Estab_c/_Equip_SUS'],latest('eqap'))
run('cnes_equip_sel_esfera_latest',Qp,'Equipamento_selecionado','Esfera_Administrativa',['Equipamentos_em_Uso'],latest('eqap'))
run('cnes_equip_sel_mun_latest',Qp,'Equipamento_selecionado','Município',['Equipamentos_em_Uso'],latest('eqap'))
run('cnes_equip_grupo_ano',Qp,'Grupo_de_Equipamentos','Ano/mês_compet.',['Equipamentos_em_Uso'],dec_files('eqap',YEARS,['eqap2609.dbf']))
P='cnes/cnv/prid02ap.def'
run('cnes_prof_sup_latest',P,'Ocupações_de_Nível_Superior','Atende_no_SUS',['Quantidade'],latest('pfap'))
run('cnes_prof_medicos_latest',P,'Médicos','Atende_no_SUS',['Quantidade'],latest('pfap'))
run('cnes_prof_medicos_mun_latest',P,'Município','Atende_no_SUS',['Quantidade'],latest('pfap'),{'SMédicos':[str(i) for i in range(1,200)]})
run('cnes_prof_geral_ano',P,'Ocupações_em_geral','Ano/mês_compet.',['Quantidade'],dec_files('pfap',YEARS,['pfap2609.dbf']))
run('cnes_prof_sup_esfera_latest',P,'Ocupações_de_Nível_Superior','Esfera_Administrativa',['Quantidade'],latest('pfap'))
run('cnes_prof_tec_latest',P,'Ocupações_de_Nível_Téc_Aux','Atende_no_SUS',['Quantidade'],latest('pfap'))
# SIM / SINASC / POP
S='sim/cnv/obt10ap.def'
allyears=lambda p,a,b:(lambda sel:[v for v,t in sel['Arquivos'] if re.match(rf'{p}(\d\d)\.dbf',v) and a<=2000+int(re.match(rf'{p}(\d\d)\.dbf',v).group(1))<=b])
run('sim_cap_ano',S,'Capítulo_CID-10','Ano_do_Óbito',['Óbitos_p/Residênc'],allyears('obtap',2015,2026))
run('sim_fxet_ano',S,'Faixa_Etária','Ano_do_Óbito',['Óbitos_p/Residênc'],allyears('obtap',2015,2026))
run('sim_mun_ano',S,'Município','Ano_do_Óbito',['Óbitos_p/Residênc'],allyears('obtap',2015,2026))
run('sim_causabr_2024',S,'Causa_-_CID-BR-10','--Não-Ativa--',['Óbitos_p/Residênc'],allyears('obtap',2024,2024))
run('sim_causabr_2023',S,'Causa_-_CID-BR-10','--Não-Ativa--',['Óbitos_p/Residênc'],allyears('obtap',2023,2023))
run('sim_local_ano',S,'Local_ocorrência','Ano_do_Óbito',['Óbitos_p/Residênc'],allyears('obtap',2015,2026))
run('sim_maldef_ano',S,'Causa_mal_definidas','Ano_do_Óbito',['Óbitos_p/Residênc'],allyears('obtap',2015,2026))
I='sim/cnv/inf10ap.def'
run('siminf_fxet_ano',I,'Faixa_etária_1','Ano_do_Óbito',['Óbitos_p/Residênc'],allyears('infap',2015,2026))
run('siminf_mun_ano',I,'Município','Ano_do_Óbito',['Óbitos_p/Residênc'],allyears('infap',2015,2026))
run('siminf_evit_ano',I,'Causas_evitáveis_-_0_a_4_anos','Ano_do_Óbito',['Óbitos_p/Residênc'],allyears('infap',2015,2026))
B='sinasc/cnv/nvap.def'
run('sinasc_ano',B,'Ano_do_nascimento','--Não-Ativa--',['Nascim_p/resid.mãe','Nascim_p/ocorrênc'],allyears('nvap',2015,2026))
run('sinasc_mun_ano',B,'Município','Ano_do_nascimento',['Nascim_p/resid.mãe'],allyears('nvap',2015,2026))
run('sinasc_parto_ano',B,'Tipo_de_parto','Ano_do_nascimento',['Nascim_p/resid.mãe'],allyears('nvap',2015,2026))
run('sinasc_prenatal_ano',B,'Consult_pré-natal','Ano_do_nascimento',['Nascim_p/resid.mãe'],allyears('nvap',2015,2026))
run('sinasc_peso_ano',B,'Peso_ao_nascer','Ano_do_nascimento',['Nascim_p/resid.mãe'],allyears('nvap',2015,2026))
run('sinasc_idademae_ano',B,'Idade_da_mãe','Ano_do_nascimento',['Nascim_p/resid.mãe'],allyears('nvap',2015,2026))
run('sinasc_gest_ano',B,'Duração_gestação','Ano_do_nascimento',['Nascim_p/resid.mãe'],allyears('nvap',2015,2026))
run('sinasc_local_ano',B,'Local_ocorrência','Ano_do_nascimento',['Nascim_p/ocorrênc'],allyears('nvap',2015,2026))
run('sinasc_robson_2024',B,'Grupos_de_Robson','Tipo_de_parto',['Nascim_p/resid.mãe'],allyears('nvap',2024,2024))
Pp='ibge/cnv/poptap.def'
run('pop_mun_ano',Pp,'Município','Ano',['População_estimada'],allyears('poptap',2015,2023))
print('DONE')
