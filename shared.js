// ── LRMS Shared JavaScript ────────────────────────────────────────────────────

// ── THEME ──────────────────────────────────────────────────────────────────────
function initTheme() {
  const saved = localStorage.getItem('lrms-theme') || 'light';
  document.documentElement.setAttribute('data-theme', saved);
  updateThemeBtn(saved);
}

function toggleTheme() {
  const cur = document.documentElement.getAttribute('data-theme') || 'light';
  const next = cur === 'dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', next);
  localStorage.setItem('lrms-theme', next);
  updateThemeBtn(next);
  if (next === 'dark') startStars();
  else stopStars();
}

function updateThemeBtn(theme) {
  const btn = document.getElementById('theme-toggle');
  if (btn) btn.textContent = theme === 'dark' ? '☀️' : '🌙';
}

// ── STAR FIELD ─────────────────────────────────────────────────────────────────
let starsAF = null, starsCtx = null;
const STARS = [];

function startStars() {
  const canvas = document.getElementById('star-canvas');
  if (!canvas) return;
  canvas.width  = window.innerWidth;
  canvas.height = window.innerHeight;
  starsCtx = canvas.getContext('2d');

  if (!STARS.length) {
    for (let i = 0; i < 160; i++) {
      STARS.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        r: Math.random() * 1.4 + 0.3,
        speed: Math.random() * 0.12 + 0.03,
        phase: Math.random() * Math.PI * 2,
        opacity: Math.random() * 0.5 + 0.2,
        dy: Math.random() * 0.08 + 0.02
      });
    }
  }
  if (starsAF) cancelAnimationFrame(starsAF);
  animateStars();
}

function stopStars() {
  if (starsAF) { cancelAnimationFrame(starsAF); starsAF = null; }
}

function animateStars() {
  const canvas = document.getElementById('star-canvas');
  if (!canvas || !starsCtx) return;
  starsCtx.clearRect(0, 0, canvas.width, canvas.height);
  const t = Date.now() / 1000;
  STARS.forEach(s => {
    const alpha = s.opacity * (0.6 + 0.4 * Math.sin(t * s.speed * 3 + s.phase));
    starsCtx.beginPath();
    starsCtx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
    starsCtx.fillStyle = `rgba(180,210,255,${alpha})`;
    starsCtx.fill();
    s.y -= s.dy;
    if (s.y < -2) { s.y = canvas.height + 2; s.x = Math.random() * canvas.width; }
  });
  starsAF = requestAnimationFrame(animateStars);
}

window.addEventListener('resize', () => {
  const canvas = document.getElementById('star-canvas');
  if (canvas) { canvas.width = window.innerWidth; canvas.height = window.innerHeight; }
});

// ── ANALOG CLOCK ───────────────────────────────────────────────────────────────
function drawClock(canvasId) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const size = canvas.width;
  const cx = size / 2, cy = size / 2, r = size / 2 - 2;
  const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
  const now = new Date();
  const sec  = now.getSeconds() + now.getMilliseconds() / 1000;
  const min  = now.getMinutes() + sec / 60;
  const hour = (now.getHours() % 12) + min / 60;

  ctx.clearRect(0, 0, size, size);

  // Face
  ctx.beginPath(); ctx.arc(cx, cy, r, 0, Math.PI * 2);
  ctx.fillStyle = isDark ? '#182438' : '#F8FAFF';
  ctx.fill();
  ctx.strokeStyle = isDark ? '#334466' : '#B8C5E0';
  ctx.lineWidth = 1.5; ctx.stroke();

  // Hour ticks
  for (let i = 0; i < 12; i++) {
    const a = (i / 12) * Math.PI * 2;
    const inner = i % 3 === 0 ? r * 0.76 : r * 0.85;
    ctx.beginPath();
    ctx.moveTo(cx + Math.sin(a) * inner, cy - Math.cos(a) * inner);
    ctx.lineTo(cx + Math.sin(a) * (r - 2), cy - Math.cos(a) * (r - 2));
    ctx.strokeStyle = isDark ? '#4A6080' : '#94A3B8';
    ctx.lineWidth = i % 3 === 0 ? 2 : 1;
    ctx.stroke();
  }

  // Hour hand
  drawHand(ctx, cx, cy, hour / 12 * Math.PI * 2, r * 0.52, 2.5, isDark ? '#60B8F0' : '#0B6BA8');
  // Minute hand
  drawHand(ctx, cx, cy, min / 60 * Math.PI * 2, r * 0.70, 2, isDark ? '#94D4F0' : '#1A8FD8');
  // Second hand (smooth)
  drawHand(ctx, cx, cy, sec / 60 * Math.PI * 2, r * 0.78, 1, isDark ? '#FF7A40' : '#E05A1A');

  // Center dot
  ctx.beginPath(); ctx.arc(cx, cy, 3, 0, Math.PI * 2);
  ctx.fillStyle = isDark ? '#FF7A40' : '#E05A1A'; ctx.fill();
}

function drawHand(ctx, cx, cy, angle, length, width, color) {
  ctx.beginPath();
  ctx.moveTo(cx, cy);
  ctx.lineTo(cx + Math.sin(angle) * length, cy - Math.cos(angle) * length);
  ctx.strokeStyle = color; ctx.lineWidth = width;
  ctx.lineCap = 'round'; ctx.stroke();
}

function startClock(canvasId, labelId) {
  function tick() {
    drawClock(canvasId);
    if (labelId) {
      const el = document.getElementById(labelId);
      if (el) {
        const now = new Date();
        el.textContent = now.toLocaleDateString('en-IN', { weekday: 'short', day: '2-digit', month: 'short', year: 'numeric' });
      }
    }
    requestAnimationFrame(tick);
  }
  tick();
}

// ── VISITOR COUNTER ─────────────────────────────────────────────────────────────
function getVisitorCount() {
  let count = parseInt(localStorage.getItem('lrms-visitor-count') || '0');
  const lastVisit = localStorage.getItem('lrms-last-visit');
  const today = new Date().toDateString();
  if (lastVisit !== today) {
    count++;
    localStorage.setItem('lrms-visitor-count', count);
    localStorage.setItem('lrms-last-visit', today);
  }
  return count;
}

// ── TICKER ─────────────────────────────────────────────────────────────────────
function buildTicker(libs) {
  const el = document.getElementById('ticker-inner');
  if (!el || !libs) return;
  const items = libs.map(([, name]) =>
    `<span class="ticker-item"><span class="ticker-dot"></span>${name}</span>`
  ).join('');
  el.innerHTML = items + items; // duplicate for seamless loop
}

// ── UTILITY ────────────────────────────────────────────────────────────────────
function esc(s) {
  if (!s && s !== 0) return '';
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

function showMsg(elId, type, text, ms = 5500) {
  const el = document.getElementById(elId);
  if (!el) return;
  el.className = 'msg-box show ' + type;
  el.textContent = text;
  if (ms > 0) setTimeout(() => { el.className = 'msg-box'; el.textContent = ''; }, ms);
}

async function doLogout() {
  await fetch('/api/logout', { method: 'POST' });
  window.location.href = '/login';
}

// ── INIT ───────────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  const theme = document.documentElement.getAttribute('data-theme');
  if (theme === 'dark') startStars();
  // Update visitor count display
  const vcEl = document.getElementById('visitor-count');
  if (vcEl) vcEl.textContent = getVisitorCount().toLocaleString('en-IN');
});
