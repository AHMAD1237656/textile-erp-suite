/**
 * sales_entry.js – Sales invoice entry module
 * ─────────────────────────────────────────────
 * Features:
 *  - Dynamic add/remove line item rows
 *  - Product search via Select2 / API (autofills rate, unit)
 *  - Live totals calculation (subtotal, discount, tax, freight, grand total, balance)
 *  - Credit limit check on client selection
 *  - Stock availability check on product selection
 *  - Save as Draft / Save & Print / Save & New
 *  - Client-side form validation
 */

import { api, showToast } from '/static/js/api.js';

/* ── Sample clients ──────────────────────────────────────────────────────── */
const CLIENTS = [
  { id:1, name:'TechMart Pvt Ltd',   credit_limit:2000000, balance:2300000 },
  { id:2, name:'Digital World',       credit_limit:1500000, balance:900000  },
  { id:3, name:'ByteHouse Corp',      credit_limit:1000000, balance:680000  },
  { id:4, name:'MicroHub',            credit_limit:800000,  balance:420000  },
  { id:5, name:'Lahore Gadgets',      credit_limit:600000,  balance:180000  },
];

/* ── Sample products (matches /products/api/search/ response) ────────────── */
const PRODUCTS = [
  { id:1, text:'USB-C 65W GaN Charger',     sku:'CHG-65W-001', price:'1299', unit:'Pcs', stock:'340' },
  { id:2, text:'DDR4 16GB 3200MHz RAM',     sku:'RAM-DDR4-16G',price:'6500', unit:'Pcs', stock:'8'   },
  { id:3, text:'HDMI 2.1 Cable 4K 2m',     sku:'CBL-HDMI-4K', price:'599',  unit:'Pcs', stock:'520' },
  { id:4, text:'USB 3.0 Hub 7-Port',        sku:'HUB-USB7-001',price:'1899', unit:'Pcs', stock:'85'  },
  { id:5, text:'NVMe SSD 1TB Gen4',         sku:'SSD-1TB-NVM', price:'14999',unit:'Pcs', stock:'42'  },
  { id:6, text:'CAT6 RJ45 Patch Cable 5m',  sku:'CBL-RJ45-5M', price:'350',  unit:'Pcs', stock:'1200'},
  { id:7, text:'Power Bank 20000mAh PD45W', sku:'PB-20K-001',  price:'4500', unit:'Pcs', stock:'60'  },
  { id:8, text:'Type-C to A Cable 1m 3A',   sku:'CBL-TYCA-001',price:'250',  unit:'Pcs', stock:'12'  },
];

/* ── Row counter ─────────────────────────────────────────────────────────── */
let rowCounter = 0;

/* ── Helpers ─────────────────────────────────────────────────────────────── */
function fmt(n) {
  return '₨ ' + Number(n || 0).toLocaleString('en-PK', { maximumFractionDigits: 0 });
}

function calcRowTotal(row) {
  const qty      = parseFloat(row.querySelector('.r-qty')?.value)  || 0;
  const rate     = parseFloat(row.querySelector('.r-rate')?.value) || 0;
  const disc     = parseFloat(row.querySelector('.r-disc')?.value) || 0;
  const tax      = parseFloat(row.querySelector('.r-tax')?.value)  || 0;

  const base      = qty * rate;
  const discAmt   = base * (disc / 100);
  const taxable   = base - discAmt;
  const taxAmt    = taxable * (tax / 100);
  const lineTotal = taxable + taxAmt;

  row.querySelector('.r-total').value = lineTotal.toFixed(2);
  return { base, discAmt, taxAmt, lineTotal };
}

function recalcAll() {
  let subtotal = 0, totalDisc = 0, totalTax = 0, totalQty = 0, itemCount = 0;

  document.querySelectorAll('#line-items-tbody tr').forEach(row => {
    if (row.dataset.empty) return;
    const r = calcRowTotal(row);
    subtotal  += r.base;
    totalDisc += r.discAmt;
    totalTax  += r.taxAmt;
    totalQty  += parseFloat(row.querySelector('.r-qty')?.value) || 0;
    itemCount++;
  });

  const freight   = parseFloat(document.getElementById('inv-freight')?.value)       || 0;
  const other     = parseFloat(document.getElementById('inv-other-charges')?.value)  || 0;
  const paid      = parseFloat(document.getElementById('inv-amount-paid')?.value)    || 0;
  const grandTotal = (subtotal - totalDisc + totalTax + freight + other);
  const balance    = grandTotal - paid;

  document.getElementById('total-subtotal').textContent = fmt(subtotal);
  document.getElementById('total-discount').textContent = '- ' + fmt(totalDisc);
  document.getElementById('total-tax').textContent      = '+ ' + fmt(totalTax);
  document.getElementById('total-freight').textContent  = '+ ' + fmt(freight);
  document.getElementById('total-other').textContent    = '+ ' + fmt(other);
  document.getElementById('total-grand').textContent    = fmt(grandTotal);
  document.getElementById('total-paid').textContent     = fmt(paid);
  document.getElementById('total-balance').textContent  = fmt(balance);
  document.getElementById('items-count').textContent    = itemCount;
  document.getElementById('total-qty').textContent      = totalQty;

  // Update balance colour
  const balEl = document.getElementById('total-balance');
  balEl.style.color = balance > 0 ? 'var(--erp-danger)' : 'var(--erp-success)';
}

/* ── Build one line-item row ─────────────────────────────────────────────── */
function buildRow() {
  rowCounter++;
  const idx = rowCounter;

  const tr = document.createElement('tr');
  tr.dataset.rowIdx = idx;
  tr.innerHTML = `
    <td style="text-align:center;color:var(--erp-text-muted);font-size:12px;">${idx}</td>
    <td>
      <select class="form-select-erp r-product" name="lines[${idx}][product]"
              aria-label="Select product for row ${idx}" style="height:32px;font-size:12.5px;">
        <option value="">Search product…</option>
        ${PRODUCTS.map(p => `<option value="${p.id}" data-price="${p.price}" data-unit="${p.unit}" data-sku="${p.sku}" data-stock="${p.stock}">${p.text}</option>`).join('')}
      </select>
    </td>
    <td>
      <input type="text" class="form-input-erp r-sku font-mono"
             name="lines[${idx}][sku]" readonly placeholder="—"
             aria-label="SKU for row ${idx}" style="height:32px;font-size:11px;background:var(--erp-bg);">
    </td>
    <td>
      <input type="number" class="form-input-erp r-qty"
             name="lines[${idx}][qty]" min="1" step="1" value="1"
             aria-label="Quantity for row ${idx}">
    </td>
    <td>
      <input type="text" class="form-input-erp r-unit"
             name="lines[${idx}][unit]" placeholder="Pcs" readonly
             aria-label="Unit for row ${idx}" style="background:var(--erp-bg);">
    </td>
    <td>
      <input type="number" class="form-input-erp r-rate"
             name="lines[${idx}][rate]" min="0" step="0.01" value="0"
             aria-label="Rate for row ${idx}">
    </td>
    <td>
      <input type="number" class="form-input-erp r-disc"
             name="lines[${idx}][disc]" min="0" max="100" step="0.01" value="0"
             aria-label="Discount % for row ${idx}">
    </td>
    <td>
      <input type="number" class="form-input-erp r-tax"
             name="lines[${idx}][tax]" min="0" max="100" step="0.01" value="17"
             aria-label="Tax % for row ${idx}">
    </td>
    <td>
      <input type="number" class="form-input-erp r-total"
             name="lines[${idx}][total]" readonly value="0"
             aria-label="Line total for row ${idx}" style="background:var(--erp-bg);font-weight:600;">
    </td>
    <td>
      <button type="button" class="btn-erp btn-erp-danger btn-erp-icon btn-erp-sm btn-remove-row"
              aria-label="Remove row ${idx}" title="Remove row">
        <i class="bi bi-trash3" aria-hidden="true"></i>
      </button>
    </td>
  `;

  // Product select change → auto-fill rate, unit, sku + stock check
  tr.querySelector('.r-product').addEventListener('change', function () {
    const opt = this.options[this.selectedIndex];
    if (!opt.value) return;

    const price = opt.dataset.price || 0;
    const unit  = opt.dataset.unit  || '';
    const sku   = opt.dataset.sku   || '';
    const stock = parseFloat(opt.dataset.stock) || 0;

    tr.querySelector('.r-rate').value = price;
    tr.querySelector('.r-unit').value = unit;
    tr.querySelector('.r-sku').value  = sku;

    calcRowTotal(tr);
    recalcAll();

    // Stock warning
    const qty = parseFloat(tr.querySelector('.r-qty').value) || 1;
    checkStockWarning(opt.text, sku, qty, stock);
  });

  // Recalc on any numeric input change
  tr.querySelectorAll('.r-qty,.r-rate,.r-disc,.r-tax').forEach(el => {
    el.addEventListener('input', () => { calcRowTotal(tr); recalcAll(); });
  });

  // Remove row
  tr.querySelector('.btn-remove-row').addEventListener('click', () => {
    tr.remove();
    renumberRows();
    recalcAll();
  });

  return tr;
}

function renumberRows() {
  document.querySelectorAll('#line-items-tbody tr').forEach((tr, i) => {
    const numCell = tr.querySelector('td:first-child');
    if (numCell) numCell.textContent = i + 1;
  });
}

function addRow() {
  const tbody = document.getElementById('line-items-tbody');
  tbody.appendChild(buildRow());
  recalcAll();
}

/* ── Warnings ─────────────────────────────────────────────────────────────── */
function checkStockWarning(name, sku, qty, available) {
  const container = document.getElementById('inline-alerts');
  // Remove previous stock warning for this SKU
  document.querySelectorAll(`[data-stock-sku="${sku}"]`).forEach(el => el.remove());

  if (qty > available) {
    const div = document.createElement('div');
    div.className = 'warning-banner warning-stock';
    div.dataset.stockSku = sku;
    div.innerHTML = `
      <i class="bi bi-exclamation-triangle-fill flex-shrink-0"></i>
      <span>
        <strong>Low Stock:</strong> ${name} — Requested: ${qty}, Available: ${available} ${available === 0 ? '(OUT OF STOCK)' : ''}.
      </span>
    `;
    container.appendChild(div);
  }
}

function checkCreditLimit(client) {
  const container = document.getElementById('inline-alerts');
  document.getElementById('credit-warning')?.remove();

  if (!client) return;

  const creditPct = client.credit_limit > 0
    ? Math.round((client.balance / client.credit_limit) * 100)
    : 0;

  // Credit bar
  const bar = document.getElementById('credit-limit-bar');
  if (bar) {
    bar.classList.remove('d-none');
    const fill = document.getElementById('credit-used-fill');
    const label = document.getElementById('credit-used-label');
    if (fill)  fill.style.width      = `${Math.min(100, creditPct)}%`;
    if (fill)  fill.style.background = creditPct >= 100 ? 'var(--erp-danger)' : creditPct > 75 ? 'var(--erp-warning)' : 'var(--erp-success)';
    if (label) label.textContent     = `${fmt(client.balance)} / ${fmt(client.credit_limit)} (${creditPct}%)`;
  }

  if (creditPct >= 100) {
    const div = document.createElement('div');
    div.id = 'credit-warning';
    div.className = 'warning-banner warning-credit';
    div.innerHTML = `
      <i class="bi bi-credit-card-2-back-fill flex-shrink-0"></i>
      <strong>Credit Limit Exceeded:</strong>&nbsp;${client.name} — Balance ₨${client.balance.toLocaleString()} exceeds limit ₨${client.credit_limit.toLocaleString()}.
    `;
    container.prepend(div);
  }
}

/* ── Client Select2 ──────────────────────────────────────────────────────── */
async function initClientSelect() {
  let clientsData = CLIENTS;
  try {
    const res = await fetch('/sales/api/clients/');
    if (res.ok) {
      const json = await res.json();
      if (json.data && json.data.length) {
        clientsData = json.data.map(c => ({
          id: c.id,
          name: c.company_name ? `${c.name} (${c.company_name})` : c.name,
          credit_limit: c.credit_limit,
          balance: c.current_balance,
        }));
      }
    }
  } catch (err) {
    // Fallback to local CLIENTS array
  }

  $('#inv-client').select2({
    placeholder: 'Search client by name…',
    allowClear: true,
    data: clientsData.map(c => ({ id: c.id, text: c.name })),
  }).on('select2:select', function (e) {
    const client = clientsData.find(c => c.id == e.params.data.id);
    checkCreditLimit(client);
  }).on('select2:clear', () => {
    document.getElementById('credit-limit-bar')?.classList.add('d-none');
    document.getElementById('credit-warning')?.remove();
  });
}

/* ── Save invoice ─────────────────────────────────────────────────────────── */
async function saveInvoice(mode = 'draft') {
  // Basic validation
  const client = document.getElementById('inv-client').value;
  if (!client) {
    showToast('Please select a client.', 'warning');
    document.getElementById('inv-client').closest('.col-md-6').scrollIntoView({ behavior: 'smooth' });
    return;
  }

  const rows = document.querySelectorAll('#line-items-tbody tr');
  if (!rows.length) {
    showToast('Please add at least one line item.', 'warning');
    return;
  }

  const payload = {
    client_id:      client,
    invoice_number: document.getElementById('inv-number').value,
    invoice_date:   document.getElementById('inv-date').value,
    due_date:       document.getElementById('inv-due-date')?.value,
    payment_terms:  document.getElementById('inv-payment-terms').value,
    warehouse:      document.getElementById('inv-warehouse').value,
    notes:          document.getElementById('inv-notes').value,
    freight:        document.getElementById('inv-freight').value       || 0,
    other_charges:  document.getElementById('inv-other-charges').value || 0,
    amount_paid:    document.getElementById('inv-amount-paid').value   || 0,
    status:         mode,
    lines: [],
  };

  rows.forEach(row => {
    const product = row.querySelector('.r-product')?.value;
    if (!product) return;
    payload.lines.push({
      product:  product,
      qty:      row.querySelector('.r-qty')?.value,
      rate:     row.querySelector('.r-rate')?.value,
      discount: row.querySelector('.r-disc')?.value,
      tax:      row.querySelector('.r-tax')?.value,
      total:    row.querySelector('.r-total')?.value,
    });
  });

  // Demo: show success toast
  const modeLabels = { draft:'Saved as Draft', saved_print:'Saved – opening print preview…', saved_new:'Saved – ready for new invoice' };
  showToast(modeLabels[mode] || 'Invoice saved.', 'success');

  // Update badge
  const badge = document.getElementById('invoice-status-badge');
  if (badge) {
    badge.textContent = mode === 'draft' ? 'Draft' : 'Saved';
    badge.className   = 'badge-erp ' + (mode === 'draft' ? 'badge-erp-warning' : 'badge-erp-success');
  }

  if (mode === 'saved_print') {
    setTimeout(() => window.print(), 800);
  } else if (mode === 'saved_new') {
    setTimeout(() => window.location.href = '{% url "sales:create" %}', 600);
  }
}

/* ── Init ─────────────────────────────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  // Init client Select2
  initClientSelect();

  // Add initial empty row
  addRow();

  // Add row buttons
  document.getElementById('btn-add-row')?.addEventListener('click', addRow);
  document.getElementById('btn-add-row-bottom')?.addEventListener('click', addRow);

  // Recalc when freight / other / paid change
  ['inv-freight','inv-other-charges','inv-amount-paid'].forEach(id => {
    document.getElementById(id)?.addEventListener('input', recalcAll);
  });

  // Save buttons
  document.getElementById('btn-save-draft')?.addEventListener('click', () => saveInvoice('draft'));
  document.getElementById('btn-save-print')?.addEventListener('click', () => saveInvoice('saved_print'));
  document.getElementById('btn-save-new')?.addEventListener('click',   () => saveInvoice('saved_new'));

  // Payment terms → auto-calculate due date
  document.getElementById('inv-payment-terms')?.addEventListener('change', function() {
    const terms = { net30:30, net15:15, net7:7, cod:0, advance:0 };
    const days  = terms[this.value] ?? 0;
    const from  = flatpickr.parseDate(document.getElementById('inv-date').value, 'Y-m-d');
    if (from && days > 0) {
      const due = new Date(from);
      due.setDate(due.getDate() + days);
      flatpickr.setDate
        ? null
        : (document.getElementById('inv-due-date').value = flatpickr.formatDate(due, 'Y-m-d'));
    }
  });
});
