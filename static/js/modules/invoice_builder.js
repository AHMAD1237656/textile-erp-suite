/**
 * invoice_builder.js – Invoice Format Builder
 * ─────────────────────────────────────────────
 * SortableJS drag-and-drop, element selection,
 * property panel live preview, paper size switching,
 * template save/load via localStorage.
 */

import { showToast } from '/static/js/api.js';

const canvas   = document.getElementById('invoice-canvas');
let   selected = null;

/* ── Element names map ────────────────────────────────────────────────────── */
const EL_NAMES = {
  header_block:   'Header Block',
  client_block:   'Client / Bill-To Block',
  items_table:    'Items Table',
  totals_block:   'Totals Block',
  notes:          'Notes & Terms',
  signature:      'Signature Block',
  qr_code:        'QR Code',
  logo:           'Company Logo',
  company_name:   'Company Name',
  divider:        'Divider',
  custom_text:    'Custom Text',
};

/* ── SortableJS – reorder canvas elements ─────────────────────────────────── */
Sortable.create(canvas, {
  animation:    200,
  ghostClass:   'tw-opacity-40',
  handle:       '.builder-el',
  draggable:    '.builder-el',
  onEnd: ()   => showToast('Element repositioned', 'info', 1500),
});

/* ── Drag from elements panel → canvas ───────────────────────────────────── */
document.querySelectorAll('.drag-item').forEach(item => {
  item.addEventListener('dragstart', e => {
    e.dataTransfer.setData('text/plain', item.dataset.elType);
  });
});

canvas.addEventListener('dragover',  e => { e.preventDefault(); canvas.style.outline = '2px dashed var(--erp-primary)'; });
canvas.addEventListener('dragleave', ()  => { canvas.style.outline = ''; });
canvas.addEventListener('drop', e => {
  e.preventDefault();
  canvas.style.outline = '';
  const type = e.dataTransfer.getData('text/plain');
  if (type) addElement(type);
});

function addElement(type) {
  const el = document.createElement('div');
  el.className     = 'builder-el animate-fade-up';
  el.dataset.el    = type;

  const content = buildElementHTML(type);
  el.innerHTML = `
    <div class="el-handle" aria-hidden="true">
      <button title="Move up"><i class="bi bi-arrow-up"></i></button>
      <button title="Move down"><i class="bi bi-arrow-down"></i></button>
      <button class="btn-el-delete" title="Remove"><i class="bi bi-x"></i></button>
    </div>
    ${content}
  `;

  canvas.appendChild(el);
  selectElement(el);
  showToast(`Added: ${EL_NAMES[type] || type}`, 'success', 1500);
}

function buildElementHTML(type) {
  const templates = {
    logo:           `<img src="" alt="Company Logo" class="inv-logo" style="width:80px;height:50px;background:var(--erp-bg);display:block;border-radius:4px;">`,
    company_name:   `<div style="font-size:20px;font-weight:700;color:var(--erp-primary-dark);">TechImport ERP</div>`,
    company_address:`<div style="font-size:11px;color:#666;">123 Electronics Plaza, Karachi 75000<br>Tel: +92-21-1234567</div>`,
    invoice_title:  `<div style="font-size:28px;font-weight:700;color:var(--erp-primary);letter-spacing:-0.5px;">INVOICE</div>`,
    invoice_number: `<div style="font-size:13px;"><strong>Invoice No:</strong> INV-2024-0922</div>`,
    invoice_date:   `<div style="font-size:13px;"><strong>Date:</strong> Oct 7, 2024</div>`,
    due_date:       `<div style="font-size:13px;"><strong>Due Date:</strong> Nov 6, 2024</div>`,
    client_block:   `<div class="inv-parties"><div><div class="inv-party-label">Bill To</div><div class="inv-party-name">Client Name</div><div class="inv-party-addr">Address Line 1<br>City, Country</div></div></div>`,
    items_table:    `<table class="inv-items-table"><thead><tr><th>#</th><th>Description</th><th class="text-end">Qty</th><th class="text-end">Rate</th><th class="text-end">Total</th></tr></thead><tbody><tr><td>1</td><td>Sample Product</td><td class="text-end">10</td><td class="text-end">₨1,000</td><td class="text-end">₨10,000</td></tr></tbody></table>`,
    totals_block:   `<div class="d-flex justify-content-end"><div class="inv-totals"><div class="inv-total-row grand"><span>Grand Total</span><span>₨ 10,000</span></div></div></div>`,
    notes:          `<div style="font-size:11.5px;color:#555;margin-top:12px;"><strong>Notes:</strong> Thank you for your business.</div>`,
    signature:      `<div style="margin-top:20px;"><div style="border-top:1px solid #999;width:180px;margin-bottom:4px;"></div><div style="font-size:11px;">Authorised Signature</div></div>`,
    qr_code:        `<div style="width:80px;height:80px;background:var(--erp-bg);border:1px solid var(--erp-border);border-radius:4px;display:flex;align-items:center;justify-content:center;"><i class="bi bi-qr-code" style="font-size:40px;color:var(--erp-text-muted);"></i></div>`,
    divider:        `<hr style="border-color:var(--erp-border);margin:8px 0;">`,
    custom_text:    `<div contenteditable="true" style="font-size:12px;color:#555;min-height:20px;outline:none;" placeholder="Click to edit text…">Custom text here…</div>`,
  };
  return templates[type] || `<div style="padding:8px;color:var(--erp-text-muted);">${EL_NAMES[type]||type}</div>`;
}

/* ── Select element ───────────────────────────────────────────────────────── */
function selectElement(el) {
  document.querySelectorAll('.builder-el.selected').forEach(e => e.classList.remove('selected'));
  if (!el) { selected = null; updatePropsPanel(null); return; }

  el.classList.add('selected');
  selected = el;
  updatePropsPanel(el);
}

canvas.addEventListener('click', e => {
  const el = e.target.closest('.builder-el');
  if (el) selectElement(el);

  // Delete handle
  if (e.target.closest('.btn-el-delete')) {
    const row = e.target.closest('.builder-el');
    if (row) { row.remove(); selected = null; showToast('Element removed', 'info', 1500); }
    return;
  }
});

/* ── Properties panel ─────────────────────────────────────────────────────── */
function updatePropsPanel(el) {
  const nameEl = document.getElementById('selected-el-name');
  if (!el) { if (nameEl) nameEl.textContent = 'None selected'; return; }
  if (nameEl) nameEl.textContent = EL_NAMES[el.dataset.el] || el.dataset.el;
}

// Live property application
document.getElementById('prop-text-color')?.addEventListener('input', function () {
  if (selected) selected.style.color = this.value;
});
document.getElementById('prop-bg-color')?.addEventListener('input', function () {
  if (selected) selected.style.background = this.value;
});
document.getElementById('prop-font-size')?.addEventListener('input', function () {
  if (selected) selected.style.fontSize = this.value + 'px';
});
document.getElementById('prop-font')?.addEventListener('change', function () {
  if (selected) selected.style.fontFamily = this.value + ', sans-serif';
});
document.getElementById('prop-padding')?.addEventListener('input', function () {
  if (selected) selected.style.padding = this.value + 'px';
});
document.getElementById('prop-bold')?.addEventListener('click', () => {
  if (selected) selected.style.fontWeight = selected.style.fontWeight === '700' ? '' : '700';
});
['prop-align-left','prop-align-center','prop-align-right'].forEach(id => {
  document.getElementById(id)?.addEventListener('click', function () {
    if (!selected) return;
    const map = { 'prop-align-left':'left','prop-align-center':'center','prop-align-right':'right' };
    selected.style.textAlign = map[this.id];
  });
});
document.getElementById('prop-visible')?.addEventListener('change', function () {
  if (selected) selected.style.display = this.checked ? '' : 'none';
});
document.getElementById('btn-remove-selected')?.addEventListener('click', () => {
  if (selected) { selected.remove(); selected = null; showToast('Element removed', 'info', 1500); }
});
document.getElementById('btn-duplicate-selected')?.addEventListener('click', () => {
  if (!selected) return;
  const clone = selected.cloneNode(true);
  canvas.insertBefore(clone, selected.nextSibling);
  selectElement(clone);
  showToast('Element duplicated', 'success', 1500);
});

/* ── Paper size ───────────────────────────────────────────────────────────── */
document.querySelectorAll('.paper-size-btn').forEach(btn => {
  btn.addEventListener('click', function () {
    document.querySelectorAll('.paper-size-btn').forEach(b => {
      b.classList.remove('btn-erp-primary');
      b.classList.add('btn-erp-ghost');
    });
    this.classList.remove('btn-erp-ghost');
    this.classList.add('btn-erp-primary');

    canvas.className = 'builder-canvas canvas-' + this.dataset.size;
    showToast(`Paper size: ${this.textContent}`, 'info', 1500);
  });
});

/* ── Template thumbnails ──────────────────────────────────────────────────── */
document.querySelectorAll('.template-thumb').forEach(thumb => {
  thumb.addEventListener('click', function () {
    document.querySelectorAll('.template-thumb').forEach(t => t.classList.remove('active'));
    this.classList.add('active');
    showToast(`Template "${this.dataset.template}" loaded`, 'success', 1500);
  });
});

/* ── Save template ────────────────────────────────────────────────────────── */
document.getElementById('btn-save-template')?.addEventListener('click', () => {
  const html = canvas.innerHTML;
  try {
    localStorage.setItem('erp-invoice-template', html);
    showToast('Template saved to browser storage.', 'success');
  } catch { showToast('Could not save template.', 'danger'); }
});

document.getElementById('btn-set-default')?.addEventListener('click', () => {
  localStorage.setItem('erp-default-template', canvas.innerHTML);
  showToast('Set as default invoice template.', 'success');
});

/* ── Init ─────────────────────────────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  // Select the first element by default
  const first = canvas.querySelector('.builder-el');
  if (first) selectElement(first);
});
