// Datos con mails de coaches y vacantes: solo se entregan con una sesión válida de Supabase.
// Los archivos viven en /priv/ dentro del sitio (ASSETS) pero esta función se ejecuta antes que el hosting estático.
const SUPABASE_URL = "https://dliayalkzvaugukhxmcb.supabase.co";
const SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRsaWF5YWxrenZhdWd1a2h4bWNiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI1MzkwOTMsImV4cCI6MjA4ODExNTA5M30.vGBprr8FKBxTayS6Q6ZbWIxUZKItY4avgMJbUGgQC1E";
const ok = new Map(); // token -> vence (ms); cache por isolate para no consultar a Supabase en cada archivo

async function validToken(token) {
  const now = Date.now();
  const hit = ok.get(token);
  if (hit && hit > now) return true;
  try {
    const r = await fetch(`${SUPABASE_URL}/auth/v1/user`, { headers: { apikey: SUPABASE_ANON_KEY, Authorization: `Bearer ${token}` } });
    if (!r.ok) return false;
    ok.set(token, now + 5 * 60 * 1000);
    if (ok.size > 500) ok.clear();
    return true;
  } catch (e) { return false; }
}

export async function onRequestGet({ request, env }) {
  const m = /^Bearer\s+(.+)$/i.exec(request.headers.get("Authorization") || "");
  if (!m || !(await validToken(m[1]))) {
    return new Response("Se necesita una cuenta", { status: 401, headers: { "Cache-Control": "no-store" } });
  }
  const res = await env.ASSETS.fetch(request);
  const out = new Response(res.body, res);
  out.headers.set("Cache-Control", "private, max-age=86400");
  return out;
}
