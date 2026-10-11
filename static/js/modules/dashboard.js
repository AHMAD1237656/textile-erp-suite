/**
 * dashboard.js – Dashboard page module
 * ─────────────────────────────────────
 * Handles:
 *  - KPI card auto-refresh (every 60s)
 *  - Chart.js initialisation (sales vs purchase, cash flow, top products, top clients)
 *  - Period toggle (Daily / Weekly / Monthly)
 *  - Activity feed live updates
 *  - Widget data loading
 *  - Export helpers
 */

import { api, showToast } from '/static/js/api.js';

/* ── Sample data (mirrors Django API response format) ────────────────────── */
const SAMPLE = {
  daily: {
    labels: ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'],
    sales:  [1200000,1850000,1320000,2400000,2840000,1900000,1100000],
    purchase:[900000,1100000,800000,1600000,1200000,1400000,700000],
    cashIn:  [800000,1200000,950000,1800000,2100000,1500000,900000],
    cashOut: [650000,900000,720000,1300000,1050000,1100000,580000],
  },
  weekly: {
    labels: ['W40','W41','W42','W43','W44'],
    sales:  [9800000,11200000,8900000,13400000,10200000],
    purchase:[7200000,8400000,6700000,9800000,7600000],
    cashIn:  [7100000,9300000,7800000,11200000,8400000],
    cashOut: [5400000,6800000,5900000,8100000,6200000],
  },
  monthly: {
    labels: ['May','Jun','Jul','Aug','Sep','Oct'],
    sales:  [38000000,42000000,39500000,51000000,47000000,28400000],
    purchase:[29000000,31000000,28000000,38000000,34000000,21000000],
    cashIn:  [31000000,35000000,32000000,44000000,40000000,22000000],
    cashOut: [22000000,25000000,21000000,31000000,28000000,15000000],
  },
  topProducts: {
    labels: ['USB-C 65W Charger','DDR4 16GB RAM','HDMI Cable 4K',
             'USB Hub 7-Port','SSD 1TB','RJ45 CAT6 Cable','Power Bank 20K',
             'Type-C to A Cable','Wireless Mouse','Ethernet Switch 8P'],
    data: [4200000,3800000,3100000,2900000,2600000,2400000,2200000,1900000,1700000,1500000],
  },
  topClients: {
    labels: ['TechMart Pvt Ltd','Digital World','ByteHouse Corp','MicroHub',
             'Lahore Gadgets','Pixel Store','IT Galaxy','CompuZone','NetStar','Prime Tech'],
    data: [6800000,5400000,4900000,4200000,3700000,3100000,2800000,2300000,2100000,1800000],
  },
};

const ACTIVITY_FEED = [
  { type:'success', icon:'cart-check',      text:'Sale invoice <strong>INV-2024-0921</strong> created – TechMart ₨420K',   time:'Just now'  },
  { type:'primary', icon:'box-seam',         text:'Stock received: 500× USB-C Cable 3A – Main Warehouse',                   time:'3 min ago' },
  { type:'warning', icon:'exclamation-tri',  text:'Low stock alert: DDR4 16GB RAM – 8 units remaining',                     time:'8 min ago' },
  { type:'success', icon:'cash-coin',        text:'Payment received ₨450,000 from <strong>Digital World</strong>',          time:'12 min ago'},
  { type:'danger',  icon:'credit-card',      text:'Credit limit exceeded: TechMart Pvt Ltd (₨2.3M)',                        time:'18 min ago'},
  { type:'info',    icon:'ship',             text:'Container <strong>OOLU-441892</strong> cleared customs – Port Qasim',    time:'1 hr ago'  },
  { type:'primary', icon:'person-check',     text:'New client registered: <strong>Prime Tech Peshawar</strong>',            time:'2 hrs ago' },
  { type:'success', icon:'check2-circle',    text:'Production order <strong>MO-2024-0038</strong> completed (500 units)',   time:'3 hrs ago' },
];

/* ── Chart colour palette ─────────────────────────────────────────────────── */
const COLORS = {
  primary:  '#1E5EFF',
  accent:   '#00C6AE',
  warning:  '#F59E0B',
  danger:   '#EF4444',
  success:  '#10B981',
  purple:   '#8B5CF6',
  orange:   '#F97316',
};

/* ── Shared Chart.js defaults ─────────────────────────────────────────────── */
if (window.Chart) {
  Chart.defaults.font.family = "'Inter', system-ui, sans-serif";
  Chart.defaults.font.size   = 12;
  Chart.defaults.color       = getComputedStyle(document.documentElement)
                                 .getPropertyValue('--erp-text-muted').trim() || '#8898AA';
}

/* ── Chart instances store ────────────────────────────────────────────────── */
const charts = {};

/* ══════════════════════════════════════════════════════════════════════════════
   CHART BUILDERS
   ══════════════════════════════════════════════════════════════════════════════ */

function buildSalesVsPurchaseChart(period = 'daily') {
  if (!window.Chart) return;
  const ctx = document.getElementById('salesVsPurchaseChart');
  if (!ctx) return;

  const d = SAMPLE[period];
  if (charts.salesvspurchase) charts.salesvspurchase.destroy();

  charts.salesvspurchase = new Chart(ctx, {
    type: 'line',
    data: {
      labels: d.labels,
      datasets: [
        {
          label: 'Sales',
          data: d.sales,
          borderColor: COLORS.primary,
          backgroundColor: 'rgba(30,94,255,0.08)',
          tension: 0.4,
          fill: true,
          pointRadius: 4,
          pointHoverRadius: 7,
          pointBackgroundColor: COLORS.primary,
          borderWidth: 2.5,
        },
        {
          label: 'Purchases',
          data: d.purchase,
          borderColor: COLORS.accent,
          backgroundColor: 'rgba(0,198,174,0.08)',
          tension: 0.4,
          fill: true,
          pointRadius: 4,
          pointHoverRadius: 7,
          pointBackgroundColor: COLORS.accent,
          borderWidth: 2.5,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      plugins: {
        legend: { position: 'top', labels: { usePointStyle: true, padding: 16 } },
        tooltip: {
          callbacks: {
            label: ctx => ` ${ctx.dataset.label}: ₨ ${ERP.formatNumber(ctx.parsed.y)}`,
          },
        },
      },
      scales: {
        x: { grid: { display: false } },
        y: {
          grid: { color: 'rgba(0,0,0,0.04)' },
          ticks: { callback: v => '₨ ' + ERP.formatNumber(v) },
        },
      },
    },
  });
}

function buildCashFlowChart(period = 'daily') {
  if (!window.Chart) return;
  const ctx = document.getElementById('cashFlowChart');
  if (!ctx) return;

  const d = SAMPLE[period];
  if (charts.cashflow) charts.cashflow.destroy();

  charts.cashflow = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: d.labels,
      datasets: [
        {
          label: 'Cash In',
          data: d.cashIn,
          backgroundColor: 'rgba(16,185,129,0.75)',
          borderColor: COLORS.success,
          borderWidth: 1.5,
          borderRadius: 6,
        },
        {
          label: 'Cash Out',
          data: d.cashOut,
          backgroundColor: 'rgba(239,68,68,0.65)',
          borderColor: COLORS.danger,
          borderWidth: 1.5,
          borderRadius: 6,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      plugins: {
        legend: { position: 'top', labels: { usePointStyle: true, padding: 16 } },
        tooltip: {
          callbacks: {
            label: ctx => ` ${ctx.dataset.label}: ₨ ${ERP.formatNumber(ctx.parsed.y)}`,
          },
        },
      },
      scales: {
        x: { grid: { display: false } },
        y: {
          grid: { color: 'rgba(0,0,0,0.04)' },
          ticks: { callback: v => '₨ ' + ERP.formatNumber(v) },
        },
      },
    },
  });
}

function buildTopProductsChart(period = 'daily') {
  if (!window.Chart) return;
  const ctx = document.getElementById('topProductsChart');
  if (!ctx) return;

  if (charts.topproducts) charts.topproducts.destroy();

  charts.topproducts = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: SAMPLE.topProducts.labels,
      datasets: [{
        label: 'Sales Amount',
        data: SAMPLE.topProducts.data,
        backgroundColor: [
          'rgba(30,94,255,0.8)','rgba(0,198,174,0.8)','rgba(245,158,11,0.8)',
          'rgba(239,68,68,0.8)','rgba(139,92,246,0.8)','rgba(249,115,22,0.8)',
          'rgba(16,185,129,0.8)','rgba(59,130,246,0.8)','rgba(236,72,153,0.8)',
          'rgba(107,114,128,0.8)',
        ],
        borderRadius: 6,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      indexAxis: 'y',
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: ctx => ` ₨ ${ERP.formatNumber(ctx.parsed.x)}`,
          },
        },
      },
      scales: {
        x: {
          grid: { color: 'rgba(0,0,0,0.04)' },
          ticks: { callback: v => '₨ ' + ERP.formatNumber(v) },
        },
        y: { grid: { display: false } },
      },
    },
  });
}

function buildTopClientsChart(period = 'daily') {
  if (!window.Chart) return;
  const ctx = document.getElementById('topClientsChart');
  if (!ctx) return;

  if (charts.topclients) charts.topclients.destroy();

  charts.topclients = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: SAMPLE.topClients.labels,
      datasets: [{
        label: 'Revenue',
        data: SAMPLE.topClients.data,
        backgroundColor: 'rgba(30,94,255,0.75)',
        borderColor: COLORS.primary,
        borderWidth: 1.5,
        borderRadius: 6,
        hoverBackgroundColor: COLORS.primary,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      indexAxis: 'y',
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: ctx => ` ₨ ${ERP.formatNumber(ctx.parsed.x)}`,
          },
        },
      },
      scales: {
        x: {
          grid: { color: 'rgba(0,0,0,0.04)' },
          ticks: { callback: v => '₨ ' + ERP.formatNumber(v) },
        },
        y: { grid: { display: false } },
      },
    },
  });
}

async function loadDashboardAnalytics() {
  const salesCanvas = document.getElementById('monthlySalesDispatchChart');
  const categoryCanvas = document.getElementById('inventoryCategoryChart');
  if (!salesCanvas || !categoryCanvas) return;

  const salesEmpty = document.getElementById('monthly-sales-dispatch-empty');
  const categoryEmpty = document.getElementById('inventory-category-empty');
  const showEmpty = (canvas, element, message) => {
    canvas.classList.add('d-none');
    if (element) {
      element.textContent = message;
      element.classList.remove('d-none');
    }
  };

  if (!window.Chart) {
    showEmpty(salesCanvas, salesEmpty, 'Charts are unavailable right now.');
    showEmpty(categoryCanvas, categoryEmpty, 'Charts are unavailable right now.');
    return;
  }

  try {
    const response = await fetch(salesCanvas.dataset.url, {
      credentials: 'same-origin',
      headers: { Accept: 'application/json' },
    });
    if (!response.ok) {
      throw new Error(`Dashboard analytics request failed (${response.status}).`);
    }
    const data = await response.json();
    const monthly = data.monthly;
    const hasTrendData = Array.isArray(monthly?.labels)
      && monthly.labels.length > 0
      && (monthly.sales.some(value => Number(value) > 0)
        || monthly.dispatches.some(value => Number(value) > 0));

    if (!hasTrendData) {
      showEmpty(salesCanvas, salesEmpty, 'No sales or dispatch data available.');
    } else {
      salesCanvas.classList.remove('d-none');
      salesEmpty?.classList.add('d-none');
      charts.monthlySalesDispatch?.destroy();
      charts.monthlySalesDispatch = new Chart(salesCanvas, {
        type: 'bar',
        data: {
          labels: monthly.labels,
          datasets: [
            {
              type: 'bar',
              label: 'Sales (₨)',
              data: monthly.sales,
              backgroundColor: 'rgba(30,94,255,0.7)',
              borderColor: COLORS.primary,
              borderWidth: 1,
              yAxisID: 'sales',
            },
            {
              type: 'line',
              label: 'Dispatched units',
              data: monthly.dispatches,
              borderColor: COLORS.accent,
              backgroundColor: COLORS.accent,
              tension: 0.35,
              yAxisID: 'dispatches',
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          interaction: { mode: 'index', intersect: false },
          scales: {
            sales: {
              type: 'linear',
              position: 'left',
              beginAtZero: true,
              ticks: { callback: value => `₨ ${ERP.formatNumber(value)}` },
            },
            dispatches: {
              type: 'linear',
              position: 'right',
              beginAtZero: true,
              grid: { drawOnChartArea: false },
            },
          },
        },
      });
    }

    const categories = Array.isArray(data.inventory_categories)
      ? data.inventory_categories.filter(item => Number(item.stock) > 0)
      : [];
    if (!categories.length) {
      showEmpty(categoryCanvas, categoryEmpty, 'No inventory category data available.');
    } else {
      categoryCanvas.classList.remove('d-none');
      categoryEmpty?.classList.add('d-none');
      charts.inventoryCategory?.destroy();
      charts.inventoryCategory = new Chart(categoryCanvas, {
        type: 'doughnut',
        data: {
          labels: categories.map(item => item.name),
          datasets: [{
            data: categories.map(item => item.stock),
            backgroundColor: [
              COLORS.primary, COLORS.accent, COLORS.warning, COLORS.danger,
              COLORS.purple, COLORS.orange, COLORS.success,
            ],
            borderColor: '#fff',
            borderWidth: 2,
          }],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          cutout: '58%',
          plugins: { legend: { position: 'right' } },
        },
      });
    }
  } catch (error) {
    console.error('[Dashboard] Analytics failed to load:', error);
    showEmpty(salesCanvas, salesEmpty, 'Analytics could not be loaded.');
    showEmpty(categoryCanvas, categoryEmpty, 'Analytics could not be loaded.');
  }
}

/* ══════════════════════════════════════════════════════════════════════════════
   PERIOD TOGGLE
   ══════════════════════════════════════════════════════════════════════════════ */
function initPeriodToggles() {
  document.querySelectorAll('.chart-period-btn').forEach(btn => {
    btn.addEventListener('click', function () {
      // Update active state within this button group
      const chartId = this.dataset.chart;
      document.querySelectorAll(`.chart-period-btn[data-chart="${chartId}"]`).forEach(b => {
        b.classList.remove('active');
      });
      this.classList.add('active');

      const period = this.dataset.period;
      switch (chartId) {
        case 'salesvspurchase': buildSalesVsPurchaseChart(period); break;
        case 'cashflow':        buildCashFlowChart(period);        break;
        case 'topproducts':     buildTopProductsChart(period);     break;
        case 'topclients':      buildTopClientsChart(period);      break;
      }
    });
  });
}

/* ══════════════════════════════════════════════════════════════════════════════
   ACTIVITY FEED
   ══════════════════════════════════════════════════════════════════════════════ */
function renderActivityFeed(items) {
  const feed = document.getElementById('activity-feed');
  if (!feed) return;

  const colorMap = {
    success: 'var(--erp-success)', primary: 'var(--erp-primary)',
    warning: 'var(--erp-warning)', danger: 'var(--erp-danger)',
    info: 'var(--erp-info)',
  };

  feed.innerHTML = items.map(item => `
    <div class="activity-item animate-fade">
      <span class="activity-dot" style="background:${colorMap[item.type]||'#999'};margin-top:5px;"></span>
      <div class="activity-content">
        <p class="activity-text">${item.text}</p>
        <span class="activity-meta">${item.time}</span>
      </div>
    </div>
  `).join('');
}

/* ══════════════════════════════════════════════════════════════════════════════
   KPI REFRESH
   ══════════════════════════════════════════════════════════════════════════════ */
async function refreshKPIs() {
  try {
    // In production: const res = await api.get('/api/dashboard/kpis/');
    // Using sample data for demonstration
    const kpiData = {
      sales: { value: '₨ 2.84M', pct: '12.4%', up: true },
      recv:  { value: '₨ 18.6M', pct: '4.2%',  up: false },
      pay:   { value: '₨ 9.2M',  pct: '3.1%',  up: false },
      stock: { value: '₨ 34.1M', pct: '6.8%',  up: true  },
    };

    // Animate value updates
    const animate = (el, newVal) => {
      if (!el) return;
      el.style.transform = 'scale(0.95)';
      el.style.opacity   = '0.5';
      setTimeout(() => {
        el.textContent = newVal;
        el.style.transform = 'scale(1)';
        el.style.opacity   = '1';
        el.style.transition = 'all 0.3s ease';
      }, 200);
    };

    animate(document.getElementById('kpi-sales-val'), kpiData.sales.value);
    animate(document.getElementById('kpi-recv-val'),  kpiData.recv.value);
    animate(document.getElementById('kpi-pay-val'),   kpiData.pay.value);
    animate(document.getElementById('kpi-stock-val'), kpiData.stock.value);

    // Update last refreshed time
    const ts = new Date().toLocaleTimeString('en-PK', { hour:'2-digit', minute:'2-digit' });
    const el = document.getElementById('last-updated');
    if (el) el.innerHTML = `<i class="bi bi-arrow-clockwise me-1"></i>Updated ${ts}`;

  } catch (err) {
    console.warn('[Dashboard] KPI refresh failed:', err);
  }
}

/* ══════════════════════════════════════════════════════════════════════════════
   EXPORT HELPERS
   ══════════════════════════════════════════════════════════════════════════════ */
window.exportChart = function(chartId) {
  const chart = charts[chartId];
  if (!chart) return;
  const link = document.createElement('a');
  link.download = `${chartId}-${new Date().toISOString().slice(0,10)}.png`;
  link.href     = chart.toBase64Image('image/png', 1.0);
  link.click();
  showToast('Chart exported as PNG', 'success');
};

/* ── Inventory widget ────────────────────────────────────────────────────── */
function formatInventoryQuantity(value) {
  const quantity = Number(value);
  return Number.isFinite(quantity)
    ? quantity.toLocaleString(undefined, { maximumFractionDigits: 2 })
    : value;
}

function renderInventoryMessage(widget, message, className = 'text-muted') {
  const emptyState = document.createElement('div');
  emptyState.className = `p-3 ${className} text-center`;
  emptyState.textContent = message;
  widget.replaceChildren(emptyState);
}

function renderInventoryItems(widget, items) {
  if (!items.length) {
    renderInventoryMessage(widget, 'No inventory records found.');
    return;
  }

  const fragment = document.createDocumentFragment();
  items.forEach(item => {
    const row = document.createElement('div');
    row.className = 'd-flex align-items-center justify-content-between py-2 border-bottom';

    const details = document.createElement('div');
    const name = document.createElement('div');
    name.style.cssText = 'font-size:13px;font-weight:500;color:var(--erp-text-primary)';
    name.textContent = item.name;
    const sku = document.createElement('div');
    sku.style.cssText = 'font-size:11px;color:var(--erp-text-muted)';
    sku.textContent = `SKU: ${item.sku}`;
    details.append(name, sku);

    const quantity = document.createElement('div');
    quantity.className = 'text-end';
    const badge = document.createElement('span');
    badge.className = `badge-erp ${item.status === 'low_stock' ? 'badge-erp-danger' : 'badge-erp-warning'}`;
    badge.textContent = `${formatInventoryQuantity(item.qty)}${item.unit ? ` ${item.unit}` : ''}`;
    const reorder = document.createElement('div');
    reorder.style.cssText = 'font-size:10px;color:var(--erp-text-muted)';
    reorder.textContent = `Min: ${formatInventoryQuantity(item.reorder)}`;
    quantity.append(badge, reorder);

    row.append(details, quantity);
    fragment.append(row);
  });
  widget.replaceChildren(fragment);
}

window.loadInventoryWidget = async function() {
  const widget = document.getElementById('inventory-widget');
  if (!widget) return;

  const endpoint = widget.dataset.url;
  if (!endpoint) {
    renderInventoryMessage(widget, 'Inventory could not be loaded.', 'text-danger');
    return;
  }

  const skeleton = document.createElement('div');
  skeleton.id = 'inv-skeleton';
  skeleton.setAttribute('role', 'status');
  skeleton.setAttribute('aria-label', 'Loading inventory');
  for (let index = 0; index < 6; index += 1) {
    const row = document.createElement('div');
    row.className = 'skeleton skeleton-row mb-2';
    skeleton.append(row);
  }
  widget.replaceChildren(skeleton);

  try {
    const response = await fetch(endpoint, { credentials: 'same-origin' });
    if (!response.ok) {
      throw new Error(`Inventory request failed (${response.status}).`);
    }
    const data = await response.json();
    if (!Array.isArray(data.items)) {
      throw new Error('Inventory response has an invalid format.');
    }
    renderInventoryItems(widget, data.items);
  } catch (error) {
    console.error('[Dashboard] Inventory widget failed to load:', error);
    renderInventoryMessage(widget, 'Inventory could not be loaded. Try refreshing.', 'text-danger');
  }
};

/* ══════════════════════════════════════════════════════════════════════════════
   GLOBAL DASHBOARD REFRESH
   ══════════════════════════════════════════════════════════════════════════════ */
window.refreshDashboard = async function() {
  const btn = document.getElementById('btn-refresh-all');
  if (btn) {
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>Refreshing…';
  }

  await refreshKPIs();

  // Re-render activity with shuffled "just now" items
  renderActivityFeed(ACTIVITY_FEED);

  if (btn) {
    btn.disabled = false;
    btn.innerHTML = '<i class="bi bi-arrow-clockwise"></i> Refresh';
  }
  showToast('Dashboard refreshed', 'success', 2000);
};

/* ══════════════════════════════════════════════════════════════════════════════
   INIT
   ══════════════════════════════════════════════════════════════════════════════ */
document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('inventory-widget-refresh')?.addEventListener('click', () => {
    window.loadInventoryWidget();
  });
  window.loadInventoryWidget();
  loadDashboardAnalytics();

  // Build all 4 charts
  buildSalesVsPurchaseChart();
  buildCashFlowChart();
  buildTopProductsChart();
  buildTopClientsChart();

  // Period toggles
  initPeriodToggles();

  // Activity feed initial render
  renderActivityFeed(ACTIVITY_FEED);

  // Auto-refresh KPIs every 60 seconds
  setInterval(refreshKPIs, 60_000);

  // Mark-all-read button
  document.getElementById('mark-all-read-btn')?.addEventListener('click', () => {
    showToast('All alerts marked as read', 'success', 2000);
  });

  // Redraw charts when dark mode changes
  const observer = new MutationObserver(() => {
    buildSalesVsPurchaseChart();
    buildCashFlowChart();
    buildTopProductsChart();
    buildTopClientsChart();
  });
  observer.observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
});
