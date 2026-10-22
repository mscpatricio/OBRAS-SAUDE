/* ============================================================
   App "Minha visita ao dentista" — perfis Dentista e Criança
   Vanilla JS, sem build. Dados ficam só no aparelho (localStorage).
   ============================================================ */
(function () {
  const D = window.DATA;
  const $ = (sel) => document.querySelector(sel);
  const esc = (t) => String(t == null ? '' : t).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  const CREDIT = 'Coautoria: <b>Dr. Patrício Almeida</b> · Material educativo sobre atendimento odontológico à pessoa com TEA';

  // ---------- armazenamento ----------
  const store = {
    get(k, def) { try { const v = localStorage.getItem('tea.' + k); return v ? JSON.parse(v) : def; } catch (e) { return def; } },
    set(k, v) { try { localStorage.setItem('tea.' + k, JSON.stringify(v)); } catch (e) { /* sem espaço */ } },
  };
  const child = () => store.get('child', { name: '', voice: true, done: {}, achievements: {}, visits: [] });
  const saveChild = (c) => store.set('child', c);
  const dentist = () => store.get('dentist', { patients: [], checks: {}, schedule: {} });
  const saveDentist = (d) => store.set('dentist', d);

  // ---------- voz (leitura em voz alta) ----------
  function speak(text) {
    if (!('speechSynthesis' in window)) return toast('Este aparelho não tem leitura em voz alta.');
    const c = child();
    if (c.voice === false) return;
    window.speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(text);
    u.lang = 'pt-BR'; u.rate = 0.9;
    const v = window.speechSynthesis.getVoices().find((x) => /pt(-|_)BR/i.test(x.lang));
    if (v) u.voice = v;
    window.speechSynthesis.speak(u);
  }
  function toast(msg) {
    const t = $('#toast'); t.textContent = msg; t.classList.add('show');
    clearTimeout(t._h); t._h = setTimeout(() => t.classList.remove('show'), 1800);
  }
  function vibrate(p) { try { navigator.vibrate && navigator.vibrate(p); } catch (e) { /* ignore */ } }

  // ---------- helpers de UI ----------
  const ill = (scene, cls = '') => `<div class="ill ${cls}" data-scene="${scene}"></div>`;
  const ico = (name) => `<div class="ic" data-icon="${name}"></div>`;
  const btn = (href, label, opts = {}) =>
    `<a class="btn ${opts.cls || ''}" href="${href}">${opts.scene ? ill(opts.scene) : opts.icon ? ico(opts.icon) : ''}<span class="lbl">${label}${opts.sub ? `<small>${opts.sub}</small>` : ''}</span></a>`;
  const credit = () => `<p class="muted center" style="margin-top:18px">${CREDIT}</p>`;

  function setTop(title, back, extra = '') {
    $('#topbar').innerHTML = `${back ? `<a class="back" href="${back}" aria-label="Voltar">←</a>` : '<span class="spacer"></span>'}<h1>${title}</h1>${extra || '<span class="spacer"></span>'}`;
  }
  function render(html, nav = '') {
    $('#main').innerHTML = html + (nav ? `<div class="navbar"><div class="inner">${nav}</div></div>` : '');
    window.ILL.render();
    window.scrollTo(0, 0);
  }

  // ============================================================
  // TELAS
  // ============================================================
  const V = {};

  // ---------- escolha de perfil ----------
  V.home = () => {
    document.body.className = '';
    setTop('Minha visita ao dentista', null);
    render(`
      <div class="profile-pick">
        <div class="hero">${ill('cardCover')}</div>
        <p class="muted center">Escolha como você vai usar o app:</p>
        ${btn('#/crianca', 'Sou a criança / família', { scene: 'p_kid', sub: 'Minha história, meus sinais e “Eu consegui!”', cls: 'yellow' })}
        ${btn('#/dentista', 'Sou o dentista / equipe', { scene: 'p_dentist', sub: 'Antes, durante e depois; fichas; modo consulta', cls: 'blue' })}
        <div class="card" style="margin-top:6px"><p class="muted" style="margin:0">Funciona sem internet depois de aberto uma vez. No celular, use “Adicionar à tela de início” para instalar.</p></div>
        ${credit()}
      </div>`);
  };

  // ---------- CRIANÇA ----------
  V.crianca = () => {
    document.body.className = 'profile-crianca';
    const c = child();
    setTop(c.name ? `Oi, ${esc(c.name)}!` : 'Minha visita ao dentista', '#/', `<a class="back" href="#/crianca/config" aria-label="Ajustes">⚙</a>`);
    const total = D.steps.length, doneN = Object.values(c.done).filter(Boolean).length;
    render(`
      ${btn('#/crianca/historia/1', 'Minha história', { scene: 'c7_open', sub: doneN ? `${doneN} de ${total} passos já aconteceram` : `${total} passos, do começo ao fim`, cls: 'yellow' })}
      ${btn('#/crianca/sinais', 'Meus sinais', { scene: 'sig_stop', sub: 'PARE · Pausa · Tudo bem', cls: 'red' })}
      ${btn('#/crianca/pessoas', 'Quem eu vou encontrar', { scene: 'p_dentist_mask', sub: 'O dentista, o auxiliar, a recepção' })}
      ${btn('#/crianca/sala', 'O que tem na sala', { scene: 'o_chair', sub: 'Cadeira, luz, espelhinho, canudinho…' })}
      ${btn('#/crianca/consegui', 'Eu consegui!', { scene: 'c9_gift', sub: 'Minhas conquistas e estrelas', cls: 'green' })}
      ${credit()}`);
    fab();
  };

  V.config = () => {
    const c = child();
    setTop('Ajustes', '#/crianca');
    render(`
      <div class="card">
        <div class="field"><label>Meu nome</label><input id="cfg-name" value="${esc(c.name)}" placeholder="Como você se chama?"></div>
        <button class="check big ${c.voice !== false ? 'on' : ''}" id="cfg-voice"><span class="box">${c.voice !== false ? '✓' : ''}</span><div><b>Ler em voz alta</b><span>O app lê cada passo quando você toca em “Ouvir”.</span></div></button>
        <a class="btn small" href="#/crianca" id="cfg-save">Salvar</a>
      </div>
      <div class="card">
        <h2>Recomeçar</h2>
        <p class="muted">Desmarca os passos que “já aconteceram”, para a próxima consulta.</p>
        <button class="btn small ghost" id="cfg-reset">Desmarcar os passos</button>
      </div>
      ${credit()}`);
    $('#cfg-voice').onclick = () => { const cc = child(); cc.voice = cc.voice === false; saveChild(cc); V.config(); };
    $('#cfg-save').onclick = () => { const cc = child(); cc.name = $('#cfg-name').value.trim(); saveChild(cc); toast('Salvo!'); };
    $('#cfg-reset').onclick = () => { const cc = child(); cc.done = {}; saveChild(cc); toast('Passos desmarcados.'); };
  };

  V.historia = (n) => {
    n = Math.min(Math.max(parseInt(n, 10) || 1, 1), D.steps.length);
    const st = D.steps[n - 1], c = child(), done = !!c.done[n];
    setTop(`Passo ${n} de ${D.steps.length}`, '#/crianca');
    const prog = D.steps.map((_, i) => `<i class="${c.done[i + 1] ? 'done' : ''} ${i + 1 === n ? 'cur' : ''}"></i>`).join('');
    render(`
      <div class="step-view">
        <div class="progress">${prog}</div>
        <div class="art">${ill(st.s)}</div>
        <div class="sentence"><div class="n">${n}</div><p>${st.t}</p></div>
        <div class="row" style="margin-bottom:12px">
          <button class="btn small blue" id="st-speak">🔊 Ouvir</button>
          <button class="btn small ${done ? 'green' : ''}" id="st-done">${done ? '✓ Já aconteceu' : 'Já aconteceu?'}</button>
        </div>
        <div class="chips feel"><h5>O que eu posso sentir</h5>${st.feel.map((f) => `<div class="chip">${ico(f[0])}<div>${f[1]}</div></div>`).join('')}</div>
        <div class="chips can"><h5>O que eu posso fazer</h5>${st.can.map((f) => `<div class="chip">${ico(f[0])}<div>${f[1]}</div></div>`).join('')}</div>
      </div>`,
      `<a class="btn icon-only" href="#/crianca/historia/${n - 1}" ${n === 1 ? 'style="visibility:hidden"' : ''}>◀</a>
       <a class="btn primary" href="${n === D.steps.length ? '#/crianca/consegui' : `#/crianca/historia/${n + 1}`}">${n === D.steps.length ? 'Terminei! ⭐' : 'Próximo passo ▶'}</a>`);
    $('#st-speak').onclick = () => speak(`Passo ${n}. ${st.t} O que eu posso sentir: ${st.feel.map((f) => f[1]).join(' ')} O que eu posso fazer: ${st.can.map((f) => f[1]).join(' ')}`);
    $('#st-done').onclick = () => { const cc = child(); cc.done[n] = !cc.done[n]; saveChild(cc); vibrate(30); V.historia(n); };
    fab();
  };

  V.sinais = () => {
    setTop('Meus sinais', '#/crianca');
    render(`
      <p style="font-family:var(--comic);font-weight:700;font-size:17px;margin:0 0 12px">Toque em um sinal para mostrar ao dentista na tela inteira.</p>
      <div class="signal-grid">
        ${D.signals.map((s, i) => `<button class="signal" data-sig="${i}">${ill(s[0])}<div><h3>${s[1]}</h3><p>${s[2]}</p></div></button>`).join('')}
      </div>
      ${credit()}`);
    document.querySelectorAll('[data-sig]').forEach((b) => (b.onclick = () => showSignal(+b.dataset.sig)));
  };

  function showSignal(i) {
    const s = D.signals[i];
    vibrate(i === 0 ? [80, 40, 80] : 40);
    $('#overlay').innerHTML = `<div class="fullsignal" style="background:${s[3]}">${ill(s[0])}<h2>${s[1]}</h2><p>${s[2]}</p><button class="btn" id="sig-close">Fechar</button></div>`;
    window.ILL.render();
    speak(s[1]);
    $('#sig-close').onclick = () => { $('#overlay').innerHTML = ''; };
  }
  function fab() {
    $('#main').insertAdjacentHTML('beforeend', `<button class="fab" id="fab" aria-label="PARE">${ico('stop')}</button>`);
    window.ILL.render();
    $('#fab').onclick = () => showSignal(0);
  }

  V.pessoas = () => {
    setTop('Quem eu vou encontrar', '#/crianca');
    const c = child(); c.names = c.names || {};
    render(`${D.people.map((p) => `<div class="card person">${ill(p[0])}<div><h3>${p[1]}</h3><p>${p[2]}</p>${p[3] ? `<input data-name="${p[3]}" value="${esc(c.names[p[3]] || '')}" placeholder="Nome">` : ''}</div></div>`).join('')}${credit()}`);
    document.querySelectorAll('[data-name]').forEach((inp) => (inp.onchange = () => { const cc = child(); cc.names = cc.names || {}; cc.names[inp.dataset.name] = inp.value; saveChild(cc); toast('Salvo!'); }));
  };

  V.sala = () => {
    setTop('O que tem na sala', '#/crianca');
    render(`
      <p style="font-family:var(--comic);font-weight:700;font-size:16px;margin:0 0 12px">Antes de usar qualquer coisa, o dentista me mostra, deixa eu tocar e explica. Nada acontece de surpresa.</p>
      <div class="gallery">${D.objects.map((o) => `<div class="tile">${ill(o[0])}<h4>${o[1]}</h4><p>${o[2]}</p><span class="tag">${o[3]}</span></div>`).join('')}</div>${credit()}`);
  };

  V.consegui = () => {
    const c = child();
    const n = Object.values(c.achievements).filter(Boolean).length;
    setTop('Eu consegui!', '#/crianca');
    render(`
      <div class="card center"><div class="stars">${'⭐'.repeat(Math.min(n, 12)) || '☆'}</div><p class="muted">${n} de ${D.achievements.length} conquistas · ${c.visits.length} visita(s) registrada(s)</p></div>
      ${D.achievements.map((a, i) => `<button class="check big ${c.achievements[i] ? 'on' : ''}" data-ach="${i}"><span class="box">${c.achievements[i] ? '✓' : ''}</span><div><b>${a}</b></div></button>`).join('')}
      <div class="card">
        <h2>Minhas visitas</h2>
        ${c.visits.length ? `<ol>${c.visits.map((v) => `<li>${esc(v)}</li>`).join('')}</ol>` : '<p class="muted">Quando terminar uma consulta, registre aqui e ganhe uma estrela.</p>'}
        <button class="btn small green" id="add-visit">⭐ Registrar visita de hoje</button>
      </div>
      ${credit()}`);
    document.querySelectorAll('[data-ach]').forEach((b) => (b.onclick = () => { const cc = child(); cc.achievements[b.dataset.ach] = !cc.achievements[b.dataset.ach]; saveChild(cc); vibrate(30); V.consegui(); }));
    $('#add-visit').onclick = () => { const cc = child(); cc.visits.push(new Date().toLocaleDateString('pt-BR')); saveChild(cc); speak('Parabéns! Você conseguiu!'); V.consegui(); };
  };

  // ---------- DENTISTA ----------
  V.dentista = () => {
    document.body.className = 'profile-dentista';
    const d = dentist();
    setTop('Perfil do dentista', '#/');
    render(`
      ${btn('#/dentista/consulta', 'Modo consulta', { scene: 'countTeeth', sub: 'Contagem em voz alta, sinais, sequência visual', cls: 'yellow' })}
      ${btn('#/dentista/lista/antes', 'Antes da consulta', { scene: 'before_phone', sub: 'Entrevista, vídeo, agenda, ambiente', cls: 'blue' })}
      ${btn('#/dentista/lista/durante', 'Durante a consulta', { scene: 'tellShowDo', sub: 'Acolhimento, Falar–Mostrar–Fazer, limites', cls: 'green' })}
      ${btn('#/dentista/lista/depois', 'Depois da consulta', { scene: 'reward', sub: 'Brinde, higiene em casa, registro, retorno' })}
      ${btn('#/dentista/pacientes', 'Pacientes', { scene: 'record', sub: d.patients.length ? `${d.patients.length} cadastrado(s)` : 'Perfil sensorial e registro das consultas', cls: 'purple' })}
      ${btn('#/dentista/info', 'Informativo', { scene: 'overload', sub: 'O TEA no consultório, o que dizer e evitar' })}
      ${btn('#/crianca', 'Mostrar a história para a criança', { scene: 'p_kid', sub: 'Abre o perfil Criança neste aparelho' })}
      ${credit()}`);
  };

  V.lista = (key) => {
    const L = D.checklists[key]; if (!L) return go('#/dentista');
    const d = dentist(); const ch = d.checks[key] || {};
    setTop(L.title, '#/dentista');
    render(`
      <div class="card" style="padding:0;overflow:hidden;border-color:${L.color}"><div style="aspect-ratio:1.4">${ill(L.scene)}</div></div>
      ${L.items.map((it, i) => `<button class="check ${ch[i] ? 'on' : ''}" data-i="${i}"><span class="box">${ch[i] ? '✓' : ''}</span>${ico(it[0])}<div><b>${it[1]}</b><span>${it[2]}</span></div></button>`).join('')}
      <button class="btn small ghost" id="clear">Limpar marcações</button>
      ${credit()}`);
    document.querySelectorAll('[data-i]').forEach((b) => (b.onclick = () => { const dd = dentist(); dd.checks[key] = dd.checks[key] || {}; dd.checks[key][b.dataset.i] = !dd.checks[key][b.dataset.i]; saveDentist(dd); V.lista(key); }));
    $('#clear').onclick = () => { const dd = dentist(); dd.checks[key] = {}; saveDentist(dd); V.lista(key); };
  };

  V.info = () => {
    setTop('Informativo', '#/dentista');
    render(`
      <div class="card"><h2>O TEA no consultório</h2><p>O autismo é um espectro: cada pessoa é única. Nos níveis de suporte 1 e 2, o paciente geralmente se comunica (com fala, figuras ou gestos) e consegue ser atendido no consultório comum, desde que haja preparo, previsibilidade e respeito ao ritmo dele.</p>
        ${D.info.map((i) => `<p><b>${i[0]}:</b> ${i[1]}</p>`).join('')}</div>
      <h2 style="margin:6px 0 10px">O que dizer e o que evitar</h2>
      ${D.avoidPrefer.map((r) => `<div class="ap"><div class="no">${r[0]}</div><div class="yes">${r[1]}</div></div>`).join('')}
      <div class="card" style="margin-top:14px"><h2>Sinais de sobrecarga sensorial</h2><p>${D.overloadSigns}</p></div>
      <div class="card"><h2>Sinais combinados com a criança</h2><div class="signal-grid">${D.signals.map((s) => `<div class="signal" style="box-shadow:none">${ill(s[0])}<div><h3>${s[1]}</h3><p>${s[2]}</p></div></div>`).join('')}</div></div>
      <div class="card"><h2>Base das recomendações</h2><p class="muted">Falar–Mostrar–Fazer (tell-show-do), dessensibilização sistemática, histórias sociais, apoio visual (PECS) e reforço positivo, recomendados na odontopediatria e na odontologia para pacientes com necessidades especiais. Material educativo; não substitui a avaliação clínica individual.</p></div>
      ${credit()}`);
  };

  // pacientes
  V.pacientes = () => {
    const d = dentist();
    setTop('Pacientes', '#/dentista');
    render(`
      <a class="btn primary" href="#/dentista/paciente/novo">＋ Novo paciente</a>
      ${d.patients.length ? d.patients.map((p) => `<a class="btn" href="#/dentista/paciente/${p.id}">${ico('family')}<span class="lbl">${esc(p.nome || 'Sem nome')}<small>${esc([p.idade && `${p.idade} anos`, p.nivel && `nível ${p.nivel}`].filter(Boolean).join(' · '))} · ${(p.consultas || []).length} consulta(s)</small></span></a>`).join('') : '<div class="card"><p class="muted">Nenhum paciente ainda. Cadastre o perfil sensorial na entrevista com a família e registre cada consulta.</p></div>'}
      <p class="muted">Os dados ficam somente neste aparelho. Use “Copiar ficha” para levar ao prontuário.</p>
      ${credit()}`);
  };

  V.paciente = (id) => {
    const d = dentist();
    const isNew = id === 'novo';
    const p = isNew ? { id: 'p' + Date.now(), consultas: [] } : d.patients.find((x) => x.id === id);
    if (!p) return go('#/dentista/pacientes');
    setTop(isNew ? 'Novo paciente' : esc(p.nome || 'Paciente'), '#/dentista/pacientes');
    const field = (f) => {
      const [k, label, type, opts, ph] = f; const v = esc(p[k] || '');
      if (type === 'select') return `<div class="field"><label>${label}</label><select data-k="${k}"><option value="">—</option>${opts.map((o) => `<option ${p[k] === o ? 'selected' : ''}>${o}</option>`).join('')}</select></div>`;
      if (type === 'textarea') return `<div class="field"><label>${label}</label><textarea data-k="${k}" placeholder="${ph || ''}">${v}</textarea></div>`;
      return `<div class="field"><label>${label}</label><input type="${type}" data-k="${k}" value="${v}" placeholder="${ph || ''}"></div>`;
    };
    const consultasHtml = (p.consultas || []).length
      ? p.consultas.map((c, i) => `<div class="check" style="display:block"><b>${esc(c.data || '')} · ${esc(c.degrau || '')}</b><span><b>Funcionou:</b> ${esc(c.funcionou || '—')}<br><b>Próximo passo:</b> ${esc(c.proximo || '—')}</span><br><button class="btn small ghost" data-del="${i}" style="margin-top:6px">Apagar</button></div>`).join('')
      : '<p class="muted">Nenhuma consulta registrada.</p>';
    const today = new Date().toISOString().slice(0, 10);
    const consultaForm = D.consultaFields.map((f) => {
      if (f[2] === 'textarea') return `<div class="field"><label>${f[1]}</label><textarea data-c="${f[0]}"></textarea></div>`;
      if (f[0] === 'degrau') return `<div class="field"><label>${f[1]}</label><select data-c="degrau"><option value="">—</option>${D.ladder.map((l) => `<option>${l}</option>`).join('')}<option>Só ambientação</option></select></div>`;
      return `<div class="field"><label>${f[1]}</label><input type="${f[2]}" data-c="${f[0]}" value="${f[2] === 'date' ? today : ''}"></div>`;
    }).join('');
    const registro = isNew ? '' : `<div class="card"><h2>Registro das consultas</h2>${consultasHtml}
        <h3 style="margin:10px 0 6px;font-size:16px">Nova consulta</h3>${consultaForm}
        <button class="btn small green" id="c-add">＋ Registrar consulta</button></div>
      <button class="btn small ghost" id="p-del" style="color:var(--red)">Excluir paciente</button>`;
    render(`
      <div class="card"><h2>Perfil sensorial</h2>${D.patientFields.map(field).join('')}
        <div class="row"><button class="btn small primary" id="p-save">Salvar</button><button class="btn small" id="p-copy">Copiar ficha</button></div>
      </div>
      ${registro}
      ${credit()}`);
    const collect = () => { document.querySelectorAll('[data-k]').forEach((el) => { p[el.dataset.k] = el.value; }); };
    const persist = () => { const dd = dentist(); const i = dd.patients.findIndex((x) => x.id === p.id); if (i >= 0) dd.patients[i] = p; else dd.patients.push(p); saveDentist(dd); };
    $('#p-save').onclick = () => { collect(); persist(); toast('Paciente salvo.'); if (isNew) go('#/dentista/paciente/' + p.id); };
    $('#p-copy').onclick = async () => {
      collect();
      const txt = ['FICHA — PERFIL DO PACIENTE COM TEA', ...D.patientFields.map((f) => `${f[1]}: ${p[f[0]] || '—'}`), '', 'CONSULTAS:', ...(p.consultas || []).map((c) => `- ${c.data} | ${c.degrau} | funcionou: ${c.funcionou} | próximo: ${c.proximo}`)].join('\n');
      try { if (navigator.share) await navigator.share({ title: 'Ficha do paciente', text: txt }); else { await navigator.clipboard.writeText(txt); toast('Ficha copiada.'); } } catch (e) { toast('Não foi possível copiar.'); }
    };
    if (!isNew) {
      $('#c-add').onclick = () => { collect(); const c = {}; document.querySelectorAll('[data-c]').forEach((el) => { c[el.dataset.c] = el.value; }); if (!c.data) c.data = new Date().toISOString().slice(0, 10); p.consultas = p.consultas || []; p.consultas.unshift(c); persist(); toast('Consulta registrada.'); V.paciente(p.id); };
      document.querySelectorAll('[data-del]').forEach((b) => (b.onclick = () => { p.consultas.splice(+b.dataset.del, 1); persist(); V.paciente(p.id); }));
      $('#p-del').onclick = () => { if (!confirm('Excluir este paciente e suas consultas?')) return; const dd = dentist(); dd.patients = dd.patients.filter((x) => x.id !== p.id); saveDentist(dd); go('#/dentista/pacientes'); };
    }
  };

  // modo consulta
  let countTimer = null, clockTimer = null, clockStart = null;
  V.consulta = () => {
    const d = dentist(); const sch = d.schedule || {};
    setTop('Modo consulta', '#/dentista');
    render(`
      <div class="card counter">
        <div class="num" id="cnt">10</div>
        <div class="msg" id="cnt-msg">Contagem combinada: “até dez e eu paro”.</div>
        <div class="row" style="margin-top:10px"><button class="btn small primary" id="cnt-go">▶ Contar até 10</button><button class="btn small" id="cnt-stop">■ Parar</button></div>
      </div>
      <div class="card">
        <div class="row"><span class="timer" id="clock">00:00</span><button class="btn small" id="clock-btn">Iniciar consulta</button></div>
        <p class="muted" style="margin:6px 0 0">Consultas curtas (20 a 30 min) funcionam melhor.</p>
      </div>
      <h2 style="margin:4px 0 10px">Sinais para mostrar</h2>
      <div class="row" style="margin-bottom:14px">${D.signals.map((s, i) => `<button class="btn small" style="background:${s[3]};color:#fff;-webkit-text-stroke:.5px var(--ink)" data-sig="${i}">${s[1]}</button>`).join('')}</div>
      <h2 style="margin:4px 0 10px">Sequência visual (toque ao concluir)</h2>
      <div class="schedule">${D.shortSteps.map((s, i) => `<button class="btn ${sch[i] ? 'done' : ''}" data-s="${i}">${ill(s[0])}<span>${sch[i] ? '✓ ' : ''}${i + 1}. ${s[1]}</span></button>`).join('')}</div>
      <button class="btn small ghost" id="sch-clear" style="margin-top:12px">Reiniciar sequência</button>
      ${credit()}`);
    document.querySelectorAll('[data-sig]').forEach((b) => (b.onclick = () => showSignal(+b.dataset.sig)));
    document.querySelectorAll('[data-s]').forEach((b) => (b.onclick = () => { const dd = dentist(); dd.schedule = dd.schedule || {}; dd.schedule[b.dataset.s] = !dd.schedule[b.dataset.s]; saveDentist(dd); if (dd.schedule[b.dataset.s]) speak(`${D.shortSteps[b.dataset.s][1]}. Muito bem!`); V.consulta(); }));
    $('#sch-clear').onclick = () => { const dd = dentist(); dd.schedule = {}; saveDentist(dd); V.consulta(); };
    $('#cnt-go').onclick = () => {
      clearInterval(countTimer); let i = 0; const el = $('#cnt'), msg = $('#cnt-msg');
      msg.textContent = 'Contando…'; el.textContent = '0';
      const tick = () => { i++; el.textContent = i; try { window.speechSynthesis.cancel(); const u = new SpeechSynthesisUtterance(String(i)); u.lang = 'pt-BR'; window.speechSynthesis.speak(u); } catch (e) { /* sem voz */ } if (i >= 10) { clearInterval(countTimer); msg.textContent = 'Acabou! Pode fechar a boca.'; setTimeout(() => { try { const u = new SpeechSynthesisUtterance('Acabou! Pode fechar a boca.'); u.lang = 'pt-BR'; window.speechSynthesis.speak(u); } catch (e) { /* */ } }, 700); } };
      tick(); countTimer = setInterval(tick, 1000);
    };
    $('#cnt-stop').onclick = () => { clearInterval(countTimer); try { window.speechSynthesis.cancel(); } catch (e) { /* */ } $('#cnt-msg').textContent = 'Parado. Respira… quando quiser, a gente continua.'; };
    const fmt = (s) => `${String(Math.floor(s / 60)).padStart(2, '0')}:${String(s % 60).padStart(2, '0')}`;
    if (clockStart) { $('#clock-btn').textContent = 'Encerrar'; $('#clock').textContent = fmt(Math.floor((Date.now() - clockStart) / 1000)); }
    $('#clock-btn').onclick = () => {
      if (clockStart) { clearInterval(clockTimer); clockStart = null; $('#clock-btn').textContent = 'Iniciar consulta'; toast('Consulta encerrada. Registre na ficha do paciente.'); return; }
      clockStart = Date.now(); $('#clock-btn').textContent = 'Encerrar';
      clockTimer = setInterval(() => { const el = $('#clock'); if (el) el.textContent = fmt(Math.floor((Date.now() - clockStart) / 1000)); }, 1000);
    };
  };

  // ============================================================
  // ROTEADOR
  // ============================================================
  function go(h) { location.hash = h; }
  function route() {
    const parts = (location.hash || '#/').slice(2).split('/').filter(Boolean);
    $('#overlay').innerHTML = '';
    try { window.speechSynthesis && window.speechSynthesis.cancel(); } catch (e) { /* */ }
    const [a, b, c] = parts;
    if (!a) return V.home();
    if (a === 'crianca') {
      if (!b) return V.crianca();
      if (b === 'historia') return V.historia(c);
      if (V[b]) return V[b]();
    }
    if (a === 'dentista') {
      if (!b) return V.dentista();
      if (b === 'lista') return V.lista(c);
      if (b === 'paciente') return V.paciente(c);
      if (V[b]) return V[b]();
    }
    return V.home();
  }
  window.addEventListener('hashchange', route);
  route();

  // service worker (modo offline)
  if ('serviceWorker' in navigator && location.protocol.startsWith('http')) {
    navigator.serviceWorker.register('sw.js').catch(() => {});
  }
})();
