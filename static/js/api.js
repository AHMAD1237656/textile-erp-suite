/**
 * api.js – Shared Fetch wrapper for TechImport ERP
 * ─────────────────────────────────────────────────
 * Provides:
 *  - CSRF token injection on all mutating requests
 *  - Centralised loading state management
 *  - Standardised error handling (401 redirect, 403 toast, 500 toast)
 *  - Request cancellation via AbortController
 *  - Retry logic for transient failures
 *
 * Usage:
 *   import { api } from '/static/js/api.js';
 *   const data = await api.get('/api/products/');
 *   const res  = await api.post('/api/products/', { name: 'USB Cable' });
 */

// ── CSRF helper ──────────────────────────────────────────────────────────────
function getCsrfToken() {
  // Django sets the cookie; Bootstrap forms inject {% csrf_token %} as well
  const meta = document.querySelector('meta[name="csrf-token"]');
  if (meta) return meta.getAttribute('content');

  const match = document.cookie.match(/csrftoken=([^;]+)/);
  return match ? match[1] : '';
}

// ── Toast notification (uses ERP toast system) ────────────────────────────────
function showToast(message, type = 'info', duration = 4000) {
  const container = document.getElementById('erp-toast-container');
  if (!container) return;

  const icons = {
    success: 'check-circle-fill',
    danger:  'x-circle-fill',
    warning: 'exclamation-triangle-fill',
    info:    'info-circle-fill',
  };

  const id = `toast-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`;
  const el = document.createElement('div');
  el.className = `toast align-items-center text-bg-${type} border-0 show`;
  el.setAttribute('role', type === 'danger' ? 'alert' : 'status');
  el.setAttribute('aria-live', type === 'danger' ? 'assertive' : 'polite');
  el.id = id;
  el.innerHTML = `
    <div class="d-flex">
      <div class="toast-body d-flex align-items-center gap-2">
        <i class="bi bi-${icons[type] || 'info-circle-fill'}"></i>
        <span>${message}</span>
      </div>
      <button type="button" class="btn-close btn-close-white me-2 m-auto"
              data-bs-dismiss="toast" aria-label="Close"></button>
    </div>`;
  container.appendChild(el);

  // Auto-remove after duration
  setTimeout(() => {
    el.classList.remove('show');
    setTimeout(() => el.remove(), 350);
  }, duration);
}

// ── Loading state overlay ─────────────────────────────────────────────────────
function setLoading(element, loading) {
  if (!element) return;
  if (loading) {
    element.dataset.origText = element.innerHTML;
    element.disabled = true;
    element.innerHTML = `<span class="spinner-border spinner-border-sm" role="status"></span> Loading…`;
  } else {
    element.disabled = false;
    element.innerHTML = element.dataset.origText || element.innerHTML;
  }
}

// ── Core fetch wrapper ────────────────────────────────────────────────────────
async function request(url, options = {}, { triggerEl = null, silent = false, retries = 1 } = {}) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 30_000);

  if (triggerEl) setLoading(triggerEl, true);

  const headers = {
    'Content-Type': 'application/json',
    'X-CSRFToken':  getCsrfToken(),
    'X-Requested-With': 'XMLHttpRequest',
    ...options.headers,
  };

  // If body is FormData, let browser set Content-Type with boundary
  if (options.body instanceof FormData) {
    delete headers['Content-Type'];
  }

  let lastError;

  for (let attempt = 0; attempt <= retries; attempt++) {
    try {
      const response = await fetch(url, {
        credentials: 'same-origin',
        signal: controller.signal,
        ...options,
        headers,
      });

      clearTimeout(timeoutId);
      if (triggerEl) setLoading(triggerEl, false);

      // Handle HTTP errors
      if (response.status === 401) {
        window.location.href = `/login/?next=${encodeURIComponent(window.location.pathname)}`;
        return null;
      }

      if (response.status === 403) {
        if (!silent) showToast('You do not have permission to perform this action.', 'warning');
        return null;
      }

      if (response.status === 404) {
        if (!silent) showToast('Resource not found.', 'warning');
        return null;
      }

      if (response.status >= 500) {
        const text = await response.text();
        if (!silent) showToast('Server error. Please try again or contact support.', 'danger');
        console.error('[ERP API] Server error:', response.status, text);
        return null;
      }

      // Parse JSON or return raw response
      const contentType = response.headers.get('Content-Type') || '';
      if (contentType.includes('application/json')) {
        const data = await response.json();
        return { ok: response.ok, status: response.status, data };
      }

      return { ok: response.ok, status: response.status, data: await response.text() };

    } catch (err) {
      lastError = err;
      if (err.name === 'AbortError') {
        if (!silent) showToast('Request timed out. Please check your connection.', 'warning');
        break;
      }
      if (attempt < retries) {
        await new Promise(r => setTimeout(r, 500 * (attempt + 1))); // exponential backoff
        continue;
      }
      if (!silent) showToast(`Network error: ${err.message}`, 'danger');
      console.error('[ERP API] Fetch error:', err);
    }
  }

  if (triggerEl) setLoading(triggerEl, false);
  clearTimeout(timeoutId);
  return null;
}

// ── Public API surface ────────────────────────────────────────────────────────
export const api = {
  get:    (url, opts = {}) => request(url, { method: 'GET',    ...opts }),
  post:   (url, body, opts = {}) => request(url, { method: 'POST',   body: JSON.stringify(body), ...opts }),
  put:    (url, body, opts = {}) => request(url, { method: 'PUT',    body: JSON.stringify(body), ...opts }),
  patch:  (url, body, opts = {}) => request(url, { method: 'PATCH',  body: JSON.stringify(body), ...opts }),
  delete: (url, opts = {}) => request(url, { method: 'DELETE',  ...opts }),

  /** Upload file(s) via FormData */
  upload: (url, formData, opts = {}) => request(url, { method: 'POST', body: formData, ...opts }),
};

// ── Export helpers ────────────────────────────────────────────────────────────
export { showToast, setLoading, getCsrfToken };

// ── Global keyboard shortcuts ─────────────────────────────────────────────────
document.addEventListener('keydown', (e) => {
  // Skip if user is typing in an input
  if (['INPUT', 'TEXTAREA', 'SELECT'].includes(e.target.tagName)) return;

  switch (e.key) {
    case 'n':
    case 'N':
      // Trigger "New" button if present
      document.getElementById('btn-new')?.click();
      break;
    case '/':
      e.preventDefault();
      document.querySelector('.navbar-search-input, [data-search-focus]')?.focus();
      break;
    case 'Escape':
      // Close any open Bootstrap modal
      document.querySelector('.modal.show')?.dispatchEvent(new Event('erp:close'));
      import('https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.esm.min.js')
        .then(({ Modal }) => {
          document.querySelectorAll('.modal.show').forEach(el => Modal.getInstance(el)?.hide());
        }).catch(() => {});
      break;
  }
});
