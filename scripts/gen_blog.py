#!/usr/bin/env python3
"""Blog (es): public/blog/<slug>/ + índice, sitemap y llms.txt. Correr después de gen_seo.py y gen_seo_en.py."""
import re, json, html, datetime, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "https://smartrecruit.com.ar"
TODAY = os.environ.get("SEO_DATE", datetime.date.today().isoformat())
tpl = open(f"{ROOT}/public/guias/como-escribirle-a-un-coach/index.html", encoding="utf-8").read()
style = re.search(r"<style>.*?</style>", tpl, re.S).group(0)
footer = re.search(r"<footer>.*?</footer>", tpl, re.S).group(0)
POSTS = sorted(json.load(open(f"{ROOT}/scripts/blog_posts.json", encoding="utf-8")), key=lambda p: p["date"], reverse=True)
esc = html.escape
MES = ["enero","febrero","marzo","abril","mayo","junio","julio","agosto","septiembre","octubre","noviembre","diciembre"]
def fdate(d):
    y, m, dd = map(int, d.split("-")); return f"{dd} de {MES[m-1]} de {y}"
FONTS = '<link rel="icon" href="/favicon.ico" sizes="any" />\n<link rel="apple-touch-icon" href="/apple-touch-icon.png" />\n<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700&family=Source+Sans+3:wght@400;600&display=swap" rel="stylesheet">'
def head(title, desc, url, typ, alt=""):
    return f'''<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} | Smartrecruit</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{url}">
{alt}<meta property="og:title" content="{esc(title)} | Smartrecruit">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:type" content="{typ}">
<meta property="og:locale" content="es_AR">
<meta name="theme-color" content="#0b2a6b">
{FONTS}
{style}
'''
EN = json.load(open(f"{ROOT}/scripts/blog_posts_en.json", encoding="utf-8"))
EN_BY_ES = {e["es"]: e["slug"] for e in EN}
def alt(es_url, en_url):
    if not en_url: return ""
    return f'<link rel="alternate" hreflang="es" href="{es_url}"><link rel="alternate" hreflang="en" href="{en_url}"><link rel="alternate" hreflang="x-default" href="{es_url}">\n'
HEADER = '<header><div class="in"><a class="brand" href="/">Smartrecruit</a><a class="cta" href="/">Armá tu perfil gratis</a></div></header>'
for p in POSTS:
    url = f"{BASE}/blog/{p['slug']}/"
    faq_ld = {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"<[^>]+>", "", a)}} for q, a in p["faq"]]}
    art = {"@type": "BlogPosting", "headline": p["h1"], "description": p["desc"], "inLanguage": "es-AR", "datePublished": p["date"], "dateModified": p.get("modified", p["date"]),
           "author": {"@type": "Organization", "name": "Smartrecruit"}, "publisher": {"@type": "Organization", "name": "Smartrecruit", "url": BASE}, "mainEntityOfPage": url}
    ld = json.dumps([dict({"@context": "https://schema.org"}, **art), dict({"@context": "https://schema.org"}, **faq_ld)], ensure_ascii=False)
    others = "".join(f'<li><a href="/blog/{o["slug"]}/">{esc(o["h1"])}</a></li>' for o in POSTS if o["slug"] != p["slug"])
    faq = "".join(f"<h3>{esc(q)}</h3><p>{a}</p>" for q, a in p["faq"])
    d = f"{ROOT}/public/blog/{p['slug']}"; os.makedirs(d, exist_ok=True)
    open(f"{d}/index.html", "w", encoding="utf-8").write(head(p["title"], p["desc"], url, "article", alt(url, EN_BY_ES.get(p["slug"]) and f"{BASE}/en/blog/{EN_BY_ES[p['slug']]}/")) + f'''<script type="application/ld+json">{ld}</script>
<script defer src="/assets/analytics.js"></script>
</head>
<body>
{HEADER}
<main>
<div class="crumb"><a href="/">Inicio</a> › <a href="/blog/">Blog</a> › {esc(p['h1'])}</div>
<h1>{esc(p['h1'])}</h1>
<p class="upd">Publicado el {fdate(p['date'])}</p>
<p class="lead">{p['lead']}</p>
{p['body']}
<h2>Preguntas frecuentes</h2>
{faq}
<div class="box"><b>Hacelo por tu cuenta, gratis, con Smartrecruit:</b> armá tu perfil, mirá qué universidades encajan con vos, conseguí los contactos de los coaches y generá el mail en inglés en minutos. <a href="/">Empezar ahora →</a></div>
<div class="next"><b>Más del blog</b><ul>{others}<li><a href="/guias/">Todas las guías</a></li></ul></div>
</main>
{footer}
</body>
</html>
''')
lst = "".join(f'<li><a href="/blog/{p["slug"]}/">{esc(p["h1"])}</a> <small>({fdate(p["date"])})</small> — {esc(p["desc"])}</li>' for p in POSTS)
os.makedirs(f"{ROOT}/public/blog", exist_ok=True)
open(f"{ROOT}/public/blog/index.html", "w", encoding="utf-8").write(head("Blog: becas deportivas en EE.UU., datos y novedades", "Datos propios, cambios de reglas y calendarios para atletas que buscan una beca deportiva en Estados Unidos por su cuenta.", f"{BASE}/blog/", "website", alt(f"{BASE}/blog/", f"{BASE}/en/blog/")) + f'''<script defer src="/assets/analytics.js"></script></head>
<body>
{HEADER}
<main><div class="crumb"><a href="/">Inicio</a> › Blog</div>
<h1>Blog de Smartrecruit</h1>
<p class="lead"><b>Datos propios, cambios de reglas y calendarios para conseguir una beca deportiva en Estados Unidos por tu cuenta.</b> Para guías paso a paso, mirá las <a href="/guias/">guías</a>.</p>
<ul>{lst}</ul>
</main>{footer}</body></html>
''')

# ---- English blog ----
ES_BY_SLUG = {p["slug"]: p for p in POSTS}
for e in EN:
    e["date"] = ES_BY_SLUG[e["es"]]["date"]
EN.sort(key=lambda p: p["date"], reverse=True)
FOOT_EN = '<footer><div class="in">Smartrecruit is a website for getting a U.S. college sports scholarship on your own, for free. It is not an agent or an intermediary, does not guarantee scholarships or admission, and does not charge for its use. It is not affiliated with the NCAA, the NAIA, the NJCAA or any university. Rules change: always confirm with official sources. The Smartrecruit app itself is currently in Spanish.</div></footer>'
HEADER_EN = '<header><div class="in"><a class="brand" href="/en/">Smartrecruit</a><a class="cta" href="/">Open the app (Spanish)</a></div></header>'
def head_en(title, desc, url, es, typ):
    h = head(title, desc, url, typ, f'<link rel="alternate" hreflang="en" href="{url}"><link rel="alternate" hreflang="es" href="{es}"><link rel="alternate" hreflang="x-default" href="{es}">\n')
    return h.replace('<html lang="es">', '<html lang="en">').replace("es_AR", "en_US")
def fdate_en(d): return datetime.date.fromisoformat(d).strftime("%B %d, %Y").replace(" 0", " ")
for p in EN:
    url = f"{BASE}/en/blog/{p['slug']}/"; es = f"{BASE}/blog/{p['es']}/"
    faq_ld = {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"<[^>]+>", "", a)}} for q, a in p["faq"]]}
    art = {"@type": "BlogPosting", "headline": p["h1"], "description": p["desc"], "inLanguage": "en", "datePublished": p["date"], "dateModified": p["date"],
           "author": {"@type": "Organization", "name": "Smartrecruit"}, "publisher": {"@type": "Organization", "name": "Smartrecruit", "url": BASE}, "mainEntityOfPage": url}
    ld = json.dumps([dict({"@context": "https://schema.org"}, **art), dict({"@context": "https://schema.org"}, **faq_ld)], ensure_ascii=False)
    others = "".join(f'<li><a href="/en/blog/{o["slug"]}/">{esc(o["h1"])}</a></li>' for o in EN if o["slug"] != p["slug"])
    faq = "".join(f"<h3>{esc(q)}</h3><p>{a}</p>" for q, a in p["faq"])
    d = f"{ROOT}/public/en/blog/{p['slug']}"; os.makedirs(d, exist_ok=True)
    open(f"{d}/index.html", "w", encoding="utf-8").write(head_en(p["title"], p["desc"], url, es, "article") + f'''<script type="application/ld+json">{ld}</script>
<script defer src="/assets/analytics.js"></script>
</head>
<body>
{HEADER_EN}
<main>
<div class="crumb"><a href="/en/">Home</a> › <a href="/en/blog/">Blog</a> › {esc(p['h1'])}</div>
<h1>{esc(p['h1'])}</h1>
<p class="upd">Published {fdate_en(p['date'])}</p>
<p class="lead">{p['lead']}</p>
{p['body']}
<h2>Frequently asked questions</h2>
{faq}
<div class="box"><b>Do it yourself, for free, with Smartrecruit:</b> build your profile, see which universities fit you, get the coaches' contacts and generate the email in English in minutes. The app itself is currently in Spanish. <a href="/en/">Learn more →</a></div>
<div class="next"><b>More from the blog</b><ul>{others}<li><a href="/en/guides/">All guides</a></li></ul></div>
</main>
{FOOT_EN}
</body>
</html>
''')
lst = "".join(f'<li><a href="/en/blog/{p["slug"]}/">{esc(p["h1"])}</a> <small>({fdate_en(p["date"])})</small> — {esc(p["desc"])}</li>' for p in EN)
os.makedirs(f"{ROOT}/public/en/blog", exist_ok=True)
open(f"{ROOT}/public/en/blog/index.html", "w", encoding="utf-8").write(head_en("Blog: U.S. college sports scholarships, data and news", "Original data, rule changes and calendars for athletes pursuing a U.S. college sports scholarship on their own.", f"{BASE}/en/blog/", f"{BASE}/blog/", "website") + f'''<script defer src="/assets/analytics.js"></script></head>
<body>
{HEADER_EN}
<main><div class="crumb"><a href="/en/">Home</a> › Blog</div>
<h1>Smartrecruit blog</h1>
<p class="lead"><b>Original data, rule changes and calendars to get a U.S. college sports scholarship on your own.</b> For step-by-step help, see the <a href="/en/guides/">guides</a>.</p>
<ul>{lst}</ul>
</main>{FOOT_EN}</body></html>
''')
sp = f"{ROOT}/public/sitemap.xml"; sm = open(sp, encoding="utf-8").read()
sm = re.sub(r"\s*<url><loc>[^<]*/blog/[^<]*</loc>.*?</url>", "", sm)
urls = [("/blog/", TODAY)] + [(f"/blog/{p['slug']}/", p["date"]) for p in POSTS] + [("/en/blog/", TODAY)] + [(f"/en/blog/{p['slug']}/", p["date"]) for p in EN]
sm = sm.replace("</urlset>", "".join(f"  <url><loc>{BASE}{u}</loc><lastmod>{d}</lastmod></url>\n" for u, d in urls) + "</urlset>")
open(sp, "w", encoding="utf-8").write(sm)
lp = f"{ROOT}/public/llms.txt"; l = open(lp, encoding="utf-8").read().split("\n## Blog")[0].rstrip("\n")
l += "\n\n## Blog (datos propios y novedades)\n- [Blog](https://smartrecruit.com.ar/blog/)\n" + "".join(f"- [{p['h1']}]({BASE}/blog/{p['slug']}/)\n" for p in POSTS) + "\n## Blog (English)\n- [Blog](https://smartrecruit.com.ar/en/blog/)\n" + "".join(f"- [{p['h1']}]({BASE}/en/blog/{p['slug']}/)\n" for p in EN)
open(lp, "w", encoding="utf-8").write(l)
print("posts:", len(POSTS))
