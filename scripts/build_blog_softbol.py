#!/usr/bin/env python3
"""Nota de blog de softbol (es + en). Calcula las cifras desde datos/FIELDLEVEL_NEEDS.json y las agrega (idempotente)
a scripts/blog_posts.json y scripts/blog_posts_en.json. Después correr gen_blog.py y gen_softbol.py."""
import json, os, re, datetime
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rows = [x for x in json.load(open(f"{ROOT}/datos/FIELDLEVEL_NEEDS.json", encoding="utf-8")) if "softball" in str(x.get("sport", "")).lower()]
SNAP = datetime.datetime.strptime(re.search(r'NEEDS_SNAPSHOT_AT\s*=\s*"([^"]+)"', open(f"{ROOT}/RosterReal.jsx", encoding="utf-8").read()).group(1), "%Y-%m-%dT%H:%M:%SZ")
_RO = json.load(open(f"{ROOT}/datos/SOFTBALL_ROSTERS.json", encoding="utf-8"))
RO_N = len(_RO); RO_I = sum(len(v.get('intl', [])) for v in _RO.values()); RO_P = sum(1 for v in _RO.values() if v.get('intl'))
N = len(rows); U = len(set(x["university"] for x in rows))
def cnt(f):
    c = {}
    for x in rows: c[f(x)] = c.get(f(x), 0) + 1
    return c
DIV = ["NCAA D1", "NCAA D2", "NCAA D3", "NAIA", "NJCAA D1", "NJCAA D2", "NJCAA D3", "CCCAA", "NWAC", "NCCAA", "USCAA"]
dv = cnt(lambda x: x["division"])
GROUP = {"P": "P", "C": "C", "1B": "IF", "2B": "IF", "3B": "IF", "SS": "IF", "INF": "IF", "OF": "OF", "LF": "OF", "CF": "OF", "RF": "OF"}
pg = cnt(lambda x: GROUP.get(x.get("position_code"), "?"))
yr = cnt(lambda x: x.get("class_year_needed"))
pct = lambda n: f"{100 * n / N:.0f}%".replace(".", ",")
pct_en = lambda n: f"{100 * n / N:.0f}%"
juco = sum(dv.get(d, 0) for d in ["NJCAA D1", "NJCAA D2", "NJCAA D3", "CCCAA", "NWAC"])
T = lambda *r: "<table><tr>" + "".join(f"<th>{c}</th>" for c in r[0]) + "</tr>" + "".join("<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>" for row in r[1:]) + "</table>"
W = lambda t: f'<div class="wrap">{t}</div>'
fecha_es = SNAP.strftime("%d/%m/%Y"); fecha_en = SNAP.strftime("%B %d, %Y").replace(" 0", " ")
A = lambda u, t: f'<a href="{u}" rel="noopener" target="_blank">{t}</a>'
SRC = dict(
  wiki_d1=("https://en.wikipedia.org/wiki/2026_NCAA_Division_I_softball_tournament", "Wikipedia: 2026 NCAA Division I softball tournament"),
  si=("https://www.si.com/onsi/softball/college/when-the-2026-college-softball-season-starts", "Sports Illustrated: when the 2026 college softball season starts"),
  dpr=("https://www.diamondplayersrecruits.com/post/big-changes-in-2025-26-division-1-baseball-and-softball-scholarship-rules", "Diamond Players Recruits: 2025-26 Division I rule changes"),
  nc=("https://www.nextcommit.ai/blog/how-to-get-recruited-for-college-softball", "NextCommit: how to get recruited for college softball"),
  naia=("https://en.wikipedia.org/wiki/2026_NAIA_softball_tournament", "Wikipedia: 2026 NAIA softball tournament"),
  njcaa=("https://en.wikipedia.org/wiki/National_Junior_College_Athletic_Association", "Wikipedia: NJCAA"))
src_li = lambda: "<ul>" + "".join(f"<li>{A(*v)}</li>" for v in SRC.values()) + "</ul>"

# ---------------- ES ----------------
tabla_div = lambda lab: W(T(lab, *[[d, str(dv[d]), pct(dv[d])] for d in DIV if d in dv]))
es = dict(
 slug="softbol-universitario-eeuu-divisiones-becas-calendario", date=SNAP.strftime("%Y-%m-%d") if False else "2026-11-03",
 title="Softbol universitario en EE.UU.: divisiones, becas, calendario y campeonatos",
 h1="Cómo funciona el softbol universitario en EE.UU.: divisiones, becas, calendario y campeonatos",
 desc=f"Qué diferencia hay entre NCAA, NAIA y junior colleges en softbol femenino, cuánto cubre cada beca, cuándo se juega, cómo son los campeonatos y qué buscan hoy {N} búsquedas abiertas de coaches.",
 lead=f"<b>El softbol universitario se reparte entre la NCAA (tres divisiones), la NAIA y la NJCAA (junior colleges, también con tres divisiones), y las becas cambian mucho según el nivel.</b> En las {N} búsquedas abiertas que relevamos al {fecha_es}, {pct(juco)} son de junior colleges: ahí hay más lugar para una jugadora de afuera.",
 faq=[
  ["¿Los junior colleges tienen Division I, II y III?", "Sí. La NJCAA tiene sus propias divisiones I, II y III, independientes de las de la NCAA. En la D1 se pueden dar becas completas, en la D2 cubren matrícula, tasas y libros pero no alojamiento, y en la D3 no hay becas deportivas."],
  ["¿Cuántas becas tiene un equipo de softbol?", "En la NCAA Division I, desde 2025-26 no hay tope de becas sino un límite de 25 jugadoras por plantel; en la D2 el máximo es de 7,2 equivalencias; en la D3 no hay becas deportivas. La NAIA y la NJCAA tienen sus reglas: confirmalas en sus sitios oficiales."],
  ["¿Cuándo empieza la temporada de softbol universitario?", "En 2026 empezó el 23 de enero en la NJCAA, el 30 de enero en NCAA D2, el 5 de febrero en D1, el 6 de febrero en la NAIA y el 13 de febrero en D3. Los programas de clima frío arrancan más tarde."]],
 body=f"""<h2>Quién organiza qué</h2>
<p>El softbol universitario femenino lo organizan varias asociaciones. La <b>NCAA</b> tiene tres divisiones: la I es la más visible y competitiva, la II tiene becas parciales y la III no da becas deportivas. La <b>NAIA</b> es otra asociación, con campeonato propio. La <b>NJCAA</b> agrupa a los junior colleges, instituciones de dos años que también se dividen en D1, D2 y D3: son divisiones propias, no equivalen a las de la NCAA. En California (CCCAA) y en el noroeste (NWAC) los junior colleges tienen asociaciones distintas.</p>
<h2>Becas por nivel</h2>
{W(T(["Nivel", "Qué puede ofrecer", "Fuente"],
 ["NCAA D1", "Desde 2025-26 no hay tope de becas: hay un límite de 25 jugadoras por plantel y cada universidad decide cuánto ofrecer. Sigue siendo un deporte de equivalencias, o sea que hay becas parciales.", A(*SRC["dpr"])],
 ["NCAA D2", "Hasta 7,2 equivalencias de beca por equipo, que el coach reparte en porciones.", "Reglas de la NCAA (ver nuestra nota sobre House v. NCAA)"],
 ["NCAA D3", "Sin becas deportivas; hay ayuda académica o por necesidad.", "Reglas de la NCAA"],
 ["NAIA", "Hasta 10 equivalencias, según una fuente de reclutamiento. Confirmalo en naia.org.", A(*SRC["nc"])],
 ["NJCAA D1", "Becas deportivas completas: matrícula, tasas, alojamiento y comida, libros, hasta 250 dólares en materiales y un viaje de ida y vuelta por año. Una fuente de reclutamiento menciona un tope de 24 becas en softbol: confirmalo en njcaa.org.", A(*SRC["njcaa"]) + " y " + A(*SRC["nc"])],
 ["NJCAA D2", "Matrícula, tasas, libros y hasta 250 dólares en materiales, pero no alojamiento ni comida.", A(*SRC["njcaa"])],
 ["NJCAA D3", "No puede dar ayuda económica por deporte.", A(*SRC["njcaa"])]))}
<p>Las reglas cambian cada año: usá esta tabla para orientarte y confirmá siempre en los sitios oficiales. Para el detalle de la D1 leé <a href="/blog/house-v-ncaa-becas-limites-de-plantel/">House v. NCAA</a>.</p>
<h2>Calendario de la temporada</h2>
<p>La temporada se juega principalmente entre enero y mayo. En 2026 ({A(*SRC["si"])}):</p>
{W(T(["Nivel", "Inicio de temporada 2026"], ["NJCAA", "23 de enero"], ["NCAA D2", "30 de enero"], ["NCAA D1", "5 de febrero"], ["NAIA", "6 de febrero"], ["NCAA D3", "13 de febrero"]))}
<p>Los programas de climas fríos suelen empezar más tarde. Muchos programas también juegan partidos de preparación en otoño (fall ball); las fechas varían por programa y no las verificamos.</p>
<h2>Campeonatos: así terminó la temporada 2026</h2>
<ul>
<li><b>NCAA Division I:</b> torneo de 64 equipos (31 por ganar su conferencia y 33 por selección del comité). Regionales del 15 al 17 de mayo, súper regionales del 21 al 24 y Women's College World Series del 28 de mayo al 4 de junio en Oklahoma City. Campeón: Texas, que venció a Texas Tech 7-3 y 4-1 en la final. {A(*SRC["wiki_d1"])}.</li>
<li><b>NAIA:</b> 48 equipos. Primera ronda en 10 sedes del 11 al 15 de mayo, con doble eliminación, y Serie Mundial del 21 al 28 de mayo en Columbus, Georgia. Campeón: Madonna (Michigan), que venció a Southeastern (Florida) 8-4. {A(*SRC["naia"])}.</li>
<li><b>NJCAA y NCAA D2/D3:</b> también tienen campeonatos nacionales, pero no pudimos confirmar el formato y no lo detallamos.</li>
</ul>
<h2>Cómo es el reclutamiento</h2>
<p>En la D1, los coaches pueden empezar a contactar a las jugadoras el 1 de septiembre del tercer año de secundaria (junior year), según nuestra nota sobre <a href="/blog/cuando-pueden-escribirte-los-coaches-fechas-ncaa-por-deporte/">fechas de contacto</a>. En la D2 pueden contactar en cualquier momento por teléfono, mensaje o mail, y la NAIA y los junior colleges no siguen las fechas de la NCAA. Según {A(*SRC["nc"])}, el período de firma de cartas de beca de D1 y D2 en 2026 es el 11 de noviembre; confirmalo en ncaa.org. Los showcases (PGF Nationals, Triple Crown, Alliance Fastpitch, entre otros) son una vitrina para los coaches. Si terminás el secundario en diciembre, mirá el <a href="/blog/calendario-reclutamiento-secundaria-termina-en-diciembre/">calendario de reclutamiento</a> para ordenar los pasos.</p>
<h2>Qué buscan hoy los coaches: {N} búsquedas abiertas</h2>
<p>Smartrecruit reúne las búsquedas que publican los coaches. Al {fecha_es} había <b>{N} búsquedas de {U} universidades</b>. Esta es la distribución:</p>
{tabla_div(["División", "Búsquedas", "Porcentaje"])}
{W(T(["Posición", "Búsquedas", "Porcentaje"], ["Lanzadora (P)", str(pg.get("P", 0)), pct(pg.get("P", 0))], ["Cuadro (1B, 2B, 3B, SS, INF)", str(pg.get("IF", 0)), pct(pg.get("IF", 0))], ["Jardín (LF, CF, RF, OF)", str(pg.get("OF", 0)), pct(pg.get("OF", 0))], ["Receptora (C)", str(pg.get("C", 0)), pct(pg.get("C", 0))]))}
<p>Por año de egreso, la mayoría busca la <i>class</i> de 2027 ({yr.get(2027, 0)} búsquedas), seguida por 2026 ({yr.get(2026, 0)}), 2028 ({yr.get(2028, 0)}) y 2029 ({yr.get(2029, 0)}). Podés filtrar la lista completa por división, estado, posición y año en <a href="/softball/">búsquedas abiertas de softbol</a>.</p>
<h2>Qué significa para una jugadora de Argentina</h2>
<p>Esta es nuestra lectura de los datos, no una garantía. Tres de cada cuatro búsquedas ({pct(juco + dv.get("NAIA", 0))}) son de junior colleges o de la NAIA, y solo {dv.get("NCAA D1", 0)} son de la D1 de la NCAA: son los niveles que más reclutan en este momento. En la NJCAA D1 hay becas completas, y desde un junior college muchas jugadoras se transfieren después a una universidad de cuatro años. Las lanzadoras y las receptoras suman {pct(pg.get("P", 0) + pg.get("C", 0))} de las búsquedas, aunque cada programa y cada año son distintos. Antes de escribir, revisá la <a href="/guias/beca-softbol-estados-unidos-latinoamericanas/">guía de becas de softbol</a> y la elegibilidad.</p>
<h2>Límites de estos datos</h2>
<p>Son publicaciones de coaches, con días o semanas de antigüedad: el cupo puede estar cubierto. No son todas las vacantes que existen, porque muchos coaches reclutan sin publicar. De los {RO_N} planteles que pudimos leer, {RO_I} jugadoras figuran con hometown fuera de EE.UU. ({RO_P} programas) y ninguna de Argentina ni de Latinoamérica; en los otros programas no pudimos leer el plantel. Las cifras de becas de la NAIA y de la NJCAA D1 vienen en parte de una fuente de reclutamiento y conviene confirmarlas.</p>
<h2>Fuentes</h2>
{src_li()}""")

# ---------------- EN ----------------
en = dict(
 es=es["slug"], slug="how-us-college-softball-works-divisions-scholarships-calendar",
 title="How U.S. college softball works: divisions, scholarships, calendar and championships",
 h1="How U.S. college softball works: divisions, scholarships, calendar and championships",
 desc=f"The difference between NCAA, NAIA and junior colleges in women's softball, what each scholarship covers, when the season is played, how the championships work and what {N} open coach needs show.",
 lead=f"<b>College softball is split between the NCAA (three divisions), the NAIA and the NJCAA (junior colleges, also with three divisions), and scholarships vary a lot by level.</b> Of the {N} open needs we collected as of {fecha_en}, {pct_en(juco)} are from junior colleges, where there is more room for an international player.",
 faq=[
  ["Do junior colleges have Division I, II and III?", "Yes. The NJCAA has its own Divisions I, II and III, separate from the NCAA's. Division I can give full scholarships, Division II covers tuition, fees and books but not room and board, and Division III gives no athletic scholarships."],
  ["How many scholarships does a softball team have?", "In NCAA Division I, since 2025-26 there is no scholarship cap but a roster limit of 25 players; in Division II the maximum is 7.2 equivalencies; Division III gives no athletic scholarships. The NAIA and the NJCAA have their own rules: confirm them on the official sites."],
  ["When does the college softball season start?", "In 2026 it started January 23 in the NJCAA, January 30 in NCAA D2, February 5 in D1, February 6 in the NAIA and February 13 in D3. Cold-weather programs start later."]],
 body=f"""<h2>Who runs what</h2>
<p>Women's college softball is run by several associations. The <b>NCAA</b> has three divisions: Division I is the most visible and competitive, Division II has partial scholarships and Division III gives no athletic scholarships. The <b>NAIA</b> is a separate association with its own championship. The <b>NJCAA</b> groups junior colleges, two-year institutions that are also split into D1, D2 and D3: these are their own divisions and do not match the NCAA's. In California (CCCAA) and the Northwest (NWAC), junior colleges belong to different associations.</p>
<h2>Scholarships by level</h2>
{W(T(["Level", "What it can offer", "Source"],
 ["NCAA D1", "Since 2025-26 there is no scholarship cap: there is a roster limit of 25 players and each school decides how much to offer. It is still an equivalency sport, so partial scholarships exist.", A(*SRC["dpr"])],
 ["NCAA D2", "Up to 7.2 scholarship equivalencies per team, which the coach splits into portions.", "NCAA rules (see our note on House v. NCAA)"],
 ["NCAA D3", "No athletic scholarships; academic or need-based aid is available.", "NCAA rules"],
 ["NAIA", "Up to 10 equivalencies, according to a recruiting source. Confirm at naia.org.", A(*SRC["nc"])],
 ["NJCAA D1", "Full athletic scholarships: tuition, fees, room and board, books, up to $250 in supplies and one round trip per year. A recruiting source mentions a cap of 24 scholarships in softball: confirm at njcaa.org.", A(*SRC["njcaa"]) + " and " + A(*SRC["nc"])],
 ["NJCAA D2", "Tuition, fees, books and up to $250 in supplies, but no room and board.", A(*SRC["njcaa"])],
 ["NJCAA D3", "Cannot give athletic financial aid.", A(*SRC["njcaa"])]))}
<p>Rules change every year: use this table to get oriented and always confirm on the official sites. For Division I details, read <a href="/en/blog/house-v-ncaa-scholarship-caps-roster-limits/">House v. NCAA</a>.</p>
<h2>Season calendar</h2>
<p>The season is played mainly between January and May. In 2026 ({A(*SRC["si"])}):</p>
{W(T(["Level", "2026 season start"], ["NJCAA", "January 23"], ["NCAA D2", "January 30"], ["NCAA D1", "February 5"], ["NAIA", "February 6"], ["NCAA D3", "February 13"]))}
<p>Cold-weather programs usually start later. Many programs also play preparation games in the fall (fall ball); dates vary by program and we did not verify them.</p>
<h2>Championships: how the 2026 season ended</h2>
<ul>
<li><b>NCAA Division I:</b> a 64-team tournament (31 conference champions and 33 committee selections). Regionals May 15 to 17, super regionals May 21 to 24 and the Women's College World Series May 28 to June 4 in Oklahoma City. Champion: Texas, which beat Texas Tech 7-3 and 4-1 in the final. {A(*SRC["wiki_d1"])}.</li>
<li><b>NAIA:</b> 48 teams. Opening round at 10 sites May 11 to 15, double elimination, and a World Series May 21 to 28 in Columbus, Georgia. Champion: Madonna (Michigan), which beat Southeastern (Florida) 8-4. {A(*SRC["naia"])}.</li>
<li><b>NJCAA and NCAA D2/D3:</b> they also hold national championships, but we could not confirm the format and do not detail it.</li>
</ul>
<h2>How recruiting works</h2>
<p>In Division I, coaches can start contacting players on September 1 of junior year, according to our note on <a href="/en/blog/when-ncaa-coaches-can-contact-you-dates-by-sport/">contact dates</a>. In Division II they can contact you at any time by phone, message or email, and the NAIA and junior colleges do not follow NCAA dates. According to {A(*SRC["nc"])}, the 2026 signing date for Division I and II scholarship letters is November 11; confirm it at ncaa.org. Showcases (PGF Nationals, Triple Crown, Alliance Fastpitch, among others) are a window for coaches. If you finish high school in December, see the <a href="/en/blog/recruiting-timeline-finishing-high-school-in-december/">recruiting timeline</a> to order your steps.</p>
<h2>What coaches want today: {N} open needs</h2>
<p>Smartrecruit gathers the needs coaches post. As of {fecha_en} there were <b>{N} needs from {U} colleges</b>. Here is the breakdown:</p>
{tabla_div(["Division", "Needs", "Share"]).replace("%</td></tr>", "%</td></tr>")}
{W(T(["Position", "Needs", "Share"], ["Pitcher (P)", str(pg.get("P", 0)), pct_en(pg.get("P", 0))], ["Infield (1B, 2B, 3B, SS, INF)", str(pg.get("IF", 0)), pct_en(pg.get("IF", 0))], ["Outfield (LF, CF, RF, OF)", str(pg.get("OF", 0)), pct_en(pg.get("OF", 0))], ["Catcher (C)", str(pg.get("C", 0)), pct_en(pg.get("C", 0))]))}
<p>By graduation year, most look for the class of 2027 ({yr.get(2027, 0)} needs), followed by 2026 ({yr.get(2026, 0)}), 2028 ({yr.get(2028, 0)}) and 2029 ({yr.get(2029, 0)}). You can filter the full list by division, state, position and year in <a href="/en/softball/">open softball needs</a>.</p>
<h2>What this means for an international player</h2>
<p>This is our reading of the data, not a guarantee. Three out of four needs ({pct_en(juco + dv.get("NAIA", 0))}) are from junior colleges or the NAIA, and only {dv.get("NCAA D1", 0)} are from NCAA Division I: those are the levels recruiting most right now. NJCAA Division I offers full scholarships, and many players later transfer from a junior college to a four-year school. Pitchers and catchers add up to {pct_en(pg.get("P", 0) + pg.get("C", 0))} of the needs, although every program and year is different. Before writing, read the <a href="/en/guides/">guides</a> and check eligibility.</p>
<h2>Limits of this data</h2>
<p>These are coach posts, days or weeks old: the spot may be filled. They are not every vacancy, because many coaches recruit without posting. Of the {RO_N} rosters we could read, {RO_I} players list a hometown outside the U.S. ({RO_P} programs) and none from Argentina or Latin America; for the other programs we could not read the roster. NAIA and NJCAA Division I scholarship figures come partly from a recruiting source and should be confirmed.</p>
<h2>Sources</h2>
{src_li()}""")

def merge(path, key, post, order_key):
    L = json.load(open(path, encoding="utf-8"))
    L = [p for p in L if p[key] != post[key]]; L.append(post)
    json.dump(L, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return len(L)
print(merge(f"{ROOT}/scripts/blog_posts.json", "slug", es, "date"), merge(f"{ROOT}/scripts/blog_posts_en.json", "slug", en, "date"))
print("N", N, "U", U, dict(dv), dict(pg), dict(yr), "juco", juco, pct(juco))
