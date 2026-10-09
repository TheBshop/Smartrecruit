// Smartrecruit · Analítica con PostHog
import posthog from 'posthog-js';

const POSTHOG_KEY = 'phc_vYFHqqsZqSTwrxwaYXjTAi4UdLpedqWJafJpkjqJVBUT';
const POSTHOG_HOST = 'https://us.i.posthog.com'; // si tu proyecto está en EU: 'https://eu.i.posthog.com'
const SUPABASE_SESSION_KEY = 'sb-dliayalkzvaugukhxmcb-auth-token';
const NAV = ['INICIO','UNIVERSIDADES','RECRUITING NEEDS','CALENDARIO','RECURSOS','ELEGIBILIDAD','EXÁMENES','CONVERSOR GPA','BUSCAR POR CARRERA','TU VIDEO','BECAS Y COSTOS','GUARDAR MI PROGRESO','MI PERFIL'];

posthog.init(POSTHOG_KEY, {
  api_host: POSTHOG_HOST,
  person_profiles: 'identified_only',
  opt_out_capturing_by_default: true,
  capture_pageview: true,
  session_recording: { maskAllInputs: true },
});
window.posthog = posthog;

const track = (ev, props) => { try { posthog.capture(ev, props || {}); } catch (e) {} };
const parse = (v) => { try { return JSON.parse(v); } catch (e) { return null; } };
const count = (v) => { const o = parse(v); return Array.isArray(o) ? o.length : (o && typeof o === 'object' ? Object.keys(o).length : 0); };

// ---------- Sesión de usuario (Supabase) ----------
function syncUser(raw) {
  const s = parse(raw); const u = s && (s.user || (s.currentSession && s.currentSession.user));
  if (!u || !u.id) return;
  if (posthog.get_distinct_id() !== u.id) {
    posthog.identify(u.id); // solo el ID interno: nunca email ni nombre
    const nuevo = u.created_at && (Date.now() - new Date(u.created_at).getTime()) < 15 * 60 * 1000;
    track(nuevo ? 'registro_completado' : 'sesion_iniciada');
  }
}
syncUser(localStorage.getItem(SUPABASE_SESSION_KEY));

// ---------- Acciones dentro de la app (lo que la app guarda) ----------
const proto = Storage.prototype, origSet = proto.setItem, origRemove = proto.removeItem;
proto.setItem = function (k, v) {
  let prev = null;
  try { if (this === localStorage) prev = localStorage.getItem(k); } catch (e) {}
  origSet.apply(this, arguments);
  if (this !== localStorage) return;
  try {
    if (k === SUPABASE_SESSION_KEY) return syncUser(v);
    if (prev === v) return;
    switch (k) {
      case 'rr_profile': {
        const p = parse(v) || {};
        track(prev ? 'perfil_actualizado' : 'perfil_completado', { deporte: p.sport, genero: p.gender });
        break;
      }
      case 'rr_favorites': track('lista_universidades_actualizada', { cantidad: count(v), agrego: count(v) > count(prev) }); break;
      case 'rr_outreach_log': {
        if (count(v) > count(prev)) track('mail_registrado', { total_universidades: count(v) });
        const nv = parse(v) || {}, pv = parse(prev) || {};
        Object.keys(nv).forEach((u) => {
          const st = nv[u] && nv[u].status, old = pv[u] && pv[u].status;
          if (st && st !== old && ['respondio', 'visita', 'oferta', 'rechazo'].includes(st)) {
            track(st === 'oferta' ? 'oferta_recibida' : st === 'visita' ? 'visita_acordada' : st === 'rechazo' ? 'coach_rechazo' : 'coach_respondio', { division: nv[u].division || null });
          }
        });
        break;
      }
      case 'rr_exam_best': track('examen_practicado'); break;
      case 'rr_eligibility_checklist': track('checklist_elegibilidad_actualizado'); break;
      case 'rr_checkins': track('checkin_registrado'); break;
      case 'rr_admissions': track('admision_actualizada'); break;
      case 'rr_visit_days': track('visita_agendada'); break;
    }
  } catch (e) {}
};
proto.removeItem = function (k) {
  origRemove.apply(this, arguments);
  if (this === localStorage && k === SUPABASE_SESSION_KEY) { track('sesion_cerrada'); posthog.reset(); }
};

// ---------- Clics: secciones y apertura del mail ----------
document.addEventListener('click', (e) => {
  const a = e.target.closest && e.target.closest('a[href]');
  if (a) {
    const h = a.getAttribute('href') || '';
    const prov = h.includes('mail.google.com') ? 'gmail' : h.includes('outlook') ? 'outlook' : h.startsWith('mailto:') ? 'app_de_mail' : null;
    if (prov) track('mail_abierto', { proveedor: prov });
    return;
  }
  const b = e.target.closest && e.target.closest('button');
  if (!b) return;
  const t = (b.innerText || '').replace(/[^\p{L}\s]/gu, ' ').replace(/\s+/g, ' ').trim().toUpperCase();
  if (NAV.includes(t)) track('seccion_vista', { seccion: t });
}, true);

// ---------- Aviso de cookies ----------
function banner() {
  let c = null; try { c = localStorage.getItem('sr_consent'); } catch (e) {}
  if (c === 'si') { posthog.opt_in_capturing(); return; }
  if (c === 'no') return;
  const d = document.createElement('div');
  d.setAttribute('role', 'dialog'); d.setAttribute('aria-label', 'Aviso de cookies');
  d.style.cssText = 'position:fixed;left:12px;right:12px;bottom:12px;z-index:2147483647;max-width:560px;margin:0 auto;background:#111;color:#fff;border:1px solid #333;border-radius:12px;padding:16px;font:14px/1.45 Inter,system-ui,sans-serif;box-shadow:0 8px 30px rgba(0,0,0,.35)';
  d.innerHTML = '<div style="margin-bottom:12px">Usamos cookies de analítica para entender cómo se usa Smartrecruit y mejorarlo. No vendemos tus datos ni registramos lo que escribís. <a href="#" data-sr-priv style="color:#9fd3ff">Más info</a></div><div style="display:flex;gap:8px;justify-content:flex-end;flex-wrap:wrap"><button data-sr="no" style="padding:9px 14px;border-radius:8px;border:1px solid #555;background:transparent;color:#fff;cursor:pointer">Rechazar</button><button data-sr="si" style="padding:9px 14px;border-radius:8px;border:0;background:#fff;color:#111;font-weight:600;cursor:pointer">Aceptar</button></div>';
  d.addEventListener('click', (e) => {
    const v = e.target.getAttribute && e.target.getAttribute('data-sr');
    if (e.target.hasAttribute && e.target.hasAttribute('data-sr-priv')) {
      e.preventDefault();
      const btn = [...document.querySelectorAll('button')].find(x => /pol[ií]tica de privacidad/i.test(x.innerText));
      if (btn) btn.click(); else window.location.href = '/';
      return;
    }
    if (v === 'si') { try { localStorage.setItem('sr_consent','si'); } catch (e) {} posthog.opt_in_capturing(); syncUser(localStorage.getItem(SUPABASE_SESSION_KEY)); d.remove(); }
    if (v === 'no') { try { localStorage.setItem('sr_consent','no'); } catch (e) {} posthog.opt_out_capturing(); d.remove(); }
  });
  document.body.appendChild(d);
}
if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', banner); else banner();

// Para que puedas reabrir el aviso: window.srCookies()
window.srCookies = () => { try { localStorage.removeItem('sr_consent'); } catch (e) {} posthog.opt_out_capturing(); banner(); };
