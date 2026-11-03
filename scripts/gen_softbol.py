#!/usr/bin/env python3
"""Páginas de búsquedas abiertas de softbol: /softball/ (es) y /en/softball/ (en).
Estáticas, con filtros en JS mínimo. Correr DESPUÉS de gen_seo.py, gen_seo_en.py y gen_blog.py
(agrega sus URLs al sitemap y a llms.txt). Se regenera cada vez que se actualiza datos/FIELDLEVEL_NEEDS.json."""
import re, json, html, datetime, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "https://smartrecruit.com.ar"
esc = html.escape
TODAY = os.environ.get("SEO_DATE", datetime.date.today().isoformat())

src = open(f"{ROOT}/RosterReal.jsx", encoding="utf-8").read()
SNAP = datetime.datetime.strptime(re.search(r'NEEDS_SNAPSHOT_AT\s*=\s*"([^"]+)"', src).group(1), "%Y-%m-%dT%H:%M:%SZ")
data = json.load(open(f"{ROOT}/datos/FIELDLEVEL_NEEDS.json", encoding="utf-8"))
rows = [x for x in data if "softball" in str(x.get("sport", "")).lower()]
rows.sort(key=lambda x: x.get("hours_since_posted", 0))
N = len(rows)

GROUP = {"P": "P", "C": "C", "1B": "IF", "2B": "IF", "3B": "IF", "SS": "IF", "INF": "IF", "OF": "OF", "LF": "OF", "CF": "OF", "RF": "OF"}
STATES = {"AL": "Alabama", "AZ": "Arizona", "AR": "Arkansas", "CA": "California", "GA": "Georgia", "IL": "Illinois", "IA": "Iowa", "KS": "Kansas", "MD": "Maryland", "MA": "Massachusetts",
          "MN": "Minnesota", "MO": "Missouri", "NE": "Nebraska", "NJ": "New Jersey", "NY": "New York", "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio", "OR": "Oregon",
          "PA": "Pennsylvania", "RI": "Rhode Island", "TN": "Tennessee", "TX": "Texas", "VT": "Vermont", "WA": "Washington", "WV": "West Virginia", "FL": "Florida"}
def state(x):
    m = re.search(r",\s*([A-Z]{2})\s*$", x.get("place") or "")
    return m.group(1) if m else ""
for x in rows:
    x["_st"] = state(x)
    x["_date"] = (SNAP - datetime.timedelta(hours=x.get("hours_since_posted", 0))).date()
    x["_g"] = GROUP.get(x.get("position_code"), "")

CC = json.load(open(f"{ROOT}/datos/COACH_CONTACTS_BY_PROGRAM.json", encoding="utf-8"))
def has_mail(x):
    c = CC.get(f"{x['university']}|Softball|F") or {}
    return bool(c.get("email") or any(a.get("email") for a in c.get("assistants", [])))
def counts(key):
    c = {}
    for x in rows: c[x[key]] = c.get(x[key], 0) + 1
    return c
DIV_ORDER = ["NCAA D1", "NCAA D2", "NCAA D3", "NAIA", "NJCAA D1", "NJCAA D2", "NJCAA D3", "CCCAA", "NWAC", "NCCAA", "USCAA"]
divs = counts("division"); yrs = {}
for x in rows: yrs[x.get("class_year_needed")] = yrs.get(x.get("class_year_needed"), 0) + 1
sts = counts("_st")

STYLE_EXTRA = """<style>.flt{display:flex;flex-wrap:wrap;gap:10px;margin:14px 0}.flt label{display:flex;flex-direction:column;font-size:.85rem;font-weight:600;gap:4px}.flt select{padding:8px 10px;border:1px solid #c9d3e6;border-radius:8px;font:inherit;background:#fff;min-width:140px}#cnt{font-weight:600;margin:6px 0}td.p{white-space:nowrap}table.sb td,table.sb th{font-size:.92rem}tr[hidden]{display:none}</style>"""
FOOT_ES = None
tpl = open(f"{ROOT}/public/guias/como-escribirle-a-un-coach/index.html", encoding="utf-8").read()
style = re.search(r"<style>.*?</style>", tpl, re.S).group(0)
footer_es = re.search(r"<footer>.*?</footer>", tpl, re.S).group(0)
footer_en = '<footer><div class="in">Smartrecruit is a website for getting a U.S. college sports scholarship on your own, for free. It is not an agent or an intermediary, does not guarantee scholarships or admission, and does not charge for its use. It is not affiliated with the NCAA, the NAIA, the NJCAA or any university. Rules change: always confirm with official sources. The Smartrecruit app itself is currently in Spanish.</div></footer>'
FONTS = '<link rel="icon" href="/favicon.ico" sizes="any" />\n<link rel="apple-touch-icon" href="/apple-touch-icon.png" />\n<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700&family=Source+Sans+3:wght@400;600&display=swap" rel="stylesheet">'

JS = """<script>(function(){var f=document.querySelectorAll('.flt select'),r=document.querySelectorAll('#t tbody tr'),c=document.getElementById('cnt'),T=%d,M=%s;
function a(){var v={};f.forEach(function(s){v[s.name]=s.value});var n=0;r.forEach(function(e){var ok=(!v.d||e.dataset.d===v.d)&&(!v.s||e.dataset.s===v.s)&&(!v.p||e.dataset.p===v.p)&&(!v.y||e.dataset.y===v.y);e.hidden=!ok;if(ok)n++});c.textContent=M.replace('{n}',n).replace('{t}',T)}
f.forEach(function(s){s.addEventListener('change',a)});a()})();</script>"""

L = {
 "es": dict(lang="es", loc="es_AR", url=f"{BASE}/softball/", alt=f"{BASE}/en/softball/", out="public/softball/index.html",
   title="Búsquedas abiertas de softbol en universidades de EE.UU. (coaches que reclutan ahora)",
   h1="Búsquedas abiertas de softbol en universidades de EE.UU.",
   desc=f"{N} búsquedas de coaches de softbol femenino, filtrables por división, estado, posición y año de egreso. NCAA, NAIA y NJCAA. Actualizado al {SNAP.strftime('%d/%m/%Y')}.",
   home="/", homet="Inicio", brand_cta="Armá tu perfil gratis", crumbs='<a href="/">Inicio</a> › <a href="/guias/">Guías</a> › Búsquedas abiertas de softbol',
   upd=f"Datos al {SNAP.strftime('%d/%m/%Y')}",
   lead=f"<b>Hay {N} búsquedas abiertas de softbol femenino de {len(set(x['university'] for x in rows))} universidades, publicadas por sus coaches.</b> Filtralas por división, estado, posición y año de egreso, y escribile al coach con el mail que genera Smartrecruit.",
   how="<h2>Cómo usar esta lista</h2><p>Cada fila es una publicación de un coach que busca jugadoras para un puesto y un año de egreso. <b>Egreso</b> es el año en que la jugadora termina el secundario. Si terminás en diciembre de 2026 y empezás la universidad en agosto de 2027, en general te corresponde la <i>class</i> de 2027: confirmalo con cada coach. Las publicaciones tienen días o semanas, así que el cupo puede estar cubierto: fijate la fecha y escribile al coach igual si tu perfil encaja.</p>",
   cols=["Universidad", "División", "Lugar", "Posición", "Egreso", "Publicada", "Mail del coach"],
   fl=dict(d="División", s="Estado", p="Posición", y="Año de egreso", all="Todas", alls="Todos"),
   pos={"P": "Lanzadora", "C": "Receptora", "IF": "Cuadro (1B, 2B, 3B, SS)", "OF": "Jardín (LF, CF, RF)"},
   cnt="Mostrando {n} de {t} búsquedas", link="🔒 Ver mail (cuenta gratis)", fmt=lambda d: d.strftime("%d/%m"),
   foot=footer_es,
   tail=f"""<h2>Qué divisiones aparecen</h2><p>La mayoría de las búsquedas son de junior colleges (NJCAA y asociaciones regionales como CCCAA y NWAC) y de la NAIA; la NCAA Division I tiene muy pocas. Para entender qué da cada división, leé <a href="/blog/softbol-universitario-eeuu-divisiones-becas-calendario/">cómo funciona el softbol universitario en EE.UU.</a> y la <a href="/guias/beca-softbol-estados-unidos-latinoamericanas/">guía de becas de softbol</a>.</p>
<h2>Preguntas frecuentes</h2>
<h3>¿De dónde salen estas búsquedas?</h3><p>Son publicaciones de los coaches de cada programa. Smartrecruit las reúne, las ordena y les suma el mail del coach; no es parte de ninguna universidad.</p>
<h3>¿Puede postularse una jugadora argentina?</h3><p>Sí: las universidades pueden reclutar atletas internacionales, sujetas a las reglas de su asociación y a la admisión de cada una. Revisá la elegibilidad antes de escribir.</p>
<h3>¿Cada cuánto se actualiza?</h3><p>Aproximadamente cada tres días. La fecha de los datos figura arriba.</p>""",
   cta='<div class="box"><b>Hacelo por tu cuenta, gratis, con Smartrecruit:</b> armá tu perfil, mirá qué universidades encajan con vos, conseguí los contactos de los coaches y generá el mail en inglés en minutos. <a href="/">Empezar ahora →</a></div>',
   header='<header><div class="in"><a class="brand" href="/">Smartrecruit</a><a class="cta" href="/">Armá tu perfil gratis</a></div></header>'),
 "en": dict(lang="en", loc="en_US", url=f"{BASE}/en/softball/", alt=f"{BASE}/softball/", out="public/en/softball/index.html",
   title="Open softball recruiting needs at U.S. colleges (coaches recruiting now)",
   h1="Open softball recruiting needs at U.S. colleges",
   desc=f"{N} recruiting needs posted by college softball coaches, filterable by division, state, position and graduation year. NCAA, NAIA and NJCAA. Updated {SNAP.strftime('%B %d, %Y').replace(' 0', ' ')}.",
   crumbs='<a href="/en/">Home</a> › <a href="/en/guides/">Guides</a> › Open softball needs',
   upd=f"Data as of {SNAP.strftime('%B %d, %Y').replace(' 0', ' ')}",
   lead=f"<b>There are {N} open women's softball needs from {len(set(x['university'] for x in rows))} colleges, posted by their coaches.</b> Filter by division, state, position and graduation year, then write to the coach with the email Smartrecruit generates.",
   how="<h2>How to use this list</h2><p>Each row is a coach's post looking for players at a position and graduation year. <b>Class</b> is the year the player finishes high school. If you finish in December 2026 and start college in August 2027, you generally fit the class of 2027: confirm with each coach. Posts are days or weeks old, so the spot may already be filled: check the date and email the coach anyway if your profile fits.</p>",
   cols=["College", "Division", "Location", "Position", "Class", "Posted", "Coach email"],
   fl=dict(d="Division", s="State", p="Position", y="Class", all="All", alls="All"),
   pos={"P": "Pitcher", "C": "Catcher", "IF": "Infield (1B, 2B, 3B, SS)", "OF": "Outfield (LF, CF, RF)"},
   cnt="Showing {n} of {t} needs", link="🔒 View email (free account)", fmt=lambda d: d.strftime("%b %d").replace(" 0", " "),
   foot=footer_en,
   tail="""<h2>Which divisions appear</h2><p>Most needs come from junior colleges (NJCAA and regional associations such as CCCAA and NWAC) and the NAIA; NCAA Division I has very few. To understand what each division offers, read <a href="/en/blog/how-us-college-softball-works-divisions-scholarships-calendar/">how U.S. college softball works</a> and the <a href="/en/guides/">guides</a>.</p>
<h2>Frequently asked questions</h2>
<h3>Where do these needs come from?</h3><p>They are posts by each program's coaches. Smartrecruit gathers and sorts them and adds the coach's email; it is not part of any college.</p>
<h3>Can an international player apply?</h3><p>Yes: colleges can recruit international athletes, subject to their association's rules and each school's admission. Check eligibility before writing.</p>
<h3>How often is it updated?</h3><p>About every three days. The data date is shown above.</p>""",
   cta='<div class="box"><b>Do it yourself, for free, with Smartrecruit:</b> build your profile, see which universities fit you, get the coaches\' contacts and generate the email in English in minutes. The app itself is currently in Spanish. <a href="/en/">Learn more →</a></div>',
   header='<header><div class="in"><a class="brand" href="/en/">Smartrecruit</a><a class="cta" href="/">Open the app (Spanish)</a></div></header>'),
}

def build(k):
    c = L[k]
    def sel(name, label, opts):
        o = f'<option value="">{c["fl"]["all"] if name != "s" else c["fl"]["alls"]}</option>' + "".join(f'<option value="{esc(v)}">{esc(t)}</option>' for v, t in opts)
        return f'<label>{label}<select name="{name}">{o}</select></label>'
    d_opts = [(d, f"{d} ({divs[d]})") for d in DIV_ORDER if d in divs] + [(d, f"{d} ({n})") for d, n in divs.items() if d not in DIV_ORDER]
    s_opts = [(s, f"{STATES.get(s, s)} ({n})") for s, n in sorted(sts.items(), key=lambda kv: STATES.get(kv[0], kv[0])) if s]
    p_opts = [(g, f"{t} ({sum(1 for x in rows if x['_g'] == g)})") for g, t in c["pos"].items()]
    y_opts = [(str(y), f"{y} ({n})") for y, n in sorted(yrs.items()) if y]
    filters = '<div class="flt">' + sel("d", c["fl"]["d"], d_opts) + sel("s", c["fl"]["s"], s_opts) + sel("p", c["fl"]["p"], p_opts) + sel("y", c["fl"]["y"], y_opts) + "</div>"
    body_rows = "".join(
        f'<tr data-d="{esc(x["division"] or "")}" data-s="{x["_st"]}" data-p="{x["_g"]}" data-y="{x.get("class_year_needed") or ""}"><td>{esc(x["university"])}</td><td>{esc(x["division"] or "")}</td><td>{esc(x["place"] or "")}</td><td>{esc(x.get("position_code") or "")}</td><td>{x.get("class_year_needed") or ""}</td><td class="p">{c["fmt"](x["_date"])}</td><td>' + (f'<a href="/">{c["link"]}</a>' if has_mail(x) else "—") + "</td></tr>"
        for x in rows)
    table = '<div class="wrap"><table class="sb" id="t"><thead><tr>' + "".join(f"<th>{h}</th>" for h in c["cols"]) + f"</tr></thead><tbody>{body_rows}</tbody></table></div>"
    faq = re.findall(r"<h3>(.*?)</h3><p>(.*?)</p>", c["tail"])
    ld = json.dumps([
        {"@context": "https://schema.org", "@type": "WebPage", "name": c["h1"], "description": c["desc"], "inLanguage": c["lang"], "url": c["url"], "dateModified": SNAP.date().isoformat(), "publisher": {"@type": "Organization", "name": "Smartrecruit", "url": BASE}},
        {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"<[^>]+>", "", a)}} for q, a in faq]}], ensure_ascii=False)
    alt = f'<link rel="alternate" hreflang="{c["lang"]}" href="{c["url"]}"><link rel="alternate" hreflang="{"en" if k == "es" else "es"}" href="{c["alt"]}"><link rel="alternate" hreflang="x-default" href="{BASE}/softball/">'
    page = f'''<!doctype html>
<html lang="{c['lang']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(c['title'])} | Smartrecruit</title>
<meta name="description" content="{esc(c['desc'])}">
<link rel="canonical" href="{c['url']}">
{alt}
<meta property="og:title" content="{esc(c['title'])} | Smartrecruit">
<meta property="og:description" content="{esc(c['desc'])}">
<meta property="og:url" content="{c['url']}">
<meta property="og:type" content="website">
<meta property="og:locale" content="{c['loc']}">
<meta name="theme-color" content="#0b2a6b">
{FONTS}
{style}
{STYLE_EXTRA}
<script type="application/ld+json">{ld}</script>
<script defer src="/assets/analytics.js"></script>
</head>
<body>
{c['header']}
<main>
<div class="crumb">{c['crumbs']}</div>
<h1>{esc(c['h1'])}</h1>
<p class="upd">{c['upd']}</p>
<p class="lead">{c['lead']}</p>
{filters}
<p id="cnt" aria-live="polite"></p>
{table}
{c['how']}
{c['tail']}
{c['cta']}
</main>
{c['foot']}
{JS % (N, json.dumps(c['cnt']))}
</body>
</html>
'''
    out = f"{ROOT}/{c['out']}"; os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w", encoding="utf-8").write(page)
build("es"); build("en")

# sitemap y llms.txt (idempotente)
sp = f"{ROOT}/public/sitemap.xml"; sm = open(sp, encoding="utf-8").read()
sm = re.sub(r"\s*<url><loc>[^<]*/(softball|en/softball)/</loc>.*?</url>", "", sm)
sm = sm.replace("</urlset>", "".join(f"  <url><loc>{BASE}{u}</loc><lastmod>{SNAP.date().isoformat()}</lastmod></url>\n" for u in ("/softball/", "/en/softball/")) + "</urlset>")
open(sp, "w", encoding="utf-8").write(sm)
lp = f"{ROOT}/public/llms.txt"; l = open(lp, encoding="utf-8").read().split("\n## Softbol")[0].rstrip("\n")
l += f"\n\n## Softbol (búsquedas abiertas de coaches)\n- [Búsquedas abiertas de softbol]({BASE}/softball/)\n- [Open softball needs (English)]({BASE}/en/softball/)\n"
open(lp, "w", encoding="utf-8").write(l)
print("softbol rows:", N, "divisions:", len(divs), "states:", len(sts))
