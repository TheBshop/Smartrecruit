// Build: copia los datos pesados (datos/*.json) a dist/data/ con hash en el nombre (cache inmutable) y empaqueta el código.
import { build } from "esbuild";
import fs from "fs";
import crypto from "crypto";
import { execSync } from "child_process";

fs.rmSync("dist", { recursive: true, force: true });
fs.mkdirSync("dist/data", { recursive: true });
execSync("cp -r public/. dist/");
const manifest = {}, manifestPriv = {}, totals = {};
// ---- Datos con mails de coaches y vacantes: el archivo completo vive en dist/priv/ (la función functions/priv exige sesión);
// en dist/data/ queda una versión de muestra: pocos registros completos y el resto enmascarado (iniciales, mail a***@dominio).
const GATED = ["COACH_CONTACTS_BY_PROGRAM", "ROSTER_COACH_CONTACTS", "FIELD_HOCKEY_HEAD_COACHES", "BBALL_D2_COACHES_FCP", "BBALL_D2_COACHES_WEB", "BBALL_D2_COACHES_2026", "BASKETBALL_WOMEN_COACHES", "STAFF_BY_PROGRAM", "RUGBY_WOMEN_PROGRAMS", "RUGBY_MEN_COACHES", "VOLLEYBALL_MEN_COACHES", "FIELDLEVEL_NEEDS", "OFFERS_BOARD"];
const SAMPLE = { COACH_CONTACTS_BY_PROGRAM: 3, ROSTER_COACH_CONTACTS: 4, BBALL_D2_COACHES_FCP: 2, BBALL_D2_COACHES_WEB: 2, BBALL_D2_COACHES_2026: 2, BASKETBALL_WOMEN_COACHES: 2, STAFF_BY_PROGRAM: 3, RUGBY_WOMEN_PROGRAMS: 2, RUGBY_MEN_COACHES: 1, VOLLEYBALL_MEN_COACHES: 2 };
const maskEmail = (e) => e.replace(/([A-Za-z0-9._%+-])[A-Za-z0-9._%+-]*@([A-Za-z0-9.-]+\.[A-Za-z]{2,})/g, "$1***@$2");
const initials = (n) => String(n).split(/\s+/).filter(Boolean).map((w) => w[0].toUpperCase() + ".").join(" ");
function maskEntry(v) {
  if (typeof v === "string") return initials(v);
  let hit = false;
  const walk = (x, k) => {
    if (Array.isArray(x)) return x.map((y) => walk(y, k));
    if (x && typeof x === "object") { const o = {}; for (const [kk, vv] of Object.entries(x)) { if (["phone", "profileUrl", "note"].includes(kk)) { hit = true; continue; } const r = walk(vv, kk); if (r !== undefined) o[kk] = r; } return o; }
    if (typeof x !== "string") return x;
    if (/^(name|Coach|coach|coachName)$/.test(k || "")) { hit = true; return initials(x); }
    if (k === "label") { hit = true; return "Contacto disponible con tu cuenta"; }
    if (/@/.test(x)) { hit = true; return maskEmail(x); }
    return x;
  };
  const out = walk(v);
  if (out && typeof out === "object" && !Array.isArray(out) && hit) out.locked = true;
  return out;
}
const hasEmail = (v) => /@/.test(JSON.stringify(v));
function previewOf(name, data) {
  if (name === "FIELDLEVEL_NEEDS") { const by = {}; return data.filter((r) => r.source === "fieldlevel").sort((a, b) => (a.hours_since_posted ?? 1e9) - (b.hours_since_posted ?? 1e9)).filter((r) => (by[r.sport] = (by[r.sport] || 0) + 1) <= 4); }
  if (name === "OFFERS_BOARD") { const by = {}; return data.filter((o) => (by[o[0]] = (by[o[0]] || 0) + 1) <= 4); }
  const K = SAMPLE[name] || 0;
  if (Array.isArray(data)) { let n = 0; const free = new Set(); for (let i = data.length - 1; i >= 0 && n < K; i--) if (hasEmail(data[i])) { free.add(i); n++; } return data.map((v, i) => (free.has(i) ? v : maskEntry(v))); }
  const by = {}, out = {};
  for (const [k, v] of Object.entries(data)) {
    const g = name === "COACH_CONTACTS_BY_PROGRAM" ? k.split("|").slice(-2).join("|") : "x";
    const free = typeof v === "object" && hasEmail(v) && (by[g] = (by[g] || 0) + 1) <= K;
    out[k] = free ? v : maskEntry(v);
  }
  return out;
}
for (const f of fs.readdirSync("datos").filter((x) => x.endsWith(".json") && !x.startsWith("_"))) {
  const name = f.replace(/\.json$/, "");
  const buf = fs.readFileSync(`datos/${f}`);
  const hash = crypto.createHash("sha1").update(buf).digest("hex").slice(0, 10);
  const out = `${name}.${hash}.json`;
  if (GATED.includes(name)) {
    const data = JSON.parse(buf.toString("utf8"));
    fs.mkdirSync("dist/priv", { recursive: true });
    fs.writeFileSync(`dist/priv/${out}`, buf);
    manifestPriv[name] = out;
    fs.writeFileSync(`dist/data/${out}`, JSON.stringify(previewOf(name, data)));
    if (name === "FIELDLEVEL_NEEDS") totals.needs = data.length;
    if (name === "OFFERS_BOARD") totals.offers = data.length;
    if (name === "COACH_CONTACTS_BY_PROGRAM") totals.contacts = Object.values(data).filter((v) => v && v.email).length;
  } else fs.writeFileSync(`dist/data/${out}`, buf);
  manifest[name] = out;
}
for (const g of GATED) if (!manifestPriv[g]) throw new Error("falta dataset gated " + g);
await build({
  entryPoints: ["main.jsx"],
  bundle: true,
  minify: true,
  format: "iife",
  jsx: "automatic",
  outfile: "dist/assets/index.js",
  define: { "process.env.NODE_ENV": '"production"', DATA_MANIFEST: JSON.stringify(manifest), DATA_MANIFEST_PRIV: JSON.stringify(manifestPriv), DATA_TOTALS: JSON.stringify(totals) },
});
const V = Date.now().toString(36);
for (const f of ["dist/index.html", "dist/privacidad/index.html", "dist/terminos/index.html"]) {
  fs.writeFileSync(f, fs.readFileSync(f, "utf8").replace(/\?v=[0-9a-z]*/g, `?v=${V}`));
}
// Precarga en paralelo con el JS los datos públicos que loadData pide siempre (los gated se piden con token, no se precargan).
{
  const src = fs.readFileSync("RosterReal.jsx", "utf8");
  const m = src.match(/const names = \[([^\]]+)\]/);
  const wanted = m ? m[1].match(/"([A-Z0-9_]+)"/g).map((x) => x.replace(/"/g, "")) : [];
  const links = wanted.filter((n) => manifest[n] && !GATED.includes(n)).map((n) => `    <link rel="preload" as="fetch" crossorigin="anonymous" href="/data/${manifest[n]}" />`).join("\n");
  const f = "dist/index.html";
  fs.writeFileSync(f, fs.readFileSync(f, "utf8").replace('<script defer src="/assets/analytics.js', links + '\n    <script defer src="/assets/analytics.js'));
  console.log("precarga:", wanted.filter((n) => manifest[n] && !GATED.includes(n)).length);
}
await import("./scripts/gen_schools.mjs");
console.log("ok", Object.keys(manifest).length, "archivos de datos");
