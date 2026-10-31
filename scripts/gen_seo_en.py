#!/usr/bin/env python3
"""English content: /en/ home, /en/guides/*, hreflang on the Spanish counterparts, sitemap and llms.txt additions. Run after gen_seo.py."""
import re, json, html, datetime, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TODAY = os.environ.get("SEO_DATE", datetime.date.today().isoformat())
BASE = "https://smartrecruit.com.ar"
tpl = open(f"{ROOT}/public/guias/como-escribirle-a-un-coach/index.html", encoding="utf-8").read()
style = re.search(r"<style>.*?</style>", tpl, re.S).group(0)
PAGES = json.load(open(f"{ROOT}/scripts/seo_pages_en.json", encoding="utf-8"))
esc = html.escape
FOOT = '<footer><div class="in">Smartrecruit is a website for getting a U.S. college sports scholarship on your own, for free. It is not an agent or an intermediary, does not guarantee scholarships or admission, and does not charge for its use. It is not affiliated with the NCAA, the NAIA, the NJCAA or any university. Rules change: always confirm with official sources. The Smartrecruit app itself is currently in Spanish.</div></footer>'
FONTS = '<link rel="icon" href="/favicon.ico" sizes="any" />\n<link rel="icon" type="image/png" sizes="48x48" href="/favicon-48.png" />\n<link rel="icon" type="image/png" sizes="192x192" href="/icon-192.png" />\n<link rel="apple-touch-icon" href="/apple-touch-icon.png" />\n<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700&family=Source+Sans+3:wght@400;600&display=swap" rel="stylesheet">'
HEADER = '<header><div class="in"><a class="brand" href="/en/">Smartrecruit</a><a class="cta" href="/">Open the app (Spanish)</a></div></header>'
def head(title, desc, url, es, typ):
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} | Smartrecruit</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{url}">
<link rel="alternate" hreflang="en" href="{url}"><link rel="alternate" hreflang="es" href="{es}"><link rel="alternate" hreflang="x-default" href="{es}">
<meta property="og:title" content="{esc(title)} | Smartrecruit">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:type" content="{typ}">
<meta property="og:locale" content="en_US">
<meta name="theme-color" content="#0b2a6b">
{FONTS}
{style}
'''
def guide(p):
    url = f"{BASE}/en/guides/{p['slug']}/"; es = f"{BASE}/guias/{p['es']}/"
    faq_ld = {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"<[^>]+>", "", a)}} for q, a in p["faq"]]}
    art = {"@type": "Article", "headline": p["h1"], "description": p["desc"], "inLanguage": "en", "datePublished": TODAY, "dateModified": TODAY,
           "author": {"@type": "Organization", "name": "Smartrecruit"}, "publisher": {"@type": "Organization", "name": "Smartrecruit", "url": BASE}, "mainEntityOfPage": url}
    ld = json.dumps([dict({"@context": "https://schema.org"}, **art), dict({"@context": "https://schema.org"}, **faq_ld)], ensure_ascii=False)
    others = "".join(f'<li><a href="/en/guides/{o["slug"]}/">{esc(o["h1"])}</a></li>' for o in PAGES if o["slug"] != p["slug"])
    faq = "".join(f"<h3>{esc(q)}</h3><p>{a}</p>" for q, a in p["faq"])
    d = datetime.date.fromisoformat(TODAY).strftime("%B %d, %Y")
    return head(p["title"] + "", p["desc"], url, es, "article") + f'''<script type="application/ld+json">{ld}</script>
<script defer src="/assets/analytics.js"></script>
</head>
<body>
{HEADER}
<main>
<div class="crumb"><a href="/en/">Home</a> › <a href="/en/guides/">Guides</a> › {esc(p['h1'])}</div>
<h1>{esc(p['h1'])}</h1>
<p class="upd">Updated: {d}</p>
<p class="lead">{p['lead']}</p>
{p['body']}
<h2>Frequently asked questions</h2>
{faq}
<div class="box"><b>Do it yourself, for free, with Smartrecruit:</b> build your profile, see which universities fit you, get the coaches' contacts and generate the email in English in minutes. The app itself is currently in Spanish. <a href="/en/">Learn more →</a></div>
<div class="next"><b>More guides</b><ul>{others}</ul></div>
</main>
{FOOT}
</body>
</html>
'''
for p in PAGES:
    d = f"{ROOT}/public/en/guides/{p['slug']}"; os.makedirs(d, exist_ok=True)
    open(f"{d}/index.html", "w", encoding="utf-8").write(guide(p))
# guides index
url = f"{BASE}/en/guides/"; es = f"{BASE}/guias/"
lst = "".join(f'<li><a href="/en/guides/{p["slug"]}/">{esc(p["h1"])}</a> — {esc(p["desc"])}</li>' for p in PAGES)
open(f"{ROOT}/public/en/guides/index.html", "w", encoding="utf-8").write(head("Free guides: U.S. college sports scholarships for international athletes", "Free guides on NCAA and NAIA eligibility, scholarship coverage, recruiting emails, highlight videos and sport-by-sport paths for international athletes.", url, es, "website") + f'''<script defer src="/assets/analytics.js"></script></head>
<body>
{HEADER}
<main><div class="crumb"><a href="/en/">Home</a> › Guides</div>
<h1>Free guides for international athletes</h1>
<p class="lead"><b>Everything you need to pursue a U.S. college sports scholarship on your own.</b> Written for athletes from outside the United States, especially Latin America.</p>
<ul>{lst}</ul>
<p>Looking for a specific school? Browse the <a href="/en/universities/">U.S. universities directory</a>.</p>
</main>{FOOT}</body></html>
''')
# English home
hurl = f"{BASE}/en/"; hes = f"{BASE}/"
ld = json.dumps([{"@context": "https://schema.org", "@type": "WebSite", "name": "Smartrecruit", "url": hurl, "inLanguage": "en"},
  {"@context": "https://schema.org", "@type": "Organization", "name": "Smartrecruit", "url": BASE, "logo": f"{BASE}/icon-512.png", "description": "A website for getting a U.S. college sports scholarship on your own, for free. Built for athletes in Argentina and Latin America. Not an agency."}], ensure_ascii=False)
cards = "".join(f'<li><a href="/en/guides/{p["slug"]}/">{esc(p["h1"])}</a></li>' for p in PAGES)
os.makedirs(f"{ROOT}/public/en", exist_ok=True)
open(f"{ROOT}/public/en/index.html", "w", encoding="utf-8").write(head("Get a U.S. college sports scholarship on your own, for free", "Smartrecruit helps athletes from Argentina and Latin America pursue a U.S. college sports scholarship without an agency: universities, official coach emails, open searches and free guides.", hurl, hes, "website") + f'''<script type="application/ld+json">{ld}</script>
<script defer src="/assets/analytics.js"></script></head>
<body>
{HEADER}
<main>
<h1>Get a U.S. college sports scholarship on your own, for free</h1>
<p class="lead"><b>Smartrecruit is a website for pursuing a college sports scholarship in the United States without an agency.</b> It shows which universities recruit your position, the official emails of their coaches and the searches coaches have posted, and it helps you write to them in English.</p>
<div class="box"><b>Language note:</b> the Smartrecruit app (profile, university matching, coach contacts and email generator) is currently in Spanish. The emails it generates for coaches are always in English. These guides and the university directory are in English.</div>
<h2>What it is, and what it is not</h2>
<p>It is a free tool and a set of guides for athletes in NCAA, NAIA and NJCAA recruiting, covering soccer, basketball, volleyball, softball, field hockey, rugby and more. It is not an agency or an intermediary, it does not guarantee scholarships or admission, it does not charge for its use, and it is not affiliated with the NCAA, the NAIA, the NJCAA or any university.</p>
<h2>Start here</h2>
<ul>{cards}</ul>
<p>Browse the <a href="/en/universities/">U.S. universities directory</a> for sports, athletic aid, cost and admission data for each school, or <a href="/">open the app</a>.</p>
</main>{FOOT}</body></html>
''')
# hreflang on Spanish counterparts (idempotent)
def patch(path, es_url, en_url):
    if not os.path.exists(path): return
    t = open(path, encoding="utf-8").read()
    t = re.sub(r'<link rel="alternate" hreflang="[^"]*" href="[^"]*">', "", t)
    tag = f'<link rel="alternate" hreflang="es" href="{es_url}"><link rel="alternate" hreflang="en" href="{en_url}"><link rel="alternate" hreflang="x-default" href="{es_url}">'
    m = re.search(r'<link rel="canonical" href="%s"\s*/?>' % re.escape(es_url), t)
    t2 = t[:m.end()] + "\n" + tag + t[m.end():] if m else t
    if t2 != t or tag in t2: open(path, "w", encoding="utf-8").write(t2)
for p in PAGES:
    patch(f"{ROOT}/public/guias/{p['es']}/index.html", f"{BASE}/guias/{p['es']}/", f"{BASE}/en/guides/{p['slug']}/")
patch(f"{ROOT}/public/guias/index.html", f"{BASE}/guias/", f"{BASE}/en/guides/")
patch(f"{ROOT}/public/index.html", f"{BASE}/", f"{BASE}/en/")
# sitemap
sp = f"{ROOT}/public/sitemap.xml"; sm = open(sp, encoding="utf-8").read()
sm = re.sub(r"\s*<url><loc>[^<]*/en/[^<]*</loc>.*?</url>", "", sm)
urls = ["/en/", "/en/guides/"] + [f"/en/guides/{p['slug']}/" for p in PAGES]
sm = sm.replace("</urlset>", "".join(f"  <url><loc>{BASE}{u}</loc><lastmod>{TODAY}</lastmod></url>\n" for u in urls) + "</urlset>")
open(sp, "w", encoding="utf-8").write(sm)
# llms.txt
lp = f"{ROOT}/public/llms.txt"; l = open(lp, encoding="utf-8").read().split("\n## English")[0].rstrip("\n")
l += "\n\n## English\n- [Home (English)](https://smartrecruit.com.ar/en/)\n- [Guides](https://smartrecruit.com.ar/en/guides/)\n" + "".join(f"- [{p['h1']}]({BASE}/en/guides/{p['slug']}/)\n" for p in PAGES) + "- [U.S. universities directory](https://smartrecruit.com.ar/en/universities/)\n- Note: the app is currently in Spanish; guides and the university directory are available in English.\n"
open(lp, "w", encoding="utf-8").write(l)
print("en pages:", len(PAGES), "sitemap en urls:", len(urls))
