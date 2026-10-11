/* ─── Urban Traffic Management System — Shared JS Utilities ────────────────── */

const API_BASE = '';  // same origin

// ── Role simulation (set via header) ─────────────────────────────────────────
let currentRole = localStorage.getItem('utms_role') || 'public';

function setRole(role) {
  currentRole = role;
  localStorage.setItem('utms_role', role);
  document.querySelectorAll('[data-role-display]').forEach(el => {
    el.textContent = role.charAt(0).toUpperCase() + role.slice(1);
  });
  document.querySelectorAll('[data-requires-role]').forEach(el => {
    const required = el.dataset.requiresRole.split(',');
    el.style.display = required.includes(currentRole) ? '' : 'none';
  });
}

// ── Fetch wrapper ─────────────────────────────────────────────────────────────
async function apiFetch(path, options = {}) {
  const headers = { 'X-User-Role': currentRole, ...options.headers };
  if (options.body) headers['Content-Type'] = 'application/json';
  const resp = await fetch(API_BASE + path, { ...options, headers });
  const data = await resp.json().catch(() => ({}));
  return { ok: resp.ok, status: resp.status, data };
}

// ── Toast notification ────────────────────────────────────────────────────────
function showToast(message, type = 'info') {
  const t = document.getElementById('toast');
  if (!t) return;
  t.textContent = message;
  t.className = type;
  t.style.display = 'block';
  clearTimeout(t._timer);
  t._timer = setTimeout(() => { t.style.display = 'none'; }, 3500);
}

// ── Badge helpers ─────────────────────────────────────────────────────────────
function severityBadge(s) {
  if (!s) return '';
  const cls = { CRITICAL:'critical', HIGH:'high', MEDIUM:'medium', LOW:'low' }[s] || 'low';
  return `<span class="badge badge-${cls}">${s}</span>`;
}
function congestionBadge(c) {
  if (!c) return '<span class="text-muted">—</span>';
  const cls = { SEVERE:'severe', HIGH:'high', MODERATE:'medium', LOW:'normal' }[c] || 'normal';
  return `<span class="badge badge-${cls}">${c}</span>`;
}
function statusBadge(open) {
  return open
    ? '<span class="badge badge-open">OPEN</span>'
    : '<span class="badge badge-resolved">RESOLVED</span>';
}
function signalBadge(s) {
  const cls = { Active:'active', Inactive:'medium', Faulty:'faulty' }[s] || 'medium';
  return `<span class="badge badge-${cls}">${s || '—'}</span>`;
}

// ── Table renderer ────────────────────────────────────────────────────────────
function renderTable(tbodyId, rows, renderRow) {
  const tbody = document.getElementById(tbodyId);
  if (!tbody) return;
  if (!rows || rows.length === 0) {
    tbody.innerHTML = `<tr><td colspan="99" class="empty-msg">No records found.</td></tr>`;
    return;
  }
  tbody.innerHTML = rows.map(renderRow).join('');
}

// ── Populate select from API ──────────────────────────────────────────────────
async function populateSelect(selectId, path, valueKey, labelKey, placeholder = 'All') {
  const sel = document.getElementById(selectId);
  if (!sel) return;
  const { ok, data } = await apiFetch(path);
  if (!ok) return;
  sel.innerHTML = `<option value="">${placeholder}</option>` +
    data.map(r => `<option value="${r[valueKey]}">${r[labelKey]}</option>`).join('');
}

// ── Role switcher init ────────────────────────────────────────────────────────
function initRoleSwitcher() {
  const sel = document.getElementById('roleSelect');
  if (sel) {
    sel.value = currentRole;
    sel.addEventListener('change', () => { setRole(sel.value); window.location.reload(); });
  }
  setRole(currentRole);
}

document.addEventListener('DOMContentLoaded', initRoleSwitcher);
