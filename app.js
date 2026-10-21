// Sitio estático: los registros viven en data/entries.json y los archivos en media/.
const PROJECT = window.PROJECT || { name: 'Proyecto', areas: [], phases: [] };

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

// Solo rutas relativas dentro de media/ (evita enlaces externos o javascript:)
function safePath(p) {
  return /^media\/[^:]*$/.test(p || '') && !p.includes('..') ? encodeURI(p) : '';
}

function formatDate(iso) {
  if (!iso) return '';
  const [y, m, d] = iso.split('-').map(Number);
  return new Date(y, m - 1, d).toLocaleDateString('es-MX', {
    day: 'numeric', month: 'short', year: 'numeric',
  });
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
  entries.sort((a, b) =>
    (b.date || '').localeCompare(a.date || '') || String(b.id).localeCompare(String(a.id)));
  renderAreaFilter();
  renderSummary();
  renderList();
}

function renderProject() {
  $('#project-name').textContent = PROJECT.name || 'Proyecto';
  $('#project-desc').textContent = PROJECT.description || '';
  $('#project-dates').textContent =
    PROJECT.startDate && PROJECT.targetDate
      ? `Inicio ${formatDate(PROJECT.startDate)} · Entrega estimada ${formatDate(PROJECT.targetDate)}`
      : '';

  const labels = { pendiente: 'Pendiente', 'en curso': 'En curso', terminada: 'Terminada' };
  $('#phases').innerHTML = (PROJECT.phases || []).map((p) => {
    const cls = p.status === 'terminada' ? 'done' : p.status === 'en curso' ? 'doing' : 'todo';
    return `<li class="phase ${cls}"><span>${esc(p.name)}</span><em>${esc(labels[p.status] || p.status)}</em></li>`;
  }).join('');
}

function renderAreaFilter() {
  const areas = [...new Set([...(PROJECT.areas || []), ...entries.map((e) => e.area)])].sort();
  el.filterArea.innerHTML =
    '<option value="">Todas las áreas</option>' +
    areas.map((a) => `<option value="${esc(a)}">${esc(a)}</option>`).join('');
}

// Último reporte de cada área. Las áreas de project.js aparecen siempre.
function renderSummary() {
  const latest = {};
  for (const e of entries) {
    if (e.kind === 'reporte' && e.progress_pct != null && !latest[e.area]) latest[e.area] = e;
  }
  const names = [...new Set([...(PROJECT.areas || []), ...Object.keys(latest)])];
  const pcts = names.map((n) => (latest[n] ? latest[n].progress_pct : 0));
  const overall = pcts.length ? Math.round(pcts.reduce((a, b) => a + b, 0) / pcts.length) : 0;

  $('#overall-pct').textContent = `${overall}%`;
  $('#overall-bar').style.width = `${overall}%`;

  el.summary.innerHTML = names.length
    ? names.map((n) => {
        const e = latest[n];
        return `
        <div class="bar-row">
          <span class="bar-label">${esc(n)}</span>
          <div class="bar"><div style="width:${e ? Number(e.progress_pct) : 0}%"></div></div>
          <span class="bar-value">${e ? `${Number(e.progress_pct)}% <small>(${esc(formatDate(e.date))})</small>` : '<small>sin reporte</small>'}</span>
        </div>`;
      }).join('')
    : '<p>Aún no hay áreas ni reportes de avance.</p>';
}

function fileHtml(f) {
  const path = safePath(f.path);
  if (!path) return '';
  const name = esc(f.name || f.path);
  const type = f.type || '';
  if (type.startsWith('image/')) {
    return `<a href="${path}" target="_blank" rel="noopener"><img src="${path}" alt="${name}" loading="lazy"></a>`;
  }
  if (type.startsWith('video/')) {
    return `<video src="${path}" controls preload="metadata"></video>`;
  }
  return `<a href="${path}" target="_blank" rel="noopener">📎 ${name}</a>`;
}

function card(e) {
  const files = (e.files || []).map((f) => `<div class="file">${fileHtml(f)}</div>`).join('');
  return `
    <article class="card">
      <header>
        <span class="tag ${esc(e.kind)}">${e.kind === 'reporte' ? 'Reporte' : 'Evidencia'}</span>
        <strong>${esc(e.title)}</strong>
        <span class="meta">${esc(e.area)} · ${esc(formatDate(e.date))}${e.progress_pct != null ? ` · <b>${Number(e.progress_pct)}%</b>` : ''}</span>
      </header>
      ${e.description ? `<p>${esc(e.description)}</p>` : ''}
      ${e.pendientes ? `<p><b>Pendientes:</b> ${esc(e.pendientes)}</p>` : ''}
      ${files ? `<div class="files">${files}</div>` : ''}
    </article>`;
}

function renderList() {
  const area = el.filterArea.value;
  const kind = el.filterKind.value;
  const shown = entries.filter((e) => (!area || e.area === area) && (!kind || e.kind === kind));
  el.list.innerHTML = shown.length
    ? shown.map(card).join('')
    : `<p class="muted">${entries.length ? 'No hay registros con esos filtros.' : 'Aún no hay registros.'}</p>`;
}

el.filterArea.addEventListener('change', renderList);
el.filterKind.addEventListener('change', renderList);

renderProject();
loadEntries();
