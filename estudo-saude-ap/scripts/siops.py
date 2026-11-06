import re,html,urllib.request,urllib.parse,csv,sys,time
OUT='/tmp/claude-0/-home-user-OBRAS-SAUDE/c712070a-2954-5409-93ab-21cafbd2988b/scratchpad/raw/siops/'
UFS={'12':'Acre','27':'Alagoas','16':'Amapá','13':'Amazonas','29':'Bahia','23':'Ceará','53':'Distrito Federal','32':'Espírito Santo','52':'Goiás','21':'Maranhão','51':'Mato Grosso','50':'Mato Grosso do Sul','31':'Minas Gerais','15':'Pará','25':'Paraíba','41':'Paraná','26':'Pernambuco','22':'Piauí','33':'Rio de Janeiro','24':'Rio Grande do Norte','43':'Rio Grande do Sul','11':'Rondônia','14':'Roraima','42':'Santa Catarina','35':'São Paulo','28':'Sergipe','17':'Tocantins'}
def fetch(uf,ano,per):
    body=urllib.parse.urlencode({'cmbAno':ano,'cmbUF':uf,'cmbPeriodo':per,'BtConsultar':'Consultar'}).encode()
    for a in range(3):
        try:
            s=urllib.request.urlopen(urllib.request.Request('http://siops.datasus.gov.br/consdetalhereenvio2uf.php',data=body),timeout=60).read().decode('latin1'); break
        except Exception as e:
            if a==2: raise
            time.sleep(2)
    txt=re.sub(r'<(script|style).*?</\1>','',s,flags=re.S); txt=re.sub(r'<!--.*?-->','',txt,flags=re.S); txt=re.sub(r'<[^>]+>','|',txt); txt=html.unescape(txt); txt=re.sub(r'[|\s]+',' ',txt)
    m=re.search(r'Ano-Base: (\d{4}) - (\d)º Bimestre',txt)
    if not m: return None
    d={'uf':UFS[uf],'cod_uf':uf,'ano':m.group(1),'bimestre':m.group(2)}
    dt=re.search(r'Versão do Cliente (\d\d/\d\d/\d{4})',txt); d['data_transmissao']=dt.group(1) if dt else ''
    for ind,val in re.findall(r'(\d\.\d) [^|]*? (?:R\$ )?([\d\.]+,\d+) ?%?',txt):
        d['ind_'+ind]=val.replace('.','').replace(',','.')
    return d
rows=[]
# AP serie anual 2015-2025 (6º bimestre = periodo 2)
for ano in range(2015,2026):
    d=fetch('16',str(ano),'2'); print(ano,d and d.get('ind_3.2'), d and d.get('ind_2.1'))
    if d: rows.append(d)
# AP 2026 parcial: try periods
for per in ['20','18','1','14','12']:
    d=fetch('16','2026',per)
    if d: print('2026',per,d.get('bimestre'),d.get('ind_3.2')); rows.append(d); break
# all UFs 2024 and 2025 annual
for ano in ['2024','2025']:
    for uf in UFS:
        if uf=='16': continue
        d=fetch(uf,ano,'2')
        if d: rows.append(d)
        else: print('no data',uf,ano)
keys=sorted({k for r in rows for k in r})
keys=['uf','cod_uf','ano','bimestre','data_transmissao']+[k for k in keys if k.startswith('ind_')]
with open(OUT+'siops_indicadores.csv','w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=keys,delimiter=';'); w.writeheader(); w.writerows(rows)
print('rows',len(rows))
