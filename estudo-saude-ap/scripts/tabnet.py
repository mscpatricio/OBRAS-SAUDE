import re, sys, html, urllib.request, urllib.parse, json, time
BASE="http://tabnet.datasus.gov.br"
def getdef(defpath):
    url=f"{BASE}/cgi/deftohtm.exe?{defpath}"
    s=urllib.request.urlopen(url,timeout=90).read().decode('latin1')
    sel={}
    for m in re.finditer(r'<select([^>]*)>(.*?)</select>',s,re.S|re.I):
        name=re.search(r'name="?([^"\s>]+)',m.group(1),re.I)
        if not name: continue
        opts=[(v,html.unescape(t).strip()) for v,t in re.findall(r'<option[^>]*value="?([^"\s>]*)"?[^>]*>([^<]*)',m.group(2),re.I)]
        sel[name.group(1)]=opts
    return sel
def query(defpath, linha, coluna, incr, arquivos, filtros=None, formato='prn'):
    sel=getdef(defpath)
    data=[('Linha',linha),('Coluna',coluna)]
    for i in incr: data.append(('Incremento',i))
    for a in arquivos: data.append(('Arquivos',a))
    for k in sel:
        if k.startswith('S') and k not in ('S',):
            if k in ('SMunicípio',) or k.startswith('S'):
                pass
    filtros=filtros or {}
    for k,opts in sel.items():
        if k in ('Linha','Coluna','Incremento','Arquivos') or k.startswith('listahidden'): continue
        if k in filtros:
            for v in filtros[k]: data.append((k,v))
        else:
            data.append((k,'TODAS_AS_CATEGORIAS__'))
    for k in sel:
        pass
    data += [('formato',formato),('mostre','Mostra')]
    body=urllib.parse.urlencode(data,encoding='latin1').encode()
    url=f"{BASE}/cgi/tabcgi.exe?{defpath}"
    for attempt in range(4):
        try:
            r=urllib.request.urlopen(urllib.request.Request(url,data=body,headers={'Referer':f'{BASE}/cgi/deftohtm.exe?{defpath}','User-Agent':'Mozilla/5.0'}),timeout=300)
            s=r.read().decode('latin1'); break
        except Exception as e:
            if attempt==3: raise
            time.sleep(2**attempt)
    return s
def parse_prn(s):
    m=re.search(r'<pre>(.*?)</pre>',s,re.S|re.I)
    txt=html.unescape(m.group(1)) if m else s
    rows=[]
    for line in txt.splitlines():
        line=line.strip()
        if not line or not line.startswith('"'): continue
        rows.append([c.strip('"') for c in line.split(';')])
    return rows
def tocsv(rows,path):
    import csv
    with open(path,'w',newline='',encoding='utf-8') as f:
        csv.writer(f,delimiter=';').writerows(rows)
def files_between(sel, prefix, y0, y1):
    out=[]
    for v,t in sel['Arquivos']:
        m=re.match(rf'{prefix}(\d\d)(\d\d)\.dbf',v)
        if m and y0<=2000+int(m.group(1))<=y1: out.append(v)
    return out
if __name__=='__main__':
    d=getdef(sys.argv[1])
    for k,v in d.items(): print(k,len(v),v[:5])
