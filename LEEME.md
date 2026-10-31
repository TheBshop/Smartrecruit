# Smartrecruit — código fuente

- `RosterReal.jsx`: la app (interfaz y lógica; ~1,5 MB). Es el archivo que se edita.
- `datos/*.json`: los datos pesados (universidades, planteles, coaches, Scorecard, FieldLevel, etc.; ~15 MB). **Ya no están dentro del código**: el build los copia a `dist/data/NOMBRE.<hash>.json` (cache inmutable, ver `public/_headers`) y la app los baja en paralelo al abrir (`loadData()`), mostrando una pantalla liviana mientras tanto. Para cambiar un dato se edita el JSON de `datos/` (el nombre del archivo es el de la constante). Lo que se calcula a partir de esos datos al cargar vive en `__deriveAll()` (al final de `RosterReal.jsx`). Los scripts de `datos-src/*.py` fueron escritos para reemplazar constantes dentro de `RosterReal.jsx`: hay que apuntarlos a `datos/<CONSTANTE>.json` antes de volver a usarlos.
- `build.mjs`: arma `dist/` (`npm run build`).

## Regla permanente: el rendimiento es prioridad
Velocidad de carga y peso de la página son prioridad en cada cambio. Antes de publicar: no meter datos grandes dentro del código (van en `datos/*.json`), no sumar librerías pesadas sin necesidad, y medir. Referencia (26/10/2026): código 1,7 MB (antes 16 MB); visitante nuevo ve el título y el botón a los 0,3 s (portada completa ~1,3 s; antes 2 s); con CPU 4 veces más lenta, 1,1 s y ~4 s (antes 5,8 s).
- `main.jsx`: arranca la app.
- `public/`: se copia tal cual al sitio. Incluye `index.html` (con PostHog, SEO e ícono), `assets/analytics.js` (PostHog + aviso de cookies), `robots.txt` y `sitemap.xml`.
- `analytics-src/entry.js`: código legible de la analítica (solo hace falta si se cambia).

Compilar: `npm install` y después `npm run build`. El resultado queda en `dist/`, que es la carpeta que publica Cloudflare Pages.


## Funciones de servidor (Cloudflare Pages)
- `functions/api/generate-email.js`: genera mails con Claude en `/api/generate-email`. Necesita el secreto `ANTHROPIC_API_KEY` en Cloudflare Pages (Settings → Variables and Secrets; opcional: `ANTHROPIC_MODEL`).
- Cloudflare Pages: comando de build `npm run build`, carpeta de salida `dist`; la carpeta `functions/` se despliega sola.

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

## Chequeo del trimestre y mails nuevos (27/10/2026)
- **Chequeo del trimestre** (`/chequeo`, en Recursos): revisión guiada cada 90 días (notas, estadísticas y video, coaches sin novedades, lista, resultados, etapa, elegibilidad) más "copiar resumen para mi familia". Estado en `rr_quarterly` (`done`: fechas de cada chequeo, `since`: desde cuándo usa el sitio; se sincroniza con la cuenta). Toca cuando pasaron 90 días desde el último chequeo (o, si nunca hizo uno, desde lo más antiguo entre `since`, el inicio del plan y el primer envío). Aparece como aviso en Inicio, como "próximo paso" si no hay nada más urgente, como tarea del plan y como línea del mail semanal (`digest.quarterly`; hay que pegar `supabase/functions/send-weekly-reminders/email.ts` y volver a desplegar).
- **Mails nuevos** (`MAIL_KINDS`): pedir videollamada, check-in después de meses, ofrecer una referencia, pedir más tiempo para decidir, rechazar una oferta y aceptar una oferta. Salen en español e inglés, usan solo datos reales (nuevos campos opcionales: plazo y motivo) y avisan qué falta. La IA (`functions/api/generate-email.js`) conoce los mismos tipos. "Check-in" también se sugiere solo cuando pasaron 90 días sin novedades con un programa.
- **Modo familia** (`/familia`, en Recursos): guía en lenguaje simple para madre, padre o tutor (qué es Smartrecruit y qué no, las etapas, cuánto puede cubrir una beca, qué mirar antes de aceptar, señales de alerta, cómo acompañar) y, si hay perfil, el avance (etapa, coaches, respuestas, lista) con "copiar resumen" y "enviar por WhatsApp". No usa servidor ni cuentas nuevas: el resumen se arma en el navegador y lo comparte la atleta.
- El botón "Eliminar mi cuenta" está oculto (`ACCOUNT_DELETE_LIVE = false`) hasta que se despliegue `delete-account` en Supabase.

## Ficha para compartir (/atleta)
- En Perfil → "Tu ficha para compartir": medidor de completitud, usuarios de Instagram/TikTok, opciones de mostrar email/teléfono, y botones Copiar link / Compartir / WhatsApp.
- El link es `/atleta#<datos en base64url>`: el perfil viaja en el fragmento (nunca llega a un servidor). La página pública (`AthleteCardPage`) no descarga los datos grandes, es `noindex` y valida todo lo que lee del link (solo http/https, usuarios alfanuméricos, email/teléfono con formato).
- Menores: el email viene destildado por defecto y se avisa que se comparta con conformidad del adulto responsable.
- Clave `rr_share` (sincronizada) guarda redes y opciones.

## Instituciones: cerradas, renombradas y fichas (27/10/2026)
- Se quitaron del catálogo 25 instituciones que ya no funcionan (con fuente y fecha en `datos-src/instituciones_cerradas.json`): Clarks Summit, Eastern Nazarene, Northland, Alderson Broaddus, Alliance, Birmingham-Southern, Cabrini, Finlandia, Fontbonne, Holy Names, Medaille, Notre Dame College, Saint Rose, Wells, The King's College NY, St. Andrews NC, Univ. of Saint Katherine, ASA Miami, Multnomah (x2), Bacone y 4 campus de UW Colleges (Fond du Lac, Waukesha, Marinette, Baraboo). Se sacaron de `PROGRAMS_ALL_SPORTS`, `SCHOOL_PROFILES_NCSA`, `BBALL_ROSTERS` y `MAJOR_DATA_BY_SCHOOL`.
- Con nombre nuevo, ahora enlazadas a su ficha (`SCORECARD_NAME_IDS`): Union College KY → Union Commonwealth University; Univ. of Houston–Victoria → Texas A&M–Victoria; Southwestern Assemblies of God → Nelson University; West Hills Lemoore/Coalinga → Lemoore/Coalinga College; Fort Berthold CC → Nueta Hidatsa Sahnish College; Bethel KS y Ottawa AZ (Surprise).
- Fichas cargadas a mano porque no estaban en la descarga masiva: Saint John's (MN) 174792 y Nueta Hidatsa Sahnish 200086 (College Navigator / Scorecard).
- Quedan 9 sin ficha, con mensaje propio: campus regionales (UWSP Marshfield y Wausau, UW Marshfield-Wood, Benedictine Mesa, CT State Gateway, Bryant & Stratton Milwaukee), 2 clubes de rugby y John Melvin University (no se pudo confirmar).
- Los nombres viejos se mantienen en pantalla para no romper cruces con contactos y planteles; no hay buscador por nombre nuevo todavía.

## Perfil de demo para grabar
- Abrí `https://smartrecruit.com.ar/?demo=1` (idealmente en una ventana privada). Carga a "Tomás Herrera" (arquero argentino ficticio, ingreso 2028, quiere Kinesiología) con 6 universidades en la lista, 4 contactos en el tablero (uno respondió, uno con visita, dos para seguimiento) y las redes de ejemplo.
- Con `&go=catalog` (o `plan`, `outreach`, `profile`, `chequeo`, `familia`) abre directo esa pantalla.
- Solo se aplica si el navegador NO tiene un perfil propio: nunca pisa datos reales. Para repetir la demo, borrar los datos del sitio o abrir otra ventana privada.

## Repaso general del catálogo y rosters (27/10/2026)
- `node datos-src/limpiar_datos.mjs [--dry] [--verbose]` (repetible, idempotente): unifica instituciones renombradas (Mercy, Nazareth, Canisius, Manhattan → "University"), limpia conferencias (88 programas), reenlaza por nombre los planteles de básquet femenino (antes solo 92 de 550 equipos coincidían con el catálogo y el resto nunca aparecía), las estadísticas ESPN, FieldLevel y ofertas; corrige nombres de jugadores de fútbol con dígitos ("Adriana 0Durango, Adriana Durango"), normaliza clase (Fr/So/Jr/Sr/Gr, "R-" redshirt) y posiciones de básquet (G/F/C) y deja una sola ciudad/estado por institución.
- `node datos-src/importar_espn_mbb.mjs <carpeta con c0..c7.txt>`: importa los planteles 2026-27 de básquet masculino D1 (362 equipos, ~5.500 jugadores) con ciudad natal, país real y altura. Los alias entre nombres de ESPN y del catálogo están en `datos-src/espn_mbb_alias.json`. Conserva ppg/rpg/apg ya cargados (por nombre de jugador). El país "USA" falso que tenían los 99 planteles anteriores desapareció: ahora es el real.
- Las tarjetas de resultados sin ubicación (rosters que no traían `place`) toman ciudad/estado del catálogo (`catalogPlace`).
- Conferencias: varias universidades tienen conferencias distintas por deporte a propósito (reordenamiento 2026: Pac-12 renovada con Boise State, Colorado State, Fresno State, San Diego State, Gonzaga, Utah State, Oregon State, Washington State y Texas State; WAC → UAC, etc.). No "unificar" sin revisar.

## Hoja de ruta: guía de firma, visa y viaje (28/10/2026)
La etapa "Firma, visa y viaje" de `buildYearChecklist` pasó de 3 casilleros a 6 (acuerdo de beca, I-20, tarifa SEVIS, visa F-1, documentos, llegada). Cada ítem puede llevar `how` (lista de pasos, se muestra en un desplegable "Cómo se hace") y `link` a la fuente oficial (travel.state.gov, ICE/SEVP, fmjfee.com). Fuentes: travel.state.gov (visa de estudiante), ice.gov/sevis/students y studyinthestates.dhs.gov (formulario I-20). No se publican montos de la tarifa SEVIS ni de la visa porque las páginas consultadas no los traen: el texto manda a verlos en el sitio oficial. Nota: el ítem `y-i20` ahora cubre solo el I-20 (antes incluía el SEVIS, que ahora es `y-sevis`).

## Planteles D2 de fútbol masculino cargados a mano (28/10/2026)
`datos-src/cargar_plantel_pegado.mjs` lee un .txt con planteles (formato en `datos-src/planteles_pegados/futbol_d2m_2026.txt`: `## Escuela | fuente | fecha` y una línea `número|nombre|posición|año|ciudad natal|colegio previo` por jugador), normaliza posición y año, deduce el país de la ciudad natal y lo guarda en `SOCCER_D2M_BIO_2026.json` (clave `M`). Los equipos que están en BIO y no en STATS se cargan como plantel sin estadísticas (`statsLoaded: false`, temporada 2026-27). Entran al puntaje (compatriotas y vacantes por año) pero las tablas de jugadores siguen ocultas (`SHOW_ROSTER_TABLES`). Cargados: University of Findlay (45) y University of Jamestown (40). Para sumar más: pegar el plantel en ese formato y volver a correr el script. Se puede repetir sin problema (reemplaza el plantel de la escuela). Las estadísticas de 2025 de D2 no se pudieron conseguir: los sitios bloquean el navegador automatizado y la herramienta de lectura solo abre páginas que aparecen en búsquedas.

## Planteles, estadísticas y staff desde los sitios oficiales (plataforma Sidearm)
`datos-src/planteles_web/hacer_sitemaps.mjs <hosts.txt> [deporte] [temporada]` genera 3 sitemaps importables en la extensión Web Scraper (webscraper.io): estadísticas del año anterior (`/stats/AÑO`), plantel actual (`/roster`) y coaches (`/coaches`). `hosts.txt`: una línea `sitio | nombre exacto en el catálogo`. Los selectores se verificaron en los sitios de Lewis, Findlay y Grand Valley State. No cubre los sitios que muestran el staff solo en un directorio general (por ejemplo Ashland) ni los que bloquean el acceso (Tampa, Barry). `extractor_sidearm.js` hace lo mismo pegándolo en el navegador, escuela por escuela.

## Vacantes de FieldLevel (31/10/2026)
- `datos/FIELDLEVEL_NEEDS.json`: las búsquedas de coaches de los últimos 50 días (sin cerradas ni ofuscadas, descripción cortada en 170 caracteres) + 182 registros de RosterHunter (`source` distinto de `fieldlevel`, se conservan). Fuente: API pública `/api/RecruitingNeedApi/needs?sportEnum=<deporte>&page=N` (20 por página, las más nuevas primero), 29 deportes.
- **Las edades son horas al momento de la descarga.** Al abrir la app `__ageAndDeriveNeeds()` les suma el tiempo transcurrido desde `NEEDS_SNAPSHOT_AT` (constante en `RosterReal.jsx`). **Al actualizar el archivo hay que cambiar esa fecha** por la hora (UTC) de la descarga.
- `RECRUITING_NEEDS_GENERAL` ya no es un archivo propio: se arma al abrir a partir de `FIELDLEVEL_NEEDS` (antes era una copia con fechas relativas congeladas). `datos/RECRUITING_NEEDS_GENERAL.json` queda vacío.
- `OFFERS_BOARD` sigue siendo un listado más viejo y amplio (2.833): incluye búsquedas de hace meses que pueden estar cerradas. La pantalla lo aclara.
- Después de actualizar: `node datos-src/limpiar_datos.mjs` (vincula nombres de universidades con el catálogo) y `npm run build`.

## Datos fuera del código (29/10/2026)
Se sacaron de `RosterReal.jsx` 14 constantes grandes a `datos/*.json` (CDS_DATA, ESSLO_DATA, CIP_NAMES —ya con los nombres extra fusionados—, FOS_ASSOCIATE_SCHOOLS —lista; se arma el Set al cargar—, PSAC_FH_STATS, HOCKEY_D2_STATS_2026, HOCKEY_D2_BIO_2026, BIGTEN_MSOC_STATS_2025, BBALL_D2_CONFERENCES, BBALL_D2_COACHES_FCP/WEB, FIELD_HOCKEY_HEAD_COACHES, ROSTER_COACH_CONTACTS, SCORECARD_NAME_IDS). Se cargan como el resto en `loadData()`. El código pasó de 1,4 MB a 1,1 MB.

## Seguridad de la IA de mails (29/10/2026)
`/api/generate-email` exige sesión (token de Supabase en `Authorization: Bearer`, verificado contra `/auth/v1/user`) y limita a 40 borradores por hora por usuario (en memoria de cada instancia; para un tope firme, sumar una regla de Rate Limiting en Cloudflare). Antes cualquiera que falsificara el origen podía gastar la clave de Anthropic.
