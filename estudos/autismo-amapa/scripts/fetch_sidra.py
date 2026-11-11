import json, time, urllib.request, sys, os
BASE="https://apisidra.ibge.gov.br/values"
def get(path, name):
    out=f"raw/{name}.json"
    if os.path.exists(out) and os.path.getsize(out)>100: print("cached",name); return
    for i in range(5):
        try:
            with urllib.request.urlopen(BASE+path+"?formato=json", timeout=120) as r:
                data=r.read()
            j=json.loads(data)
            open(out,"wb").write(data); print("ok",name,len(j)-1,"rows"); return
        except Exception as e:
            print("retry",name,i,e); time.sleep(2*(i+1))
    print("FAILED",name)
Q=[
 ("/t/10145/n1/all/v/all/p/last/c2/all/c58/all","t10145_br"),
 ("/t/10145/n2/all/v/all/p/last/c2/all/c58/all","t10145_reg"),
 ("/t/10145/n3/all/v/all/p/last/c2/all/c58/all","t10145_uf"),
 ("/t/10145/n6/in%20n3%2016/v/all/p/last/c2/all/c58/all","t10145_mun_ap"),
 ("/t/10147/n1/all/v/all/p/last/c86/all","t10147_br"),
 ("/t/10147/n3/all/v/all/p/last/c86/all","t10147_uf"),
 ("/t/10147/n6/in%20n3%2016/v/all/p/last/c86/all","t10147_mun_ap"),
 ("/t/10148/n1/all/v/all/p/last/c2/all/c58/all","t10148_br"),
 ("/t/10148/n3/all/v/all/p/last/c2/all/c58/all","t10148_uf"),
 ("/t/10148/n6/in%20n3%2016/v/all/p/last/c2/all/c58/all","t10148_mun_ap"),
 ("/t/10150/n1/all/v/all/p/last/c2/all/c58/all","t10150_br"),
 ("/t/10150/n3/all/v/all/p/last/c2/all/c58/all","t10150_uf"),
 ("/t/10151/n1/all/v/all/p/last/c58/all/c86/all","t10151_br"),
 ("/t/10151/n3/all/v/all/p/last/c58/all/c86/all","t10151_uf"),
 ("/t/10153/n1/all/v/all/p/last/c2/all/c1568/all","t10153_br"),
 ("/t/10153/n3/all/v/all/p/last/c2/all/c1568/all","t10153_uf"),
 ("/t/10146/n1/all/v/all/p/last/c58/all","t10146_br_nocourse"),
 ("/t/10146/n3/16/v/all/p/last/c58/all","t10146_ap_nocourse"),
]
for p,n in Q: get(p,n)
