// Carga planteles de fútbol masculino D2 (sin estadísticas) en datos/SOCCER_D2M_BIO_2026.json (clave "M").
// La app arma los equipos que están en BIO pero no en STATS como plantel sin estadísticas.
// Uso: node datos-src/cargar_plantel_pegado.mjs <archivo.txt> [--dry]
// Formato del .txt: ver datos-src/planteles_pegados/futbol_d2m_2026.txt. Repetible: reemplaza el plantel de la escuela.
import fs from "fs";
const [file] = process.argv.slice(2).filter((a) => !a.startsWith("--"));
const dry = process.argv.includes("--dry");
if (!file) { console.error("Falta el archivo de entrada"); process.exit(1); }

const US = new Set(("alabama alaska arizona arkansas california colorado connecticut delaware florida georgia hawaii idaho illinois indiana iowa kansas kentucky louisiana maine maryland massachusetts michigan minnesota mississippi missouri montana nebraska nevada ohio oklahoma oregon pennsylvania tennessee texas utah vermont virginia washington wisconsin wyoming " +
  "ala alaska ariz ark calif colo conn del fla ga hawaii idaho ill ind iowa kan ky la me md mass mich minn miss mo mont neb nev nh nj nm ny nc nd ohio okla ore pa ri sc sd tenn tex utah vt va wash wva wis wyo dc d.c. n.h. n.j. n.m. n.y. n.c. n.d. r.i. s.c. s.d. w.va. w.v.").split(" "));
const CA = new Set("ontario ont quebec qc que british columbia bc b.c. alberta alta manitoba man saskatchewan sask nova scotia ns nb new brunswick newfoundland nl pei".split(" "));
const clean = (s) => s.trim().toLowerCase().replace(/\.$/, "").replace(/\./g, "");
function country(hometown) {
  if (!hometown) return "";
  const parts = hometown.split(",").map((s) => s.trim()).filter(Boolean);
  const last = parts[parts.length - 1] || "";
  const k = clean(last);
  if (US.has(k) || US.has(last.toLowerCase())) return "USA";
  if (CA.has(k) || k === "canada") return "Canada";
  if (parts.length === 1) return ""; // sin país ni estado: no se adivina
  return last;
}
const POS = { GK: "GK", D: "D", DEF: "D", M: "M", MID: "M", F: "F", FWD: "F", "D/M": "D/M", "M/D": "M/D", "M/F": "M/F", "F/M": "F/M" };
const CLS = { "FR": "Fr", "SO": "So", "JR": "Jr", "SR": "Sr", "GR": "Gr", "5TH": "Gr", "R-FR": "R-Fr", "R-SO": "R-So", "R-JR": "R-Jr", "R-SR": "R-Sr" };

const text = fs.readFileSync(file, "utf8").split("\n");
const out = {}; let cur = null;
for (const raw of text) {
  const line = raw.trim();
  if (!line || line.startsWith("#") && !line.startsWith("##")) continue;
  if (line.startsWith("##")) { cur = line.slice(2).split("|")[0].trim(); out[cur] = {}; continue; }
  const [, name, pos, cls, hometown] = line.split("|").map((s) => s.trim());
  if (!cur || !name) continue;
  out[cur][name] = [POS[(pos || "").toUpperCase()] || (pos || ""), CLS[(cls || "").toUpperCase().replace(/\.$/, "")] || "", hometown || "", country(hometown)];
}
const f = "datos/SOCCER_D2M_BIO_2026.json";
const B = JSON.parse(fs.readFileSync(f, "utf8"));
const P = JSON.parse(fs.readFileSync("datos/PROGRAMS_ALL_SPORTS.json", "utf8"));
for (const [school, bio] of Object.entries(out)) {
  const known = P.some((p) => p.School === school && p.sport === "Soccer" && p.Gender === "M");
  const n = Object.keys(bio).length, ext = Object.values(bio).filter((b) => b[3] && b[3] !== "USA").length, nocountry = Object.values(bio).filter((b) => !b[3]).length;
  console.log(`${known ? "OK " : "NO ESTÁ EN EL CATÁLOGO "}${school}: ${n} jugadores, ${ext} de afuera de EE.UU., ${nocountry} sin país`);
  if (known) B.M[school] = bio;
}
if (!dry) fs.writeFileSync(f, JSON.stringify(B));
