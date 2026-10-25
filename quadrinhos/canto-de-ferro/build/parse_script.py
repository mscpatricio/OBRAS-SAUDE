import re
FORJADOS_GUARDA={"VIGÍLIA","MARÉ","FUSO","CERRADO","CÁLAMO"}
FORJADOS_CADINHO={"DOBRE","LASTRO","ESTILHAÇO","GRIMPA"}

def parse(md):
    """Retorna lista de páginas: dict(num, title, panels=[dict(num,note,items=[...])])"""
    sections=re.split(r'\n## ', "\n"+md)
    pages=[]
    for sec in sections:
        m=re.match(r'PÁGINA (\d+)\s*\n', sec)
        if not m: continue
        num=int(m.group(1)); body=sec[m.end():]
        body=body.split('\n---')[0]
        parts=re.split(r'\*\*Quadro (\d+)\*\*\s*(?:\*\(([^)]*)\)\*)?\s*\n', body)
        panels=[]
        for i in range(1,len(parts),3):
            pn=int(parts[i]); note=(parts[i+1] or "").strip(); content=parts[i+2]
            panels.append(dict(num=pn, note=note, items=parse_items(content)))
        pages.append(dict(num=num, panels=panels))
    return pages

SPK=re.compile(r'^([A-ZÁÉÍÓÚÂÊÔÃÕÇÜ0-9][A-ZÁÉÍÓÚÂÊÔÃÕÇÜ0-9 .\-\']*?)\s*(?:\(([^)]*)\))?\s*:\s*(.*)$', re.S)

def parse_items(content):
    items=[]
    paras=[p.strip() for p in re.split(r'\n\s*\n', content) if p.strip()]
    for p in paras:
        if p.startswith('*') and p.endswith('*') and not p.startswith('**'):
            items.append(dict(kind='desc', text=clean(p.strip('*')))); continue
        if p.startswith('>'):
            items.append(dict(kind='note', text="\n".join(l.lstrip('> ').rstrip() for l in p.splitlines()))); continue
        m=SPK.match(p)
        if m:
            spk,q,txt=m.group(1).strip(),(m.group(2) or "").strip(),clean(m.group(3))
            if spk.startswith('LEGENDA'): items.append(dict(kind='cap', who=q, text=txt))
            elif spk.startswith('SFX'): items.append(dict(kind='sfx', q=q, text=txt))
            elif spk.startswith('TEXTO FINAL'): items.append(dict(kind='final', text=txt))
            elif spk.startswith('RÁDIO'): items.append(dict(kind='say', who='RÁDIO', q=q, text=txt, side='radio'))
            else:
                side='guarda' if spk in FORJADOS_GUARDA else 'cadinho' if spk in FORJADOS_CADINHO else 'human'
                wavy='ondulado' in q
                thought='pensamento' in q
                items.append(dict(kind='say', who=spk, q=q, text=txt, side=side, wavy=wavy, thought=thought))
        else:
            items.append(dict(kind='desc', text=clean(p)))
    return items

def clean(t):
    t=re.sub(r'\s*\n\s*',' ',t.strip())
    t=re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', t)
    t=re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<i>\1</i>', t)
    return t

if __name__=="__main__":
    import sys,json
    pages=parse(open(sys.argv[1]).read())
    for p in pages:
        print(p['num'], [(q['num'],q['note'],len(q['items'])) for q in p['panels']])
