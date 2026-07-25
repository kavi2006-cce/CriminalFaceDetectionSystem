/* ── CFCS Auth Module ─────────────────────────────────────────────── */

const Auth = {
  TOKEN_KEY: 'cfcs_token',

  getToken() {
    return localStorage.getItem(this.TOKEN_KEY);
  },

  setToken(token) {
    localStorage.setItem(this.TOKEN_KEY, token);
  },

  removeToken() {
    localStorage.removeItem(this.TOKEN_KEY);
  },

  isLoggedIn() {
    const t = this.getToken();
    if (!t) return false;
    try {
      const payload = JSON.parse(atob(t.split('.')[1]));
      return payload.exp * 1000 > Date.now();
    } catch {
      return false;
    }
  },

  requireLogin() {
    if (!this.isLoggedIn()) {
      window.location.href = '/';
      return false;
    }
    return true;
  },

  logout() {
    this.removeToken();
    document.body.style.opacity = '0';
    document.body.style.transition = 'opacity 0.35s';
    setTimeout(() => window.location.href = '/', 350);
  },

  authHeaders() {
    return {
      'Authorization': `Bearer ${this.getToken()}`,
      'Content-Type': 'application/json'
    };
  },

  authHeadersOnly() {
    return { 'Authorization': `Bearer ${this.getToken()}` };
  }
};

// Auto-redirect if not logged in (except login page)
if (window.location.pathname !== '/') {
  Auth.requireLogin();
}
