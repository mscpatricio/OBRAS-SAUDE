// Gera os ícones do app (PNG) a partir da ilustração vetorial do dentinho.
import { createRequire } from 'node:module';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const require = createRequire(import.meta.url);
const pw = ['playwright', '/opt/node-tools/node_modules/playwright'].reduce((m, c) => m || (() => { try { return require(c); } catch (e) { return null; } })(), null);
if (!pw) throw new Error('playwright não encontrado');
const dir = path.join(path.dirname(fileURLToPath(import.meta.url)), 'www', 'icons');

const svg = (pad) => `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120">
  <rect width="120" height="120" rx="${pad ? 0 : 26}" fill="#5DADE2"/>
  <g transform="translate(60 ${pad ? 62 : 60}) scale(${pad ? 0.72 : 0.95})">
    <path d="M-40 -40 C-40 -70 40 -70 40 -40 C44 -10 36 20 28 44 C22 58 10 58 6 42 L0 20 L-6 42 C-10 58 -22 58 -28 44 C-36 20 -44 -10 -40 -40 Z" fill="#FFFFFF" stroke="#2B2B2B" stroke-width="4" stroke-linejoin="round"/>
    <circle cx="-14" cy="-28" r="4.5" fill="#2B2B2B"/><circle cx="14" cy="-28" r="4.5" fill="#2B2B2B"/>
    <path d="M-14 -12 Q0 4 14 -12" fill="none" stroke="#2B2B2B" stroke-width="4" stroke-linecap="round"/>
    <circle cx="-25" cy="-14" r="5" fill="#F5A3A3" opacity=".9"/><circle cx="25" cy="-14" r="5" fill="#F5A3A3" opacity=".9"/>
  </g></svg>`;

const browser = await pw.chromium.launch();
const page = await browser.newPage();
for (const [name, size, pad] of [['icon-192.png', 192, false], ['icon-512.png', 512, false], ['apple-touch-icon.png', 180, true], ['icon-maskable-512.png', 512, true]]) {
  await page.setViewportSize({ width: size, height: size });
  await page.setContent(`<html><body style="margin:0;background:transparent">${svg(pad).replace('<svg ', `<svg width="${size}" height="${size}" `)}</body></html>`);
  await page.screenshot({ path: path.join(dir, name), omitBackground: !pad });
  console.log('icone', name);
}
await browser.close();
