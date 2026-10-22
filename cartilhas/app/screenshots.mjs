// Captura telas do app em viewport de celular (para revisão / loja).
import { createRequire } from 'node:module';
import path from 'node:path';
import fs from 'node:fs';
import { fileURLToPath, pathToFileURL } from 'node:url';
const require = createRequire(import.meta.url);
const pw = ['playwright', '/opt/node-tools/node_modules/playwright'].reduce((m, c) => m || (() => { try { return require(c); } catch (e) { return null; } })(), null);
const root = path.dirname(fileURLToPath(import.meta.url));
const out = path.join(root, 'screenshots'); fs.mkdirSync(out, { recursive: true });
const routes = process.argv.slice(2).length ? process.argv.slice(2) : ['#/', '#/crianca', '#/crianca/historia/13', '#/crianca/sinais', '#/crianca/pessoas', '#/crianca/sala', '#/crianca/consegui', '#/dentista', '#/dentista/lista/durante', '#/dentista/consulta', '#/dentista/pacientes', '#/dentista/paciente/novo', '#/dentista/info'];
const browser = await pw.chromium.launch();
const ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true });
const page = await ctx.newPage();
const errors = [];
page.on('pageerror', (e) => errors.push(String(e)));
page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()); });
await page.goto(pathToFileURL(path.join(root, 'www', 'index.html')).href);
await page.evaluate(() => document.fonts.ready);
for (const r of routes) {
  await page.evaluate((h) => { location.hash = h; }, r);
  await page.waitForTimeout(250);
  const name = r.replace(/[#/]+/g, '_').replace(/^_|_$/g, '') || 'home';
  await page.screenshot({ path: path.join(out, `${name}.png`), fullPage: true });
  console.log('tela', r, '→', `${name}.png`);
}
if (errors.length) { console.error('ERROS:\n' + errors.join('\n')); process.exitCode = 1; }
await browser.close();
