// Importa rosters D1 de básquet masculino 2026-27 (ESPN, hometown/país/altura) a BBALL_ROSTERS.
// Uso: node datos-src/importar_espn_mbb.mjs <carpeta con c0..c7.txt> [--dry]
// Formato de línea: "#Equipo Mascota" luego "Nombre|Pos|Clase|Ciudad|País|Altura".
import fs from "fs";
const dir = process.argv[2]; const DRY = process.argv.includes("--dry");
const rd = (n) => JSON.parse(fs.readFileSync(`datos/${n}.json`, "utf8"));
const P = rd("PROGRAMS_ALL_SPORTS");
const cat = [...new Set(P.filter((p) => p.sport === "Basketball" && p.Gender === "M" && p.Division === "NCAA D1").map((p) => p.School))];
const strip = (s) => String(s).normalize("NFKD").replace(/[̀-ͯ]/g, "").toLowerCase().replace(/&/g, " and ").replace(/[–—-]/g, " ").replace(/\bst\.?(?=\s|$)/g, "state").replace(/[^a-z0-9 ]/g, " ").replace(/\b(the|of|at|university|college|and)\b/g, " ").replace(/\s+/g, " ").trim();
const idx = {}; cat.forEach((c) => { (idx[strip(c)] = idx[strip(c)] || []).push(c); });
const ALIAS = JSON.parse(fs.readFileSync("datos-src/espn_mbb_alias.json", "utf8"));
const resolve = (team) => {
  if (ALIAS[team]) return ALIAS[team];
  const w = team.split(" ");
  for (let n = w.length - 1; n >= 1; n--) {
    const k = strip(w.slice(0, n).join(" "));
    if (idx[k]?.length === 1) return idx[k][0];
  }
  return null;
};
const teams = {};
for (let i = 0; i < 8; i++) {
  let cur = null;
  for (const ln of fs.readFileSync(`${dir}/c${i}.txt`, "utf8").split("\n")) {
    if (!ln.trim()) continue;
    if (ln[0] === "#") { cur = ln.slice(1).trim(); teams[cur] = []; continue; }
    const [name, pos, cls, home, country, ht] = ln.split("|");
    teams[cur].push({ name, pos, cls, home, country, ht });
  }
}
const old = rd("BBALL_ROSTERS");
const nk = (s) => String(s || "").normalize("NFKD").replace(/[̀-ͯ]/g, "").toLowerCase().replace(/[^a-z]/g, "");
const normCls = (c) => { c = String(c || "").trim(); const r = /^R-?/i.test(c) ? "R-" : ""; const b = c.replace(/^R-?/i, "").toLowerCase(); const m = { fr: "Fr", so: "So", jr: "Jr", sr: "Sr", gr: "Gr" }[b.slice(0, 2)]; return m ? r + m : ""; };
const normPos = (p) => { p = String(p || "").toUpperCase(); if (/^(PG|SG|G)$/.test(p)) return "G"; if (/^(SF|PF|F)$/.test(p)) return "F"; if (p === "C") return "C"; return ""; };
const out = {}; const unresolved = []; let nNew = 0, nKept = 0, players = 0;
for (const [team, pl] of Object.entries(teams)) {
  const school = resolve(team);
  if (!school) { unresolved.push(team); continue; }
  if (out[school]) continue;
  const prev = new Map((old[school] || (school === "University of North Carolina – Wilmington" ? old["Wilmington University"] : null) || []).map((p) => [nk(p.player_name), p]));
  const hadStats = prev.size > 0;
  out[school] = pl.map((p) => {
    const o = prev.get(nk(p.name));
    const r = { player_name: p.name, position: normPos(p.pos) || (o && o.position) || "", class_year: normCls(p.cls) || (o && o.class_year) || "", country: p.country || (p.home && /, [A-Z]{2}$/.test(p.home) ? "USA" : ""), hometown: p.home || "", height: p.ht || "" };
    if (o) { r.ppg = o.ppg; r.rpg = o.rpg; r.apg = o.apg; nKept++; } else if (hadStats) { r.ppg = 0; r.rpg = 0; r.apg = 0; }
    players++; return r;
  });
  if (!hadStats) nNew++;
}
// equipos que ya estaban y ESPN no devolvió: se conservan, con país "USA" falso vaciado
for (const [s, pl] of Object.entries(old)) if (!out[s] && cat.includes(s)) out[s] = pl.map((p) => ({ ...p, country: p.country === "USA" ? "" : p.country }));
console.log({ espnTeams: Object.keys(teams).length, resolved: Object.keys(teams).length - unresolved.length, nuevosEquipos: nNew, jugadores: players, conservaStats: nKept, total: Object.keys(out).length });
console.log("SIN RESOLVER:", unresolved);
const miss = cat.filter((c) => !out[c]); console.log("Catálogo D1 sin roster:", miss.length, miss.slice(0, 40));
if (!DRY) fs.writeFileSync("datos/BBALL_ROSTERS.json", JSON.stringify(out));
