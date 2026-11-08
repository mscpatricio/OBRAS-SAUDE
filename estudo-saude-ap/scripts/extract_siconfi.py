# -*- coding: utf-8 -*-
"""Extrai do SICONFI (API Tesouro Transparente) RREO e DCA para o estudo de financiamento da saúde do Amapá.
Saída: raw/siconfi/json/*.json (brutos) e raw/siconfi/*.csv (tabelas)."""
import json, urllib.request, urllib.parse, csv, os, time, sys
RAW='/tmp/claude-0/-home-user-OBRAS-SAUDE/c712070a-2954-5409-93ab-21cafbd2988b/scratchpad/raw/siconfi/'
J=RAW+'json/'; os.makedirs(J,exist_ok=True)
API='https://apidatalake.tesouro.gov.br/ords/siconfi/tt/'
UFS={'12':'Acre','27':'Alagoas','16':'Amapá','13':'Amazonas','29':'Bahia','23':'Ceará','53':'Distrito Federal','32':'Espírito Santo','52':'Goiás','21':'Maranhão','51':'Mato Grosso','50':'Mato Grosso do Sul','31':'Minas Gerais','15':'Pará','25':'Paraíba','41':'Paraná','26':'Pernambuco','22':'Piauí','33':'Rio de Janeiro','24':'Rio Grande do Norte','43':'Rio Grande do Sul','11':'Rondônia','14':'Roraima','42':'Santa Catarina','35':'São Paulo','28':'Sergipe','17':'Tocantins'}
MUN={'1600055':'Serra do Navio','1600105':'Amapá','1600154':'Pedra Branca do Amapari','1600204':'Calçoene','1600212':'Cutias','1600238':'Ferreira Gomes','1600253':'Itaubal','1600279':'Laranjal do Jari','1600303':'Macapá','1600402':'Mazagão','1600501':'Oiapoque','1600535':'Porto Grande','1600550':'Pracuúba','1600600':'Santana','1600709':'Tartarugalzinho','1600808':'Vitória do Jari'}
def get(path,params,name):
    fn=J+name+'.json'
    if os.path.exists(fn):
        return json.load(open(fn))
    url=API+path+'?'+urllib.parse.urlencode(params)
    for a in range(4):
        try:
            d=json.load(urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=180)); break
        except Exception as e:
            print('retry',name,e,file=sys.stderr); time.sleep(3*(a+1))
            if a==3: return []
    it=d.get('items',[]); json.dump(it,open(fn,'w')); print(name,len(it),flush=True); return it
def rreo(ente,ano,per,name): return get('rreo',{'an_exercicio':ano,'nr_periodo':per,'co_tipo_demonstrativo':'RREO','id_ente':ente},name)
def dca(ente,ano,name,anexo=None):
    p={'an_exercicio':ano,'id_ente':ente}
    if anexo: p['no_anexo']=anexo
    return get('dca',p,name)
rows_02=[]; rows_01=[]; rows_14=[]; rows_03=[]; rows_06=[]
def harvest(items,ente_nome,ano,per):
    for r in items:
        an=r['anexo']; c=r['conta']; cc=r['cod_conta']
        base=dict(ente=ente_nome,cod_ibge=r['cod_ibge'],populacao=r.get('populacao'),exercicio=ano,periodo=per,cod_conta=cc,conta=c,coluna=r['coluna'],valor=r['valor'])
        if an=='RREO-Anexo 02' and cc in ('RREO2TotalDespesas','RREO2TotalDespesasIntra','RREO2TotalDespesasExcetoIntra') :
            rows_02.append(base)
        elif an=='RREO-Anexo 01': rows_01.append(base)
        elif an=='RREO-Anexo 14': rows_14.append(base)
        elif an=='RREO-Anexo 03': rows_03.append(base)
        elif an=='RREO-Anexo 06': rows_06.append(base)
# 1) Amapá estado: 2022-2025 (6º bim) e 2026 (último bimestre disponível)
for ano in range(2022,2026):
    harvest(rreo('16',ano,6,f'rreo_16_{ano}_6'),'Amapá',ano,6)
per26=None
for per in (6,5,4,3):
    it=rreo('16',2026,per,f'rreo_16_2026_{per}')
    if it: per26=per; harvest(it,'Amapá',2026,per); break
print('2026 periodo',per26)
# 2) benchmark UFs 2024 e 2025 (6º bim)
for ano in (2024,2025):
    for uf,nome in UFS.items():
        if uf=='16': continue
        harvest(rreo(uf,ano,6,f'rreo_{uf}_{ano}_6'),nome,ano,6)
def wcsv(name,rows):
    if not rows: return
    with open(RAW+name,'w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0].keys()),delimiter=';'); w.writeheader(); w.writerows(rows)
wcsv('rreo02_funcoes.csv',rows_02); wcsv('rreo01_receitas.csv',rows_01); wcsv('rreo14_simplificado.csv',rows_14); wcsv('rreo03_rcl.csv',rows_03); wcsv('rreo06_primario.csv',rows_06)
# 3) DCA Amapá 2022-2025 (todos os anexos) e municípios (Anexo I-E)
rows_dca=[]
for ano in range(2022,2026):
    for r in dca('16',ano,f'dca_16_{ano}'):
        rows_dca.append(dict(ente='Amapá',cod_ibge=r['cod_ibge'],populacao=r.get('populacao'),exercicio=ano,anexo=r['anexo'],cod_conta=r['cod_conta'],conta=r['conta'],coluna=r['coluna'],valor=r['valor']))
    for cod,nome in MUN.items():
        for r in dca(cod,ano,f'dca_{cod}_{ano}_IE','DCA-Anexo I-E'):
            rows_dca.append(dict(ente=nome,cod_ibge=r['cod_ibge'],populacao=r.get('populacao'),exercicio=ano,anexo=r['anexo'],cod_conta=r['cod_conta'],conta=r['conta'],coluna=r['coluna'],valor=r['valor']))
wcsv('dca.csv',rows_dca)
print('DONE')
