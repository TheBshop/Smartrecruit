# Convierte crudo/stats_d2f_2025.txt y crudo/coaches_d2f_2026.txt (extraídos de los sitios Sidearm) en:
#   datos/SOCCER_D2F_STATS_2025.json  {school: [[name,gp,gs,min,g,a,pts,sh,sog(,ga,sv)],...]}
#   y suma los entrenadores a datos/COACH_CONTACTS_BY_PROGRAM.json con clave "Universidad|Soccer|F".
# Uso: python3 cargar_d2f_2025.py   (desde datos-src/planteles_web)
import json,re,unicodedata,os,sys
R=os.path.dirname(os.path.abspath(__file__)); D=os.path.join(R,'..','..','datos')
EXTRA={ # hosts resueltos con búsqueda web -> nombre en el catálogo
 'gobarrybucs.com':'Barry University','gannonsports.com':'Gannon University','goshorterhawks.com':'Shorter University',
 'fightingfalcons.com':'Fairmont State University','frostburgsports.com':'Frostburg State University','roadrunnersathletics.com':'Metropolitan State University of Denver',
 'gogriffons.com':'Missouri Western State University','ungathletics.com':'University of North Georgia','nsuwolves.com':'Northern State University',
 'rockathletics.com':'Slippery Rock University','uwaathletics.com':'University of West Alabama','swuathletics.com':'Southern Wesleyan University',
 'gswcanes.com':'Georgia Southwestern State University','lmurailsplitters.com':'Lincoln Memorial University','umobilerams.com':'University of Mobile',
 'hilltoppersports.com':'West Liberty University','athletics.walsh.edu':'Walsh University','govalkyries.com':'Converse University','cuigoldeneagles.com':'Concordia University – Irvine','cspbears.com':'Concordia University, St. Paul – Minnesota','yellowjackets.cedarville.edu':'Cedarville University','csusbathletics.com':'California State University – San Bernardino','lagoldeneagles.com':'California State University – Los Angeles','aumathletics.com':'Auburn University – Montgomery','fhsuathletics.com':'Fort Hays State University','gcsubobcats.com':'Georgia College & State University',
 'athletics.biola.edu':'Biola University','gotoros.com':'California State University – Dominguez Hills',
}
hosts={}
for l in open(os.path.join(R,'hosts_d2f.txt'),encoding='utf8'):
    if l.startswith('#') or '|' not in l: continue
    h,s=[x.strip() for x in l.split('|',1)]; hosts[h]=s.rstrip('?').strip()
hosts.update(EXTRA)
def blocks(path):
    out={};cur=None
    for l in open(path,encoding='utf8'):
        l=l.rstrip('\n')
        if l.startswith('#'): cur=l[1:].split('|')[0]; out[cur]=[]   # el último bloque de cada host manda
        elif cur and l: out[cur].append(l)
    return out
def ascii_key(n): return re.sub(r'\s+',' ',''.join(c for c in unicodedata.normalize('NFD',n) if unicodedata.category(c)!='Mn')).strip().lower()
PART={'de','da','van','von','del','la','di','do','dos','der','le','y','du','das','al','el','bin'}
def cap(w): return w if (not w or w[0].isupper() or w.lower() in PART or not w[0].isalpha()) else w[0].upper()+w[1:]
def norm_name(n):
    n=re.sub(r'\s+',' ',n).strip()
    if ',' in n: a,b=[x.strip() for x in n.split(',',1)]; n=f'{b} {a}'
    return ' '.join(cap(w) for w in n.split(' '))
def num(x):
    x=x.strip()
    if x=='': return None
    try: return int(x)
    except: return None
def mins(x): 
    try: return int(float(x.split(':')[0]))
    except: return None
stats={};missing=set()
for h,lines in blocks(os.path.join(R,'crudo/stats_d2f_2025.txt')).items():
    sc=hosts.get(h) or hosts.get(h.replace('www.',''))
    if not sc: missing.add(h); continue
    pl={};order=[]
    for l in lines:
        p=l.split('|')
        if p[0]=='S':
            nm=norm_name(p[1]); k=ascii_key(nm); row=[num(x) for x in p[2:10]]
            if k in pl:
                for i in range(len(row)): pl[k][1+i]=(pl[k][1+i] or 0)+(row[i] or 0) if row[i] is not None or pl[k][1+i] is not None else None
            else: pl[k]=[nm]+row; order.append(k)
    for l in lines:
        p=l.split('|')
        if p[0]=='G':
            k=ascii_key(norm_name(p[1])); ga,sv=num(p[5]),num(p[6])
            if k in pl and len(pl[k])==9: pl[k]+=[ga,sv]
            elif k in pl and ga is not None: pl[k][9]=(pl[k][9] or 0)+ga; pl[k][10]=(pl[k][10] or 0)+(sv or 0)
    stats[sc]=[pl[k] for k in order]
json.dump(stats,open(os.path.join(D,'SOCCER_D2F_STATS_2025.json'),'w',encoding='utf8'),ensure_ascii=False,separators=(',',':'))
print('stats:',len(stats),'escuelas;','sin catálogo:',sorted(missing))
# ---- entrenadores
KEEP=re.compile(r'coach|assistant|head|goalkeep|interim|recruit',re.I); DROP=re.compile(r'student|communicat|trainer|sports info|strength|athletic director$|administrator|equipment',re.I)
cc=json.load(open(os.path.join(D,'COACH_CONTACTS_BY_PROGRAM.json'),encoding='utf8')); n=0
for h,lines in blocks(os.path.join(R,'crudo/coaches_d2f_2026.txt')).items():
    sc=hosts.get(h) or hosts.get(h.replace('www.',''))
    if not sc or h.startswith('wusports'): 
        if sc is None: print('coach sin catálogo',h)
    if not sc: continue
    staff=[]
    for l in lines:
        p=l.split('|')
        if p[0]!='C' or len(p)<4: continue
        name,title,em=p[1].strip(),p[2].strip(),p[3].strip()
        if h=='wusports.com' and not title: name=' '.join(w.capitalize() for w in em.split('@')[0].split('.'))  # sitio sin cargo: se deduce nombre del mail
        if title and (not KEEP.search(title) or DROP.search(title)): continue
        if not title and not em: continue
        staff.append((name,title,em))
    head=next((s for s in staff if re.search(r'head|interim',s[1],re.I) and not re.search(r'associate|assistant|graduate|volunteer',s[1],re.I)),None)
    if not head and not any(s[2] for s in staff): continue
    if not head: head=next(s for s in staff if s[2]) if not any(re.search(r'coach',s[1],re.I) for s in staff) else None
    if not head: continue
    ass=[{'name':s[0],'email':s[2].lower()} for s in staff if s is not head and s[2]]
    cc[f'{sc}|Soccer|F']={'name':head[0],'title':('Head Coach' if re.search(r'head|interim',head[1],re.I) else None),'email':head[2].lower() or None,'generic':False,'updated':'2026-10-28','assistants':ass,'source':'sitio oficial del programa'}; n+=1
json.dump(cc,open(os.path.join(D,'COACH_CONTACTS_BY_PROGRAM.json'),'w',encoding='utf8'),ensure_ascii=False,separators=(',',':'))
print('contactos D2F agregados:',n)
