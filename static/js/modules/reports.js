/**
 * reports.js – Reports page module
 * Charts: Sales Trend, By Category, Stock by Category, P&L Trend
 * Report nav tabs, Custom Report Builder
 */

import { showToast } from '/static/js/api.js';

/* ── Report tab navigation ─────────────────────────────────────────────── */
const TAB_MAP = {
  'sales':           'rpt-sales',
  'purchase':        'rpt-purchase',
  'inventory':       'rpt-inventory',
  'profit-loss':     'rpt-profit-loss',
  'cash-flow':       'rpt-profit-loss',
  'client-ledger':   'rpt-client-ledger',
  'supplier-ledger': 'rpt-client-ledger',
  'manufacturing':   'rpt-sales',
  'distribution':    'rpt-sales',
  'custom-builder':  'rpt-custom-builder',
};

document.querySelectorAll('.report-nav-btn').forEach(btn => {
  btn.addEventListener('click', function () {
    document.querySelectorAll('.report-nav-btn').forEach(b => {
      b.classList.remove('active');
      b.setAttribute('aria-selected', 'false');
    });
    this.classList.add('active');
    this.setAttribute('aria-selected', 'true');

    const targetId = TAB_MAP[this.dataset.report] || 'rpt-sales';
    document.querySelectorAll('.report-section').forEach(s => s.classList.remove('active'));
    document.getElementById(targetId)?.classList.add('active');
  });
});

/* ── Chart helpers ────────────────────────────────────────────────────────── */
Chart.defaults.font.family = "'Inter', system-ui, sans-serif";
Chart.defaults.font.size   = 12;

function createLineChart(canvasId, labels, datasets) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;
  return new Chart(ctx, {
    type: 'line',
    data: { labels, datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      plugins: { legend: { position: 'top', labels: { usePointStyle: true } } },
      scales: {
        x: { grid: { display: false } },
        y: { grid: { color: 'rgba(0,0,0,0.04)' },
             ticks: { callback: v => '₨' + (v >= 1e6 ? (v/1e6).toFixed(1)+'M' : v >= 1e3 ? (v/1e3).toFixed(0)+'K' : v) } },
      },
    },
  });
}

function createDoughnutChart(canvasId, labels, data, colors) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;
  return new Chart(ctx, {
    type: 'doughnut',
    data: { labels, datasets: [{ data, backgroundColor: colors, borderWidth: 2, borderColor: '#fff' }] },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '60%',
      plugins: { legend: { position: 'right', labels: { usePointStyle: true, padding: 12 } } },
    },
  });
}

function createBarChart(canvasId, labels, data, color = '#1E5EFF') {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;
  return new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{ data, backgroundColor: color + 'CC', borderColor: color,
                   borderWidth: 1.5, borderRadius: 6 }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { grid: { display: false } },
        y: { grid: { color: 'rgba(0,0,0,0.04)' },
             ticks: { callback: v => '₨' + (v/1e6).toFixed(1)+'M' } },
      },
    },
  });
}

/* ── Chart data ───────────────────────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {

  /* Sales Trend */
  createLineChart('salesTrendChart',
    ['May','Jun','Jul','Aug','Sep','Oct'],
    [{
      label: 'Sales',
      data: [38e6, 42e6, 39.5e6, 51e6, 47e6, 28.4e6],
      borderColor: '#1E5EFF', backgroundColor: 'rgba(30,94,255,.08)',
      tension: 0.4, fill: true, pointRadius: 4, borderWidth: 2.5,
    }]
  );

  /* Sales by Category (doughnut) */
  createDoughnutChart('salesByCatChart',
    ['Chargers','Memory','Cables','Storage','Networking','Peripherals'],
    [12.4, 9.8, 8.2, 7.6, 5.3, 3.9],
    ['#1E5EFF','#00C6AE','#F59E0B','#EF4444','#8B5CF6','#F97316']
  );

  /* Stock by Category */
  createBarChart('stockByCatChart',
    ['Chargers','Memory','Cables','Hubs','Storage','Power','Peripherals'],
    [8.2e6, 5.4e6, 4.1e6, 3.8e6, 6.2e6, 2.9e6, 3.5e6]
  );

  /* P&L Trend */
  createLineChart('plTrendChart',
    ['May','Jun','Jul','Aug','Sep','Oct'],
    [
      {
        label: 'Gross Profit',
        data: [10.2e6, 11.8e6, 10.5e6, 13.2e6, 12.4e6, 12.7e6],
        borderColor: '#10B981', backgroundColor: 'rgba(16,185,129,.08)',
        tension: 0.4, fill: true, borderWidth: 2.5,
      },
      {
        label: 'Net Profit',
        data: [7.4e6, 8.9e6, 7.8e6, 10.1e6, 9.5e6, 9.7e6],
        borderColor: '#1E5EFF', backgroundColor: 'rgba(30,94,255,.08)',
        tension: 0.4, fill: true, borderWidth: 2.5,
      },
    ]
  );

  /* Period toggle for sales trend */
  const PERIOD_DATA = {
    daily:   { labels:['Mon','Tue','Wed','Thu','Fri','Sat','Sun'], data:[1.2e6,1.85e6,1.32e6,2.4e6,2.84e6,1.9e6,1.1e6] },
    weekly:  { labels:['W40','W41','W42','W43','W44'], data:[9.8e6,11.2e6,8.9e6,13.4e6,10.2e6] },
    monthly: { labels:['May','Jun','Jul','Aug','Sep','Oct'], data:[38e6,42e6,39.5e6,51e6,47e6,28.4e6] },
  };
  document.querySelectorAll('.chart-period-btn[data-chart="sales-trend"]').forEach(btn => {
    btn.addEventListener('click', function () {
      document.querySelectorAll('.chart-period-btn[data-chart="sales-trend"]')
        .forEach(b => b.classList.remove('active'));
      this.classList.add('active');
    });
  });

  /* Custom Report Builder */
  document.getElementById('btn-run-custom')?.addEventListener('click', () => {
    const source = document.getElementById('custom-source')?.value || 'sales';
    const results = document.getElementById('custom-results');
    if (results) results.style.display = 'block';

    /* Inject sample data */
    document.getElementById('custom-thead').innerHTML = `
      <tr>
        <th>Date</th><th>Reference</th><th>Client</th><th>Product</th>
        <th>Qty</th><th class="text-end">Total</th>
      </tr>`;
    document.getElementById('custom-tbody').innerHTML = `
      <tr><td>Oct 7</td><td class="font-mono text-primary">INV-2024-0921</td>
          <td>TechMart</td><td>USB-C 65W GaN Charger</td><td>50</td><td class="text-end">₨65,845</td></tr>
      <tr><td>Oct 6</td><td class="font-mono text-primary">INV-2024-0920</td>
          <td>Digital World</td><td>DDR4 16GB RAM</td><td>10</td><td class="text-end">₨65,000</td></tr>
      <tr><td>Oct 5</td><td class="font-mono text-primary">INV-2024-0919</td>
          <td>ByteHouse</td><td>NVMe SSD 1TB</td><td>15</td><td class="text-end">₨224,985</td></tr>`;
    showToast('Custom report generated.', 'success');
  });

  document.getElementById('btn-save-filter')?.addEventListener('click', () => {
    showToast('Report filter saved.', 'success');
  });
});

/* ── Export helper ─────────────────────────────────────────────────────────── */
window.exportReport = function(format) {
  const endpointAttribute = format === 'pdf'
    ? 'data-export-pdf-url'
    : format === 'excel'
      ? 'data-export-excel-url'
      : null;
  const button = endpointAttribute
    ? document.querySelector(`[${endpointAttribute}]`)
    : null;

  if (!button) {
    showToast('This report format is not supported.', 'error');
    return;
  }

  const activeSection = document.querySelector('.report-section.active');
  const reportType = activeSection?.id === 'rpt-inventory' ? 'inventory' : 'sales';
  const downloadUrl = new URL(button.getAttribute(endpointAttribute), window.location.origin);
  downloadUrl.searchParams.set('type', reportType);
  window.location.assign(downloadUrl);
};
