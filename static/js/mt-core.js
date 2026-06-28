/**
 * mt-core.js — Merma Textil Analytics
 * Módulo compartido: sesión, guard, toast
 *
 * [TODO-API] Cuando haya backend, reemplazar la función login()
 * por un fetch POST /api/auth/login
 */

const MT = (() => {

  /* ─── Usuarios hardcodeados ─────────────────────────────────────────────
   * [TODO-API] Reemplazar por POST /api/auth/login
   * Retorno esperado: { ok: true, token, user: { usuario, nombre, rol, tienda } }
   */
  const USUARIOS = [
    { usuario: 'admin',    password: 'admin123', rol: 'admin',   nombre: 'Administrador'       },
    { usuario: 'empresa1', password: 'emp123',   rol: 'empresa', nombre: 'Textil Sur S.A.',     tienda: 'Textil Sur'         },
    { usuario: 'empresa2', password: 'emp456',   rol: 'empresa', nombre: 'Confecciones Norte',  tienda: 'Confecciones Norte'  },
    { usuario: 'empresa3', password: 'emp789',   rol: 'empresa', nombre: 'Industrias Fibra',    tienda: 'Industrias Fibra'   },
  ];

  /* ─── Sesión ─────────────────────────────────────────────────────────────*/
  function getUser()   { return JSON.parse(sessionStorage.getItem('mt_user') || 'null'); }
  function setUser(u)  { sessionStorage.setItem('mt_user', JSON.stringify(u)); }
  function clearUser() { sessionStorage.removeItem('mt_user'); sessionStorage.removeItem('mt_welcomed'); }

  function login(usuario, password) {
    // [TODO-API] fetch POST /api/auth/login
    const match = USUARIOS.find(u => u.usuario === usuario && u.password === password);
    if (!match) return { ok: false, error: 'Usuario o contraseña incorrectos.' };
    setUser({ usuario: match.usuario, nombre: match.nombre, rol: match.rol, tienda: match.tienda || null });
    return { ok: true };
  }

  function logout() {
    clearUser();
    window.location.href = 'login.html';
  }

  function guard(rolRequerido) {
    const user = getUser();
    if (!user) { window.location.href = 'login.html'; return; }
    if (rolRequerido && user.rol !== rolRequerido) { window.location.href = 'login.html'; }
  }

  /* ─── Toast ──────────────────────────────────────────────────────────────*/
  function _ensureStyles() {
    if (document.getElementById('mt-toast-styles')) return;
    const s = document.createElement('style');
    s.id = 'mt-toast-styles';
    s.textContent = `
      #mt-toast-container {
        position: fixed; bottom: 24px; right: 24px; z-index: 99999;
        display: flex; flex-direction: column; gap: 10px;
        pointer-events: none;
      }
      .mt-toast {
        display: flex; align-items: center; gap: 10px;
        background: #1A1D27; border: 1px solid #2A2D3E;
        border-radius: 12px; padding: 12px 16px;
        font-family: 'Segoe UI', system-ui, sans-serif;
        font-size: 0.82rem; color: #F0F2FF;
        box-shadow: 0 8px 32px rgba(0,0,0,0.5);
        max-width: 300px; pointer-events: all;
        animation: mt-in 0.25s cubic-bezier(.22,.68,0,1.2) both;
      }
      .mt-toast.out { animation: mt-out 0.2s ease-in both; }
      .mt-toast.success { border-color: rgba(0,229,160,0.4); }
      .mt-toast.error   { border-color: rgba(255,100,100,0.4); }
      .mt-toast.info    { border-color: rgba(124,111,255,0.4); }
      @keyframes mt-in  { from{opacity:0;transform:translateX(30px)} to{opacity:1;transform:translateX(0)} }
      @keyframes mt-out { from{opacity:1;transform:translateX(0)}    to{opacity:0;transform:translateX(30px)} }
    `;
    document.head.appendChild(s);
    const c = document.createElement('div');
    c.id = 'mt-toast-container';
    document.body.appendChild(c);
  }

  function toast(msg, tipo = 'info', ms = 3500) {
    _ensureStyles();
    const icons = { success: '✅', error: '❌', info: 'ℹ️' };
    const el = document.createElement('div');
    el.className = `mt-toast ${tipo}`;
    el.innerHTML = `<span>${icons[tipo]}</span><span>${msg}</span>`;
    document.getElementById('mt-toast-container').appendChild(el);
    setTimeout(() => {
      el.classList.add('out');
      setTimeout(() => el.remove(), 220);
    }, ms);
  }

  /* ─── Bienvenida ─────────────────────────────────────────────────────────*/
  function bienvenida() {
    if (sessionStorage.getItem('mt_welcomed')) return;
    sessionStorage.setItem('mt_welcomed', '1');
    const user = getUser();
    if (!user) return;
    setTimeout(() => {
      toast(`¡Bienvenido, ${user.nombre}!`, 'success', 4000);
    }, 400);
  }

  /* ─── Rellena elementos de UI con datos de sesión ────────────────────────*/
  function fillUI() {
    const user = getUser();
    if (!user) return;
    // Nombre en sidebar y topbar
    document.querySelectorAll('[data-mt-nombre]').forEach(el => el.textContent = user.nombre);
    document.querySelectorAll('[data-mt-usuario]').forEach(el => el.textContent = '@' + user.usuario);
    // Avatar inicial
    document.querySelectorAll('[data-mt-avatar]').forEach(el => el.textContent = user.nombre[0].toUpperCase());
    // Toast de bienvenida
    bienvenida();
  }

  return { login, logout, guard, getUser, toast, fillUI };

})();
