// English university pages (dist/en/universities/<slug>/). Written natively; called from gen_schools.mjs with the same per-school data.
import fs from "fs";
const BASE = "https://smartrecruit.com.ar";
export const esc = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
const usd = (v) => "USD " + Math.round(v).toLocaleString("en-US");
const SPORT = { soc: "Soccer", bkb: "Basketball", vb: "Volleyball", fh: "Field hockey", gym: "Gymnastics", trk: "Track and field", xc: "Cross country", ten: "Tennis", sb: "Softball", bsb: "Baseball", swm: "Swimming", golf: "Golf", lax: "Lacrosse", rug: "Rugby" };
const GUIDE = { Soccer: ["soccer-scholarship-international-players", "Soccer scholarships for international players"], Volleyball: ["volleyball-scholarship-international-players", "Volleyball scholarships for international players"], Basketball: ["basketball-scholarship-international-players", "Basketball scholarships for international players"], Softball: ["softball-scholarship-international-players", "Softball scholarships for international players"], "Field Hockey": ["field-hockey-scholarship-international-players", "Field hockey scholarships for international players"], Rugby: ["rugby-scholarship-international-players", "Rugby scholarships for international players"] };
const cap = (s) => s[0].toUpperCase() + s.slice(1);
const LABEL = { "Básquet masculino": "Men's basketball", "Básquet femenino": "Women's basketball", "Fútbol femenino": "Women's soccer", "Fútbol masculino": "Men's soccer", "Hockey sobre césped": "Field hockey" };
export function enFooter() {
  return `<footer><div class="in">Smartrecruit is a website for getting a U.S. college sports scholarship on your own, for free. It is not an agent or an intermediary, does not guarantee scholarships or admission, and does not charge for its use. It is not affiliated with the NCAA, the NAIA, the NJCAA or any university. Rules change: always confirm with official sources. The Smartrecruit app itself is currently in Spanish.</div></footer>`;
}
export function head({ title, desc, url, esUrl, type, ld }) {
  return `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${esc(title)} | Smartrecruit</title>
<meta name="description" content="${esc(desc)}">
<link rel="canonical" href="${url}">
<link rel="alternate" hreflang="en" href="${url}"><link rel="alternate" hreflang="es" href="${esUrl}"><link rel="alternate" hreflang="x-default" href="${esUrl}">
<meta property="og:title" content="${esc(title)} | Smartrecruit">
<meta property="og:description" content="${esc(desc)}">
<meta property="og:url" content="${url}">
<meta property="og:type" content="${type}">
<meta property="og:locale" content="en_US">
<meta name="theme-color" content="#0b2a6b">
<link rel="icon" href="/favicon.ico" sizes="any" />
<link rel="apple-touch-icon" href="/apple-touch-icon.png" />
<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700&family=Source+Sans+3:wght@400;600&display=swap" rel="stylesheet">
`;
}
export function buildEn(c) {
  const { school, slug, e, sc, division, place, city, ownSports, teams, ra, latamTotal, argTotal, perAth, aidAny, d3, style, esUrl } = c;
  const pub = e.ctl === 1 ? "public" : "private";
  const kind = e.lvl === 2 ? "two-year college" : "four-year university";
  const url = `${BASE}/en/universities/${slug}/`;
  const ownEn = ownSports.map((s) => ({ Soccer: "Soccer", Basketball: "Basketball", Volleyball: "Volleyball", Softball: "Softball", "Field Hockey": "Field hockey", Track: "Track and field" }[s] || s));
  const lead = `<b>${esc(school)} is a ${pub} ${kind}${place ? ` in ${esc(place)}` : ""} that competes in ${esc(division)}.</b> On Smartrecruit it is listed with programs in ${esc(ownEn.slice(0, 6).join(", "))}${ownEn.length > 6 ? " and more" : ""}. Below are its official data on sports, scholarships, cost and admission.`;
  let body = `<h2>Basics</h2><div class="k"><div><span>Athletic association</span><b>${esc(division)}</b></div><div><span>Type</span><b>${cap(pub)} · ${esc(kind)}</b></div>${place ? `<div><span>Location</span><b>${esc(place)}</b></div>` : ""}${c.conference ? `<div><span>Conference</span><b>${esc(c.conference)}</b></div>` : ""}</div>`;
  if (teams.length) body += `<h2>Sports and number of athletes</h2><p>Number of athletes per sport reported by the institution to the U.S. Department of Education (EADA 2024).</p><div class="wrap"><table><tr><th>Sport</th><th>Men</th><th>Women</th></tr>${teams.map(([k, v]) => `<tr><td>${esc(SPORT[k] || k)}</td><td>${v[0] || "—"}</td><td>${v[1] || "—"}</td></tr>`).join("")}</table></div>`;
  if (ra.length) {
    body += `<h2>International players on the rosters</h2><p>Aggregate figures from the most recent rosters we have, counting only players with a listed country of origin. We do not publish names.</p><div class="wrap"><table><tr><th>Team</th><th>Players with country listed</th><th>International</th><th>Most frequent countries</th></tr>${ra.map((r) => `<tr><td>${esc(LABEL[r.label] || r.label)}</td><td>${r.known}</td><td>${r.intl}</td><td>${esc(Object.entries(r.by).sort((a, b) => b[1] - a[1]).slice(0, 4).map(([k, n]) => `${k} (${n})`).join(", ") || "—")}</td></tr>`).join("")}</table></div>${latamTotal > 0 ? `<p>In total, <b>${latamTotal} player${latamTotal === 1 ? "" : "s"} from Latin America</b> appear${argTotal > 0 ? `, ${argTotal} of them from Argentina` : ""}. If you come from the region, it is a sign that the program recruits in your area.</p>` : ""}`;
  }
  body += `<h2>Athletic scholarships</h2>`;
  if (d3) body += `<p>${esc(school)} competes in NCAA Division III, which does not give athletic scholarships. Athletes receive academic or need-based aid.</p>`;
  else if (aidAny) body += `<p>${esc(school)} reported athletic aid${perAth(0) > 0 ? ` averaging ${usd(perAth(0))} per male athlete` : ""}${perAth(0) > 0 && perAth(1) > 0 ? " and" : ""}${perAth(1) > 0 ? ` ${usd(perAth(1))} per female athlete` : ""}. Keep in mind that in most sports the scholarship is split among several athletes, so offers vary a lot from player to player. Never assume a full scholarship.</p>`;
  else body += `<p>${esc(school)} did not report athletic aid in the official data we use. Ask the coach directly what aid they can offer.</p>`;
  if (sc) body += `<h2>Cost and admission</h2><div class="k">${sc.co || sc.ci ? `<div><span>Estimated yearly cost${e.ctl === 1 ? " (out of state)" : ""}</span><b>${usd(sc.co || sc.ci)}</b></div>` : ""}${e.ctl === 1 && sc.ci ? `<div><span>Yearly cost (in-state residents)</span><b>${usd(sc.ci)}</b></div>` : ""}${sc.a ? `<div><span>Admission rate</span><b>${esc(sc.a)}</b></div>` : ""}${sc.s ? `<div><span>SAT (25%-75%)</span><b>${esc(sc.s)}</b></div>` : ""}${sc.t ? `<div><span>ACT (25%-75%)</span><b>${esc(sc.t)}</b></div>` : ""}${sc.e ? `<div><span>Undergraduate students</span><b>${Number(sc.e).toLocaleString("en-US")}</b></div>` : ""}${sc.g ? `<div><span>Graduation rate</span><b>${esc(sc.g)}</b></div>` : ""}${e.intl != null ? `<div><span>International graduates</span><b>${(e.intl * 100).toFixed(1)}%</b></div>` : ""}</div><p>Cost is a yearly estimate before scholarships and includes tuition, housing and other expenses. At public universities an international student pays the out-of-state cost. Source: U.S. Department of Education College Scorecard. Confirm everything on the official site${sc.w ? ` (${esc(sc.w.replace(/\/$/, ""))})` : ""}.</p>`;
  const guides = ownSports.filter((s) => GUIDE[s]);
  body += `<h2>Guides</h2><ul>${guides.map((s) => `<li><a href="/en/guides/${GUIDE[s][0]}/">${GUIDE[s][1]}</a></li>`).join("")}<li><a href="/en/guides/ncaa-eligibility-international-athletes/">NCAA and NAIA eligibility for international athletes</a></li><li><a href="/en/guides/how-to-email-a-college-coach/">How to email a U.S. college coach</a></li></ul>`;
  body += `<h2>How to contact the coaches at ${esc(school)}</h2><p>Official coach contacts and open recruiting searches are available with a free Smartrecruit account, along with an email generator that writes in English. The app itself is currently in Spanish. Start with the <a href="/en/guides/how-to-email-a-college-coach/">guide to emailing a coach</a>.</p>`;
  const faq = [
    [`Does ${school} give athletic scholarships?`, d3 ? `No. ${school} competes in NCAA Division III, which does not give athletic scholarships; aid is academic or need-based.` : aidAny ? `According to official data, it reported athletic aid. The amount depends on each sport and each player, so ask the coach.` : `It did not report athletic aid in the official data. Ask the coach directly.`],
    [`What division does ${school} compete in?`, `It competes in ${division}.`],
    [`Which sports does ${school} have on Smartrecruit?`, `${ownEn.join(", ")}.`],
  ];
  if (ra.length) faq.push([`Does ${school} have international players?`, `On the rosters where we have complete data, ${ra.reduce((a, r) => a + r.intl, 0)} of ${ra.reduce((a, r) => a + r.known, 0)} players with a listed country are international${latamTotal > 0 ? `; ${latamTotal} are from Latin America${argTotal > 0 ? ` and ${argTotal} from Argentina` : ""}` : ""}. Rosters change every season.`]);
  if (sc && (sc.co || sc.ci)) faq.splice(2, 0, [`How much does ${school} cost for an international student?`, `The estimated yearly cost is ${usd(sc.co || sc.ci)} before scholarships${e.ctl === 1 ? " (the out-of-state cost, which is what an international student pays)" : ""}. Confirm it on the university's official site.`]);
  const title = `${school}: athletic scholarships, costs and sports for international athletes`;
  const desc = `${school}${place ? ` (${place})` : ""}: ${division}, sports and athlete numbers, athletic aid, yearly cost and admission, with official U.S. data.`.slice(0, 300);
  const ld = JSON.stringify([
    { "@context": "https://schema.org", "@type": "CollegeOrUniversity", name: school, url: sc && sc.w ? "https://" + sc.w.replace(/^https?:\/\//, "") : undefined, address: place ? { "@type": "PostalAddress", addressLocality: city, addressRegion: c.state, addressCountry: "US" } : undefined },
    { "@context": "https://schema.org", "@type": "FAQPage", mainEntity: faq.map(([q, a]) => ({ "@type": "Question", name: q, acceptedAnswer: { "@type": "Answer", text: a } })) },
  ]);
  const html = `${head({ title, desc, url, esUrl, type: "article" })}${style}
<script type="application/ld+json">${ld}</script>
<script defer src="/assets/analytics.js"></script>
</head>
<body>
<header><div class="in"><a class="brand" href="/en/">Smartrecruit</a><a class="cta" href="/">Open the app (Spanish)</a></div></header>
<main>
<div class="crumb"><a href="/en/">Home</a> › <a href="/en/universities/">Universities</a> › ${esc(school)}</div>
<h1>${esc(school)}: athletic scholarships, costs and sports</h1>
<p class="lead">${lead}</p>
${body}
<h2>Frequently asked questions</h2>
${faq.map(([q, a]) => `<h3>${esc(q)}</h3><p>${esc(a)}</p>`).join("")}
<div class="box"><b>Do it yourself, for free, with Smartrecruit:</b> build your profile, see which universities fit you and generate the English email for the coach. The app is currently in Spanish. <a href="/en/">Learn more →</a></div>
<p class="upd">Official data from the U.S. Department of Education (EADA 2024, IPEDS, College Scorecard). It may be out of date: confirm on the university's official site.</p>
</main>
${enFooter()}
</body>
</html>
`;
  fs.mkdirSync(`dist/en/universities/${slug}`, { recursive: true });
  fs.writeFileSync(`dist/en/universities/${slug}/index.html`, html);
}
export function buildEnIndex(pages, style) {
  const slugify = (s) => s.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase().replace(/&/g, "and").replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "");
  const byState = new Map(); pages.forEach((p) => { const st = p.state === "Otros" ? "Other" : p.state; if (!byState.has(st)) byState.set(st, []); byState.get(st).push(p); });
  const idxBody = [...byState].sort((a, b) => a[0].localeCompare(b[0])).map(([st, ps]) => `<h2 id="${slugify(st)}">${esc(st)}</h2><ul class="cols">${ps.map((p) => `<li><a href="/en/universities/${p.slug}/">${esc(p.school)}</a> <small>${esc(p.division)}</small></li>`).join("")}</ul>`).join("");
  const url = `${BASE}/en/universities/`, esUrl = `${BASE}/universidades/`;
  const title = "U.S. colleges with varsity sports: scholarships, costs and programs", desc = `${pages.length}+ U.S. universities and colleges with their sports, division, athletic aid, yearly cost and admission, using official data.`;
  fs.mkdirSync("dist/en/universities", { recursive: true });
  fs.writeFileSync("dist/en/universities/index.html", `${head({ title, desc, url, esUrl, type: "website" })}${style}
<script defer src="/assets/analytics.js"></script></head><body>
<header><div class="in"><a class="brand" href="/en/">Smartrecruit</a><a class="cta" href="/">Open the app (Spanish)</a></div></header>
<main><div class="crumb"><a href="/en/">Home</a> › Universities</div>
<h1>U.S. colleges with varsity sports</h1>
<p class="lead"><b>${pages.length} universities and colleges with their sports, division, athletic aid, yearly cost and admission, using official U.S. data.</b> Pick one to see its page.</p>
${idxBody}
</main>${enFooter()}</body></html>
`);
}
