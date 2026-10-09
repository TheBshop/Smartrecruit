"""Auditoría y limpieza de COACH_CONTACTS_BY_PROGRAM (RosterReal.jsx).

Uso:  python3 contactos_auditoria.py <RosterReal.jsx>

Lee la constante, aplica las reglas de abajo y escribe en la carpeta actual:
  - CC_clean.json   el contenido limpio, para reemplazar la constante
  - clean_log.json  qué se quitó o corrigió y por qué
Sobre datos ya limpios no cambia nada: sirve para revisar cada lote nuevo de contactos antes de publicarlo.

Reglas:
  - Universidad equivocada: el dominio del mail tiene que ser el del sitio de la universidad (NCSA / EADA) o estar en OKDOM.
    Si corresponde a otra universidad del catálogo (MOVE o dominio único), el contacto se reasigna; si no, se descarta.
  - Deporte o rama equivocados según el cargo (softball, "Men's" en un equipo femenino, etc.) y cargos que no son de coach.
  - Mails: formato válido, uno solo por contacto; los de equipo (msoccer@, volleyball@) se marcan generic; los de otra
    persona o de la institución (accessibility@, webmaster@) se quitan.
  - Nombres: sin año de egreso ("Chris Murphy '06"), sin "Dr.", sin apodos entre paréntesis, sin mayúsculas sostenidas.
  - Asistentes: sin mail si es el del principal, si lo comparten varias personas o si no es institucional (.edu).
  - Una sola entrada por programa (se descarta la clave u:<unitid> si ya está la clave por nombre).
"""
import re,json,collections,sys,unicodedata
src=open(sys.argv[1],encoding="utf-8").read()
def const(name):
    i=src.index('const '+name+' = ')+len('const '+name+' = ')
    return json.JSONDecoder().raw_decode(src[i:])[0]
CC=const('COACH_CONTACTS_BY_PROGRAM'); LEG=const('ROSTER_COACH_CONTACTS'); STAFF=const('STAFF_BY_PROGRAM'); NEW=const('BBALL_D2_COACHES_2026')
EADA=const('EADA_DATA'); SITE=const('EADA_SITE_NAMES')
def norm(s): return re.sub(r'[^a-z]','',unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower())
TEAM=r'soccer|socc|futbol|basket|bball|hoops|volley|vball|vb$|^vb|hockey|rugby|coach|recruit|team|mbb|wbb|mbk|msoc|wsoc|wvb|\bfh\b|program|staff|^m?w?soc'
DEPT=r'access|webmaster|^info$|admission|^athletics?$|athletics$|sportsinfo|rec-?sports|^sports$|complian|ticket'
def toks(name):
    name=re.sub(r"\(.*?\)|[’'‘]\d\d.*$|,.*$|\b(jr|sr|ii|iii|iv|dr|ph\.?d)\b\.?",' ',name,flags=re.I)
    return [norm(t) for t in name.replace('-',' ').split() if norm(t)]
def match(name,email):
    """True si el mail parece ser de esa persona."""
    loc=email.split('@')[0].lower(); l=norm(loc); t=toks(name)
    if not t or not l: return False
    first,last=t[0],t[-1]
    for x in t:
        if len(x)>=4 and x[:4] in l: return True
        if len(x)==3 and x in l: return True
    for x in t[1:]:
        if len(x)>=3 and x[:3] in l and l[0]==first[0]: return True
    ini=''.join(x[0] for x in t)
    if len(l)<=4 and (l.startswith(first[0]) or l.endswith(last[0])): return True
    if l[:2]==first[0]+last[0] or l[:2]==last[0]+first[0]: return True
    if len(ini)>=3 and l.startswith(ini[:3]): return True
    return False
NCSA=const('SCHOOL_PROFILES_NCSA'); PROG=const('PROGRAMS_ALL_SPORTS')
catalog={p['School'] for p in PROG}
byu={e['u']:e for e in EADA}
SITEINV=collections.defaultdict(list)
for n,u in SITE.items(): SITEINV[u].append(n)
LOG=collections.defaultdict(list)
def reg(h):
    h=re.sub(r'^https?://','',(h or '').lower()).split('/')[0].split(':')[0]; p=h.split('.')
    return '.'.join(p[-2:]) if len(p)>=2 else h
def doms_of(name):
    d=set(); w=(NCSA.get(name) or {}).get('website')
    if w: d.add(reg(w))
    u=SITE.get(name)
    if u in byu and byu[u].get('web'): d.add(reg(byu[u]['web']))
    return d
dom2school=collections.defaultdict(set)
for n in catalog:
    for d in doms_of(n): dom2school[d].add(n)
# dominios que son legítimos aunque no coincidan con el sitio institucional (verificados a mano)
OKDOM={'Emmanuel University – Georgia':'ec.edu','Maine Maritime Academy':'mma.edu','Ursuline College':'gannon.edu','Belmont Abbey College':'bac.edu',
 'Charleston Southern University':'csuniv.edu','Illinois State University':'ilstu.edu','Indiana State University':'indstate.edu','Kansas State University':'kstatesports.com',
 'Texas State University':'txstate.edu','University of Maine':'maine.edu','University of New Orleans':'lsuneworleans.edu','Wichita State University':'goshockers.com',
 'College of Charleston':'cofc.edu','Illinois Institute of Technology':'illinoistech.edu','Mansfield University of Pennsylvania':'mansfield.edu','North Central College':'noctrl.edu',
 'Principia College':'principia.edu','Springfield College':'springfieldcollege.edu','Syracuse University':'syr.edu','University of Alaska – Fairbanks':'alaska.edu',
 'University of Delaware':'gmail.com','University of Louisville':'gocards.com','University of Maine at Presque Isle':'maine.edu','University of Mount Saint Vincent':'umsv.edu',
 'University of Nebraska at Omaha':'omavs.com','University of the Incarnate Word':'uiwtx.edu','Vermont State University – Castleton':'vermontstate.edu',
 'Virginia Wesleyan University':'batten.edu','Washington University in St. Louis':'wustl.edu','Bloomsburg University of Pennsylvania':'bloomu.edu','George Washington University':'gmail.com',
 'St. John Fisher College':'sjfc.edu','Catholic University of America':'cua.edu','Lock Haven University':'lockhaven.edu','Westminster College – Missouri':'westminster-mo.edu',
 'University of Southern Maine':'onmicrosoft.com','University of Washington':'uw.edu'}
# destino cuando el dominio no alcanza para decidir solo
MOVE={'murraystate.edu':'Murray State University','ic.edu':'Illinois College','uconn.edu':'University of Connecticut','uw.edu':'University of Washington',
 'cornellcollege.edu':'Cornell College','gcsu.edu':'Georgia College & State University','maryvillecollege.edu':'Maryville College','mc.edu':'Mississippi College',
 'monmouthcollege.edu':'Monmouth College','pacificu.edu':'Pacific University','regis.edu':'Regis University','ric.edu':'Rhode Island College','salem.edu':'Salem College',
 'wesleyancollege.edu':'Wesleyan College','wilmington.edu':'Wilmington College','ozarks.edu':'University of the Ozarks','stthomas.edu':'University of St. Thomas – Minnesota',
 'stthom.edu':'University of St. Thomas – Texas','union.edu':'Union College – New York','sjcme.edu':"Saint Joseph's College of Maine",'ycp.edu':'York College of Pennsylvania',
 'york.cuny.edu':'York College – New York','kean.edu':'Kean University','ucwv.edu':'University of Charleston'}
EMAIL=r"[A-Za-z0-9._%+'-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}"
def fix_email(e,k):
    e=(e or '').strip()
    if not e: return ''
    if re.fullmatch(EMAIL,e): return e
    m=re.findall(EMAIL,e.replace(' .','.').replace('. ','.'))
    LOG['mail con formato inválido corregido'].append((k,e,m[0] if m else ''))
    return m[0] if m else ''
def fix_name(n):
    o=n
    n=re.sub(r"\s*\(?[’'‘]\d\d.*$",'',n)          # años de egreso: Chris Murphy '06
    n=re.sub(r"\s*\((?!.*\)\s*\w)[^)]*\)\s*$",'',n) # paréntesis al final
    n=re.sub(r"\s*\([^)]*\)\s*",' ',n)             # apodo o apellido de soltera en el medio
    n=re.sub(r"^Dr\.?\s+",'',n); n=re.sub(r",?\s+(PH\.?D\.?|Ed\.M\.?|M\.Ed\.?)$",'',n,flags=re.I)
    n=re.sub(r",\s*(Jr|Sr)\.?$",r' \1.',n); n=re.sub(r"[,\s]+$",'',n)
    if n.isupper(): n=' '.join(w.capitalize() for w in n.split())
    return re.sub(r'\s+',' ',n).strip()
OTHER_PERSON={'beckv@nmsu.edu','lori.landino@qu.edu','tmilchman@ualr.edu','rjchampa@central.uh.edu','caleigh.cookson@mso.umt.edu','sfuta@nd.edu','lambriz2@utep.edu',
 'nicholas.bowman@utsa.edu','haley.langstraat@usu.edu','nmagee@goshockers.com','donn.groth@mnstate.edu','sellari@rose-hulman.edu','email.mscoccer@umich.edu'}
DROP={'University of Kentucky|Basketball|M'}  # el único contacto era un asistente con el mail de otra persona
NONCOACH=r"special assistant|executive assistant|executive to|s&c|sports performance|player development|athletic administrator"
out={}
src={k:v for k,v in CC.items()}
for k,v in src.items():
    v=json.loads(json.dumps(v)); school,sp,g=k.split('|')
    if sp=='Basketball' and v.get('updated')=='2026-10-02': LOG['lote de básquet que era staff de fútbol'].append((k,v['name'],v.get('title'))); continue
    t=(v.get('title') or '')
    if k in DROP: LOG['principal que no es coach'].append((k,v['name'],t)); continue
    if re.search(NONCOACH,t,re.I): LOG['principal que no es coach'].append((k,v['name'],t)); continue
    if g=='F' and re.search(r"(?<!wo)\bmen'?s\b",t,re.I) and not re.search(r"women",t,re.I): LOG['rama cruzada'].append((k,v['name'],t)); continue
    if re.search(r'softball',t,re.I) and not re.search(CONTACT:=r'soccer|basket|volley|hockey|rugby',t,re.I): LOG['otro deporte'].append((k,v['name'],t)); continue
    v['email']=fix_email(v.get('email'),k)
    # --- universidad equivocada ---
    if not school.startswith('u:') and v['email']:
        ed=reg(v['email'].split('@')[-1]); full=v['email'].split('@')[-1].lower()
        doms=doms_of(school)
        if doms and ed not in doms and OKDOM.get(school)!=ed:
            dest=MOVE.get(full) or MOVE.get(ed)
            if not dest:
                c=dom2school.get(ed,set())-{school}
                dest=next(iter(c)) if len(c)==1 else None
            LOG['universidad equivocada'].append((k,v['email'],dest))
            if dest and (dest in catalog or dest in SITE):
                nk=f'{dest}|{sp}|{g}'; du=SITE.get(dest)
                taken=[f'{n}|{sp}|{g}' for n in ([dest]+SITEINV.get(du,[]))]+[f'u:{du}|{sp}|{g}']
                if sp=='Basketball' and any(n in NEW for n in [dest]+SITEINV.get(du,[])): taken.append(k)
                if not any(x in src or x in out for x in taken):
                    out[nk]=v; LOG['  → reasignada a la universidad correcta'].append((k,nk))
            continue
    out[k]=v
# Seattle U: el coach masculino cargado también como femenino
k="Seattle University|Soccer|F"
if k in out and out[k]['name']==out.get("Seattle University|Soccer|M",{}).get('name'): LOG['rama cruzada'].append((k,out[k]['name'],out[k]['title'])); del out[k]
# --- duplicados u:<id> vs nombre ---
for k in [k for k in out if k.startswith('u:')]:
    u=int(k.split('|')[0][2:]); rest=k.split('|',1)[1]
    for n in SITEINV.get(u,[]):
        o=out.get(f'{n}|{rest}')
        if o and o['name']==out[k]['name']:
            LOG['duplicado (misma universidad con dos claves)'].append((k,n)); del out[k]; break
# --- por persona ---
for k,v in out.items():
    school,sp,g=k.split('|')
    nn=fix_name(v['name'])
    if nn!=v['name']: LOG['nombre limpiado'].append((k,v['name'],nn)); v['name']=nn
    e=v['email']; loc=e.split('@')[0].lower()
    if e:
        if re.search(r'access|webmaster|^info$|onmicrosoft',e.lower()): LOG['mail del principal quitado (no es del programa)'].append((k,v['name'],e)); v['email']=''
        elif e.lower() in OTHER_PERSON: LOG['mail del principal quitado (es de otra persona)'].append((k,v['name'],e)); v['email']=''
        elif match(v['name'],e) or re.match(r'coach[a-z]{3,}$',loc): v['generic']=False
        elif re.search(TEAM,loc) or re.search(DEPT,loc):
            if not v.get('generic'): LOG['marcado como mail del programa'].append((k,v['name'],e))
            v['generic']=True
    A=[]; seen={norm(v['name'])}
    for a in v.get('assistants') or []:
        an=fix_name(a.get('name') or '')
        if len(an.split())<2 or re.search(r'\b(staff|coach|coaches|coaching|tba|tbd|vacant)\b',an,re.I): LOG['asistente quitado (no es una persona)'].append((k,a.get('name'))); continue
        if norm(an) in seen: continue
        seen.add(norm(an))
        ae=fix_email(a.get('email'),k) if a.get('email') else ''
        A.append({'name':an,'email':ae})
    v['assistants']=A
# mails de asistentes: fuera si son el del principal, si los comparten varias personas, o si son de la institución
for k,v in out.items():
    cnt=collections.Counter(a['email'].lower() for a in v['assistants'] if a['email'])
    for a in v['assistants']:
        e=a['email'].lower()
        if not e: a.pop('email'); continue
        loc=e.split('@')[0]
        if e==(v.get('email') or '').lower() or cnt[e]>1 or not re.search(r'\.(edu|ca)$',e) or re.search(DEPT,loc) or re.search(r'onmicrosoft',e) or (not match(a['name'],e) and any(match(x,e) for x in [v['name']]+[b['name'] for b in v['assistants'] if b is not a])) or (re.search(TEAM,loc) and not match(a['name'],e)):
            LOG['mail de asistente quitado (compartido o no personal)'].append((k,a['name'],e)); a.pop('email')
    if not v['assistants']: v.pop('assistants')
# un mismo mail personal en dos deportes de la misma universidad
def uid(k):
    s=k.split('|')[0]; return int(s[2:]) if s.startswith('u:') else SITE.get(s,s)
ppl=collections.defaultdict(set)
for k,v in out.items():
    for a in v.get('assistants') or []:
        if a.get('email'): ppl[(uid(k),a['email'].lower())].add((k.split('|')[1],a['name']))
for k,v in out.items():
    for a in v.get('assistants') or []:
        e=(a.get('email') or '').lower()
        if e and len({n for _,n in ppl[(uid(k),e)]})>1: LOG['mail de asistente quitado (compartido o no personal)'].append((k,a['name'],e)); a.pop('email')
json.dump(out,open('CC_clean.json','w'),ensure_ascii=False)
json.dump(LOG,open('clean_log.json','w'),ensure_ascii=False,indent=0)
print(len(src),'->',len(out))
for c,l in LOG.items(): print(f'{len(l):5d}  {c}')
for c in ['universidad equivocada','mail del principal quitado (es de otra persona)','mail del principal quitado (no es del programa)','principal que no es coach','rama cruzada','otro deporte','mail con formato inválido corregido','asistente quitado (no es una persona)']:
    print('\n##',c)
    for x in LOG[c]: print('  ',x)
print('\n## nombre limpiado'); print([ (a,b) for _,a,b in LOG['nombre limpiado']])
print('no reasignadas:',[x for x in LOG['universidad equivocada'] if x[0] not in {a for a,_ in LOG['  → reasignada a la universidad correcta']}])
print('\n## marcado programa', [(n,e) for _,n,e in LOG['marcado como mail del programa']][:400])
