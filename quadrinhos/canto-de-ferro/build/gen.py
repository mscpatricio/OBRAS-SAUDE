# -*- coding: utf-8 -*-
import math, html, sys
from svgs import *
from parse_script import parse

ROOT="/home/user/OBRAS-SAUDE/quadrinhos/canto-de-ferro"
import os
def A(name):
    return f"art_real/{name}" if os.path.exists(f"art_real/{name}") else f"art/{name}"
AUTHOR="Patrício Almeida"
script_md=open(f"{ROOT}/03-edicao-01-roteiro.md").read()
PAGES=parse(script_md)

CSS=r"""
@page { size: 170mm 260mm; margin: 0; }
*{box-sizing:border-box}
html,body{margin:0;padding:0;background:#fff}
body{font-family:'Inter',sans-serif;color:#1b1b1f;-webkit-print-color-adjust:exact;print-color-adjust:exact}
.page{width:170mm;height:260mm;position:relative;overflow:hidden;page-break-after:always;background:#fff}
.page.dark{background:#141518;color:#f1ebdd}
.pad{padding:16mm 14mm 14mm 14mm;height:100%;position:relative}
.bebas{font-family:'Bebas Neue',sans-serif;font-weight:400}
.osw{font-family:'Oswald',sans-serif}
.bar{font-family:'Barlow Condensed',sans-serif}
.rust{color:#c8501e}.bronze{color:#c9a24a}.bone{color:#f1ebdd}.red{color:#b8261f}
.kicker{font-family:'Oswald';text-transform:uppercase;letter-spacing:.22em;font-size:8pt;color:#c8501e;font-weight:600}
h1.sec{font-family:'Bebas Neue';font-size:54pt;line-height:.92;margin:2mm 0 6mm;letter-spacing:.01em}
h2{font-family:'Bebas Neue';font-size:22pt;line-height:1;margin:7mm 0 2mm;color:#141518;letter-spacing:.02em}
h3{font-family:'Oswald';font-size:10.5pt;text-transform:uppercase;letter-spacing:.08em;margin:5mm 0 1.5mm;color:#c8501e}
p{font-size:9.2pt;line-height:1.5;margin:0 0 2.6mm}
.lead{font-size:11pt;line-height:1.45;font-family:'Barlow Condensed';font-weight:400;color:#333}
.cols2{columns:2;column-gap:7mm}
.rule{height:2px;background:#c8501e;width:22mm;margin:3mm 0 5mm}
.quote{font-family:'Barlow Condensed';font-size:14pt;line-height:1.25;color:#141518;border-left:3px solid #c8501e;padding-left:5mm;margin:5mm 0}
.quote small{display:block;font-family:'Oswald';font-size:8pt;letter-spacing:.15em;text-transform:uppercase;color:#c8501e;margin-top:2mm}
.folio{position:absolute;bottom:7mm;left:14mm;right:14mm;display:flex;justify-content:space-between;font-family:'Oswald';font-size:7pt;letter-spacing:.2em;text-transform:uppercase;color:#888}
.page.dark .folio{color:#8a8578}
.rivets{position:absolute;top:0;left:0;right:0;height:4mm;background:repeating-linear-gradient(90deg,#141518 0 6mm,#c8501e 6mm 7mm)}
table.glos{width:100%;border-collapse:collapse;font-size:8.4pt}
table.glos td{padding:2mm 2.5mm;border-bottom:1px solid #e3ded2;vertical-align:top;line-height:1.35}
table.glos td:first-child{font-family:'Oswald';font-weight:600;text-transform:uppercase;letter-spacing:.04em;width:34mm;color:#141518;font-size:7.8pt}
/* capa */
.cover img.bg{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:center top}
.cover .shade{position:absolute;left:0;right:0;bottom:0;height:40mm;background:linear-gradient(180deg,rgba(0,0,0,0) 0%,rgba(10,6,4,.85) 100%)}
.cover .shadetop{position:absolute;left:0;right:0;top:0;height:48mm;background:linear-gradient(180deg,rgba(10,6,4,.55) 0%,rgba(0,0,0,0) 100%)}
.cover .logo{position:absolute;top:14mm;left:0;right:0;text-align:center}
.cover .logo .t{font-family:'Bebas Neue';font-size:72pt;line-height:.9;color:#f1ebdd;letter-spacing:.02em;text-shadow:3px 0 0 #c8501e,-3px 0 0 #7a2a10,0 6px 18px rgba(0,0,0,.6)}
.cover .logo .s{font-family:'Oswald';font-size:9pt;letter-spacing:.35em;text-transform:uppercase;color:#f1ebdd;opacity:.9;margin-top:1mm}
.cover .num{position:absolute;top:12mm;left:9mm;background:#f1ebdd;color:#141518;font-family:'Bebas Neue';font-size:16pt;padding:1.5mm 3mm;line-height:1;transform:rotate(-4deg)}
.cover .num small{display:block;font-family:'Oswald';font-size:6pt;letter-spacing:.2em}
.cover .tag{position:absolute;bottom:14mm;left:12mm;right:12mm;color:#f1ebdd;font-family:'Barlow Condensed';font-weight:600;font-size:17pt;line-height:1.1;text-transform:uppercase;letter-spacing:.02em;text-shadow:0 2px 8px rgba(0,0,0,.8)}
.cover .tag b{color:#ffd9a0}
.cover .pub{position:absolute;bottom:7mm;left:12mm;font-family:'Oswald';font-size:6.5pt;letter-spacing:.25em;color:#f1ebdd;opacity:.75;text-transform:uppercase}
/* frontispício */
.credits{display:grid;grid-template-columns:1fr 1fr;gap:3mm 8mm;font-size:8.5pt}
.credits dt{font-family:'Oswald';font-size:7pt;letter-spacing:.2em;text-transform:uppercase;color:#c8501e}
.credits dd{margin:0 0 2mm;font-family:'Barlow Condensed';font-size:11pt}
.toc{margin-top:6mm}
.toc div{display:flex;justify-content:space-between;border-bottom:1px dotted #bbb;padding:1.6mm 0;font-family:'Barlow Condensed';font-size:11pt}
.toc div span:last-child{font-family:'Bebas Neue';color:#c8501e}
/* personagens */
.char{display:grid;grid-template-columns:52mm 1fr;gap:6mm;align-items:start}
.char .emb{background:#f6f2e8;border-radius:3mm;padding:3mm;display:flex;flex-direction:column;align-items:center}
.char .emb img{width:46mm;height:61.3mm;object-fit:cover;border-radius:2mm;display:block}
.char.solo{grid-template-columns:72mm 1fr}
.char.solo .emb img{width:66mm;height:88mm}
.char .emb .nm{font-family:'Bebas Neue';font-size:26pt;line-height:1;margin-top:2mm;color:#141518}
.char .emb .fac{font-family:'Oswald';font-size:6.5pt;letter-spacing:.2em;text-transform:uppercase;color:#c8501e}
.char .emb.cad .fac{color:#9a7a2a}
.char dl{margin:0;font-size:8.6pt}
.char dt{font-family:'Oswald';font-size:7pt;letter-spacing:.18em;text-transform:uppercase;color:#c8501e;margin-top:2.2mm}
.char.cad dt{color:#9a7a2a}
.char dd{margin:0;line-height:1.45}
.char .frase{font-family:'Barlow Condensed';font-size:13pt;line-height:1.2;margin-top:4mm;color:#141518}
.stats{display:flex;gap:2mm;margin-top:3mm;width:100%}
.stats div{flex:1;background:#141518;color:#f1ebdd;border-radius:1.5mm;padding:1.5mm;text-align:center}
.stats div b{display:block;font-family:'Bebas Neue';font-size:13pt;line-height:1}
.stats div span{font-family:'Oswald';font-size:5.5pt;letter-spacing:.12em;text-transform:uppercase;opacity:.8}
.char2{display:grid;grid-template-rows:1fr 1fr;height:100%;gap:4mm}
.char2 .char{align-items:start}
.char2 .char .emb img{width:40mm;height:53.3mm}
.char2 .char .emb .nm{font-size:22pt}
.char2 dl{font-size:8pt}
.humans{display:grid;grid-template-columns:1fr 1fr;gap:5mm}
.hum{border:1.5px solid #141518;border-radius:3mm;padding:4mm}
.hum.pic{display:grid;grid-template-columns:30mm 1fr;gap:3.5mm;align-items:start}
.hum.pic img{width:30mm;height:40mm;object-fit:cover;border-radius:1.5mm}
.hum .nm{font-family:'Bebas Neue';font-size:20pt;line-height:1}
.hum .age{font-family:'Oswald';font-size:7pt;letter-spacing:.2em;color:#c8501e;text-transform:uppercase;margin-bottom:2mm}
.hum p{font-size:8.3pt}
/* facções */
.fac2{display:grid;grid-template-columns:1fr 1fr;gap:6mm}
.facbox{border-radius:3mm;padding:5mm;color:#f1ebdd}
.facbox.g{background:#141518}.facbox.c{background:#3a2a10}
.facbox .nm{font-family:'Bebas Neue';font-size:24pt;line-height:1}
.facbox .lema{font-family:'Barlow Condensed';font-size:11pt;color:#c9a24a;margin:2mm 0 3mm;line-height:1.2}
.facbox p{font-size:8.3pt;color:#e8e2d4}
/* storyboard */
.sb{padding:9mm 9mm 14mm 20mm;height:100%;position:relative}
.sb .pg{position:absolute;left:5mm;top:9mm;width:12mm;text-align:center}
.sb .pg .l{font-family:'Oswald';font-size:5.5pt;letter-spacing:.25em;text-transform:uppercase;color:#c8501e;writing-mode:vertical-rl;transform:rotate(180deg);display:block;margin:0 auto 2mm}
.sb .pg .n{font-family:'Bebas Neue';font-size:34pt;line-height:.9;color:#141518;display:block}
.sb .pg .tot{font-family:'Oswald';font-size:6pt;color:#999;display:block;letter-spacing:.1em}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:3mm;height:100%}
.panel{border:2px solid #141518;background:#fff radial-gradient(circle at 100% 100%, transparent 0 9mm, rgba(200,80,30,.10) 9mm 9.5mm, transparent 9.5mm 15mm, rgba(200,80,30,.08) 15mm 15.5mm, transparent 15.5mm 21mm, rgba(200,80,30,.06) 21mm 21.5mm, transparent 21.5mm 27mm, rgba(200,80,30,.04) 27mm 27.5mm, transparent 27.5mm) no-repeat;position:relative;padding:5mm 3mm 3mm 3mm;overflow:hidden;display:flex;flex-direction:column;gap:1.6mm;border-radius:1mm}
.panel.wide{grid-column:1/3}
.panel.art{padding:5mm 3mm 3mm 3mm;background-size:cover;background-position:center;background-repeat:no-repeat}
.panel.art .desc{display:none}
.panel.art .say{box-shadow:0 1px 3px rgba(0,0,0,.35)}
.panel.art .cap{box-shadow:0 1px 3px rgba(0,0,0,.35)}
.panel.art .sfx{color:#ffd9a0;text-shadow:2px 2px 0 #141518,-1px -1px 0 #141518,1px -1px 0 #141518,-1px 1px 0 #141518}
.panel.art .sfx{font-size:16pt;margin-top:auto;align-self:flex-end;margin-right:2mm}
.panel.art .sfx.huge{font-size:20pt}
.panel.art .say{max-width:72%}
.panel.art .cap{max-width:80%}
.panel.art .note{background:rgba(20,21,24,.75);color:#f1ebdd;border-radius:0 0 0 1.5mm}
.panel.art .final{background:rgba(20,21,24,.92)}
.panel.art .note-type{background:rgba(250,247,239,.95)}
.panel .pn{position:absolute;top:0;left:0;background:#141518;color:#f1ebdd;font-family:'Bebas Neue';font-size:9pt;line-height:1;padding:1mm 2mm .6mm;border-radius:0 0 1.5mm 0}
.panel .note{position:absolute;top:0;right:0;font-family:'Oswald';font-size:5.5pt;letter-spacing:.15em;text-transform:uppercase;color:#c8501e;padding:1.2mm 2mm}
.panel .desc{font-size:8pt;line-height:1.4;color:#555;font-style:italic}
.panel .desc.big{font-size:9.2pt}
.cap{background:#f3ecd8;border-left:3px solid #c8501e;padding:1.5mm 2.4mm;font-family:'Barlow Condensed';font-size:9pt;line-height:1.25;color:#141518;font-weight:600;letter-spacing:.01em;text-transform:uppercase}
.cap .who{font-size:6pt;letter-spacing:.2em;color:#c8501e;display:block;font-family:'Oswald';font-weight:600}
.say{border:1.4px solid #141518;border-radius:3.5mm;padding:1.6mm 2.8mm 1.7mm;font-size:8.5pt;line-height:1.3;background:#fff;max-width:92%;position:relative}
.say .who{display:block;font-family:'Oswald';font-weight:600;font-size:6.5pt;letter-spacing:.18em;text-transform:uppercase;color:#141518;margin-bottom:.3mm}
.say .who i{font-weight:400;letter-spacing:.05em;text-transform:none;color:#888}
.say.guarda .who{color:#b8261f}.say.cadinho .who{color:#9a7a2a}
.say.wavy{border-style:dashed;border-color:#c8501e}
.say.cadinho.wavy{border-color:#9a7a2a}
.say.thought{border-style:dotted;background:#faf8f2;font-style:italic}
.say.radio{border-radius:1mm;background:#141518;color:#f1ebdd;font-family:'JetBrains Mono',monospace;font-size:7pt}
.say.radio .who{color:#c9a24a}
.say.r{align-self:flex-end}
.sfx{font-family:'Bangers',cursive;font-size:22pt;line-height:.95;color:#c8501e;letter-spacing:.03em;text-shadow:1.5px 1.5px 0 #141518;transform:rotate(-3deg);margin:1mm 0 .5mm 2mm;word-break:break-all}
.sfx.huge{font-size:34pt}
.sfx .q{display:block;font-family:'Oswald';font-size:5.5pt;letter-spacing:.15em;color:#888;text-shadow:none;transform:none;text-transform:uppercase}
.note-type{font-family:'JetBrains Mono',monospace;font-size:7.4pt;white-space:pre-wrap;background:#faf7ef;border:1px solid #d8d2c4;padding:2mm 3mm;color:#222;line-height:1.4}
.final{margin-top:auto;background:#141518;color:#f1ebdd;font-family:'Bebas Neue';font-size:12pt;letter-spacing:.06em;padding:2mm 3mm;text-align:center}
.splash .desc{font-size:10pt;color:#444;line-height:1.5}
.splash .cap{font-size:11.5pt}
.splash .say{font-size:10pt}
/* arco */
table.arc{width:100%;border-collapse:collapse;font-size:7.9pt}
table.arc th{font-family:'Oswald';font-size:7pt;letter-spacing:.15em;text-transform:uppercase;text-align:left;color:#c8501e;padding:1.5mm 2mm;border-bottom:2px solid #141518}
table.arc td{padding:2mm;border-bottom:1px solid #e3ded2;vertical-align:top;line-height:1.38}
table.arc td.n{font-family:'Bebas Neue';font-size:22pt;color:#141518;line-height:1;width:9mm}
table.arc td.t{font-family:'Barlow Condensed';font-weight:700;font-size:11pt;width:30mm;line-height:1.1}
.extra{display:grid;grid-template-columns:1fr 1fr;gap:5mm}
.letter{background:#f6f2e8;padding:5mm;border-radius:3mm;font-family:'Barlow Condensed';font-size:10.5pt;line-height:1.35}
.sheet{border:2px solid #141518;padding:4mm;border-radius:2mm}
.sheet .tt{font-family:'Oswald';font-size:7pt;letter-spacing:.2em;text-transform:uppercase;color:#c8501e}
.sheet .nm{font-family:'Bebas Neue';font-size:28pt;line-height:1}
.sheet img{width:100%;height:60mm;object-fit:cover;object-position:center 20%;border-radius:1.5mm}
.dobra2{display:grid;grid-template-columns:1fr 1fr;gap:4mm;margin:2mm 0 2mm}
.dobra2 div{position:relative;height:58mm;border-radius:2mm;overflow:hidden;background-size:cover;background-position:center}
.dobra2 span{position:absolute;left:0;bottom:0;background:rgba(20,21,24,.85);color:#f1ebdd;font-family:'Bebas Neue';font-size:16pt;padding:1.5mm 4mm;letter-spacing:.05em}
.dobra2 small{display:block;font-family:'Oswald';font-size:6.5pt;letter-spacing:.15em;color:#c9a24a}
.sheet table{width:100%;font-size:8pt;border-collapse:collapse;margin-top:2mm}
.sheet td{padding:1.2mm 0;border-bottom:1px solid #ddd}
.sheet td:first-child{font-family:'Oswald';text-transform:uppercase;font-size:6.5pt;letter-spacing:.12em;color:#555;width:26mm}
.back{display:flex;flex-direction:column;justify-content:space-between;height:100%;padding:18mm 14mm}
.back .big{font-family:'Bebas Neue';font-size:40pt;line-height:.95;color:#f1ebdd}
.back p{color:#cfc8b8;font-family:'Barlow Condensed';font-size:12pt;line-height:1.3}
.barcode{display:flex;gap:1px;height:14mm;align-items:flex-end}
.barcode i{display:block;background:#f1ebdd;width:1.2px}
"""

def esc(t): return t  # já contém <b>/<i> controlados

def folio(left, n):
    return f'<div class="folio"><span>{left}</span><span>Canto de Ferro · nº 1 · {n:02d}</span></div>'

out=[]
def page(inner, cls="", left="", n=None):
    f=folio(left, n) if n else ""
    out.append(f'<section class="page {cls}">{inner}{f}</section>')

# ---------- CAPA ----------
page(f'''<div class="cover" style="position:absolute;inset:0"><img class="bg" src="{A('capa.jpg')}"><div class="shadetop"></div><div class="shade"></div>
<div class="num">Nº 1<small>Outubro 2026</small></div>
<div class="logo"><div class="t">CANTO<br>DE FERRO</div><div class="s">Primeira Têmpera</div><div class="s" style="margin-top:3mm;letter-spacing:.2em;opacity:.85">por {AUTHOR}</div></div>
<div class="tag">Todo metal lembra.<br><b>O nosso lembra você.</b></div>
<div class="pub">Uma revista em quadrinhos original · Minas Gerais, 1811–2026</div>
</div>''', cls="dark")

# ---------- FRONTISPÍCIO ----------
page(f'''<div class="rivets"></div><div class="pad">
<div class="kicker">Canto de Ferro · Edição nº 1</div>
<h1 class="sec">Primeira<br>Têmpera</h1>
<div class="rule"></div>
<p class="lead">Quando o sino mais antigo de Minas é retirado da torre para ser derretido, ele desperta todas as máquinas que nasceram do mesmo metal e decide que a humanidade só se salva sendo refundida. Um caminhão de bombeiros aposentado e um estagiário de 16 anos são os únicos que o ouvem a tempo.</p>
<dl class="credits" style="margin-top:8mm">
<div><dt>Criação e roteiro</dt><dd>{AUTHOR}</dd></div>
<div><dt>Arte</dt><dd>Ilustrações geradas por IA sob direção do autor</dd></div>
<div><dt>Formato</dt><dd>24 páginas de história + extras</dd></div>
<div><dt>Gênero</dt><dd>Ficção científica · Aventura · Época</dd></div>
<div><dt>Faixa etária</dt><dd>A partir de 10 anos</dd></div>
<div><dt>Ambientação</dt><dd>Sabará, Belo Horizonte e Ipanema (SP)</dd></div>
<div><dt>Periodicidade</dt><dd>Mensal · Arco "A Refundição" em 6 edições</dd></div>
<div><dt>Idioma</dt><dd>Português (Brasil)</dd></div>
</dl>
<div class="toc">
<div class="kicker" style="border:0;padding:0 0 2mm">Nesta edição</div>
<div><span>A Estrela de Sabará: a bíblia do universo</span><span>03</span></div>
<div><span>Ofício, Figura e a Dobra</span><span>05</span></div>
<div><span>Guarda da Bigorna × Cadinho</span><span>07</span></div>
<div><span>Glossário dos Forjados</span><span>08</span></div>
<div><span>Personagens</span><span>09</span></div>
<div><span>Roteiro ilustrado: "Primeira Têmpera", 24 páginas</span><span>17</span></div>
<div><span>Extras: carta ao leitor e ficha do Forjado</span><span>41</span></div>
<div><span>O primeiro arco: as seis edições</span><span>42</span></div>
</div>
<div class="quote" style="position:absolute;bottom:18mm;left:14mm;right:14mm">"Todo metal lembra o que foi. O nosso, além disso, lembra quem o usou."<small>Mestre Ambrósio Ferraz, Sabará, 1812</small></div>
</div>''', left="Frontispício", n=2)

# ---------- BÍBLIA 1: Origem ----------
page(f'''<div class="pad">
<div class="kicker">Bíblia do universo · I</div>
<h1 class="sec">A Estrela<br>de Sabará</h1>
<div class="rule"></div>
<div class="cols2">
<p>Na madrugada de 14 de agosto de 1811, um meteoro cruzou o céu de Minas Gerais e caiu na serra atrás da vila de Sabará. Não explodiu. Afundou na terra vermelha e ficou ali, zunindo. Quem chegou perto nos primeiros dias contou a mesma coisa: a pedra <b>cantava</b>. Um zumbido grave, contínuo, que fazia os dentes doerem e as vacas se recusarem a pastar.</p>
<p>O ferreiro liberto <b>Mestre Ambrósio Ferraz</b> foi o primeiro a tocar o minério sem medo. Descobriu que ele se deixava trabalhar como ferro comum, mas guardava o som do martelo: batia-se uma vez, e a peça continuava vibrando por horas, em afinação. A vila encomendou a ele um sino para a capela de Nossa Senhora do Ó. Ambrósio fundiu o sino com o coração do meteoro. Chamou-o de <b>Dobre</b>.</p>
<p>A Coroa portuguesa, que acabava de fundar a <b>Real Fábrica de Ferro de Ipanema</b> em São Paulo, soube do achado e confiscou o restante da pedra. Dali em diante, o ferro-canto foi misturado, aos poucos e sem registro, a tudo que o país fabricava com ferro durante um século e meio: trilhos, locomotivas, canhões da Guerra do Paraguai, teares de Blumenau, arados, cascos de barco e, por fim, chassis de caminhão e carrocerias de ônibus nas fábricas do ABC paulista.</p>
<p>Ninguém sabia. Mas o metal sabia.</p>
</div>
<h3>Dois séculos em uma linha</h3>
{timeline_svg()}
<h3>A regra central: a têmpera do uso</h3>
<p>O ferro-canto não nasce vivo. <b>Ele desperta pelo uso repetido.</b> Uma máquina feita com uma fração relevante de ferro-canto, operada pelas mesmas mãos, no mesmo ritmo, durante décadas, começa a guardar aquele ritmo como memória. Primeiro o metal aprende a tarefa. Depois aprende as <b>pessoas</b>: a postura, o peso, o jeito de olhar de quem a operou. Por fim, aprende a querer. Esse processo se chama <b>Têmpera</b>. Nenhum Forjado escolhe quando desperta.</p>
</div>''', left="Bíblia do universo", n=3)

# ---------- BÍBLIA 2: consequência + ressonância ----------
page(f'''<div class="pad">
<div class="kicker">Bíblia do universo · II</div>
<h1 class="sec">Cada Forjado é<br>a soma de quem o usou</h1>
<div class="rule"></div>
<div class="cols2">
<p>Um caminhão de bombeiros é corajoso porque carregou bombeiros corajosos. Um canhão é cruel porque só conheceu a guerra. Um sino que ouviu dois séculos de confissões acha que conhece a alma humana melhor do que qualquer humano.</p>
<p>Essa é a consequência narrativa de tudo na série: <b>cada cena de ação revela algo sobre as pessoas que operaram aquela máquina.</b> O Forjado não é um alienígena com um disfarce. É uma biografia coletiva, com rodas.</p>
<h3>Ressonância e Mudez</h3>
<p>Os Forjados não consomem combustível nem eletricidade. Alimentam-se de <b>Ressonância</b>: vibração rítmica contínua. Motores ligados, trilhos em uso, sinos tocando, fábricas em funcionamento, uma cidade em movimento. Um Forjado numa oficina viva está sempre alimentado. Um Forjado abandonado num galpão silencioso entra em <b>Mudez</b>: um sono sem sonhos de que poucos voltam inteiros.</p>
<p>A Mudez é o grande medo coletivo da espécie. É também a arma mais eficaz contra eles: silêncio absoluto, câmaras anecoicas, frio extremo que endurece o metal e abafa o canto.</p>
<h3>Afinar-se</h3>
<p>Os Forjados <b>falam cantando</b>. Para um humano destreinado, a voz de um Forjado é um zumbido grave no peito. Para ser compreendido, o Forjado precisa <b>afinar-se</b> à voz daquela pessoa, o que leva horas de convivência. Por isso escolhem com cuidado com quem falam.</p>
<h3>As Lascas</h3>
<p>Fragmentos brutos do meteoro original, nunca forjados, chamam-se <b>Lascas</b>. Existem poucas. Uma Lasca em contato com dois Forjados ao mesmo tempo <b>funde as memórias deles</b> por alguns segundos: cada um vê o que o outro viveu. É a única forma de um Forjado mentir ser descoberta. Lascas são o tesouro, a moeda e o segredo mais bem guardado da espécie.</p>
</div>
<div class="quote">"Eu ouvi duzentos anos de gente pedindo perdão. Ninguém nunca pediu para continuar como estava."<small>Dobre, o primeiro Forjado</small></div>
</div>''', left="Bíblia do universo", n=4)

# ---------- BÍBLIA 3: Ofício e Figura ----------
page(f'''<div class="pad">
<div class="kicker">Bíblia do universo · III</div>
<h1 class="sec">Ofício, Figura<br>e a Dobra</h1>
<div class="rule"></div>
<p class="lead">Todo Forjado tem exatamente duas formas, e a passagem entre elas se chama <b>Dobra</b>.</p>
<div class="dobra2"><div style="background-image:url({A('panel_08.jpg')})"><span>Ofício<small>o caminhão, 1958</small></span></div><div style="background-image:url({A('port_vigilia.jpg')});background-position:center 20%"><span>Figura<small>4,2 m · a memória de 36 anos de bombeiros</small></span></div></div>
<div class="cols2" style="margin-top:4mm">
<p><b>Ofício</b> é a forma para a qual a máquina foi fabricada: o caminhão, o sino, a locomotiva, o tear. É a forma de descanso e de disfarce, mas também a de maior força bruta.</p>
<p><b>Figura</b> é um corpo erguido, articulado, construído pelo próprio metal a partir da <b>memória dos corpos humanos que o usaram</b>. Por isso nenhuma Figura é igual: Vigília tem ombros largos e postura de quem carrega gente; Fuso tem dedos finos e muitos; Dobre não tem pernas, porque um sino nunca viu as pernas de quem o tocava, só as mãos e o rosto virado para cima.</p>
<h3>Limites da Dobra</h3>
<p><b>1.</b> A massa é conservada. Um sino de 900 kg vira uma Figura de 900 kg.</p>
<p><b>2.</b> A Dobra leva de 3 a 8 segundos e produz um <b>acorde</b>, um som metálico afinado que outros Forjados ouvem a quilômetros. Dobrar é anunciar-se.</p>
<p><b>3.</b> Um Forjado só pode ter <b>um</b> Ofício. Não existe copiar um veículo novo. O que você foi feito para ser é o que você é.</p>
<p><b>4.</b> Ferimentos na Figura aparecem no Ofício e vice-versa.</p>
</div>
<div class="quote">"Nenhum Forjado tem um rosto que não tenha visto."<small>Regra de ouro da série</small></div>
</div>''', left="Bíblia do universo", n=5)

# ---------- BÍBLIA 4: tom ----------
page(f'''<div class="pad">
<div class="kicker">Bíblia do universo · IV</div>
<h1 class="sec">Tom e regras<br>de escrita</h1>
<div class="rule"></div>
<div class="cols2">
<h3>Aventura com peso</h3><p>Ação grande, legível, com consequências físicas. Metal amassa e não volta sozinho.</p>
<h3>Memória é o superpoder e a maldição</h3><p>Cada cena de ação deve revelar algo sobre quem usou aquela máquina.</p>
<h3>O Brasil é cenário, não enfeite</h3><p>Ferrovias desativadas, igrejas barrocas, galpões do ABC, pátios de manutenção, o cerrado. Nada de cidade genérica.</p>
<h3>Humanos não são plateia</h3><p>Teo e Inácia resolvem problemas que os Forjados não conseguem: caber em lugares pequenos, mentir, convencer gente.</p>
<h3>Nada de disfarce secreto</h3><p>Quando um Forjado dobra na rua, as pessoas veem. A série trata do que acontece depois que viram.</p>
<h3>Sem vilão vazio</h3><p>Dobre está errado, mas nunca está mentindo.</p>
</div>
<h3>Convenção visual dos balões</h3>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:3mm;margin-top:2mm">
<div class="say human"><span class="who">Humano</span>Balão comum, contorno contínuo.</div>
<div class="say guarda wavy"><span class="who">Forjado <i>(balão ondulado)</i></span>Forjados falando entre si: contorno ondulado (aqui, tracejado), inaudível para humanos não afinados.</div>
<div class="say guarda"><span class="who">Vigília</span>Forjado afinado a um humano: contorno normal, nome em vermelho (Guarda) ou bronze (Cadinho).</div>
<div class="say radio"><span class="who">Rádio</span>Voz pelo rádio do caminhão: caixa escura, letra de máquina.</div>
</div>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:3mm;margin-top:3mm">
<div class="cap"><span class="who">Legenda</span>Narração e passagens de tempo: caixa creme com barra ferrugem.</div>
<div class="sfx" style="font-size:16pt">DOOOMMM <span class="q">efeito sonoro</span></div>
</div>
</div>''', left="Bíblia do universo", n=6)

# ---------- FACÇÕES ----------
page(f'''<div class="pad">
<div class="kicker">Bíblia do universo · V</div>
<h1 class="sec">As facções</h1>
<div class="rule"></div>
<div class="fac2">
<div class="facbox g"><div class="nm">Guarda da Bigorna</div><div class="lema">"Carregar, não ser carregado.<br>Guardar, não ser guardado."</div>
<p>Fundada em 1897 pelos primeiros Forjados despertos na ferrovia, a Guarda decidiu que a espécie deveria permanecer <b>oculta e útil</b>. Acreditam que a vida deles é um empréstimo das mãos que os usaram e que a dívida se paga protegendo essas mãos.</p>
<p>Símbolo: uma bigorna vista de cima, com um círculo no centro. Juntas marcadas por <b>pintura desgastada</b>, as cores originais de trabalho descascadas pelo uso.</p>
<p style="margin-top:3mm"><b>Membros:</b> Vigília, Maré, Fuso, Cerrado, Cálamo.</p></div>
<div class="facbox c"><div class="nm">O Cadinho</div><div class="lema">"Eu posso fundir o perdão."</div>
<p>Dobre fundou o Cadinho em segredo nos anos 1970, quando ouviu, do alto da torre, que sinos antigos de Minas estavam sendo vendidos para fundição. Sua tese: os Forjados são <b>um só ser partido em pedaços</b>, e existir em pedaços é sofrimento. A solução é a <b>Refundição</b>: derreter todo o ferro-canto do mundo, junto com todo o ferro em que ele se misturou, em um único corpo, <b>o Lingote</b>.</p>
<p>Símbolo: um cadinho derramando, com uma gota em forma de sino. Juntas <b>polidas até o espelho</b>: Dobre exige que seus seguidores apaguem as marcas de uso.</p>
<p style="margin-top:3mm"><b>Membros:</b> Dobre, Lastro, Estilhaço, Grimpa e os Mudos.</p></div>
</div>
<h3>Os Mudos</h3>
<p>Forjados que caíram em Mudez e foram despertados à força por Dobre com Ressonância bruta. Voltam sem memória própria, apenas com a tarefa que ele lhes dá. São a tropa do Cadinho e a prova de que ele está disposto a esvaziar os seus para preencher o seu plano. Ao fim da edição nº 1, são trezentos e doze.</p>
<h3>O Concílio Mudo</h3>
<p>Nome antigo da reunião secreta de todos os Forjados despertos, extinta após a cisão de Dobre. Faz cinquenta anos que o primeiro Forjado não fala com nenhum dos outros. Até agora.</p>
</div>''', left="Bíblia do universo", n=7)

# ---------- GLOSSÁRIO ----------
GLOS=[("Ferro-canto","O minério do meteoro de 1811. Vibra em afinação quando trabalhado."),("Forjado(a)","Uma máquina despertada pela Têmpera."),("Têmpera","O despertar pelo uso repetido ao longo de décadas."),("Ofício","A forma original da máquina."),("Figura","O corpo erguido, construído da memória dos corpos humanos que a usaram."),("Dobra / Dobrar","A transformação entre Ofício e Figura. Produz um acorde audível."),("Acorde","O som da Dobra. Cada Forjado tem o seu, como uma assinatura."),("Ressonância","A vibração rítmica de que os Forjados se alimentam."),("Mudez","Sono profundo por falta de Ressonância. Pode ser permanente."),("Afinar-se","O processo de um Forjado tornar sua voz compreensível a um humano específico."),("Lasca","Fragmento bruto do meteoro. Funde memórias."),("Badalo","O pulso sonoro de Dobre: força a Dobra em outros Forjados e arranca Forjados da Mudez."),("Guarda da Bigorna","Facção que protege os humanos e permanece oculta."),("Cadinho","Facção de Dobre. Quer a Refundição."),("Refundição / O Lingote","O plano de derreter todo o ferro-canto em um só corpo."),("Os Mudos","Forjados despertados à força, sem memória, a serviço de Dobre."),("Concílio Mudo","A antiga reunião secreta de todos os Forjados despertos.")]
page(f'''<div class="pad">
<div class="kicker">Bíblia do universo · VI</div>
<h1 class="sec">Glossário<br>dos Forjados</h1>
<div class="rule"></div>
<table class="glos">{"".join(f"<tr><td>{a}</td><td>{b}</td></tr>" for a,b in GLOS)}</table>
</div>''', left="Glossário", n=8)

# ---------- PERSONAGENS ----------
CH={
"vigilia":dict(nm="Vigília",fac="Guarda da Bigorna",cls="",oficio="Caminhão de bombeiros com escada Magirus, chassi 1958, vermelho desbotado, frota do Corpo de Bombeiros de Belo Horizonte. Aposentado em 1994, exposto no Museu dos Bombeiros.",figura="4,2 m. Ombros muito largos, braços longos; a escada dobrada forma a coluna vertebral e pode se estender pelas costas como uma cauda rígida de apoio. Rosto quadrado, dois faróis como olhos e uma viseira (o para-brisa) que ele abaixa quando está sério.",desp="1983, no incêndio de um depósito de tecidos na Lagoinha, quando sentiu a escada esticar antes de o operador puxar a alavanca. Nunca saiu de Minas.",pers="Calmo, lento para falar, rápido para agir. Carrega 36 anos de bombeiros dentro de si e fala com os maneirismos de todos eles ao mesmo tempo. Conta o tempo em turnos. Odeia sirenes desnecessárias.",acorde="Três notas descendentes, graves, como uma sirene antiga desacelerando.",frase="Primeiro tira todo mundo. Depois a gente discute de quem é a culpa.",stats=[("4,2 m","altura"),("11,4 t","massa"),("1958","fabricação"),("1983","despertar")]),
"dobre":dict(nm="Dobre",fac="O Cadinho · o primeiro Forjado",cls="cad",oficio="Sino de bronze com coração de ferro-canto puro, 900 kg, fundido em 1812 por Ambrósio Ferraz para a capela de Nossa Senhora do Ó, em Sabará.",figura="4,5 m, sem pernas. Flutua a poucos centímetros do chão por ressonância. O corpo é o sino invertido abrindo-se em quatro pétalas de bronze; dentro, um torso de ferro escuro. A cabeça é um rosto erguido, de olhos fechados, memória de dois séculos de fiéis olhando para cima. Mãos pequenas e delicadas: as mãos dos sineiros.",desp="Por volta de 1840. Passou 180 anos acordado, sozinho, ouvindo tudo que se dizia abaixo dele: confissões, casamentos, velórios, brigas, a cidade inteira mudando.",pers="Gentil, paciente, melancólico, absolutamente convicto. Fala baixo. Quando grita, é um badalo que estilhaça vidro num raio de cem metros. Não se vê como vilão: vê-se como o único que ouviu o suficiente para ter o direito de decidir.",acorde="Um único toque de sino, perfeito, que dura demais. Poder próprio: o Badalo.",frase="Eu ouvi duzentos anos de gente pedindo perdão. Ninguém nunca pediu para continuar como estava.",stats=[("4,5 m","altura"),("900 kg","massa"),("1812","fundição"),("c. 1840","despertar")]),
"mare":dict(nm="Maré",fac="Guarda da Bigorna",cls="",oficio="Barco de pesca de arrasto, 14 m, casco de aço, Itajaí (SC), 1964. Nome no casco: Nossa Senhora dos Navegantes II.",figura="5 m, assimétrica. O casco se abre como duas asas pesadas que servem de escudo; as redes viram cabos preênseis. Única Forjada anfíbia conhecida.",desp="1998, em alto-mar, numa tempestade, quando virou sozinha o leme para salvar a tripulação.",pers="Irônica, direta, supersticiosa à maneira dos pescadores. Segunda em comando, e a única que discorda de Vigília na frente dos outros.",acorde="Duas notas longas em uníssono, com um baque surdo no fim.",frase="Em terra todo mundo é corajoso. Quero ver com água na canela.",stats=[("5 m","altura"),("1964","fabricação"),("1998","despertar")]),
"fuso":dict(nm="Fuso",fac="Guarda da Bigorna",cls="",oficio="Tear mecânico de uma tecelagem de Blumenau (SC), 1922, reformado com peças de ferro-canto nos anos 1940.",figura="2,1 m, magra, com oito dedos finos em cada mão e um pente de lançadeiras no antebraço que dispara e recolhe cabos de aço. A menor da Guarda e a mais rápida.",desp="1971. A fábrica fechou em 1972 e Fuso passou 19 anos em Mudez até ser religada por um colecionador.",pers="Fala rápido, tece frases dentro de frases. Pavor da Mudez: nunca desliga por completo. A técnica do grupo.",acorde="Sequência rápida e tiquetaqueante, como uma lançadeira correndo.",frase="Rasgou? Rasgou. Agora olha o que eu faço com rasgado.",stats=[("2,1 m","altura"),("1922","fabricação"),("1971","despertar")]),
"cerrado":dict(nm="Cerrado",fac="Guarda da Bigorna",cls="",oficio="Trator agrícola Valmet 85 id, 1972, de uma fazenda de soja em Rio Verde (GO). Amarelo-laranja, para-lamas remendados.",figura="3,8 m, atarracada, pernas curtas e braços enormes terminados em pás. O escapamento forma uma chaminé no ombro.",desp="2004, quando o fazendeiro que o dirigiu por 32 anos morreu na cabine, no meio da lavoura, e o trator terminou a linha sozinho antes de parar.",pers="Fala pouco e em frases curtas. Imensa paciência e um senso de ciclo: planta, espera, colhe.",acorde="Uma nota só, longa, muito grave.",frase="Terra não tem pressa. Eu também não.",stats=[("3,8 m","altura"),("1972","fabricação"),("2004","despertar")]),
"calamo":dict(nm="Cálamo",fac="Guarda da Bigorna",cls="",oficio="Máquina de escrever Remington 12, 1927, da redação do Estado de Minas. Escreveu notícias por 50 anos.",figura="60 cm. Teclas que viram dedos, carro de impressão que vira visor. Anda sobre quatro hastes finas. Olheiro e arquivista: grava tudo que ouve. Não luta.",desp="1977. Primeiro Forjado a aprender a ler, porque passou décadas vendo as letras que ele mesmo imprimia.",pers="Fala em manchetes. Preciso, pedante, acha que nada aconteceu até ser registrado. O único que Teo carrega na mochila.",acorde="Um tim de fim de linha.",frase="Anotado. E eu não anoto mentira.",stats=[("60 cm","altura"),("1927","fabricação"),("1977","despertar")]),
"lastro":dict(nm="Lastro",fac="O Cadinho",cls="cad",oficio="Locomotiva 2-8-0, 1912, da antiga Estrada de Ferro Central do Brasil, convertida a diesel nos anos 1950. Preta, imensa.",figura="7 m. O maior Forjado conhecido. Caldeira como tórax, rodas motrizes nos ombros e quadris. Rosto achatado, memória de maquinistas olhando sempre para a frente.",desp="Desconhecido. Dobre o tirou de 40 anos de Mudez num pátio abandonado em Lafaiete.",pers="Leal a Dobre por gratidão. Só sabe seguir trilho: dada uma direção, não para. Não é cruel. É inevitável.",acorde="Um apito longo e um baque de engate.",frase="Eu não desvio. Quem desvia é a carga.",stats=[("7 m","altura"),("1912","fabricação"),("Mudez","40 anos")]),
"estilhaco":dict(nm="Estilhaço",fac="O Cadinho",cls="cad",oficio="Canhão La Hitte de 1866, da Guerra do Paraguai, fundido em Ipanema com o lote mais pesado de ferro-canto confiscado.",figura="3 m, sobre rodas raiadas. O braço direito é o próprio cano. Cabeça sem rosto: só um escudo liso. Nunca viu o rosto de ninguém, apenas as costas dos artilheiros e o inimigo ao longe.",desp="Desconhecido. Exposto por um século no pátio de um quartel.",pers="Só conheceu a guerra, então acha que tudo é guerra. Fala em ordens e distâncias. Nunca hesita.",acorde="Um estampido seco e o chiado da recarga.",frase="Alcance: oitocentos. Vento: nenhum. Motivo: dispensável.",stats=[("3 m","altura"),("1866","fundição"),("800 m","alcance")]),
"grimpa":dict(nm="Grimpa",fac="O Cadinho",cls="cad",oficio="Galo de catavento de ferro, 1890, do telhado da estação ferroviária de Sabará.",figura="90 cm. Articulada, esguia, pescoço longo; gira a cabeça 360 graus. Sobe em qualquer coisa. A espiã do Cadinho: viu a cidade por 130 anos de cima e viu Dobre todos os dias da torre vizinha.",desp="Desconhecido. Provavelmente a segunda Forjada a despertar em Sabará.",pers="Ciumenta, fofoqueira, devota de Dobre. Mente com facilidade; é a razão de a Guarda valorizar tanto as Lascas.",acorde="Um rangido de eixo e um estalo.",frase="O vento muda. Eu não. Eu só mostro para onde ele foi.",stats=[("90 cm","altura"),("1890","fabricação"),("360°","visão")]),
}
def char_block(k, solo=False):
    c=CH[k]
    stats="".join(f'<div><b>{a}</b><span>{b}</span></div>' for a,b in c["stats"])
    return f'''<div class="char {c['cls']}{" solo" if solo else ""}">
<div class="emb {c['cls']}"><img src="{A(f'port_{k}.jpg')}"><div class="nm">{c['nm']}</div><div class="fac">{c['fac']}</div><div class="stats">{stats}</div></div>
<div><dl>
<dt>Ofício</dt><dd>{c['oficio']}</dd>
<dt>Figura</dt><dd>{c['figura']}</dd>
<dt>Despertar</dt><dd>{c['desp']}</dd>
<dt>Personalidade</dt><dd>{c['pers']}</dd>
<dt>Acorde</dt><dd>{c['acorde']}</dd>
</dl><div class="frase">"{c['frase']}"</div></div></div>'''

n=9
for k in ("vigilia","dobre"):
    page(f'<div class="pad"><div class="kicker">Personagens · {CH[k]["fac"]}</div><h1 class="sec">{CH[k]["nm"]}</h1><div class="rule"></div>{char_block(k, solo=True)}</div>', left="Personagens", n=n); n+=1
for a,b in (("mare","fuso"),("cerrado","calamo"),("lastro","estilhaco")):
    page(f'<div class="pad"><div class="kicker">Personagens</div><div class="char2">{char_block(a)}{char_block(b)}</div></div>', left="Personagens", n=n); n+=1
HUM=[("Teo (Teodoro Nascimento)","16 anos","Estagiário do Museu dos Bombeiros de Belo Horizonte, aluno do curso técnico de mecânica. Mora com a avó na Lagoinha. Cresceu ouvindo histórias do avô bombeiro, que morreu antes de ele nascer. Gosta de consertar coisas porque coisas consertadas ficam. É o primeiro humano a quem Vigília se afina em 40 anos. Cabe onde Forjados não cabem e pergunta \"para quem\" toda vez que alguém diz \"é para o bem de todos\"."),
("Dra. Inácia Varela","44 anos","Engenheira metalurgista da Fundição Sabará Ltda., contratada para avaliar o sino antes da \"restauração\". É a primeira pessoa em dois séculos a analisar o ferro-canto em laboratório, e percebe que o espectrograma do metal muda quando alguém fala perto dele. Cética, metódica, dura. A única com quem Dobre faz questão de conversar."),
("Dona Zélia","71 anos","Avó de Teo, viúva de bombeiro. Guarda uma caixa com as coisas do marido. Numa delas há uma foto: ele, jovem, sentado no para-choque de um caminhão vermelho com escada Magirus. Ela sabe mais do que diz desde a primeira cena."),
("Prefeito Odair Custódio","Antagonista menor","Vendeu o sino para fundição e prometeu uma réplica à igreja. Não é mau, é pequeno. Serve para lembrar que o desastre começa com uma decisão administrativa.")]
page(f'''<div class="pad"><div class="kicker">Personagens · O Cadinho</div><h1 class="sec">Grimpa</h1><div class="rule"></div>{char_block("grimpa", solo=True)}
<div class="quote" style="margin-top:12mm">"Mente com facilidade. É a razão de a Guarda da Bigorna valorizar tanto as Lascas: diante de uma Lasca, nenhum Forjado consegue mentir."<small>Sobre Grimpa, a espiã do Cadinho</small></div></div>''', left="Personagens", n=n); n+=1
page(f'''<div class="pad"><div class="kicker">Personagens</div><h1 class="sec">Os humanos</h1><div class="rule"></div>
<p class="lead">Humanos não são plateia. Eles cabem onde os Forjados não cabem, mentem quando precisam e sabem onde os adultos guardam as chaves.</p>
<div class="humans" style="margin-top:4mm;grid-template-columns:1fr">{"".join((f'<div class="hum pic"><img src="{A(f'port_{k}.jpg')}"><div><div class="nm">{a}</div><div class="age">{b}</div><p>{c}</p></div></div>' if k else f'<div class="hum"><div class="nm">{a}</div><div class="age">{b}</div><p>{c}</p></div>') for (a,b,c),k in zip(HUM,["teo","inacia",None,None]))}</div></div>''', left="Personagens", n=n); n+=1

# ---------- ABERTURA DO ROTEIRO ----------
page(f'''<div class="pad" style="display:flex;flex-direction:column;justify-content:center">
<div class="kicker bronze">Roteiro ilustrado · 24 páginas</div>
<h1 class="sec bone" style="font-size:66pt">Primeira<br>Têmpera</h1>
<div class="rule" style="background:#c9a24a"></div>
<p style="color:#cfc8b8;font-family:'Barlow Condensed';font-size:12pt;line-height:1.35">Cada página a seguir reproduz a diagramação proposta da edição: a grade de quadros, as indicações de cena para o desenhista, as legendas, os balões e os efeitos sonoros, no lugar em que vão aparecer. O quadro principal de cada página está ilustrado; os demais trazem a indicação de cena para o desenhista.</p>
<p style="color:#cfc8b8;font-family:'Barlow Condensed';font-size:12pt;line-height:1.35"><b style="color:#f1ebdd">Como ler.</b> Nos quadros ainda sem arte, o texto em itálico cinza é a indicação de cena. Caixas creme são legendas de narração. Balões com nome em vermelho são da Guarda da Bigorna; em bronze, do Cadinho; tracejados, falas que humanos não afinados não ouvem.</p>
<div style="margin-top:12mm;color:#c9a24a;font-family:'Oswald';font-size:8pt;letter-spacing:.3em;text-transform:uppercase">Sabará, Minas Gerais · 14 de agosto de 1811</div>
</div>''', cls="dark", left="Roteiro", n=n); n+=1

# ---------- STORYBOARD ----------
def render_item(it, splash=False):
    k=it['kind']
    if k=='desc': return f'<div class="desc{" big" if splash else ""}">{it["text"]}</div>'
    if k=='cap':
        who=f'<span class="who">Legenda · {it["who"]}</span>' if it.get('who') else ''
        return f'<div class="cap">{who}{it["text"]}</div>'
    if k=='sfx':
        huge=len(it['text'])>14 or 'página' in it.get('q','')
        q=f'<span class="q">{it["q"]}</span>' if it.get('q') else ''
        return f'<div class="sfx{" huge" if huge else ""}">{it["text"]}{q}</div>'
    if k=='note': return f'<div class="note-type">{html.escape(it["text"])}</div>'
    if k=='final': return f'<div class="final">{it["text"]}</div>'
    if k=='say':
        cls=["say",it.get('side','human')]
        if it.get('wavy'): cls.append('wavy')
        if it.get('thought'): cls.append('thought')
        q=it.get('q','')
        q=q.replace('balão ondulado','').replace('balão trêmulo','').replace('balão pequeno, redondo','').replace('balão pequeno','').strip(' ,')
        qq=f' <i>({q})</i>' if q and q not in ('pensamento, legenda',) else ''
        if it['side']=='cadinho' or it['who'] in ('TEO','INÁCIA') and False: pass
        side_r = it['who'] in ('DOBRE','GRIMPA','LASTRO','ESTILHAÇO','INÁCIA','ZÉLIA','ODAIR','NILTON','OPERÁRIO 2','HOMEM DA VILA','BOMBEIRO JOVEM')
        if side_r: cls.append('r')
        who=it['who'].title() if it['who'] not in ('TEO',) else 'Teo'
        return f'<div class="{" ".join(cls)}"><span class="who">{html.escape(who)}{qq}</span>{it["text"]}</div>'
    return ''

ART={1:1,2:1,3:1,4:3,5:1,6:1,7:4,8:3,9:5,10:4,11:5,12:1,13:3,14:1,15:1,16:3,17:1,18:1,19:1,20:2,21:1,22:2,23:5,24:5}
def is_wide(p):
    nt=p['note'].lower()
    return any(w in nt for w in ('faixa','página inteira','quadro grande','splash'))

for pg in PAGES:
    panels=pg['panels']; cnt=len(panels)
    wide=[is_wide(p) for p in panels]
    narrow=sum(1 for w in wide if not w)
    if narrow%2==1:
        # torna largo o último quadro estreito
        for i in range(cnt-1,-1,-1):
            if not wide[i]: wide[i]=True; break
    rows=sum(1 for w in wide if w)+ (cnt-sum(1 for w in wide if w))//2
    splash = cnt==1
    cells=[]
    for p,w in zip(panels,wide):
        note=f'<span class="note">{html.escape(p["note"])}</span>' if p['note'] else ''
        inner="".join(render_item(it, splash) for it in p['items'])
        art = ART.get(pg["num"])==p["num"]
        pfile = "panel_%02d.jpg" % pg["num"]
        style = f' style="background-image:url({A(pfile)})"' if art else ''
        cells.append(f'<div class="panel{" wide" if w else ""}{" splash" if splash else ""}{" art" if art else ""}"{style}><span class="pn">{p["num"]}</span>{note}{inner}</div>')
    grid=f'<div class="grid" style="grid-template-rows:repeat({rows},1fr)">{"".join(cells)}</div>'
    page(f'<div class="sb"><div class="pg"><span class="l">Página</span><span class="n">{pg["num"]:02d}</span><span class="tot">/ 24</span></div>{grid}</div>', left="Primeira Têmpera · roteiro", n=n); n+=1

# ---------- EXTRAS ----------
page(f'''<div class="pad"><div class="kicker">Extras</div><h1 class="sec">Contracapa<br>interna</h1><div class="rule"></div>
<div class="extra">
<div class="letter"><div class="kicker" style="margin-bottom:2mm">Carta ao leitor</div>
Toda criança que já teve um carrinho de ferro sabe que ele não é só um carrinho. Ele é a viagem, o chão da sala, a mão que o empurrou. <b>Canto de Ferro</b> nasce dessa intuição: e se o metal se lembrasse? E se as máquinas que construíram um país tivessem guardado, no corpo, as pessoas que as usaram?<br><br>
Não viriam do espaço. Viriam da fundição, da ferrovia, da fazenda, da fábrica. Teriam o nosso sotaque. E, como nós, teriam que decidir o que fazer com o que lembram.<br><br>
Boa leitura. E, se o seu carro fizer um barulho estranho esta noite, não desligue o rádio.</div>
<div class="sheet"><div class="tt">Ficha do Forjado · nº 1</div><div class="nm">Vigília</div>
<img src="{A('port_vigilia.jpg')}" style="margin:2mm 0">
<table>
<tr><td>Ofício</td><td>Caminhão de bombeiros, escada Magirus, 1958</td></tr>
<tr><td>Massa</td><td>11.400 kg</td></tr>
<tr><td>Altura em Figura</td><td>4,2 m</td></tr>
<tr><td>Acorde</td><td>Três notas descendentes (Sol, Mi, Dó)</td></tr>
<tr><td>Despertar</td><td>1983, Rua Itapecerica, Belo Horizonte</td></tr>
<tr><td>Lema</td><td>"Primeiro tira todo mundo."</td></tr>
</table></div></div>
<h3>Página de rascunhos</h3>
<p>Estudos do desenhista para a Figura de Dobre: três versões descartadas com pernas, e a nota manuscrita: <i>"Ele nunca viu perna. Tirar. Fazer ele flutuar. Fica MUITO pior assim."</i></p>
</div>''', left="Extras", n=n); n+=1

# ---------- ARCO ----------
ARC=[("1","Primeira Têmpera","Vigília","Dobre é retirado da torre, revela-se a Inácia, convoca Lastro e Estilhaço. Vigília desperta diante de Teo e sai do museu pela primeira vez. Fuga de Sabará. Dobre acende o forno e desperta 312 Forjados em Mudez."),
("2","Os que Dormem","Fuso","Pelo país, máquinas acordam sem memória: os Mudos. Vigília, Teo e Inácia buscam a Guarda da Bigorna no pátio ferroviário abandonado de Lafaiete e encontram Fuso e Cerrado. Flashback: 1972, Fuso cai em Mudez quando a fábrica fecha."),
("3","Água na Canela","Maré","A única Lasca conhecida está afundada em Itajaí, num casco de 1964. Maré entra na série. Combate anfíbio contra Mudos no porto. Cálamo descobre que Grimpa planta mentiras entre a Guarda."),
("4","Nenhum Rosto que Não Tenha Visto","Estilhaço","Estilhaço é enviado a Belo Horizonte para capturar Dona Zélia. Flashback: 1866. Vigília enfrenta Estilhaço na Lagoinha, à luz do dia, diante de centenas de pessoas: o fim do segredo."),
("5","O Concílio Mudo","Dobre","Dobre reúne os 312 Mudos na antiga Real Fábrica de Ferro de Ipanema. Inácia, com a Lasca, funde memórias com Dobre e entende: ele não quer destruir, quer parar de ouvir. Lastro hesita pela primeira vez."),
("6","Lingote","Cerrado","Batalha em Ipanema. Teo entra no forno desligado. Vigília oferece a Dobre o que ele nunca teve: silêncio voluntário. Dobre aceita voltar ao alto da torre e nunca mais tocar. Lastro pede para entrar na Guarda. As 312 máquinas precisam de um lugar no mundo.")]
page(f'''<div class="pad"><div class="kicker">O primeiro arco · A Refundição</div><h1 class="sec">Seis edições</h1><div class="rule"></div>
<table class="arc"><tr><th></th><th>Título</th><th>Destaque</th><th>O que acontece</th></tr>
{"".join(f'<tr><td class="n">{a}</td><td class="t">{b}</td><td class="bar" style="font-weight:600;width:18mm">{c}</td><td>{d}</td></tr>' for a,b,c,d in ARC)}</table>
<h3>Fio condutor emocional</h3>
<div class="cols2"><p><b>Teo:</b> de "o caminhão que meu avô dirigiu uma vez" a "o caminhão que lembra do meu avô melhor do que eu". <b>Inácia:</b> de cética a tradutora. <b>Vigília:</b> de escondido a visível. <b>Dobre:</b> de monstro a tragédia: a criatura que ouviu demais, e cujo fim não é morte nem derrota, é descanso.</p></div>
<h3>Segundo arco (notas)</h3>
<p>Título de trabalho: <b>"Carregar, não ser carregado."</b> O mundo sabe. O governo quer registrar os Forjados como patrimônio ou como armas. E, no fundo de um pátio em Lafaiete, um Forjado que ninguém despertou acorda sozinho, sem ter sido usado por ninguém. O que lembra uma máquina que nunca foi tocada?</p>
</div>''', left="Plano de arco", n=n); n+=1

# ---------- CONTRACAPA ----------
import random; random.seed(7)
bars="".join(f'<i style="height:{random.choice([60,80,100])}%;width:{random.choice([1,1,2,3])}px"></i>' for _ in range(70))
page(f'''<div class="back">
<div><div class="kicker bronze">Na próxima edição</div><div class="big">Canto de Ferro nº 2<br><span class="bronze">Os que Dormem</span></div>
<p style="margin-top:6mm">Trezentos e doze máquinas abriram os olhos sem saber quem são. Em um pátio ferroviário abandonado em Lafaiete, a Guarda da Bigorna se reúne pela primeira vez em cinquenta anos. E um tear que passou dezenove anos em silêncio tem muito a dizer.</p></div>
<div style="display:flex;justify-content:center"><img src="{A('port_dobre.jpg')}" style="width:84mm;height:112mm;object-fit:cover;border-radius:2mm"></div>
<div><p style="font-size:9pt;color:#8a8578">© {AUTHOR}. Canto de Ferro é uma obra de ficção original. Personagens, nomes, facções e mitologia são inéditos. Sabará, a Real Fábrica de Ferro de Ipanema e a Estrada de Ferro Central do Brasil são lugares reais usados como cenário ficcional.</p>
<div style="display:flex;justify-content:space-between;align-items:flex-end"><div class="barcode">{bars}</div><div class="bebas" style="font-size:22pt;color:#f1ebdd">Nº 1</div></div></div>
</div>''', cls="dark")

HTML=f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>Canto de Ferro nº 1</title>
<link rel="stylesheet" href="fonts.css"><style>{CSS}</style></head><body>{"".join(out)}</body></html>'''
open("canto-de-ferro-01.html","w").write(HTML)
print("pages:", len(out))
