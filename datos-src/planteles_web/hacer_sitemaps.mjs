// Genera 3 sitemaps de Web Scraper (webscraper.io) para sitios Sidearm: estadísticas del año anterior, plantel actual y coaches.
// Uso: node hacer_sitemaps.mjs hosts.txt [deporte=womens-soccer] [temporada_stats=2025]
// Después: en la extensión Web Scraper > Create new sitemap > Import sitemap, pegar cada .json de la carpeta sitemaps/ y correr "Scrape".
import fs from "fs";
const [file, sport = "womens-soccer", season = "2025"] = process.argv.slice(2);
const hosts = fs.readFileSync(file, "utf8").split("\n").map((l) => l.trim()).filter((l) => l && !l.startsWith("#")).map((l) => l.split("|")[0].trim());
const txt = (id, selector, extra = {}) => ({ id, type: "SelectorText", parentSelectors: ["fila"], selector, multiple: false, regex: "", delay: 0, ...extra });
const mk = (name, page, selectors) => ({ _id: `sr_${sport}_${name}`, startUrl: hosts.map((h) => `https://${h}/sports/${sport}/${page}`), selectors });
const stats = mk(`stats_${season}`, `stats/${season}`, [
  { id: "tabla", type: "SelectorTable", parentSelectors: ["_root"], selector: "table", multiple: true, delay: 0, tableHeaderRowSelector: "thead tr", tableDataRowSelector: "tbody tr",
    columns: ["Player", "GP", "GS", "MIN", "G", "A", "PTS", "SH", "SOG", "GA", "GAA", "SV", "W", "L"].map((h) => ({ header: h, name: h, extract: true })) },
]);
const roster = mk("roster", "roster", [
  { id: "fila", type: "SelectorElement", parentSelectors: ["_root"], selector: ".sidearm-roster-player", multiple: true, delay: 0 },
  txt("numero", ".sidearm-roster-player-jersey-number"), txt("nombre", ".sidearm-roster-player-name a"), txt("posicion", ".sidearm-roster-player-position"),
  txt("anio", ".sidearm-roster-player-academic-year"), txt("ciudad", ".sidearm-roster-player-hometown"), txt("colegio", ".sidearm-roster-player-highschool"),
]);
const coaches = mk("coaches", "coaches", [
  { id: "fila", type: "SelectorElement", parentSelectors: ["_root"], selector: "tr.sidearm-coaches-coach", multiple: true, delay: 0 },
  txt("nombre", "th a"), txt("cargo", "td:not(.sidearm-coaches-image-cell)"), txt("email", 'a[href^="mailto:"]'), txt("telefono", "span.text-no-wrap"),
]);
fs.mkdirSync("sitemaps", { recursive: true });
for (const [n, s] of [["stats", stats], ["roster", roster], ["coaches", coaches]]) fs.writeFileSync(`sitemaps/${n}_${sport}.json`, JSON.stringify(s));
console.log(`${hosts.length} sitios -> sitemaps/stats_${sport}.json, roster_${sport}.json, coaches_${sport}.json`);
