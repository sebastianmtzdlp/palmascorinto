// Sitio estático: el contenido sale de project.js, los registros de data/entries.json y los archivos de media/.
const PROJECT = window.PROJECT || {};
const $ = (sel) => document.querySelector(sel);
const el = {
  list: $('#entries'),
  summary: $('#summary'),
  filterArea: $('#filter-area'),
  filterKind: $('#filter-kind'),
};
let entries = [];

function esc(s) {
  return String(s ?? '').replace(/[&<>"']/g, (c) => (
    { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]
  ));
}

// Solo rutas relativas dentro de media/ o assets/ (evita enlaces externos o javascript:)
function safePath(p) {
  return /^(media|assets)\/[^:]*$/.test(p || '') && !p.includes('..') ? encodeURI(p) : '';
}

function formatDate(iso) {
  if (!iso) return '';
  const [y, m, d] = iso.split('-').map(Number);
  return new Date(y, m - 1, d).toLocaleDateString('es-MX', { day: 'numeric', month: 'short', year: 'numeric' });
}

/* ---------- Parte pública tipo preventa ---------- */
function renderLanding() {
  const h = PROJECT.hero || {};
  document.title = `${PROJECT.name || 'Proyecto'} · Preventa`;
  $('#sample-strip').hidden = !PROJECT.sample;
  document.body.classList.toggle('has-strip', !!PROJECT.sample);

  const img = $('#hero-img');
  img.src = safePath(h.image);
  img.alt = h.imageAlt || '';
  $('#hero-badge').textContent = h.badge || '';
  $('#hero-badge').hidden = !h.badge;
  $('#hero-title').textContent = h.title || PROJECT.name || '';
  $('#hero-sub').textContent = h.subtitle || '';
  $('#hero-cta').textContent = h.cta || 'Contacto';
  $('#hero-stats').innerHTML = (h.stats || []).map((s) =>
    `<div class="stat"><b>${esc(s.value)}</b><span>${esc(s.label)}</span></div>`).join('');

  $('#highlights').innerHTML = (PROJECT.highlights || []).map((x) => `
    <article class="feature"><div class="ico" aria-hidden="true">${esc(x.icon)}</div>
      <h3>${esc(x.title)}</h3><p>${esc(x.text)}</p></article>`).join('');

  const statusLabel = { disponible: 'Disponible', apartado: 'Apartado', vendido: 'Vendido' };
  $('#units').innerHTML = (PROJECT.units || []).map((u) => `
    <article class="unit ${esc(u.status)}">
      <span class="pill ${esc(u.status)}">${esc(statusLabel[u.status] || u.status)}</span>
      <h3>${esc(u.name)}</h3>
      <ul><li>${esc(u.area)}</li><li>${esc(u.rooms)}</li><li>${esc(u.baths)}</li></ul>
      <p class="price">${esc(u.price)}</p>
    </article>`).join('');
  $('#price-note').textContent = PROJECT.priceNote || '';

  $('#payment').innerHTML = (PROJECT.payment || []).map((p) => `
    <article class="feature pay"><div class="pay-val">${esc(p.value)}</div>
      <h3>${esc(p.step)}. ${esc(p.title)}</h3><p>${esc(p.text)}</p></article>`).join('');

  $('#gallery').innerHTML = (PROJECT.gallery || []).map((g, i) => {
    const src = safePath(g.src);
    return src ? `<button type="button" class="g-item g${i}" data-src="${src}" data-cap="${esc(g.caption || g.alt)}">
      <img src="${src}" alt="${esc(g.alt)}" loading="lazy"><span>${esc(g.caption)}</span></button>` : '';
  }).join('');

  renderContact();
  $('#footer-credit').textContent = PROJECT.sample ? 'Fotos de ejemplo: Unsplash' : '';
}

function renderContact() {
  const c = PROJECT.contact || {};
  const out = [];
  const wa = String(c.whatsapp || '').replace(/\D/g, '');
  if (wa) {
    out.push(`<a class="btn" target="_blank" rel="noopener" href="https://wa.me/${wa}?text=${encodeURIComponent(c.message || '')}">Escribir por WhatsApp</a>`);
  }
  if (/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(c.email || '')) {
    out.push(`<a class="btn ghost-dark" href="mailto:${esc(c.email)}?subject=${encodeURIComponent('Información ' + (PROJECT.name || ''))}&body=${encodeURIComponent(c.message || '')}">Enviar correo</a>`);
  }
  $('#contact-actions').innerHTML = out.length ? out.join('') : '<p class="muted">Muy pronto compartiremos los datos de contacto.</p>';
}

function renderReports() {
  const list = PROJECT.reports || [];
  $('#reports').innerHTML = list.map((r) => {
    const path = safePath(r.file);
    if (!path) return '';
    const fname = path.split('/').pop();
    return `<article class="report">
      <div class="doc-ico" aria-hidden="true">PDF</div>
      <div class="report-body">
        <h3>${esc(r.title)} ${r.sample ? '<span class="pill apartado">Ejemplo</span>' : ''}</h3>
        <p class="meta">${esc(formatDate(r.date))}</p>
        <p>${esc(r.description)}</p>
      </div>
      <a class="btn dl" href="${path}" download="${esc(fname)}">Descargar</a>
    </article>`;
  }).join('') || '<p class="muted">Aún no hay reportes disponibles.</p>';
}

/* ---------- Galería ampliada ---------- */
const lb = $('#lightbox');
$('#gallery').addEventListener('click', (e) => {
  const b = e.target.closest('.g-item');
  if (!b) return;
  $('#lb-img').src = b.dataset.src;
  $('#lb-cap').textContent = b.dataset.cap || '';
  lb.hidden = false;
});
const closeLb = () => { lb.hidden = true; $('#lb-img').removeAttribute('src'); };
$('#lb-close').addEventListener('click', closeLb);
lb.addEventListener('click', (e) => { if (e.target === lb) closeLb(); });
document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && !lb.hidden) closeLb(); });

/* ---------- Avance de obra ---------- */
function renderProject() {
  $('#project-desc').textContent = PROJECT.description || '';
  $('#project-dates').textContent = PROJECT.startDate && PROJECT.targetDate
    ? `Inicio ${formatDate(PROJECT.startDate)} · Entrega estimada ${formatDate(PROJECT.targetDate)}` : '';
  const labels = { pendiente: 'Pendiente', 'en curso': 'En curso', terminada: 'Terminada' };
  $('#phases').innerHTML = (PROJECT.phases || []).map((p) => {
    const cls = p.status === 'terminada' ? 'done' : p.status === 'en curso' ? 'doing' : 'todo';
    return `<li class="phase ${cls}"><span>${esc(p.name)}</span><em>${esc(labels[p.status] || p.status)}</em></li>`;
  }).join('');
}

function renderAreaFilter() {
  const areas = [...new Set([...(PROJECT.areas || []), ...entries.map((e) => e.area)])].sort();
  el.filterArea.innerHTML = '<option value="">Todas las áreas</option>' +
    areas.map((a) => `<option value="${esc(a)}">${esc(a)}</option>`).join('');
}

function renderSummary() {
  const latest = {};
  for (const e of entries) {
    if (e.kind === 'reporte' && e.progress_pct != null && !latest[e.area]) latest[e.area] = e;
  }
  const names = [...new Set([...(PROJECT.areas || []), ...Object.keys(latest)])];
  const pcts = names.map((n) => (latest[n] ? Number(latest[n].progress_pct) : 0));
  const overall = pcts.length ? Math.round(pcts.reduce((a, b) => a + b, 0) / pcts.length) : 0;
  $('#overall-pct').textContent = `${overall}%`;
  $('#overall-bar').style.width = `${overall}%`;
  el.summary.innerHTML = names.length ? names.map((n) => {
    const e = latest[n];
    return `<div class="bar-row"><span class="bar-label">${esc(n)}</span>
      <div class="bar"><div style="width:${e ? Number(e.progress_pct) : 0}%"></div></div>
      <span class="bar-value">${e ? `${Number(e.progress_pct)}% <small>(${esc(formatDate(e.date))})</small>` : '<small>sin reporte</small>'}</span></div>`;
  }).join('') : '<p>Aún no hay áreas ni reportes de avance.</p>';
}

function fileHtml(f) {
  const path = safePath(f.path);
  if (!path) return '';
  const name = esc(f.name || f.path);
  const type = f.type || '';
  if (type.startsWith('image/')) return `<a href="${path}" target="_blank" rel="noopener"><img src="${path}" alt="${name}" loading="lazy"></a>`;
  if (type.startsWith('video/')) return `<video src="${path}" controls preload="metadata"></video>`;
  return `<a href="${path}" target="_blank" rel="noopener">📎 ${name}</a>`;
}

function card(e) {
  const files = (e.files || []).map((f) => `<div class="file">${fileHtml(f)}</div>`).join('');
  return `<article class="card">
    <header><span class="tag ${esc(e.kind)}">${e.kind === 'reporte' ? 'Reporte' : 'Evidencia'}</span>
      <strong>${esc(e.title)}</strong>
      <span class="meta">${esc(e.area)} · ${esc(formatDate(e.date))}${e.progress_pct != null ? ` · <b>${Number(e.progress_pct)}%</b>` : ''}</span></header>
    ${e.description ? `<p>${esc(e.description)}</p>` : ''}
    ${e.pendientes ? `<p><b>Pendientes:</b> ${esc(e.pendientes)}</p>` : ''}
    ${files ? `<div class="files">${files}</div>` : ''}</article>`;
}

function renderList() {
  const area = el.filterArea.value;
  const kind = el.filterKind.value;
  const shown = entries.filter((e) => (!area || e.area === area) && (!kind || e.kind === kind));
  el.list.innerHTML = shown.length ? shown.map(card).join('')
    : `<p class="muted">${entries.length ? 'No hay registros con esos filtros.' : 'Aún no hay registros.'}</p>`;
}

async function loadEntries() {
  try {
    const res = await fetch('data/entries.json', { cache: 'no-store' });
    if (!res.ok) throw new Error(res.status);
    entries = await res.json();
  } catch (err) {
    el.list.innerHTML = '<p class="error">No se pudieron cargar los registros.</p>';
    return;
  }
  entries.sort((a, b) => (b.date || '').localeCompare(a.date || '') || String(b.id).localeCompare(String(a.id)));
  renderAreaFilter();
  renderSummary();
  renderList();
}

el.filterArea.addEventListener('change', renderList);
el.filterKind.addEventListener('change', renderList);

renderLanding();
renderReports();
renderProject();
renderSummary();
loadEntries();
