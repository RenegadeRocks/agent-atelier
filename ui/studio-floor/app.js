/* Agent Atelier · Studio Floor — v1 (P5-B approachable subset).
   A pure consumer of the exported projection (data/state.json). The Sheets
   SoR stays authoritative; this console submits owner signals via POST
   /action and never derives or writes a Status the orchestrator did not. */
'use strict';

const POLL_MS = 5000;                 // poll cadence for the exported projection
const STATE_URL = 'data/state.json';
const DEMO_URL = 'data/demo-state.json';
const ACTION_URL = '/action';
const MAX_FEED_ROWS = 200;

const AGENTS = {
  managing_editor:      { name: 'Managing Editor',            glyph: '◆', hue: 'var(--a-me)',  station: 'me',        role: 'orchestrator — plans, assigns, does no IC work' },
  evergreen_content:    { name: 'Evergreen Content',          glyph: '▢', hue: 'var(--a-ever)', station: 'evergreen', role: 'drafts timeless brand pieces' },
  offering_content:     { name: 'Offering Content',           glyph: '▤', hue: 'var(--a-off)', station: 'offering',  role: 'drafts offering-funnel pieces (by offering_id)' },
  research_verification:{ name: 'Research & Verification',    glyph: '◈', hue: 'var(--a-res)', station: 'research',  role: 'verifies claims into the Claim Bank' },
  creative_director:    { name: 'Creative Director',          glyph: '✶', hue: 'var(--a-cd)',  station: 'cd',        role: 'Scroll Test + Compliance review; render pass' },
  visual_production:    { name: 'Visual Production',          glyph: '▣', hue: 'var(--a-vis)', station: 'visual',    role: 'renders images + alt text' },
  publishing_ops:       { name: 'Publishing & Ops',           glyph: '⬡', hue: 'var(--a-pub)', station: 'pubops',    role: 'ledger lint, queueing, publish, record' },
  brand_strategist:     { name: 'Brand Onboarding Strategist',glyph: '✦', hue: 'var(--a-str)', station: 'strategist',role: 'runs the one-time brand intake' },
  // human hue = warm sienna (--human): owner-taste deviation from the spec's
  // violet (§12.4), applied everywhere; logged in the deviation log.
  human:                { name: 'you',                        glyph: '★', hue: 'var(--human)', station: 'desk',     role: 'the ninth seat — the human gate' },
  system:               { name: 'system',                     glyph: '⚙', hue: 'var(--ink-dim)', station: null,      role: 'deterministic gates, breaker, scheduler' },
};

const STATUSES = ['Draft', 'CD Review', 'Approval Queue', 'Approved', 'Published', 'Archived'];
const STAGE_STATION = {
  PLAN: 'me', DRAFT: null /* by agent */, LINT: 'lint', CD_REVIEW: 'cd',
  VISUALIZE: 'visual', CD_RENDER: 'cdrender', QUEUE: 'pubops',
  HUMAN_GATE: 'desk', PUBLISH: 'pubops', RECORD: 'pubops',
};

const S = {
  data: null, demo: false, offline: false, loadFailed: false,
  brand: null, tab: 'floor', filter: 'all', follow: null,
  lastSeq: 0, newSeqs: new Set(), localEvents: [], localSeq: 0,
  drawerPiece: null, expanded: new Set(),
};

/* ---------- tiny helpers ---------- */
const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => Array.from(document.querySelectorAll(sel));
function esc(s) {
  return String(s == null ? '' : s)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}
function fmtTime(ts) {
  const d = new Date(ts);
  if (isNaN(d)) return '——:——';
  return d.toTimeString().slice(0, 5);
}
function relAge(iso) {
  let ms = Date.now() - new Date(iso).getTime();
  if (isNaN(ms)) return '?';
  if (ms < 0) ms = 0; // tolerate small clock skew vs the exporter
  const s = Math.floor(ms / 1000);
  if (s < 90) return s + 's';
  const m = Math.floor(s / 60);
  if (m < 90) return m + 'm';
  const h = Math.floor(m / 60);
  if (h < 36) return h + 'h';
  return Math.floor(h / 24) + 'd';
}
function actorMeta(actor) {
  return AGENTS[actor] || { name: actor || '—', glyph: '·', hue: 'var(--ink-dim)', station: null };
}

/* Client-side redaction guard: the projection is pre-redacted upstream, but
   nothing shaped like a secret may render even if a bad row slips through. */
const SECRET_KEY_RE = /(key|token|bearer|authorization|secret|password|credential)/i;
function maskString(v) {
  return String(v)
    .replace(/\b(api[_-]?key|secret|password|key|token|bearer|authorization)\b(\s*[:=]\s*)(\S+)/gi, '$1$2[masked]')
    .replace(/\bBearer\s+[A-Za-z0-9._~+/=-]{4,}/gi, 'Bearer [masked]');
}
function maskDeep(value, keyName) {
  if (keyName && SECRET_KEY_RE.test(keyName)) return '[masked]';
  if (typeof value === 'string') return maskString(value);
  if (Array.isArray(value)) return value.map((v) => maskDeep(v));
  if (value && typeof value === 'object') {
    const out = {};
    for (const k of Object.keys(value)) out[k] = maskDeep(value[k], k);
    return out;
  }
  return value;
}

/* ---------- data access ---------- */
function brandPieces() {
  if (!S.data) return [];
  return S.data.pieces.filter((p) => p.brand_id === S.brand);
}
function brandEvents() {
  if (!S.data) return [];
  const evts = S.data.events.filter((e) => !e.brand_id || e.brand_id === S.brand);
  const local = S.localEvents.filter((e) => e.brand_id === S.brand);
  return evts.concat(local);
}
function pieceById(id) {
  return (S.data ? S.data.pieces : []).find((p) => p.piece_id === id) || null;
}
function pieceEvents(id) {
  return (S.data ? S.data.events : []).filter((e) => e.piece_id === id)
    .concat(S.localEvents.filter((e) => e.piece_id === id));
}
function inMotion(p) {
  return (p.status === 'Draft' || p.status === 'CD Review') && !p.exception;
}

/* ---------- theme & density ---------- */
function initTheme() {
  // ATELIER PAPER: light is the default theme; dark ("ink & candlelight")
  // stays one toggle away. An explicit saved preference always wins.
  const theme = localStorage.getItem('sf-theme') || 'light';
  document.documentElement.dataset.theme = theme;
  $('#themeBtn').textContent = theme === 'dark' ? '☀' : '☾';
}
function toggleTheme() {
  const next = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
  document.documentElement.dataset.theme = next;
  localStorage.setItem('sf-theme', next);
  $('#themeBtn').textContent = next === 'dark' ? '☀' : '☾';
  requestAnimationFrame(drawEdges);
}
function initDensity() {
  const d = localStorage.getItem('sf-density') || 'comfortable';
  document.body.dataset.density = d;
}
function toggleDensity() {
  const next = document.body.dataset.density === 'compact' ? 'comfortable' : 'compact';
  document.body.dataset.density = next;
  localStorage.setItem('sf-density', next);
  requestAnimationFrame(drawEdges);
}

/* ---------- polling ---------- */
async function fetchJson(url) {
  const res = await fetch(url, { cache: 'no-store' });
  if (!res.ok) throw new Error('HTTP ' + res.status);
  return res.json();
}
function inlineDemoState() {
  // Third fallback in the load order: the inline mirror of
  // data/demo-state.json embedded in index.html, so double-clicking the
  // file (file://, where fetch of local files is blocked) still works.
  const el = document.getElementById('demo-state');
  if (!el) return null;
  try { return JSON.parse(el.textContent); } catch (err) { return null; }
}
async function poll() {
  // Over file:// fetch is structurally blocked, so after the inline
  // fixture has loaded there is nothing new a poll could ever see —
  // skip the doomed fetches instead of spamming the console.
  if (window.location.protocol === 'file:' && S.data) {
    renderHeader();
    return;
  }
  let data = null; let demo = false;
  try {
    data = await fetchJson(STATE_URL);
  } catch (err) {
    // first-run: no exported state.json -> bundled demo fixture
    try {
      data = await fetchJson(DEMO_URL);
      demo = true;
    } catch (err2) {
      data = inlineDemoState();
      if (data) {
        demo = true;
      } else {
        if (S.data) { S.offline = true; renderHeader(); return; }
        S.loadFailed = true;
        document.body.classList.remove('loading');
        $('#offlineBanner').hidden = false;
        $('#offlineBanner').textContent = '▲ Could not load any state (state.json, the demo fixture, or the inline copy). Serve this folder with tools/floor_serve.py.';
        return;
      }
    }
  }
  S.offline = false;
  const maxSeq = data.events.length ? data.events[data.events.length - 1].seq : 0;
  const changed = !S.data || maxSeq !== S.lastSeq ||
    data.generated_at !== S.data.generated_at;
  S.demo = demo;
  if (changed) {
    S.newSeqs = new Set(
      S.data ? data.events.filter((e) => e.seq > S.lastSeq).map((e) => e.seq) : []
    );
    S.data = data;
    S.lastSeq = maxSeq;
    if (!S.brand || !data.brands.some((b) => b.brand_id === S.brand)) {
      S.brand = data.brands.length ? data.brands[0].brand_id : null;
    }
    document.body.classList.remove('loading');
    renderAll();
    S.newSeqs = new Set(); // animate once
  } else {
    renderHeader(); // refresh snapshot age
  }
}

/* ---------- header ---------- */
function renderHeader() {
  if (!S.data) return;
  const sel = $('#brandSelect');
  const want = S.data.brands.map((b) => b.brand_id).join('|');
  if (sel.dataset.have !== want) {
    sel.innerHTML = S.data.brands.map((b) =>
      `<option value="${esc(b.brand_id)}">${esc(b.name)}</option>`).join('');
    sel.dataset.have = want;
  }
  sel.value = S.brand;

  $('#demoBadge').hidden = !S.demo;
  const conn = $('#connChip');
  conn.classList.toggle('offline', S.offline);
  if (S.offline) {
    conn.textContent = '▲ Offline — showing last-known';
  } else {
    const age = relAge(S.data.generated_at);
    conn.textContent = (S.demo ? '◌ Demo snapshot — exported ' : '◌ Snapshot — exported ') + age + ' ago';
  }
  $('#offlineBanner').hidden = !S.offline;
  $('#layout').classList.toggle('dimmed', S.offline);

  const b = S.data.budget || {};
  const pct = Math.max(0, Math.min(100, Number(b.pct) || 0));
  const fill = $('#budgetFill');
  fill.style.width = pct + '%';
  fill.classList.toggle('hot', pct > 80 && pct <= 95);
  fill.classList.toggle('crit', pct > 95);
  $('#budgetPct').textContent = pct + '%' + (pct > 80 ? ' · only-critical-work band' : '');
  const breaker = $('#breakerChip');
  const ok = (b.breaker || 'OK') === 'OK';
  breaker.textContent = 'breaker: ' + (b.breaker || 'OK');
  breaker.className = 'chip ' + (ok ? 'chip-ok' : 'chip-tripped');

  const pieces = brandPieces();
  const motion = pieces.filter(inMotion).length;
  const needs = pieces.filter((p) => p.needs_you).length;
  // echo the active-station working accent so the eye connects counter -> station
  const motionChip = $('#inMotion');
  motionChip.textContent = (motion > 0 ? '● ' : '') + motion + ' in motion';
  motionChip.classList.toggle('chip-motion', motion > 0);
  $('#needYou').textContent = '▲ ' + needs + ' need you';

  const rn = $('#rightNow');
  const top = pieces.filter((p) => p.needs_you)
    .sort((a, b2) => (a.exception ? -1 : 1) - (b2.exception ? -1 : 1))[0];
  if (top) {
    rn.hidden = false;
    rn.innerHTML = `<span class="rn-label">RIGHT NOW ▸</span> ` +
      `“${esc(top.title)}” — ${esc(top.needs_you_reason || 'needs you')} — <strong>for YOU</strong>`;
  } else {
    rn.hidden = true;
  }
}

/* ---------- piece chips ---------- */
function chipHtml(p, opts) {
  const flag = p.needs_you ? '<span class="pc-flag">▲</span> ' : '';
  const followed = S.follow === p.piece_id ? ' followed' : '';
  const label = opts && opts.short ? p.piece_id.slice(-6) : p.piece_id;
  return `<button type="button" class="piece-chip${followed}" data-piece="${esc(p.piece_id)}" ` +
    `title="${esc(p.title)} · ${esc(p.status)} — click to follow this piece">${flag}${esc(label)}</button>`;
}

/* ---------- the floor ---------- */
function stationOf(p) {
  if (p.stage === 'DRAFT') return actorMeta(p.agent).station === 'offering' ? 'offering' : 'evergreen';
  return STAGE_STATION[p.stage] || null;
}
function renderFloor() {
  const pieces = brandPieces().filter((p) =>
    ['Draft', 'CD Review', 'Approval Queue', 'Approved'].includes(p.status));
  const shown = S.follow ? pieces.filter((p) => p.piece_id === S.follow) : pieces;
  const byStation = {};
  shown.forEach((p) => {
    const st = stationOf(p);
    if (st) (byStation[st] = byStation[st] || []).push(p);
  });

  $('#floorEmpty').hidden = brandPieces().length !== 0;

  // Layered active-state cues (owner eye-test round 2): state class drives
  // the accent border + tinted card + ring; the pill is the loud text cue.
  const ACTIVE_STATES = { working: 1, orchestrating: 1, reviewing: 1 };
  const ATTN_STATES = { looping: 1, waiting: 1 };
  const PILL_TEXT = {
    working: '● WORKING', orchestrating: '◆ ORCHESTRATING', reviewing: '✶ REVIEWING',
    looping: '⟲ REVISE LOOP', waiting: '▲ NEEDS YOU', blocked: '⛨ BLOCKED', paused: '‖ PAUSED',
  };
  const setStation = (id, state, ico, label, stPieces, pillText) => {
    const el = $('#st-' + id);
    if (!el) return;
    el.dataset.state = state;
    el.classList.toggle('is-active', !!ACTIVE_STATES[state]);
    el.classList.toggle('is-attn', !!ATTN_STATES[state]);
    el.classList.toggle('is-blocked', state === 'blocked' || state === 'paused');
    const icoEl = el.querySelector('.st-ico');
    const labelEl = el.querySelector('.st-label');
    if (icoEl) icoEl.textContent = ico;
    if (labelEl) labelEl.textContent = label;
    const head = el.querySelector('.st-head');
    if (head) {
      let pill = el.querySelector('.st-pill');
      if (!pill) {
        pill = document.createElement('span');
        head.appendChild(pill);
      }
      const text = pillText || PILL_TEXT[state] || '';
      pill.hidden = !text;
      pill.textContent = text;
      pill.className = 'st-pill' +
        (ATTN_STATES[state] ? ' st-pill--attn' : '') +
        (state === 'blocked' || state === 'paused' ? ' st-pill--blocked' : '');
    }
    const wrap = el.querySelector('.st-pieces');
    if (wrap) wrap.innerHTML = (stPieces || []).map((p) => chipHtml(p, { short: true })).join('');
    el.classList.toggle('followdim', !!S.follow && !(stPieces || []).length && id !== 'record');
  };

  const anyMotion = pieces.some(inMotion);
  setStation('me', anyMotion ? 'orchestrating' : 'idle', anyMotion ? '◆' : '·',
    anyMotion ? 'orchestrating' : 'resting — next wake: Monday editorial calendar', []);

  const ever = byStation.evergreen || [];
  setStation('evergreen', ever.length ? 'working' : 'idle', ever.length ? '●' : '·',
    ever.length ? 'drafting' : 'Idle', ever);
  const off = byStation.offering || [];
  setStation('offering', off.length ? 'working' : 'idle', off.length ? '●' : '·',
    off.length ? 'drafting' : 'Idle', off);

  // research wakes on a recent claim_verified event in the snapshot
  const recentClaim = brandEvents().some((e) =>
    e.actor === 'research_verification' &&
    (new Date(S.data.generated_at) - new Date(e.ts)) < 45 * 60 * 1000);
  setStation('research', recentClaim ? 'working' : 'idle', recentClaim ? '◈' : '·',
    recentClaim ? 'verifying a claim' : 'Idle', []);

  const lint = byStation.lint || [];
  const lintBlocked = lint.some((p) => p.exception === 'Safety-Blocked');
  setStation('lint', lintBlocked ? 'blocked' : (lint.length ? 'working' : 'idle'),
    lintBlocked ? '⛨' : (lint.length ? '⬢' : '·'),
    lintBlocked ? 'FAIL-CLOSED safety block' : (lint.length ? 'checking countable rules' : 'Idle'),
    lint);

  const cd = byStation.cd || [];
  const maxRound = Math.max(0, ...cd.map((p) => p.review_round || 0));
  const cap = cd.length ? (cd[0].review_cap || 2) : 2;
  setStation('cd',
    cd.length ? (maxRound >= 1 ? 'looping' : 'reviewing') : 'idle',
    cd.length ? (maxRound >= 1 ? '⟲' : '✶') : '·',
    cd.length ? (maxRound >= 1 ? `reviewing — revise ${maxRound}/${cap}` : 'reviewing') : 'Idle',
    cd,
    cd.length && maxRound >= 1 ? `⟲ REVISE ${maxRound}/${cap}` : undefined);

  const vis = byStation.visual || [];
  setStation('visual', vis.length ? 'working' : 'idle', vis.length ? '▣' : '·',
    vis.length ? 'rendering image + alt text' : 'Idle', vis);

  const cdr = byStation.cdrender || [];
  setStation('cdrender', cdr.length ? 'reviewing' : 'idle', cdr.length ? '✶' : '·',
    cdr.length ? 'render pass' : 'Idle', cdr);

  const pub = byStation.pubops || [];
  setStation('pubops', pub.length ? 'working' : 'idle', pub.length ? '⬡' : '·',
    pub.length ? 'ops' : 'Idle', pub);

  const desk = byStation.desk || [];
  const gateN = desk.filter((p) => p.status === 'Approval Queue').length;
  const awaitPost = desk.filter((p) => p.status === 'Approved').length;
  let deskLabel = 'Idle — nothing waiting';
  if (gateN) deskLabel = `Waiting on you ▲${gateN}`;
  else if (awaitPost) deskLabel = `awaiting your post (${awaitPost} approved)`;
  setStation('desk', (gateN || awaitPost) ? 'waiting' : 'idle',
    (gateN || awaitPost) ? '▲' : '·', deskLabel, desk,
    gateN ? `▲ NEEDS YOU (${gateN})` : (awaitPost ? '▲ AWAITING POST' : undefined));

  S.cdRound = maxRound;
  S.cdCap = cap;
  requestAnimationFrame(() => drawEdges(maxRound, cap));
}

function drawEdges(maxRound, cap) {
  if (maxRound === undefined) { maxRound = S.cdRound || 0; cap = S.cdCap || 2; }
  const svg = $('#edges');
  const floor = $('#floor');
  if (!svg || !floor || $('#viewFloor').hidden) return;
  const W = floor.clientWidth, H = floor.clientHeight;
  svg.setAttribute('viewBox', `0 0 ${W} ${H}`);
  const pt = (id, side) => {
    const el = $('#st-' + id);
    if (!el) return null;
    const x = el.offsetLeft, y = el.offsetTop, w = el.offsetWidth, h = el.offsetHeight;
    switch (side) {
      case 'top': return [x + w / 2, y];
      case 'bottom': return [x + w / 2, y + h];
      case 'left': return [x, y + h / 2];
      case 'right': return [x + w, y + h / 2];
    }
  };
  const specs = [
    { f: ['me', 'bottom'], t: ['evergreen', 'top'], cls: 'edge', label: 'plan · assigns' },
    { f: ['me', 'bottom'], t: ['offering', 'top'], cls: 'edge' },
    { f: ['research', 'right'], t: ['evergreen', 'left'], cls: 'edge edge-feeder', label: 'verified claim ┄▶' },
    { f: ['evergreen', 'bottom'], t: ['lint', 'top'], cls: 'edge', label: 'draft ▶' },
    { f: ['offering', 'bottom'], t: ['lint', 'top'], cls: 'edge' },
    { f: ['lint', 'bottom'], t: ['cd', 'top'], cls: 'edge', label: 'lint ✓ ▶' },
    { f: ['cd', 'bottom'], t: ['visual', 'top'], cls: 'edge', label: 'approve ▶' },
    { f: ['visual', 'bottom'], t: ['cdrender', 'top'], cls: 'edge' },
    { f: ['cdrender', 'bottom'], t: ['pubops', 'top'], cls: 'edge', label: 'queue ▶' },
    { f: ['pubops', 'bottom'], t: ['desk', 'top'], cls: 'edge', label: 'gate ▶' },
    { f: ['desk', 'bottom'], t: ['record', 'top'], cls: 'edge', label: 'publish ▶' },
  ];
  // the two structural back-edges (§12.4): CD revise + render-fail return arcs
  const rounds = maxRound || 0;
  const capN = cap || 2;
  const hot = rounds >= 3;
  specs.push({
    f: ['cd', 'left'], t: ['evergreen', 'left'], curve: -70,
    cls: 'edge edge-return' + (hot ? ' hot' : ''),
    label: `↩ revise R${rounds}/${capN}`, labelCls: hot ? 'red' : 'amber',
  });
  specs.push({
    f: ['cdrender', 'right'], t: ['visual', 'right'], curve: 70,
    cls: 'edge edge-return', label: '↩ render fail', labelCls: 'amber',
  });
  if (rounds >= capN && rounds > 0) {
    specs.push({
      f: ['cd', 'right'], t: ['me', 'right'], curve: 110,
      cls: 'edge edge-escalate',
      label: hot ? 'round 3 → ME (escalated)' : 'next round → ME',
      labelCls: hot ? 'red' : 'amber',
    });
  }
  let html = '';
  for (const s of specs) {
    const a = pt(s.f[0], s.f[1]), b = pt(s.t[0], s.t[1]);
    if (!a || !b) continue;
    let d;
    if (s.curve) {
      const cx = Math.min(a[0], b[0]) + s.curve;
      d = `M ${a[0]} ${a[1]} C ${cx} ${a[1]}, ${cx} ${b[1]}, ${b[0]} ${b[1]}`;
    } else {
      const my = (a[1] + b[1]) / 2;
      d = `M ${a[0]} ${a[1]} C ${a[0]} ${my}, ${b[0]} ${my}, ${b[0]} ${b[1]}`;
    }
    html += `<path class="${s.cls}" d="${d}"></path>`;
    if (s.label) {
      const lx = s.curve ? Math.min(a[0], b[0]) + s.curve + 6 : (a[0] + b[0]) / 2 + 8;
      const ly = (a[1] + b[1]) / 2 - 4;
      html += `<text class="edge-label ${s.labelCls || ''}" x="${lx}" y="${ly}">${esc(s.label)}</text>`;
    }
  }
  svg.innerHTML = html;
}

/* ---------- pipeline (kanban) ---------- */
function renderPipeline() {
  const pieces = S.follow
    ? brandPieces().filter((p) => p.piece_id === S.follow)
    : brandPieces();
  if (!pieces.length) {
    $('#lanes').innerHTML =
      '<div class="empty-note lanes-empty">No pieces yet — the pipeline is quiet. ' +
      'New work appears here the moment the Managing Editor assigns it.</div>';
    return;
  }
  $('#lanes').innerHTML = STATUSES.map((st) => {
    const lane = pieces.filter((p) => p.status === st);
    const cards = lane.map((p) => {
      const meta = actorMeta(p.agent);
      const loop = p.review_round ? `<span class="loopmeter">⟲ R${p.review_round}/${p.review_cap}</span>` : '';
      const exc = p.exception ? `<span class="exc">⛨ ${esc(p.exception)}</span>` : '';
      return `<div class="card" style="--hue:${meta.hue}">
        <span class="card-title">${p.needs_you ? '▲ ' : ''}${esc(p.title)}</span>
        ${chipHtml(p, { short: false })}
        <div>${exc} ${loop}</div>
      </div>`;
    }).join('') || '<p class="tray-quiet">—</p>';
    return `<div class="lane"><h3>${esc(st)} <span class="lane-count">${lane.length}</span></h3>${cards}</div>`;
  }).join('');
}

/* ---------- company ---------- */
function renderCompany() {
  const order = ['evergreen_content', 'offering_content', 'research_verification',
    'creative_director', 'visual_production', 'publishing_ops', 'brand_strategist'];
  const card = (key, extra) => {
    const a = AGENTS[key];
    return `<div class="org-card ${extra || ''}" style="--hue:${a.hue}">
      <div class="org-name">${a.glyph} ${esc(a.name)}</div>
      <div class="org-role">${esc(a.role)}</div>
    </div>`;
  };
  const quiet = brandPieces().length ? '' :
    '<div class="empty-note">The company is assembled but resting — no pieces yet. ' +
    'The floor comes alive with the first assignment.</div>';
  $('#company').innerHTML = quiet +
    `<div class="org-root">${card('managing_editor')}</div>
     <div class="org-stem"></div>
     <div class="org-row">${order.map((k) => card(k)).join('')}</div>
     <div class="org-row"><div class="org-card" style="--hue:var(--human)">
       <div class="org-name">★ You — the Showrunner's chair</div>
       <div class="org-role">the human gate; every action you take shows your sienna mark</div>
     </div></div>`;
}

/* ---------- activity feed ---------- */
function classify(e) {
  const v = (e.verb || '').toLowerCase();
  if (e.severity === 'alert') return 'alerts';
  if (e.severity === 'needs_you') return 'needsme';
  if (/owner_|approve|reject|request_changes|mark_posted|publish/.test(v)) return 'approvals';
  if (/revise|review|render_pass|render_fail|lint/.test(v)) return 'reviews';
  if (/handoff|draft|assigned|plan|verified|render|queue|record/.test(v)) return 'handoffs';
  return 'other';
}
function feedRow(e) {
  const meta = actorMeta(e.actor);
  const isGate = !!e.rule;
  const isHuman = e.actor === 'human';
  const cls = ['evt', 'sev-' + (e.severity || 'info')];
  if (isGate) cls.push('gate');
  if (isHuman) cls.push('human');
  if (e.local) cls.push('local');
  if (S.newSeqs.has(e.seq)) cls.push('evt-new');
  const p = e.piece_id ? pieceById(e.piece_id) : null;
  const chip = p ? chipHtml(p, { short: true })
    : (e.piece_id ? `<span class="mono">${esc(String(e.piece_id).slice(-6))}</span>` : '');
  const stage = e.stage ? `<span class="stage-chip">${esc(e.stage)}</span>` : '';
  const rule = e.rule ? `<span class="rule-chip">rule: ${esc(e.rule)}</span>` : '';
  const verb = esc((e.verb || '').replace(/_/g, ' '));
  const key = e.event_id || ('local-' + e.seq);
  const open = S.expanded.has(key);
  const raw = open
    ? `<pre class="evt-raw">${esc(JSON.stringify(maskDeep(e), null, 2))}</pre>` : '';
  const localTag = e.local ? ' <span class="dim">(local — not yet in the exported snapshot)</span>' : '';
  return `<div class="${cls.join(' ')}" data-eid="${esc(key)}">
    <div class="evt-row" style="--dot:${meta.hue}">
      <span class="evt-time">${fmtTime(e.ts)}</span>
      <span class="actor-dot"></span>
      <span class="evt-actor">${meta.glyph} ${esc(meta.name)}</span>
      <span class="evt-verb">${verb}</span>
      ${chip} ${stage} ${rule}
      <button type="button" class="evt-expand" data-eid="${esc(key)}" aria-expanded="${open}">${open ? '▾ raw' : '▸ raw'}</button>
    </div>
    <div class="evt-detail">${esc(e.detail || '')}${localTag}</div>
    ${raw}
  </div>`;
}
function renderFeed() {
  let evts = brandEvents();
  if (S.follow) evts = evts.filter((e) => e.piece_id === S.follow);
  if (S.filter !== 'all') evts = evts.filter((e) => classify(e) === S.filter);
  evts = evts.slice().sort((a, b) => (b.seq || 0) - (a.seq || 0)).slice(0, MAX_FEED_ROWS);
  $('#feed').innerHTML = evts.length
    ? evts.map(feedRow).join('')
    : '<p class="feed-quiet">Nothing here yet — the studio is quiet.</p>';
}

/* ---------- needs-you tray ---------- */
function renderTray() {
  const items = brandPieces().filter((p) => p.needs_you);
  $('#trayCount').textContent = items.length;
  $('#tray').innerHTML = items.length ? items.map((p) => {
    const blocked = p.exception ? ' blocked' : '';
    const badge = p.exception ? ('⛨ ' + p.exception)
      : (p.review_round >= p.review_cap ? `↩ ${p.review_round}/${p.review_cap} ⚠` : '▲ ready');
    return `<button type="button" class="tray-item${blocked}" data-piece="${esc(p.piece_id)}" data-open="1">
      <span><span class="ti-title">“${esc(p.title)}”</span><br>
      <span class="ti-reason">${esc(p.needs_you_reason || '')}</span></span>
      <span class="ti-badge">${esc(badge)}</span>
    </button>`;
  }).join('') : '<p class="tray-quiet">Nothing needs you — the studio is running.</p>';
}

/* ---------- trust panel ---------- */
function renderTrust() {
  const t = S.data.trust ? S.data.trust[S.brand] : null;
  const body = $('#trustBody');
  if (!t) { body.innerHTML = '<p class="tray-quiet">No trust data for this brand.</p>'; return; }
  const th = t.threshold, w = t.window;
  const dots = 10;
  const lit = Math.max(0, Math.min(dots, Math.round((w.decisions / Math.max(1, th.window_pieces)) * dots)));
  const meter = '<span class="lit">' + '●'.repeat(lit) + '</span><span class="unlit">' + '○'.repeat(dots - lit) + '</span>';
  const crit = (ok, label, val) =>
    `<li><span>${esc(label)}</span><span class="${ok ? 'ok' : 'no'} mono">${esc(val)} ${ok ? '✓' : '…'}</span></li>`;
  const reco = w.met
    ? `<div class="trust-reco">✓ Trust window met — the studio recommends enabling auto-publish.
       Enabling is an owner-only Vibe-Diff action taken outside this console; nothing flips here.</div>`
    : '';
  body.innerHTML = `
    <div class="trust-row">
      <span class="trust-meter" aria-label="Trust window ${w.decisions} of ${th.window_pieces}">${meter}</span>
      <span class="mono">${w.decisions}/${th.window_pieces}</span>
      <span class="chip">approval_mode: <strong>${esc(t.approval_mode)}</strong></span>
      <span class="kill-switch">auto-publish kill-switch:
        <span class="${t.auto_publish_enabled ? 'on' : 'off'}">${t.auto_publish_enabled ? 'ON' : 'OFF'}</span>
      </span>
    </div>
    <ul class="trust-crit">
      ${crit(w.decisions >= th.window_pieces, `window filled (${th.window_pieces} pieces)`, `${w.decisions}/${th.window_pieces}`)}
      ${crit(w.approval_rate >= th.min_approval_rate, `approval rate ≥ ${th.min_approval_rate}`, w.approval_rate)}
      ${crit(w.avg_human_edits <= th.max_avg_human_edits, `avg human edits ≤ ${th.max_avg_human_edits}`, w.avg_human_edits)}
      ${crit(w.policy_violations === 0, 'zero policy violations', w.policy_violations)}
    </ul>
    ${reco}
    <p class="trust-note">Display-only: this panel never auto-flips anything. A single owner reject or
    policy violation visibly resets the window to 0 (routine CD rejects do not).</p>`;
}

/* ---------- follow-a-piece ---------- */
function journeyHtml(pieceId) {
  const evts = pieceEvents(pieceId).slice().sort((a, b) => (a.seq || 0) - (b.seq || 0));
  const steps = evts.map((e) => {
    const meta = actorMeta(e.actor);
    return `<div class="j-step"><span class="j-time mono">${fmtTime(e.ts)}</span>
      <span style="color:${meta.hue}">${meta.glyph}</span>
      <span><strong>${esc((e.verb || '').replace(/_/g, ' '))}</strong>
      ${e.stage ? `<span class="stage-chip">${esc(e.stage)}</span>` : ''}
      <span class="dim">${esc(e.detail || '')}</span></span></div>`;
  }).join('');
  return `<p class="replay-note">Replay (from audit record — nothing re-runs)</p>
    <div class="journey">${steps || '<span class="dim">no recorded events for this piece</span>'}</div>`;
}
function renderFollow() {
  const el = $('#followBanner');
  if (!S.follow) { el.hidden = true; el.innerHTML = ''; return; }
  const p = pieceById(S.follow);
  el.hidden = false;
  el.innerHTML = `Following <span class="mono">${esc(S.follow)}</span>` +
    (p ? ` — “${esc(p.title)}” · ${esc(p.status)}` : '') +
    ` <button type="button" class="icon-btn" id="clearFollow">✕ stop following</button>` +
    journeyHtml(S.follow);
}
function setFollow(pieceId) {
  S.follow = (S.follow === pieceId) ? null : pieceId;
  const p = pieceId ? pieceById(pieceId) : null;
  if (S.follow && p && p.brand_id && p.brand_id !== S.brand) {
    S.brand = p.brand_id;
  }
  renderAll();
}

/* ---------- intervene drawer ---------- */
function cliFallback(body) {
  const json = JSON.stringify(body).replace(/'/g, "'\\''");
  return `python3 tools/apply_floor_actions.py --enqueue '${json}'`;
}
function actionsDisabledReason() {
  // Demo-mode safety: an action against demo data would write a fake
  // piece_id into a real sheet (or just fail). Actions are live only when
  // a real exported state.json was served over http. The CLI-fallback path
  // stays reserved for real-data-but-server-died.
  if (window.location.protocol === 'file:' || S.demo) {
    return 'demo data — actions need tools/floor_serve.py with real state';
  }
  return null;
}
function whereWhy(p) {
  const revises = pieceEvents(p.piece_id)
    .filter((e) => /revise/.test(e.verb || ''))
    .sort((a, b) => (a.seq || 0) - (b.seq || 0));
  const blocks = pieceEvents(p.piece_id)
    .filter((e) => e.severity === 'alert');
  let what = p.needs_you_reason || 'Waiting for a decision.';
  let consequence = 'Publishing waits on your decision — nothing ships without it.';
  if (p.review_round >= p.review_cap && p.review_round > 0) {
    // p.agent is the station currently holding the piece (often the CD);
    // the loop partner is the drafting agent from the piece's DRAFT events.
    const draftEvt = pieceEvents(p.piece_id).filter((e) =>
      e.stage === 'DRAFT' && AGENTS[e.actor] && e.actor !== 'creative_director').pop();
    const partner = draftEvt ? actorMeta(draftEvt.actor).name
      : (p.agent !== 'creative_director' ? actorMeta(p.agent).name : 'the content agent');
    what = `The Creative Director and ${partner} went back and forth ` +
      `${p.review_round} time(s) (cap ${p.review_cap}/${p.review_cap}).`;
    consequence = 'One more reject → escalates to the Managing Editor.';
  }
  if (p.exception === 'Safety-Blocked') {
    consequence = 'Fail-closed: this piece will not move without your call.';
  }
  const evidence = [];
  revises.forEach((e, i) => evidence.push(`<blockquote>R${i + 1} — ${esc(e.detail)}</blockquote>`));
  blocks.forEach((e) => evidence.push(`<blockquote>⛨ ${esc(e.detail)}</blockquote>`));
  if (!evidence.length && p.cd_note) evidence.push(`<blockquote>CD — ${esc(p.cd_note)}</blockquote>`);
  const loop = revises.length ? `<div class="loop-timeline">` +
    revises.map((e, i) => `<span class="loop-step${i + 1 >= p.review_cap ? ' hot' : ''}">R${i + 1}</span>`)
      .join('<span class="loop-arrow">→</span>') +
    (p.review_round >= p.review_cap ? '<span class="loop-arrow">→</span><span class="loop-step hot">ME?</span>' : '') +
    `</div>` : '';
  return `<div class="wcard">
    <h3>WHERE &amp; WHY</h3>
    <p>${esc(what)}</p>
    <div class="evidence">${evidence.join('') || '<span class="dim">no verbatim evidence recorded</span>'}</div>
    ${loop}
    <p class="consequence">${esc(consequence)}</p>
  </div>`;
}
function openDrawer(pieceId) {
  const p = pieceById(pieceId);
  if (!p) return;
  S.drawerPiece = pieceId;
  const drawer = $('#drawer');
  const asset = p.asset_url
    ? `<p class="drawer-sub">asset: <span class="mono">${esc(p.asset_url)}</span></p>` : '';
  const alt = p.alt_text ? `<p class="drawer-sub">alt: ${esc(p.alt_text)}</p>` : '';
  const demoReason = actionsDisabledReason();
  const demoDis = demoReason
    ? ` disabled aria-disabled="true" title="${esc(demoReason)}"` : '';
  const disabledTip = 'wires in at P5-A';
  const disabled = [
    ['Unstick & resume', disabledTip],
    ['Edit task ✎', disabledTip],
    ['Re-route ⇄', disabledTip],
    ['Inject note ▸', disabledTip],
    ['Publish (Post Kit)', 'Post Kit wires in at P3 / P5-A'],
  ].map(([label, tip]) =>
    `<button type="button" class="act-btn" disabled aria-disabled="true" title="${esc(tip)}">${esc(label)}</button>`
  ).join('');
  drawer.querySelector('#drawerBody').innerHTML = `
    <button type="button" class="icon-btn drawer-close" id="drawerClose" aria-label="Close">✕</button>
    <h2 id="drawerTitle">INTERVENE · “${esc(p.title)}”</h2>
    <p class="drawer-sub">${esc(p.piece_id)} · ${esc(p.status)}${p.exception ? ' · ⛨ ' + esc(p.exception) : ''} · rev ${esc(p.rev)}</p>
    ${asset}${alt}
    ${p.caption ? `<p>${esc(p.caption)}</p>` : ''}
    ${whereWhy(p)}
    <div class="wcard"><h3>JOURNEY</h3>${journeyHtml(p.piece_id)}</div>
    <div class="wcard">
      <h3>FLOOR ACTIONS <span class="dim">· every action is audited · acting on rev ${esc(p.rev)}</span></h3>
      <label class="note-field">note (optional — travels with your action into the audit trail)
        <textarea id="actionNote" rows="2"></textarea>
      </label>
      <div class="actions-row">
        <button type="button" class="act-btn act-approve" data-action="approve"${demoDis}>Approve ✓</button>
        <button type="button" class="act-btn act-changes" data-action="request_changes"${demoDis}>Request changes ↩</button>
        <button type="button" class="act-btn act-reject" data-action="reject"${demoDis}>Reject ✕</button>
      </div>
      ${demoReason ? `<p class="action-disabled-note">⚠ ${esc(demoReason)}</p>` : ''}
      <div class="actions-row">${disabled}</div>
      <div id="actionResult" class="action-result" aria-live="polite"></div>
    </div>`;
  drawer.hidden = false;
  $('#drawerBackdrop').hidden = false;
  drawer.querySelector('#drawerClose').focus();
}
function closeDrawer() {
  $('#drawer').hidden = true;
  $('#drawerBackdrop').hidden = true;
  S.drawerPiece = null;
}
async function submitAction(action) {
  if (actionsDisabledReason()) return; // defense in depth vs the disabled buttons
  const p = pieceById(S.drawerPiece);
  if (!p) return;
  const note = ($('#actionNote') && $('#actionNote').value || '').trim();
  const body = { piece_id: p.piece_id, action, note, rev: p.rev };
  const out = $('#actionResult');
  out.className = 'action-result';
  out.textContent = 'submitting…';
  let ok = false, msg = '';
  try {
    const res = await fetch(ACTION_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    const payload = await res.json().catch(() => ({}));
    if (res.status === 200) { ok = true; msg = '✓ recorded to the Owner-Action cell + audit trail.'; }
    else if (res.status === 202) { ok = true; msg = '✓ queued locally — apply with tools/apply_floor_actions.py (no Sheets credentials on the server).'; }
    else msg = `✕ ${payload.error || ('server said ' + res.status)}`;
  } catch (err) {
    msg = '✕ could not reach /action (is tools/floor_serve.py running?)';
  }
  if (ok) {
    out.className = 'action-result ok';
    out.textContent = msg;
    S.localSeq += 1;
    S.localEvents.push({
      seq: S.lastSeq + 1000 + S.localSeq, local: true,
      event_id: 'local-' + S.localSeq,
      brand_id: p.brand_id, ts: new Date().toISOString(),
      piece_id: p.piece_id, stage: 'HUMAN_GATE', actor: 'human',
      operator_id: null, verb: 'owner_' + action,
      detail: note || ('you chose ' + action.replace(/_/g, ' ')),
      severity: 'info', rule: null,
    });
    renderFeed();
  } else {
    out.className = 'action-result err';
    out.innerHTML = `${esc(msg)}<br>Fallback — run this from the repo root:` +
      `<pre class="cli-fallback" id="cliCmd">${esc(cliFallback(body))}</pre>` +
      `<button type="button" class="icon-btn copy-btn" id="copyCli">copy command</button>`;
  }
}

/* ---------- tabs & render root ---------- */
function setTab(tab) {
  S.tab = tab;
  $$('.tab').forEach((b) => {
    const active = b.dataset.tab === tab;
    b.classList.toggle('active', active);
    b.setAttribute('aria-selected', String(active));
  });
  $('#viewFloor').hidden = tab !== 'floor';
  $('#viewPipeline').hidden = tab !== 'pipeline';
  $('#viewCompany').hidden = tab !== 'company';
  if (tab === 'floor') requestAnimationFrame(() => renderFloor());
}
function renderAll() {
  if (!S.data) return;
  renderHeader();
  renderFollow();
  renderFloor();
  renderPipeline();
  renderCompany();
  renderTray();
  renderTrust();
  renderFeed();
}

/* ---------- wiring ---------- */
function init() {
  initTheme();
  initDensity();
  $('#themeBtn').addEventListener('click', toggleTheme);
  $('#densityBtn').addEventListener('click', toggleDensity);
  $('#brandSelect').addEventListener('change', (e) => {
    S.brand = e.target.value;
    S.follow = null;
    renderAll();
  });
  $$('.tab').forEach((b) => b.addEventListener('click', () => setTab(b.dataset.tab)));
  $$('.ffilter').forEach((b) => b.addEventListener('click', () => {
    S.filter = b.dataset.filter;
    $$('.ffilter').forEach((x) => x.classList.toggle('active', x === b));
    renderFeed();
  }));

  // one delegated handler: piece chips (follow), tray items (drawer),
  // feed raw-expand, drawer actions, follow-clear, copy CLI
  document.addEventListener('click', (e) => {
    const trayItem = e.target.closest('[data-open="1"]');
    if (trayItem) { openDrawer(trayItem.dataset.piece); return; }
    const chip = e.target.closest('.piece-chip');
    if (chip) { setFollow(chip.dataset.piece); return; }
    const expand = e.target.closest('.evt-expand');
    if (expand) {
      const k = expand.dataset.eid;
      if (S.expanded.has(k)) S.expanded.delete(k); else S.expanded.add(k);
      renderFeed();
      return;
    }
    if (e.target.closest('#drawerClose') || e.target.closest('#drawerBackdrop')) { closeDrawer(); return; }
    const act = e.target.closest('.act-btn[data-action]');
    if (act && !act.disabled) { submitAction(act.dataset.action); return; }
    if (e.target.closest('#clearFollow')) { setFollow(S.follow); return; }
    if (e.target.closest('#copyCli')) {
      const cmd = $('#cliCmd') ? $('#cliCmd').textContent : '';
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(cmd);
      } else {
        const ta = document.createElement('textarea');
        ta.value = cmd; document.body.appendChild(ta); ta.select();
        document.execCommand('copy'); ta.remove();
      }
      e.target.textContent = 'copied ✓';
      return;
    }
  });
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && !$('#drawer').hidden) closeDrawer();
  });
  window.addEventListener('resize', () => requestAnimationFrame(() => drawEdges()));

  poll();
  setInterval(poll, POLL_MS);
}

document.addEventListener('DOMContentLoaded', init);
