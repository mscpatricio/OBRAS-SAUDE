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


  // ======= ENFERMAGEM NA UBS =======
  const NURSE = (o = {}) => person(Object.assign({ skin: '#F2C9A6', hair: '#3B2A1A', hairStyle: 'bun', shirt: '#FFFFFF', pants: '#FFFFFF', coat: '#5DADE2', sleeve: 'long', shoes: '#FFFFFF' }, o));
  ITEMS.syringe = () => `<g transform="rotate(-30)"><rect x="-5" y="-30" width="10" height="40" rx="3" fill="#ECF0F1" ${S}/><rect x="-3" y="-20" width="6" height="26" fill="#AED6F1"/><rect x="-9" y="10" width="18" height="5" rx="2" fill="#95A5A6" ${S}/><rect x="-2" y="14" width="4" height="12" fill="#7F8C8D" ${S}/><line x1="0" y1="-30" x2="0" y2="-42" ${S} stroke-width="2"/></g>`;
  ITEMS.thermo = () => `<g transform="rotate(-30)"><rect x="-5" y="-36" width="10" height="56" rx="5" fill="#ECF0F1" ${S}/><rect x="-7" y="-44" width="14" height="12" rx="3" fill="#5DADE2" ${S}/><rect x="-3" y="-20" width="6" height="22" rx="2" fill="#2C3E50"/></g>`;
  ITEMS.bandage = () => `<g transform="rotate(-20)"><rect x="-26" y="-9" width="52" height="18" rx="9" fill="#F5CBA7" ${S}/><rect x="-10" y="-7" width="20" height="14" rx="3" fill="#FFFFFF" ${S} stroke-width="2"/></g>`;
  ITEMS.cuff = () => `<g><rect x="-26" y="-14" width="52" height="28" rx="6" fill="#2C3E50" ${S}/><circle cx="0" cy="0" r="10" fill="#ECF0F1" ${S}/><line x1="0" y1="0" x2="5" y2="-6" ${S} stroke-width="2"/></g>`;
  ITEMS.sticker = () => `${star(0, 0, 14, '#F7C21B')}`;
  function scale(x, y) {
    return `<g transform="translate(${x} ${y})"><rect x="-44" y="-14" width="88" height="14" rx="4" fill="#5DADE2" ${S}/><rect x="-34" y="-150" width="8" height="136" fill="#95A5A6" ${S}/><rect x="-42" y="-176" width="56" height="28" rx="4" fill="#ECF0F1" ${S}/><rect x="-36" y="-170" width="44" height="16" rx="2" fill="#2C3E50"/></g>`;
  }
  function bpMonitor(x, y) {
    return `<g transform="translate(${x} ${y})"><rect x="-28" y="-60" width="56" height="60" rx="6" fill="#ECF0F1" ${S}/><rect x="-22" y="-54" width="44" height="26" rx="3" fill="#2C3E50"/>${htmlText(-22, -54, 44, 26, '120/80', 9, 800, '#58D68D')}<circle cx="-10" cy="-14" r="5" fill="#5DADE2" ${S}/><circle cx="10" cy="-14" r="5" fill="#E74C3C" ${S}/></g>`;
  }
  function stretcher(x, y, w = 190) {
    return `<g transform="translate(${x} ${y})"><rect x="0" y="-50" width="${w}" height="22" rx="6" fill="#AED6F1" ${S}/><rect x="-6" y="-66" width="44" height="22" rx="8" fill="#FFFFFF" ${S}/><rect x="0" y="-28" width="${w}" height="10" fill="#95A5A6" ${S}/><rect x="14" y="-18" width="10" height="44" fill="#7F8C8D" ${S}/><rect x="${w - 24}" y="-18" width="10" height="44" fill="#7F8C8D" ${S}/><circle cx="19" cy="28" r="7" fill="#2C3E50" ${S}/><circle cx="${w - 19}" cy="28" r="7" fill="#2C3E50" ${S}/></g>`;
  }
  function vaccineFridge(x, y) {
    return `<g transform="translate(${x} ${y})"><rect x="0" y="-150" width="70" height="150" rx="6" fill="#ECF0F1" ${S}/><rect x="6" y="-144" width="58" height="80" rx="3" fill="#AED6F1" ${S}/><rect x="6" y="-58" width="58" height="52" rx="3" fill="#D6EAF8" ${S}/><rect x="56" y="-120" width="6" height="30" rx="3" fill="#7F8C8D"/><rect x="14" y="-136" width="42" height="6" fill="#58D68D"/><rect x="14" y="-124" width="42" height="6" fill="#F7C21B"/><rect x="14" y="-112" width="42" height="6" fill="#E74C3C"/></g>`;
  }
  const UBS = (extra = '') => `${plainWall(420, 232, '#E8F8F5')}${floor(420, 232, 68, '#F2E394')}<rect x="0" y="150" width="420" height="10" fill="#58D68D" ${S}/>${extra}`;

  SCENES.n_cover = () => scene(420, 470, `
    ${plainWall(420, 332, '#E8F8F5')}${floor(420, 332, 138, '#F2E394')}<rect x="0" y="230" width="420" height="12" fill="#58D68D" ${S}/>
    ${window_(296, 40, 96, 72)}
    ${wallSign(40, 150, 'UBS · Enfermagem', 150, 36)}
    ${stretcher(40, 330, 170)}
    ${bpMonitor(372, 330)}
    ${put(NURSE({ armL: 'wave', armR: 'hold', holdR: 'clipboard', expr: 'bigsmile' }), 300, 440, 1.0)}
    ${put(KID({ headphones: true, armL: 'hold', holdL: 'teddy', expr: 'happy' }), 140, 436, 0.82, true)}
  `, '', 'xMidYMax slice');
  SCENES.n_acolhimento = () => scene(420, 300, UBS(`
    ${put(RECEP({ armL: 'wave', expr: 'happy' }), 100, 196, 0.6)}
    ${deskReception(30, 240, 150, 90, false)}
    ${put(MOM({ armL: 'hold', holdL: 'card', expr: 'happy' }), 290, 296, 0.78)}
    ${put(KID({ armR: 'hold', holdR: 'teddy', headphones: true, expr: 'neutral' }), 372, 296, 0.64)}
    ${bubble({ x: 150, y: 10, w: 200, h: 56, text: 'Bom dia! Já vi na ficha que ele prefere esperar na sala calma.', tail: [112, 90], size: 11 })}
  `));
  SCENES.n_triagem = () => scene(420, 300, UBS(`
    ${scale(380, 232)}
    ${bpMonitor(60, 232)}
    ${put(KID({ sit: true, headphones: true, armL: 'hold', holdL: 'teddy', armR: 'down', expr: 'happy' }), 300, 240, 0.64)}
    <rect x="250" y="206" width="100" height="26" rx="6" fill="#5DADE2" ${S}/><rect x="258" y="232" width="8" height="50" fill="#7F8C8D" ${S}/><rect x="334" y="232" width="8" height="50" fill="#7F8C8D" ${S}/>
    ${put(NURSE({ armR: 'show', holdR: 'cuff', expr: 'happy' }), 140, 296, 0.8)}
    ${bubble({ x: 10, y: 10, w: 210, h: 60, text: 'Esta braçadeira vai apertar o braço, como um abraço. Conto até dez e solta.', tail: [140, 118], size: 11 })}
  `));
  SCENES.n_vacina = () => scene(420, 300, UBS(`
    ${vaccineFridge(340, 232)}
    ${wallSign(30, 24, 'Sala de vacina', 130, 30)}
    ${put(MOM({ sit: true, expr: 'happy', armL: 'lap' }), 250, 240, 0.7)}
    <rect x="200" y="206" width="100" height="26" rx="6" fill="#5DADE2" ${S}/><rect x="208" y="232" width="8" height="50" fill="#7F8C8D" ${S}/><rect x="284" y="232" width="8" height="50" fill="#7F8C8D" ${S}/>
    ${put(KID({ sit: true, headphones: true, sunglasses: true, armL: 'hold', holdL: 'teddy', armR: 'front', expr: 'happyclosed' }), 236, 250, 0.5)}
    ${put(NURSE({ armR: 'show', holdR: 'syringe', gloves: true, expr: 'happy' }), 110, 296, 0.8)}
    ${bubble({ x: 10, y: 10, w: 190, h: 60, text: 'Vai ser uma picadinha rápida, como um beliscão. Olha para o ursinho e conta comigo.', tail: [110, 118], size: 11 })}
  `));
  SCENES.n_curativo = () => scene(420, 300, UBS(`
    ${stretcher(190, 232, 200)}
    ${tray(30, 232)}
    ${put(KID({ sit: true, headphones: true, armL: 'hold', holdL: 'teddy', armR: 'front', expr: 'happy' }), 290, 236, 0.6)}
    ${put(NURSE({ armR: 'show', holdR: 'bandage', gloves: true, expr: 'happy' }), 140, 296, 0.8)}
    ${bubble({ x: 10, y: 10, w: 210, h: 56, text: 'Primeiro eu limpo, fica gelado. Depois coloco o curativo. Você escolhe a cor.', tail: [140, 118], size: 11 })}
  `));
  SCENES.n_coleta = () => scene(420, 300, UBS(`
    ${tray(330, 232)}
    ${put(KID({ sit: true, headphones: true, sunglasses: true, armL: 'hold', holdL: 'teddy', armR: 'front', expr: 'neutral' }), 280, 240, 0.64)}
    <rect x="230" y="206" width="100" height="26" rx="6" fill="#5DADE2" ${S}/><rect x="238" y="232" width="8" height="50" fill="#7F8C8D" ${S}/><rect x="314" y="232" width="8" height="50" fill="#7F8C8D" ${S}/>
    ${put(NURSE({ armR: 'show', holdR: 'syringe', gloves: true, expr: 'happy' }), 120, 296, 0.8)}
    ${at(ICON.timer(), 30, 100, 0.9)}
    ${bubble({ x: 10, y: 10, w: 200, h: 56, text: 'Vou amarrar esta fitinha no braço. Aperta um pouco. Até dez e acabou.', tail: [120, 118], size: 11 })}
  `));
  SCENES.n_registro = () => scene(420, 240, `
    ${plainWall(420, 180, '#E8F8F5')}${floor(420, 180, 60, '#F2E394')}
    ${deskReception(40, 180, 170)}
    ${put(NURSE({ armL: 'hold', holdL: 'clipboard', armR: 'hold', holdR: 'pen', expr: 'happy' }), 300, 236, 0.58)}
    ${bubble({ x: 150, y: 0, w: 240, h: 56, text: 'Funcionou: fones, contar até dez e o ursinho. Próxima vez: sala calma e vacina no início.', tail: [300, 100], kind: 'thought', size: 11 })}
    ${at(ICON.calendar(), 70, 40, 0.9)}
  `);
  SCENES.n_recompensa = () => scene(420, 300, UBS(`
    ${sparkles(330, 70)}${sparkles(90, 60)}
    ${put(NURSE({ armR: 'show', holdR: 'sticker', expr: 'bigsmile' }), 120, 296, 0.82)}
    ${put(KID({ armL: 'up', armR: 'hold', holdR: 'teddy', expr: 'bigsmile', headphones: true }), 290, 296, 0.72, true)}
    ${bubble({ x: 150, y: 10, w: 240, h: 56, text: 'Você ficou quietinho e deixou medir a pressão. Parabéns! Escolhe o adesivo.', tail: [140, 110], size: 11 })}
  `));
  SCENES.n_domicilio = () => scene(420, 300, `
    ${plainWall(420, 232, '#FDF2D0')}${floor(420, 232, 68, '#D7A86E')}
    ${door(20, 70, 70, 162)}${window_(300, 40, 100, 70)}
    ${put(NURSE({ armL: 'hold', holdL: 'clipboard', armR: 'wave', expr: 'bigsmile' }), 150, 296, 0.8)}
    ${put(MOM({ armR: 'hold', expr: 'happy' }), 300, 296, 0.8, true)}
    ${put(KID({ armL: 'hold', holdL: 'teddy', expr: 'happy' }), 370, 296, 0.62, true)}
    ${bubble({ x: 10, y: 10, w: 220, h: 56, text: 'Vim conhecer vocês em casa, onde ele se sente seguro.', tail: [150, 112], size: 12 })}
  `);
  SCENES.nurseWave = () => scene(200, 310, put(NURSE({ armL: 'wave', expr: 'bigsmile' }), 100, 305, 1));
  // mini história da vacina (6 quadros)
  const nc = (inner) => scene(240, 170, inner);
  SCENES.v1 = () => nc(`${plainWall(240, 130, '#E8F8F5')}${floor(240, 130, 40, '#F2E394')}${door(150, 20, 56, 112)}${wallSign(150, 4, 'UBS', 56, 18)}${put(MOM({ expr: 'happy' }), 60, 166, 0.5)}${put(KID({ armR: 'hold', holdR: 'teddy', headphones: true, expr: 'happy' }), 108, 166, 0.42)}`);
  SCENES.v2 = () => nc(`${plainWall(240, 130, '#E8F8F5')}${floor(240, 130, 40, '#F2E394')}${waitingChairs(30, 130, 2, '#58D68D')}${put(MOM({ sit: true, expr: 'happy', armL: 'lap' }), 62, 134, 0.46)}${put(KID({ sit: true, headphones: true, armL: 'hold', holdL: 'teddy', expr: 'neutral' }), 136, 134, 0.4)}${at(ICON.mute(), 190, 20, 0.55)}`);
  SCENES.v3 = () => nc(`${plainWall(240, 130, '#E8F8F5')}${floor(240, 130, 40, '#F2E394')}${put(NURSE({ armL: 'wave', expr: 'bigsmile' }), 70, 166, 0.5)}${put(KID({ expr: 'happy', headphones: true, armR: 'hold', holdR: 'teddy' }), 180, 166, 0.46, true)}${bubble({ x: 6, y: 6, w: 110, h: 34, text: 'Oi! Eu sou a enfermeira.', tail: [70, 60], size: 10 })}`);
  SCENES.v4 = () => nc(`${plainWall(240, 130, '#E8F8F5')}${floor(240, 130, 40, '#F2E394')}${put(KID({ sit: true, headphones: true, sunglasses: true, armL: 'hold', holdL: 'teddy', armR: 'front', expr: 'happyclosed' }), 150, 140, 0.4)}${put(NURSE({ armR: 'show', holdR: 'syringe', gloves: true, expr: 'happy' }), 60, 166, 0.5)}${bubble({ x: 6, y: 6, w: 100, h: 34, text: '1, 2, 3… pronto!', tail: [60, 64], size: 11 })}`);
  SCENES.v5 = () => nc(`${plainWall(240, 130, '#E8F8F5')}${floor(240, 130, 40, '#F2E394')}${sparkles(200, 36)}${put(NURSE({ armR: 'show', holdR: 'sticker', expr: 'bigsmile' }), 70, 166, 0.5)}${put(KID({ armL: 'up', armR: 'hold', holdR: 'teddy', expr: 'bigsmile', headphones: true }), 180, 166, 0.46, true)}`);
  SCENES.v6 = () => nc(`${plainWall(240, 130, '#E8F8F5')}${floor(240, 130, 40, '#F2E394')}${door(170, 20, 56, 112)}${put(NURSE({ armL: 'wave', expr: 'bigsmile' }), 60, 166, 0.5)}${put(MOM({ expr: 'happy' }), 130, 166, 0.46)}${put(KID({ armL: 'wave', armR: 'hold', holdR: 'teddy', expr: 'bigsmile', headphones: true }), 112, 166, 0.4, true)}${bubble({ x: 6, y: 6, w: 100, h: 34, text: 'Tchau! Até a próxima.', tail: [60, 60], size: 10 })}`);


  // ======= HOSPITAL: EMERGÊNCIA E INTERNAÇÃO =======
  const DOC = (o = {}) => person(Object.assign({ skin: '#F7D6B9', hair: '#8D6E63', hairStyle: 'side', shirt: '#2E86C1', pants: '#2E86C1', coat: '#FFFFFF', sleeve: 'long', shoes: '#FFFFFF' }, o));
  ITEMS.oximeter = () => `<g><rect x="-14" y="-10" width="28" height="20" rx="5" fill="#2C3E50" ${S}/><rect x="-9" y="-6" width="18" height="8" rx="2" fill="#58D68D"/><circle cx="0" cy="6" r="2" fill="#E74C3C"/></g>`;
  ITEMS.scale = () => `<g><rect x="-30" y="-20" width="60" height="40" rx="6" fill="#FFFFFF" ${S}/><circle cx="-18" cy="-6" r="6" fill="#58D68D" ${S} stroke-width="2"/><circle cx="0" cy="-6" r="6" fill="#F7C21B" ${S} stroke-width="2"/><circle cx="18" cy="-6" r="6" fill="#E74C3C" ${S} stroke-width="2"/><path d="M-21 -5 q3 3 6 0 M-3 -6 h6 M15 -3 q3 -3 6 0" fill="none" ${S} stroke-width="2"/><rect x="-22" y="6" width="44" height="6" rx="3" fill="#BDC3C7"/></g>`;
  function hospBed(x, y, w = 220, color = '#AED6F1') {
    return `<g transform="translate(${x} ${y})">
      <rect x="0" y="-70" width="${w}" height="26" rx="6" fill="${color}" ${S}/><rect x="-10" y="-120" width="14" height="76" rx="4" fill="#5DADE2" ${S}/><rect x="${w - 4}" y="-104" width="14" height="60" rx="4" fill="#5DADE2" ${S}/>
      <rect x="12" y="-86" width="56" height="20" rx="8" fill="#FFFFFF" ${S}/>
      <rect x="0" y="-44" width="${w}" height="12" fill="#95A5A6" ${S}/>
      <rect x="30" y="-104" width="${w - 60}" height="8" rx="4" fill="#95A5A6" ${S}/><line x1="60" y1="-96" x2="60" y2="-72" ${S} stroke-width="4"/><line x1="${w - 60}" y1="-96" x2="${w - 60}" y2="-72" ${S} stroke-width="4"/>
      <rect x="16" y="-32" width="10" height="36" fill="#7F8C8D" ${S}/><rect x="${w - 26}" y="-32" width="10" height="36" fill="#7F8C8D" ${S}/><circle cx="21" cy="6" r="7" fill="#2C3E50" ${S}/><circle cx="${w - 21}" cy="6" r="7" fill="#2C3E50" ${S}/></g>`;
  }
  function ivPole(x, y) {
    return `<g transform="translate(${x} ${y})"><rect x="-3" y="-190" width="6" height="190" fill="#95A5A6" ${S}/><path d="M-26 0 L26 0 M-18 -8 L18 -8" fill="none" ${S} stroke-width="5"/><path d="M-30 -196 L30 -196" ${S} stroke-width="5"/><rect x="-36" y="-192" width="20" height="40" rx="5" fill="#D6EAF8" ${S}/><rect x="-32" y="-166" width="12" height="12" fill="#AED6F1"/><path d="M-26 -152 q0 60 20 90" fill="none" stroke="#5DADE2" stroke-width="3"/></g>`;
  }
  function monitor(x, y) {
    return `<g transform="translate(${x} ${y})"><rect x="-4" y="-80" width="8" height="80" fill="#95A5A6" ${S}/><rect x="-44" y="-140" width="88" height="64" rx="6" fill="#ECF0F1" ${S}/><rect x="-38" y="-134" width="76" height="46" rx="3" fill="#1C2833"/>
      <path d="M-34 -108 h12 l4 -10 l6 20 l6 -24 l6 14 h22" fill="none" stroke="#58D68D" stroke-width="2.5"/><path d="M-34 -96 h14 l4 -6 l4 8 l4 -6 h30" fill="none" stroke="#5DADE2" stroke-width="2"/>${htmlText(-38, -134, 76, 14, '98  ♥ 88', 8, 800, '#58D68D')}
      <circle cx="-20" cy="-72" r="0" /></g>`;
  }
  function oxygen(x, y) { return `<g transform="translate(${x} ${y})"><rect x="-14" y="-110" width="28" height="110" rx="10" fill="#58D68D" ${S}/><rect x="-6" y="-124" width="12" height="16" rx="3" fill="#7F8C8D" ${S}/><rect x="-8" y="-70" width="16" height="30" rx="3" fill="#FFFFFF" opacity=".8"/></g>`; }
  function hospWindowNight(x, y, w, h) { return `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="4" fill="#1F3A5F" ${S}/><line x1="${x + w / 2}" y1="${y}" x2="${x + w / 2}" y2="${y + h}" ${S}/><line x1="${x}" y1="${y + h / 2}" x2="${x + w}" y2="${y + h / 2}" ${S}/><circle cx="${x + w * 0.7}" cy="${y + h * 0.3}" r="${h * 0.12}" fill="#FFF6B0"/>${star(x + w * 0.25, y + h * 0.3, 4, '#FFF6B0')}${star(x + w * 0.4, y + h * 0.7, 3, '#FFF6B0')}`; }
  const HOSP = (extra = '', wall = '#EAF2F8') => `${plainWall(420, 232, wall)}${floor(420, 232, 68, '#D5DBDB')}<rect x="0" y="150" width="420" height="10" fill="#5DADE2" ${S}/>${extra}`;

  SCENES.h_cover = () => scene(420, 470, `
    ${plainWall(420, 332, '#EAF2F8')}${floor(420, 332, 138, '#D5DBDB')}<rect x="0" y="230" width="420" height="12" fill="#5DADE2" ${S}/>
    ${window_(296, 40, 96, 72)}
    ${wallSign(30, 150, 'Hospital', 110, 36)}
    ${hospBed(30, 330, 200)}${ivPole(250, 330)}${monitor(360, 330)}
    ${put(NURSE({ armL: 'wave', armR: 'hold', holdR: 'clipboard', expr: 'bigsmile' }), 310, 440, 1.0)}
    ${put(KID({ headphones: true, armL: 'hold', holdL: 'teddy', expr: 'happy' }), 140, 436, 0.82, true)}
  `, '', 'xMidYMax slice');
  SCENES.h_triagem = () => scene(420, 300, HOSP(`
    ${put(NURSE({ armR: 'show', holdR: 'scale', expr: 'happy' }), 110, 296, 0.8)}
    ${wallSign(8, 196, 'Classificação de risco', 150, 26)}
    ${put(MOM({ armL: 'hold', holdL: 'card', expr: 'worried' }), 290, 296, 0.78)}
    ${put(KID({ armR: 'hold', holdR: 'teddy', headphones: true, armL: 'chin', expr: 'worried' }), 372, 296, 0.64)}
    ${bubble({ x: 150, y: 10, w: 220, h: 60, text: 'Ele tem TEA? Vou marcar na ficha e já levo vocês para a sala calma. Me mostra na carinha: dói pouco, médio ou muito?', tail: [112, 110], size: 10.5 })}
  `));
  SCENES.h_box = () => scene(420, 300, HOSP(`
    ${monitor(60, 232)}${oxygen(130, 232)}
    ${hospBed(160, 232, 190, '#D6EAF8')}
    ${put(KID({ sit: true, headphones: true, sunglasses: true, armL: 'hold', holdL: 'teddy', armR: 'front', expr: 'neutral' }), 270, 236, 0.58)}
    ${put(DOC({ armR: 'show', holdR: 'oximeter', expr: 'happy' }), 110, 296, 0.8, false)}
    ${put(MOM({ expr: 'happy', armL: 'down' }), 392, 296, 0.56, true)}
    ${bubble({ x: 10, y: 10, w: 210, h: 56, text: 'Este é o dedinho de luz. Só aperta de leve. Primeiro na mamãe, depois em você.', tail: [110, 118], size: 11 })}
  `, '#FDFEFE'));
  SCENES.h_quarto = () => scene(420, 300, HOSP(`
    ${window_(300, 30, 100, 70)}
    ${hospBed(30, 232, 210)}${ivPole(262, 232)}
    ${put(KID({ sit: true, headphones: true, armL: 'hold', holdL: 'teddy', expr: 'happy' }), 150, 236, 0.58)}
    <rect x="330" y="110" width="80" height="100" rx="6" fill="#FFFFFF" ${S}/>${at(ICON.clock(), 338, 116, 0.4)}${at(ICON.tooth(), 366, 116, 0.4)}${at(ICON.toy(), 338, 144, 0.4)}${at(ICON.calendar(), 366, 144, 0.4)}${at(ICON.pause(), 338, 172, 0.4)}${at(ICON.home(), 366, 172, 0.4)}
    ${put(NURSE({ armR: 'point', expr: 'happy' }), 300, 296, 0.64)}
    ${bubble({ x: 120, y: 6, w: 170, h: 56, text: 'Este é o seu quadro do dia: remédio, lanche, brincar, visita, dormir.', tail: [300, 108], size: 10.5 })}
  `));
  SCENES.h_noite = () => scene(420, 300, `
    ${plainWall(420, 232, '#2C3E50')}${floor(420, 232, 68, '#34495E')}<rect x="0" y="150" width="420" height="10" fill="#1F3A5F" ${S}/>
    ${hospWindowNight(300, 30, 100, 70)}
    ${hospBed(30, 232, 210, '#5D6D7E')}
    ${put(KID({ sit: true, armL: 'hold', holdL: 'teddy', expr: 'happyclosed' }), 150, 236, 0.58)}
    ${zzz(190, 100)}
    ${waitingChairs(320, 232, 1, '#7D3C98')}${put(MOM({ sit: true, expr: 'happyclosed', armL: 'lap' }), 352, 238, 0.6)}
    <rect x="30" y="40" width="60" height="30" rx="6" fill="#F7C21B" opacity=".25"/><circle cx="60" cy="55" r="6" fill="#FFF6B0"/>
    ${at(ICON.mute(), 110, 36, 0.7)}${at(ICON.lampdim(), 160, 36, 0.7)}
  `);
  SCENES.h_cirurgia = () => scene(420, 300, HOSP(`
    ${wallSign(20, 24, 'Centro cirúrgico', 140, 28)}
    ${put(NURSE({ maskUp: true, gloves: true, armR: 'show', holdR: 'mask', expr: 'happy' }), 120, 296, 0.8)}
    ${put(KID({ armL: 'hold', holdL: 'teddy', armR: 'hold', holdR: 'card', headphones: true, expr: 'happy' }), 290, 296, 0.7)}
    ${put(MOM({ expr: 'happy' }), 380, 296, 0.6, true)}
    ${bubble({ x: 180, y: 10, w: 220, h: 56, text: 'Esta é a máscara do “ar com cheirinho”. Você escolhe o cheiro e segura o ursinho até dormir.', tail: [120, 110], size: 10.5 })}
  `, '#E8F8F5'));
  ITEMS.mask = () => `<g><path d="M-22 -8 Q0 -16 22 -8 L18 14 Q0 22 -18 14 Z" fill="#A8D8EA" ${S}/><path d="M-22 -6 q-10 -2 -12 8 M22 -6 q10 -2 12 8" fill="none" ${S}/></g>`;
  SCENES.h_alta = () => scene(420, 300, HOSP(`
    ${door(20, 70, 70, 162)}${wallSign(100, 30, 'Alta', 60, 28)}
    ${sparkles(330, 70)}
    ${put(NURSE({ armL: 'wave', armR: 'hold', holdR: 'clipboard', expr: 'bigsmile' }), 150, 296, 0.8)}
    ${put(MOM({ armR: 'hold', holdR: 'card', expr: 'bigsmile' }), 300, 296, 0.8, true)}
    ${put(KID({ armL: 'wave', armR: 'hold', holdR: 'gift', headphones: true, expr: 'bigsmile' }), 380, 296, 0.64, true)}
    ${bubble({ x: 160, y: 10, w: 240, h: 56, text: 'Aqui estão as orientações com figuras. Vocês foram incríveis. Tchau!', tail: [150, 112], size: 11 })}
  `));
  SCENES.h_crise = () => scene(420, 240, `
    ${plainWall(420, 180, '#FADBD8')}${floor(420, 180, 60, '#D5DBDB')}
    ${monitor(50, 180)}${htmlText(90, 20, 90, 30, 'BIP BIP!', 20, 800, '#C0392B')}${htmlText(290, 30, 110, 30, 'VRRR!', 20, 800, '#C0392B')}
    ${put(KID({ armL: 'ears', armR: 'ears', expr: 'scared' }), 210, 236, 0.74)}
    ${noteMusic(320, 90)}${noteMusic(130, 110)}
  `);
  SCENES.docWave = () => scene(200, 310, put(DOC({ armL: 'wave', expr: 'bigsmile' }), 100, 305, 1));
  // história social "Eu no hospital" (6 quadros)
  const hc = (inner) => scene(240, 170, inner);
  const HW = (x = '') => `${plainWall(240, 130, '#EAF2F8')}${floor(240, 130, 40, '#D5DBDB')}${x}`;
  SCENES.e1 = () => hc(HW(`${door(150, 20, 56, 112)}${wallSign(150, 4, 'Hospital', 60, 18)}${put(MOM({ expr: 'happy' }), 60, 166, 0.5)}${put(KID({ armR: 'hold', holdR: 'teddy', headphones: true, expr: 'neutral' }), 108, 166, 0.42)}`));
  SCENES.e2 = () => hc(HW(`${put(NURSE({ armR: 'show', holdR: 'scale', expr: 'happy' }), 70, 166, 0.5)}${put(KID({ expr: 'neutral', headphones: true, armR: 'hold', holdR: 'teddy' }), 180, 166, 0.46, true)}${bubble({ x: 6, y: 6, w: 110, h: 34, text: 'Dói pouco, médio ou muito?', tail: [70, 60], size: 9.5 })}`));
  SCENES.e3 = () => hc(HW(`${at(`<g transform="scale(.5)">${hospBed(0, 0, 220, '#D6EAF8')}</g>`, 90, 130, 1)}${put(KID({ sit: true, headphones: true, armL: 'hold', holdL: 'teddy', expr: 'happy' }), 150, 136, 0.36)}${put(DOC({ armR: 'show', holdR: 'oximeter', expr: 'happy' }), 50, 166, 0.48)}`));
  SCENES.e4 = () => hc(HW(`${at(`<g transform="scale(.5)">${hospBed(0, 0, 220)}</g>`, 70, 130, 1)}${at(`<g transform="scale(.5)">${ivPole(0, 0)}</g>`, 190, 130, 1)}${put(KID({ sit: true, headphones: true, armL: 'hold', holdL: 'teddy', expr: 'happy' }), 130, 136, 0.36)}<rect x="200" y="20" width="34" height="46" rx="4" fill="#fff" ${S} stroke-width="2"/>${at(ICON.clock(), 204, 24, 0.2)}${at(ICON.toy(), 218, 24, 0.2)}${at(ICON.calendar(), 204, 40, 0.2)}${at(ICON.pause(), 218, 40, 0.2)}`));
  SCENES.e5 = () => hc(`${plainWall(240, 130, '#2C3E50')}${floor(240, 130, 40, '#34495E')}${hospWindowNight(170, 16, 56, 40)}${at(`<g transform="scale(.5)">${hospBed(0, 0, 220, '#5D6D7E')}</g>`, 40, 130, 1)}${put(KID({ sit: true, armL: 'hold', holdL: 'teddy', expr: 'happyclosed' }), 100, 136, 0.36)}${zzz(120, 50)}${put(MOM({ sit: true, expr: 'happyclosed', armL: 'lap' }), 200, 136, 0.38)}`);
  SCENES.e6 = () => hc(HW(`${door(170, 20, 56, 112)}${sparkles(40, 30)}${put(NURSE({ armL: 'wave', expr: 'bigsmile' }), 60, 166, 0.5)}${put(MOM({ expr: 'happy' }), 130, 166, 0.46)}${put(KID({ armL: 'wave', armR: 'hold', holdR: 'gift', expr: 'bigsmile', headphones: true }), 112, 166, 0.4, true)}${bubble({ x: 6, y: 6, w: 100, h: 34, text: 'Vou para casa!', tail: [112, 60], size: 10 })}`));


  // ======= CENAS E OBJETOS EXTRAS (cartilhas da criança: UBS e hospital) =======
  SCENES.n_termo = () => scene(420, 300, UBS(`
    ${put(KID({ sit: true, headphones: true, armL: 'hold', holdL: 'teddy', expr: 'happy' }), 300, 240, 0.64)}
    <rect x="250" y="206" width="100" height="26" rx="6" fill="#5DADE2" ${S}/><rect x="258" y="232" width="8" height="50" fill="#7F8C8D" ${S}/><rect x="334" y="232" width="8" height="50" fill="#7F8C8D" ${S}/>
    ${put(NURSE({ armR: 'show', holdR: 'thermo', expr: 'happy' }), 140, 296, 0.8)}
    ${bubble({ x: 10, y: 10, w: 210, h: 56, text: 'O termômetro fica na testa ou embaixo do braço. Faz “bip” quando termina.', tail: [140, 118], size: 11 })}
  `));
  SCENES.n_balanca = () => scene(420, 300, UBS(`
    ${scale(300, 232)}
    ${put(KID({ headphones: true, armL: 'hold', holdL: 'teddy', expr: 'happy' }), 300, 296, 0.7)}
    ${put(NURSE({ armR: 'point', expr: 'happy' }), 130, 296, 0.8)}
    ${bubble({ x: 10, y: 10, w: 200, h: 56, text: 'Sobe na balança e fica paradinho. Os números aparecem e pronto.', tail: [130, 118], size: 11 })}
  `));
  SCENES.n_oximetro = () => scene(420, 300, UBS(`
    ${put(KID({ sit: true, headphones: true, armL: 'hold', holdL: 'teddy', expr: 'happy' }), 300, 240, 0.64)}
    <rect x="250" y="206" width="100" height="26" rx="6" fill="#5DADE2" ${S}/><rect x="258" y="232" width="8" height="50" fill="#7F8C8D" ${S}/><rect x="334" y="232" width="8" height="50" fill="#7F8C8D" ${S}/>
    ${put(NURSE({ armR: 'show', holdR: 'oximeter', expr: 'happy' }), 140, 296, 0.8)}
    ${bubble({ x: 10, y: 10, w: 210, h: 56, text: 'O dedinho de luz só aperta de leve e acende vermelho. Não dói nada.', tail: [140, 118], size: 11 })}
  `));
  SCENES.n_remedio = () => scene(420, 300, UBS(`
    ${put(KID({ sit: true, headphones: true, armL: 'hold', holdL: 'teddy', expr: 'open' }), 300, 240, 0.64)}
    <rect x="250" y="206" width="100" height="26" rx="6" fill="#5DADE2" ${S}/><rect x="258" y="232" width="8" height="50" fill="#7F8C8D" ${S}/><rect x="334" y="232" width="8" height="50" fill="#7F8C8D" ${S}/>
    ${put(NURSE({ armR: 'show', holdR: 'cup', expr: 'happy' }), 140, 296, 0.8)}
    ${bubble({ x: 10, y: 10, w: 210, h: 56, text: 'O remédio vem no copinho. Tem gosto de fruta e dá para beber de uma vez.', tail: [140, 118], size: 11 })}
  `));
  SCENES.h_pulseira = () => scene(420, 300, HOSP(`
    ${put(KID({ armR: 'show', headphones: true, armL: 'hold', holdL: 'teddy', expr: 'happy' }), 290, 296, 0.72)}
    ${put(NURSE({ armR: 'show', holdR: 'bandage', expr: 'happy' }), 120, 296, 0.8)}
    ${bubble({ x: 10, y: 10, w: 210, h: 56, text: 'Esta pulseira tem o seu nome. Todo mundo vai saber quem você é.', tail: [120, 118], size: 11 })}
  `));
  SCENES.h_raiox = () => scene(420, 300, HOSP(`
    <rect x="240" y="60" width="150" height="172" rx="8" fill="#5D6D7E" ${S}/><rect x="256" y="76" width="118" height="100" rx="4" fill="#1C2833"/><rect x="300" y="40" width="30" height="24" fill="#95A5A6" ${S}/><rect x="312" y="0" width="8" height="42" fill="#95A5A6" ${S}/>
    ${put(KID({ sit: true, headphones: true, armL: 'hold', holdL: 'teddy', expr: 'happy' }), 314, 240, 0.5)}
    ${put(NURSE({ armR: 'point', expr: 'happy' }), 110, 296, 0.8)}
    ${bubble({ x: 10, y: 10, w: 200, h: 56, text: 'Esta máquina tira uma foto de dentro do corpo. Só precisa ficar paradinho e contar até três.', tail: [110, 118], size: 10.5 })}
  `, '#FDFEFE'));
  SCENES.h_comida = () => scene(420, 300, HOSP(`
    ${hospBed(30, 232, 210)}
    ${put(KID({ sit: true, headphones: true, armR: 'hold', holdR: 'cup', expr: 'happy' }), 150, 236, 0.58)}
    <rect x="90" y="160" width="100" height="10" rx="3" fill="#D7A86E" ${S}/><rect x="100" y="146" width="36" height="14" rx="3" fill="#F7C21B" ${S}/><circle cx="160" cy="152" r="9" fill="#E74C3C" ${S}/>
    ${put(MOM({ armR: 'point', expr: 'happy' }), 320, 296, 0.78)}
    ${bubble({ x: 190, y: 10, w: 220, h: 56, text: 'Trouxe a sua comida preferida de casa. A enfermeira deixou.', tail: [320, 112], size: 11 })}
  `));
  SCENES.h_visita = () => scene(420, 300, HOSP(`
    ${hospBed(30, 232, 210)}
    ${put(KID({ sit: true, headphones: true, armL: 'hold', holdL: 'teddy', armR: 'wave', expr: 'bigsmile' }), 150, 236, 0.58)}
    ${put(ASSIST({ armL: 'wave', expr: 'bigsmile' }), 330, 296, 0.78)}
    ${bubble({ x: 190, y: 10, w: 220, h: 56, text: 'Oi! Eu sou a técnica do plantão da tarde. Vim me apresentar.', tail: [330, 112], size: 11 })}
  `));
  SCENES.p_nurse = () => scene(200, 310, put(NURSE({ armL: 'wave', expr: 'bigsmile' }), 100, 305, 1));
  SCENES.p_nurse_mask = () => scene(200, 310, put(NURSE({ maskUp: true, gloves: true, armL: 'wave', expr: 'happy' }), 100, 305, 1));
  SCENES.p_tech = () => scene(200, 310, put(ASSIST({ armL: 'wave', expr: 'bigsmile' }), 100, 305, 1));
  SCENES.p_doc = () => scene(200, 310, put(DOC({ armL: 'wave', expr: 'bigsmile' }), 100, 305, 1));
  SCENES.p_acs = () => scene(200, 310, put(person({ skin: '#8D5B3A', hair: '#1C1C1C', hairStyle: 'cap', shirt: '#58D68D', pants: '#2C3E50', armL: 'wave', armR: 'hold', holdR: 'clipboard', expr: 'bigsmile' }), 100, 305, 1));
  SCENES.o_thermo = () => OBJ(at(ITEMS.thermo(), 60, 70, 1.3));
  SCENES.o_cuffItem = () => OBJ(at(ITEMS.cuff(), 60, 60, 1.6));
  SCENES.o_scale = () => OBJ(`<g transform="translate(20 10) scale(.55)">${scale(80, 190)}</g>`);
  SCENES.o_oximeter = () => OBJ(at(ITEMS.oximeter(), 60, 60, 2.4));
  SCENES.o_syringe = () => OBJ(at(ITEMS.syringe(), 60, 66, 1.3));
  SCENES.o_bandageItem = () => OBJ(at(ITEMS.bandage(), 60, 60, 1.6));
  SCENES.o_garrote = () => OBJ(`<path d="M20 70 Q60 30 100 70" fill="none" stroke="#5DADE2" stroke-width="14" stroke-linecap="round"/><path d="M20 70 Q60 30 100 70" fill="none" ${S} stroke-width="3" stroke-dasharray="0" opacity=".0"/><rect x="48" y="40" width="24" height="18" rx="4" fill="#2C3E50" ${S}/>`);
  SCENES.o_sticker = () => OBJ(`${star(60, 60, 34, '#F7C21B')}<circle cx="48" cy="52" r="4" fill="${OUT}"/><circle cx="72" cy="52" r="4" fill="${OUT}"/><path d="M48 68 Q60 78 72 68" fill="none" ${S}/>`);
  SCENES.o_fridge = () => OBJ(`<g transform="translate(25 10) scale(.66)">${vaccineFridge(0, 150)}</g>`);
  SCENES.o_bed = () => OBJ(`<g transform="translate(6 10) scale(.46)">${hospBed(0, 170, 220)}</g>`);
  SCENES.o_monitor = () => OBJ(`<g transform="translate(10 0) scale(.7)">${monitor(72, 160)}</g>`);
  SCENES.o_iv = () => OBJ(`<g transform="translate(0 0) scale(.5)">${ivPole(120, 220)}</g>`);
  SCENES.o_bracelet = () => OBJ(`<ellipse cx="60" cy="60" rx="40" ry="26" fill="none" stroke="#FFFFFF" stroke-width="14"/><ellipse cx="60" cy="60" rx="40" ry="26" fill="none" ${S}/><ellipse cx="60" cy="60" rx="26" ry="12" fill="none" ${S}/><rect x="40" y="52" width="40" height="16" rx="3" fill="#FFFFFF" ${S} stroke-width="2"/><line x1="46" y1="58" x2="74" y2="58" ${S} stroke-width="2"/><line x1="46" y1="63" x2="66" y2="63" ${S} stroke-width="2"/>`);
  SCENES.o_dayboard = () => OBJ(`<rect x="18" y="14" width="84" height="92" rx="6" fill="#FFFFFF" ${S}/>${at(ICON.clock(), 24, 20, 0.5)}${at(ICON.toy(), 62, 20, 0.5)}${at(ICON.calendar(), 24, 50, 0.5)}${at(ICON.pause(), 62, 50, 0.5)}${at(ICON.home(), 24, 80, 0.35)}${at(ICON.tooth(), 62, 80, 0.35)}`);
  SCENES.o_medcup = () => OBJ(at(ITEMS.cup(), 60, 60, 2.4));
  SCENES.o_xray = () => OBJ(`<rect x="20" y="20" width="80" height="80" rx="6" fill="#5D6D7E" ${S}/><rect x="30" y="30" width="60" height="50" rx="3" fill="#1C2833"/><path d="M60 40 v30 M48 48 h24 M50 58 h20 M52 68 h16" stroke="#ECF0F1" stroke-width="4" stroke-linecap="round"/>`);
  SCENES.o_painfaces = () => OBJ(at(ITEMS.scale(), 60, 60, 1.6));
  SCENES.o_anestmask = () => OBJ(at(ITEMS.mask(), 60, 60, 2.2));
  SCENES.o_stetho = () => OBJ(`<path d="M40 20 q0 40 20 46 q20 -6 20 -46" fill="none" ${S} stroke-width="5"/><path d="M60 66 v16 q0 14 14 14 h6" fill="none" ${S} stroke-width="5"/><circle cx="88" cy="96" r="10" fill="#95A5A6" ${S}/><rect x="36" y="12" width="8" height="12" rx="3" fill="#2C3E50"/><rect x="76" y="12" width="8" height="12" rx="3" fill="#2C3E50"/>`);
  SCENES.n_stetho = () => scene(420, 300, UBS(`
    ${put(KID({ sit: true, headphones: true, armL: 'hold', holdL: 'teddy', expr: 'happy' }), 300, 240, 0.64)}
    <rect x="250" y="206" width="100" height="26" rx="6" fill="#5DADE2" ${S}/><rect x="258" y="232" width="8" height="50" fill="#7F8C8D" ${S}/><rect x="334" y="232" width="8" height="50" fill="#7F8C8D" ${S}/>
    ${put(NURSE({ armR: 'point', expr: 'happy' }), 140, 296, 0.8)}
    ${at(`<path d="M-20 -30 q0 40 20 46 q20 -6 20 -46" fill="none" ${S} stroke-width="5"/><path d="M0 16 v16 q0 14 14 14 h6" fill="none" ${S} stroke-width="5"/><circle cx="28" cy="46" r="10" fill="#95A5A6" ${S}/>`, 196, 150, 1)}
    ${bubble({ x: 10, y: 10, w: 210, h: 56, text: 'O “ouvidor” escuta o coração. É frio no começo e depois esquenta.', tail: [140, 118], size: 11 })}
  `));


  // ======= DIDÁTICA APLICADA À ENFERMAGEM =======
  const PROF = (o = {}) => person(Object.assign({ skin: '#C58C5A', hair: '#1C1C1C', hairStyle: 'cap', shirt: '#FFFFFF', pants: '#2C3E50', coat: '#5DADE2', sleeve: 'long', shoes: '#2C3E50', glasses: true }, o));
  const STU1 = (o = {}) => person(Object.assign({ skin: '#F7D6B9', hair: '#E67E22', hairStyle: 'side', shirt: '#FFFFFF', pants: '#5B5F97', coat: null, sleeve: 'short' }, o));
  const STU2 = (o = {}) => person(Object.assign({ skin: '#8D5B3A', hair: '#1C1C1C', hairStyle: 'bun', shirt: '#FFFFFF', pants: '#2C3E50', sleeve: 'short' }, o));
  const STU3 = (o = {}) => person(Object.assign({ skin: '#F2C9A6', hair: '#7A3F1E', hairStyle: 'long', shirt: '#FFFFFF', pants: '#6B6B6B', sleeve: 'short' }, o));
  const ELDER = (o = {}) => person(Object.assign({ skin: '#F2C9A6', hair: '#BDC3C7', hairStyle: 'bald', shirt: '#9B59B6', pants: '#6B6B6B', glasses: true }, o));
  ITEMS.insulin = () => `<g transform="rotate(-30)"><rect x="-5" y="-36" width="10" height="56" rx="4" fill="#5DADE2" ${S}/><rect x="-6" y="-44" width="12" height="10" rx="2" fill="#2C3E50" ${S}/><rect x="-3" y="-10" width="6" height="22" fill="#ECF0F1"/><line x1="0" y1="20" x2="0" y2="30" ${S} stroke-width="2"/></g>`;
  ITEMS.folder = () => `<g transform="rotate(-8)"><rect x="-24" y="-18" width="48" height="36" rx="3" fill="#F7C21B" ${S}/><rect x="-18" y="-12" width="36" height="4" rx="2" fill="#FFFFFF"/><rect x="-18" y="-4" width="28" height="4" rx="2" fill="#FFFFFF"/><rect x="-18" y="4" width="32" height="4" rx="2" fill="#FFFFFF"/></g>`;
  ITEMS.marker = () => `<g transform="rotate(-35)"><rect x="-4" y="-34" width="8" height="40" rx="3" fill="#E74C3C" ${S}/><rect x="-3" y="-42" width="6" height="8" fill="#2C3E50"/></g>`;
  function whiteboard(x, y, w, h, inner = '') {
    return `<g transform="translate(${x} ${y})"><rect x="-6" y="-6" width="${w + 12}" height="${h + 12}" rx="6" fill="#95A5A6" ${S}/><rect x="0" y="0" width="${w}" height="${h}" fill="#FFFFFF" ${S}/>${inner}</g>`;
  }
  function deskRow(x, y, n = 3, gap = 110) {
    let o = '';
    for (let i = 0; i < n; i++) { const dx = x + i * gap; o += `<rect x="${dx}" y="${y - 40}" width="80" height="12" rx="3" fill="#D7A86E" ${S}/><rect x="${dx + 6}" y="${y - 28}" width="8" height="30" fill="#A0522D" ${S}/><rect x="${dx + 66}" y="${y - 28}" width="8" height="30" fill="#A0522D" ${S}/>`; }
    return o;
  }
  function infusionPump(x, y) {
    return `<g transform="translate(${x} ${y})"><rect x="-4" y="-150" width="8" height="150" fill="#95A5A6" ${S}/><path d="M-26 0 L26 0" ${S} stroke-width="6"/><rect x="-36" y="-130" width="72" height="54" rx="6" fill="#ECF0F1" ${S}/><rect x="-28" y="-122" width="56" height="22" rx="2" fill="#2C3E50"/>${htmlText(-28, -122, 56, 22, '50 mL/h', 9, 800, '#58D68D')}<circle cx="-16" cy="-88" r="4" fill="#58D68D" ${S} stroke-width="2"/><circle cx="0" cy="-88" r="4" fill="#F7C21B" ${S} stroke-width="2"/><circle cx="16" cy="-88" r="4" fill="#E74C3C" ${S} stroke-width="2"/><rect x="-14" y="-186" width="16" height="34" rx="4" fill="#D6EAF8" ${S}/></g>`;
  }
  function manikin(x, y) {
    return `<g transform="translate(${x} ${y})">${hospBed(0, 0, 200, '#D6EAF8')}<ellipse cx="50" cy="-82" rx="18" ry="16" fill="#E8D5C4" ${S}/><rect x="66" y="-92" width="100" height="26" rx="10" fill="#E8D5C4" ${S}/><rect x="70" y="-90" width="60" height="22" rx="6" fill="#5DADE2" ${S} stroke-width="2"/></g>`;
  }
  const CLASS = (extra = '') => `${plainWall(420, 232, '#FDF2E9')}${floor(420, 232, 68, '#D7A86E')}<rect x="0" y="150" width="420" height="8" fill="#F5B041" ${S}/>${extra}`;

  SCENES.d_cover = () => scene(420, 470, `
    ${plainWall(420, 332, '#FDF2E9')}${floor(420, 332, 138, '#D7A86E')}<rect x="0" y="230" width="420" height="10" fill="#F5B041" ${S}/>
    ${whiteboard(40, 40, 230, 130, `${htmlText(6, 6, 218, 40, 'Para quê? O quê? Como? Como avaliar?', 13, 800, '#2E86C1', 'center', 'Baloo 2')}<rect x="20" y="60" width="190" height="8" rx="4" fill="#BDC3C7"/><rect x="20" y="78" width="150" height="8" rx="4" fill="#BDC3C7"/><rect x="20" y="96" width="170" height="8" rx="4" fill="#BDC3C7"/>`)}
    ${window_(300, 40, 96, 72)}
    ${put(PROF({ armL: 'point', armR: 'hold', holdR: 'marker', expr: 'bigsmile' }), 310, 440, 1.0)}
    ${deskRow(30, 330, 2, 120)}
    ${put(STU1({ sit: true, expr: 'happy', armL: 'lap' }), 70, 338, 0.62)}
    ${put(STU2({ sit: true, expr: 'happy', armR: 'hold', holdR: 'pen' }), 190, 338, 0.62)}
  `, '', 'xMidYMax slice');
  SCENES.d_tres = () => scene(420, 300, `
    ${plainWall(140, 232, '#E8F8F5')}<rect x="140" y="0" width="140" height="232" fill="#EAF2F8"/><rect x="280" y="0" width="140" height="232" fill="#FDF2E9"/>${floor(420, 232, 68, '#F2E394')}
    <line x1="140" y1="0" x2="140" y2="300" ${S} stroke-dasharray="8 6"/><line x1="280" y1="0" x2="280" y2="300" ${S} stroke-dasharray="8 6"/>
    ${put(NURSE({ armR: 'show', holdR: 'insulin', expr: 'happy' }), 46, 296, 0.56)}${put(ELDER({ sit: true, expr: 'happy', armL: 'lap' }), 104, 250, 0.46)}
    ${put(NURSE({ armR: 'point', expr: 'happy' }), 178, 296, 0.56)}${put(ASSIST({ expr: 'happy' }), 246, 296, 0.5)}${at(`<g transform="scale(.5)">${infusionPump(0, 0)}</g>`, 222, 232, 1)}
    ${put(NURSE({ armL: 'wave', expr: 'bigsmile' }), 312, 296, 0.56)}${put(MOM({ sit: true, expr: 'happy', armL: 'lap' }), 362, 250, 0.42)}${put(STU3({ sit: true, expr: 'happy' }), 400, 250, 0.42)}
    ${htmlText(4, 8, 132, 30, 'Paciente', 12, 800, OUT, 'center', 'Baloo 2')}${htmlText(144, 8, 132, 30, 'Equipe', 12, 800, OUT, 'center', 'Baloo 2')}${htmlText(284, 8, 132, 30, 'Comunidade', 12, 800, OUT, 'center', 'Baloo 2')}
  `);
  SCENES.d_joao = () => scene(420, 300, HOSP(`
    ${put(NURSE({ armR: 'show', holdR: 'folder', expr: 'happy' }), 110, 296, 0.8)}
    ${put(ELDER({ armL: 'down', expr: 'neutral' }), 300, 296, 0.8)}
    ${bubble({ x: 10, y: 10, w: 150, h: 46, text: 'Entendeu?', tail: [110, 118], size: 13 })}
    ${bubble({ x: 230, y: 10, w: 120, h: 46, text: 'Sim…', tail: [300, 118], size: 13 })}
    ${bubble({ x: 250, y: 70, w: 160, h: 60, text: 'Duas semanas depois: dose dobrada e sangramento.', kind: 'thought', size: 10 })}
  `));
  SCENES.d_teachback = () => scene(420, 300, HOSP(`
    ${put(NURSE({ armR: 'point', expr: 'happy' }), 110, 296, 0.8)}
    ${put(ELDER({ armR: 'show', holdR: 'folder', expr: 'happy' }), 300, 296, 0.8)}
    ${bubble({ x: 10, y: 10, w: 200, h: 60, text: 'Me explique com as suas palavras: o que o senhor faz se esquecer uma dose?', tail: [110, 118], size: 10.5 })}
    ${bubble({ x: 230, y: 10, w: 180, h: 60, text: 'Não tomo em dobro. Tomo a próxima no horário e anoto aqui.', tail: [300, 118], size: 10.5 })}
  `));
  SCENES.d_bomba = () => scene(420, 300, HOSP(`
    ${infusionPump(330, 232)}
    ${put(NURSE({ armR: 'point', expr: 'happy' }), 110, 296, 0.8)}
    ${put(ASSIST({ armL: 'hold', expr: 'happy' }), 230, 296, 0.74)}
    ${put(STU2({ expr: 'happy', shirt: '#5DADE2', coat: '#DDF3FF', sleeve: 'long' }), 300, 296, 0.66)}
    ${bubble({ x: 10, y: 10, w: 220, h: 60, text: 'Semana passada tivemos um quase-erro de dose. Como vocês resolveriam? Depois, cada um programa a bomba.', tail: [110, 118], size: 10 })}
  `));
  SCENES.d_roda = () => scene(420, 300, UBS(`
    ${waitingChairs(20, 232, 5, '#58D68D')}
    ${put(NURSE({ sit: true, expr: 'happy', armR: 'point' }), 52, 238, 0.56)}
    ${put(MOM({ sit: true, expr: 'happy', armL: 'lap' }), 130, 238, 0.56)}
    ${put(ELDER({ sit: true, expr: 'happy' }), 208, 238, 0.56)}
    ${put(STU3({ sit: true, expr: 'happy', shirt: '#E74C3C' }), 286, 238, 0.56)}
    ${put(STU2({ sit: true, expr: 'happy', shirt: '#F7C21B' }), 364, 238, 0.56)}
    ${bubble({ x: 10, y: 10, w: 200, h: 56, text: 'O que vocês fazem quando a pressão “não dá sintoma”?', tail: [52, 120], size: 11 })}
    ${bubble({ x: 230, y: 10, w: 180, h: 56, text: 'Eu paro o remédio. Pressão é do nervoso, passa.', tail: [208, 120], size: 10.5 })}
  `));
  SCENES.d_simulacao = () => scene(420, 300, HOSP(`
    ${manikin(30, 232)}${monitor(260, 232)}
    ${put(STU1({ armR: 'front', expr: 'worried', coat: '#DDF3FF', sleeve: 'long' }), 150, 296, 0.7)}
    ${put(STU2({ armL: 'hold', holdL: 'clipboard', expr: 'neutral', coat: '#DDF3FF', sleeve: 'long' }), 240, 296, 0.66)}
    ${put(PROF({ armL: 'hold', holdL: 'clipboard', expr: 'happy' }), 360, 296, 0.76)}
    ${wallSign(20, 24, 'Briefing → Cenário → Debriefing', 210, 28)}
  `, '#FDFEFE'));
  SCENES.d_debrief = () => scene(420, 300, CLASS(`
    ${waitingChairs(40, 232, 4, '#5DADE2')}
    ${put(PROF({ sit: true, expr: 'happy', armR: 'point' }), 72, 238, 0.56)}
    ${put(STU1({ sit: true, expr: 'happy' }), 150, 238, 0.56)}
    ${put(STU2({ sit: true, expr: 'happy' }), 228, 238, 0.56)}
    ${put(STU3({ sit: true, expr: 'happy' }), 306, 238, 0.56)}
    ${bubble({ x: 10, y: 10, w: 230, h: 60, text: 'O que vocês fizeram? Por quê? O que sentiram? O que fariam diferente?', tail: [72, 120], size: 11 })}
    ${wallSign(280, 30, 'Debriefing', 110, 28)}
  `));
  SCENES.d_maos = () => scene(420, 300, HOSP(`
    <rect x="290" y="150" width="110" height="82" rx="6" fill="#49B9A9" ${S}/><ellipse cx="345" cy="150" rx="46" ry="12" fill="#A9DFD8" ${S}/><rect x="340" y="104" width="10" height="42" fill="#95A5A6" ${S}/>
    ${wallSign(20, 24, '5 momentos', 100, 28)}
    ${put(NURSE({ armL: 'show', armR: 'show', expr: 'happy' }), 120, 296, 0.8)}
    ${put(MOM({ armL: 'show', armR: 'show', expr: 'happy' }), 250, 296, 0.78)}
    ${bubble({ x: 140, y: 10, w: 240, h: 56, text: 'Agora a senhora faz, e eu vou marcando no checklist.', tail: [120, 118], size: 11 })}
  `));
  SCENES.d_prova = () => scene(420, 300, CLASS(`
    ${deskRow(60, 232, 2, 150)}
    ${put(STU1({ sit: true, expr: 'neutral', armR: 'hold', holdR: 'pen' }), 100, 238, 0.62)}
    ${put(STU3({ sit: true, expr: 'happy', armR: 'hold', holdR: 'pen' }), 250, 238, 0.62)}
    ${put(PROF({ armR: 'hold', holdR: 'clipboard', expr: 'happy' }), 360, 296, 0.76)}
    ${bubble({ x: 150, y: 10, w: 250, h: 60, text: 'Você acertou a técnica. Faltou o tempo de secagem. Na próxima, conte até 20 em voz alta.', tail: [360, 118], size: 10.5 })}
  `));
  SCENES.d_tradicional = () => scene(420, 240, CLASS(`
    ${whiteboard(30, 20, 150, 90, `<rect x="12" y="14" width="120" height="6" rx="3" fill="#BDC3C7"/><rect x="12" y="30" width="100" height="6" rx="3" fill="#BDC3C7"/><rect x="12" y="46" width="124" height="6" rx="3" fill="#BDC3C7"/><rect x="12" y="62" width="90" height="6" rx="3" fill="#BDC3C7"/>`)}
    ${put(PROF({ armL: 'point', expr: 'neutral' }), 230, 236, 0.64)}
    ${deskRow(270, 180, 1, 0)}${put(STU1({ sit: true, expr: 'happyclosed' }), 310, 184, 0.5)}${zzz(330, 80)}
    ${htmlText(290, 20, 120, 24, 'Tradicional', 12, 800, OUT, 'center', 'Baloo 2')}
  `).replace('floor(420, 232', 'floor(420, 180'));
  SCENES.d_ativa = () => scene(420, 240, `
    ${plainWall(420, 180, '#E8F8F5')}${floor(420, 180, 60, '#F2E394')}
    <circle cx="210" cy="150" r="60" fill="#FFF6B0" ${S}/>${htmlText(160, 130, 100, 40, 'PROBLEMA', 12, 800, OUT, 'center', 'Baloo 2')}
    ${put(STU1({ expr: 'happy', armR: 'point' }), 110, 236, 0.56)}${put(STU2({ expr: 'happy', armL: 'point' }), 310, 236, 0.56)}${put(PROF({ expr: 'happy' }), 210, 110, 0.4)}
    ${htmlText(290, 10, 120, 24, 'Metodologia ativa', 12, 800, OUT, 'center', 'Baloo 2')}
  `);
  SCENES.profWave = () => scene(200, 310, put(PROF({ armL: 'wave', armR: 'hold', holdR: 'marker', expr: 'bigsmile' }), 100, 305, 1));
  SCENES.studentsWave = () => scene(260, 310, put(STU1({ armL: 'wave', expr: 'bigsmile' }), 80, 305, 0.9) + put(STU2({ armR: 'wave', expr: 'bigsmile', armL: 'hold', holdL: 'clipboard' }), 190, 305, 0.9));


  // ======= BIOFÍSICA APLICADA À SAÚDE =======
  function beaker(x, y, w, h, color, label, inner = '') {
    return `<g transform="translate(${x} ${y})"><path d="M0 0 L0 ${h} Q0 ${h + 10} 10 ${h + 10} L${w - 10} ${h + 10} Q${w} ${h + 10} ${w} ${h} L${w} 0" fill="${color}" ${S}/><rect x="-6" y="-8" width="${w + 12}" height="10" rx="3" fill="#ECF0F1" ${S}/>${inner}${htmlText(0, h + 14, w, 22, label, 11, 800, OUT, 'center', 'Baloo 2')}</g>`;
  }
  function rbc(x, y, rx, ry, expr = 'happy', color = '#E74C3C') {
    const face = expr === 'happy' ? `<path d="M${x - 8} ${y + 4} Q${x} ${y + 12} ${x + 8} ${y + 4}" fill="none" ${S}/>` : expr === 'sad' ? `<path d="M${x - 8} ${y + 10} Q${x} ${y + 2} ${x + 8} ${y + 10}" fill="none" ${S}/>` : `<ellipse cx="${x}" cy="${y + 8}" rx="5" ry="6" fill="#C0392B" ${S}/>`;
    return `<ellipse cx="${x}" cy="${y}" rx="${rx}" ry="${ry}" fill="${color}" ${S}/><ellipse cx="${x}" cy="${y}" rx="${rx * 0.45}" ry="${ry * 0.4}" fill="#C0392B" opacity=".35"/><circle cx="${x - 7}" cy="${y - 4}" r="2.5" fill="${OUT}"/><circle cx="${x + 7}" cy="${y - 4}" r="2.5" fill="${OUT}"/>${face}`;
  }
  const arrow = (x1, y1, x2, y2, color = '#2E86C1') => `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${color}" stroke-width="4" stroke-linecap="round"/><polygon points="${x2},${y2} ${x2 - 10 * Math.cos(Math.atan2(y2 - y1, x2 - x1) - .5)},${y2 - 10 * Math.sin(Math.atan2(y2 - y1, x2 - x1) - .5)} ${x2 - 10 * Math.cos(Math.atan2(y2 - y1, x2 - x1) + .5)},${y2 - 10 * Math.sin(Math.atan2(y2 - y1, x2 - x1) + .5)}" fill="${color}"/>`;

  SCENES.b_cover = () => scene(420, 470, `
    ${plainWall(420, 332, '#E8F6F3')}${floor(420, 332, 138, '#D5DBDB')}<rect x="0" y="230" width="420" height="10" fill="#1ABC9C" ${S}/>
    ${whiteboard(30, 36, 220, 120, `${htmlText(6, 4, 208, 30, 'Q = ΔP / R', 18, 800, '#2E86C1', 'center', 'Baloo 2')}${htmlText(6, 36, 208, 26, 'pH = −log[H⁺]', 14, 800, '#C0392B', 'center', 'Baloo 2')}${htmlText(6, 64, 208, 26, 'P × V = constante', 14, 800, '#27AE60', 'center', 'Baloo 2')}${htmlText(6, 90, 208, 26, '3 Na⁺ fora · 2 K⁺ dentro', 12, 800, '#8E44AD', 'center', 'Baloo 2')}`)}
    ${window_(300, 40, 96, 72)}
    ${ivPole(300, 330)}${monitor(380, 330)}
    ${put(PROF({ armL: 'point', armR: 'hold', holdR: 'marker', expr: 'bigsmile', coat: '#1ABC9C' }), 300, 440, 1.0)}
    ${put(STU2({ armL: 'hold', holdL: 'clipboard', expr: 'happy' }), 110, 436, 0.78)}
    ${put(STU1({ armR: 'show', holdR: 'cup', expr: 'happy' }), 200, 436, 0.78)}
  `, '', 'xMidYMax slice');
  SCENES.b_tonicidade = () => scene(420, 240, `
    <rect width="420" height="240" fill="#FFFFFF"/>
    ${beaker(20, 40, 110, 130, '#AED6F1', 'Isotônica (SF 0,9%)', rbc(55, 60, 30, 22, 'happy'))}
    ${beaker(155, 40, 110, 130, '#D6EAF8', 'Hipotônica (água)', rbc(55, 62, 42, 38, 'open') + arrow(8, 14, 24, 32, '#3D8FD1') + arrow(102, 14, 86, 32, '#3D8FD1') + arrow(8, 112, 24, 94, '#3D8FD1') + arrow(102, 112, 86, 94, '#3D8FD1'))}
    ${beaker(290, 40, 110, 130, '#F5B7B1', 'Hipertônica (NaCl 3%)', rbc(55, 62, 22, 14, 'sad') + arrow(42, 40, 20, 18, '#9C2A4E') + arrow(68, 40, 90, 18, '#9C2A4E') + arrow(42, 84, 20, 106, '#9C2A4E') + arrow(68, 84, 90, 106, '#9C2A4E'))}
    ${htmlText(0, 6, 420, 24, 'A água segue o soluto: mantém · incha (hemólise) · murcha (crenação)', 11, 800, OUT, 'center', 'Baloo 2')}
  `);
  SCENES.b_membrana = () => scene(420, 240, `
    <rect width="420" height="240" fill="#FFFFFF"/>
    <rect x="0" y="0" width="420" height="100" fill="#FDEBD0"/><rect x="0" y="140" width="420" height="100" fill="#D5F5E3"/>
    ${htmlText(10, 6, 200, 22, 'FORA: muito Na⁺', 12, 800, '#C0392B', 'left', 'Baloo 2')}${htmlText(10, 212, 200, 22, 'DENTRO: muito K⁺ · −70 mV', 12, 800, '#1E8449', 'left', 'Baloo 2')}
    ${Array.from({ length: 14 }, (_, i) => `<circle cx="${15 + i * 30}" cy="108" r="8" fill="#F7C21B" ${S} stroke-width="2"/><line x1="${15 + i * 30}" y1="116" x2="${15 + i * 30}" y2="126" ${S} stroke-width="2"/><circle cx="${15 + i * 30}" cy="132" r="8" fill="#F7C21B" ${S} stroke-width="2"/><line x1="${15 + i * 30}" y1="124" x2="${15 + i * 30}" y2="114" ${S} stroke-width="2"/>`).join('')}
    <rect x="150" y="90" width="60" height="60" rx="14" fill="#8E44AD" ${S}/>${htmlText(150, 90, 60, 60, 'Na⁺/K⁺ ATPase', 9, 800, '#fff', 'center', 'Baloo 2')}
    ${arrow(140, 160, 140, 80, '#C0392B')}${htmlText(100, 160, 60, 22, '3 Na⁺', 11, 800, '#C0392B')}
    ${arrow(222, 80, 222, 160, '#1E8449')}${htmlText(226, 160, 60, 22, '2 K⁺', 11, 800, '#1E8449')}
    <rect x="290" y="92" width="36" height="56" rx="8" fill="#5DADE2" ${S}/>${htmlText(280, 150, 60, 22, 'canal', 9, 800, OUT)}
    ${arrow(308, 86, 308, 70, '#1E8449')}${htmlText(318, 60, 80, 22, 'K⁺ vaza', 9, 800, '#1E8449', 'left')}
    ${htmlText(330, 100, 86, 40, 'ATP', 14, 800, '#8E44AD', 'center', 'Baloo 2')}
  `);
  SCENES.b_pa = () => scene(420, 240, `
    <rect width="420" height="240" fill="#FFFFFF"/>
    <line x1="30" y1="200" x2="400" y2="200" ${S}/><line x1="30" y1="200" x2="30" y2="20" ${S}/>
    <path d="M30 150 L80 150 L90 120 L100 40 L110 60 L120 160 L130 190 L150 170 L170 150 L200 150" fill="none" stroke="#8E44AD" stroke-width="4"/>
    <line x1="30" y1="150" x2="200" y2="150" stroke="#BDC3C7" stroke-width="2" stroke-dasharray="6 4"/><line x1="30" y1="40" x2="200" y2="40" stroke="#BDC3C7" stroke-width="2" stroke-dasharray="6 4"/>
    ${htmlText(0, 28, 30, 22, '+30', 9, 800, OUT, 'center')}${htmlText(0, 140, 30, 22, '−70', 9, 800, OUT, 'center')}${htmlText(0, 112, 30, 22, '−55', 9, 800, '#C0392B', 'center')}
    ${htmlText(80, 60, 60, 40, 'Na⁺ entra', 10, 800, '#C0392B')}${htmlText(118, 90, 70, 40, 'K⁺ sai', 10, 800, '#1E8449')}${htmlText(36, 152, 60, 22, 'repouso', 9, 800, OUT, 'left')}${htmlText(60, 118, 50, 22, 'limiar', 9, 800, '#C0392B')}${htmlText(118, 190, 90, 30, 'hiperpolarização', 8, 800, OUT)}
    ${htmlText(30, 205, 200, 22, 'tempo (ms)', 9, 800, OUT, 'center')}
    <rect x="230" y="20" width="180" height="180" rx="8" fill="#FDFEFE" ${S}/>
    ${htmlText(230, 24, 180, 24, 'Pressão arterial', 12, 800, OUT, 'center', 'Baloo 2')}
    <path d="M240 150 Q255 70 270 110 T300 150 Q315 70 330 110 T360 150 Q375 70 390 110 T400 150" fill="none" stroke="#C0392B" stroke-width="3"/>
    <line x1="240" y1="80" x2="400" y2="80" stroke="#BDC3C7" stroke-width="2" stroke-dasharray="6 4"/><line x1="240" y1="150" x2="400" y2="150" stroke="#BDC3C7" stroke-width="2" stroke-dasharray="6 4"/>
    ${htmlText(236, 60, 170, 22, 'sistólica ~120 mmHg', 9, 800, '#C0392B', 'left')}${htmlText(236, 152, 170, 22, 'diastólica ~80 mmHg', 9, 800, '#2E86C1', 'left')}${htmlText(236, 172, 170, 24, 'PAM ≈ diast. + ⅓ pressão de pulso', 8.5, 800, OUT, 'left')}
  `);
  SCENES.b_alveolo = () => scene(420, 240, `
    <rect width="420" height="240" fill="#FFFFFF"/>
    <circle cx="150" cy="120" r="95" fill="#FDFEFE" ${S}/><circle cx="150" cy="120" r="80" fill="#EBF5FB"/>
    ${htmlText(90, 70, 120, 24, 'ALVÉOLO', 13, 800, '#2E86C1', 'center', 'Baloo 2')}${htmlText(80, 96, 140, 22, 'PO₂ ~100 mmHg', 11, 800, '#C0392B')}${htmlText(80, 118, 140, 22, 'PCO₂ ~40 mmHg', 11, 800, '#5D6D7E')}
    <path d="M250 40 Q290 120 250 200" fill="none" stroke="#E74C3C" stroke-width="40"/><path d="M250 40 Q290 120 250 200" fill="none" stroke="#C0392B" stroke-width="2" stroke-dasharray="4 4"/>
    ${htmlText(286, 52, 130, 24, 'CAPILAR (venoso)', 11, 800, '#C0392B', 'left', 'Baloo 2')}${htmlText(286, 78, 130, 22, 'PO₂ ~40', 11, 800, '#C0392B', 'left')}${htmlText(286, 100, 130, 22, 'PCO₂ ~46', 11, 800, '#5D6D7E', 'left')}
    ${arrow(215, 100, 262, 100, '#C0392B')}${htmlText(214, 78, 60, 22, 'O₂', 12, 800, '#C0392B')}
    ${arrow(262, 150, 215, 150, '#5D6D7E')}${htmlText(214, 152, 60, 22, 'CO₂', 12, 800, '#5D6D7E')}
    ${htmlText(286, 130, 134, 60, 'Lei de Fick: ↑ área, ↑ gradiente, ↓ espessura', 10, 800, OUT, 'left')}${htmlText(286, 186, 134, 40, 'Surfactante: ↓ tensão (Laplace)', 9.5, 800, '#1E8449', 'left')}
  `);
  SCENES.b_nefron = () => scene(420, 240, `
    <rect width="420" height="240" fill="#FFFFFF"/>
    <circle cx="110" cy="100" r="60" fill="#FADBD8" ${S}/><path d="M70 100 q20 -40 40 0 t40 0" fill="none" stroke="#C0392B" stroke-width="10"/>
    ${htmlText(60, 30, 100, 22, 'Glomérulo', 12, 800, OUT, 'center', 'Baloo 2')}
    ${arrow(150, 130, 190, 150, '#2E86C1')}${htmlText(140, 150, 80, 36, 'P. hidrostática favorece', 8.5, 800, '#2E86C1')}
    ${arrow(100, 150, 100, 125, '#9C2A4E')}${htmlText(20, 160, 110, 36, 'P. oncótica opõe', 8.5, 800, '#9C2A4E')}
    <path d="M190 160 h60 v-80 h40 v120 h40 v-60 h40" fill="none" stroke="#F5B041" stroke-width="16" stroke-linejoin="round"/><path d="M190 160 h60 v-80 h40 v120 h40 v-60 h40" fill="none" stroke="#FFF6B0" stroke-width="8" stroke-linejoin="round"/>
    ${htmlText(250, 40, 80, 36, 'Reabsorção (osmose · ativo)', 8.5, 800, OUT)}${htmlText(330, 200, 80, 36, 'Secreção (H⁺)', 8.5, 800, OUT)}
    ${htmlText(220, 190, 110, 30, 'TFG ~125 mL/min', 11, 800, '#C0392B')}
    ${htmlText(10, 210, 200, 24, 'Néfron: filtra, reabsorve, secreta', 10, 800, OUT, 'left', 'Baloo 2')}
  `);
  SCENES.b_radio = () => scene(420, 300, HOSP(`
    <rect x="30" y="60" width="90" height="172" rx="8" fill="#5D6D7E" ${S}/><rect x="40" y="70" width="70" height="90" rx="4" fill="#1C2833"/>${htmlText(30, 170, 90, 24, 'Raio X', 11, 800, '#fff', 'center', 'Baloo 2')}
    ${Array.from({ length: 5 }, (_, i) => `<line x1="120" y1="${90 + i * 18}" x2="190" y2="${100 + i * 18}" stroke="#F7C21B" stroke-width="3" stroke-dasharray="6 5"/>`).join('')}
    <rect x="200" y="60" width="18" height="172" fill="#7F8C8D" ${S}/>${htmlText(192, 36, 40, 22, 'Pb', 11, 800, OUT)}
    ${put(NURSE({ coat: '#7F8C8D', armR: 'hold', holdR: 'clipboard', expr: 'happy' }), 300, 296, 0.8)}
    ${bubble({ x: 230, y: 10, w: 180, h: 60, text: 'Tempo, distância e blindagem. Avental, dosímetro e ALARA.', tail: [300, 118], size: 11 })}
    ${htmlText(110, 240, 90, 24, 'distância', 9, 800, OUT)}
  `, '#FDFEFE'));
  SCENES.b_gasometria = () => scene(420, 300, HOSP(`
    ${hospBed(30, 232, 200)}
    ${put(ELDER({ sit: true, expr: 'worried', armL: 'hold' }), 130, 236, 0.58)}
    ${put(NURSE({ armL: 'hold', holdL: 'clipboard', armR: 'point', expr: 'happy' }), 320, 296, 0.8)}
    ${bubble({ x: 150, y: 6, w: 240, h: 60, text: 'Hiperventilando: elimina CO₂, o pH sobe. Vamos respirar devagar comigo.', tail: [320, 110], size: 10.5 })}
    <rect x="30" y="96" width="110" height="34" rx="6" fill="#FFFFFF" ${S}/>${htmlText(30, 96, 110, 34, 'pH 7,52 · PCO₂ 28', 10, 800, '#C0392B', 'center', 'Baloo 2')}
  `));
  SCENES.b_oximetro = () => scene(420, 300, HOSP(`
    ${hospBed(30, 232, 200)}${oxygen(300, 232)}
    ${put(KID({ sit: true, expr: 'happy', armL: 'hold', holdL: 'teddy', hairStyle: 'cap', headphones: false }), 130, 236, 0.58)}
    ${put(NURSE({ armR: 'show', holdR: 'oximeter', expr: 'happy' }), 380, 296, 0.74)}
    ${bubble({ x: 150, y: 6, w: 240, h: 60, text: 'O oxímetro lê a luz que a hemoglobina absorve: 97% de saturação.', tail: [380, 110], size: 10.5 })}
  `));
  SCENES.b_dialise = () => scene(420, 300, HOSP(`
    ${hospBed(20, 232, 190)}
    ${put(ELDER({ sit: true, expr: 'happy', armL: 'hold' }), 115, 236, 0.58)}
    <rect x="250" y="70" width="80" height="162" rx="8" fill="#ECF0F1" ${S}/><rect x="262" y="84" width="56" height="60" rx="4" fill="#2C3E50"/>${htmlText(250, 150, 80, 24, 'Dialisador', 10, 800, OUT, 'center', 'Baloo 2')}<rect x="270" y="176" width="40" height="44" rx="4" fill="#AED6F1" ${S}/>
    <path d="M200 160 q40 -40 56 -60" fill="none" stroke="#C0392B" stroke-width="5"/><path d="M200 180 q40 20 56 40" fill="none" stroke="#2E86C1" stroke-width="5"/>
    ${put(NURSE({ armL: 'point', expr: 'happy' }), 380, 296, 0.74)}
    ${bubble({ x: 190, y: 6, w: 220, h: 56, text: 'A ureia sai por difusão; a água, por ultrafiltração. É a Unidade 1 salvando vidas.', tail: [380, 110], size: 10.5 })}
  `));
  SCENES.b_termo = () => scene(420, 240, `
    <rect width="420" height="240" fill="#FFFFFF"/>
    ${put(KID({ expr: 'neutral', armL: 'down', armR: 'down' }), 110, 236, 0.74)}
    <rect x="30" y="40" width="40" height="18" rx="4" fill="#5DADE2" ${S}/>${htmlText(0, 60, 100, 22, 'compressa', 8.5, 800, OUT)}
    ${arrow(70, 60, 86, 82, '#2E86C1')}${htmlText(0, 84, 70, 22, 'condução', 8, 800, '#2E86C1')}
    ${arrow(150, 120, 190, 110, '#1ABC9C')}${arrow(150, 150, 190, 150, '#1ABC9C')}${htmlText(160, 88, 80, 22, 'convecção', 8.5, 800, '#1ABC9C')}
    ${Array.from({ length: 3 }, (_, i) => `<path d="M${40 + i * 8} 180 q-6 -10 0 -20 q6 -10 0 -20" fill="none" stroke="#E67E22" stroke-width="2.5"/>`).join('')}${htmlText(10, 186, 70, 22, 'radiação', 8.5, 800, '#E67E22')}
    <circle cx="90" cy="40" r="4" fill="#5DADE2"/><circle cx="130" cy="36" r="4" fill="#5DADE2"/>${htmlText(84, 8, 70, 22, 'evaporação', 8.5, 800, '#2E86C1')}
    <rect x="230" y="20" width="180" height="200" rx="10" fill="#FFF6B0" ${S}/>
    ${htmlText(236, 26, 168, 30, '1ª lei: energia se conserva', 10, 800, OUT, 'left', 'Baloo 2')}${htmlText(236, 58, 168, 30, '2ª lei: entropia ↑, calor sempre sobra', 10, 800, OUT, 'left', 'Baloo 2')}${htmlText(236, 96, 168, 30, 'ATP = moeda energética', 10, 800, '#8E44AD', 'left', 'Baloo 2')}${htmlText(236, 130, 168, 80, 'Febre e hipotermia: manejo pela física do calor (compressas, ambiente fresco, aquecimento)', 9, 700, OUT, 'left')}
  `);
  SCENES.f_termo = () => scene(420, 240, `
    <rect width="420" height="240" fill="#FFFFFF"/>
    ${put(KID({ expr: 'neutral', armL: 'down', armR: 'down' }), 110, 236, 0.74)}
    <rect x="30" y="40" width="40" height="18" rx="4" fill="#5DADE2" ${S}/>${htmlText(0, 60, 100, 22, 'compressa', 8.5, 800, OUT)}
    ${arrow(70, 60, 86, 82, '#2E86C1')}${htmlText(0, 84, 70, 22, 'condução', 8, 800, '#2E86C1')}
    ${arrow(150, 120, 190, 110, '#1ABC9C')}${arrow(150, 150, 190, 150, '#1ABC9C')}${htmlText(160, 88, 80, 22, 'convecção', 8.5, 800, '#1ABC9C')}
    ${Array.from({ length: 3 }, (_, i) => `<path d="M${40 + i * 8} 180 q-6 -10 0 -20 q6 -10 0 -20" fill="none" stroke="#E67E22" stroke-width="2.5"/>`).join('')}${htmlText(10, 186, 70, 22, 'radiação', 8.5, 800, '#E67E22')}
    <circle cx="90" cy="40" r="4" fill="#5DADE2"/><circle cx="130" cy="36" r="4" fill="#5DADE2"/>${htmlText(84, 8, 70, 22, 'evaporação', 8.5, 800, '#2E86C1')}
    <rect x="230" y="20" width="180" height="200" rx="10" fill="#FFF6B0" ${S}/>
    ${htmlText(236, 26, 168, 30, 'Termostato: hipotálamo ~37 °C', 10, 800, OUT, 'left', 'Baloo 2')}${htmlText(236, 58, 168, 34, 'Calor: vasodilatação + sudorese', 9.5, 800, '#C0392B', 'left', 'Baloo 2')}${htmlText(236, 94, 168, 34, 'Frio: vasoconstrição + tremores', 9.5, 800, '#2E86C1', 'left', 'Baloo 2')}${htmlText(236, 132, 168, 60, 'Febre: pirógenos elevam o set point; o corpo defende uma temperatura maior (calafrios)', 8.5, 800, '#8E44AD', 'left')}
  `);
  SCENES.b_sinais = () => scene(420, 300, HOSP(`
    ${bpMonitor(60, 232)}${monitor(360, 232)}
    ${put(ELDER({ sit: true, expr: 'happy', armL: 'down' }), 210, 240, 0.64)}
    <rect x="160" y="206" width="100" height="26" rx="6" fill="#5DADE2" ${S}/><rect x="168" y="232" width="8" height="50" fill="#7F8C8D" ${S}/><rect x="244" y="232" width="8" height="50" fill="#7F8C8D" ${S}/>
    ${put(NURSE({ armR: 'show', holdR: 'cuff', expr: 'happy' }), 110, 296, 0.78)}
    ${bubble({ x: 10, y: 6, w: 220, h: 60, text: '1º som de Korotkoff: sistólica. Some o som: diastólica. Manguito do tamanho certo!', tail: [110, 118], size: 10.5 })}
  `));
  SCENES.b_soro = () => scene(420, 300, HOSP(`
    ${hospBed(30, 232, 200)}${ivPole(250, 232)}
    ${put(ELDER({ sit: true, expr: 'happy' }), 130, 236, 0.58)}
    ${put(NURSE({ armR: 'point', armL: 'hold', holdL: 'clipboard', expr: 'happy' }), 350, 296, 0.78)}
    ${bubble({ x: 170, y: 6, w: 230, h: 60, text: 'SF 0,9% é isotônico: a hemácia mantém o volume. Hipertônico rápido? Nunca.', tail: [350, 110], size: 10.5 })}
  `));

  // ======= FÍSICO-QUÍMICA APLICADA ÀS CIÊNCIAS BIOMÉDICAS =======
  const BIOMED = (o = {}) => person(Object.assign({ skin: '#F2C9A6', hair: '#2C3E50', hairStyle: 'long', shirt: '#1ABC9C', pants: '#2C3E50', coat: '#FFFFFF', sleeve: 'long', shoes: '#FFFFFF', glasses: true, gloves: true }, o));
  const BIOMED2 = (o = {}) => person(Object.assign({ skin: '#8D5B3A', hair: '#1C1C1C', hairStyle: 'cap', shirt: '#8E44AD', pants: '#2C3E50', coat: '#FFFFFF', sleeve: 'long', shoes: '#FFFFFF', gloves: true }, o));
  ITEMS.tube = () => `<g transform="rotate(-15)"><path d="M-6 -40 L-6 6 Q-6 14 0 14 Q6 14 6 6 L6 -40 Z" fill="#D6EAF8" ${S}/><path d="M-6 -12 L-6 6 Q-6 14 0 14 Q6 14 6 6 L6 -12 Z" fill="#E74C3C"/><rect x="-9" y="-44" width="18" height="6" rx="2" fill="#ECF0F1" ${S}/></g>`;
  ITEMS.pipette = () => `<g transform="rotate(-40)"><rect x="-3" y="-52" width="6" height="60" rx="2" fill="#ECF0F1" ${S}/><rect x="-7" y="-64" width="14" height="14" rx="4" fill="#3498DB" ${S}/><path d="M-3 8 L0 20 L3 8 Z" fill="#ECF0F1" ${S}/></g>`;
  function flask(x, y, h = 60, color = '#AED6F1', label = '') {
    const w = h * 0.9;
    return `<g transform="translate(${x} ${y})"><path d="M${-w * 0.14} ${-h} L${-w * 0.14} ${-h * 0.55} L${-w / 2} 0 L${w / 2} 0 L${w * 0.14} ${-h * 0.55} L${w * 0.14} ${-h} Z" fill="#F4F6F7" ${S}/><path d="M${-w * 0.33} ${-h * 0.28} L${-w / 2 + 2} -2 L${w / 2 - 2} -2 L${w * 0.33} ${-h * 0.28} Z" fill="${color}"/><rect x="${-w * 0.2}" y="${-h - 6}" width="${w * 0.4}" height="8" rx="2" fill="#ECF0F1" ${S}/>${label ? htmlText(-40, 4, 80, 20, label, 9, 800, OUT) : ''}</g>`;
  }
  function tubeRack(x, y) {
    const cols = ['#E74C3C', '#F7C21B', '#58D68D', '#5DADE2'];
    return `<g transform="translate(${x} ${y})"><rect x="0" y="-14" width="76" height="14" rx="3" fill="#8D6E63" ${S}/>${cols.map((c, i) => `<path d="M${8 + i * 18} -50 L${8 + i * 18} -16 Q${8 + i * 18} -10 ${13 + i * 18} -10 Q${18 + i * 18} -10 ${18 + i * 18} -16 L${18 + i * 18} -50 Z" fill="#D6EAF8" ${S} stroke-width="2"/><path d="M${8 + i * 18} -30 L${8 + i * 18} -16 Q${8 + i * 18} -10 ${13 + i * 18} -10 Q${18 + i * 18} -10 ${18 + i * 18} -16 L${18 + i * 18} -30 Z" fill="${c}"/>`).join('')}</g>`;
  }
  function labBench(x, y, w) {
    return `<rect x="${x}" y="${y}" width="${w}" height="14" rx="3" fill="#2C3E50" ${S}/><rect x="${x + 6}" y="${y + 14}" width="${w - 12}" height="60" fill="#ECF0F1" ${S}/><line x1="${x + w / 2}" y1="${y + 14}" x2="${x + w / 2}" y2="${y + 74}" ${S} stroke-width="2"/><rect x="${x + 16}" y="${y + 24}" width="18" height="6" rx="2" fill="#BDC3C7" ${S} stroke-width="2"/><rect x="${x + w / 2 + 10}" y="${y + 24}" width="18" height="6" rx="2" fill="#BDC3C7" ${S} stroke-width="2"/>`;
  }
  function analyzer(x, y, w, h, title, lines = [], color = '#5DADE2') {
    return `<g transform="translate(${x} ${y})"><rect x="0" y="${-h}" width="${w}" height="${h}" rx="8" fill="#F4F6F7" ${S}/><rect x="8" y="${-h + 8}" width="${w - 16}" height="${h * 0.5}" rx="4" fill="#1C2833" ${S}/>${htmlText(10, -h + 10, w - 20, 18, title, 9, 800, color, 'center', 'Baloo 2')}${lines.map((l, i) => htmlText(10, -h + 28 + i * 15, w - 20, 16, l, 9, 800, '#58D68D', 'left', 'Baloo 2')).join('')}<rect x="12" y="${-h * 0.4}" width="${w - 24}" height="${h * 0.14}" rx="3" fill="${color}" ${S} stroke-width="2"/><circle cx="${w - 18}" cy="${-h * 0.14}" r="5" fill="#E74C3C" ${S} stroke-width="2"/><circle cx="${w - 34}" cy="${-h * 0.14}" r="5" fill="#58D68D" ${S} stroke-width="2"/></g>`;
  }
  function LAB(inner) {
    return `${plainWall(420, 300, '#EAF2F8')}<rect x="0" y="0" width="420" height="30" fill="#AED6F1" ${S}/>${htmlText(0, 4, 420, 24, 'LABORATÓRIO DE ANÁLISES CLÍNICAS', 10, 800, '#1F618D', 'center', 'Baloo 2')}${floor(420, 232, 68, '#D5DBDB')}${inner}`;
  }
  function axes(x, y, w, h, xl, yl) {
    return `<line x1="${x}" y1="${y + h}" x2="${x + w}" y2="${y + h}" ${S}/><line x1="${x}" y1="${y + h}" x2="${x}" y2="${y}" ${S}/>${htmlText(x, y + h + 4, w, 18, xl, 9, 800, OUT)}${htmlText(x - 2, y - 20, 90, 18, yl, 9, 800, OUT, 'left')}`;
  }

  SCENES.q_cover = () => scene(420, 470, `
    ${plainWall(420, 332, '#EAF2F8')}${floor(420, 332, 138, '#D5DBDB')}<rect x="0" y="230" width="420" height="10" fill="#8E44AD" ${S}/>
    ${whiteboard(26, 34, 226, 124, `${htmlText(6, 4, 214, 28, 'PV = nRT', 18, 800, '#2E86C1', 'center', 'Baloo 2')}${htmlText(6, 34, 214, 26, 'ΔG = ΔH − TΔS', 14, 800, '#8E44AD', 'center', 'Baloo 2')}${htmlText(6, 62, 214, 26, 'pH = pKa + log([A⁻]/[HA])', 12.5, 800, '#C0392B', 'center', 'Baloo 2')}${htmlText(6, 90, 214, 26, 'V = Vmax·[S] / (Km + [S])', 12.5, 800, '#1E8449', 'center', 'Baloo 2')}`)}
    ${window_(300, 40, 96, 72)}
    ${labBench(250, 332, 170)}${flask(290, 332, 52, '#F5B7B1')}${flask(340, 332, 40, '#58D68D')}${tubeRack(330, 332)}
    ${put(PROF({ armL: 'point', armR: 'hold', holdR: 'tube', expr: 'bigsmile', coat: '#FFFFFF', shirt: '#8E44AD' }), 300, 440, 1.0)}
    ${put(BIOMED({ armL: 'hold', holdL: 'clipboard', expr: 'happy' }), 110, 436, 0.78)}
    ${put(BIOMED2({ armR: 'show', holdR: 'pipette', expr: 'happy' }), 200, 436, 0.78)}
  `, '', 'xMidYMax slice');

  SCENES.q_gases = () => scene(420, 240, `
    <rect width="420" height="240" fill="#FFFFFF"/>
    ${htmlText(0, 4, 420, 24, 'PV = nRT: as leis dos gases', 12, 800, OUT, 'center', 'Baloo 2')}
    <rect x="30" y="60" width="70" height="140" rx="4" fill="#EBF5FB" ${S}/><rect x="26" y="70" width="78" height="10" rx="2" fill="#7F8C8D" ${S}/><rect x="60" y="34" width="10" height="40" fill="#7F8C8D" ${S}/>
    ${Array.from({ length: 10 }, (_, i) => `<circle cx="${40 + (i % 4) * 17}" cy="${100 + Math.floor(i / 4) * 30}" r="4" fill="#3498DB"/>`).join('')}
    <rect x="120" y="60" width="70" height="140" rx="4" fill="#EBF5FB" ${S}/><rect x="116" y="130" width="78" height="10" rx="2" fill="#7F8C8D" ${S}/><rect x="150" y="34" width="10" height="100" fill="#7F8C8D" ${S}/>
    ${Array.from({ length: 10 }, (_, i) => `<circle cx="${130 + (i % 4) * 17}" cy="${150 + Math.floor(i / 4) * 18}" r="4" fill="#3498DB"/>`).join('')}
    ${arrow(104, 40, 116, 40, OUT)}
    ${htmlText(20, 204, 190, 34, 'Boyle (T const.): ↑ P → ↓ V', 10, 800, '#2E86C1')}
    <circle cx="300" cy="120" r="62" fill="#AED6F1" ${S}/>
    <path d="M300 120 L300 58 A62 62 0 0 1 359 101 Z" fill="#E74C3C" ${S}/>
    <path d="M300 120 L359 101 A62 62 0 0 1 356 140 Z" fill="#F7C21B" ${S}/>
    ${htmlText(250, 112, 70, 24, 'N₂ 78%', 11, 800, '#1F618D')}${htmlText(318, 66, 60, 22, 'O₂ 21%', 10, 800, '#C0392B')}${htmlText(356, 112, 60, 22, 'outros', 8, 800, OUT, 'left')}
    ${htmlText(230, 190, 150, 40, 'Dalton: P total = soma das pressões parciais (PO₂ ≈ 160 mmHg)', 9.5, 800, '#C0392B')}
    ${htmlText(230, 30, 150, 24, 'Ar atmosférico', 11, 800, OUT, 'center', 'Baloo 2')}
  `);

  SCENES.q_entalpia = () => scene(420, 240, `
    <rect width="420" height="240" fill="#FFFFFF"/>
    ${axes(30, 48, 170, 152, 'caminho da reação', 'energia')}
    <path d="M40 90 L90 90 Q120 40 150 90 L150 150 L190 150" fill="none" stroke="#E74C3C" stroke-width="4"/>
    ${arrow(170, 92, 170, 146, '#E74C3C')}${htmlText(96, 100, 110, 22, 'ΔH < 0', 11, 800, '#C0392B')}
    ${htmlText(34, 70, 60, 20, 'reagentes', 8, 800, OUT)}${htmlText(140, 152, 60, 20, 'produtos', 8, 800, OUT)}
    ${htmlText(30, 6, 170, 24, 'EXOTÉRMICO: libera calor', 11, 800, '#C0392B', 'center', 'Baloo 2')}
    ${axes(240, 48, 170, 152, 'caminho da reação', 'energia')}
    <path d="M250 150 L300 150 Q330 60 360 90 L360 90 L400 90" fill="none" stroke="#3498DB" stroke-width="4"/>
    ${arrow(380, 148, 380, 94, '#2E86C1')}${htmlText(300, 108, 110, 22, 'ΔH > 0', 11, 800, '#2E86C1')}
    ${htmlText(244, 152, 60, 20, 'reagentes', 8, 800, OUT)}${htmlText(350, 72, 60, 20, 'produtos', 8, 800, OUT)}
    ${htmlText(240, 6, 170, 24, 'ENDOTÉRMICO: absorve calor', 11, 800, '#2E86C1', 'center', 'Baloo 2')}
  `);

  SCENES.q_gibbs = () => scene(420, 240, `
    <rect width="420" height="240" fill="#FFFFFF"/>
    ${htmlText(0, 4, 420, 24, 'ΔG = ΔH − TΔS: o sinal decide a espontaneidade', 11.5, 800, OUT, 'center', 'Baloo 2')}
    <rect x="20" y="40" width="120" height="70" rx="8" fill="#D5F5E3" ${S}/>${htmlText(20, 44, 120, 24, 'ΔG < 0', 14, 800, '#1E8449', 'center', 'Baloo 2')}${htmlText(24, 68, 112, 40, 'exergônico: espontâneo, libera energia útil', 9, 800, OUT)}
    <rect x="150" y="40" width="120" height="70" rx="8" fill="#FFF6B0" ${S}/>${htmlText(150, 44, 120, 24, 'ΔG = 0', 14, 800, '#9A7D0A', 'center', 'Baloo 2')}${htmlText(154, 68, 112, 40, 'equilíbrio: sem tendência líquida de mudança', 9, 800, OUT)}
    <rect x="280" y="40" width="120" height="70" rx="8" fill="#FDE2E0" ${S}/>${htmlText(280, 44, 120, 24, 'ΔG > 0', 14, 800, '#C0392B', 'center', 'Baloo 2')}${htmlText(284, 68, 112, 40, 'endergônico: não espontâneo, requer energia', 9, 800, OUT)}
    ${htmlText(0, 118, 420, 22, 'Acoplamento: o ATP “financia” a reação endergônica', 10.5, 800, '#8E44AD', 'center', 'Baloo 2')}
    <line x1="40" y1="220" x2="400" y2="220" ${S}/>
    <rect x="60" y="190" width="70" height="30" fill="#FDE2E0" ${S}/>${htmlText(60, 194, 70, 22, 'A → B', 10, 800, '#C0392B')}${htmlText(40, 166, 110, 22, 'ΔG = +15', 9.5, 800, '#C0392B')}
    <rect x="170" y="160" width="90" height="60" fill="#D5F5E3" ${S}/>${htmlText(170, 180, 90, 22, 'ATP → ADP', 10, 800, '#1E8449')}${htmlText(160, 140, 110, 22, 'ΔG = −30', 9.5, 800, '#1E8449')}
    ${htmlText(262, 176, 30, 30, '=', 20, 800, OUT)}
    <rect x="300" y="175" width="90" height="45" fill="#D5F5E3" ${S}/>${htmlText(300, 186, 90, 22, 'soma', 10, 800, '#1E8449')}${htmlText(290, 150, 110, 22, 'ΔG = −15 ✓', 9.5, 800, '#1E8449')}
  `);

  SCENES.q_lechatelier = () => scene(420, 240, `
    <rect width="420" height="240" fill="#FFFFFF"/>
    ${htmlText(0, 4, 420, 24, 'Le Chatelier no equilíbrio do bicarbonato', 11.5, 800, OUT, 'center', 'Baloo 2')}
    ${htmlText(0, 30, 420, 26, 'CO₂ + H₂O ⇌ H₂CO₃ ⇌ H⁺ + HCO₃⁻', 15, 800, '#2C3E50', 'center', 'Baloo 2')}
    <rect x="20" y="70" width="185" height="150" rx="8" fill="#FDE2E0" ${S}/>
    ${htmlText(20, 74, 185, 22, '↑ CO₂ (hipoventilação)', 10.5, 800, '#C0392B', 'center', 'Baloo 2')}
    ${arrow(60, 130, 160, 130, '#C0392B')}${htmlText(40, 104, 145, 22, 'desloca para a direita', 9.5, 800, OUT)}
    ${htmlText(30, 140, 165, 70, '↑ H⁺ → pH cai: ACIDOSE respiratória. O rim compensa retendo HCO₃⁻.', 9.5, 800, OUT)}
    <rect x="215" y="70" width="185" height="150" rx="8" fill="#D6EAF8" ${S}/>
    ${htmlText(215, 74, 185, 22, '↓ CO₂ (hiperventilação)', 10.5, 800, '#2E86C1', 'center', 'Baloo 2')}
    ${arrow(355, 130, 255, 130, '#2E86C1')}${htmlText(235, 104, 145, 22, 'desloca para a esquerda', 9.5, 800, OUT)}
    ${htmlText(225, 140, 165, 70, '↓ H⁺ → pH sobe: ALCALOSE respiratória. O rim compensa eliminando HCO₃⁻.', 9.5, 800, OUT)}
  `);

  SCENES.q_tampao = () => scene(420, 240, `
    <rect width="420" height="240" fill="#FFFFFF"/>
    ${axes(40, 30, 220, 170, 'base adicionada (OH⁻)', 'pH')}
    <path d="M44 190 Q90 170 110 130 L150 120 Q170 110 190 50 L250 40" fill="none" stroke="#8E44AD" stroke-width="4"/>
    <rect x="100" y="100" width="100" height="50" fill="#FFF6B0" opacity=".7"/>
    <line x1="40" y1="125" x2="150" y2="125" stroke="#C0392B" stroke-width="2" stroke-dasharray="6 4"/>
    <circle cx="150" cy="125" r="6" fill="#C0392B" ${S} stroke-width="2"/>
    ${htmlText(0, 114, 40, 22, 'pKa', 10, 800, '#C0392B')}
    ${htmlText(96, 150, 110, 40, 'região tampão: pH ≈ pKa ± 1', 8.5, 800, '#9A7D0A')}
    ${htmlText(150, 100, 110, 22, '[A⁻] = [HA]', 9, 800, '#C0392B', 'left')}
    <rect x="270" y="30" width="140" height="170" rx="8" fill="#F4F6F7" ${S}/>
    ${htmlText(270, 34, 140, 24, 'Henderson-Hasselbalch', 10, 800, OUT, 'center', 'Baloo 2')}
    ${htmlText(274, 60, 132, 44, 'pH = pKa + log ([base conj.] / [ácido])', 10.5, 800, '#8E44AD')}
    ${htmlText(274, 108, 132, 30, 'Sangue: pH 7,4', 10, 800, '#C0392B')}${htmlText(274, 132, 132, 60, '[HCO₃⁻] 24 mM / [CO₂] 1,2 mM = 20 : 1 → 6,1 + log 20 ≈ 7,4', 9, 800, OUT)}
  `);

  SCENES.q_coligativas = () => scene(420, 240, `
    <rect width="420" height="240" fill="#FFFFFF"/>
    ${htmlText(0, 4, 420, 24, 'As 4 propriedades coligativas: só o NÚMERO de partículas importa', 10.5, 800, OUT, 'center', 'Baloo 2')}
    ${beaker(18, 60, 80, 90, '#AED6F1', 'Tonoscopia', `<path d="M16 -16 q6 -10 0 -20 M34 -16 q6 -10 0 -20" fill="none" stroke="#95A5A6" stroke-width="2.5"/><text x="56" y="-18" font-size="16" font-weight="800" fill="#2E86C1">↓</text>` + htmlText(0, 20, 80, 40, '↓ pressão de vapor', 8.5, 800, OUT))}
    ${beaker(118, 60, 80, 90, '#F5B7B1', 'Ebulioscopia', `<circle cx="20" cy="60" r="4" fill="#fff" ${S} stroke-width="1.5"/><circle cx="40" cy="48" r="5" fill="#fff" ${S} stroke-width="1.5"/><circle cx="58" cy="66" r="4" fill="#fff" ${S} stroke-width="1.5"/>` + htmlText(0, 10, 80, 40, '↑ ponto de ebulição', 8.5, 800, OUT))}
    ${beaker(218, 60, 80, 90, '#D6EAF8', 'Crioscopia', `<path d="M40 30 l0 30 M25 37 l30 16 M25 53 l30 -16" stroke="#2E86C1" stroke-width="3" fill="none"/>` + htmlText(0, 64, 80, 30, '↓ ponto de congelamento', 8, 800, OUT))}
    ${beaker(318, 60, 80, 90, '#D5F5E3', 'Pressão osmótica', `<line x1="40" y1="0" x2="40" y2="90" stroke="#7F8C8D" stroke-width="3" stroke-dasharray="4 3"/><rect x="42" y="0" width="38" height="90" fill="#58D68D" opacity=".5"/>` + arrow(14, 50, 32, 50, '#1E8449') + htmlText(0, 10, 80, 40, 'π = iMRT', 9.5, 800, '#1E8449'))}
    ${htmlText(10, 190, 400, 44, 'Fator de van’t Hoff: NaCl → Na⁺ + Cl⁻ (i ≈ 2). Na mesma molaridade, o eletrólito tem o dobro do efeito do não eletrólito (glicose, i = 1).', 9.5, 800, OUT)}
  `);

  SCENES.q_cinetica = () => scene(420, 240, `
    <rect width="420" height="240" fill="#FFFFFF"/>
    ${axes(30, 48, 170, 152, 'caminho da reação', 'energia')}
    <path d="M40 120 L80 120 Q115 20 150 150 L190 150" fill="none" stroke="#E74C3C" stroke-width="4"/>
    <path d="M40 120 L80 120 Q115 70 150 150" fill="none" stroke="#1E8449" stroke-width="4" stroke-dasharray="7 4"/>
    ${arrow(100, 118, 100, 48, '#C0392B')}${htmlText(104, 52, 60, 20, 'Ea', 10, 800, '#C0392B', 'left')}
    ${arrow(130, 118, 130, 86, '#1E8449')}${htmlText(134, 80, 70, 20, 'Ea c/ enzima', 8.5, 800, '#1E8449', 'left')}
    ${htmlText(30, 6, 170, 24, 'Catalisador: ↓ Ea, ΔG igual', 11, 800, OUT, 'center', 'Baloo 2')}
    ${axes(240, 48, 170, 152, '[S] substrato', 'V')}
    <path d="M240 200 Q270 70 400 52" fill="none" stroke="#8E44AD" stroke-width="4"/>
    <line x1="240" y1="48" x2="410" y2="48" stroke="#BDC3C7" stroke-width="2" stroke-dasharray="6 4"/>${htmlText(360, 28, 60, 20, 'Vmax', 10, 800, '#8E44AD')}
    <line x1="240" y1="124" x2="290" y2="124" stroke="#BDC3C7" stroke-width="2" stroke-dasharray="6 4"/><line x1="290" y1="124" x2="290" y2="200" stroke="#BDC3C7" stroke-width="2" stroke-dasharray="6 4"/>
    ${htmlText(236, 104, 60, 20, 'Vmax/2', 9, 800, OUT, 'left')}${htmlText(276, 180, 40, 20, 'Km', 10, 800, '#C0392B')}
    ${htmlText(240, 6, 170, 24, 'Michaelis-Menten', 11, 800, OUT, 'center', 'Baloo 2')}
    ${htmlText(300, 150, 110, 40, '↓ Km = ↑ afinidade', 9, 800, '#8E44AD')}
  `);

  SCENES.q_pilha = () => scene(420, 240, `
    <rect width="420" height="240" fill="#FFFFFF"/>
    ${htmlText(0, 2, 420, 22, 'Pilha (célula galvânica): ΔG < 0, energia química → elétrica', 10.5, 800, OUT, 'center', 'Baloo 2')}
    ${beaker(40, 92, 120, 92, '#D6EAF8', 'ÂNODO (−): oxidação', `<rect x="50" y="-38" width="20" height="100" fill="#95A5A6" ${S}/>` + htmlText(0, 60, 120, 24, 'Zn → Zn²⁺ + 2e⁻', 9, 800, '#2E86C1'))}
    ${beaker(260, 92, 120, 92, '#FADBD8', 'CÁTODO (+): redução', `<rect x="50" y="-38" width="20" height="100" fill="#CD853F" ${S}/>` + htmlText(0, 60, 120, 24, 'Cu²⁺ + 2e⁻ → Cu', 9, 800, '#C0392B'))}
    <path d="M150 112 L150 90 Q150 80 160 80 L260 80 Q270 80 270 90 L270 112" fill="none" stroke="#F7C21B" stroke-width="12"/><path d="M150 112 L150 90 Q150 80 160 80 L260 80 Q270 80 270 90 L270 112" fill="none" ${S}/>
    ${htmlText(160, 96, 100, 20, 'ponte salina', 9, 800, OUT)}
    <line x1="100" y1="54" x2="100" y2="46" ${S}/><line x1="100" y1="46" x2="192" y2="46" ${S}/><line x1="228" y1="46" x2="320" y2="46" ${S}/><line x1="320" y1="46" x2="320" y2="54" ${S}/>
    <circle cx="210" cy="46" r="18" fill="#FFFFFF" ${S}/>${htmlText(192, 35, 36, 22, 'V', 13, 800, OUT, 'center', 'Baloo 2')}
    ${arrow(120, 36, 180, 36, '#1E8449')}${htmlText(120, 22, 60, 16, 'e⁻', 9, 800, '#1E8449')}
    ${htmlText(0, 216, 420, 22, 'PERDE = OXIDA (ânodo) · GANHA = REDUZ (cátodo) · agente redutor doa e⁻', 9.5, 800, '#8E44AD', 'center', 'Baloo 2')}
  `);
  SCENES.q_coloide = () => scene(420, 240, `
    <rect width="420" height="240" fill="#FFFFFF"/>
    ${htmlText(0, 4, 420, 24, 'Solução · coloide · suspensão: o efeito Tyndall', 11.5, 800, OUT, 'center', 'Baloo 2')}
    <rect x="0" y="96" width="30" height="22" rx="3" fill="#2C3E50" ${S}/>${htmlText(0, 120, 40, 20, 'laser', 8, 800, OUT)}
    <line x1="30" y1="107" x2="150" y2="107" stroke="#E74C3C" stroke-width="3" opacity=".35"/>
    ${beaker(40, 50, 100, 110, '#D6EAF8', 'Solução (<1 nm)', htmlText(0, 76, 100, 30, 'feixe invisível', 8, 800, OUT))}
    <line x1="150" y1="107" x2="290" y2="107" stroke="#E74C3C" stroke-width="7"/>
    ${beaker(170, 50, 100, 110, '#FADBD8', 'Coloide (1–1000 nm)', Array.from({ length: 9 }, (_, i) => `<circle cx="${14 + (i % 3) * 36}" cy="${20 + Math.floor(i / 3) * 34}" r="4" fill="#C0392B"/>`).join('') + htmlText(0, 76, 100, 30, 'feixe VISÍVEL', 8, 800, '#C0392B'))}
    <line x1="290" y1="107" x2="400" y2="107" stroke="#E74C3C" stroke-width="3" opacity=".35"/>
    ${beaker(300, 50, 100, 110, '#EBF5FB', 'Suspensão (>1000 nm)', `<ellipse cx="50" cy="95" rx="40" ry="10" fill="#8D6E63"/>` + htmlText(0, 20, 100, 30, 'sedimenta e filtra', 8, 800, OUT))}
    ${htmlText(10, 196, 400, 40, 'Plasma = coloide de proteínas. Turbidimetria mede a luz transmitida; nefelometria mede a luz espalhada.', 9.5, 800, '#8E44AD')}
  `);

  SCENES.q_lab_dilui = () => scene(420, 300, LAB(`
    ${labBench(20, 232, 220)}${flask(60, 232, 56, '#AED6F1', '1 M')}${flask(120, 232, 70, '#D6EAF8', '0,05 M')}${tubeRack(160, 232)}
    ${put(BIOMED({ armR: 'show', holdR: 'pipette', armL: 'point', expr: 'happy' }), 320, 296, 0.8)}
    ${bubble({ x: 150, y: 40, w: 250, h: 60, text: 'C₁V₁ = C₂V₂: 1 M × V₁ = 0,05 M × 500 mL → V₁ = 25 mL do estoque e completo com água até 500 mL.', tail: [320, 108], size: 10 })}
  `));
  SCENES.q_lab_gaso = () => scene(420, 300, LAB(`
    ${labBench(20, 232, 200)}${analyzer(40, 232, 130, 96, 'GASOMETRIA', ['pH 7,28', 'PaCO₂ 58', 'HCO₃⁻ 26'])}
    ${put(BIOMED2({ armL: 'hold', holdL: 'clipboard', armR: 'point', expr: 'worried' }), 300, 296, 0.8)}
    ${bubble({ x: 150, y: 40, w: 250, h: 60, text: 'pH baixo com PaCO₂ alta: acidose respiratória. Eletrodo de vidro (pH) e eletrodos íon-seletivos fizeram a leitura.', tail: [300, 108], size: 10 })}
  `));
  SCENES.q_lab_enzima = () => scene(420, 300, LAB(`
    ${labBench(20, 232, 200)}${analyzer(40, 232, 130, 96, 'ESPECTROFOTÔMETRO', ['ALT: ΔA/min', '340 nm · 37 °C'], '#8E44AD')}
    ${put(BIOMED({ armR: 'hold', holdR: 'tube', armL: 'point', expr: 'happy' }), 300, 296, 0.8)}
    ${bubble({ x: 150, y: 40, w: 250, h: 60, text: 'Método cinético: a velocidade da reação é proporcional à atividade da enzima. Por isso temperatura e pH são padronizados.', tail: [300, 108], size: 10 })}
  `));
  SCENES.q_lab_ise = () => scene(420, 300, LAB(`
    ${labBench(20, 232, 200)}${analyzer(40, 232, 130, 96, 'ELETRÓLITOS (ISE)', ['Na⁺ 138 mmol/L', 'K⁺ 6,2 mmol/L ▲'], '#E67E22')}
    ${put(BIOMED2({ armL: 'hold', holdL: 'clipboard', armR: 'point', expr: 'surprised' }), 300, 296, 0.8)}
    ${bubble({ x: 150, y: 40, w: 250, h: 60, text: 'Cada eletrodo íon-seletivo gera um potencial proporcional ao íon. Potássio alto: confirmo hemólise antes de liberar.', tail: [300, 108], size: 10 })}
  `));
  SCENES.q_lab_osmo = () => scene(420, 300, LAB(`
    ${labBench(20, 232, 200)}${analyzer(40, 232, 130, 96, 'OSMÔMETRO', ['soro: 290 mOsm/kg', 'crioscopia −0,54 °C'], '#1ABC9C')}${tubeRack(176, 232)}
    ${put(BIOMED({ armR: 'show', holdR: 'tube', expr: 'happy' }), 300, 296, 0.8)}
    ${bubble({ x: 150, y: 40, w: 250, h: 60, text: 'O osmômetro mede o abaixamento do ponto de congelamento: quanto mais partículas, mais baixo congela.', tail: [300, 108], size: 10 })}
  `));

  // ======= FISIOLOGIA II — SISTEMAS ORGÂNICOS INTEGRADOS =======
  function box(x, y, w, h, fill, text, size = 9.5, color = OUT) {
    return `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="7" fill="${fill}" ${S}/>${htmlText(x + 2, y, w - 4, h, text, size, 800, color, 'center', 'Baloo 2')}`;
  }
  SCENES.f_cover = () => scene(420, 470, `
    ${plainWall(420, 332, '#FDF2E9')}${floor(420, 332, 138, '#D5DBDB')}<rect x="0" y="230" width="420" height="10" fill="#E74C3C" ${S}/>
    ${whiteboard(26, 34, 226, 124, `${htmlText(6, 4, 214, 28, 'DC = FC × VS', 18, 800, '#C0392B', 'center', 'Baloo 2')}${htmlText(6, 34, 214, 26, 'PA = DC × RVP', 14, 800, '#2E86C1', 'center', 'Baloo 2')}${htmlText(6, 62, 214, 26, 'TFG ≈ 125 mL/min', 13, 800, '#E67E22', 'center', 'Baloo 2')}${htmlText(6, 90, 214, 26, 'TRH → TSH → T₃/T₄ ⊣', 13, 800, '#8E44AD', 'center', 'Baloo 2')}`)}
    ${window_(300, 40, 96, 72)}
    ${labBench(250, 332, 170)}${analyzer(262, 332, 110, 80, 'ANALISADOR', ['Troponina', 'Creatinina'], '#E74C3C')}${tubeRack(340, 332)}
    ${put(PROF({ armL: 'point', armR: 'hold', holdR: 'marker', expr: 'bigsmile', coat: '#FFFFFF', shirt: '#E74C3C' }), 300, 440, 1.0)}
    ${put(BIOMED({ armL: 'hold', holdL: 'clipboard', expr: 'happy' }), 110, 436, 0.78)}
    ${put(BIOMED2({ armR: 'show', holdR: 'tube', expr: 'happy' }), 200, 436, 0.78)}
  `, '', 'xMidYMax slice');

  SCENES.f_feedback = () => scene(420, 240, `
    <rect width="420" height="240" fill="#FFFFFF"/>
    ${htmlText(0, 4, 250, 22, 'Alça de feedback negativo', 11.5, 800, OUT, 'center', 'Baloo 2')}
    ${box(70, 34, 110, 34, '#FFF6B0', 'VARIÁVEL (glicemia, PA, T°)', 8.5)}
    ${box(150, 96, 90, 34, '#D6EAF8', 'SENSOR', 10)}
    ${box(150, 160, 90, 40, '#E8DAEF', 'CENTRO INTEGRADOR (set point)', 8.5)}
    ${box(10, 120, 90, 40, '#D5F5E3', 'EFETOR', 10)}
    ${arrow(180, 68, 190, 94, OUT)}${arrow(195, 132, 195, 158, OUT)}${arrow(148, 178, 100, 150, OUT)}${arrow(55, 118, 100, 70, OUT)}
    ${htmlText(60, 196, 140, 30, 'reverte o desvio → estabiliza', 8.5, 800, '#1E8449')}
    ${htmlText(8, 60, 60, 40, 'desvio detectado', 7.5, 800, '#C0392B')}
    <circle cx="330" cy="120" r="70" fill="#F7C21B" ${S}/>
    <path d="M330 120 L330 50 A70 70 0 0 1 390 155 Z" fill="#5DADE2" ${S}/>
    <path d="M330 120 L390 155 A70 70 0 0 1 335 190 Z" fill="#AED6F1" ${S}/>
    ${htmlText(262, 100, 70, 40, 'LIC ⅔ K⁺', 11, 800, OUT)}${htmlText(338, 78, 60, 40, 'LEC ⅓ Na⁺', 9.5, 800, '#1F618D')}${htmlText(338, 150, 60, 22, 'interstício', 7.5, 800, OUT)}${htmlText(350, 106, 60, 22, 'plasma', 8, 800, '#1F618D')}
    ${htmlText(260, 4, 140, 22, 'Água: 60% do peso', 11, 800, OUT, 'center', 'Baloo 2')}
    ${htmlText(255, 200, 150, 34, 'LEC = meio interno; o plasma é o que o laboratório dosa', 8.5, 800, OUT)}
  `);

  SCENES.f_coracao = () => scene(420, 240, `
    <rect width="420" height="240" fill="#FFFFFF"/>
    <path d="M120 60 Q120 20 160 24 Q200 28 210 60 Q220 28 260 24 Q300 20 300 60 Q300 120 210 200 Q120 120 120 60 Z" fill="#F5B7B1" ${S}/>
    <line x1="210" y1="60" x2="210" y2="190" ${S}/><line x1="130" y1="100" x2="290" y2="100" ${S}/>
    ${htmlText(132, 62, 76, 36, 'AD', 12, 800, '#2E86C1')}${htmlText(214, 62, 76, 36, 'AE', 12, 800, '#C0392B')}${htmlText(140, 118, 68, 36, 'VD', 12, 800, '#2E86C1')}${htmlText(214, 118, 76, 36, 'VE', 12, 800, '#C0392B')}
    <rect x="160" y="96" width="36" height="8" rx="3" fill="#F7C21B" ${S} stroke-width="2"/><rect x="226" y="96" width="36" height="8" rx="3" fill="#F7C21B" ${S} stroke-width="2"/>
    ${htmlText(126, 104, 70, 16, 'tricúspide', 7, 800, OUT)}${htmlText(226, 104, 70, 16, 'mitral', 7, 800, OUT)}
    ${arrow(60, 80, 118, 80, '#2E86C1')}${htmlText(10, 56, 100, 22, 'veias cavas', 8, 800, '#2E86C1')}
    ${arrow(170, 40, 150, 10, '#2E86C1')}${htmlText(80, 2, 100, 22, 'a. pulmonar → pulmões', 7.5, 800, '#2E86C1')}
    ${arrow(300, 80, 360, 80, '#C0392B')}${htmlText(320, 56, 100, 22, 'aorta → corpo', 8, 800, '#C0392B')}
    ${arrow(280, 10, 262, 40, '#C0392B')}${htmlText(262, 2, 110, 22, 'veias pulmonares', 7.5, 800, '#C0392B')}
    ${htmlText(10, 150, 110, 80, 'Circulação pulmonar: coração direito → pulmões. B1 = fecham AV (sístole)', 8.5, 800, '#2E86C1')}
    ${htmlText(300, 150, 115, 80, 'Circulação sistêmica: VE espesso (mais resistência). B2 = fecham semilunares', 8.5, 800, '#C0392B')}
    <rect x="130" y="206" width="160" height="28" rx="6" fill="#FFF6B0" ${S}/>${htmlText(130, 206, 160, 28, 'DC = FC × VS ≈ 5 L/min', 12, 800, OUT, 'center', 'Baloo 2')}
  `);

  SCENES.f_ecg = () => scene(420, 240, `
    <rect width="420" height="240" fill="#FFFFFF"/>
    <rect x="10" y="20" width="400" height="120" fill="#FDEDEC" ${S}/>
    ${Array.from({ length: 20 }, (_, i) => `<line x1="${10 + i * 20}" y1="20" x2="${10 + i * 20}" y2="140" stroke="#F5B7B1" stroke-width="1"/>`).join('')}${Array.from({ length: 6 }, (_, i) => `<line x1="10" y1="${20 + i * 20}" x2="410" y2="${20 + i * 20}" stroke="#F5B7B1" stroke-width="1"/>`).join('')}
    <path d="M20 100 L60 100 Q75 80 90 100 L120 100 L130 108 L140 40 L150 125 L160 100 L200 100 Q220 70 240 100 L280 100 Q295 80 310 100 L340 100 L350 108 L360 40 L370 125 L380 100 L400 100" fill="none" stroke="#C0392B" stroke-width="3"/>
    ${htmlText(60, 58, 40, 20, 'P', 12, 800, '#2E86C1', 'center', 'Baloo 2')}${htmlText(118, 22, 50, 20, 'QRS', 12, 800, '#8E44AD', 'center', 'Baloo 2')}${htmlText(200, 48, 40, 20, 'T', 12, 800, '#1E8449', 'center', 'Baloo 2')}
    ${box(10, 150, 120, 30, '#D6EAF8', 'P: despolarização atrial', 8.5, '#2E86C1')}
    ${box(150, 150, 120, 30, '#E8DAEF', 'QRS: despolarização ventricular', 8, '#8E44AD')}
    ${box(290, 150, 120, 30, '#D5F5E3', 'T: repolarização ventricular', 8, '#1E8449')}
    ${box(10, 196, 74, 30, '#FFF6B0', 'nó SA', 9)}${arrow(86, 211, 98, 211, OUT)}${box(100, 196, 74, 30, '#FFF6B0', 'átrios', 9)}${arrow(176, 211, 188, 211, OUT)}${box(190, 196, 74, 30, '#FFF6B0', 'nó AV (retardo)', 8)}${arrow(266, 211, 278, 211, OUT)}${box(280, 196, 60, 30, '#FFF6B0', 'His', 9)}${arrow(342, 211, 354, 211, OUT)}${box(356, 196, 54, 30, '#FFF6B0', 'Purkinje', 8)}
  `);

  SCENES.f_volumes = () => scene(420, 240, `
    <rect width="420" height="240" fill="#FFFFFF"/>
    ${axes(40, 20, 240, 200, 'tempo', 'volume (L)')}
    <path d="M44 150 q10 -20 20 0 q10 20 20 0 q10 -20 20 0 q10 20 20 0 L150 60 L180 190 L210 150 q10 -20 20 0 q10 20 20 0 L270 150" fill="none" stroke="#2E86C1" stroke-width="3"/>
    <line x1="40" y1="60" x2="280" y2="60" stroke="#BDC3C7" stroke-width="1.5" stroke-dasharray="5 3"/><line x1="40" y1="130" x2="280" y2="130" stroke="#BDC3C7" stroke-width="1.5" stroke-dasharray="5 3"/><line x1="40" y1="150" x2="280" y2="150" stroke="#BDC3C7" stroke-width="1.5" stroke-dasharray="5 3"/><line x1="40" y1="190" x2="280" y2="190" stroke="#BDC3C7" stroke-width="1.5" stroke-dasharray="5 3"/>
    ${htmlText(0, 52, 40, 16, '6', 8, 800, OUT)}${htmlText(0, 182, 40, 16, '1,2', 8, 800, OUT)}${htmlText(0, 212, 40, 16, '0', 8, 800, OUT)}
    ${htmlText(60, 100, 60, 30, 'VRI', 9, 800, '#2E86C1')}${htmlText(124, 140, 30, 18, 'VC', 9, 800, '#C0392B')}${htmlText(60, 160, 60, 30, 'VRE', 9, 800, '#2E86C1')}${htmlText(60, 196, 60, 22, 'VR', 9, 800, '#7F8C8D')}
    <rect x="290" y="20" width="120" height="200" rx="8" fill="#F4F6F7" ${S}/>
    ${htmlText(290, 24, 120, 22, 'Capacidades', 10.5, 800, OUT, 'center', 'Baloo 2')}
    ${htmlText(294, 48, 112, 50, 'CV = VRI + VC + VRE (o máximo mobilizável)', 8.5, 800, '#2E86C1')}
    ${htmlText(294, 100, 112, 40, 'CPT = CV + VR', 8.5, 800, OUT)}
    ${htmlText(294, 140, 112, 76, 'Espirometria: VEF₁/CVF ↓ = obstrutivo (asma, DPOC); volumes ↓ com relação normal = restritivo', 8, 800, '#C0392B')}
  `);

  SCENES.f_digest = () => scene(420, 240, `
    <rect width="420" height="240" fill="#FFFFFF"/>
    ${box(10, 10, 92, 44, '#FFF6B0', 'BOCA: saliva (amilase)', 8.5)}
    ${box(112, 10, 110, 44, '#FADBD8', 'ESTÔMAGO: HCl, pepsina, fator intrínseco', 8)}
    ${box(232, 10, 90, 44, '#D5F5E3', 'DUODENO: bicarbonato neutraliza', 8)}
    ${box(332, 10, 80, 44, '#D6EAF8', 'DELGADO: absorção (vilosidades)', 7.5)}
    ${arrow(102, 32, 110, 32, OUT)}${arrow(222, 32, 230, 32, OUT)}${arrow(322, 32, 330, 32, OUT)}
    ${box(120, 90, 110, 44, '#E8DAEF', 'PÂNCREAS: amilase, lipase, proteases + HCO₃⁻', 7.5)}
    ${box(240, 90, 100, 44, '#F9E79F', 'FÍGADO/VESÍCULA: bile emulsiona gorduras', 7.5)}
    ${arrow(190, 88, 262, 56, '#8E44AD')}${arrow(280, 88, 272, 56, '#B7950B')}
    ${htmlText(10, 92, 100, 44, 'Via porta → fígado (açúcares, aminoácidos); linfa (lipídios)', 7.5, 800, OUT)}
    ${htmlText(0, 146, 420, 20, 'Regulação hormonal', 10.5, 800, OUT, 'center', 'Baloo 2')}
    ${box(10, 170, 125, 56, '#FADBD8', 'GASTRINA → ↑ ácido gástrico', 8.5, '#C0392B')}
    ${box(148, 170, 125, 56, '#D5F5E3', 'SECRETINA → ↑ bicarbonato pancreático', 8.5, '#1E8449')}
    ${box(286, 170, 125, 56, '#E8DAEF', 'CCK → enzimas pancreáticas + contração da vesícula', 8, '#7D3C98')}
  `);

  SCENES.f_eixo = () => scene(420, 240, `
    <rect width="420" height="240" fill="#FFFFFF"/>
    ${box(20, 14, 150, 40, '#E8DAEF', 'HIPOTÁLAMO: TRH', 10, '#7D3C98')}
    ${arrow(95, 56, 95, 78, OUT)}
    ${box(20, 80, 150, 40, '#D6EAF8', 'ADENO-HIPÓFISE: TSH', 10, '#2E86C1')}
    ${arrow(95, 122, 95, 144, OUT)}
    ${box(20, 146, 150, 40, '#FFF6B0', 'TIREOIDE: T₃ e T₄', 10, '#B7950B')}
    ${arrow(95, 188, 95, 206, OUT)}${htmlText(10, 208, 170, 30, '↑ metabolismo basal', 9, 800, OUT)}
    <path d="M172 166 Q215 166 215 120 Q215 34 172 34" fill="none" stroke="#C0392B" stroke-width="3" stroke-dasharray="7 4"/><line x1="166" y1="26" x2="166" y2="42" stroke="#C0392B" stroke-width="4"/>
    <path d="M172 166 Q200 166 200 120 Q200 100 172 100" fill="none" stroke="#C0392B" stroke-width="3" stroke-dasharray="7 4"/><line x1="166" y1="92" x2="166" y2="108" stroke="#C0392B" stroke-width="4"/>
    ${htmlText(196, 194, 74, 40, 'feedback negativo ⊣', 8, 800, '#C0392B')}
    <rect x="270" y="14" width="140" height="210" rx="8" fill="#F4F6F7" ${S}/>
    ${htmlText(270, 18, 140, 22, 'Ler pares hormonais', 10, 800, OUT, 'center', 'Baloo 2')}
    ${box(278, 44, 124, 50, '#FADBD8', 'Hipotireoidismo primário: TSH ↑ · T₄ livre ↓', 8.5, '#C0392B')}
    ${box(278, 102, 124, 50, '#D6EAF8', 'Hipertireoidismo primário: TSH ↓ · T₄ livre ↑', 8.5, '#2E86C1')}
    ${htmlText(278, 158, 124, 64, 'A mesma lógica vale para ACTH → cortisol (ritmo circadiano, mais alto de manhã) e FSH/LH → gônadas', 8, 800, OUT)}
  `);

  SCENES.f_glicemia = () => scene(420, 240, `
    <rect width="420" height="240" fill="#FFFFFF"/>
    ${htmlText(0, 4, 420, 22, 'Glicemia: dois hormônios antagônicos, um feedback negativo', 10.5, 800, OUT, 'center', 'Baloo 2')}
    <line x1="30" y1="130" x2="390" y2="130" stroke="#F7C21B" stroke-width="6"/><polygon points="200,118 215,140 185,140" fill="#2C3E50"/>
    ${box(40, 40, 140, 70, '#FADBD8', 'APÓS A REFEIÇÃO: glicemia ↑ → células β → INSULINA → captação e armazenamento → glicemia ↓', 8, '#C0392B')}
    ${box(240, 40, 140, 70, '#D6EAF8', 'JEJUM: glicemia ↓ → células α → GLUCAGON → fígado libera glicose → glicemia ↑', 8, '#2E86C1')}
    ${arrow(110, 112, 110, 126, '#C0392B')}${arrow(310, 112, 310, 126, '#2E86C1')}
    ${box(20, 160, 180, 64, '#FFF6B0', 'Diabetes tipo 1: falta insulina. Tipo 2: resistência à insulina. Resultado: hiperglicemia crônica', 8.5)}
    ${box(220, 160, 180, 64, '#D5F5E3', 'Laboratório: glicemia de jejum, HbA1c (média de semanas), insulina e peptídeo C', 8.5, '#1E8449')}
  `);

  SCENES.f_ciclo = () => scene(420, 240, `
    <rect width="420" height="240" fill="#FFFFFF"/>
    ${axes(30, 30, 380, 150, 'dias do ciclo (28)', 'hormônios')}
    <rect x="30" y="30" width="190" height="150" fill="#FDEBD0" opacity=".5"/><rect x="220" y="30" width="190" height="150" fill="#E8DAEF" opacity=".5"/>
    <path d="M34 170 Q140 160 200 80 Q215 60 220 110 Q260 150 300 150 Q350 150 400 172" fill="none" stroke="#E67E22" stroke-width="3"/>
    <path d="M34 175 L190 170 L210 40 L228 170 L400 176" fill="none" stroke="#8E44AD" stroke-width="3"/>
    <path d="M34 178 L225 176 Q300 60 340 90 Q380 120 400 176" fill="none" stroke="#1E8449" stroke-width="3"/>
    <path d="M34 150 Q90 120 180 150 Q210 165 230 160 Q300 150 400 160" fill="none" stroke="#2E86C1" stroke-width="2" stroke-dasharray="5 3"/>
    ${htmlText(60, 40, 120, 20, 'FASE FOLICULAR', 9.5, 800, '#B9770E', 'center', 'Baloo 2')}${htmlText(260, 40, 120, 20, 'FASE LÚTEA', 9.5, 800, '#7D3C98', 'center', 'Baloo 2')}
    ${htmlText(150, 100, 60, 20, 'estrogênio', 8, 800, '#E67E22')}${htmlText(180, 28, 70, 20, 'pico de LH', 8.5, 800, '#8E44AD')}${htmlText(300, 62, 80, 20, 'progesterona', 8, 800, '#1E8449')}${htmlText(60, 126, 60, 20, 'FSH', 8, 800, '#2E86C1')}
    <line x1="215" y1="30" x2="215" y2="180" stroke="#C0392B" stroke-width="2" stroke-dasharray="4 3"/>${htmlText(220, 160, 90, 18, 'ovulação ~dia 14', 8, 800, '#C0392B', 'left')}
    ${htmlText(10, 212, 400, 26, 'Útero: menstrual → proliferativa (estrogênio) → secretora (progesterona). Gravidez: hCG mantém o corpo lúteo', 8.5, 800, OUT)}
  `);

  const labCase = (title, lines, color, who, bubbleText, expr = 'happy') => scene(420, 300, LAB(`
    ${labBench(20, 232, 200)}${analyzer(40, 232, 130, 96, title, lines, color)}${tubeRack(176, 232)}
    ${put(who({ armL: 'hold', holdL: 'clipboard', armR: 'point', expr }), 300, 296, 0.8)}
    ${bubble({ x: 150, y: 40, w: 250, h: 60, text: bubbleText, tail: [300, 108], size: 10 })}
  `));
  SCENES.f_lab_tropo = () => labCase('MARCADORES CARDÍACOS', ['Troponina I 0,9 → 2,4 ▲', 'CK-MB ▲ · BNP normal'], '#E74C3C', BIOMED2, 'Troponina em ascensão nas dosagens seriadas: lesão do miócito. A curva temporal é tão importante quanto o valor.', 'worried');
  SCENES.f_lab_renal = () => labCase('FUNÇÃO RENAL', ['Creatinina 3,2 · Ureia 110', 'TFGe 22 mL/min · K⁺ 5,9'], '#E67E22', BIOMED, 'Creatinina e ureia sobem porque a filtração caiu. Potássio alto e acidose metabólica costumam acompanhar.', 'surprised');
  SCENES.f_lab_hepat = () => labCase('PERFIL HEPÁTICO', ['ALT 180 · AST 150 ▲', 'Bilirrubina 4,5 · GGT ▲'], '#B7950B', BIOMED2, 'ALT e AST vêm do hepatócito lesado; GGT e fosfatase alcalina apontam para a via biliar; a bilirrubina explica a icterícia.');
  SCENES.f_lab_tsh = () => labCase('HORMÔNIOS', ['TSH 12,0 ▲', 'T₄ livre 0,5 ▼'], '#8E44AD', BIOMED, 'TSH alto com T₄ livre baixo: a tireoide falhou e a hipófise insiste. É o padrão do hipotireoidismo primário.');
  SCENES.f_lab_hcg = () => labCase('REPRODUTIVO', ['β-hCG 1 250 mUI/mL', 'Progesterona ▲'], '#1ABC9C', BIOMED2, 'hCG do trofoblasto mantém o corpo lúteo produzindo progesterona. Na leitura de FSH, LH e estradiol, a fase do ciclo muda tudo.');

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

  window.ILL = { SCENES, ICON, person, KID, DENTIST, MOM, RECEP, ASSIST, NURSE, put, scene, bubble, render };
})();
