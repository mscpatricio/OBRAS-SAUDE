import subprocess, time, sys, os, uno
from com.sun.star.beans import PropertyValue
src=os.path.abspath(sys.argv[1]); dst=os.path.abspath(sys.argv[2])
prof='file:///tmp/lo_prof_uno'
p=subprocess.Popen(['soffice','--headless','--invisible','--norestore',f'-env:UserInstallation={prof}','--accept=socket,host=127.0.0.1,port=2002;urp;'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
ctx=None
for i in range(60):
    try:
        local=uno.getComponentContext(); resolver=local.ServiceManager.createInstanceWithContext('com.sun.star.bridge.UnoUrlResolver',local)
        ctx=resolver.resolve('uno:socket,host=127.0.0.1,port=2002;urp;StarOffice.ComponentContext'); break
    except Exception: time.sleep(1)
if ctx is None: print('no connection'); p.kill(); sys.exit(1)
smgr=ctx.ServiceManager; desktop=smgr.createInstanceWithContext('com.sun.star.frame.Desktop',ctx)
def pv(n,v): x=PropertyValue(); x.Name=n; x.Value=v; return x
doc=desktop.loadComponentFromURL(uno.systemPathToFileUrl(src),'_blank',0,(pv('Hidden',True),))
# update indexes twice (page numbers shift after TOC fills)
for _ in range(2):
    idx=doc.getDocumentIndexes()
    for i in range(idx.getCount()): idx.getByIndex(i).update()
    doc.getTextFields().refresh()
doc.storeToURL(uno.systemPathToFileUrl(dst),(pv('FilterName','writer_pdf_Export'),))
doc.close(True)
try: desktop.terminate()
except Exception: pass
p.wait(timeout=30); print('pdf ok')
