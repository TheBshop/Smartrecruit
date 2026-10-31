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
def head(title, desc, url, typ):
    return f'''<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} | Smartrecruit</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:title" content="{esc(title)} | Smartrecruit">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:type" content="{typ}">
<meta property="og:locale" content="es_AR">
<meta name="theme-color" content="#0b2a6b">
{FONTS}
{style}
'''
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
    open(f"{d}/index.html", "w", encoding="utf-8").write(head(p["title"], p["desc"], url, "article") + f'''<script type="application/ld+json">{ld}</script>
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
open(f"{ROOT}/public/blog/index.html", "w", encoding="utf-8").write(head("Blog: becas deportivas en EE.UU., datos y novedades", "Datos propios, cambios de reglas y calendarios para atletas que buscan una beca deportiva en Estados Unidos por su cuenta.", f"{BASE}/blog/", "website") + f'''<script defer src="/assets/analytics.js"></script></head>
<body>
{HEADER}
<main><div class="crumb"><a href="/">Inicio</a> › Blog</div>
<h1>Blog de Smartrecruit</h1>
<p class="lead"><b>Datos propios, cambios de reglas y calendarios para conseguir una beca deportiva en Estados Unidos por tu cuenta.</b> Para guías paso a paso, mirá las <a href="/guias/">guías</a>.</p>
<ul>{lst}</ul>
</main>{footer}</body></html>
''')
sp = f"{ROOT}/public/sitemap.xml"; sm = open(sp, encoding="utf-8").read()
sm = re.sub(r"\s*<url><loc>[^<]*/blog/[^<]*</loc>.*?</url>", "", sm)
urls = [("/blog/", TODAY)] + [(f"/blog/{p['slug']}/", p["date"]) for p in POSTS]
sm = sm.replace("</urlset>", "".join(f"  <url><loc>{BASE}{u}</loc><lastmod>{d}</lastmod></url>\n" for u, d in urls) + "</urlset>")
open(sp, "w", encoding="utf-8").write(sm)
lp = f"{ROOT}/public/llms.txt"; l = open(lp, encoding="utf-8").read().split("\n## Blog")[0].rstrip("\n")
l += "\n\n## Blog (datos propios y novedades)\n- [Blog](https://smartrecruit.com.ar/blog/)\n" + "".join(f"- [{p['h1']}]({BASE}/blog/{p['slug']}/)\n" for p in POSTS)
open(lp, "w", encoding="utf-8").write(l)
print("posts:", len(POSTS))
