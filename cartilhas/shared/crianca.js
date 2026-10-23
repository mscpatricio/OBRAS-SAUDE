/* ============================================================
   crianca.js — gera a cartilha da criança (história social) a partir
   de window.CONFIG: capa, quem eu vou encontrar, o que tem na sala,
   passos (2 por página), meus sinais + eu consegui, para quem cuida.
   ============================================================ */
(function () {
  const C = window.CONFIG;
  const ICN = (n) => `<div class="ic" data-icon="${n}"></div>`;
  const ill = (s, st = '') => `<div class="ill" data-scene="${s}" style="${st}"></div>`;
  const credit = C.credit; // ex.: "Autoria: Dr. Patrício Almeida"
  const pn = (n, dark) => `<div class="pagenum"${dark ? ' style="color:#0B2A3A"' : ''}><span class="credit">${credit}</span> · ${n}</div>`;
  let html = '';
  let page = 1;

  // capa
  html += `<section class="page cover" style="background:${C.coverColor}">
    <div class="tiles"></div>
    <div class="art">${ill(C.coverScene)}</div>
    <div class="titlebox">
      <div class="hq-title">${C.title}</div>
      <div class="sub">${C.subtitle}</div>
      <div class="name">Eu me chamo <span class="line"></span></div>
    </div>
    <div class="foot"><div class="who">Para ler em casa, todos os dias, antes de ir</div><div class="org">História social ilustrada · ${credit}<br>${C.series}</div></div>
  </section>`;

  // quem eu vou encontrar
  page++;
  html += `<section class="page"><div class="pad">
    <div class="head"><span class="hq-title">Quem eu vou encontrar</span><span class="mini">${C.short}</span></div>
    <div class="people">
      ${C.people.map((p, i) => `<div class="person"${p.full ? ' style="grid-column: 1 / -1; background:#FFF6B0"' : ''}>${ill(p.scene, p.full ? 'height:40mm' : '')}<div><h4>${p.name}</h4><p>${p.text}</p>${p.nameField ? `<p>${p.nameField}</p><span class="line"${p.full ? ' style="width:70mm"' : ''}></span>` : ''}</div></div>`).join('')}
    </div></div>${pn(page)}</section>`;

  // o que tem na sala
  page++;
  html += `<section class="page"><div class="pad">
    <div class="head"><span class="hq-title">${C.roomTitle}</span><span class="mini">${C.short}</span></div>
    <p style="margin:0 0 4mm;font-family:var(--comic);font-weight:700;font-size:11pt">${C.roomIntro}</p>
    <div class="objects">${C.objects.map((o) => `<div class="obj">${ill(o[0])}<div><h4>${o[1]}</h4><p>${o[2]}</p><span class="tag">${o[3]}</span></div></div>`).join('')}</div>
    </div>${pn(page)}</section>`;

  // passos
  for (let i = 0; i < C.steps.length; i += 2) {
    page++;
    html += `<section class="page"><div class="pad"><div class="head"><span class="hq-title">Passo a passo</span><span class="mini">${C.short} · passos ${i + 1}${C.steps[i + 1] ? ` e ${i + 2}` : ''}</span></div>`;
    C.steps.slice(i, i + 2).forEach((st, j) => {
      html += `<div class="step">
        <div class="main"><div class="n">${i + j + 1}</div><p>${st.t}</p></div>
        <div class="body">
          <div class="art">${ill(st.s)}</div>
          <div class="txt">
            <div class="chips feel"><h5>O que eu posso sentir</h5>${st.feel.map((f) => `<div class="chip">${ICN(f[0])}<div>${f[1]}</div></div>`).join('')}</div>
            <div class="chips can"><h5>O que eu posso fazer</h5>${st.can.map((f) => `<div class="chip">${ICN(f[0])}<div>${f[1]}</div></div>`).join('')}</div>
          </div>
        </div></div>`;
    });
    html += `</div>${pn(page)}</section>`;
  }

  // sinais + eu consegui
  page++;
  html += `<section class="page"><div class="pad" style="gap:5mm">
    <div class="head"><span class="hq-title">Meus sinais</span><span class="mini">${C.short}</span></div>
    <p style="margin:0;font-family:var(--comic);font-weight:700;font-size:11.5pt">Eu não preciso falar para ser entendido. Combinei estes sinais com a equipe e com quem cuida de mim. Eles sempre funcionam.</p>
    <div class="sig-big">
      <div class="sig-card">${ill('sig_stop')}<h4>Mão levantada</h4><p><b>PARE.</b> ${C.stopText}</p></div>
      <div class="sig-card">${ill('sig_pause')}<h4>Pausa</h4><p>Quero descansar um pouco, abraçar meu brinquedo e depois continuar.</p></div>
      <div class="sig-card">${ill('sig_ok')}<h4>Polegar para cima</h4><p>Tudo bem, pode continuar.</p></div>
    </div>
    <div class="done-big">
      <h3>Eu consegui!</h3>
      <div class="grid">${C.achievements.map((a) => `<div><span class="checkbox"></span>${a}</div>`).join('')}</div>
      <div style="font-family:var(--title);font-weight:800;font-size:11pt;margin-top:4mm">Carimbos ou adesivos de cada ${C.visitWord}:</div>
      <div class="stamps"><div class="stamp">1ª ${C.visitWord}</div><div class="stamp">2ª ${C.visitWord}</div><div class="stamp">3ª ${C.visitWord}</div><div class="stamp">4ª ${C.visitWord}</div></div>
    </div>
    <div class="tip" style="margin-top:auto"><div class="ic" data-icon="heart"></div><div><b>Cada passo conta.</b> ${C.eachStep}</div></div>
    </div>${pn(page)}</section>`;

  // para quem cuida (resumo) + mini-card
  page++;
  html += `<section class="page back"><div class="pad" style="gap:4mm">
    <div class="row" style="justify-content:space-between;align-items:flex-start">
      <div><h2>Para quem cuida: como usar esta cartilha</h2><p>Esta cartilha é uma <b>história social</b>: conta, em primeira pessoa e com figuras, exatamente o que vai acontecer, o que a criança pode sentir e o que ela pode fazer. Saber o que vem a seguir diminui a ansiedade. ${C.familyNote}</p></div>
      ${ill('momKid', 'width:30mm;height:36mm;flex:0 0 30mm')}
    </div>
    <div class="agenda">${C.agenda}</div>
    <div class="grid2">
      <div class="box" style="padding:5mm"><h3>Antes</h3><ul>${C.familyBefore.map((f) => `<li>${ICN(f[0])}<div>${f[1]}</div></li>`).join('')}</ul></div>
      <div class="box" style="padding:5mm"><h3>No dia e depois</h3><ul>${C.familyDay.map((f) => `<li>${ICN(f[0])}<div>${f[1]}</div></li>`).join('')}</ul></div>
    </div>
    <div class="cutline"></div>
    <div style="font-family:var(--title);font-weight:800;font-size:10.5pt;margin:-1mm 0 1mm">Mini-card para a carteira ou a geladeira</div>
    <div class="minicard">${C.mini.map((m, i) => `<div class="m">${ill(m[0])}<span class="n">${i + 1}</span>${m[1]}</div>`).join('')}</div>
    <div class="small center" style="margin-top:auto">Material educativo · ${C.series}. ${credit}. Pode ser reproduzido gratuitamente para fins educativos.</div>
    </div>${pn(page)}</section>`;

  document.getElementById('book').outerHTML = html;
})();
