const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage();
  await p.goto('file://' + __dirname + '/canto-de-ferro-01.html', { waitUntil: 'load' });
  await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(500);
  // ajuste automático: reduz levemente o conteúdo de quadros que transbordam
  await p.evaluate(() => {
    document.querySelectorAll('.panel').forEach(el => {
      let z = 1;
      while (el.scrollHeight > el.clientHeight + 1 && z > 0.78) {
        z -= 0.03;
        el.querySelectorAll(':scope > *:not(.pn):not(.note)').forEach(c => c.style.zoom = z);
      }
    });
  });
  const ov = await p.evaluate(() => {
    const r=[]; const pages=[...document.querySelectorAll('.page')];
    document.querySelectorAll('.panel').forEach(el=>{ if(el.scrollHeight>el.clientHeight+2){ r.push({page:pages.indexOf(el.closest('.page'))+1, panel:el.querySelector('.pn').textContent, over:el.scrollHeight-el.clientHeight}); } });
    document.querrySelectorAll && 0;
    document.querySelectorAll('.pad,.back,.sb').forEach(el=>{ if(el.scrollHeight>el.clientHeight+2){ r.push({page:pages.indexOf(el.closest('.page'))+1, block:el.className, over:el.scrollHeight-el.clientHeight}); } });
    return r;
  });
  console.log(JSON.stringify(ov));
  await p.pdf({ path: 'canto-de-ferro-01.pdf', printBackground: true, preferCSSPageSize: true });
  await b.close();
})();
