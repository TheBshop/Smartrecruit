// Genera una página estática por universidad (dist/universidades/<slug>/) con datos oficiales de EE.UU. (EADA, IPEDS, College Scorecard)
// y los programas que tiene Smartrecruit. Sin contactos de coaches (esos son solo con cuenta). Se ejecuta desde build.mjs.
import fs from "fs";
const R = (f) => JSON.parse(fs.readFileSync(`datos/${f}.json`, "utf8"));
const BASE = "https://smartrecruit.com.ar";
const PROGRAMS = R("PROGRAMS_ALL_SPORTS"), EADA = R("EADA_DATA"), SITE = R("EADA_SITE_NAMES"), SC = R("SCORECARD_BY_ID"), SCN = R("SCORECARD_NAME_IDS");
const byName = new Map(EADA.map((e) => [e.n, e])), byU = new Map(EADA.map((e) => [e.u, e]));
const tpl = fs.readFileSync("public/guias/como-escribirle-a-un-coach/index.html", "utf8");
const style = tpl.match(/<style>[\s\S]*?<\/style>/)[0].replace("</style>", "ul.cols{columns:2;padding-left:18px}@media(max-width:600px){ul.cols{columns:1}}.k{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:10px;margin:14px 0}.k div{background:var(--raised);border:1px solid var(--line);border-radius:8px;padding:10px 12px}.k span{display:block;font-size:13px;color:var(--muted)}.k b{font-size:18px}</style>");
const footer = tpl.match(/<footer>[\s\S]*?<\/footer>/)[0];
const esc = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
const slugify = (s) => s.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase().replace(/&/g, "and").replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "");
const usd = (v) => "USD " + Math.round(v).toLocaleString("es-AR");
function eadaDivision(c0) {
  const c = String(c0 || "");
  if (/NCAA Division III/.test(c)) return "NCAA D3"; if (/NCAA Division II\b/.test(c)) return "NCAA D2"; if (/NCAA Division I\b/.test(c)) return "NCAA D1";
  if (/NAIA/.test(c)) return "NAIA";
  if (/NJCAA/.test(c)) return /(Division I\b|D-?1\b)/.test(c) ? "NJCAA D1" : /(Division II\b|D-?2\b)/.test(c) ? "NJCAA D2" : /(Division III\b|D-?3\b)/.test(c) ? "NJCAA D3" : "NJCAA";
  for (const k of ["NWAC", "CCCAA", "NCCAA", "USCAA"]) if (c.includes(k)) return k;
  return c;
}
const SPORT_ES = { Soccer: "Fútbol", Basketball: "Básquet", Volleyball: "Vóley", Softball: "Softbol", "Field Hockey": "Hockey sobre césped", Rugby: "Rugby", Baseball: "Béisbol", Track: "Atletismo", Tennis: "Tenis", Golf: "Golf", Swimming: "Natación", Lacrosse: "Lacrosse", "Cross Country": "Cross country", Gymnastics: "Gimnasia" };
const EADA_ES = { soc: "Fútbol", bkb: "Básquet", vb: "Vóley", fh: "Hockey sobre césped", gym: "Gimnasia", trk: "Atletismo", xc: "Cross country", ten: "Tenis", sb: "Softbol", bsb: "Béisbol", swm: "Natación", golf: "Golf", lax: "Lacrosse", rug: "Rugby" };
const GUIDE = { Soccer: ["beca-futbol-estados-unidos-latinoamericanos", "Becas de fútbol"], Basketball: ["beca-basquet-estados-unidos-latinoamericanos", "Becas de básquet"], Volleyball: ["beca-voley-estados-unidos-latinoamericanas", "Becas de vóley"], Softball: ["beca-softbol-estados-unidos-latinoamericanas", "Becas de softbol"], "Field Hockey": ["beca-hockey-cesped-estados-unidos-latinoamericanas", "Becas de hockey sobre césped"], Rugby: ["beca-rugby-estados-unidos-latinoamericanos", "Becas de rugby"] };
const bySchool = new Map();
for (const p of PROGRAMS) { if (!bySchool.has(p.School)) bySchool.set(p.School, []); bySchool.get(p.School).push(p); }
const used = new Set(), pages = [];
for (const [school, progs] of [...bySchool].sort((a, b) => a[0].localeCompare(b[0]))) {
  const e = byU.get(SITE[school]) || byName.get(school);
  if (!e) continue;
  const sc = SC[String(e.u)] || SC[SCN[school]] || null;
  const divs = {}; progs.forEach((p) => { if (p.Division) divs[p.Division] = (divs[p.Division] || 0) + 1; });
  const division = Object.entries(divs).sort((a, b) => b[1] - a[1])[0]?.[0] || eadaDivision(e.cls);
  const first = progs.find((p) => p.City) || {};
  const city = first.City || e.city || "", state = first.State || e.st || "";
  let slug = slugify(school); if (used.has(slug)) slug += "-" + slugify(e.st || state); used.add(slug);
  const ownSports = [...new Set(progs.map((p) => p.sport))].sort();
  const ownEs = ownSports.map((s) => SPORT_ES[s] || s);
  const pub = e.ctl === 1 ? "pública" : "privada";
  const kind = e.lvl === 2 ? "college de 2 años" : "universidad de 4 años";
  const d3 = /D3/.test(division);
  const teams = Object.entries(e.sp || {}).sort((a, b) => b[1][0] + b[1][1] - (a[1][0] + a[1][1]));
  const perAth = (i) => (e.ath && e.ath[i] > 0 ? e.aid[i] / e.ath[i] : 0);
  const aidAny = (e.aid || [0, 0]).some((v) => v > 0);
  const place = [city, state].filter(Boolean).join(", ");
  const lead = `<b>${esc(school)} es una ${e.lvl === 2 ? "institución de 2 años" : "universidad"} ${pub}${place ? ` de ${esc(place)}` : ""} que compite en ${esc(division)}.</b> En Smartrecruit figura con programas de ${esc(ownEs.slice(0, 6).join(", "))}${ownEs.length > 6 ? " y otros" : ""}. Acá tenés sus datos oficiales de deportes, becas, costo y admisión.`;
  let body = `<h2>Datos básicos</h2><div class="k"><div><span>Asociación deportiva</span><b>${esc(division)}</b></div><div><span>Tipo</span><b>${esc(pub[0].toUpperCase() + pub.slice(1))} · ${esc(kind)}</b></div>${place ? `<div><span>Ubicación</span><b>${esc(place)}</b></div>` : ""}${first.Conference ? `<div><span>Conferencia</span><b>${esc(first.Conference)}</b></div>` : ""}</div>`;
  if (teams.length) body += `<h2>Deportes y cantidad de atletas</h2><p>Cantidad de deportistas por deporte que la institución reportó al Departamento de Educación de EE.UU. (EADA 2024).</p><div class="wrap"><table><tr><th>Deporte</th><th>Varones</th><th>Mujeres</th></tr>${teams.map(([k, v]) => `<tr><td>${esc(EADA_ES[k] || k)}</td><td>${v[0] || "—"}</td><td>${v[1] || "—"}</td></tr>`).join("")}</table></div>`;
  body += `<h2>Becas deportivas</h2>`;
  if (d3) body += `<p>${esc(school)} compite en la Division III de la NCAA, que no da becas deportivas. Los atletas reciben ayuda académica o por necesidad económica.</p>`;
  else if (aidAny) body += `<p>${esc(school)} reportó ayuda económica para atletas${perAth(0) > 0 ? ` de ${usd(perAth(0))} por deportista varón` : ""}${perAth(0) > 0 && perAth(1) > 0 ? " y" : ""}${perAth(1) > 0 ? ` de ${usd(perAth(1))} por deportista mujer` : ""}, en promedio. Ojo: en la mayoría de los deportes la beca se reparte entre varios atletas, así que las ofertas varían mucho de un jugador a otro. Nunca asumas una beca completa.</p>`;
  else body += `<p>${esc(school)} no reportó ayuda económica para atletas en los datos oficiales que usamos. Preguntale directamente al coach qué ayuda puede ofrecer.</p>`;
  if (sc) {
    body += `<h2>Costo y admisión</h2><div class="k">${sc.co || sc.ci ? `<div><span>Costo anual estimado${e.ctl === 1 ? " (fuera del estado)" : ""}</span><b>${usd(sc.co || sc.ci)}</b></div>` : ""}${e.ctl === 1 && sc.ci ? `<div><span>Costo anual (residentes del estado)</span><b>${usd(sc.ci)}</b></div>` : ""}${sc.a ? `<div><span>Tasa de admisión</span><b>${esc(sc.a)}</b></div>` : ""}${sc.s ? `<div><span>SAT (25%-75%)</span><b>${esc(sc.s)}</b></div>` : ""}${sc.t ? `<div><span>ACT (25%-75%)</span><b>${esc(sc.t)}</b></div>` : ""}${sc.e ? `<div><span>Estudiantes de grado</span><b>${Number(sc.e).toLocaleString("es-AR")}</b></div>` : ""}${sc.g ? `<div><span>Tasa de graduación</span><b>${esc(sc.g)}</b></div>` : ""}${e.intl != null ? `<div><span>Egresados internacionales</span><b>${(e.intl * 100).toFixed(1).replace(".", ",")}%</b></div>` : ""}</div><p>El costo es una estimación anual antes de becas e incluye matrícula, alojamiento y otros gastos. En universidades públicas, un estudiante internacional paga el costo fuera del estado. Fuente: College Scorecard del Departamento de Educación de EE.UU. Confirmá todo en el sitio oficial${sc.w ? ` (${esc(sc.w.replace(/\/$/, ""))})` : ""}.</p>`;
  }
  const guides = ownSports.filter((s) => GUIDE[s]);
  if (guides.length) body += `<h2>Guías para tu deporte</h2><ul>${guides.map((s) => `<li><a href="/guias/${GUIDE[s][0]}/">${GUIDE[s][1]} en Estados Unidos para latinoamericanos</a></li>`).join("")}</ul>`;
  body += `<h2>Cómo contactar a los coaches de ${esc(school)}</h2><p>Los contactos oficiales de los coaches y las vacantes abiertas están disponibles con una cuenta gratuita de Smartrecruit, junto con un generador de mails en inglés. Mirá primero la <a href="/guias/como-escribirle-a-un-coach/">guía para escribirle a un coach</a>.</p>`;
  const faq = [
    [`¿${school} da becas deportivas?`, d3 ? `No. ${school} compite en la Division III de la NCAA, que no da becas deportivas; la ayuda es académica o por necesidad económica.` : aidAny ? `Según los datos oficiales, sí reportó ayuda económica para atletas. La cantidad depende de cada deporte y de cada jugador, así que preguntale al coach.` : `En los datos oficiales no reportó ayuda económica para atletas. Preguntale directamente al coach.`],
    [`¿En qué división compite ${school}?`, `Compite en ${division}.`],
    [`¿Qué deportes tiene ${school} en Smartrecruit?`, `${ownEs.join(", ")}.`],
  ];
  if (sc && (sc.co || sc.ci)) faq.splice(2, 0, [`¿Cuánto cuesta estudiar en ${school} siendo internacional?`, `El costo anual estimado es de ${usd(sc.co || sc.ci)} antes de becas${e.ctl === 1 ? " (es el costo fuera del estado, que es el que paga un estudiante internacional)" : ""}. Confirmalo en el sitio oficial de la universidad.`]);
  const url = `${BASE}/universidades/${slug}/`;
  const title = `${school}: becas deportivas, costos y deportes para internacionales`;
  const desc = `${school}${place ? ` (${place})` : ""}: división ${division}, deportes con atletas, ayuda económica, costo anual y admisión, con datos oficiales de EE.UU.`.slice(0, 300);
  const ld = JSON.stringify([
    { "@context": "https://schema.org", "@type": "CollegeOrUniversity", name: school, url: sc && sc.w ? "https://" + sc.w.replace(/^https?:\/\//, "") : undefined, address: place ? { "@type": "PostalAddress", addressLocality: city, addressRegion: state, addressCountry: "US" } : undefined },
    { "@context": "https://schema.org", "@type": "FAQPage", mainEntity: faq.map(([q, a]) => ({ "@type": "Question", name: q, acceptedAnswer: { "@type": "Answer", text: a } })) },
  ]);
  const html = `<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${esc(title)} | Smartrecruit</title>
<meta name="description" content="${esc(desc)}">
<link rel="canonical" href="${url}">
<meta property="og:title" content="${esc(title)} | Smartrecruit">
<meta property="og:description" content="${esc(desc)}">
<meta property="og:url" content="${url}">
<meta property="og:type" content="article">
<meta property="og:locale" content="es_AR">
<meta name="theme-color" content="#0b2a6b">
<link rel="icon" href="/favicon.ico" sizes="any" />
<link rel="apple-touch-icon" href="/apple-touch-icon.png" />
<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700&family=Source+Sans+3:wght@400;600&display=swap" rel="stylesheet">
${style}
<script type="application/ld+json">${ld}</script>
<script defer src="/assets/analytics.js"></script>
</head>
<body>
<header><div class="in"><a class="brand" href="/">Smartrecruit</a><a class="cta" href="/">Armá tu perfil gratis</a></div></header>
<main>
<div class="crumb"><a href="/">Inicio</a> › <a href="/universidades/">Universidades</a> › ${esc(school)}</div>
<h1>${esc(school)}: becas deportivas, costos y deportes</h1>
<p class="lead">${lead}</p>
${body}
<h2>Preguntas frecuentes</h2>
${faq.map(([q, a]) => `<h3>${esc(q)}</h3><p>${esc(a)}</p>`).join("")}
<div class="box"><b>Hacelo por tu cuenta, gratis, con Smartrecruit:</b> armá tu perfil, mirá qué universidades encajan con vos y generá el mail en inglés para el coach. <a href="/">Empezar ahora →</a></div>
<p class="upd">Datos oficiales del Departamento de Educación de EE.UU. (EADA 2024, IPEDS, College Scorecard). Pueden estar desactualizados: confirmá en el sitio oficial de la universidad.</p>
</main>
${footer}
</body>
</html>
`;
  fs.mkdirSync(`dist/universidades/${slug}`, { recursive: true });
  fs.writeFileSync(`dist/universidades/${slug}/index.html`, html);
  pages.push({ school, slug, state: state || "Otros", division });
}
// Índice
const byState = new Map(); pages.forEach((p) => { if (!byState.has(p.state)) byState.set(p.state, []); byState.get(p.state).push(p); });
const idxBody = [...byState].sort((a, b) => a[0].localeCompare(b[0])).map(([st, ps]) => `<h2 id="${slugify(st)}">${esc(st)}</h2><ul class="cols">${ps.map((p) => `<li><a href="/universidades/${p.slug}/">${esc(p.school)}</a> <small>${esc(p.division)}</small></li>`).join("")}</ul>`).join("");
const idxUrl = `${BASE}/universidades/`;
fs.writeFileSync("dist/universidades/index.html", `<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Universidades de EE.UU. con deporte universitario: becas, costos y programas | Smartrecruit</title>
<meta name="description" content="Más de ${pages.length} universidades y colleges de EE.UU. con sus deportes, división, ayuda económica para atletas, costo anual y admisión, con datos oficiales.">
<link rel="canonical" href="${idxUrl}">
<meta property="og:title" content="Universidades de EE.UU. con deporte universitario | Smartrecruit"><meta property="og:url" content="${idxUrl}"><meta property="og:type" content="website"><meta property="og:locale" content="es_AR">
<meta name="theme-color" content="#0b2a6b"><link rel="icon" href="/favicon.ico" sizes="any" />
<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700&family=Source+Sans+3:wght@400;600&display=swap" rel="stylesheet">
${style}
<script defer src="/assets/analytics.js"></script></head><body>
<header><div class="in"><a class="brand" href="/">Smartrecruit</a><a class="cta" href="/">Armá tu perfil gratis</a></div></header>
<main><div class="crumb"><a href="/">Inicio</a> › Universidades</div>
<h1>Universidades de EE.UU. con deporte universitario</h1>
<p class="lead"><b>${pages.length} universidades y colleges con sus deportes, división, ayuda económica para atletas, costo anual y admisión, con datos oficiales de EE.UU.</b> Elegí una para ver su ficha.</p>
${idxBody}
</main>${footer}</body></html>
`);
// Sitemap: agrega las páginas a dist/sitemap.xml
const lm = new Date().toISOString().slice(0, 10);
const smp = "dist/sitemap.xml";
fs.writeFileSync(smp, fs.readFileSync(smp, "utf8").replace("</urlset>", [`${idxUrl}`, ...pages.map((p) => `${BASE}/universidades/${p.slug}/`)].map((u) => `  <url><loc>${u}</loc><lastmod>${lm}</lastmod></url>\n`).join("") + "</urlset>"));
console.log("universidades:", pages.length);
