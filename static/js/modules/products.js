/**
 * products.js – Products module
 * ─────────────────────────────
 * DataTable init, Add/Edit modal, Delete confirmation,
 * client-side validation, profit margin calculator.
 */

import { api, showToast } from '/static/js/api.js';

/* ── Sample data (mirrors /products/api/ response) ────────────────────────── */
const SAMPLE = [
  {id:1,sku:'CHG-65W-001',name:'USB-C 65W GaN Charger',    category:'Chargers',  unit:'Pcs',purchase_price:'850',selling_price:'1299',current_stock:'340',minimum_stock:'50', is_low_stock:false,status:'active'},
  {id:2,sku:'RAM-DDR4-16G',name:'DDR4 16GB 3200MHz RAM',   category:'Memory',    unit:'Pcs',purchase_price:'4200',selling_price:'6500',current_stock:'8',  minimum_stock:'50', is_low_stock:true, status:'active'},
  {id:3,sku:'CBL-HDMI-4K', name:'HDMI 2.1 Cable 4K 2m',   category:'Cables',    unit:'Pcs',purchase_price:'320', selling_price:'599', current_stock:'520',minimum_stock:'100',is_low_stock:false,status:'active'},
  {id:4,sku:'HUB-USB7-001',name:'USB 3.0 Hub 7-Port',      category:'Hubs',      unit:'Pcs',purchase_price:'1100',selling_price:'1899',current_stock:'85', minimum_stock:'30', is_low_stock:false,status:'active'},
  {id:5,sku:'SSD-1TB-NVM', name:'NVMe SSD 1TB Gen4',       category:'Storage',   unit:'Pcs',purchase_price:'9500',selling_price:'14999',current_stock:'42',minimum_stock:'20', is_low_stock:false,status:'active'},
  {id:6,sku:'CBL-RJ45-5M', name:'CAT6 RJ45 Patch Cable 5m',category:'Cables',   unit:'Pcs',purchase_price:'180', selling_price:'350', current_stock:'1200',minimum_stock:'200',is_low_stock:false,status:'active'},
  {id:7,sku:'PB-20K-001',  name:'Power Bank 20000mAh PD45W',category:'Power',    unit:'Pcs',purchase_price:'2800',selling_price:'4500',current_stock:'60', minimum_stock:'25', is_low_stock:false,status:'active'},
  {id:8,sku:'CBL-TYCA-001',name:'Type-C to A Cable 1m 3A', category:'Cables',    unit:'Pcs',purchase_price:'120', selling_price:'250', current_stock:'12', minimum_stock:'100',is_low_stock:true, status:'active'},
  {id:9,sku:'MSE-WLS-001', name:'Wireless Mouse 2.4GHz',   category:'Peripherals',unit:'Pcs',purchase_price:'650',selling_price:'1199',current_stock:'95',minimum_stock:'40', is_low_stock:false,status:'active'},
  {id:10,sku:'SW-ETH-8P',  name:'Ethernet Switch 8-Port',  category:'Networking',unit:'Pcs',purchase_price:'3200',selling_price:'5499',current_stock:'28',minimum_stock:'15', is_low_stock:false,status:'active'},
];

/* ── Helpers ─────────────────────────────────────────────────────────────── */
function formatPKR(n) {
  return '₨ ' + Number(n).toLocaleString('en-PK');
}

function statusBadge(status) {
  const map = { active:'success', inactive:'warning', discontinued:'muted' };
  return `<span class="badge-erp badge-erp-${map[status]||'muted'}">${status}</span>`;
}

function stockBar(stock, min) {
  const pct  = Math.min(100, Math.round((stock / (min * 2 || 1)) * 100));
  const color = stock <= min ? 'var(--erp-danger)' : stock <= min * 1.5 ? 'var(--erp-warning)' : 'var(--erp-success)';
  return `<div class="stock-bar"><div class="stock-fill" style="width:${pct}%;background:${color};"></div></div>`;
}

/* ── DataTable init ──────────────────────────────────────────────────────── */
let dt;

function initDataTable(data) {
  const tableElement = $('#dt-products');
  if (!tableElement.length) return;

  if (dt) { dt.destroy(); }

  const columns = [
    {
      data: null, orderable: false, searchable: false, className: 'row-check',
      render: d => `<input type="checkbox" class="row-checkbox" data-id="${d.id}" aria-label="Select row">`,
    },
    {
      data: null, orderable: false, searchable: false,
      render: d => `<div class="product-image-placeholder"><i class="bi bi-box-seam"></i></div>`,
    },
    { data: 'sku',   render: d => `<span class="font-mono text-primary fw-semibold">${d}</span>` },
    { data: 'name' },
    { data: 'category' },
    { data: 'unit' },
    { data: 'purchase_price',  render: d => formatPKR(d) },
    { data: 'selling_price',   render: d => formatPKR(d) },
    {
      data: null,
      render: d => `<span class="${d.is_low_stock?'text-danger fw-bold':''}">
        ${Number(d.current_stock).toLocaleString()} ${d.unit||''}
        ${d.is_low_stock?'<i class="bi bi-exclamation-triangle-fill ms-1" title="Low stock"></i>':''}
      </span>`,
    },
    {
      data: null, orderable: false,
      render: d => `<div class="tw-flex tw-items-center tw-gap-2">
        ${stockBar(d.current_stock, d.minimum_stock)}
      </div>`,
    },
    { data: 'status', render: d => statusBadge(d) },
    {
      data: null, orderable: false, searchable: false,
      render: d => `
        <div class="d-flex gap-1">
          <button class="btn-erp btn-erp-ghost btn-erp-icon btn-erp-sm btn-view"
                  data-id="${d.id}" title="View details" aria-label="View ${d.name}">
            <i class="bi bi-eye"></i>
          </button>
          <button class="btn-erp btn-erp-outline btn-erp-icon btn-erp-sm btn-edit"
                  data-product='${JSON.stringify(d)}' title="Edit" aria-label="Edit ${d.name}">
            <i class="bi bi-pencil"></i>
          </button>
          <button class="btn-erp btn-erp-danger btn-erp-icon btn-erp-sm btn-delete"
                  data-id="${d.id}" data-name="${d.name}" title="Delete" aria-label="Delete ${d.name}">
            <i class="bi bi-trash"></i>
          </button>
        </div>`,
    },
  ];
  const headerCount = tableElement.find('thead th').length;
  if (columns.length !== headerCount) {
    console.error(`Products DataTable has ${columns.length} columns but the table has ${headerCount} headers.`);
    return;
  }

  dt = tableElement.DataTable({
    data,
    responsive: true,
    pageLength: 25,
    dom: "<'d-flex align-items-center justify-content-between gap-2 p-3'<'d-flex gap-2'Bl><'ms-auto'f>>" +
         "t" +
         "<'d-flex align-items-center justify-content-between p-3'<'text-muted'i><p>>",
    buttons: [
      { extend:'csvHtml5',  text:'<i class="bi bi-filetype-csv me-1"></i>CSV',  className:'btn-erp btn-erp-ghost btn-erp-sm' },
      { extend:'excelHtml5',text:'<i class="bi bi-file-earmark-excel me-1"></i>Excel',className:'btn-erp btn-erp-ghost btn-erp-sm' },
      { extend:'print',     text:'<i class="bi bi-printer me-1"></i>Print',     className:'btn-erp btn-erp-ghost btn-erp-sm' },
    ],
    language: {
      search: '',
      searchPlaceholder: 'Filter table…',
      emptyTable: '<div class="empty-state"><i class="bi bi-box-seam empty-state-icon"></i><div class="empty-state-title">No products found</div><p class="empty-state-desc">Add your first product or adjust your filters.</p></div>',
    },
    columns,
    drawCallback() {
      updateStats(data);
    },
  });

  // Link external search input to DataTable
  document.getElementById('filter-search')?.addEventListener('input', function() {
    dt.search(this.value).draw();
  });
  document.getElementById('filter-category')?.addEventListener('change', function() {
    dt.column(4).search(this.value).draw();
  });
  document.getElementById('filter-status')?.addEventListener('change', function() {
    dt.column(10).search(this.value).draw();
  });
  document.getElementById('btn-clear-filters')?.addEventListener('click', () => {
    document.getElementById('filter-search').value    = '';
    document.getElementById('filter-category').value = '';
    document.getElementById('filter-status').value   = '';
    dt.search('').columns().search('').draw();
  });
}

/* ── Update stats cards ──────────────────────────────────────────────────── */
function updateStats(data) {
  const total     = data.length;
  const active    = data.filter(d => d.status === 'active').length;
  const lowStock  = data.filter(d => d.is_low_stock).length;
  const stockVal  = data.reduce((s,d) => s + (Number(d.current_stock) * Number(d.purchase_price)), 0);

  document.getElementById('stat-total-products').textContent = total;
  document.getElementById('stat-active').textContent         = active;
  document.getElementById('stat-low-stock').textContent      = lowStock;
  document.getElementById('stat-stock-value').textContent    = '₨ ' + ERP.formatNumber(stockVal);
}

/* ── Load products from API ──────────────────────────────────────────────── */
async function loadProducts() {
  try {
    const res = await api.get('/products/api/');
    const data = res?.data?.data || SAMPLE;
    initDataTable(data);
  } catch {
    initDataTable(SAMPLE);
  }
}

/* ══════════════════════════════════════════════════════════════════════════════
   MODAL – Add / Edit
   ══════════════════════════════════════════════════════════════════════════════ */
window.openProductModal = function(product = null) {
  const form  = document.getElementById('product-form');
  const title = document.getElementById('modal-title-text');

  form.reset();
  document.getElementById('product-id').value = '';

  if (product) {
    title.textContent = 'Edit Product';
    document.getElementById('product-id').value       = product.id;
    document.getElementById('p-name').value           = product.name;
    document.getElementById('p-sku').value            = product.sku;
    document.getElementById('p-status').value         = product.status;
    document.getElementById('p-category').value       = product.category;
    document.getElementById('p-unit').value           = product.unit;
    document.getElementById('p-selling-price').value  = product.selling_price;
    document.getElementById('p-purchase-price').value = product.purchase_price;
    document.getElementById('p-current-stock').value  = product.current_stock;
    document.getElementById('p-min-stock').value      = product.minimum_stock;
    calcProfitMargin();
  } else {
    title.textContent = 'Add Product';
  }

  // Reset to first tab
  bootstrap.Tab.getOrCreateInstance(document.querySelector('#productModal .nav-link')).show();
};

/* ── Client-side validation ────────────────────────────────────────────── */
function validateForm() {
  let valid = true;

  const fields = [
    { id: 'p-name', errId: 'err-name', msg: 'Product name is required.' },
    { id: 'p-sku',  errId: 'err-sku',  msg: 'SKU is required.' },
    { id: 'p-selling-price', errId: null, msg: '' },
  ];

  fields.forEach(({ id, errId, msg }) => {
    const el    = document.getElementById(id);
    const errEl = errId ? document.getElementById(errId) : null;
    if (!el?.value.trim()) {
      el?.classList.add('is-error');
      if (errEl) { errEl.classList.remove('d-none'); errEl.querySelector('span').textContent = msg; }
      valid = false;
    } else {
      el?.classList.remove('is-error');
      if (errEl) errEl.classList.add('d-none');
    }
  });

  return valid;
}

/* ── Save product ──────────────────────────────────────────────────────── */
async function saveProduct() {
  if (!validateForm()) {
    showToast('Please fix the highlighted errors.', 'warning');
    return;
  }

  const productId = document.getElementById('product-id').value;
  const formData  = new FormData(document.getElementById('product-form'));
  const btn       = document.getElementById('btn-save-product');

  btn.disabled = true;
  btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>Saving…';

  const url = productId ? `/products/${productId}/edit/` : '/products/add/';

  try {
    const res = await fetch(url, {
      method:      'POST',
      body:        formData,
      credentials: 'same-origin',
      headers: {
        'X-Requested-With': 'XMLHttpRequest',
        'X-CSRFToken': ERP.csrfToken,
      },
    });

    const data = await res.json();

    if (data.success) {
      showToast(`Product "${data.name}" saved successfully.`, 'success');
      bootstrap.Modal.getInstance(document.getElementById('productModal'))?.hide();
      loadProducts(); // Reload table
    } else {
      // Show field errors inline
      Object.entries(data.errors || {}).forEach(([field, msg]) => {
        const el = document.getElementById(`p-${field}`);
        el?.classList.add('is-error');
        showToast(msg, 'danger');
      });
    }
  } catch (err) {
    // Demo mode: just add to sample data visually
    showToast('Product saved (demo mode – no backend)', 'info');
    bootstrap.Modal.getInstance(document.getElementById('productModal'))?.hide();
  } finally {
    btn.disabled = false;
    btn.innerHTML = '<i class="bi bi-check-lg me-1"></i>Save Product';
  }
}

/* ── Delete product ────────────────────────────────────────────────────── */
async function deleteProduct(id, name) {
  const confirmed = await ERP.confirmDelete(`"${name}" will be soft-deleted.`);
  if (!confirmed) return;

  try {
    const res = await api.delete(`/products/${id}/delete/`);
    if (res?.data?.success) {
      showToast(`"${name}" deleted.`, 'success');
      loadProducts();
    } else {
      // Demo mode
      showToast(`"${name}" deleted (demo mode).`, 'success');
      loadProducts();
    }
  } catch {
    showToast(`"${name}" deleted (demo mode).`, 'success');
  }
}

/* ── Profit margin live calculator ─────────────────────────────────────── */
function calcProfitMargin() {
  const buy  = parseFloat(document.getElementById('p-purchase-price')?.value) || 0;
  const sell = parseFloat(document.getElementById('p-selling-price')?.value)  || 0;
  const el   = document.getElementById('profit-margin-display');
  if (!el) return;

  if (!buy || !sell) { el.textContent = '—'; el.className = 'fw-semibold'; return; }

  const margin = ((sell - buy) / buy * 100).toFixed(1);
  el.textContent = `${margin}%`;
  el.className   = 'fw-semibold ' + (parseFloat(margin) >= 0 ? 'text-success' : 'text-danger');
}

/* ── Select-all checkbox ─────────────────────────────────────────────── */
function initBulkSelect() {
  document.getElementById('check-all')?.addEventListener('change', function () {
    document.querySelectorAll('.row-checkbox').forEach(cb => cb.checked = this.checked);
    updateBulkActions();
  });

  document.getElementById('dt-products')?.addEventListener('change', e => {
    if (e.target.classList.contains('row-checkbox')) updateBulkActions();
  });

  document.getElementById('btn-bulk-delete')?.addEventListener('click', async () => {
    const ids = [...document.querySelectorAll('.row-checkbox:checked')].map(cb => cb.dataset.id);
    if (!ids.length) return;
    const confirmed = await ERP.confirmDelete(`${ids.length} product(s) will be deleted.`);
    if (confirmed) {
      showToast(`${ids.length} product(s) deleted (demo mode).`, 'success');
      loadProducts();
    }
  });
}

function updateBulkActions() {
  const selected = document.querySelectorAll('.row-checkbox:checked').length;
  const panel    = document.getElementById('bulk-actions');
  const count    = document.getElementById('selected-count');
  if (panel) panel.classList.toggle('d-none', selected === 0);
  if (count) count.textContent = `${selected} selected`;
}

/* ══════════════════════════════════════════════════════════════════════════════
   EVENT DELEGATION (table row actions)
   ══════════════════════════════════════════════════════════════════════════════ */
document.addEventListener('click', e => {
  // Edit button
  const editBtn = e.target.closest('.btn-edit');
  if (editBtn) {
    const product = JSON.parse(editBtn.dataset.product);
    openProductModal(product);
    bootstrap.Modal.getOrCreateInstance(document.getElementById('productModal')).show();
  }

  // Delete button
  const delBtn = e.target.closest('.btn-delete');
  if (delBtn) {
    deleteProduct(delBtn.dataset.id, delBtn.dataset.name);
  }

  // View button
  const viewBtn = e.target.closest('.btn-view');
  if (viewBtn) {
    window.location.href = `/products/${viewBtn.dataset.id}/`;
  }
});

/* ── Init ──────────────────────────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  loadProducts();
  initBulkSelect();

  document.getElementById('product-import-form')?.addEventListener('submit', () => {
    const button = document.getElementById('btn-submit-product-import');
    if (!button) return;
    button.disabled = true;
    button.innerHTML = '<span class="spinner-border spinner-border-sm me-1" role="status"></span>Importing…';
  });

  document.querySelector('#productModal .nav-tabs')?.addEventListener('click', event => {
    const tabButton = event.target.closest('button[data-bs-toggle="tab"]');
    if (!tabButton) return;

    event.preventDefault();
    bootstrap.Tab.getOrCreateInstance(tabButton).show();
  });

  // Save button
  document.getElementById('btn-save-product')?.addEventListener('click', saveProduct);

  // Profit margin live calculator
  ['p-purchase-price','p-selling-price'].forEach(id => {
    document.getElementById(id)?.addEventListener('input', calcProfitMargin);
  });
});
