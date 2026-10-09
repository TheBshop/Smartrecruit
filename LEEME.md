# Smartrecruit — código fuente

- `RosterReal.jsx`: toda la app (datos + interfaz). Es el archivo que se edita.
- `main.jsx`: arranca la app.
- `public/`: se copia tal cual al sitio. Incluye `index.html` (con PostHog, SEO e ícono), `assets/analytics.js` (PostHog + aviso de cookies), `robots.txt` y `sitemap.xml`.
- `analytics-src/entry.js`: código legible de la analítica (solo hace falta si se cambia).

Compilar: `npm install` y después `npm run build`. El resultado queda en `dist/`, que es la carpeta que se sube a Netlify.


## Funciones de servidor (Netlify)
- `netlify/functions/generate-email.mjs`: genera mails con Claude en `/api/generate-email`. Necesita la variable de entorno `ANTHROPIC_API_KEY` en Netlify (opcional: `ANTHROPIC_MODEL`).
- `netlify.toml`: comando de build, carpeta `dist` y carpeta de funciones.

## Mails: tipos, ganchos y registro (octubre 2026)
- `MAIL_KINDS`: los 7 tipos de mail (primer contacto, seguimiento, novedad, respuesta, post-llamada, oferta, cierre). `composeEmail` arma cada uno.
- Ganchos (`HOOK_LABELS`): dato propio, búsqueda publicada, staff compatriota, vacante proyectada, compatriotas en el plantel. La comparación de estadísticas contra el plantel se sacó de los mails (7/10/2026): solo pesa en el ranking. Un solo gancho por mail; los seguimientos usan uno que no se haya usado antes con ese coach.
- `rr_outreach_log[universidad].messages`: un registro por envío `{ at, kind, hook, lang, ai, stage, subject }`. `nextOutreachStep(entry)` dice qué toca (esperas de 10, 14 y 21 días; máximo 3 seguimientos).
- `rr_mail_facts`: datos que suma la atleta por universidad; se borran al usarlos en un envío.
- Analítica (solo con cookies aceptadas): eventos `mail_enviado` y `respuesta_registrada`, con tipo y gancho, sin texto del mail.

## Básquet D2: planteles (octubre 2026)
- `BBALL_D2_ROSTERS`: 258 planteles de básquet masculino NCAA D2 (RealGM, 21 de 23 conferencias), con posición, clase, ciudad y país de nacimiento. Formato `{ universidad: [temporada, filas] }`.
- Estadísticas 2025-26 (partidos, puntos y asistencias por partido) de 2.307 de los 4.200 jugadores: `datos-src/basquet_d2_stats_2025-26.csv` (`id_realgm,pj,ppg,apg`), cruzadas por id de jugador. Los ingresantes no tienen.
- 213 son de la temporada 2026-27 (la actual) y 40 de la 2025-26, porque RealGM todavía no había publicado su plantel nuevo. A esos el motor los "envejece": `activeRoster()` saca a los que ya terminaron su elegibilidad y `projectRosterForProfile()` estima las camadas que faltan.
- `datos-src/basquet_d2.py` regenera las constantes a partir de los CSV de una o más temporadas (ver el encabezado del script).
- `rosterPosMatch()`: en básquet agrupa posiciones en G / F / C.

## Contactos de coaches (7/10/2026)
- `BBALL_D2_COACHES_2026`: cuerpos técnicos 2026-27 de 24 programas de básquet D2, copiados de las páginas oficiales de staff.
- `coachContactFor()` descarta los contactos cuyo cargo dice ser de otro deporte. Había 172 contactos de básquet que en realidad eran entrenadores de fútbol (error de una carga anterior): ahora esos programas figuran sin mail hasta que se cargue el correcto.

### Auditoría de contactos (7/10/2026)
Pasada completa sobre `COACH_CONTACTS_BY_PROGRAM` (3.505 → 2.671 entradas). Script: `datos-src/contactos_auditoria.py <RosterReal.jsx>` (sobre datos limpios no cambia nada; correrlo con cada lote nuevo antes de publicar).
- **Lote de básquet del 2/10 eliminado (791 entradas: los 424 programas femeninos y 367 masculinos).** Era el staff de fútbol de cada universidad copiado como básquet. Básquet femenino queda sin contactos; masculino queda con 541 del lote bueno + los 24 cargados a mano.
- 50 contactos estaban en la universidad equivocada por nombre parecido (Cornell University ← Cornell College, Washington College ← University of Washington, etc.): 31 se reasignaron a la universidad correcta, 19 se descartaron (la correcta ya tenía contacto o no está en el catálogo).
- Descartados: 9 contactos de básquet cuyo "principal" no era coach (asistente ejecutiva, preparador físico), 3 con la rama cruzada, 1 de softball.
- Mails: 6 con formato inválido corregidos, 14 del principal quitados (eran de otra persona o de la institución), 178 marcados como mail del programa, 379 de asistentes quitados (repetían el del principal, eran compartidos o personales tipo gmail).
- Nombres: 65 limpiados (año de egreso, "Dr.", apodos, mayúsculas).
- `ROSTER_COACH_CONTACTS` (58 contactos viejos, uno por universidad): cada uno tiene ahora `sport` y `gender` y solo se usa para ese programa. Antes un "Head Coach" de hockey podía salir como contacto de otro deporte de la misma universidad.
- La ficha de universidad ("Coaches por programa") muestra exactamente lo que usa el armador de mails (`contactsForSchool` pasa por `coachContactFor`). Se quitó el aviso "Head Coach identificado por NCSA".
- Saludo: `coachLastName()` respeta apellidos con partícula ("Coach Van Dyke", "Coach da Luz") y saca sufijos (Jr., III).

## Calendario: desde cuándo puede contestar un coach (7/10/2026)
Son dos reglas distintas y la app ahora las separa:
- **Por año de la atleta** (`CONTACT_START`, `contactStartFor`, `contactStartText`): desde cuándo un coach puede escribirle, llamarla u ofrecerle algo. Se calcula con su año de ingreso (`getEntryYear`): en D1, 15/6 de dos años antes (básquet femenino 1/6); en D2 la comunicación es libre y las visitas oficiales y el contacto en persona arrancan el 15/6 previo al año junior (fuente: *NCAA Division II Coaches Off-Campus Recruiting Guide 2026-27*). Se muestra en la página Calendario ("Tu caso"), en Inicio y en el aviso de cada mail.
- **Por fecha** (`SPORT_CALENDARS[...].events`): períodos de contacto, evaluación, silencioso y muerto. Solo limitan el contacto en persona, las visitas y las evaluaciones; no los mails.
- Corregido: para las mujeres en fútbol y básquet el armador de mails no encontraba el calendario (buscaba "Soccer (W)" y la clave es "Soccer (F)"); `contactWindowNote` decía que el coach "puede responderte recién" al abrir el próximo período de contacto; con dos períodos activos a la vez se tomaba el primero de la lista y no el más corto (un período muerto dentro de uno de contacto no se detectaba).
- "2° año de secundaria" se reemplazó por "año sophomore (10.º grado de EE.UU.: el antepenúltimo año de tu secundaria)".
- Básquet masculino D1 contrastado con el PDF oficial de la NCAA (actualizado el 30/7/2026): coincide; se agregaron las ventanas de evaluación y el período silencioso del 19 al 25/7/2027.
- Contrastados después con los PDF oficiales (todos actualizados el 30/7/2026): **vóley** (coincide; el período silencioso 1/5-3/6 es correcto y NCSA lo omite), **básquet femenino** (shutdown 3-9/5 correcto; se agregaron los días muertos del 22/4, 26/4 y 17/5 y las ventanas de evaluación), **atletismo** (coincide; se agregaron los dos períodos de contacto).
- El "recruiting shutdown" es el único período en que el coach tampoco puede escribir ni llamar: el aviso del mail lo dice aparte.
- Con las páginas por deporte de NCSA (7/10/2026): **gimnasia** pasa a la regla general de primer contacto (15/6 al terminar sophomore, visitas desde el 1/8; antes decía 1/9 del año junior); **hockey** coincide con lo cargado (silencioso 20-23/12, shutdown 24/12-1/1); D3 suma las visitas oficiales desde el 1/1 del año junior.
- **Pendiente** (hace falta el PDF oficial "Division I Other Sports"): fútbol femenino (período muerto desde el 15/12 según NCSA, 16/12 en la app), si hockey tiene además el período muerto del 9-12/11, y los períodos de gimnasia. Atletismo: la fecha de primer contacto (1/9 del año junior) sigue sin contrastar.

## Catálogo: una tarjeta por universidad (7/10/2026)
Antes había una tarjeta por programa, así que una universidad con rama masculina y femenina salía dos veces. Ahora `CatalogPage` agrupa por universidad (`schools`) y `SchoolCard` recibe `progs` (todos sus programas que pasan los filtros) y los resume: "NCAA D1 · Femenino y masculino", o la lista de deportes en la vista "Todos los deportes" (opción nueva del filtro Deporte). El detalle por deporte está en la ficha de cada universidad.
- El catálogo abre en el deporte y la rama del perfil (`defaultRama`). El Fit se calcula solo con el programa del deporte y la rama de la atleta.
- "Roster cargado" se decide por rama (`rosterKind(school, sport, gender)`): antes el equipo femenino la mostraba por el plantel masculino.

## Ranking: afinidad nacional (7/10/2026)
`matchFromLoadedRosters` suma entre 20 y 38 puntos (sobre 100) si en el plantel hay jugadores del país de la atleta: 20 de base, +3 por cada compatriota extra (hasta +9), +6 si alguno juega en su posición y +5 si alguno tiene partidos jugados. Un entrenador compatriota en el staff suma 10 más (`staffCompatriotSignal`).
- Corregido: el país se comparaba como texto, así que "Brasil" (perfil) no coincidía con "Brazil" (plantel); lo mismo España, México, Perú, República Dominicana y cualquier país escrito distinto en inglés. Ahora se normaliza con `mailCountryKey` (sin acentos, con alias en castellano, inglés y abreviaturas como "Arg.").
- El campo "País de origen" del perfil sugiere países para evitar errores de tipeo (sigue siendo texto libre).
- Límites: solo se aplica a universidades con plantel cargado y mira el plantel actual, no los de años anteriores. El "% Fit" de las tarjetas del catálogo no usa la nacionalidad.

## Rugby: programas de la NCR (8/10/2026)
`RUGBY_NCR_PROGRAMS`: 74 equipos masculinos de National Collegiate Rugby D1 y D1AA según RuckMob (ruckmob.com/competitions/ncr-d1 y ncr-d1aa). Se agregan al catálogo como "D1 (NCR)" y "D1AA (NCR)" solo si la universidad no tenía ya un programa de rugby masculino (quedaron 68 nuevos; rugby pasó de 94 a 162). Faltan NCR D2 y D3: sus páginas en RuckMob no listan equipos.

## Vínculo con los datos oficiales (EADA) (8/10/2026)
`EADA_SITE_NAMES` une el nombre de cada universidad del catálogo con su registro oficial. Se agregaron 47 vínculos que faltaban (Illinois, Maryland, Michigan, Nebraska, Rutgers, Washington, Pittsburgh, Missouri, Tennessee, Arizona State, Miami (OH), Marist, Siena, los campus de Penn State, etc.), revisados uno por uno. Sin vínculo, esas universidades no tenían la sección de becas y deportistas, y sus equipos femeninos de fútbol y básquet aparecían en el catálogo como otra universidad con el nombre oficial ("University of Maryland-College Park").
Se corrigieron 5 vínculos equivocados: University of Wisconsin (apuntaba a UW-Stout), Colorado State (a Colorado Mesa), Kent State (a Central State), University of South Carolina (a USC Aiken) y LSU (a LSU-Eunice); y se quitaron 4 que apuntaban a otra institución (Salem College, Mt. San Jacinto College, UW-Waukesha, Community Christian College).
Quedan sin vínculo unas 70 universidades NCAA sin un registro oficial claro (casos con datos combinados de varios campus, como Vermont State o Commonwealth University, se dejaron sin vincular a propósito).

## Básquet D2: contactos de Florida Coastal Prep (8/10/2026)
`BBALL_D2_COACHES_FCP`: head coach y mail de 88 programas D2 con plantel que no tenían mail, del directorio de floridacoastalprep.com (actualizado en agosto de 2026). Contra los 24 staff oficiales 2026-27, 10 de 12 coincidían. Solo se usa donde no había mail y cada uno pasó los controles de la auditoría (dominio de la universidad y nombre del coach). Programas D2 con plantel sin mail: de 113 a 25 (lista en basquet_d2_mails_faltantes.csv).

## Básquet D2: staff de las páginas oficiales (8/10/2026)
`BBALL_D2_COACHES_WEB`: staff leído de la página oficial de 20 de los 25 programas que seguían sin mail (18 con mail del head coach; West Florida con el mail del programa; Flagler y Southern Connecticut con el nombre del coach pero sin su mail en la página). Algunas páginas mostraban todavía 2024-25 o 2025-26 (King, Augustana, Dallas Baptist, Middle Georgia, Point Park, Thomas Jefferson, Southern Connecticut): queda anotado en `updated`. Siguen sin mail 7: Belmont Abbey, Dominican (NY), Emmanuel, Flagler, Southern Connecticut, UPR Bayamón y UDC (sitios bloqueados o sin página encontrada).

- (8/10/2026) Sin compatriotas, dos señales más débiles: **afinidad regional** (jugadores de otros países de Latinoamérica, si la atleta es latinoamericana: 8 puntos + 2 por cada uno extra hasta 12, +3 si alguno juega en su posición) y **proporción de internacionales** del plantel (hasta 6 puntos, con al menos 5 jugadores con país conocido; no se aplica a atletas de EE.UU.). Siempre por debajo de un compatriota (20 a 38).

## Mails paso 2 y revisión de secciones (8/10/2026)
- IA por tipo de mail (first/followup/update/reply/thanks/offer/close): "Mejorar con IA" parte del borrador base; "Responder con IA" usa el mensaje del coach pegado (se guarda por universidad en `rr_coach_msgs` y se borra al enviar). La función devuelve además una lista "Para completar o revisar".
- Elegibilidad: regla 10/7 para internacionales; amateurismo final se pide desde el 1/4 (1/10 si entrás en enero); D3 internacional necesita cuenta Amateurism-Only; equivalencia 9° grado unificada.
- Costos: tope D1 básquet femenino 15, D2 fútbol femenino 9.9; aclaración de que la columna D1 es previa al acuerdo de 2025.
- Exámenes: ACT actualizado (Science y Writing opcionales desde 2025).
- Conversor de promedio: Chile, México, Colombia, Brasil, Perú, España y porcentaje pasan a tablas por tramos (estimación).
- Carreras: sinónimos (Arquitectura, Educación Física, Contador, Nutrición); Abogacía/Medicina explican que son de posgrado en EE.UU.; se quitaron 8 sedes que heredaban las carreras de la universidad madre (ej. Texas A&M–Commerce).
- Hoja de ruta: video y lista a 28 meses, primer contacto a 24.
- Sin verificar: tarifas NCAA/NAIA, regla NAIA 2 de 3, fecha del reloj de 5 años en D1.
- Calendario "Other Division I Sports" 2026–27 (PDF oficial NCAA): se sumaron golf (F y M), natación, lucha (M y F), tenis, waterpolo, vóley de playa, bowling, lacrosse y rugby; hockey, fútbol y gimnasia contrastados (coinciden).
- NAIA: registro aparte aunque estés en NCAA, High School Portal, prioridad con la lista corta del coach, 3–7 días hábiles.
- NAIA internacionales (guía oficial NAIA): promedio 2.3+ o 2 de 3; tarifa USD 170; carta del colegio para el ranking; traducción literal sin certificar; revisión ~20 días hábiles.
- Reloj de elegibilidad D1/D2 (modelo por edad, aprobado 24/6/2026, fuente NCSA): 5 temporadas en 5 años desde el año siguiente a cumplir 19 o la primera inscripción full-time; D2 sigue con 4 temporadas en 10 semestres (fuente NCSA 2026-27). La regla 10/7 no aplica a credenciales internacionales.
- Tarifa NCAA Eligibility Center (NCSA): USD 170 internacional / 110 EE.UU.-Canadá.
- Corrección (fuente NCSA requisitos 2026-27): D2 sigue con 4 temporadas/10 semestres; la regla 10/7 no aplica a credenciales internacionales; reloj D1 desde inscripción full-time o año en que cumplís 19.
- Fuente NCSA requisitos 2026-27: D2 sin cambios (4 temporadas/10 semestres); 10/7 no aplica a credenciales internacionales; reloj D1 desde inscripción full-time o año en que cumplís 19.
- Staff básquet D2 pegado por el usuario (8/10): Belmont Abbey, Dominican NY, Emmanuel GA, Flagler, UDC, Miles, Spring Hill, Tuskegee. AUM se mantiene Komara (lista GSC trae a Joe Brooks, probablemente vieja).
- Revisión guías/glosario/quiz (8/10): guía de elegibilidad suma regla de 5 años y NAIA (InCred, USD 170, 2.3 o 2 de 3); pestaña Créditos corregida (la NCAA evalúa los boletines, no hay que tramitar equivalencias).
- Textos genéricos para toda Latinoamérica (8/10): se sacó "argentino" de la interfaz y las guías (salvo el recuadro de la ficha NCAA de Argentina, ejemplos y legales); país por defecto del perfil vacío; URLs de guías sin cambios.
- Fix IA (8/10): max_tokens 2500, rescate de JSON cortado, aviso si se cortó; posición inválida para el deporte se descarta (default de perfil sin posición).
- IA refinada (8/10): perfil limpio para la IA (aiProfile: nombre capitalizado, posición en inglés, estadísticas rotuladas, fechas calculadas); controles automáticos de números no presentes, corchetes y link de video; lista "Para completar" también en el armador de la ficha; español latinoamericano neutro.
