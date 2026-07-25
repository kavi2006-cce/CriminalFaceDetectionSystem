/* ── CFCS API Client ──────────────────────────────────────────────── */

const API = {
  async request(method, path, body = null, isForm = false) {
    const headers = Auth.authHeadersOnly();
    const opts = { method, headers };

    if (body) {
      if (isForm) {
        opts.body = body; // FormData
      } else {
        headers['Content-Type'] = 'application/json';
        opts.body = JSON.stringify(body);
      }
    }

    const res = await fetch(path, opts);

    if (res.status === 401) {
      Auth.logout();
      throw new Error('Session expired');
    }

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Request failed' }));
      throw new Error(err.detail || `HTTP ${res.status}`);
    }

    return res.json().catch(() => ({}));
  },

  get:    (path)              => API.request('GET',    path),
  post:   (path, body)        => API.request('POST',   path, body),
  put:    (path, body)        => API.request('PUT',    path, body),
  delete: (path)              => API.request('DELETE', path),
  postForm: (path, formData)  => API.request('POST',   path, formData, true),
  putForm:  (path, formData)  => API.request('PUT',    path, formData, true),

  // Specific endpoints
  stats:             () => API.get('/api/stats'),
  criminals:         (params = '') => API.get(`/api/criminals${params}`),
  criminal:          (id) => API.get(`/api/criminals/${id}`),
  deleteCriminal:    (id) => API.delete(`/api/criminals/${id}`),
  detections:        (params = '') => API.get(`/api/detections${params}`),
  alerts:            (params = '') => API.get(`/api/alerts${params}`),
  resolveAlert:      (id) => API.put(`/api/alerts/${id}/resolve`, {}),
  cameras:           () => API.get('/api/cameras'),
  trends:            (days = 7) => API.get(`/api/analytics/trends?days=${days}`),
  threatDist:        () => API.get('/api/analytics/threat-distribution'),
  cameraActivity:    () => API.get('/api/analytics/camera-activity'),
  geoData:           () => API.get('/api/analytics/geo-data'),
  chat:              (query) => API.post('/api/chat', { query }),
};

/* ── Toast Notifications ──────────────────────────────────────────── */

const Toast = {
  container: null,

  init() {
    if (!this.container) {
      this.container = document.getElementById('toast-container');
      if (!this.container) {
        this.container = document.createElement('div');
        this.container.id = 'toast-container';
        document.body.appendChild(this.container);
      }
    }
  },

  show(message, type = 'info', duration = 4000) {
    this.init();
    const icons = { success: 'check_circle', error: 'error', warning: 'warning', info: 'info' };
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
      <span class="material-icons-round" style="font-size:18px">${icons[type] || 'info'}</span>
      <span>${message}</span>
    `;
    this.container.appendChild(toast);
    setTimeout(() => {
      toast.style.animation = 'fadeOut 0.3s ease forwards';
      setTimeout(() => toast.remove(), 300);
    }, duration);
  },

  success: (msg, d) => Toast.show(msg, 'success', d),
  error:   (msg, d) => Toast.show(msg, 'error',   d),
  warning: (msg, d) => Toast.show(msg, 'warning', d),
  info:    (msg, d) => Toast.show(msg, 'info',    d),
};

/* ── Threat badge helper ──────────────────────────────────────────── */

function threatBadge(level) {
  const map = {
    Low:      'badge-low',
    Medium:   'badge-medium',
    High:     'badge-high',
    Critical: 'badge-critical',
    Unknown:  'badge-unknown',
  };
  return `<span class="badge ${map[level] || 'badge-unknown'}">${level || 'Unknown'}</span>`;
}

function statusBadge(status) {
  const map = {
    Active:   'badge-active',
    Wanted:   'badge-wanted',
    Arrested: 'badge-low',
    Closed:   'badge-closed',
    Online:   'badge-online',
    Offline:  'badge-offline',
    New:      'badge-high',
    Reviewed: 'badge-medium',
    Dismissed:'badge-closed',
  };
  return `<span class="badge ${map[status] || 'badge-unknown'}">${status || '—'}</span>`;
}

function timeAgo(dateStr) {
  const d = new Date(dateStr);
  const diff = (Date.now() - d) / 1000;
  if (diff < 60) return `${Math.floor(diff)}s ago`;
  if (diff < 3600) return `${Math.floor(diff/60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff/3600)}h ago`;
  return d.toLocaleDateString();
}

function formatDate(dateStr) {
  if (!dateStr) return '—';
  return new Date(dateStr).toLocaleString('en-IN', { day:'2-digit', month:'short', year:'numeric', hour:'2-digit', minute:'2-digit' });
}

/* ── Modal helpers ────────────────────────────────────────────────── */

function openModal(id) {
  const el = document.getElementById(id);
  if (el) el.classList.add('open');
}

function closeModal(id) {
  const el = document.getElementById(id);
  if (el) el.classList.remove('open');
}

// Close on overlay click
document.addEventListener('click', (e) => {
  if (e.target.classList.contains('modal-overlay')) {
    e.target.classList.remove('open');
  }
});

/* ── Page enter animation ─────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  document.body.style.opacity = '0';
  document.body.style.transition = 'opacity 0.4s ease';
  requestAnimationFrame(() => { document.body.style.opacity = '1'; });

  // Set active nav link
  const path = window.location.pathname;
  document.querySelectorAll('.nav-item').forEach(a => {
    if (a.getAttribute('href') === path) a.classList.add('active');
  });
});
