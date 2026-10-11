const alertList = document.getElementById('low-stock-alert-list');
const alertBadge = document.getElementById('low-stock-badge');

function formatStock(value) {
  const quantity = Number(value);
  return Number.isFinite(quantity)
    ? quantity.toLocaleString(undefined, { maximumFractionDigits: 2 })
    : value;
}

function setAlertMessage(message, className = 'text-muted') {
  const state = document.createElement('div');
  state.className = `p-3 ${className} text-center`;
  state.textContent = message;
  alertList.replaceChildren(state);
}

function renderAlerts(items) {
  alertBadge.textContent = String(items.length);
  alertBadge.classList.toggle('d-none', items.length === 0);

  if (!items.length) {
    setAlertMessage('All inventory levels healthy');
    return;
  }

  const fragment = document.createDocumentFragment();
  items.forEach(item => {
    const link = document.createElement('a');
    link.className = 'dropdown-item d-flex align-items-start gap-2 p-3 border-bottom';
    link.href = item.url;

    const icon = document.createElement('i');
    icon.className = 'bi bi-exclamation-triangle-fill text-danger mt-1';
    const details = document.createElement('span');
    details.className = 'd-flex flex-column text-wrap';
    const name = document.createElement('strong');
    name.textContent = item.name;
    const sku = document.createElement('small');
    sku.className = 'text-muted';
    sku.textContent = `SKU: ${item.sku}`;
    const stock = document.createElement('small');
    stock.className = 'text-danger';
    stock.textContent = `Stock: ${formatStock(item.current_stock)} / Reorder: ${formatStock(item.reorder_level)}`;
    details.append(name, sku, stock);
    link.append(icon, details);
    fragment.append(link);
  });
  alertList.replaceChildren(fragment);
}

async function loadLowStockAlerts() {
  if (!alertList || !alertBadge) return;
  try {
    const response = await fetch(alertList.dataset.url, {
      credentials: 'same-origin',
      headers: { Accept: 'application/json' },
    });
    if (!response.ok) {
      throw new Error(`Stock alerts request failed (${response.status}).`);
    }
    const data = await response.json();
    if (!Array.isArray(data.items)) {
      throw new Error('Stock alerts response has an invalid format.');
    }
    renderAlerts(data.items);
  } catch (error) {
    console.error('[Navbar] Low-stock alerts failed to load:', error);
    alertBadge.classList.add('d-none');
    setAlertMessage('Stock alerts could not be loaded.', 'text-danger');
  }
}

if (alertList && alertBadge) {
  loadLowStockAlerts();
  document.getElementById('low-stock-dropdown')?.addEventListener(
    'show.bs.dropdown',
    loadLowStockAlerts,
  );
}
