// Limpieza repetible del catálogo. Uso: node datos-src/limpiar_datos.mjs [--dry]
// Ejecutar desde la raíz del proyecto. Es idempotente.
import fs from "fs";
const DRY = process.argv.includes("--dry");
const rd = (n) => JSON.parse(fs.readFileSync(`datos/${n}.json`, "utf8"));
const wr = (n, o) => { if (!DRY) fs.writeFileSync(`datos/${n}.json`, JSON.stringify(o)); };
const log = [];

// ---------- A. Nombres duplicados / renombrados ----------
// [viejo, nuevo] — la institución cambió de nombre; el catálogo tenía las dos formas.
const RENAMES = [
  ["Mercy College", "Mercy University"],
  ["Nazareth College", "Nazareth University"],
  ["Canisius College", "Canisius University"],
  ["Manhattan College", "Manhattan University"],
];
const R = Object.fromEntries(RENAMES);
const rn = (s) => R[s] || s;

const P = rd("PROGRAMS_ALL_SPORTS");
let nren = 0;
P.forEach((p) => { if (R[p.School]) { p.School = R[p.School]; nren++; } });
log.push(`A. programas renombrados: ${nren}`);
// quitar filas duplicadas exactas escuela+deporte+género
{
  const seen = new Set(); let dup = 0;
  for (let i = P.length - 1; i >= 0; i--) { const k = [P[i].School, P[i].sport, P[i].Gender].join("|"); if (seen.has(k)) { P.splice(i, 1); dup++; } else seen.add(k); }
  log.push(`A. filas duplicadas quitadas: ${dup}`);
}
for (const f of ["BBALL_D2_ROSTERS", "BBALL_ROSTERS", "MAJOR_DATA_BY_SCHOOL", "SCHOOL_PROFILES_NCSA"]) {
  const o = rd(f); let c = 0;
  for (const [a, b] of RENAMES) if (a in o) { if (!(b in o)) o[b] = o[a]; delete o[a]; c++; }
  log.push(`A. ${f}: ${c} claves unificadas`); wr(f, o);
}

// ---------- B. Conferencias ----------
const N = rd("SCHOOL_PROFILES_NCSA");
const junk = (c) => !c || /football|independen|^other$|^division 3$|member of|associate member|\(division|, |\bNJCAA, Region|cheerleading|^NAIA –|^CCCAA/i.test(c);
const clean = (c) => String(c || "").replace(/\s*\((?:[^)]*Football|UCA Cheerleading|Independent|South Coast Wrestling)\)/gi, "").replace(/Conferenc$/, "Conference").replace(/\s+/g, " ").trim();
const by = {}; P.forEach((p) => { (by[p.School] = by[p.School] || []).push(p); });
// Casos donde no hay dato limpio en el propio catálogo (verificados a mano contra los sitios deportivos).
const CONF_OVERRIDE = {
  "Cuesta College": "Western State Conference",
  "Los Angeles Valley College": "Western State Conference",
  "Barstow Community College": "Inland Empire Athletic Conference",
  "Castleton University": "Little East Conference",
  "Culinary Institute of America": "Hudson Valley Intercollegiate Athletic Conference",
  "St. Joseph's College – Long Island": "Skyline Conference",
  "University of Houston – Downtown": "Independent",
  "Clinton Community College": "Independent",
  "Trinity Washington University": "Independent",
  "Manhattan Christian College": "National Christian College Athletic Association",
};
let nconf = 0; const confLog = [];
for (const p of P) {
  if (p.sport === "Rugby") continue;
  const orig = p.Conference;
  let c = clean(orig);
  if (CONF_OVERRIDE[p.School] && (junk(c) || c === "CCCAA")) c = CONF_OVERRIDE[p.School];
  else if (junk(c)) {
    const m = {}; (by[p.School] || []).forEach((q) => { if (q !== p && q.sport !== "Rugby") { const qc = clean(q.Conference); if (!junk(qc)) m[qc] = (m[qc] || 0) + 1; } });
    const top = Object.entries(m).sort((a, b) => b[1] - a[1])[0];
    const nc = clean(N[p.School] && N[p.School].conference);
    if (top && (top[1] >= 2 || junk(nc))) c = top[0];
    else if (nc && !junk(nc)) c = nc;
    else if (top) c = top[0];
    else c = "Independent";
  }
  if (c !== orig) { p.Conference = c; nconf++; if (confLog.length < 400) confLog.push(`${p.School} [${p.sport}/${p.Gender}]: ${String(orig).slice(0, 50)} -> ${c}`); }
}
log.push(`B. conferencias corregidas: ${nconf}`);
wr("PROGRAMS_ALL_SPORTS", P);
if (process.argv.includes("--verbose")) console.log(confLog.join("\n"));

// ---------- C. Enlazar nombres de otras fuentes con el catálogo ----------
const cat = [...new Set(P.map((p) => p.School))]; const catSet = new Set(cat);
const info = {}; P.forEach((p) => { const o = info[p.School] = info[p.School] || { div: new Set(), st: new Set() }; o.div.add(p.Division); if (p.State) o.st.add(p.State); });
const stop = /\b(the|of|at|university|college|and)\b/g;
const base = (s) => String(s).normalize("NFKD").replace(/[̀-ͯ]/g, "").toLowerCase().replace(/&/g, " and ").replace(/[–—]/g, " ").replace(/\(([a-z]+)\)/g, " $1 ");
const nzCat = (s) => base(s).replace(/\bst\.(?=\s|$)/g, "saint").replace(/[^a-z0-9 ]/g, " ").replace(stop, " ").replace(/\s+/g, " ").trim();
const nzExt = (s) => base(s).replace(/^st\.\s/, "saint ").replace(/\bst\.(?=\s|-|$)/g, " state").replace(/\bst\b(?=$)/g, " state").replace(/[^a-z0-9 ]/g, " ").replace(stop, " ").replace(/\s+/g, " ").trim();
const idx = {}; cat.forEach((c) => { (idx[nzCat(c)] = idx[nzCat(c)] || []).push(c); });
const ST = { AL: "Alabama", AK: "Alaska", AZ: "Arizona", AR: "Arkansas", CA: "California", CO: "Colorado", CT: "Connecticut", DE: "Delaware", DC: "District Of Columbia", FL: "Florida", GA: "Georgia", HI: "Hawaii", ID: "Idaho", IL: "Illinois", IN: "Indiana", IA: "Iowa", KS: "Kansas", KY: "Kentucky", LA: "Louisiana", ME: "Maine", MD: "Maryland", MA: "Massachusetts", MI: "Michigan", MN: "Minnesota", MS: "Mississippi", MO: "Missouri", MT: "Montana", NE: "Nebraska", NV: "Nevada", NH: "New Hampshire", NJ: "New Jersey", NM: "New Mexico", NY: "New York", NC: "North Carolina", ND: "North Dakota", OH: "Ohio", OK: "Oklahoma", OR: "Oregon", PA: "Pennsylvania", RI: "Rhode Island", SC: "South Carolina", SD: "South Dakota", TN: "Tennessee", TX: "Texas", UT: "Utah", VT: "Vermont", VA: "Virginia", WA: "Washington", WV: "West Virginia", WI: "Wisconsin", WY: "Wyoming" };
const placeState = (pl) => { const m = /,\s*([A-Z]{2})\s*$/.exec(pl || ""); return m ? ST[m[1]] : null; };
// resuelve un nombre a un nombre del catálogo; exige coincidencia de estado/división cuando se conocen
const MANUAL = { "Mercy College": "Mercy University", "Nazareth College": "Nazareth University", "Canisius College": "Canisius University", "Manhattan College": "Manhattan University" };
function resolve(name, { state, division } = {}) {
  name = MANUAL[name] || name;
  if (catSet.has(name)) return name;
  let c = idx[nzExt(name)] || [];
  if (state) c = c.filter((x) => info[x].st.has(state));
  if (division) { const f = c.filter((x) => [...info[x].div].some((d) => d.startsWith(division))); if (f.length || c.length > 1) c = f; }
  return c.length === 1 ? c[0] : null;
}
const keyedObj = (o, fn, label) => {
  const out = {}; let ch = 0, drop = 0;
  for (const [k, v] of Object.entries(o)) { const nk = fn(k, v) || k; if (nk !== k) ch++; if (nk in out) { drop++; continue; } out[nk] = v; }
  log.push(`C. ${label}: ${ch} claves reenlazadas, ${drop} colisiones descartadas`); return out;
};
// WBB: alias manuales verificados (nombre corto de la fuente -> nombre del catálogo)
const WBB_ALIAS = {
  "Colorado": "University of Colorado – Boulder", "Texas": "University of Texas – Austin", "Georgia College": "Georgia College & State University",
  "Albany": "SUNY University at Albany", "Austin Peay": "Austin Peay State University", "Bowling Green": "Bowling Green State University",
  "Central (IA)": "Central College", "Central Connecticut": "Central Connecticut State University", "Florida St": "Florida State University",
  "Grambling": "Grambling State University", "LaSalle": "La Salle University", "Minnesota St.": "Minnesota State University – Mankato",
  "Middle Tennessee": "Middle Tennessee State University", "Missouri-St. Louis": "University of Missouri – St. Louis",
  "Mount St. Mary's": "Mount St. Mary's University", "North Carolina": "University of North Carolina at Chapel Hill",
  "Northwestern State": "Northwestern State University of Louisiana", "Stephen F. Austin": "Stephen F Austin State University",
  "Winston-Salem": "Winston-Salem State University", "Mount St. Joseph": "Mount St. Joseph University", "Missouri Western": "Missouri Western State University",
  "Northwestern-St. Paul": "University of Northwestern – St. Paul", "Penn College": "Pennsylvania College of Technology",
  "Boston": "Boston University", "Miami": "University of Miami", "Ozarks": "University of the Ozarks", "Murray State": "Murray State University",
  "Le Moyne": "Le Moyne College", "Mercyhurst": "Mercyhurst University", "Canisius": "Canisius University", "Manhattan": "Manhattan University", "Mercy": "Mercy University", "Nazareth": "Nazareth University",
};
const W0 = rd("WBB_ROSTERS_2026_27"), E0 = rd("WBB_ESPN_STATS_2025_26");
const wbbName = (k, div) => { if (WBB_ALIAS[k] && catSet.has(WBB_ALIAS[k])) return WBB_ALIAS[k]; if (WBB_ALIAS[k] && catSet.has(WBB_ALIAS[k])) return WBB_ALIAS[k]; if (catSet.has(k)) return k; const c = idx[nzExt(k)] || []; const f = c.filter((x) => [...info[x].div].some((d) => d.startsWith(div || ""))); return f.length === 1 ? f[0] : null; };
const W1 = keyedObj(W0, (k, v) => wbbName(k, v.division), "WBB_ROSTERS");
const E1 = keyedObj(E0, (k) => wbbName(k, "NCAA D1") || (idx[nzExt(k)] || []).length === 1 && idx[nzExt(k)][0], "WBB_ESPN");
Object.entries(W1).forEach(([k, v]) => { if (k !== v.school) { /* campo school lo arma la app */ } });
wr("WBB_ROSTERS_2026_27", W1); wr("WBB_ESPN_STATS_2025_26", E1);
{
  const FL = rd("FIELDLEVEL_NEEDS"); let c = 0;
  FL.forEach((r) => { const n = resolve(r.university, { state: placeState(r.place) }); if (n && n !== r.university) { r.university = n; c++; } });
  log.push(`C. FIELDLEVEL_NEEDS: ${c} nombres enlazados`); wr("FIELDLEVEL_NEEDS", FL);
  const RN = rd("RECRUITING_NEEDS_GENERAL"); c = 0;
  RN.forEach((r) => { const n = resolve(r.school, { state: placeState(r.place) }); if (n && n !== r.school) { r.school = n; c++; } });
  log.push(`C. RECRUITING_NEEDS_GENERAL: ${c}`); wr("RECRUITING_NEEDS_GENERAL", RN);
  const OB = rd("OFFERS_BOARD"); c = 0;
  OB.forEach((r) => { const n = resolve(r[2], { state: placeState(r[6]) }); if (n && n !== r[2]) { r[2] = n; c++; } });
  log.push(`C. OFFERS_BOARD: ${c}`); wr("OFFERS_BOARD", OB);
}


// ---------- D. Jugadores: nombres, clase y posición ----------
const stripAcc = (t) => String(t).normalize("NFKD").replace(/[̀-ͯ]/g, "").toLowerCase().replace(/[^a-z]/g, "");
// "Adriana 0Durango, Adriana Durango" -> "Adriana Durango" (el número de camiseta se había pegado al apellido)
export function cleanPlayerName(n) {
  n = String(n);
  if (!/\d/.test(n)) return n;
  const parts = n.split(/\s*,\s*/);
  if (parts.length === 2 && stripAcc(parts[0]) === stripAcc(parts[1])) return parts[1].trim();
  return n.replace(/\s*\b\d{1,3}(?=[A-Za-zÀ-ÿ])/g, " ").replace(/\s+/g, " ").trim();
}
export function normClass(c) {
  if (c == null) return c;
  let t = String(c).toLowerCase().replace(/\([^)]*\)/g, " ").replace(/[*.]/g, " ").replace(/-/g, " ").replace(/\s+/g, " ").trim();
  if (!t || /^(tbd|redshirt|rs|\d|5 8)$/.test(t)) return "";
  const rs = /\bred ?shirt\b|^r ?(fr|so|jr|sr)\b|\brs\b/.test(t);
  let g = null;
  if (/\b(gr|grad|graduate|fifth|5th|sixth|6th|seventh|7th)\b|^red 5th|5th\+?/.test(t)) g = "Gr";
  else if (/\b(sr|senior|4th|fourth)\b/.test(t)) g = "Sr";
  else if (/\b(jr|junior|3rd|third)\b/.test(t)) g = "Jr";
  else if (/\b(so|soph|sophomore|2nd|second)\b/.test(t)) g = "So";
  else if (/\b(fr|fresh|freshman|1st|first|fy)\b/.test(t)) g = "Fr";
  if (!g) return String(c);
  return (rs && g !== "Gr" ? "R-" : "") + g;
}
const POS_TOK = { G: "G", PG: "G", SG: "G", CG: "G", WG: "G", GUARD: "G", "POINT GUARD": "G", F: "F", SF: "F", PF: "F", FW: "F", FORWARD: "F", C: "C", CENTER: "C", POST: "C", P: "C" };
export function normBasketPos(p) {
  if (p == null) return p; const t = String(p).trim(); if (!t) return "";
  const out = []; t.split(/\s*[\/,]\s*/).forEach((x) => { const m = POS_TOK[x.toUpperCase()]; if (m && !out.includes(m)) out.push(m); });
  return out.join("/");
}
let nName = 0, nCls = 0, nPos = 0;
{ // soccer: claves de bio y primera columna de stats
  for (const f of ["SOCCER_BIO_2026", "SOCCER_D2F_BIO_2026", "SOCCER_D2M_BIO_2026"]) {
    const o = rd(f);
    for (const g of Object.keys(o)) for (const sc of Object.keys(o[g])) {
      const nb = {};
      for (const [pn, arr] of Object.entries(o[g][sc])) {
        const cn = cleanPlayerName(pn); if (cn !== pn) nName++;
        if (Array.isArray(arr)) { const c2 = normClass(arr[1]); if (c2 !== arr[1]) { arr[1] = c2; nCls++; } if (arr[0] === "def") { arr[0] = "D"; nPos++; } }
        let k = cn; while (k in nb) k += " "; nb[k] = arr; // colisión de nombres: se conservan ambos
      }
      o[g][sc] = nb;
    }
    wr(f, o);
  }
  for (const f of ["SOCCER_PARTIAL_STATS_2026", "SOCCER_D2F_STATS_2026", "SOCCER_D2M_STATS_2026"]) {
    const o = rd(f);
    for (const g of Object.keys(o)) for (const sc of Object.keys(o[g])) o[g][sc].forEach((r) => { const cn = cleanPlayerName(r[0]); if (cn !== r[0]) { r[0] = cn; nName++; } });
    wr(f, o);
  }
}
{ // básquet femenino (UMD)
  const o = rd("WBB_ROSTERS_2026_27");
  for (const v of Object.values(o)) v.rows.forEach((r) => { const c2 = normClass(r[2]); if (c2 !== r[2]) { r[2] = c2; nCls++; } const p2 = normBasketPos(r[1]); if (p2 !== r[1]) { r[1] = p2; nPos++; } });
  wr("WBB_ROSTERS_2026_27", o);
}
{ // básquet masculino D2 y D1
  const o = rd("BBALL_D2_ROSTERS");
  for (const [, arr] of Object.entries(o)) arr[1].forEach((r) => { const c2 = normClass(r[2]); if (c2 !== r[2]) { r[2] = c2; nCls++; } });
  wr("BBALL_D2_ROSTERS", o);
  const b = rd("BBALL_ROSTERS");
  for (const arr of Object.values(b)) arr.forEach((p) => { const c2 = normClass(p.class_year); if (c2 !== p.class_year) { p.class_year = c2; nCls++; } });
  wr("BBALL_ROSTERS", b);
}
log.push(`D. nombres limpiados: ${nName}, clases normalizadas: ${nCls}, posiciones corregidas: ${nPos}`);


// ---------- E. Ciudad/estado: una sola forma por institución y sin vacíos ----------
const RUGBY_ONLY_PLACE = {
  "University of California": ["Berkeley", "California"], "St. Thomas University": ["Miami Gardens", "Florida"], "St. Thomas University (D2)": ["Miami Gardens", "Florida"],
  "California Polytechnic State University": ["San Luis Obispo", "California"], "Millenia Atlantic University": ["Orlando", "Florida"],
  "Claremont Colleges": ["Claremont", "California"], "California State Polytechnic University, Humboldt": ["Arcata", "California"],
  "California Polytechnic State University Maritime Academy": ["Vallejo", "California"],
};
{
  const by2 = {}; P.forEach((p) => { (by2[p.School] = by2[p.School] || []).push(p); });
  let nfix = 0;
  const top = (arr) => { const m = {}; arr.forEach((v) => { m[v] = (m[v] || 0) + 1; }); return Object.entries(m).sort((a, b) => b[1] - a[1])[0]?.[0]; };
  for (const [sc, a] of Object.entries(by2)) {
    const core = a.filter((p) => p.sport !== "Rugby");
    let city = top(core.map((p) => p.City).filter(Boolean)) || top(a.map((p) => p.City).filter(Boolean));
    let st = top(core.map((p) => p.State).filter(Boolean)) || top(a.map((p) => p.State).filter(Boolean));
    if ((!city || !st) && RUGBY_ONLY_PLACE[sc]) { city = city || RUGBY_ONLY_PLACE[sc][0]; st = st || RUGBY_ONLY_PLACE[sc][1]; }
    a.forEach((p) => {
      const isRugby = p.sport === "Rugby";
      if (city && (!p.City || (!isRugby && p.City !== city))) { p.City = city; nfix++; }
      if (st && (!p.State || (!isRugby && p.State !== st))) { p.State = st; nfix++; }
    });
  }
  let nconf2 = 0;
  for (const a of Object.values(by2)) {
    const cf = top(a.filter((p) => p.sport !== "Rugby" && p.Conference).map((p) => p.Conference));
    if (cf) a.forEach((p) => { if (!p.Conference) { p.Conference = cf; nconf2++; } });
  }
  log.push(`E. conferencias vacías completadas: ${nconf2}`);
  log.push(`E. ciudad/estado corregidos: ${nfix}`);
  wr("PROGRAMS_ALL_SPORTS", P);
}

console.log(log.join("\n"));
