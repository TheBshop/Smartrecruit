// Piezas puras del recordatorio semanal (sin Deno ni red): se pueden probar con Node.

export function escapeHtml(s: unknown): string {
  return String(s ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#39;");
}
const clip = (s: unknown, n: number) => String(s ?? "").replace(/\s+/g, " ").trim().slice(0, n);

export type Digest = {
  stage?: string;
  monthsLeft?: number;
  next?: { title?: string; when?: string; required?: boolean } | null;
  week?: string;
  reqOpen?: number;
  updated?: string;
};

// Mismas reglas que consentIsValid() del sitio: acepta Términos y, si es menor, tiene la conformidad de un adulto.
export function consentAllows(rawProfile: unknown): { ok: boolean; reason?: string; firstName: string } {
  let p: any = null;
  try { p = typeof rawProfile === "string" ? JSON.parse(rawProfile) : rawProfile; } catch (_e) { p = null; }
  const firstName = clip(p && p.name, 40).split(" ")[0] || "";
  const c = p && p.consent;
  if (!c || !c.accepted || !c.ageAnswered) return { ok: false, reason: "sin_consentimiento", firstName };
  if (c.minor) {
    const parentOk = !!(c.parentOk && String(c.parentName || "").trim() && /.+@.+\..+/.test(String(c.parentEmail || "")));
    if (!parentOk) return { ok: false, reason: "menor_sin_adulto", firstName };
  }
  return { ok: true, firstName };
}

// Un recordatorio por semana: si ya se mandó hace menos de 6 días, no corresponde (así llamar dos veces a la función no duplica mails).
export function isDue(lastSentAt: string | null | undefined, now: Date, force = false): boolean {
  if (force || !lastSentAt) return true;
  const t = new Date(lastSentAt).getTime();
  if (Number.isNaN(t)) return true;
  return now.getTime() - t >= 6 * 86400000;
}

export function buildReminderEmail(opts: { firstName: string; digest: Digest | null | undefined; unsubUrl: string; siteUrl: string; now?: Date }) {
  const now = opts.now || new Date();
  const d: Digest = (opts.digest && typeof opts.digest === "object") ? opts.digest : {};
  const upd = d.updated ? new Date(d.updated).getTime() : NaN;
  const stale = Number.isNaN(upd) || now.getTime() - upd > 7 * 86400000;
  const stage = clip(d.stage, 40);
  const months = typeof d.monthsLeft === "number" && d.monthsLeft > 0 ? Math.round(d.monthsLeft) : null;
  const nextTitle = clip(d.next && d.next.title, 260);
  const nextWhen = clip(d.next && d.next.when, 60);
  const required = !!(d.next && d.next.required);
  const week = stale
    ? "Pasó una semana sin que entres a tu plan: un solo paso alcanza para retomar el ritmo."
    : clip(d.week, 300) || "Todavía no hiciste nada esta semana. Un solo paso alcanza para mantener la racha.";
  const hi = opts.firstName ? `Hola, ${clip(opts.firstName, 40)}.` : "Hola.";
  const stageLine = stage ? `Tu etapa: ${stage}${months ? ` (faltan unos ${months} ${months === 1 ? "mes" : "meses"} para tu ingreso)` : ""}.` : "";
  const planUrl = `${opts.siteUrl.replace(/\/+$/, "")}/plan`;
  const subject = "Tu semana en Smartrecruit";
  const nextLine = nextTitle ? `Tu próxima acción${required ? " (obligatoria)" : ""}: ${nextTitle}${nextWhen ? ` — ${nextWhen}` : ""}` : "Tu próxima acción te espera en tu plan.";

  const text = [
    hi, "", week, stageLine, "", nextLine, "", `Abrir mi plan: ${planUrl}`, "",
    "—",
    "Recibís este correo porque activaste el recordatorio semanal en Smartrecruit. Es uno por semana (domingos).",
    `Para darte de baja: ${opts.unsubUrl}`,
    "Smartrecruit es una herramienta educativa: no es un agente, no garantiza becas ni admisiones y no está afiliada a la NCAA, la NAIA, la NJCAA ni a ninguna universidad.",
  ].filter((x, i, a) => !(x === "" && a[i - 1] === "")).join("\n");

  const html = `<!doctype html><html lang="es"><body style="margin:0;background:#f4f1ea;font-family:Arial,Helvetica,sans-serif;color:#1a1f2e">
<div style="max-width:520px;margin:0 auto;padding:24px 16px">
<div style="background:#fff;border-radius:10px;padding:24px;border:1px solid #e3ded2">
<p style="margin:0 0 12px;font-size:16px">${escapeHtml(hi)}</p>
<p style="margin:0 0 12px;font-size:15px"><b>${escapeHtml(week)}</b></p>
${stageLine ? `<p style="margin:0 0 16px;font-size:14px;color:#555">${escapeHtml(stageLine)}</p>` : ""}
<div style="background:#f4f1ea;border-radius:8px;padding:14px;margin:0 0 18px">
<div style="font-size:12px;color:#666;text-transform:uppercase;letter-spacing:.04em;margin-bottom:6px">Tu próxima acción${required ? " · obligatoria" : ""}</div>
<div style="font-size:15px">${nextTitle ? escapeHtml(nextTitle) : "Te espera en tu plan."}</div>
${nextWhen ? `<div style="font-size:13px;color:#666;margin-top:6px">${escapeHtml(nextWhen)}</div>` : ""}
</div>
<a href="${escapeHtml(planUrl)}" style="display:inline-block;background:#14213d;color:#fff;text-decoration:none;padding:12px 18px;border-radius:8px;font-size:15px">Abrir mi plan</a>
</div>
<p style="font-size:12px;color:#777;margin:16px 4px 0">Recibís este correo porque activaste el recordatorio semanal en Smartrecruit. Es uno por semana (domingos). <a href="${escapeHtml(opts.unsubUrl)}" style="color:#777">Darme de baja</a>.</p>
<p style="font-size:12px;color:#777;margin:8px 4px 0">Smartrecruit es una herramienta educativa: no es un agente, no garantiza becas ni admisiones y no está afiliada a la NCAA, la NAIA, la NJCAA ni a ninguna universidad.</p>
</div></body></html>`;
  return { subject, text, html, planUrl };
}
