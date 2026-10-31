#!/usr/bin/env python3
"""Genera páginas de guías estáticas (SEO) con la misma plantilla que las existentes, y actualiza guías/index y sitemap."""
import re, json, html, datetime, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TODAY = os.environ.get("SEO_DATE", datetime.date.today().isoformat())
tpl = open(f"{ROOT}/public/guias/como-escribirle-a-un-coach/index.html", encoding="utf-8").read()
style = re.search(r"<style>.*?</style>", tpl, re.S).group(0)
footer = re.search(r"<footer>.*?</footer>", tpl, re.S).group(0)
BASE = "https://smartrecruit.com.ar"
PAGES = json.load(open(f"{ROOT}/scripts/seo_pages.json", encoding="utf-8"))
esc = html.escape
def page(p):
    url = f"{BASE}/guias/{p['slug']}/"
    faq_ld = {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"<[^>]+>", "", a)}} for q, a in p["faq"]]}
    art = {"@type": "Article", "headline": p["h1"], "description": p["desc"], "inLanguage": "es-AR", "datePublished": p.get("published", TODAY), "dateModified": TODAY,
           "author": {"@type": "Organization", "name": "Smartrecruit"}, "publisher": {"@type": "Organization", "name": "Smartrecruit", "url": BASE}, "mainEntityOfPage": url}
    ld = json.dumps([dict({"@context": "https://schema.org"}, **art), dict({"@context": "https://schema.org"}, **faq_ld)], ensure_ascii=False)
    others = "".join(f'<li><a href="/guias/{o["slug"]}/">{esc(o["h1"])}</a></li>' for o in PAGES if o["slug"] != p["slug"])
    base_links = "".join(f'<li><a href="/guias/{s}/">{t}</a></li>' for s, t in EXISTING)
    faq_html = "".join(f"<h3>{esc(q)}</h3><p>{a}</p>" for q, a in p["faq"])
    return f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(p['title'])} | Smartrecruit</title>
<meta name="description" content="{esc(p['desc'])}">
<link rel="canonical" href="{url}">
<meta property="og:title" content="{esc(p['title'])} | Smartrecruit">
<meta property="og:description" content="{esc(p['desc'])}">
<meta property="og:url" content="{url}">
<meta property="og:type" content="article">
<meta property="og:locale" content="es_AR">
<meta name="theme-color" content="#0b2a6b">
<link rel="icon" href="/favicon.ico" sizes="any" />
<link rel="icon" type="image/png" sizes="48x48" href="/favicon-48.png" />
<link rel="icon" type="image/png" sizes="192x192" href="/icon-192.png" />
<link rel="apple-touch-icon" href="/apple-touch-icon.png" />
<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700&family=Source+Sans+3:wght@400;600&display=swap" rel="stylesheet">
{style}
<script type="application/ld+json">{ld}</script>
<script defer src="/assets/analytics.js"></script>
</head>
<body>
<header><div class="in"><a class="brand" href="/">Smartrecruit</a><a class="cta" href="/">Armá tu perfil gratis</a></div></header>
<main>
<div class="crumb"><a href="/">Inicio</a> › <a href="/guias/">Guías</a> › {esc(p['h1'])}</div>
<h1>{esc(p['h1'])}</h1>
<p class="upd">Actualizado: {datetime.date.fromisoformat(TODAY).strftime('%d/%m/%Y')}</p>
<p class="lead">{p['lead']}</p>
{p['body']}
<h2>Preguntas frecuentes</h2>
{faq_html}
<div class="box"><b>Hacelo por tu cuenta, gratis, con Smartrecruit:</b> armá tu perfil, mirá qué universidades encajan con vos, conseguí los contactos de los coaches y generá el mail en inglés en minutos. <a href="/">Empezar ahora →</a></div>
<div class="next"><b>Otras guías</b><ul>{base_links}{others}</ul></div>
</main>
{footer}
</body>
</html>
"""
EXISTING = [("elegibilidad-ncaa-latinoamerica", "Cómo registrarte en el NCAA Eligibility Center desde Latinoamérica"), ("cuanto-cubre-una-beca-deportiva", "¿Cuánto cubre una beca deportiva en Estados Unidos?"), ("video-highlight-universidades", "Cómo hacer un video highlight para universidades de Estados Unidos"), ("como-escribirle-a-un-coach", "Cómo escribirle a un coach universitario de Estados Unidos")]
for p in PAGES:
    d = f"{ROOT}/public/guias/{p['slug']}"; os.makedirs(d, exist_ok=True)
    open(f"{d}/index.html", "w", encoding="utf-8").write(page(p))
# guías/index: agregar las nuevas
idx_p = f"{ROOT}/public/guias/index.html"; idx = open(idx_p, encoding="utf-8").read()
main_list = re.search(r'(<p class="lead">.*?<ul>)(.*?)(</ul>)', idx, re.S)
other_list = re.search(r'(<div class="next"><b>Otras guías</b><ul>)(.*?)(</ul>)', idx, re.S)
for p in PAGES:
    href = f'href="/guias/{p["slug"]}/"'
    idx_main = re.search(r'(<p class="lead">.*?<ul>)(.*?)(</ul>)', idx, re.S)
    if href not in idx_main.group(2):
        idx = idx[:idx_main.end(2)] + f'<li><a {href}>{esc(p["h1"])}</a> — {esc(p["desc"])}</li>' + idx[idx_main.end(2):]
    idx_other = re.search(r'(<div class="next"><b>Otras guías</b><ul>)(.*?)(</ul>)', idx, re.S)
    if href not in idx_other.group(2):
        idx = idx[:idx_other.end(2)] + f'<li><a {href}>{esc(p["h1"])}</a></li>' + idx[idx_other.end(2):]
open(idx_p, "w", encoding="utf-8").write(idx)
# sitemap
urls = ["/", "/guias/"] + [f"/guias/{s}/" for s, _ in EXISTING] + [f"/guias/{p['slug']}/" for p in PAGES]
sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f"  <url><loc>{BASE}{u}</loc><lastmod>{TODAY}</lastmod></url>\n" for u in urls) + "</urlset>\n"
open(f"{ROOT}/public/sitemap.xml", "w", encoding="utf-8").write(sm)
print("páginas:", len(PAGES), "urls en sitemap:", len(urls))
