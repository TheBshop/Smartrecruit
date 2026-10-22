// Función de Supabase: manda el recordatorio semanal por Resend a quienes lo activaron.
// Secretos necesarios (Supabase → Edge Functions → Secrets):
//   RESEND_API_KEY   clave de Resend (empieza con re_)
//   CRON_SECRET      una clave larga inventada por vos; el programador de tareas la manda en el encabezado x-cron-secret
// Opcionales:
//   REMINDER_FROM    remitente, por defecto "Smartrecruit <recordatorios@smartrecruit.com.ar>" (el dominio tiene que estar verificado en Resend)
//   REPLY_TO         dirección de respuesta, por defecto contactosmartrecruit@gmail.com
//   SITE_URL         por defecto https://smartrecruit.com.ar
// SUPABASE_URL y SUPABASE_SERVICE_ROLE_KEY los pone Supabase solos.
import { createClient } from "npm:@supabase/supabase-js@2";
import { buildReminderEmail, consentAllows, isDue } from "./email.ts";

const MAX_PER_RUN = 200;
const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));
const json = (body: unknown, status = 200) => new Response(JSON.stringify(body), { status, headers: { "Content-Type": "application/json" } });

Deno.serve(async (req) => {
  const cronSecret = Deno.env.get("CRON_SECRET") || "";
  const apiKey = Deno.env.get("RESEND_API_KEY") || "";
  if (!cronSecret || !apiKey) return json({ error: "Faltan los secretos CRON_SECRET o RESEND_API_KEY" }, 500);
  if (req.headers.get("x-cron-secret") !== cronSecret) return json({ error: "No autorizado" }, 401);

  const url = new URL(req.url);
  const force = url.searchParams.get("force") === "1"; // solo para pruebas: ignora el "una vez por semana"
  const dry = url.searchParams.get("dry") === "1";      // arma todo pero no manda nada
  const from = Deno.env.get("REMINDER_FROM") || "Smartrecruit <recordatorios@smartrecruit.com.ar>";
  const replyTo = Deno.env.get("REPLY_TO") || "contactosmartrecruit@gmail.com";
  const siteUrl = Deno.env.get("SITE_URL") || "https://smartrecruit.com.ar";

  const db = createClient(Deno.env.get("SUPABASE_URL")!, Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!, { auth: { persistSession: false } });
  const now = new Date();

  const { data: rows, error } = await db.from("email_reminders")
    .select("user_id,email,digest,unsub_token,last_sent_at")
    .eq("enabled", true).order("last_sent_at", { ascending: true, nullsFirst: true }).limit(MAX_PER_RUN);
  if (error) return json({ error: error.message }, 500);

  const due = (rows || []).filter((r) => isDue(r.last_sent_at, now, force));
  const ids = due.map((r) => r.user_id);
  const profiles: Record<string, unknown> = {};
  if (ids.length) {
    const { data: ps } = await db.from("user_profiles").select("id,data").in("id", ids);
    (ps || []).forEach((p: any) => { profiles[p.id] = p.data && p.data.rr_profile; });
  }

  const result = { considered: (rows || []).length, due: due.length, sent: 0, skipped: {} as Record<string, number>, failed: 0, dry };
  const skip = (why: string) => { result.skipped[why] = (result.skipped[why] || 0) + 1; };

  for (const r of due) {
    const consent = consentAllows(profiles[r.user_id]);
    if (!consent.ok) { skip(consent.reason || "sin_consentimiento"); continue; }
    if (!r.email) { skip("sin_email"); continue; }
    const unsubUrl = `${siteUrl.replace(/\/+$/, "")}/baja?token=${r.unsub_token}`;
    const mail = buildReminderEmail({ firstName: consent.firstName, digest: r.digest, unsubUrl, siteUrl, now });
    if (dry) { result.sent++; continue; }

    // Se "reserva" el envío antes de mandar: si dos ejecuciones coinciden, solo una gana.
    let claim = db.from("email_reminders").update({ last_sent_at: now.toISOString() }).eq("user_id", r.user_id);
    claim = r.last_sent_at ? claim.eq("last_sent_at", r.last_sent_at) : claim.is("last_sent_at", null);
    const { data: claimed } = await claim.select("user_id");
    if (!claimed || !claimed.length) { skip("ya_reservado"); continue; }

    try {
      const res = await fetch("https://api.resend.com/emails", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${apiKey}`,
          "Content-Type": "application/json",
          "Idempotency-Key": `recordatorio-${r.user_id}-${now.toISOString().slice(0, 10)}`,
        },
        body: JSON.stringify({
          from, to: [r.email], reply_to: replyTo, subject: mail.subject, html: mail.html, text: mail.text,
          headers: { "List-Unsubscribe": `<${unsubUrl}>` },
        }),
      });
      if (!res.ok) throw new Error(`Resend ${res.status}`);
      result.sent++;
    } catch (_e) {
      result.failed++;
      // Se devuelve la fecha anterior para que se reintente en la próxima ejecución.
      await db.from("email_reminders").update({ last_sent_at: r.last_sent_at }).eq("user_id", r.user_id);
    }
    await sleep(600); // Resend limita la velocidad de envío
  }
  return json(result);
});
