// Función de Supabase: elimina la cuenta de quien la llama (borra su fila de progreso, su recordatorio y su usuario).
// Solo puede borrar la cuenta del propio usuario: la identidad sale del token de sesión, nunca de un dato que mande el navegador.
// No necesita secretos propios: SUPABASE_URL, SUPABASE_ANON_KEY y SUPABASE_SERVICE_ROLE_KEY los pone Supabase solos.
import { createClient } from "npm:@supabase/supabase-js@2";

const cors = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
};
const json = (body: unknown, status = 200) => new Response(JSON.stringify(body), { status, headers: { ...cors, "Content-Type": "application/json" } });

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: cors });
  if (req.method !== "POST") return json({ error: "Método no permitido" }, 405);

  const token = (req.headers.get("Authorization") || "").replace(/^Bearer\s+/i, "");
  if (!token) return json({ error: "No autorizado" }, 401);

  const admin = createClient(Deno.env.get("SUPABASE_URL")!, Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!, { auth: { persistSession: false } });
  const { data: u, error: uerr } = await admin.auth.getUser(token);
  if (uerr || !u || !u.user) return json({ error: "Sesión no válida" }, 401);
  const uid = u.user.id;

  // Confirmación explícita: el navegador manda { confirm: "ELIMINAR" }.
  let body: { confirm?: string } = {};
  try { body = await req.json(); } catch (_) { /* cuerpo vacío */ }
  if (body.confirm !== "ELIMINAR") return json({ error: "Falta la confirmación" }, 400);

  // Primero los datos propios; después el usuario. Si algo falla, se informa y se puede reintentar (borrar es idempotente).
  const r1 = await admin.from("user_profiles").delete().eq("id", uid);
  if (r1.error) return json({ error: "No se pudo borrar el progreso" }, 500);
  const r2 = await admin.from("email_reminders").delete().eq("user_id", uid);
  if (r2.error) return json({ error: "No se pudo borrar el recordatorio" }, 500);
  const r3 = await admin.auth.admin.deleteUser(uid);
  if (r3.error) return json({ error: "No se pudo borrar la cuenta" }, 500);
  return json({ ok: true });
});
