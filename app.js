const cfg = window.APP_CONFIG;
const sb = window.supabase.createClient(cfg.SUPABASE_URL, cfg.SUPABASE_ANON_KEY);
const BUCKET = 'evidencias';
const MAX_FILE_BYTES = 50 * 1024 * 1024;

const $ = (sel) => document.querySelector(sel);
const el = {
  login: $('#login-view'),
  app: $('#app-view'),
  loginForm: $('#login-form'),
  loginMsg: $('#login-msg'),
  logout: $('#logout-btn'),
  userEmail: $('#user-email'),
  form: $('#entry-form'),
  formMsg: $('#form-msg'),
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

function safeName(name) {
  return name.normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[^a-zA-Z0-9._-]/g, '_');
}

function today() {
  // YYYY-MM-DD en la zona horaria local
  return new Date().toLocaleDateString('sv-SE');
}

async function showView() {
  const { data: { session } } = await sb.auth.getSession();
  if (session) {
    el.login.hidden = true;
    el.app.hidden = false;
    el.userEmail.textContent = session.user.email;
    el.form.elements.taken_on.value = today();
    await loadEntries();
  } else {
    el.login.hidden = false;
    el.app.hidden = true;
  }
}

el.loginForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const fd = new FormData(el.loginForm);
  const { error } = await sb.auth.signInWithPassword({
    email: fd.get('email'),
    password: fd.get('password'),
  });
  el.loginMsg.textContent = error ? 'Correo o contraseña incorrectos.' : '';
  if (!error) {
    el.loginForm.reset();
    await showView();
  }
});

el.logout.addEventListener('click', async () => {
  await sb.auth.signOut();
  await showView();
});

async function loadEntries() {
  const { data, error } = await sb
    .from('entries')
    .select('*, files(*)')
    .order('taken_on', { ascending: false })
    .order('created_at', { ascending: false });

  if (error) {
    el.list.innerHTML = `<p class="error">Error al cargar: ${esc(error.message)}</p>`;
    return;
  }
  entries = data;
  renderAreaFilter();
  renderSummary();
  await renderList();
}

function renderAreaFilter() {
  const current = el.filterArea.value;
  const areas = [...new Set(entries.map((e) => e.area))].sort();
  el.filterArea.innerHTML =
    '<option value="">Todas las áreas</option>' +
    areas.map((a) => `<option value="${esc(a)}">${esc(a)}</option>`).join('');
  el.filterArea.value = areas.includes(current) ? current : '';
}

const PROJECT = window.PROJECT || { name: 'Proyecto', areas: [], phases: [] };

function formatDate(iso) {
  if (!iso) return '';
  const [y, m, d] = iso.split('-').map(Number);
  return new Date(y, m - 1, d).toLocaleDateString('es-MX', {
    day: 'numeric', month: 'short', year: 'numeric',
  });
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

// Último reporte de cada área (entries ya viene ordenado de más reciente a más antiguo).
// Las áreas definidas en project.js aparecen siempre, aunque aún no tengan reporte.
function renderSummary() {
  const latest = {};
  for (const e of entries) {
    if (e.kind === 'reporte' && e.progress_pct != null && !latest[e.area]) {
      latest[e.area] = e;
    }
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
          <div class="bar"><div style="width:${e ? e.progress_pct : 0}%"></div></div>
          <span class="bar-value">${e ? `${e.progress_pct}% <small>(${esc(e.taken_on)})</small>` : '<small>sin reporte</small>'}</span>
        </div>`;
      }).join('')
    : '<p>Aún no hay áreas ni reportes de avance.</p>';
}

function card(e) {
  const files = e.files.map((f) => `
    <div class="file" data-path="${esc(f.storage_path)}" data-mime="${esc(f.mime_type || '')}">
      ${esc(f.file_name)}
    </div>`).join('');

  return `
    <article class="card">
      <header>
        <span class="tag ${esc(e.kind)}">${e.kind === 'reporte' ? 'Reporte' : 'Evidencia'}</span>
        <strong>${esc(e.title)}</strong>
        <span class="meta">${esc(e.area)} · ${esc(e.taken_on)}${e.progress_pct != null ? ` · <b>${e.progress_pct}%</b>` : ''}</span>
      </header>
      ${e.description ? `<p>${esc(e.description)}</p>` : ''}
      ${e.pendientes ? `<p><b>Pendientes:</b> ${esc(e.pendientes)}</p>` : ''}
      ${files ? `<div class="files">${files}</div>` : ''}
    </article>`;
}

async function renderList() {
  const area = el.filterArea.value;
  const kind = el.filterKind.value;
  const shown = entries.filter((e) =>
    (!area || e.area === area) && (!kind || e.kind === kind)
  );

  if (!shown.length) {
    el.list.innerHTML = '<p>No hay registros con esos filtros.</p>';
    return;
  }
  el.list.innerHTML = shown.map(card).join('');

  // Pedir enlaces temporales para todos los archivos visibles
  const paths = shown.flatMap((e) => e.files.map((f) => f.storage_path));
  if (!paths.length) return;

  const { data, error } = await sb.storage.from(BUCKET).createSignedUrls(paths, 3600);
  if (error) return;

  const urlByPath = Object.fromEntries(
    data.filter((d) => d.signedUrl).map((d) => [d.path, d.signedUrl])
  );

  el.list.querySelectorAll('.file[data-path]').forEach((node) => {
    const url = urlByPath[node.dataset.path];
    if (!url) return;
    const name = node.textContent.trim();
    const mime = node.dataset.mime;
    node.innerHTML = mime.startsWith('image/')
      ? `<a href="${esc(url)}" target="_blank" rel="noopener"><img src="${esc(url)}" alt="${esc(name)}" loading="lazy"></a>`
      : `<a href="${esc(url)}" target="_blank" rel="noopener">📎 ${esc(name)}</a>`;
  });
}

el.filterArea.addEventListener('change', renderList);
el.filterKind.addEventListener('change', renderList);

el.form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const fd = new FormData(el.form);
  const files = [...el.form.elements.files.files];
  const kind = fd.get('kind');
  const btn = el.form.querySelector('button[type="submit"]');
  btn.disabled = true;
  el.formMsg.textContent = 'Guardando…';

  try {
    const oversized = files.find((f) => f.size > MAX_FILE_BYTES);
    if (oversized) throw new Error(`${oversized.name} supera 50 MB`);

    const pct = fd.get('progress_pct');
    const { data: entry, error } = await sb
      .from('entries')
      .insert({
        kind,
        area: fd.get('area').trim(),
        title: fd.get('title').trim(),
        description: fd.get('description') || null,
        progress_pct: kind === 'reporte' && pct !== '' && pct !== null ? Number(pct) : null,
        pendientes: fd.get('pendientes') || null,
        taken_on: fd.get('taken_on') || today(),
      })
      .select()
      .single();
    if (error) throw error;

    for (const file of files) {
      const path = `${entry.id}/${crypto.randomUUID()}-${safeName(file.name)}`;
      const up = await sb.storage.from(BUCKET).upload(path, file, { contentType: file.type });
      if (up.error) throw up.error;

      const { error: fileErr } = await sb.from('files').insert({
        entry_id: entry.id,
        storage_path: path,
        file_name: file.name,
        mime_type: file.type,
      });
      if (fileErr) throw fileErr;
    }

    el.form.reset();
    el.form.elements.taken_on.value = today();
    el.formMsg.textContent = 'Guardado correctamente.';
    await loadEntries();
  } catch (err) {
    el.formMsg.textContent = 'Error: ' + err.message;
  } finally {
    btn.disabled = false;
  }
});

renderProject();
showView();
