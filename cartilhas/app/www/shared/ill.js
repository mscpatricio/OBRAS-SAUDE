/* ============================================================
   ill.js — biblioteca de ilustrações vetoriais (SVG) no estilo
   "HQ" (traço grosso, cores chapadas) usada pelas cartilhas.
   Tudo é gerado em tempo de carregamento: os elementos com
   [data-scene="nome"] recebem o SVG da cena correspondente.
   ============================================================ */
(function () {
  const OUT = '#2B2B2B';      // cor do contorno
  const SW = 3;               // espessura do contorno
  const S = `stroke="${OUT}" stroke-width="${SW}" stroke-linejoin="round" stroke-linecap="round"`;

  // ------------------------------------------------------------
  // utilitários
  // ------------------------------------------------------------
  const g = (inner, attrs = '') => `<g ${attrs}>${inner}</g>`;
  const at = (inner, x, y, s = 1, extra = '') =>
    `<g transform="translate(${x} ${y}) scale(${s}) ${extra}">${inner}</g>`;
  const mirror = (x) => 200 - x;

  function esc(t) {
    return String(t).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }

  // texto HTML dentro do SVG (quebra de linha automática)
  function htmlText(x, y, w, h, text, size = 13, weight = 700, color = OUT, align = 'center', font = 'Comic Neue') {
    return `<foreignObject x="${x}" y="${y}" width="${w}" height="${h}">
      <div xmlns="http://www.w3.org/1999/xhtml" style="display:flex;align-items:center;justify-content:${align === 'center' ? 'center' : 'flex-start'};width:100%;height:100%;font-family:'${font}',sans-serif;font-size:${size}px;font-weight:${weight};line-height:1.15;color:${color};text-align:${align};padding:2px 4px;box-sizing:border-box;">${text}</div>
    </foreignObject>`;
  }

  // ------------------------------------------------------------
  // balões de fala / pensamento
  // ------------------------------------------------------------
  function bubble({ x, y, w, h, text, tail = null, kind = 'speech', size = 13, fill = '#FFFFFF' }) {
    let out = '';
    const r = 14;
    if (kind === 'speech') {
      if (tail) {
        const [tx, ty] = tail;
        // base do rabicho no ponto da borda mais próximo
        const cx = x + w / 2, cy = y + h / 2;
        const bx = tx < cx ? x + w * 0.35 : x + w * 0.65;
        const by = ty > cy ? y + h : y;
        out += `<polygon points="${bx - 10},${by} ${bx + 10},${by} ${tx},${ty}" fill="${fill}" ${S}/>`;
      }
      out += `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="${r}" fill="${fill}" ${S}/>`;
      if (tail) {
        const [tx, ty] = tail;
        const cx = x + w / 2, cy = y + h / 2;
        const bx = tx < cx ? x + w * 0.35 : x + w * 0.65;
        const by = ty > cy ? y + h : y;
        out += `<polygon points="${bx - 10},${by} ${bx + 10},${by} ${tx},${ty}" fill="${fill}" stroke="none"/>`;
        out += `<line x1="${bx - 10}" y1="${by}" x2="${tx}" y2="${ty}" ${S}/><line x1="${bx + 10}" y1="${by}" x2="${tx}" y2="${ty}" ${S}/>`;
      }
    } else {
      // nuvem de pensamento
      const bumps = [];
      const n = Math.max(6, Math.round((w + h) / 28));
      for (let i = 0; i < n; i++) {
        const t = i / n * Math.PI * 2;
        const px = x + w / 2 + Math.cos(t) * (w / 2 - 4);
        const py = y + h / 2 + Math.sin(t) * (h / 2 - 4);
        bumps.push(`<circle cx="${px}" cy="${py}" r="${Math.min(w, h) / 4.2}" fill="${fill}" ${S}/>`);
      }
      out += bumps.join('');
      out += `<rect x="${x + 6}" y="${y + 6}" width="${w - 12}" height="${h - 12}" rx="${r}" fill="${fill}"/>`;
      out += bumps.map(b => b.replace(S, 'stroke="none"')).join('');
      if (tail) {
        const [tx, ty] = tail;
        const cx = x + w / 2, cy = y + h / 2;
        for (let i = 1; i <= 3; i++) {
          const f = i / 4;
          const px = cx + (tx - cx) * (0.55 + f * 0.45), py = cy + (ty - cy) * (0.55 + f * 0.45);
          out += `<circle cx="${px}" cy="${py}" r="${7 - i * 1.6}" fill="${fill}" ${S}/>`;
        }
      }
    }
    out += htmlText(x + 4, y + 4, w - 8, h - 8, text, size);
    return out;
  }

  // ------------------------------------------------------------
  // PERSONAGEM (vista frontal). Caixa local 200 x 310, pés em y=300.
  // ------------------------------------------------------------
  const ARM = {
    down:  { e: [52, 182], h: [50, 218] },
    wave:  { e: [24, 112], h: [18, 56] },
    ears:  { e: [36, 122], h: [56, 80] },
    front: { e: [60, 186], h: [92, 190] },
    hold:  { e: [50, 186], h: [84, 172] },
    point: { e: [32, 152], h: [4, 140] },
    up:    { e: [44, 100], h: [56, 36] },
    hip:   { e: [38, 176], h: [60, 198] },
    phone: { e: [30, 170], h: [52, 92] },
    stop:  { e: [34, 140], h: [30, 92] },
    ok:    { e: [36, 140], h: [34, 96] },
    show:  { e: [30, 160], h: [14, 120] },
    chin:  { e: [40, 160], h: [78, 110] },
    lap:   { e: [52, 190], h: [78, 226] },
  };

  function armPath(side, pose, color, sleeve) {
    const p = ARM[pose] || ARM.down;
    const sx = 62, sy = 138;
    let e = p.e.slice(), h = p.h.slice(), s = [sx, sy];
    if (side === 'R') { e[0] = mirror(e[0]); h[0] = mirror(h[0]); s[0] = mirror(s[0]); }
    const pts = `${s[0]},${s[1]} ${e[0]},${e[1]} ${h[0]},${h[1]}`;
    const armColor = sleeve === 'long' ? sleeve.color || color.sleeveColor : color.skin;
    return {
      svg: `<polyline points="${pts}" fill="none" stroke="${OUT}" stroke-width="24" stroke-linecap="round" stroke-linejoin="round"/>
            <polyline points="${pts}" fill="none" stroke="${sleeve === 'long' ? color.sleeveColor : color.skin}" stroke-width="18" stroke-linecap="round" stroke-linejoin="round"/>`,
      hand: h, shoulder: s,
    };
  }

  function face(expr, o) {
    let out = '';
    const eyeY = 76;
    // olhos
    if (o.sunglasses) {
      out += `<rect x="64" y="64" width="32" height="24" rx="8" fill="#1F2A36" ${S}/><rect x="104" y="64" width="32" height="24" rx="8" fill="#1F2A36" ${S}/><line x1="96" y1="72" x2="104" y2="72" ${S}/>`;
      out += `<path d="M70 70 q8 -4 16 0" stroke="#FFFFFF" stroke-width="3" fill="none" opacity=".7"/>`;
    } else if (expr === 'happyclosed') {
      out += `<path d="M74 ${eyeY} q8 -9 16 0" fill="none" ${S}/><path d="M110 ${eyeY} q8 -9 16 0" fill="none" ${S}/>`;
    } else {
      out += `<ellipse cx="82" cy="${eyeY}" rx="5" ry="6.5" fill="${OUT}"/><ellipse cx="118" cy="${eyeY}" rx="5" ry="6.5" fill="${OUT}"/>`;
      out += `<circle cx="84" cy="${eyeY - 2}" r="1.8" fill="#fff"/><circle cx="120" cy="${eyeY - 2}" r="1.8" fill="#fff"/>`;
      if (o.glasses) out += `<circle cx="82" cy="${eyeY}" r="13" fill="none" ${S}/><circle cx="118" cy="${eyeY}" r="13" fill="none" ${S}/><line x1="95" y1="${eyeY}" x2="105" y2="${eyeY}" ${S}/>`;
    }
    // sobrancelhas
    if (expr === 'worried' || expr === 'scared') {
      out += `<path d="M70 62 L90 56" ${S} fill="none"/><path d="M110 56 L130 62" ${S} fill="none"/>`;
    } else if (expr === 'surprised') {
      out += `<path d="M72 54 q10 -6 20 0" ${S} fill="none"/><path d="M108 54 q10 -6 20 0" ${S} fill="none"/>`;
    } else if (!o.sunglasses) {
      out += `<path d="M72 58 q10 -4 20 0" ${S} fill="none"/><path d="M108 58 q10 -4 20 0" ${S} fill="none"/>`;
    }
    // nariz
    out += `<path d="M100 82 q-4 8 3 10" ${S} fill="none"/>`;
    // boca
    switch (expr) {
      case 'bigsmile':
        out += `<path d="M78 94 Q100 122 122 94 Z" fill="#C0392B" ${S}/><path d="M84 95 Q100 103 116 95 Z" fill="#FFFFFF"/>`;
        break;
      case 'open':
        out += `<ellipse cx="100" cy="103" rx="14" ry="15" fill="#C0392B" ${S}/><rect x="88" y="89" width="24" height="7" rx="3" fill="#FFFFFF"/>`;
        break;
      case 'worried':
        out += `<path d="M84 104 Q100 92 116 104" fill="none" ${S}/>`;
        break;
      case 'scared':
        out += `<path d="M82 100 Q100 96 118 100 Q100 116 82 100 Z" fill="#C0392B" ${S}/>`;
        break;
      case 'neutral':
        out += `<path d="M88 100 L112 100" ${S}/>`;
        break;
      case 'surprised':
        out += `<ellipse cx="100" cy="102" rx="8" ry="10" fill="#C0392B" ${S}/>`;
        break;
      default: // happy / happyclosed
        out += `<path d="M80 94 Q100 114 120 94" fill="none" ${S}/>`;
    }
    if (o.blush) out += `<circle cx="66" cy="92" r="6" fill="#F5A3A3" opacity=".7"/><circle cx="134" cy="92" r="6" fill="#F5A3A3" opacity=".7"/>`;
    return out;
  }

  function hairSvg(style, color, phase) {
    // phase 'back' = atrás da cabeça, 'front' = em cima
    if (phase === 'back') {
      if (style === 'long') return `<path d="M52 62 C40 110 42 150 56 178 L144 178 C158 150 160 110 148 62 Z" fill="${color}" ${S}/>`;
      if (style === 'curlylong') {
        let s = '';
        for (let i = 0; i < 7; i++) s += `<circle cx="${48 + i * 1.2}" cy="${70 + i * 15}" r="15" fill="${color}" ${S}/><circle cx="${152 - i * 1.2}" cy="${70 + i * 15}" r="15" fill="${color}" ${S}/>`;
        return s;
      }
      return '';
    }
    switch (style) {
      case 'curly': case 'curlylong': {
        let s = `<path d="M50 72 C48 26 152 26 150 72 C140 54 120 44 100 46 C80 44 60 54 50 72 Z" fill="${color}" ${S}/>`;
        for (let i = 0; i < 9; i++) {
          const t = Math.PI + (i / 8) * Math.PI;
          s += `<circle cx="${100 + Math.cos(t) * 50}" cy="${66 + Math.sin(t) * 44}" r="13" fill="${color}" ${S}/>`;
        }
        return s;
      }
      case 'bun':
        return `<circle cx="100" cy="26" r="16" fill="${color}" ${S}/><path d="M50 72 C48 26 152 26 150 72 C140 50 120 40 100 42 C80 40 60 50 50 72 Z" fill="${color}" ${S}/>`;
      case 'long':
        return `<path d="M50 72 C48 24 152 24 150 72 C142 46 124 38 108 48 C92 56 70 50 50 72 Z" fill="${color}" ${S}/>`;
      case 'bald':
        return '';
      case 'side':
        return `<path d="M50 70 C46 24 150 18 150 68 C130 44 110 50 86 56 C70 60 58 64 50 70 Z" fill="${color}" ${S}/>`;
      default: // cap (curto)
        return `<path d="M50 70 C48 22 152 22 150 70 C140 48 120 36 100 40 C80 36 60 48 50 70 Z" fill="${color}" ${S}/>`;
    }
  }

  const ITEMS = {}; // objetos seguráveis (definidos abaixo)

  function person(o = {}) {
    const c = {
      skin: o.skin || '#F7D6B9', hair: o.hair || '#5A3A1C', hairStyle: o.hairStyle || 'cap',
      shirt: o.shirt || '#F7C21B', pants: o.pants || '#6B6B6B', shoes: o.shoes || '#333333',
      coat: o.coat || null, sleeve: o.sleeve || 'short', expr: o.expr || 'happy',
      armL: o.armL || 'down', armR: o.armR || 'down', sit: !!o.sit,
      headphones: !!o.headphones, sunglasses: !!o.sunglasses, glasses: !!o.glasses, mask: !!o.mask,
      holdL: o.holdL || null, holdR: o.holdR || null, blush: !!o.blush, skirt: !!o.skirt,
      sleeveColor: o.coat || o.shirt || '#F7C21B', name: o.name || '',
      maskUp: !!o.maskUp, gloves: !!o.gloves, bib: !!o.bib,
    };
    const handColor = c.gloves ? '#A8D8EA' : c.skin;
    let out = '';
    // cabelo (parte de trás)
    out += hairSvg(c.hairStyle, c.hair, 'back');
    // pernas
    if (c.sit) {
      out += `<rect x="66" y="200" width="32" height="48" rx="10" fill="${c.pants}" ${S}/><rect x="102" y="200" width="32" height="48" rx="10" fill="${c.pants}" ${S}/>`;
      out += `<rect x="70" y="236" width="26" height="58" rx="10" fill="${c.pants}" ${S}/><rect x="104" y="236" width="26" height="58" rx="10" fill="${c.pants}" ${S}/>`;
      out += `<ellipse cx="83" cy="296" rx="18" ry="8" fill="${c.shoes}" ${S}/><ellipse cx="117" cy="296" rx="18" ry="8" fill="${c.shoes}" ${S}/>`;
    } else {
      if (c.skirt) {
        out += `<path d="M62 205 L138 205 L150 262 L50 262 Z" fill="${c.pants}" ${S}/>`;
        out += `<rect x="76" y="258" width="18" height="38" rx="8" fill="${c.skin}" ${S}/><rect x="106" y="258" width="18" height="38" rx="8" fill="${c.skin}" ${S}/>`;
      } else {
        out += `<rect x="70" y="205" width="28" height="92" rx="10" fill="${c.pants}" ${S}/><rect x="102" y="205" width="28" height="92" rx="10" fill="${c.pants}" ${S}/>`;
      }
      out += `<ellipse cx="84" cy="298" rx="19" ry="8" fill="${c.shoes}" ${S}/><ellipse cx="116" cy="298" rx="19" ry="8" fill="${c.shoes}" ${S}/>`;
    }
    // pescoço
    out += `<rect x="88" y="104" width="24" height="26" rx="6" fill="${c.skin}" ${S}/>`;
    // tronco
    out += `<path d="M58 132 Q58 120 72 120 L128 120 Q142 120 142 132 L142 212 L58 212 Z" fill="${c.shirt}" ${S}/>`;
    if (c.coat) {
      out += `<path d="M48 128 L84 120 L100 150 L116 120 L152 128 L158 226 L42 226 Z" fill="${c.coat}" ${S}/>`;
      out += `<path d="M84 120 L100 150 L116 120 L112 118 L100 140 L88 118 Z" fill="${c.shirt}" ${S}/>`;
      out += `<circle cx="100" cy="170" r="3" fill="${OUT}"/><circle cx="100" cy="190" r="3" fill="${OUT}"/>`;
      out += `<rect x="118" y="160" width="22" height="20" rx="3" fill="${c.coat}" ${S}/>`;
    }
    if (c.bib) {
      out += `<path d="M64 126 Q100 140 136 126 L138 196 Q100 204 62 196 Z" fill="#CFEFF7" ${S}/><path d="M84 118 Q100 130 116 118" fill="none" ${S}/>`;
    }
    // braços
    const L = armPath('L', c.armL, c, c.sleeve);
    const R = armPath('R', c.armR, c, c.sleeve);
    out += L.svg + R.svg;
    if (c.sleeve === 'short') {
      out += `<circle cx="62" cy="140" r="17" fill="${c.sleeveColor}" ${S}/><circle cx="138" cy="140" r="17" fill="${c.sleeveColor}" ${S}/>`;
    }
    // mãos
    const hand = (h, pose) => {
      if (pose === 'stop' || pose === 'ok') {
        return `<path d="M${h[0] - 12} ${h[1] + 6} L${h[0] - 12} ${h[1] - 14} L${h[0] - 4} ${h[1] - 20} L${h[0] + 4} ${h[1] - 22} L${h[0] + 12} ${h[1] - 16} L${h[0] + 14} ${h[1] + 2} Q${h[0]} ${h[1] + 14} ${h[0] - 12} ${h[1] + 6} Z" fill="${handColor}" ${S}/>`;
      }
      return `<circle cx="${h[0]}" cy="${h[1]}" r="11" fill="${handColor}" ${S}/>`;
    };
    const lateL = c.armL === 'ears', lateR = c.armR === 'ears';
    if (!lateL) out += hand(L.hand, c.armL);
    if (!lateR) out += hand(R.hand, c.armR);
    // objetos nas mãos
    if (c.holdL && ITEMS[c.holdL]) out += at(ITEMS[c.holdL](), L.hand[0], L.hand[1]);
    if (c.holdR && ITEMS[c.holdR]) out += at(ITEMS[c.holdR](), R.hand[0], R.hand[1]);
    // orelhas e cabeça
    out += `<circle cx="52" cy="80" r="9" fill="${c.skin}" ${S}/><circle cx="148" cy="80" r="9" fill="${c.skin}" ${S}/>`;
    out += `<ellipse cx="100" cy="74" rx="50" ry="47" fill="${c.skin}" ${S}/>`;
    out += face(c.expr, c);
    out += hairSvg(c.hairStyle, c.hair, 'front');
    if (lateL) out += hand(L.hand, c.armL);
    if (lateR) out += hand(R.hand, c.armR);
    if (c.maskUp) {
      out += `<path d="M64 84 Q100 78 136 84 L132 112 Q100 124 68 112 Z" fill="#A8D8EA" ${S}/><line x1="64" y1="86" x2="52" y2="76" ${S}/><line x1="136" y1="86" x2="148" y2="76" ${S}/><line x1="68" y1="110" x2="54" y2="92" ${S}/><line x1="132" y1="110" x2="146" y2="92" ${S}/>`;
    } else if (c.mask) {
      out += `<rect x="76" y="108" width="48" height="22" rx="6" fill="#A8D8EA" ${S}/><line x1="76" y1="114" x2="54" y2="88" ${S}/><line x1="124" y1="114" x2="146" y2="88" ${S}/>`;
    }
    if (c.headphones) {
      out += `<path d="M44 70 C44 14 156 14 156 70" fill="none" stroke="${OUT}" stroke-width="12" stroke-linecap="round"/><path d="M44 70 C44 14 156 14 156 70" fill="none" stroke="#E74C3C" stroke-width="6" stroke-linecap="round"/>`;
      out += `<rect x="30" y="60" width="26" height="38" rx="10" fill="#E74C3C" ${S}/><rect x="144" y="60" width="26" height="38" rx="10" fill="#E74C3C" ${S}/>`;
    }
    return out;
  }

  // personagens prontos -------------------------------------------
  const KID = (o = {}) => person(Object.assign({ skin: '#F7D6B9', hair: '#5A3A1C', hairStyle: 'cap', shirt: '#F7C21B', pants: '#6B6B6B', blush: true }, o));
  const DENTIST = (o = {}) => person(Object.assign({ skin: '#C58C5A', hair: '#1C1C1C', hairStyle: 'curly', shirt: '#2E9E8F', pants: '#2C3E50', coat: '#FFFFFF', sleeve: 'long', shoes: '#FFFFFF', mask: true }, o));
  const MOM = (o = {}) => person(Object.assign({ skin: '#F2C9A6', hair: '#7A3F1E', hairStyle: 'long', shirt: '#3FB8C8', pants: '#5B5F97', skirt: false }, o));
  const RECEP = (o = {}) => person(Object.assign({ skin: '#8D5B3A', hair: '#1C1C1C', hairStyle: 'bun', shirt: '#9B59B6', pants: '#2C3E50', glasses: true }, o));
  const ASSIST = (o = {}) => person(Object.assign({ skin: '#F7D6B9', hair: '#E67E22', hairStyle: 'side', shirt: '#5DADE2', pants: '#2C3E50', coat: '#DDF3FF', sleeve: 'long' }, o));

  // colocar um personagem com os pés em (x,y) e escala s
  const put = (svg, x, y, s = 1, flip = false) =>
    `<g transform="translate(${x} ${y}) scale(${flip ? -s : s} ${s}) translate(-100 -300)">${svg}</g>`;

  // ------------------------------------------------------------
  // OBJETOS SEGURÁVEIS (origem = centro da mão)
  // ------------------------------------------------------------
  ITEMS.teddy = () => `<g transform="translate(0 6)">
    <circle cx="-14" cy="-12" r="8" fill="#A0522D" ${S}/><circle cx="14" cy="-12" r="8" fill="#A0522D" ${S}/>
    <ellipse cx="0" cy="16" rx="18" ry="16" fill="#A0522D" ${S}/><circle cx="0" cy="-4" r="18" fill="#A0522D" ${S}/>
    <ellipse cx="0" cy="2" rx="8" ry="6" fill="#D2A679"/><circle cx="-6" cy="-8" r="2.2" fill="${OUT}"/><circle cx="6" cy="-8" r="2.2" fill="${OUT}"/><circle cx="0" cy="0" r="2.5" fill="${OUT}"/></g>`;
  ITEMS.gift = () => `<g transform="translate(0 -4)">
    <rect x="-22" y="-10" width="44" height="34" rx="4" fill="#E74C3C" ${S}/><rect x="-24" y="-18" width="48" height="12" rx="3" fill="#C0392B" ${S}/>
    <rect x="-5" y="-18" width="10" height="42" fill="#F7C21B" ${S}/><rect x="-24" y="-16" width="48" height="8" fill="#F7C21B" stroke="none"/>
    <path d="M0 -18 C-14 -34 -22 -22 -4 -18 Z" fill="#F7C21B" ${S}/><path d="M0 -18 C14 -34 22 -22 4 -18 Z" fill="#F7C21B" ${S}/></g>`;
  ITEMS.toothbrush = () => `<g transform="rotate(-30)"><rect x="-6" y="-44" width="12" height="60" rx="5" fill="#3498DB" ${S}/><rect x="-7" y="-58" width="14" height="18" rx="3" fill="#FFFFFF" ${S}/><line x1="-3" y1="-56" x2="-3" y2="-42" stroke="#95A5A6" stroke-width="2"/><line x1="3" y1="-56" x2="3" y2="-42" stroke="#95A5A6" stroke-width="2"/></g>`;
  ITEMS.mirror = () => `<g transform="rotate(-20)"><rect x="-4" y="-6" width="8" height="48" rx="3" fill="#95A5A6" ${S}/><circle cx="0" cy="-18" r="13" fill="#D6EAF8" ${S}/><circle cx="0" cy="-18" r="7" fill="#FFFFFF" opacity=".8"/></g>`;
  ITEMS.phone = () => `<g transform="rotate(-15)"><rect x="-10" y="-26" width="20" height="40" rx="5" fill="#2C3E50" ${S}/><rect x="-7" y="-22" width="14" height="28" rx="2" fill="#5DADE2"/></g>`;
  ITEMS.tablet = () => `<g><rect x="-34" y="-24" width="68" height="48" rx="5" fill="#2C3E50" ${S}/><rect x="-29" y="-19" width="58" height="38" rx="2" fill="#AED6F1"/><polygon points="-6,-10 10,0 -6,10" fill="#FFFFFF" ${S}/></g>`;
  ITEMS.pen = () => `<g transform="rotate(35)"><rect x="-4" y="-28" width="8" height="44" rx="3" fill="#F39C12" ${S}/><polygon points="-4,16 4,16 0,26" fill="#F7D6B9" ${S}/></g>`;
  ITEMS.card = () => `<g transform="rotate(-8)"><rect x="-30" y="-20" width="60" height="42" rx="4" fill="#FFFFFF" ${S}/><rect x="-24" y="-13" width="12" height="12" rx="2" fill="#F7C21B"/><rect x="-8" y="-13" width="12" height="12" rx="2" fill="#5DADE2"/><rect x="8" y="-13" width="12" height="12" rx="2" fill="#58D68D"/><rect x="-24" y="4" width="44" height="4" rx="2" fill="#BDC3C7"/><rect x="-24" y="12" width="30" height="4" rx="2" fill="#BDC3C7"/></g>`;
  ITEMS.suction = () => `<g><path d="M0 8 L0 -34 Q0 -52 16 -52 L30 -52" fill="none" stroke="${OUT}" stroke-width="12" stroke-linecap="round"/><path d="M0 8 L0 -34 Q0 -52 16 -52 L30 -52" fill="none" stroke="#BDC3C7" stroke-width="6" stroke-linecap="round"/><rect x="26" y="-58" width="18" height="12" rx="3" fill="#F7C21B" ${S}/></g>`;
  ITEMS.spray = () => `<g transform="rotate(-25)"><rect x="-6" y="-50" width="12" height="62" rx="5" fill="#95A5A6" ${S}/><rect x="-8" y="-62" width="16" height="16" rx="4" fill="#3498DB" ${S}/><circle cx="-14" cy="-74" r="3.5" fill="#AED6F1" ${S}/><circle cx="2" cy="-80" r="3.5" fill="#AED6F1" ${S}/><circle cx="16" cy="-72" r="3.5" fill="#AED6F1" ${S}/></g>`;
  ITEMS.polisher = () => `<g transform="rotate(-25)"><rect x="-6" y="-46" width="12" height="60" rx="5" fill="#95A5A6" ${S}/><rect x="-11" y="-60" width="22" height="16" rx="4" fill="#E67E22" ${S}/><ellipse cx="0" cy="-62" rx="9" ry="4" fill="#F7C21B" ${S}/></g>`;
  ITEMS.cup = () => `<g><path d="M-12 -14 L12 -14 L9 14 L-9 14 Z" fill="#5DADE2" ${S}/><ellipse cx="0" cy="-14" rx="12" ry="4" fill="#AED6F1" ${S}/></g>`;
  ITEMS.sunglassesItem = () => `<g transform="scale(.8)"><rect x="-30" y="-10" width="26" height="20" rx="8" fill="#1F2A36" ${S}/><rect x="4" y="-10" width="26" height="20" rx="8" fill="#1F2A36" ${S}/><line x1="-4" y1="-4" x2="4" y2="-4" ${S}/></g>`;
  ITEMS.clipboard = () => `<g transform="rotate(8)"><rect x="-24" y="-30" width="48" height="60" rx="4" fill="#A0522D" ${S}/><rect x="-19" y="-24" width="38" height="50" fill="#FFFFFF" ${S}/><rect x="-10" y="-34" width="20" height="10" rx="3" fill="#7F8C8D" ${S}/><line x1="-13" y1="-10" x2="13" y2="-10" ${S}/><line x1="-13" y1="0" x2="13" y2="0" ${S}/><line x1="-13" y1="10" x2="6" y2="10" ${S}/></g>`;

  // ------------------------------------------------------------
  // CENÁRIO
  // ------------------------------------------------------------
  function tiles(w, h, color = '#6CBF4A', line = '#FFFFFF', size = 46) {
    let s = `<rect x="0" y="0" width="${w}" height="${h}" fill="${color}"/>`;
    for (let x = size; x < w; x += size) s += `<line x1="${x}" y1="0" x2="${x}" y2="${h}" stroke="${line}" stroke-width="3" opacity=".75"/>`;
    for (let y = size; y < h; y += size) s += `<line x1="0" y1="${y}" x2="${w}" y2="${y}" stroke="${line}" stroke-width="3" opacity=".75"/>`;
    return s;
  }
  function plainWall(w, h, color) { return `<rect x="0" y="0" width="${w}" height="${h}" fill="${color}"/>`; }
  function floor(w, y, h, color = '#F2E394', line = true) {
    return `<rect x="0" y="${y}" width="${w}" height="${h}" fill="${color}"/>${line ? `<line x1="0" y1="${y}" x2="${w}" y2="${y}" ${S}/>` : ''}`;
  }
  function window_(x, y, w, h) {
    return `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="4" fill="#AED6F1" ${S}/><line x1="${x + w / 2}" y1="${y}" x2="${x + w / 2}" y2="${y + h}" ${S}/><line x1="${x}" y1="${y + h / 2}" x2="${x + w}" y2="${y + h / 2}" ${S}/>
      <circle cx="${x + w * 0.3}" cy="${y + h * 0.3}" r="${h * 0.12}" fill="#FFFFFF" opacity=".9"/><ellipse cx="${x + w * 0.6}" cy="${y + h * 0.35}" rx="${h * 0.2}" ry="${h * 0.1}" fill="#FFFFFF" opacity=".9"/>`;
  }
  function door(x, y, w = 70, h = 150, color = '#E67E22') {
    return `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="4" fill="${color}" ${S}/><rect x="${x + 10}" y="${y + 12}" width="${w - 20}" height="${h * 0.38}" rx="3" fill="none" ${S} opacity=".6"/><rect x="${x + 10}" y="${y + h * 0.55}" width="${w - 20}" height="${h * 0.36}" rx="3" fill="none" ${S} opacity=".6"/><circle cx="${x + w - 14}" cy="${y + h / 2}" r="5" fill="#F7C21B" ${S}/>`;
  }
  function plant(x, y, s = 1) {
    return at(`<path d="M-18 0 L18 0 L14 30 L-14 30 Z" fill="#C0392B" ${S}/>
      <ellipse cx="-12" cy="-26" rx="10" ry="20" transform="rotate(-30 -12 -26)" fill="#58D68D" ${S}/><ellipse cx="12" cy="-26" rx="10" ry="20" transform="rotate(30 12 -26)" fill="#58D68D" ${S}/><ellipse cx="0" cy="-34" rx="10" ry="24" fill="#2ECC71" ${S}/>`, x, y, s);
  }
  function waitingChairs(x, y, n = 3, color = '#5DADE2') {
    let s = '';
    for (let i = 0; i < n; i++) {
      const cx = x + i * 78;
      s += `<rect x="${cx}" y="${y - 70}" width="64" height="44" rx="8" fill="${color}" ${S}/><rect x="${cx}" y="${y - 30}" width="64" height="18" rx="6" fill="${color}" ${S}/><rect x="${cx + 6}" y="${y - 12}" width="8" height="30" fill="#7F8C8D" ${S}/><rect x="${cx + 50}" y="${y - 12}" width="8" height="30" fill="#7F8C8D" ${S}/>`;
    }
    return s;
  }
  function deskReception(x, y, w = 200, h = 90, monitor = true) {
    return `<rect x="${x}" y="${y - h}" width="${w}" height="${h}" rx="6" fill="#D7A86E" ${S}/><rect x="${x - 6}" y="${y - h - 10}" width="${w + 12}" height="14" rx="4" fill="#A0522D" ${S}/>
      ${monitor ? `<rect x="${x + w - 80}" y="${y - h - 60}" width="56" height="42" rx="4" fill="#2C3E50" ${S}/><rect x="${x + w - 75}" y="${y - h - 55}" width="46" height="32" fill="#AED6F1"/><rect x="${x + w - 60}" y="${y - h - 18}" width="16" height="10" fill="#2C3E50" ${S}/>` : ''}`;
  }
  function dentalChair(color = '#2E9E8F', light = '#49B9A9') {
    return `<ellipse cx="150" cy="252" rx="78" ry="12" fill="#7F8C8D" ${S}/><rect x="122" y="206" width="56" height="46" fill="#95A5A6" ${S}/>
      <rect x="40" y="186" width="60" height="22" rx="8" fill="${light}" ${S}/>
      <rect x="70" y="150" width="160" height="56" rx="12" fill="${color}" ${S}/>
      <rect x="84" y="20" width="132" height="140" rx="16" fill="${light}" ${S}/>
      <rect x="112" y="0" width="76" height="40" rx="12" fill="${color}" ${S}/>
      <rect x="52" y="138" width="30" height="62" rx="10" fill="${color}" ${S}/><rect x="218" y="138" width="30" height="62" rx="10" fill="${color}" ${S}/>`;
  }
  function lamp(x, y, on = true) {
    return `<g transform="translate(${x} ${y})"><rect x="-6" y="-80" width="12" height="60" fill="#95A5A6" ${S}/><line x1="0" y1="-24" x2="40" y2="4" stroke="${OUT}" stroke-width="12" stroke-linecap="round"/><line x1="0" y1="-24" x2="40" y2="4" stroke="#BDC3C7" stroke-width="7" stroke-linecap="round"/>
      <ellipse cx="46" cy="18" rx="42" ry="16" transform="rotate(-18 46 18)" fill="#ECF0F1" ${S}/><ellipse cx="46" cy="18" rx="30" ry="9" transform="rotate(-18 46 18)" fill="${on ? '#FFF6B0' : '#D5D8DC'}" ${S}/>
      ${on ? `<polygon points="10,26 82,10 110,110 -20,120" fill="#FFF6B0" opacity=".45"/>` : ''}</g>`;
  }
  function tray(x, y) {
    return `<g transform="translate(${x} ${y})"><rect x="0" y="-70" width="90" height="70" rx="6" fill="#ECF0F1" ${S}/><rect x="10" y="-60" width="70" height="20" rx="3" fill="#BDC3C7" ${S}/><rect x="10" y="-34" width="70" height="20" rx="3" fill="#BDC3C7" ${S}/><circle cx="18" cy="-50" r="3" fill="${OUT}"/><circle cx="18" cy="-24" r="3" fill="${OUT}"/>
      <rect x="-8" y="-84" width="106" height="14" rx="3" fill="#95A5A6" ${S}/><rect x="10" y="-96" width="6" height="14" fill="#7F8C8D" ${S}/><rect x="24" y="-100" width="6" height="18" fill="#3498DB" ${S}/><circle cx="60" cy="-94" r="7" fill="#D6EAF8" ${S}/><rect x="58" y="-88" width="4" height="12" fill="#95A5A6" ${S}/></g>`;
  }
  let clipN = 0;
  function tv(x, y, w, h, inner) {
    const id = 'tvclip' + (++clipN);
    return `<g transform="translate(${x} ${y})"><defs><clipPath id="${id}"><rect x="8" y="8" width="${w - 16}" height="${h - 16}" rx="3"/></clipPath></defs><rect x="0" y="0" width="${w}" height="${h}" rx="8" fill="#2C3E50" ${S}/><rect x="8" y="8" width="${w - 16}" height="${h - 16}" rx="3" fill="#AED6F1" ${S}/>
      <g clip-path="url(#${id})" transform="translate(8 8)">${inner}</g>
      <rect x="${w / 2 - 10}" y="${h}" width="20" height="18" fill="#2C3E50" ${S}/><rect x="${w / 2 - 40}" y="${h + 16}" width="80" height="8" rx="3" fill="#2C3E50" ${S}/></g>`;
  }
  function sofa(x, y, w = 200, color = '#E8A0BF') {
    return `<g transform="translate(${x} ${y})"><rect x="0" y="-80" width="${w}" height="44" rx="10" fill="${color}" ${S}/><rect x="-10" y="-50" width="${w + 20}" height="40" rx="10" fill="${color}" ${S}/><rect x="-16" y="-60" width="26" height="50" rx="10" fill="${color}" ${S}/><rect x="${w - 10}" y="-60" width="26" height="50" rx="10" fill="${color}" ${S}/></g>`;
  }
  function toothMascot(x, y, s = 1, expr = 'happy') {
    return at(`<path d="M-40 -40 C-40 -70 40 -70 40 -40 C44 -10 36 20 28 44 C22 58 10 58 6 42 L0 20 L-6 42 C-10 58 -22 58 -28 44 C-36 20 -44 -10 -40 -40 Z" fill="#FFFFFF" ${S}/>
      <circle cx="-14" cy="-28" r="4" fill="${OUT}"/><circle cx="14" cy="-28" r="4" fill="${OUT}"/>
      ${expr === 'happy' ? `<path d="M-14 -12 Q0 2 14 -12" fill="none" ${S}/>` : `<path d="M-12 -6 Q0 -16 12 -6" fill="none" ${S}/>`}
      <circle cx="-24" cy="-14" r="5" fill="#F5A3A3" opacity=".8"/><circle cx="24" cy="-14" r="5" fill="#F5A3A3" opacity=".8"/>
      <path d="M-30 -52 q8 -6 16 -2" stroke="#FFFFFF" stroke-width="3" fill="none"/>`, x, y, s);
  }
  function star(x, y, r, color = '#F7C21B') {
    let pts = '';
    for (let i = 0; i < 10; i++) {
      const rr = i % 2 ? r * 0.45 : r;
      const a = -Math.PI / 2 + i * Math.PI / 5;
      pts += `${x + Math.cos(a) * rr},${y + Math.sin(a) * rr} `;
    }
    return `<polygon points="${pts}" fill="${color}" ${S}/>`;
  }
  function sparkles(x, y) {
    return `${star(x, y, 10)}${star(x + 26, y - 18, 6)}${star(x - 22, y - 14, 7)}`;
  }
  function wallSign(x, y, text, w = 120, h = 36, fill = '#FFFFFF') {
    return `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="6" fill="${fill}" ${S}/>${htmlText(x, y, w, h, text, 12, 800, OUT, 'center', 'Baloo 2')}`;
  }
  function zzz(x, y) { return htmlText(x, y, 60, 30, 'zzz', 16, 800, '#7F8C8D'); }
  function noteMusic(x, y) { return `<path d="M${x} ${y} v-26 l14 -4 v24" fill="none" ${S}/><circle cx="${x - 5}" cy="${y}" r="5" fill="${OUT}"/><circle cx="${x + 9}" cy="${y - 6}" r="5" fill="${OUT}"/>`; }

  // ------------------------------------------------------------
  // CENA — wrapper SVG
  // ------------------------------------------------------------
  function scene(w, h, inner, extraClass = '', par = 'xMidYMid meet') {
    return `<svg class="ill-svg ${extraClass}" viewBox="0 0 ${w} ${h}" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="${par}" style="width:100%;height:100%;display:block">${inner}</svg>`;
  }

  // ------------------------------------------------------------
  // ÍCONES (viewBox 0 0 64 64)
  // ------------------------------------------------------------
  const ICON = {
    phone: () => `<rect x="18" y="6" width="28" height="52" rx="6" fill="#2C3E50" ${S}/><rect x="22" y="12" width="20" height="36" rx="2" fill="#5DADE2"/><circle cx="32" cy="53" r="2.5" fill="#fff"/>`,
    video: () => `<rect x="6" y="18" width="38" height="30" rx="5" fill="#E74C3C" ${S}/><polygon points="44,26 58,18 58,48 44,40" fill="#E74C3C" ${S}/><polygon points="20,26 32,33 20,40" fill="#fff"/>`,
    calendar: () => `<rect x="8" y="12" width="48" height="44" rx="5" fill="#fff" ${S}/><rect x="8" y="12" width="48" height="14" rx="5" fill="#E74C3C" ${S}/><line x1="20" y1="6" x2="20" y2="18" ${S}/><line x1="44" y1="6" x2="44" y2="18" ${S}/><rect x="16" y="32" width="8" height="8" fill="#5DADE2"/><rect x="28" y="32" width="8" height="8" fill="#BDC3C7"/><rect x="40" y="32" width="8" height="8" fill="#BDC3C7"/><rect x="16" y="44" width="8" height="8" fill="#BDC3C7"/>`,
    clock: () => `<circle cx="32" cy="32" r="26" fill="#fff" ${S}/><line x1="32" y1="32" x2="32" y2="14" ${S}/><line x1="32" y1="32" x2="44" y2="38" ${S}/><circle cx="32" cy="32" r="3" fill="${OUT}"/>`,
    headphones: () => `<path d="M12 40 C12 10 52 10 52 40" fill="none" stroke="${OUT}" stroke-width="8" stroke-linecap="round"/><path d="M12 40 C12 10 52 10 52 40" fill="none" stroke="#E74C3C" stroke-width="4" stroke-linecap="round"/><rect x="6" y="34" width="14" height="22" rx="5" fill="#E74C3C" ${S}/><rect x="44" y="34" width="14" height="22" rx="5" fill="#E74C3C" ${S}/>`,
    sunglasses: () => `<rect x="4" y="24" width="24" height="18" rx="7" fill="#1F2A36" ${S}/><rect x="36" y="24" width="24" height="18" rx="7" fill="#1F2A36" ${S}/><line x1="28" y1="30" x2="36" y2="30" ${S}/>`,
    lampdim: () => `<path d="M32 8 C18 8 12 20 12 28 C12 36 20 40 22 46 L42 46 C44 40 52 36 52 28 C52 20 46 8 32 8 Z" fill="#D5D8DC" ${S}/><rect x="24" y="46" width="16" height="8" rx="2" fill="#7F8C8D" ${S}/><line x1="10" y1="12" x2="54" y2="52" stroke="#E74C3C" stroke-width="5" stroke-linecap="round"/>`,
    mirror: () => `<rect x="28" y="26" width="8" height="34" rx="3" fill="#95A5A6" ${S}/><circle cx="32" cy="18" r="13" fill="#D6EAF8" ${S}/><circle cx="32" cy="18" r="6" fill="#fff" opacity=".9"/>`,
    stop: () => `<path d="M18 56 L18 24 Q18 18 24 18 Q30 18 30 24 L30 10 Q30 4 36 4 Q42 4 42 10 L42 26 L48 20 Q54 16 56 24 L56 44 Q56 58 42 58 Z" fill="#F7D6B9" ${S}/><line x1="30" y1="24" x2="30" y2="36" ${S}/><line x1="42" y1="26" x2="42" y2="36" ${S}/>`,
    gift: () => `<rect x="10" y="26" width="44" height="32" rx="3" fill="#E74C3C" ${S}/><rect x="8" y="18" width="48" height="12" rx="3" fill="#C0392B" ${S}/><rect x="28" y="18" width="8" height="40" fill="#F7C21B" ${S}/><path d="M32 18 C20 2 10 14 28 18 Z" fill="#F7C21B" ${S}/><path d="M32 18 C44 2 54 14 36 18 Z" fill="#F7C21B" ${S}/>`,
    toothbrush: () => `<g transform="rotate(-35 32 32)"><rect x="27" y="14" width="10" height="46" rx="4" fill="#3498DB" ${S}/><rect x="26" y="4" width="12" height="14" rx="2" fill="#fff" ${S}/></g>`,
    notes: () => `<rect x="12" y="8" width="40" height="50" rx="4" fill="#fff" ${S}/><rect x="22" y="4" width="20" height="8" rx="3" fill="#7F8C8D" ${S}/><line x1="20" y1="24" x2="44" y2="24" ${S}/><line x1="20" y1="34" x2="44" y2="34" ${S}/><line x1="20" y1="44" x2="36" y2="44" ${S}/>`,
    tooth: () => `<path d="M14 22 C14 6 50 6 50 22 C52 34 48 44 44 54 C42 60 36 60 34 52 L32 42 L30 52 C28 60 22 60 20 54 C16 44 12 34 14 22 Z" fill="#fff" ${S}/><circle cx="26" cy="26" r="2.5" fill="${OUT}"/><circle cx="38" cy="26" r="2.5" fill="${OUT}"/><path d="M26 34 Q32 40 38 34" fill="none" ${S}/>`,
    thumbs: () => `<path d="M8 30 L22 30 L22 58 L8 58 Z" fill="#5DADE2" ${S}/><path d="M22 32 L34 10 Q40 6 42 14 L40 28 L54 28 Q60 28 58 36 L52 54 Q50 58 44 58 L22 58 Z" fill="#F7D6B9" ${S}/>`,
    mute: () => `<polygon points="8,24 20,24 34,12 34,52 20,40 8,40" fill="#7F8C8D" ${S}/><line x1="42" y1="24" x2="56" y2="40" stroke="#E74C3C" stroke-width="5" stroke-linecap="round"/><line x1="56" y1="24" x2="42" y2="40" stroke="#E74C3C" stroke-width="5" stroke-linecap="round"/>`,
    photo: () => `<rect x="6" y="18" width="52" height="38" rx="5" fill="#2C3E50" ${S}/><rect x="22" y="10" width="20" height="10" rx="3" fill="#2C3E50" ${S}/><circle cx="32" cy="37" r="11" fill="#5DADE2" ${S}/><circle cx="32" cy="37" r="5" fill="#2C3E50"/>`,
    tablet: () => `<rect x="8" y="12" width="48" height="40" rx="5" fill="#2C3E50" ${S}/><rect x="13" y="17" width="38" height="30" rx="2" fill="#AED6F1"/><polygon points="28,24 40,32 28,40" fill="#fff" ${S}/>`,
    door: () => `<rect x="16" y="6" width="32" height="52" rx="3" fill="#E67E22" ${S}/><circle cx="40" cy="34" r="3" fill="#F7C21B" ${S}/><line x1="8" y1="58" x2="56" y2="58" ${S}/>`,
    chair: () => `<rect x="14" y="8" width="24" height="30" rx="6" fill="#49B9A9" ${S}/><rect x="10" y="34" width="44" height="14" rx="5" fill="#2E9E8F" ${S}/><rect x="28" y="48" width="12" height="10" fill="#95A5A6" ${S}/>`,
    family: () => `<circle cx="20" cy="18" r="9" fill="#F2C9A6" ${S}/><rect x="9" y="28" width="22" height="26" rx="8" fill="#3FB8C8" ${S}/><circle cx="46" cy="28" r="8" fill="#F7D6B9" ${S}/><rect x="37" y="37" width="18" height="20" rx="7" fill="#F7C21B" ${S}/>`,
    heart: () => `<path d="M32 56 C8 40 4 24 14 14 C22 8 30 12 32 20 C34 12 42 8 50 14 C60 24 56 40 32 56 Z" fill="#E74C3C" ${S}/>`,
    smell: () => `<path d="M20 50 C14 40 26 36 20 26 C14 16 26 12 20 4" fill="none" ${S}/><path d="M34 50 C28 40 40 36 34 26 C28 16 40 12 34 4" fill="none" ${S}/><line x1="8" y1="8" x2="56" y2="56" stroke="#E74C3C" stroke-width="5" stroke-linecap="round"/>`,
    timer: () => `<path d="M16 6 H48 V14 C48 24 38 28 36 32 C38 36 48 40 48 50 V58 H16 V50 C16 40 26 36 28 32 C26 28 16 24 16 14 Z" fill="#fff" ${S}/><path d="M22 52 H42 L32 40 Z" fill="#F7C21B"/>`,
    talk: () => `<path d="M8 12 H48 Q56 12 56 20 V36 Q56 44 48 44 H28 L14 56 V44 H8 Z" fill="#fff" ${S}/><circle cx="22" cy="28" r="3" fill="${OUT}"/><circle cx="32" cy="28" r="3" fill="${OUT}"/><circle cx="42" cy="28" r="3" fill="${OUT}"/>`,
    home: () => `<path d="M8 32 L32 8 L56 32" fill="none" ${S}/><rect x="14" y="30" width="36" height="28" fill="#F7C21B" ${S}/><rect x="27" y="40" width="10" height="18" fill="#A0522D" ${S}/>`,
    pause: () => `<circle cx="32" cy="32" r="26" fill="#58D68D" ${S}/><rect x="20" y="18" width="8" height="28" rx="2" fill="#fff" ${S}/><rect x="36" y="18" width="8" height="28" rx="2" fill="#fff" ${S}/>`,
    check: () => `<circle cx="32" cy="32" r="26" fill="#58D68D" ${S}/><path d="M18 33 L28 43 L46 22" fill="none" stroke="#fff" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>`,
    warn: () => `<path d="M32 6 L60 56 H4 Z" fill="#F7C21B" ${S}/><rect x="29" y="22" width="6" height="18" rx="2" fill="${OUT}"/><circle cx="32" cy="47" r="3.5" fill="${OUT}"/>`,
    steps: () => `<rect x="6" y="40" width="16" height="18" fill="#5DADE2" ${S}/><rect x="24" y="26" width="16" height="32" fill="#58D68D" ${S}/><rect x="42" y="10" width="16" height="48" fill="#F7C21B" ${S}/>`,
    ear: () => `<path d="M22 24 C22 8 46 6 46 26 C46 36 38 38 36 46 C34 56 22 58 20 48" fill="#F7D6B9" ${S}/><path d="M30 26 C30 18 40 18 40 26 C40 32 34 32 34 38" fill="none" ${S}/>`,
    eye: () => `<path d="M6 32 Q32 8 58 32 Q32 56 6 32 Z" fill="#fff" ${S}/><circle cx="32" cy="32" r="10" fill="#3498DB" ${S}/><circle cx="32" cy="32" r="4" fill="${OUT}"/><circle cx="36" cy="28" r="2" fill="#fff"/>`,
    tongue: () => `<path d="M10 24 Q32 18 54 24 Q52 50 32 52 Q12 50 10 24 Z" fill="#C0392B" ${S}/><path d="M22 34 Q32 28 42 34 Q42 50 32 50 Q22 50 22 34 Z" fill="#F08080" ${S}/>`,
    touch: () => `<path d="M26 58 L26 22 Q26 14 32 14 Q38 14 38 22 L38 36 L44 30 Q50 26 52 34 L50 48 Q48 58 38 58 Z" fill="#F7D6B9" ${S}/><path d="M18 20 q-8 -8 0 -16 M14 24 q-12 -10 -2 -22" fill="none" ${S}/>`,
    nose: () => `<path d="M32 10 L32 34 Q22 44 30 50 Q32 52 34 50 Q42 44 32 34" fill="#F7D6B9" ${S}/><path d="M44 18 q6 6 0 12 M50 14 q10 10 0 20" fill="none" ${S}/>`,
    toy: () => at(ITEMS.teddy(), 32, 28, 1),
    brinde: () => at(ITEMS.gift(), 32, 32, 0.9),
  };

  // ------------------------------------------------------------
  // CENAS
  // ------------------------------------------------------------
  const SCENES = {};

  // --- capa da cartilha do dentista ---
  SCENES.cover = () => scene(420, 470, `
    ${tiles(420, 332, '#6CBF4A')}${floor(420, 332, 138, '#F2E394')}
    ${window_(296, 40, 96, 72)}
    ${at(dentalChair(), 34, 100, 0.84)}
    ${lamp(28, 130, true)}
    ${put(DENTIST({ armL: 'wave', armR: 'show', holdR: 'mirror', expr: 'bigsmile' }), 300, 398, 1.0)}
    ${put(KID({ headphones: true, armL: 'hold', holdL: 'teddy', armR: 'down', expr: 'happy' }), 140, 396, 0.8, true)}
    ${toothMascot(392, 372, 0.5)}
  `, '', 'xMidYMax slice');

  // --- apresentação: os três formatos ---
  SCENES.threeFormats = () => scene(420, 180, `
    <rect x="0" y="0" width="420" height="180" rx="12" fill="#EAF6FF"/>
    ${at(ICON.steps(), 36, 40, 1.4)}
    ${htmlText(18, 128, 140, 44, 'Sequência visual da consulta', 12, 800, OUT, 'center', 'Baloo 2')}
    ${at(ICON.talk(), 176, 40, 1.4)}
    ${htmlText(158, 128, 140, 44, 'História social ilustrada', 12, 800, OUT, 'center', 'Baloo 2')}
    ${at(ICON.notes(), 316, 40, 1.4)}
    ${htmlText(298, 128, 120, 44, 'Passo a passo em quadrinhos', 12, 800, OUT, 'center', 'Baloo 2')}
    <line x1="150" y1="30" x2="150" y2="150" stroke="#BDC3C7" stroke-width="2" stroke-dasharray="6 6"/>
    <line x1="290" y1="30" x2="290" y2="150" stroke="#BDC3C7" stroke-width="2" stroke-dasharray="6 6"/>
  `);

  // --- ANTES 1: contato prévio por telefone ---
  SCENES.before_phone = () => scene(420, 300, `
    ${plainWall(210, 300, '#D6EAF8')}${plainWall(210, 300, '#FDEBD0').replace('x="0"', 'x="210"')}
    ${floor(420, 230, 70, '#F2E394')}
    <line x1="210" y1="0" x2="210" y2="300" ${S} stroke-dasharray="8 6"/>
    ${deskReception(10, 232, 160)}
    ${put(DENTIST({ armR: 'phone', holdR: 'phone', armL: 'hold', holdL: 'clipboard', expr: 'happy' }), 120, 296, 0.82)}
    ${sofa(236, 230, 150, '#E8A0BF')}
    ${put(MOM({ armR: 'phone', holdR: 'phone', armL: 'down', expr: 'happy' }), 300, 296, 0.82)}
    ${put(KID({ armL: 'hold', holdL: 'teddy', expr: 'neutral', sit: true }), 372, 292, 0.6)}
    ${bubble({ x: 10, y: 12, w: 190, h: 70, text: 'Me conte sobre ele: o que gosta, o que incomoda, como se comunica?', tail: [118, 118], size: 12 })}
    ${bubble({ x: 220, y: 12, w: 190, h: 70, text: 'Ele não gosta de barulho alto nem de luz forte. Adora dinossauros!', tail: [300, 118], size: 12 })}
  `);

  // --- ANTES 2: família vê vídeo do consultório em casa ---
  SCENES.before_video = () => scene(420, 300, `
    ${plainWall(420, 300, '#FDF2D0')}${floor(420, 232, 68, '#D7A86E')}
    ${tv(40, 30, 190, 130, `
      ${tiles(174, 70, '#6CBF4A', '#FFFFFF', 30)}${floor(174, 70, 44, '#F2E394')}
      ${at(dentalChair(), 90, 40, 0.3)}
      ${put(DENTIST({ armL: 'wave', expr: 'bigsmile' }), 40, 112, 0.34)}
    `)}
    ${sofa(240, 232, 160, '#E8A0BF')}
    ${put(MOM({ armR: 'point', expr: 'happy', sit: true }), 282, 236, 0.66)}
    ${put(KID({ armL: 'hold', holdL: 'teddy', expr: 'surprised', sit: true }), 360, 236, 0.56)}
    ${bubble({ x: 250, y: 14, w: 160, h: 64, text: 'Olha! Esse é o dentista e a cadeira que sobe e desce.', tail: [296, 118], size: 12 })}
  `);

  // --- ANTES 3: card entregue ao cuidador ---
  SCENES.before_card = () => scene(420, 240, `
    ${tiles(420, 180, '#6CBF4A')}${floor(420, 180, 60, '#F2E394')}
    ${put(DENTIST({ armR: 'show', holdR: 'card', expr: 'happy' }), 120, 236, 0.74)}
    ${put(MOM({ armL: 'show', expr: 'happy' }), 300, 236, 0.74, true)}
    ${bubble({ x: 150, y: 10, w: 230, h: 54, text: 'Leiam o card em casa, todos os dias, antes da consulta.', tail: [140, 86], size: 12 })}
  `);

  // --- DURANTE 1: sala de espera calma ---
  SCENES.waiting = () => scene(420, 300, `
    ${plainWall(420, 300, '#D6EAF8')}${floor(420, 232, 68, '#F2E394')}
    ${window_(280, 24, 120, 60)}
    ${plant(392, 232, 0.9)}
    ${put(RECEP({ armL: 'wave', expr: 'happy' }), 90, 180, 0.6)}
    ${deskReception(20, 232, 120, 90, false)}
    ${waitingChairs(170, 232, 3)}
    ${put(MOM({ sit: true, expr: 'happy', armL: 'lap' }), 212, 238, 0.66)}
    ${put(KID({ sit: true, headphones: true, armL: 'hold', holdL: 'teddy', expr: 'neutral' }), 288, 238, 0.56)}
    ${bubble({ x: 150, y: 12, w: 140, h: 44, text: 'Pode entrar!', tail: [112, 96], size: 13 })}
    ${at(ICON.mute(), 336, 124, 0.55)}${at(ICON.lampdim(), 374, 124, 0.55)}
  `);

  // --- DURANTE 2: Falar-Mostrar-Fazer ---
  SCENES.tellShowDo = () => scene(420, 300, `
    ${tiles(420, 232, '#6CBF4A')}${floor(420, 232, 68, '#F2E394')}
    ${lamp(60, 110, false)}
    ${at(dentalChair(), 160, 60, 0.72)}
    ${put(KID({ sit: true, headphones: true, sunglasses: true, armL: 'hold', holdL: 'teddy', expr: 'happy' }), 268, 240, 0.64)}
    ${tray(330, 232)}
    ${put(DENTIST({ armR: 'show', holdR: 'mirror', armL: 'down', expr: 'happy' }), 100, 296, 0.8)}
    ${put(MOM({ expr: 'happy', armL: 'down' }), 386, 296, 0.56, true)}
    ${bubble({ x: 10, y: 10, w: 200, h: 70, text: 'Este é o espelhinho. Olha, é frio e liso. Posso tocar no seu dente com ele?', tail: [100, 128], size: 12 })}
  `);

  // --- DURANTE 3: contar os dentinhos ---
  SCENES.countTeeth = () => scene(420, 300, `
    ${tiles(420, 232, '#6CBF4A')}${floor(420, 232, 68, '#F2E394')}
    ${lamp(330, 110, true)}
    ${at(dentalChair(), 150, 60, 0.72)}
    ${put(KID({ sit: true, headphones: true, sunglasses: true, armL: 'hold', holdL: 'teddy', expr: 'open' }), 258, 240, 0.64)}
    ${put(DENTIST({ armR: 'show', holdR: 'mirror', armL: 'up', expr: 'happy' }), 100, 296, 0.8)}
    ${bubble({ x: 10, y: 10, w: 190, h: 66, text: 'Um, dois, três… Quantos dentinhos! Mais dez segundos e acabou.', tail: [100, 128], size: 12 })}
    ${at(ICON.timer(), 350, 20, 0.9)}
  `);

  // --- DURANTE 4: sinal de PARE ---
  SCENES.stopSign = () => scene(420, 300, `
    ${tiles(420, 232, '#6CBF4A')}${floor(420, 232, 68, '#F2E394')}
    ${at(dentalChair(), 150, 60, 0.72)}
    ${put(KID({ sit: true, headphones: true, armL: 'hold', holdL: 'teddy', armR: 'stop', expr: 'worried' }), 258, 240, 0.64)}
    ${put(DENTIST({ armR: 'ok', armL: 'down', expr: 'happy' }), 100, 296, 0.8)}
    ${bubble({ x: 10, y: 10, w: 180, h: 66, text: 'Você levantou a mão: eu paro. Vamos respirar. Quando quiser, a gente continua.', tail: [100, 128], size: 11 })}
    ${bubble({ x: 250, y: 10, w: 150, h: 48, text: 'PARE!', tail: [300, 112], size: 20 })}
  `);

  // --- DURANTE 5: sobrecarga sensorial (o que evitar) ---
  SCENES.overload = () => scene(420, 240, `
    ${tiles(420, 180, '#E74C3C', '#F5B7B1')}${floor(420, 180, 60, '#F2E394')}
    ${lamp(40, 90, true)}
    ${put(KID({ armL: 'ears', armR: 'ears', expr: 'scared' }), 210, 236, 0.74)}
    ${noteMusic(300, 60)}${noteMusic(340, 90)}${noteMusic(90, 70)}
    ${htmlText(255, 128, 150, 30, 'BZZZZZ!', 20, 800, '#F7C21B')}
    ${htmlText(70, 14, 120, 30, 'VRRRR!', 20, 800, '#F7C21B')}
  `);

  // --- DEPOIS 1: brinde e elogio ---
  SCENES.reward = () => scene(420, 300, `
    ${tiles(420, 232, '#6CBF4A')}${floor(420, 232, 68, '#F2E394')}
    ${sparkles(330, 70)}${sparkles(90, 60)}
    ${put(DENTIST({ armR: 'show', holdR: 'gift', armL: 'down', expr: 'bigsmile' }), 120, 296, 0.82)}
    ${put(KID({ armL: 'up', armR: 'hold', holdR: 'teddy', expr: 'bigsmile', headphones: true }), 290, 296, 0.72, true)}
    ${bubble({ x: 150, y: 10, w: 240, h: 56, text: 'Você abriu a boca e deixou eu contar os dentes. Parabéns!', tail: [140, 110], size: 12 })}
  `);

  // --- DEPOIS 2: higiene em casa ---
  SCENES.homeHygiene = () => scene(420, 300, `
    ${tiles(420, 232, '#5DADE2', '#FFFFFF')}${floor(420, 232, 68, '#F2E394')}
    <rect x="250" y="150" width="150" height="82" rx="6" fill="#49B9A9" ${S}/><ellipse cx="325" cy="150" rx="55" ry="14" fill="#A9DFD8" ${S}/><rect x="320" y="100" width="10" height="46" fill="#95A5A6" ${S}/><rect x="306" y="96" width="38" height="10" rx="4" fill="#95A5A6" ${S}/>
    ${put(MOM({ armR: 'show', holdR: 'card', expr: 'happy' }), 110, 296, 0.8)}
    ${put(KID({ armR: 'hold', holdR: 'toothbrush', expr: 'bigsmile' }), 230, 296, 0.72)}
    ${bubble({ x: 20, y: 10, w: 200, h: 56, text: 'Primeiro em cima, depois embaixo. Igual ao cartaz!', tail: [110, 108], size: 12 })}
    <rect x="20" y="90" width="110" height="70" rx="6" fill="#FFFFFF" ${S}/>
    ${at(ICON.toothbrush(), 28, 98, 0.5)}${at(ICON.clock(), 66, 98, 0.5)}${at(ICON.tooth(), 100, 98, 0.45)}
    ${htmlText(22, 130, 106, 26, 'escovar · 2 min · flúor', 9, 800, OUT, 'center', 'Baloo 2')}
  `);

  // --- DEPOIS 3: registro e retorno ---
  SCENES.record = () => scene(420, 240, `
    ${plainWall(420, 180, '#D6EAF8')}${floor(420, 180, 60, '#F2E394')}
    ${deskReception(40, 180, 170)}
    ${put(DENTIST({ armL: 'hold', holdL: 'clipboard', armR: 'hold', holdR: 'pen', expr: 'happy' }), 300, 236, 0.58)}
    ${bubble({ x: 150, y: 0, w: 240, h: 56, text: 'Funcionou: óculos escuros, fones e contar até dez. Próxima vez: tentar a escovação.', tail: [300, 100], kind: 'thought', size: 11 })}
    ${at(ICON.calendar(), 70, 40, 0.9)}
  `);

  // --- CARD: passos da história social (quadros pequenos 240x170) ---
  const CARD_W = 240, CARD_H = 170;
  const cardScene = (inner) => scene(CARD_W, CARD_H, inner);

  SCENES.c1_arrive = () => cardScene(`
    ${plainWall(240, 130, '#D6EAF8')}${floor(240, 130, 40, '#F2E394')}
    ${door(140, 20, 60, 112)}${wallSign(150, 4, 'Dentista', 60, 18)}
    ${put(MOM({ armL: 'hold', expr: 'happy' }), 60, 166, 0.5)}
    ${put(KID({ armR: 'hold', holdR: 'teddy', expr: 'happy', headphones: true }), 108, 166, 0.42)}
  `);
  SCENES.c2_wait = () => cardScene(`
    ${plainWall(240, 130, '#D6EAF8')}${floor(240, 130, 40, '#F2E394')}
    ${waitingChairs(30, 130, 2, '#5DADE2')}${plant(210, 130, 0.6)}
    ${put(MOM({ sit: true, expr: 'happy', armL: 'lap' }), 62, 134, 0.46)}
    ${put(KID({ sit: true, headphones: true, armL: 'hold', holdL: 'teddy', expr: 'neutral' }), 136, 134, 0.4)}
    ${at(ICON.mute(), 190, 20, 0.55)}
  `);
  SCENES.c3_called = () => cardScene(`
    ${plainWall(240, 130, '#D6EAF8')}${floor(240, 130, 40, '#F2E394')}
    ${put(RECEP({ armL: 'wave', expr: 'happy' }), 80, 128, 0.44)}
    ${deskReception(20, 130, 110, 60, false)}
    ${put(KID({ expr: 'happy', headphones: true, armR: 'hold', holdR: 'teddy' }), 190, 166, 0.46)}
    ${bubble({ x: 110, y: 6, w: 100, h: 34, text: 'Pode entrar!', tail: [100, 58], size: 11 })}
  `);
  SCENES.c4_enter = () => cardScene(`
    ${tiles(240, 130, '#6CBF4A', '#FFFFFF', 30)}${floor(240, 130, 40, '#F2E394')}
    ${door(10, 20, 50, 112)}
    ${put(DENTIST({ armL: 'wave', expr: 'bigsmile' }), 160, 166, 0.52)}
    ${put(KID({ expr: 'happy', headphones: true, armR: 'hold', holdR: 'teddy' }), 80, 166, 0.44)}
    ${bubble({ x: 120, y: 6, w: 110, h: 34, text: 'Oi! Que bom te ver.', tail: [160, 60], size: 10 })}
  `);
  SCENES.c5_show = () => cardScene(`
    ${tiles(240, 130, '#6CBF4A', '#FFFFFF', 30)}${floor(240, 130, 40, '#F2E394')}
    ${at(dentalChair(), 110, 36, 0.4)}
    ${put(DENTIST({ armR: 'show', holdR: 'mirror', expr: 'happy' }), 70, 166, 0.5)}
    ${put(KID({ expr: 'surprised', headphones: true, armR: 'hold', holdR: 'teddy' }), 200, 166, 0.44, true)}
  `);
  SCENES.c6_sit = () => cardScene(`
    ${tiles(240, 130, '#6CBF4A', '#FFFFFF', 30)}${floor(240, 130, 40, '#F2E394')}
    ${at(dentalChair(), 90, 30, 0.44)}
    ${put(KID({ sit: true, headphones: true, sunglasses: true, armL: 'hold', holdL: 'teddy', expr: 'happy' }), 156, 140, 0.4)}
    <path d="M40 60 l0 -24 M32 46 l8 -10 l8 10" fill="none" ${S}/><path d="M40 80 l0 24 M32 94 l8 10 l8 -10" fill="none" ${S}/>
  `);
  SCENES.c7_open = () => cardScene(`
    ${tiles(240, 130, '#6CBF4A', '#FFFFFF', 30)}${floor(240, 130, 40, '#F2E394')}
    ${lamp(200, 60, true)}
    ${at(dentalChair(), 100, 30, 0.44)}
    ${put(KID({ sit: true, headphones: true, sunglasses: true, armL: 'hold', holdL: 'teddy', expr: 'open' }), 166, 140, 0.4)}
    ${put(DENTIST({ armR: 'show', holdR: 'mirror', armL: 'up', expr: 'happy' }), 60, 166, 0.5)}
    ${bubble({ x: 6, y: 6, w: 96, h: 34, text: '1, 2, 3…', tail: [60, 64], size: 12 })}
  `);
  SCENES.c8_clean = () => cardScene(`
    ${tiles(240, 130, '#6CBF4A', '#FFFFFF', 30)}${floor(240, 130, 40, '#F2E394')}
    ${at(dentalChair(), 100, 30, 0.44)}
    ${put(KID({ sit: true, headphones: true, sunglasses: true, armL: 'hold', holdL: 'teddy', expr: 'open' }), 166, 140, 0.4)}
    ${put(DENTIST({ armR: 'show', holdR: 'toothbrush', expr: 'happy' }), 60, 166, 0.5)}
    ${sparkles(200, 40)}
  `);
  SCENES.c9_gift = () => cardScene(`
    ${tiles(240, 130, '#6CBF4A', '#FFFFFF', 30)}${floor(240, 130, 40, '#F2E394')}
    ${sparkles(200, 36)}${sparkles(40, 40)}
    ${put(DENTIST({ armR: 'show', holdR: 'gift', expr: 'bigsmile' }), 70, 166, 0.5)}
    ${put(KID({ armL: 'up', armR: 'hold', holdR: 'teddy', expr: 'bigsmile', headphones: true }), 180, 166, 0.46, true)}
  `);
  SCENES.c10_bye = () => cardScene(`
    ${plainWall(240, 130, '#D6EAF8')}${floor(240, 130, 40, '#F2E394')}
    ${door(170, 20, 56, 112)}
    ${put(DENTIST({ armL: 'wave', expr: 'bigsmile' }), 60, 166, 0.5)}
    ${put(MOM({ armL: 'hold', expr: 'happy' }), 130, 166, 0.46)}
    ${put(KID({ armL: 'wave', armR: 'hold', holdR: 'gift', expr: 'bigsmile', headphones: true }), 112, 166, 0.4, true)}
    ${bubble({ x: 6, y: 6, w: 110, h: 34, text: 'Tchau! Até a próxima.', tail: [60, 60], size: 10 })}
  `);


  // ======= CARTILHA DA CRIANÇA (cenas grandes 420x300) =======
  const HOME = (extra = '') => `${plainWall(420, 232, '#FDF2D0')}${floor(420, 232, 68, '#D7A86E')}${extra}`;
  const ROOM = (extra = '') => `${tiles(420, 232, '#6CBF4A')}${floor(420, 232, 68, '#F2E394')}${extra}`;
  const LOBBY = (extra = '') => `${plainWall(420, 232, '#D6EAF8')}${floor(420, 232, 68, '#F2E394')}${extra}`;

  function wallCalendar(x, y, w = 110, h = 96) {
    let cells = '';
    for (let r = 0; r < 4; r++) for (let c = 0; c < 7; c++) {
      const cx = x + 8 + c * ((w - 16) / 7), cy = y + 26 + r * ((h - 32) / 4);
      cells += `<rect x="${cx}" y="${cy}" width="${(w - 16) / 7 - 2}" height="${(h - 32) / 4 - 2}" fill="#F4F6F7"/>`;
    }
    const dx = x + 8 + 3 * ((w - 16) / 7) + ((w - 16) / 14), dy = y + 26 + 1 * ((h - 32) / 4) + ((h - 32) / 8);
    return `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="5" fill="#fff" ${S}/><rect x="${x}" y="${y}" width="${w}" height="20" rx="5" fill="#E74C3C" ${S}/>${cells}<circle cx="${dx}" cy="${dy}" r="9" fill="none" stroke="#E74C3C" stroke-width="3"/>${at(ICON.tooth(), dx - 7, dy - 7, 0.22)}`;
  }
  function cuspidor(x, y) {
    return `<g transform="translate(${x} ${y})"><rect x="-8" y="-60" width="16" height="60" fill="#95A5A6" ${S}/><ellipse cx="0" cy="-62" rx="34" ry="12" fill="#ECF0F1" ${S}/><ellipse cx="0" cy="-62" rx="20" ry="6" fill="#AED6F1" ${S}/><rect x="-40" y="-120" width="8" height="56" rx="3" fill="#95A5A6" ${S}/><path d="M-36 -120 q0 -10 10 -10 h8" fill="none" ${S} stroke-width="5"/></g>`;
  }

  SCENES.k_calendar = () => scene(420, 300, HOME(`
    ${wallCalendar(40, 40)}
    ${window_(290, 36, 100, 70)}
    ${put(MOM({ armR: 'point', expr: 'happy' }), 250, 296, 0.8, true)}
    ${put(KID({ armL: 'point', armR: 'hold', holdR: 'teddy', expr: 'surprised' }), 150, 296, 0.72)}
    ${bubble({ x: 170, y: 10, w: 220, h: 54, text: 'Hoje é o dia do dentista! Está marcado no calendário.', tail: [250, 108], size: 12 })}
  `));
  SCENES.k_prepare = () => scene(420, 300, HOME(`
    <rect x="200" y="170" width="200" height="14" rx="4" fill="#A0522D" ${S}/><rect x="214" y="184" width="12" height="48" fill="#A0522D" ${S}/><rect x="374" y="184" width="12" height="48" fill="#A0522D" ${S}/>
    ${at(ICON.headphones(), 220, 118, 0.8)}${at(ITEMS.sunglassesItem(), 310, 150, 1)}${at(ITEMS.card(), 360, 150, 0.8)}
    ${put(KID({ armL: 'hold', holdL: 'teddy', armR: 'point', expr: 'happy' }), 110, 296, 0.8)}
    ${bubble({ x: 20, y: 10, w: 220, h: 54, text: 'Meu brinquedo, meus fones, meus óculos e meu card.', tail: [110, 92], size: 12 })}
  `));
  SCENES.k_reception = () => scene(420, 300, LOBBY(`
    ${put(RECEP({ armL: 'down', expr: 'happy' }), 110, 196, 0.62)}
    ${deskReception(30, 240, 160, 90, true)}
    ${put(MOM({ armL: 'hold', holdL: 'clipboard', armR: 'hold', holdR: 'pen', expr: 'happy' }), 280, 296, 0.8)}
    ${put(KID({ armR: 'hold', holdR: 'teddy', headphones: true, expr: 'neutral' }), 372, 296, 0.66)}
    ${bubble({ x: 20, y: 10, w: 180, h: 50, text: 'Bom dia! Sejam bem-vindos.', tail: [110, 98], size: 12 })}
  `));
  SCENES.k_bib = () => scene(420, 300, ROOM(`
    ${at(dentalChair(), 160, 60, 0.72)}
    ${put(KID({ sit: true, headphones: true, bib: true, armL: 'hold', holdL: 'teddy', expr: 'happy' }), 268, 240, 0.64)}
    ${put(DENTIST({ maskUp: true, gloves: true, armR: 'wave', expr: 'happy' }), 100, 296, 0.8)}
    ${bubble({ x: 10, y: 10, w: 200, h: 60, text: 'Coloquei máscara e luvas, mas sou eu mesmo! O babador protege sua roupa.', tail: [100, 118], size: 11 })}
  `));
  SCENES.k_glasses = () => scene(420, 300, ROOM(`
    ${lamp(330, 110, true)}
    ${at(dentalChair(), 150, 60, 0.72)}
    ${put(KID({ sit: true, headphones: true, sunglasses: true, bib: true, armL: 'hold', holdL: 'teddy', expr: 'happy' }), 258, 240, 0.64)}
    ${put(DENTIST({ maskUp: true, gloves: true, armR: 'point', expr: 'happy' }), 90, 296, 0.8)}
    ${bubble({ x: 10, y: 10, w: 190, h: 56, text: 'Vou ligar a luz agora. Ela ilumina a boca, não os olhos.', tail: [90, 118], size: 11 })}
  `));
  SCENES.k_mirror = () => scene(420, 300, ROOM(`
    ${at(dentalChair(), 160, 60, 0.72)}
    ${put(KID({ sit: true, headphones: true, sunglasses: true, bib: true, armL: 'hold', holdL: 'teddy', armR: 'ok', expr: 'happy' }), 268, 240, 0.64)}
    ${put(DENTIST({ maskUp: true, gloves: true, armR: 'show', holdR: 'mirror', expr: 'happy' }), 100, 296, 0.8)}
    ${bubble({ x: 10, y: 10, w: 200, h: 56, text: 'Este é o espelhinho. Toca com o dedo: é frio e liso.', tail: [100, 118], size: 11 })}
  `));
  SCENES.k_suction = () => scene(420, 300, ROOM(`
    ${at(dentalChair(), 160, 60, 0.72)}
    ${put(KID({ sit: true, headphones: true, sunglasses: true, bib: true, armL: 'hold', holdL: 'teddy', expr: 'open' }), 268, 240, 0.64)}
    ${put(DENTIST({ maskUp: true, gloves: true, armR: 'show', holdR: 'suction', expr: 'happy' }), 100, 296, 0.8)}
    ${htmlText(306, 86, 110, 30, 'shhhhhh', 18, 700, '#2C3E50')}
    ${bubble({ x: 10, y: 10, w: 190, h: 56, text: 'O canudinho faz “shhh” e puxa a água. Ouve primeiro, longe da boca.', tail: [100, 118], size: 11 })}
  `));
  SCENES.k_polish = () => scene(420, 300, ROOM(`
    ${at(dentalChair(), 160, 60, 0.72)}
    ${put(KID({ sit: true, headphones: true, sunglasses: true, bib: true, armL: 'hold', holdL: 'teddy', expr: 'open' }), 268, 240, 0.64)}
    ${put(DENTIST({ maskUp: true, gloves: true, armR: 'show', holdR: 'polisher', expr: 'happy' }), 100, 296, 0.8)}
    ${sparkles(340, 80)}
    ${bubble({ x: 10, y: 10, w: 200, h: 56, text: 'A escovinha gira e faz cócegas. A pastinha tem gosto de fruta.', tail: [100, 118], size: 11 })}
  `));
  SCENES.k_rinse = () => scene(420, 300, ROOM(`
    ${cuspidor(330, 232)}
    ${put(KID({ armR: 'hold', holdR: 'cup', headphones: true, bib: true, expr: 'happy' }), 250, 296, 0.72)}
    ${put(DENTIST({ maskUp: true, gloves: true, armR: 'point', expr: 'happy' }), 100, 296, 0.8)}
    ${bubble({ x: 10, y: 10, w: 200, h: 54, text: 'Agora pode enxaguar e cuspir aqui na pia pequena.', tail: [100, 118], size: 11 })}
  `));
  SCENES.k_next = () => scene(420, 300, LOBBY(`
    ${put(RECEP({ armL: 'hold', holdL: 'card', expr: 'happy' }), 110, 196, 0.62)}
    ${deskReception(30, 240, 160, 90, false)}
    ${at(ICON.calendar(), 60, 100, 0.9)}
    ${put(MOM({ armL: 'down', expr: 'happy' }), 290, 296, 0.8)}
    ${put(KID({ armR: 'hold', holdR: 'gift', headphones: true, expr: 'bigsmile' }), 380, 296, 0.66)}
    ${bubble({ x: 180, y: 10, w: 220, h: 54, text: 'Até o próximo dia! Vamos marcar no calendário.', tail: [300, 110], size: 12 })}
  `));
  SCENES.k_cover = () => scene(420, 470, `
    ${tiles(420, 332, '#5DADE2', '#FFFFFF')}${floor(420, 332, 138, '#F2E394')}
    ${window_(296, 40, 96, 72)}
    ${at(dentalChair(), 34, 100, 0.84)}
    ${lamp(28, 130, true)}
    ${put(KID({ headphones: true, armL: 'wave', armR: 'hold', holdR: 'teddy', expr: 'bigsmile' }), 150, 398, 0.9)}
    ${put(DENTIST({ armL: 'wave', expr: 'bigsmile' }), 320, 398, 0.86)}
    ${toothMascot(392, 372, 0.5)}
  `, '', 'xMidYMax slice');

  // retratos (quem eu vou encontrar)
  SCENES.p_dentist = () => scene(200, 310, put(DENTIST({ armL: 'wave', expr: 'bigsmile' }), 100, 305, 1));
  SCENES.p_dentist_mask = () => scene(200, 310, put(DENTIST({ maskUp: true, gloves: true, armL: 'wave', expr: 'happy' }), 100, 305, 1));
  SCENES.p_assist = () => scene(200, 310, put(ASSIST({ armL: 'wave', expr: 'bigsmile' }), 100, 305, 1));
  SCENES.p_recep = () => scene(200, 310, put(RECEP({ armL: 'wave', expr: 'bigsmile' }), 100, 305, 1));
  SCENES.p_mom = () => scene(200, 310, put(MOM({ armL: 'wave', expr: 'bigsmile' }), 100, 305, 1));
  SCENES.p_kid = () => scene(200, 310, put(KID({ armL: 'wave', armR: 'hold', holdR: 'teddy', headphones: true, expr: 'bigsmile' }), 100, 305, 1));

  // objetos (o que tem na sala)
  const OBJ = (inner) => scene(120, 120, `<rect x="2" y="2" width="116" height="116" rx="12" fill="#FFFFFF"/>${inner}`);
  SCENES.o_chair = () => OBJ(at(dentalChair(), 8, 8, 0.36));
  SCENES.o_lamp = () => OBJ(`<g transform="translate(16 8) scale(.8)">${lamp(30, 90, true)}</g>`);
  SCENES.o_mirror = () => OBJ(at(ITEMS.mirror(), 60, 62, 1.4));
  SCENES.o_suction = () => OBJ(at(ITEMS.suction(), 40, 96, 1.3));
  SCENES.o_spray = () => OBJ(at(ITEMS.spray(), 56, 98, 1.05));
  SCENES.o_polisher = () => OBJ(at(ITEMS.polisher(), 56, 92, 1.1));
  SCENES.o_bib = () => OBJ(`<path d="M30 30 Q60 46 90 30 L94 100 Q60 110 26 100 Z" fill="#CFEFF7" ${S}/><path d="M44 22 Q60 34 76 22" fill="none" ${S} stroke-width="4"/>`);
  SCENES.o_glasses = () => OBJ(at(ITEMS.sunglassesItem(), 60, 60, 2.2));
  SCENES.o_headphones = () => OBJ(at(ICON.headphones(), 14, 14, 1.45));
  SCENES.o_cup = () => OBJ(at(ITEMS.cup(), 60, 60, 2.4));
  SCENES.o_gloves = () => OBJ(`<path d="M44 108 L44 48 Q44 38 52 38 Q60 38 60 48 L60 30 Q60 20 68 20 Q76 20 76 30 L76 52 L84 44 Q92 38 94 48 L92 80 Q90 108 70 108 Z" fill="#A8D8EA" ${S}/>`);
  SCENES.o_mask = () => OBJ(`<path d="M28 44 Q60 36 92 44 L88 84 Q60 98 32 84 Z" fill="#A8D8EA" ${S}/><path d="M28 46 q-14 -4 -16 10 M92 46 q14 -4 16 10 M32 82 q-14 2 -16 -8 M88 82 q14 2 16 -8" fill="none" ${S}/>`);

  // --- sinais do card ---
  SCENES.sig_stop = () => scene(120, 120, `<circle cx="60" cy="60" r="54" fill="#E74C3C" ${S}/>${at(ICON.stop(), 28, 24, 1.1)}`);
  SCENES.sig_ok = () => scene(120, 120, `<circle cx="60" cy="60" r="54" fill="#58D68D" ${S}/>${at(ICON.thumbs(), 26, 26, 1.1)}`);
  SCENES.sig_pause = () => scene(120, 120, `<circle cx="60" cy="60" r="54" fill="#F7C21B" ${S}/><rect x="40" y="32" width="14" height="56" rx="4" fill="#fff" ${S}/><rect x="66" y="32" width="14" height="56" rx="4" fill="#fff" ${S}/>`);

  // --- capa do card ---
  SCENES.cardCover = () => scene(420, 260, `
    ${tiles(420, 200, '#5DADE2', '#FFFFFF')}${floor(420, 200, 60, '#F2E394')}
    ${at(dentalChair(), 230, 40, 0.6)}
    ${put(KID({ armL: 'wave', armR: 'hold', holdR: 'teddy', expr: 'bigsmile', headphones: true }), 150, 256, 0.78)}
    ${put(DENTIST({ armL: 'wave', expr: 'bigsmile' }), 360, 256, 0.62)}
    ${toothMascot(62, 86, 0.42)}
  `);

  // --- kid solo for notes ---
  SCENES.kidWave = () => scene(200, 310, put(KID({ armL: 'wave', expr: 'bigsmile', headphones: true }), 100, 305, 1));
  SCENES.dentistWave = () => scene(200, 310, put(DENTIST({ armL: 'wave', expr: 'bigsmile' }), 100, 305, 1));
  SCENES.momKid = () => scene(260, 310, put(MOM({ armR: 'hold', expr: 'happy' }), 90, 305, 1) + put(KID({ armL: 'hold', holdL: 'teddy', expr: 'happy' }), 200, 305, 0.78));

  // ------------------------------------------------------------
  // renderização automática
  // ------------------------------------------------------------
  function render() {
    document.querySelectorAll('[data-scene]').forEach(el => {
      const fn = SCENES[el.dataset.scene];
      if (fn) el.innerHTML = fn();
      else el.innerHTML = `<div style="color:red">cena '${el.dataset.scene}' não existe</div>`;
    });
    document.querySelectorAll('[data-icon]').forEach(el => {
      const fn = ICON[el.dataset.icon];
      if (fn) el.innerHTML = `<svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:100%;display:block">${fn()}</svg>`;
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', render); else render();

  window.ILL = { SCENES, ICON, person, KID, DENTIST, MOM, RECEP, ASSIST, put, scene, bubble, render };
})();
