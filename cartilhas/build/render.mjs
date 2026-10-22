// Renderiza as cartilhas (HTML) em PDF e PNG de pré-visualização com o Chromium.
// Uso: node cartilhas/build/render.mjs [nome-da-cartilha ...]
import { createRequire } from 'node:module';
import { fileURLToPath, pathToFileURL } from 'node:url';
import path from 'node:path';
import fs from 'node:fs';

// playwright: do projeto, ou da instalação global (ex.: /opt/node-tools)
const require = createRequire(import.meta.url);
function loadPlaywright() {
  const candidates = ['playwright', process.env.PLAYWRIGHT_MODULE, '/opt/node-tools/node_modules/playwright', '/usr/lib/node_modules/playwright'].filter(Boolean);
  for (const c of candidates) { try { return require(c); } catch (e) { /* tenta o próximo */ } }
  throw new Error('playwright não encontrado: rode `npm i -D playwright` ou defina PLAYWRIGHT_MODULE');
}
const { chromium } = loadPlaywright();

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const dist = path.join(root, 'dist');
fs.mkdirSync(dist, { recursive: true });

const DOCS = {
  'cartilha-dentista': { file: 'cartilha-dentista/index.html', out: 'Cartilha-Cirurgiao-Dentista-TEA.pdf', format: 'A4' },
  'card-paciente': { file: 'card-paciente/index.html', out: 'Card-Minha-Visita-ao-Dentista.pdf', format: 'A4' },
  'cartilha-paciente': { file: 'cartilha-paciente/index.html', out: 'Cartilha-Minha-Visita-ao-Dentista.pdf', format: 'A4' },
  'preview-cenas': { file: 'build/preview-cenas.html', out: 'preview-cenas.pdf', format: 'A4', pngOnly: true },
};

const wanted = process.argv.slice(2);
const names = wanted.length ? wanted : Object.keys(DOCS).filter(n => !DOCS[n].pngOnly);

const browser = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH || undefined });
for (const name of names) {
  const doc = DOCS[name];
  if (!doc) { console.error(`documento desconhecido: ${name}`); continue; }
  const page = await browser.newPage({ viewport: { width: 1000, height: 1400 }, deviceScaleFactor: 2 });
  const errors = [];
  page.on('pageerror', e => errors.push(String(e)));
  page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
  await page.goto(pathToFileURL(path.join(root, doc.file)).href, { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(300);
  if (errors.length) console.warn(`[${name}] erros no navegador:\n  ` + errors.join('\n  '));

  // PNG de cada página (pré-visualização)
  const pages = await page.$$('.page');
  for (let i = 0; i < pages.length; i++) {
    await pages[i].screenshot({ path: path.join(dist, `${name}-p${String(i + 1).padStart(2, '0')}.png`) });
  }
  if (!doc.pngOnly) {
    await page.emulateMedia({ media: 'print' });
    await page.pdf({ path: path.join(dist, doc.out), format: doc.format, printBackground: true, preferCSSPageSize: true, margin: { top: 0, right: 0, bottom: 0, left: 0 } });
    console.log(`[${name}] ${pages.length} páginas → dist/${doc.out}`);
  } else {
    console.log(`[${name}] ${pages.length} páginas → PNGs em dist/`);
  }
  await page.close();
}
await browser.close();
