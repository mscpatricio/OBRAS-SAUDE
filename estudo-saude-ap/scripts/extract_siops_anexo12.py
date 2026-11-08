# -*- coding: utf-8 -*-
"""Extrai do SIOPS o Demonstrativo da Lei de Responsabilidade Fiscal (RREO Anexo 12) de estados e municípios.
Estado: rel_LRFUF.php (cmbAno, cmbUF, cmbPeriodo); município: rel_LRF.php (+ cmbMunicipio[] com 6 dígitos).
cmbPeriodo: '2' = exercício encerrado (6º bimestre); 12,14,1,18,20 = 1º a 5º bimestres.
Saída: raw/siops2/html/*.html (bruto) e raw/siops2/siops_anexo12.csv (formato longo)."""
import re, html, urllib.request, urllib.parse, csv, os, sys, time
RAW='/tmp/claude-0/-home-user-OBRAS-SAUDE/c712070a-2954-5409-93ab-21cafbd2988b/scratchpad/raw/siops2/'
H=RAW+'html/'; os.makedirs(H,exist_ok=True)
UFS={'12':'Acre','27':'Alagoas','16':'Amapá','13':'Amazonas','29':'Bahia','23':'Ceará','53':'Distrito Federal','32':'Espírito Santo','52':'Goiás','21':'Maranhão','51':'Mato Grosso','50':'Mato Grosso do Sul','31':'Minas Gerais','15':'Pará','25':'Paraíba','41':'Paraná','26':'Pernambuco','22':'Piauí','33':'Rio de Janeiro','24':'Rio Grande do Norte','43':'Rio Grande do Sul','11':'Rondônia','14':'Roraima','42':'Santa Catarina','35':'São Paulo','28':'Sergipe','17':'Tocantins'}
MUN={'160005':'Serra do Navio','160010':'Amapá','160015':'Pedra Branca do Amapari','160020':'Calçoene','160021':'Cutias','160023':'Ferreira Gomes','160025':'Itaubal','160027':'Laranjal do Jari','160030':'Macapá','160040':'Mazagão','160050':'Oiapoque','160053':'Porto Grande','160055':'Pracuúba','160060':'Santana','160070':'Tartarugalzinho','160080':'Vitória do Jari'}
PER_NOME={'2':'6','12':'1','14':'2','1':'3','18':'4','20':'5'}
NUM=re.compile(r'^-?(\d{1,3}(\.\d{3})*|\d+),\d{2}$')
def fetch(esfera,ano,uf,per,mun=None):
    key=f'{esfera}_{uf}_{mun or ""}_{ano}_{per}'; fn=H+key+'.html'
    if os.path.exists(fn): return open(fn,encoding='latin1').read()
    data={'cmbAno':ano,'cmbUF':uf,'cmbPeriodo':per,'BtConsultar':'Consultar'}
    url='http://siops.datasus.gov.br/rel_LRFUF.php'
    if mun: data['cmbMunicipio[]']=mun; url='http://siops.datasus.gov.br/rel_LRF.php'
    body=urllib.parse.urlencode(data,doseq=True).encode()
    for a in range(4):
        try:
            s=urllib.request.urlopen(urllib.request.Request(url,data=body),timeout=120).read().decode('latin1'); break
        except Exception as e:
            print('retry',key,e,file=sys.stderr); time.sleep(3*(a+1)); s=''
    open(fn,'w',encoding='latin1').write(s); return s
def tokens(s):
    txt=re.sub(r'<(script|style).*?</\1>','',s,flags=re.S); txt=re.sub(r'<[^>]+>','|',txt); txt=html.unescape(txt); txt=re.sub(r'\s+',' ',txt); txt=re.sub(r'(\|\s*)+','|',txt)
    return [t.strip() for t in txt.split('|') if t.strip()]
SECOES=['RECEITAS RESULTANTES DE IMPOSTOS','DESPESAS COM AÇÕES E SERVIÇOS PÚBLICOS DE SAÚDE (ASPS)','APURAÇÃO DO CUMPRIMENTO DO LIMITE','CONTROLE DO VALOR REFERENTE AO PERCENTUAL','EXERCÍCIO DO EMPENHO','CONTROLE DE RESTOS A PAGAR CANCELADOS','RECEITAS ADICIONAIS PARA O FINANCIAMENTO','DESPESAS COM SAUDE POR SUBFUNÇÕES E CATEGORIA ECONÔMICA NÃO COMPUTADAS','DESPESAS TOTAIS COM SAÚDE EXECUTADAS']
def parse(s,meta):
    tk=tokens(s)
    if not any('RECEITA DE IMPOSTOS' in t for t in tk): return []
    hom=next((t for t in tk if t.startswith('Dados Homologados') or t.startswith('Dados Transmitidos') or 'Homologados' in t),'')
    rows=[]; secao=''; grupo=''; i=0
    while i<len(tk):
        t=tk[i]
        for sname in SECOES:
            if t.startswith(sname): secao=sname; grupo=''
        vals=[]; j=i+1
        while j<len(tk) and (NUM.match(tk[j]) or tk[j] in ('N/A','-')): vals.append(tk[j]); j+=1
        if vals and not NUM.match(t):
            if t.upper()==t and not t.startswith('Despesas'): grupo=t
            rows.append(dict(meta,homologacao=hom,secao=secao,grupo=grupo if t!=grupo else '',linha=t,**{f'v{k+1}':(v.replace('.','').replace(',','.') if NUM.match(v) else '') for k,v in enumerate(vals[:12])}))
            i=j
        else: i+=1
    return rows
out=[]
def run(esfera,uf,ano,pers,mun=None):
    for per in pers:
        s=fetch(esfera,ano,uf,per,mun)
        meta=dict(esfera=esfera,uf=UFS[uf],cod_uf=uf,municipio=MUN.get(mun,'') if mun else '',cod_mun=mun or '',ano=ano,bimestre=PER_NOME[per])
        r=parse(s,meta)
        if r: out.extend(r); print(esfera,uf,mun or '',ano,per,len(r),flush=True); return True
    print('SEM DADOS',esfera,uf,mun or '',ano,flush=True); return False
# Estado do Amapá 2022-2025 encerrados e 2026 parcial
for ano in range(2022,2026): run('E','16',str(ano),['2'])
run('E','16','2026',['20','18','1','14','12'])
# Demais UFs 2024 e 2025
for ano in ('2024','2025'):
    for uf in UFS:
        if uf!='16': run('E',uf,ano,['2'])
# Municípios do Amapá 2022-2025 e 2026 parcial
for mun in MUN:
    for ano in range(2022,2026): run('M','16',str(ano),['2'],mun)
    run('M','16','2026',['20','18','1','14','12'],mun)
keys=['esfera','uf','cod_uf','municipio','cod_mun','ano','bimestre','homologacao','secao','grupo','linha']+[f'v{k}' for k in range(1,13)]
with open(RAW+'siops_anexo12.csv','w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=keys,delimiter=';',extrasaction='ignore'); w.writeheader(); w.writerows(out)
print('DONE',len(out))
