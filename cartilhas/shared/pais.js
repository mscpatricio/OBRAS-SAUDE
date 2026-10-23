/* ============================================================
   pais.js — gera a cartilha para pais e cuidadores a partir de
   window.CONFIG: capa, por que preparar, antes, no dia, depois,
   sinais e crise, direitos e perguntas frequentes, checklist e ficha.
   ============================================================ */
(function () {
  const C = window.CONFIG;
  const ICN = (n) => `<div class="ic" data-icon="${n}"></div>`;
  const ill = (s, st = '') => `<div class="ill" data-scene="${s}" style="${st}"></div>`;
  const credit = C.credit;
  const pn = (n, dark) => `<div class="pagenum"${dark ? ' style="color:#0B2A3A"' : ''}><span class="credit">${credit}</span> · ${n}</div>`;
  const box = (title, items, extra = '') => `<div class="box compact" ${extra}><h3>${title}</h3><ul>${items.map((f) => `<li>${ICN(f[0])}<div><b>${f[1]}</b> ${f[2]}</div></li>`).join('')}</ul></div>`;
  let html = '';

  // capa
  html += `<section class="page cover" style="background:${C.coverColor}">
    <div class="tiles"></div>
    <div class="art">${ill(C.coverScene)}</div>
    <div class="titlebox"><div class="hq-title">${C.title}</div><div class="sub">${C.subtitle}</div></div>
    <div class="badge"><span class="label">${C.badge}</span></div>
    <div class="foot"><div class="who">Para pais, mães, cuidadores e familiares</div><div class="org">Material educativo · ${credit}<br>${C.series}</div></div>
  </section>`;

  // 2 — por que preparar
  html += `<section class="page"><div class="pad intro" style="display:flex;flex-direction:column;gap:4mm">
    <div><h2>${C.whyTitle}</h2>${C.why.map((p) => `<p>${p}</p>`).join('')}</div>
    <div class="kit">${ill(C.kitScene)}<div><h4>${C.kitTitle}</h4><p>${C.kitText}</p></div></div>
    <div class="moments">
      <div class="moment antes"><b>ANTES</b>${C.momentBefore}</div>
      <div class="moment durante"><b>NO DIA</b>${C.momentDay}</div>
      <div class="moment depois"><b>DEPOIS</b>${C.momentAfter}</div>
    </div>
    <div class="box" style="padding:4mm 6mm;box-shadow:none;background:#FAFAFA"><h3 style="font-size:13pt;margin-bottom:2mm">O que você encontra aqui</h3>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:1mm 8mm;font-size:10pt">${C.toc.map((t, i) => `<div><b>${i + 3}</b> · ${t}</div>`).join('')}</div></div>
    <div class="tip"><div class="ic" data-icon="heart"></div><div><b>Regra de ouro:</b> previsibilidade, uma coisa de cada vez e nunca forçar. Você conhece seu filho melhor do que ninguém: você é parte da equipe.</div></div>
    <div class="small">${C.legal}</div>
    </div>${pn(2)}</section>`;

  // 3 — antes
  html += `<section class="page m-antes"><div class="strip"></div><div class="content">
    <div class="section-head"><div class="num">1</div><div><div class="hq-title">ANTES de ir</div><div class="sub">${C.beforeSub}</div></div></div>
    <div class="panels two">
      <div class="panel-wrap"><div class="panel" style="height:70mm">${ill(C.beforeScenes[0][0])}</div><div class="caption">${C.beforeScenes[0][1]}</div></div>
      <div class="panel-wrap"><div class="panel" style="height:70mm">${ill(C.beforeScenes[1][0])}</div><div class="caption">${C.beforeScenes[1][1]}</div></div>
    </div>
    <div style="height:4mm"></div>
    ${box('O que fazer antes', C.before)}
    <div class="fill"></div>
    <div class="tip">${ICN(C.beforeTip[0])}<div><b>${C.beforeTip[1]}</b> ${C.beforeTip[2]}</div></div>
    </div>${pn(3)}</section>`;

  // 4 — no dia
  html += `<section class="page m-durante"><div class="strip"></div><div class="content">
    <div class="section-head"><div class="num">2</div><div><div class="hq-title">NO DIA</div><div class="sub">${C.daySub}</div></div></div>
    <div class="panels two">
      <div class="panel-wrap"><div class="panel" style="height:70mm">${ill(C.dayScenes[0][0])}</div><div class="caption">${C.dayScenes[0][1]}</div></div>
      <div class="panel-wrap"><div class="panel" style="height:70mm">${ill(C.dayScenes[1][0])}</div><div class="caption">${C.dayScenes[1][1]}</div></div>
    </div>
    <div style="height:4mm"></div>
    ${box('Como ajudar no dia', C.day)}
    <div class="fill"></div>
    <div class="tip">${ICN(C.dayTip[0])}<div><b>${C.dayTip[1]}</b> ${C.dayTip[2]}</div></div>
    </div>${pn(4)}</section>`;

  // 5 — sinais, sobrecarga e crise
  html += `<section class="page m-crise"><div class="strip"></div><div class="content">
    <div class="section-head"><div class="num">3</div><div><div class="hq-title">Sinais, sobrecarga e crise</div><div class="sub">Como perceber, o que fazer e o que combinar com a equipe</div></div></div>
    <div class="panels two">
      <div class="panel-wrap"><div class="panel" style="height:62mm">${ill('overload')}</div><div class="caption">O que leva à sobrecarga: barulho, luz forte, gente demais, toques sem aviso e espera sem fim.</div></div>
      <div class="panel-wrap"><div class="panel" style="height:62mm">${ill('stopSign')}</div><div class="caption">Mão levantada é PARE. Combine com a equipe: quando ele levanta a mão, todo mundo para e respira.</div></div>
    </div>
    <div style="height:4mm"></div>
    <div class="grid3" style="gap:4mm">
      <div class="box" style="padding:3mm 4mm;box-shadow:none;text-align:center">${ill('sig_stop', 'width:14mm;height:14mm;margin:0 auto 1mm')}<b style="font-family:var(--title)">Mão levantada</b><br><span style="font-family:var(--comic);font-weight:700;font-size:9.5pt">PARE. A equipe para na hora.</span></div>
      <div class="box" style="padding:3mm 4mm;box-shadow:none;text-align:center">${ill('sig_pause', 'width:14mm;height:14mm;margin:0 auto 1mm')}<b style="font-family:var(--title)">Pausa</b><br><span style="font-family:var(--comic);font-weight:700;font-size:9.5pt">Quero descansar um pouco.</span></div>
      <div class="box" style="padding:3mm 4mm;box-shadow:none;text-align:center">${ill('sig_ok', 'width:14mm;height:14mm;margin:0 auto 1mm')}<b style="font-family:var(--title)">Polegar</b><br><span style="font-family:var(--comic);font-weight:700;font-size:9.5pt">Tudo bem, pode continuar.</span></div>
    </div>
    <div style="height:4mm"></div>
    ${box('Se a crise acontecer', C.crisis)}
    <div class="fill"></div>
    <div class="tip red">${ICN('warn')}<div><b>Nunca é culpa sua nem dele.</b> A crise de sobrecarga não é birra nem falta de limite. Terminar o atendimento mais cedo e voltar outro dia também é um bom resultado.</div></div>
    </div>${pn(5)}</section>`;

  // 6 — depois
  html += `<section class="page m-depois"><div class="strip"></div><div class="content">
    <div class="section-head"><div class="num">4</div><div><div class="hq-title">DEPOIS</div><div class="sub">${C.afterSub}</div></div></div>
    <div class="panels two">
      <div class="panel-wrap"><div class="panel" style="height:70mm">${ill(C.afterScenes[0][0])}</div><div class="caption">${C.afterScenes[0][1]}</div></div>
      <div class="panel-wrap"><div class="panel" style="height:70mm">${ill(C.afterScenes[1][0])}</div><div class="caption">${C.afterScenes[1][1]}</div></div>
    </div>
    <div style="height:4mm"></div>
    ${box('O que fazer depois', C.after)}
    <div class="fill"></div>
    <div class="tip">${ICN(C.afterTip[0])}<div><b>${C.afterTip[1]}</b> ${C.afterTip[2]}</div></div>
    </div>${pn(6)}</section>`;

  // 7 — direitos e perguntas frequentes
  html += `<section class="page info" style="background:${C.infoColor}"><div class="stripes" style="background:repeating-linear-gradient(135deg, ${C.infoStripe} 0 10px, transparent 10px 20px)"></div><div class="content"><div class="dashed-box">
    <span class="hq-title white">Direitos e dúvidas</span>
    <h4>Seus direitos</h4>
    <ul style="margin:0 0 2mm;padding-left:5mm">${C.rights.map((r) => `<li>${r}</li>`).join('')}</ul>
    <h4>Perguntas frequentes</h4>
    ${C.faq.map((f) => `<p><b>${f[0]}</b><br>${f[1]}</p>`).join('')}
    <div class="fill"></div>
    <p style="margin:0;font-size:9pt">${credit}. Material educativo; não substitui a orientação da equipe de saúde que acompanha a pessoa com TEA.</p>
    </div></div>${pn(7, true)}</section>`;

  // 8 — checklist do dia + passaporte
  html += `<section class="page"><div class="pad ficha" style="display:flex;flex-direction:column;gap:3mm">
    <h2>Checklist do dia e “passaporte” do TEA</h2>
    <div class="small">Marque antes de sair de casa. Recorte e entregue o passaporte à equipe na chegada: ele conta, em uma folha, como cuidar bem do seu filho.</div>
    <div class="grid2">
      <div class="box" style="padding:4mm 5mm"><h3 style="font-size:13pt">Para levar</h3><div class="opts">${C.bring.map((b) => `<div><span class="checkbox"></span>${b}</div>`).join('')}</div></div>
      <div class="box" style="padding:4mm 5mm"><h3 style="font-size:13pt">Para fazer antes</h3><div class="opts">${C.doBefore.map((b) => `<div><span class="checkbox"></span>${b}</div>`).join('')}</div></div>
    </div>
    <div class="cutline"></div>
    <div class="passport">
      <h3>Passaporte do TEA: como cuidar bem de <span class="line" style="width:50mm"></span></h3>
      <div class="pgrid">
        <div><b>Idade:</b> <span class="line" style="width:14mm"></span> &nbsp; <b>Responsável:</b> <span class="line" style="width:46mm"></span> &nbsp; <b>Tel.:</b> <span class="line" style="width:30mm"></span></div>
        <div><b>Como se comunica:</b> <span class="checkbox"></span>Fala <span class="checkbox"></span>Figuras <span class="checkbox"></span>Gestos <span class="checkbox"></span>Tablet &nbsp; <b>Como diz “sim”, “não” e “dor”:</b> <span class="line" style="width:40mm"></span></div>
        <div><b>O que incomoda:</b> <span class="checkbox"></span>Sons <span class="checkbox"></span>Luz <span class="checkbox"></span>Cheiros <span class="checkbox"></span>Toque <span class="checkbox"></span>Pessoas novas <span class="checkbox"></span>Esperar &nbsp; Outros: <span class="line" style="width:40mm"></span></div>
        <div><b>O que acalma:</b> <span class="line" style="width:70mm"></span> &nbsp; <b>Objeto de conforto:</b> <span class="line" style="width:40mm"></span></div>
        <div><b>Gosta de (use para explicar e recompensar):</b> <span class="line" style="width:100mm"></span></div>
        <div><b>Sinais de que vai ter crise:</b> <span class="line" style="width:60mm"></span> &nbsp; <b>O que fazer:</b> <span class="line" style="width:50mm"></span></div>
        <div><b>Já funcionou:</b> <span class="checkbox"></span>Fones <span class="checkbox"></span>Óculos <span class="checkbox"></span>Colo <span class="checkbox"></span>Contagem <span class="checkbox"></span>História lida <span class="checkbox"></span>Vídeo &nbsp; <b>Sinal de PARE:</b> <span class="line" style="width:30mm"></span></div>
        <div><b>Alimentos aceitos:</b> <span class="line" style="width:60mm"></span> &nbsp; <b>Medicações / outras condições:</b> <span class="line" style="width:50mm"></span></div>
        <div><b>Experiências anteriores (o que deu certo e o que deu errado):</b> <span class="line" style="width:86mm"></span></div>
      </div>
    </div>
    <div class="small center" style="margin-top:auto">${C.series} · ${credit} · Pode ser reproduzido gratuitamente para fins educativos.</div>
    </div>${pn(8)}</section>`;

  document.getElementById('book').outerHTML = html;
})();
