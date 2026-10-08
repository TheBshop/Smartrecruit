// Smartrecruit · Generador de mails con IA (Netlify Function).
// La clave vive en la variable de entorno ANTHROPIC_API_KEY: nunca llega al navegador.
const MODEL = process.env.ANTHROPIC_MODEL || "claude-sonnet-5-5";
const ALLOWED = [/^https:\/\/(www\.)?smartrecruit\.com\.ar$/, /^https:\/\/[a-z0-9-]+--smartrecruitt\.netlify\.app$/, /^https:\/\/smartrecruitt\.netlify\.app$/, /^https:\/\/([a-z0-9-]+--)?heroic-panda-48f5a9\.netlify\.app$/, /^http:\/\/localhost(:\d+)?$/];
const KINDS = {
  intro: "first contact / introduction",
  update: "season or video update to a coach already contacted",
  follow_up: "polite follow-up after no reply (about 10-14 days later)",
  reply: "reply to a message the coach sent",
};
const TONES = {
  profesional: "professional, direct and warm",
  cercano: "friendly and enthusiastic, still respectful",
  breve: "very brief: at most 90 words in the body",
};

const SYSTEM = `You write emails from high-school student-athletes (mostly from Argentina and Latin America) to US college coaches.
Rules:
- Write in the requested language, in first person as the athlete.
- Tone: as requested. Short sentences, easy to scan on a phone. Body: 120-180 words unless told otherwise.
- Structure: who I am (position, graduation year, country, club) → why THIS program (use only the program facts given) → key numbers (only those given) → highlight video link if given → one concrete closing question.
- Use ONLY facts present in the input. Never invent stats, honors, GPA, height, rankings or program facts. If a fact is missing, leave it out. Keep any link exactly as given.
- No flattery clichés, no emojis, no markdown.
- Subject line format: "Class of {year} {position} | {Full Name} | {one key fact} + Highlights" (drop parts you don't have).
- Output ONLY valid JSON, no extra text: {"subject": "...", "body": "..."}`;

const json = (obj, status = 200, origin = "*") => new Response(JSON.stringify(obj), {
  status, headers: { "content-type": "application/json", "access-control-allow-origin": origin, "vary": "origin" } });

// Acepta JSON (aunque venga con texto alrededor o saltos de línea sin escapar) o el formato "Subject: ...".
function parseDraft(text) {
  const m = text.match(/\{[\s\S]*\}/);
  if (m) {
    try { const o = JSON.parse(m[0]); if (o.subject && o.body) return { subject: String(o.subject), body: String(o.body) }; } catch {}
    try { const o = JSON.parse(m[0].replace(/\r?\n/g, "\\n")); if (o.subject && o.body) return { subject: String(o.subject), body: String(o.body) }; } catch {}
    const r = m[0].match(/"subject"\s*:\s*"([\s\S]*?)"\s*,\s*"body"\s*:\s*"([\s\S]*)"\s*\}\s*$/);
    if (r) { const un = (x) => x.replace(/\\n/g, "\n").replace(/\\"/g, '"'); return { subject: un(r[1]), body: un(r[2]) }; }
  }
  const s = text.match(/^\s*(?:Subject|Asunto)\s*:\s*(.+)\n+([\s\S]+)$/i);
  if (s) return { subject: s[1].trim(), body: s[2].trim() };
  return null;
}

export default async (req) => {
  const origin = req.headers.get("origin") || "";
  const okOrigin = ALLOWED.some((re) => re.test(origin));
  if (req.method === "OPTIONS") return new Response(null, { status: 204, headers: {
    "access-control-allow-origin": okOrigin ? origin : "null", "access-control-allow-methods": "POST", "access-control-allow-headers": "content-type" } });
  if (req.method !== "POST") return json({ error: "method" }, 405);
  if (!okOrigin) return json({ error: "origin" }, 403);
  if (!process.env.ANTHROPIC_API_KEY) return json({ error: "La clave de la API no está configurada en Netlify." }, 500, origin);

  let input;
  try { input = await req.json(); } catch { return json({ error: "json" }, 400, origin); }
  const raw = JSON.stringify(input || {});
  if (raw.length > 12000) return json({ error: "too_large" }, 413, origin);

  const lang = input.lang === "es" ? "Spanish (Argentina, using 'usted' with the coach)" : "English (US)";
  const kind = KINDS[input.kind] || KINDS.intro;
  const tone = TONES[input.tone] || TONES.profesional;
  const user = `Email type: ${kind}
Language: ${lang}
Tone: ${tone}
${input.coachMessage ? `Coach's message to reply to:\n${String(input.coachMessage).slice(0, 2000)}\n` : ""}
Athlete profile (JSON): ${JSON.stringify(input.profile || {})}
Program (JSON): ${JSON.stringify(input.program || {})}
Verified facts draft (reuse its facts; you may restructure and shorten it):
${String(input.baseDraft || "").slice(0, 4000)}`;

  try {
    const r = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: { "content-type": "application/json", "x-api-key": process.env.ANTHROPIC_API_KEY, "anthropic-version": "2023-06-01" },
      body: JSON.stringify({ model: MODEL, max_tokens: 900, system: SYSTEM, messages: [{ role: "user", content: user }] }),
    });
    const data = await r.json();
    if (!r.ok) return json({ error: data?.error?.message || "api_error" }, 502, origin);
    const text = (data.content || []).filter((b) => b.type === "text").map((b) => b.text).join("").replace(/```json|```/g, "").trim();
    const out = parseDraft(text);
    if (!out) return json({ error: "La IA respondió en un formato inesperado. Probá de nuevo.", detail: text.slice(0, 300) }, 502, origin);
    return json({ subject: out.subject.slice(0, 200), body: out.body.slice(0, 4000), model: MODEL }, 200, origin);
  } catch (e) {
    return json({ error: "No se pudo generar el mail. Probá de nuevo.", detail: String(e && e.message || e).slice(0, 300) }, 502, origin);
  }
};

export const config = { path: "/api/generate-email" };
