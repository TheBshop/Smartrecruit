import os, json, html
BASE="https://smartrecruit.com.ar"
CSS="""
:root{--brand:#0b2a6b;--ink:#0a1633;--muted:#46527a;--line:#d3dae9;--tint:#e3eafb;--raised:#f3f5fa}
*{box-sizing:border-box}html,body{margin:0}body{font-family:"Source Sans 3",system-ui,sans-serif;color:var(--ink);background:#fff;line-height:1.6;font-size:18px}
header{background:var(--brand);color:#fff}header .in,main,footer .in{max-width:760px;margin:0 auto;padding:0 20px}
header .in{display:flex;justify-content:space-between;align-items:center;gap:16px;padding-top:14px;padding-bottom:14px;flex-wrap:wrap}
.brand{font-family:"Barlow Condensed","Arial Narrow",sans-serif;font-weight:700;font-size:28px;color:#fff;text-decoration:none}
.cta{background:#fff;color:var(--brand);font-weight:600;padding:10px 16px;border-radius:4px;text-decoration:none;font-size:16px}
main{padding-top:28px;padding-bottom:48px}
.crumb{font-size:14px;color:var(--muted)}.crumb a{color:var(--muted)}
h1,h2{font-family:"Barlow Condensed","Arial Narrow",sans-serif;line-height:1.05;color:var(--brand)}
h1{font-size:46px;margin:10px 0 12px}h2{font-size:30px;margin:36px 0 8px}h3{font-size:20px;margin:22px 0 4px}
.lead{font-size:20px;color:var(--muted)}.upd{font-size:14px;color:var(--muted)}
a{color:#00266b}table{border-collapse:collapse;width:100%;font-size:16px;margin:12px 0}td,th{border:1px solid var(--line);padding:8px 10px;text-align:left;vertical-align:top}th{background:var(--raised)}
.wrap{overflow-x:auto}.box{background:var(--tint);border-radius:8px;padding:16px 18px;margin:20px 0}
pre{white-space:pre-wrap;background:var(--raised);border:1px solid var(--line);border-radius:8px;padding:16px;font-size:15px;line-height:1.5}
.next{border-top:1px solid var(--line);margin-top:40px;padding-top:16px}.next ul{padding-left:20px}
footer{background:var(--raised);font-size:14px;color:var(--muted)}footer .in{padding-top:20px;padding-bottom:28px}
@media(max-width:600px){h1{font-size:36px}body{font-size:17px}}
"""
GUIDES=[]
def page(slug,title,seo_title,desc,body,faq=None):
    GUIDES.append((slug,title,desc))
    ld=[{"@context":"https://schema.org","@type":"Article","headline":title,"description":desc,"inLanguage":"es-AR","dateModified":"2026-10-04","author":{"@type":"Organization","name":"Smartrecruit"},"publisher":{"@type":"Organization","name":"Smartrecruit","url":BASE},"mainEntityOfPage":f"{BASE}/guias/{slug}/"}]
    if faq: ld.append({"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in faq]})
    return slug,f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(seo_title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{BASE}/guias/{slug}/">
<meta property="og:title" content="{html.escape(seo_title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{BASE}/guias/{slug}/">
<meta property="og:type" content="article">
<meta property="og:locale" content="es_AR">
<meta name="theme-color" content="#0b2a6b">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ctext y='.9em' font-size='90'%3E%F0%9F%8E%93%3C/text%3E%3C/svg%3E">
<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700&family=Source+Sans+3:wght@400;600&display=swap" rel="stylesheet">
<style>{CSS}</style>
<script type="application/ld+json">{json.dumps(ld,ensure_ascii=False)}</script>
<script defer src="/assets/analytics.js"></script>
</head>
<body>
<header><div class="in"><a class="brand" href="/">Smartrecruit</a><a class="cta" href="/">Armá tu perfil gratis</a></div></header>
<main>
<div class="crumb"><a href="/">Inicio</a> › <a href="/guias/">Guías</a> › {html.escape(title)}</div>
<h1>{html.escape(title)}</h1>
<p class="upd">Actualizado: octubre de 2026</p>
{body}
<div class="box"><b>Hacelo con Smartrecruit, gratis:</b> armá tu perfil, mirá qué universidades encajan con vos (Best Fit), conseguí el email de cada coach y generá el mail en inglés en minutos. <a href="/">Empezar ahora →</a></div>
<div class="next"><b>Otras guías</b><ul>NEXT_{slug}</ul></div>
</main>
<footer><div class="in">Smartrecruit es una herramienta educativa que orienta el autorreclutamiento deportivo universitario en Estados Unidos. No es un agente ni un intermediario, no garantiza becas ni admisiones y no cobra por su uso. No está afiliada a la NCAA, la NAIA, la NJCAA ni a ninguna universidad. Las reglas cambian: confirmá siempre en las fuentes oficiales.</div></footer>
</body>
</html>
"""
P=[]
P.append(page("elegibilidad-ncaa-argentinos","Cómo registrarte en el NCAA Eligibility Center desde Latinoamérica","Cómo registrarte en el NCAA Eligibility Center desde Latinoamérica (guía 2026) | Smartrecruit",
"Guía paso a paso para estudiantes internacionales: qué cuenta abrir en la NCAA y la NAIA, cuánto cuesta, calendario, documentos y amateurismo.",
"""<p class="lead">Para jugar en una universidad de Estados Unidos no alcanza con que un coach te quiera: un organismo oficial tiene que confirmar que cumplís los requisitos académicos y de amateurismo. Esta guía te dice qué hacer y cuándo.</p>
<h2>¿En qué centro me registro?</h2>
<div class="wrap"><table><tr><th>Si querés jugar en…</th><th>Te registrás en…</th></tr>
<tr><td>NCAA División 1 o 2</td><td>NCAA Eligibility Center (eligibilitycenter.org), cuenta académica y deportiva</td></tr>
<tr><td>NCAA División 3</td><td>Si sos extranjero, igual tenés que certificar tu amateurismo con la cuenta solo deportiva</td></tr>
<tr><td>NAIA</td><td>NAIA Eligibility Center (playnaia.org). Es aparte: estar registrado en la NCAA no alcanza</td></tr>
<tr><td>Junior college (NJCAA)</td><td>No hay centro de elegibilidad: tenés que haber terminado la secundaria</td></tr></table></div>
<h2>Los tipos de cuenta NCAA y cuánto cuestan</h2>
<p><b>Profile Page (gratis):</b> empezá por acá. Te da tu NCAA ID, que conviene poner en cada mail a un coach.</p>
<p><b>Cuenta académica y deportiva (USD 170 para internacionales):</b> la necesitás para D1 o D2, y tiene que estar completa antes de hacer visitas oficiales o firmar. Conviene pagarla cuando un coach muestra interés real.</p>
<p><b>Cuenta solo deportiva (USD 75):</b> para extranjeros que van a jugar en D3.</p>
<p>La exención de pago depende de beneficios del sistema de Estados Unidos, así que en la práctica un estudiante de un colegio fuera de EE.UU. no califica.</p>
<h2>NAIA en cuatro pasos</h2>
<p>1. Creá tu perfil en playnaia.org. 2. Tu colegio envía tus documentos académicos al NAIA Eligibility Center. 3. Como internacional, comprás la evaluación de InCred (incredevals.org): solo cuenta lo que InCred verifica. 4. Cuando un coach NAIA te pone en su lista de reclutamiento, tu caso se evalúa con prioridad. El registro internacional cuesta USD 170. Para ser elegible necesitás promedio 2.3 o más, o 2 de 3: ACT 18 / SAT 970, promedio 2.0, mitad superior de tu clase.</p>
<h2>Calendario si terminás la secundaria en diciembre</h2>
<p>En Argentina, Uruguay, Chile y Paraguay la secundaria termina en diciembre (en otros países, a mitad de año) y en Estados Unidos las clases empiezan en agosto (o en enero, en el segundo semestre).</p>
<p><b>Dos años antes de egresar:</b> creá la Profile Page (y el perfil NAIA si te interesa). <b>Un año y medio antes:</b> pedí en tu colegio el analítico o certificado de materias y notas, y averiguá la traducción oficial al inglés. <b>Cuando un coach D1 o D2 vaya en serio:</b> pasá a la cuenta paga y cargá los documentos. <b>Al egresar:</b> mandá el certificado final y la constancia de egreso; sin eso la evaluación no se cierra.</p>
<h2>La regla de los 5 años (D1)</h2>
<p>Desde 2026, en División 1 tenés 5 temporadas dentro de 5 años. El reloj arranca con tu primera inscripción full-time en una universidad o el año académico en que cumplís 19, lo que pase primero, y no frena aunque no juegues o te cambies de universidad. Por eso un año sabático largo después del secundario puede costarte temporadas: planificá para entrar el agosto siguiente a egresar. En División 2 sigue la regla de 4 temporadas en 10 semestres.</p>
<h2>Amateurismo: donde más se complican los latinoamericanos</h2>
<p>En los clubes de Latinoamérica conviven inferiores y primera. La NCAA te pregunta por contratos firmados, pagos por jugar más allá de viáticos o indumentaria, entrenamientos o partidos con un plantel profesional y representantes. Respondé siempre con la verdad: una respuesta falsa es mucho más grave que una situación que se puede explicar. Si tenés dudas, consultá a la NCAA en on.ncaa.com/intlcontact.</p>
<h2>Errores que hay que evitar</h2>
<p>Registrarse tarde · mandar documentos sin traducción · no enviar el certificado final · suponer que la NCAA sirve para la NAIA · contestar el amateurismo "a ojo".</p>""",
[("¿Cuánto cuesta registrarse en el NCAA Eligibility Center siendo extranjero?","La cuenta académica y deportiva cuesta USD 170 para estudiantes internacionales; la cuenta solo deportiva, USD 75; la Profile Page es gratis."),
 ("¿Si me registro en la NCAA sirve para la NAIA?","No. La NAIA tiene su propio centro de elegibilidad (playnaia.org) y hay que registrarse aparte.")]))
P.append(page("cuanto-cubre-una-beca-deportiva","¿Cuánto cubre una beca deportiva en Estados Unidos?","¿Cuánto cubre una beca deportiva en Estados Unidos? D1, D2, D3, NAIA y JUCO | Smartrecruit",
"Qué esperar de una beca deportiva según la división, qué ayudas no aplican a extranjeros y cómo calcular lo que paga tu familia.",
"""<p class="lead">La "beca total" casi nunca es solo deportiva: suele combinar beca deportiva, mérito académico y ayuda de la propia universidad. Saberlo de antemano evita frustraciones.</p>
<h2>Becas deportivas por división</h2>
<p><b>NCAA D1:</b> desde 2025 los programas tienen límites de plantel en lugar de topes de becas, y cada universidad decide cuántas da. Puede haber becas completas, pero son muy competidas.</p>
<p><b>NCAA D2 y NAIA:</b> casi siempre son becas parciales. El coach reparte un monto total entre todo el plantel.</p>
<p><b>NCAA D3:</b> no da becas deportivas. La ayuda llega por mérito académico o de la universidad, y puede ser generosa.</p>
<p><b>Junior college:</b> son más baratos, algunos dan becas, y muchos jugadores pasan después a una universidad de cuatro años.</p>
<h2>Lo que no aplica a extranjeros</h2>
<p>Los estudiantes internacionales no pueden recibir la ayuda federal de Estados Unidos (becas Pell, préstamos federales). Sí pueden recibir becas deportivas, becas por mérito académico y ayuda de la propia universidad.</p>
<h2>Cómo calcular lo que paga tu familia</h2>
<p>Costo total del año (matrícula + alojamiento + comida + seguro + pasajes) − beca deportiva − beca académica − ayuda de la universidad = lo que paga tu familia. Buenas notas y un buen puntaje en exámenes como el SAT o el Duolingo English Test suben la beca académica, que muchas veces se suma a la deportiva.</p>
<h2>Qué preguntarle al coach sobre plata</h2>
<p>¿Cuánto cubre la oferta y por cuántos años? ¿Se renueva automáticamente? ¿Puedo sumar becas académicas? ¿Qué gastos quedan afuera? ¿Cuál es el costo neto final para un internacional? Pedí siempre la oferta por escrito.</p>""",
[("¿La NCAA D3 da becas deportivas?","No. En D3 la ayuda llega por mérito académico o de la propia universidad."),
 ("¿Un extranjero puede recibir ayuda federal en Estados Unidos?","No. Puede recibir becas deportivas, académicas y ayuda de la universidad, pero no ayuda federal.")]))
P.append(page("video-highlight-universidades","Cómo hacer un video highlight para universidades de Estados Unidos","Cómo hacer un video highlight para universidades de Estados Unidos | Smartrecruit",
"Duración, qué mostrar según tu posición, cómo identificarte y dónde subir tu video para que un coach universitario te responda.",
"""<p class="lead">Casi ningún coach recluta a un extranjero sin verlo jugar. El mail abre la puerta; el video decide si te responde.</p>
<h2>Lo básico</h2>
<p><b>Duración:</b> entre 3 y 5 minutos. Los coaches miran los primeros 30 a 60 segundos y deciden si siguen: tus mejores jugadas, primero.</p>
<p><b>Arranque:</b> una placa de 5 a 10 segundos con tu nombre, posición, año de egreso, altura, club, país y email.</p>
<p><b>Identificate:</b> antes de cada jugada, marcá quién sos con una flecha, un círculo o una pausa de un segundo.</p>
<p><b>Partidos reales</b> mejor que entrenamientos, y contra el mejor rival posible. Sin música fuerte ni efectos.</p>
<h2>Qué mostrar según la posición</h2>
<p><b>Arqueros:</b> atajadas de reflejo, salidas, juego con los pies, uno contra uno y comunicación. <b>Defensores:</b> recuperaciones, anticipación, juego aéreo y salida limpia. <b>Mediocampistas:</b> pases que rompen líneas, visión, recuperación y llegada. <b>Delanteros:</b> goles de distinto tipo, desmarques, presión y asistencias. <b>Básquet:</b> lectura de juego, tiro, defensa y transición. <b>Vóley:</b> la acción completa de tu posición, incluido el armado o la recepción.</p>
<p>Sumá además un partido completo sin editar: muchos coaches lo piden después del highlight.</p>
<h2>Dónde subirlo</h2>
<p>YouTube (como "No listado" si no querés que sea público), Hudl o Vimeo, con un título claro: "Nombre Apellido · Posición · Clase 2028 · País". Revisá que el link abra sin pedir permisos y actualizalo cada temporada.</p>"""))
P.append(page("beca-futbol-estados-unidos-argentinos","Becas de fútbol en Estados Unidos para latinoamericanos: paso a paso","Becas de fútbol en Estados Unidos para latinoamericanos: paso a paso | Smartrecruit",
"Cómo conseguir una beca de fútbol universitario en Estados Unidos por tu cuenta: divisiones, becas, elegibilidad, video y cómo escribirle a los coaches.",
"""<p class="lead">El fútbol universitario de Estados Unidos recluta mucho en Sudamérica. Con un buen video, notas en orden y constancia para escribirle a los coaches, se puede llegar sin agencia.</p>
<h2>1. Elegí a qué nivel apuntar</h2>
<p>Hay programas de fútbol masculino y femenino en NCAA D1, D2 y D3, NAIA y junior college. En D1 la competencia es altísima; muchos latinoamericanos encuentran su lugar en D2, NAIA y junior college, donde además es más común combinar beca deportiva y académica.</p>
<h2>2. Entendé cómo son las becas</h2>
<p>Fuera de D1, las becas de fútbol suelen ser parciales: el coach reparte un monto entre todo el plantel. Por eso pesa tanto el promedio: una buena beca académica completa lo que falta. En D3 no hay becas deportivas. Más detalle en la <a href="/guias/cuanto-cubre-una-beca-deportiva/">guía de becas</a>.</p>
<h2>3. Ordená tu elegibilidad</h2>
<p>Para NCAA D1 y D2 necesitás el NCAA Eligibility Center; para NAIA, su propio registro. Prestá especial atención al amateurismo si jugaste en inferiores de un club con primera división. Todo en la <a href="/guias/elegibilidad-ncaa-argentinos/">guía de elegibilidad</a>.</p>
<h2>4. Armá tu video</h2>
<p>Entre 3 y 5 minutos, tus mejores jugadas primero, identificado en cada jugada, y un partido completo aparte. Ver la <a href="/guias/video-highlight-universidades/">guía del video</a>.</p>
<h2>5. Escribile a muchos coaches, bien</h2>
<p>Lo normal es escribirle a entre 30 y 50 programas acordes a tu nivel, con un mail corto, en inglés y personalizado para cada universidad, y hacer seguimiento. En Smartrecruit tenés los emails de cientos de coaches de fútbol y un generador de mails. Ver <a href="/guias/como-escribirle-a-un-coach/">cómo escribirle a un coach</a>.</p>"""))
P.append(page("beca-basquet-estados-unidos-argentinos","Becas de básquet en Estados Unidos para latinoamericanos: paso a paso","Becas de básquet en Estados Unidos para latinoamericanos: paso a paso | Smartrecruit",
"Cómo buscar una beca de básquet universitario en Estados Unidos por tu cuenta: divisiones, becas, elegibilidad, video y contacto con coaches.",
"""<p class="lead">El básquet universitario tiene más de mil programas entre masculino y femenino. Elegir bien a qué nivel apuntar es la mitad del trabajo.</p>
<h2>1. Elegí a qué nivel apuntar</h2>
<p>Hay programas en NCAA D1, D2 y D3, NAIA y junior college. Muchos jugadores internacionales arrancan en junior college o en NAIA, se adaptan al juego y al idioma, y después pasan a una universidad de cuatro años.</p>
<h2>2. Entendé cómo son las becas</h2>
<p>En D1 cada universidad define cuántas becas da desde 2025; en D2 y NAIA suelen ser parciales; en D3 no hay becas deportivas. Más detalle en la <a href="/guias/cuanto-cubre-una-beca-deportiva/">guía de becas</a>.</p>
<h2>3. Ordená tu elegibilidad</h2>
<p>NCAA y NAIA tienen centros de elegibilidad distintos. Si jugaste en un club con equipo profesional o cobraste algo, leé con atención la parte de amateurismo de la <a href="/guias/elegibilidad-ncaa-argentinos/">guía de elegibilidad</a>.</p>
<h2>4. Video: más que puntos</h2>
<p>Los coaches quieren ver lectura de juego, tiro, defensa y transición. Incluí tu altura y envergadura en la placa inicial. Ver la <a href="/guias/video-highlight-universidades/">guía del video</a>.</p>
<h2>5. Contactá a los coaches</h2>
<p>En Smartrecruit tenés los emails de miles de coaches de básquet universitario, masculino y femenino. Escribí mails cortos, en inglés y personalizados, y hacé seguimiento. Ver <a href="/guias/como-escribirle-a-un-coach/">cómo escribirle a un coach</a>.</p>"""))
P.append(page("como-escribirle-a-un-coach","Cómo escribirle a un coach universitario de Estados Unidos","Cómo escribirle a un coach universitario de Estados Unidos (con ejemplo en inglés) | Smartrecruit",
"Estructura, asunto y ejemplo en inglés del mail a un coach universitario, cuándo hacer seguimiento y errores comunes.",
"""<p class="lead">Los coaches reciben cientos de mails. El tuyo tiene que leerse en 30 segundos y darles un motivo concreto para abrir tu video.</p>
<h2>La estructura</h2>
<p>1. Quién sos: posición, año de egreso, país y club. 2. Por qué ese programa: algo específico (una vacante, la carrera, la conferencia). 3. Tus datos clave: altura, estadísticas, promedio. 4. El link al video. 5. Un cierre con una pregunta concreta. Máximo 150 a 200 palabras.</p>
<h2>El asunto</h2>
<p>Corto e informativo: <b>Class of 2028 GK | Juan Pérez | Argentina | Highlights</b>.</p>
<h2>Ejemplo</h2>
<pre>Subject: Class of 2028 GK | Juan Pérez | Argentina | Highlights

Hello Coach Smith,

My name is Juan Pérez, a goalkeeper from Argentina (Class of 2028) playing for Club Atlético Example. I am very interested in [University] because of your [major] program and your team's style of play.

- Height: 6'2" (1.88 m)
- GPA: 3.6 (8.7/10 in Argentina)
- Highlights: [link]

I would love to know if you are still recruiting goalkeepers for the 2028 class and what the next steps would be.

Thank you for your time,
Juan Pérez
[email] · [WhatsApp]</pre>
<h2>Seguimiento</h2>
<p>Si no hay respuesta, volvé a escribir a los 10 a 14 días, con una novedad: un video nuevo, un partido o una nota. Después, cada vez que tengas algo nuevo para contar.</p>
<h2>Errores comunes</h2>
<p>Mandar el mismo mail a todos sin personalizar · escribir en español · mails largos · no incluir el video · no decir el año de egreso · escribirle al entrenador de otro equipo de la universidad.</p>"""))
# index
items="".join(f'<li><a href="/guias/{s}/">{html.escape(t)}</a> — {html.escape(d)}</li>' for s,t,d in GUIDES)
idx=page("","Guías para conseguir una beca deportiva en Estados Unidos","Guías para conseguir una beca deportiva en Estados Unidos | Smartrecruit",
"Guías gratuitas en castellano para atletas latinoamericanos: elegibilidad NCAA y NAIA, becas, video, fútbol, básquet y cómo escribirle a un coach.",
f'<p class="lead">Todo lo que necesitás para buscar una beca deportiva por tu cuenta, explicado en castellano.</p><ul>{items}</ul>')
GUIDES.pop()
for slug,html_ in P+[idx]:
    nxt="".join(f'<li><a href="/guias/{s}/">{html.escape(t)}</a></li>' for s,t,d in GUIDES if s!=slug)
    html_=html_.replace(f"NEXT_{slug}",nxt)
    if slug=="": html_=html_.replace('<a href="/guias/">Guías</a> › Guías para conseguir una beca deportiva en Estados Unidos','Guías').replace(f'{BASE}/guias//',f'{BASE}/guias/')
    d=os.path.join("out","guias",slug); os.makedirs(d,exist_ok=True); open(os.path.join(d,"index.html"),"w").write(html_)
urls=[f"{BASE}/",f"{BASE}/guias/"]+[f"{BASE}/guias/{s}/" for s,_,_ in GUIDES]
open("out/sitemap.xml","w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+"".join(f"  <url><loc>{u}</loc><lastmod>2026-10-04</lastmod></url>\n" for u in urls)+"</urlset>\n")
print(urls)
