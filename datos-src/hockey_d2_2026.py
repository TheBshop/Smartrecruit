# Genera HOCKEY_D2_STATS_2026 y HOCKEY_D2_BIO_2026 (hockey sobre césped NCAA D2, temporada 2026 en curso).
# Entrada: fh_D2_ALL.json (tablas /stats y /roster de cada sitio Sidearm, clave H) y la tabla HOSTS de abajo (sitio -> universidad del catálogo).
# Uso: python3 hockey_d2_2026.py <dir_scratch> <hockey_d1_bio.py> <fh_D2_ALL.json>
import json,re,sys,unicodedata
SC=sys.argv[1]; HB=sys.argv[2]; FHJ=sys.argv[3]

src=open(HB,encoding='utf8').read()
a=src.index('STATES="'); b=src.index('out={};stats={}')
exec(compile('import re,unicodedata\n'+src[a:b],'hb','exec'),globals())   # classify, parse_row, parse_txt, key, pos_n, cls_n
HOSTS={'aupanthers.com':'Adelphi University','aicyellowjackets.com':'American International College','assumptiongreyhounds.com':'Assumption University','abbeyathletics.com':'Belmont Abbey College','bentleyfalcons.com':'Bentley University','dyusaints.com':"D'Youville University",'fpuravens.com':'Franklin Pierce University','frostburgsports.com':'Frostburg State University','iupathletics.com':'Indiana University of Pennsylvania','landerbearcats.com':'Lander University','www.lockhavenathletics.com':'Lock Haven University','maryvillesaints.com':'Maryville University','mercyathletics.com':'Mercy University','molloylions.com':'Molloy University','newberrywolves.com':'Newberry College','paceuathletics.com':'Pace University','robertsredhawks.com':'Roberts Wesleyan University','saintanselmhawks.com':'Saint Anselm College','smcathletics.com':"Saint Michael's College",'shipraiders.com':'Shippensburg University of Pennsylvania','rockathletics.com':'Slippery Rock University','scsuowls.com':'Southern Connecticut State University','snhupenmen.com':'Southern New Hampshire University','wingatebulldogs.com':'Wingate University'}
D=json.load(open(FHJ)); hosts={h:[n] for h,n in HOSTS.items()}
res={f'{h}|H|{n}':n for h,ns in hosts.items() for n in ns}
def getd(host):
    for h in (host,'www.'+host):
        if h and h in D: return D[h]
def num(x):
    x=(x or '').replace(',','').strip()
    try: return float(x) if '.' in x else int(x)
    except: return None
def name(s):
    s=re.sub(r'\s+',' ',s.strip())
    m=re.match(r'^([^,\d]+),\s*([^\d,]+?)\s+\d+\S',s)       # "Apellido, Nombre 12Apellido, Nombre"
    if m: return (m.group(2).strip()+' '+m.group(1).strip()).strip()
    m=re.match(r'^([^\d,]+?)\s+\d+[^,]*,\s*(.+)$',s)           # "Nombre 12Apellido, Nombre Apellido"
    if m: return m.group(2).strip()
    if ',' in s:
        a,b=s.split(',',1); s=b.strip()+' '+a.strip()
    return s
def posn(p):
    p=(p or '').lower()
    if p in ('gk',) or p.startswith(('goalkeeper','goalie')): return 'GK'
    if p.startswith('midfield'): return 'M'
    if p.startswith('forward') or p.startswith('atk') or p.startswith('attack'): return 'F'
    if p.startswith('defens'): return 'D'
    return p.upper() if p else ''
def low(h): return [x.lower().split(' ')[0] for x in h]
def stats_table(o):
    for t in o.get('t',[]):
        h=low(t['h'])
        if 'player' in h and 'g' in h and 'a' in h: return h,t['r']
SEAS='2026 (en curso)'
S={'H':{}}; B={'H':{}}; rep=[]
for k,school in res.items():
    host,g,_n=k.split('|'); v=getd(host)
    if not v or not v.get(g): continue
    o=v[g]; st=stats_table(o)
    if not st: continue
    h,rows=st; ix={}
    for i,x in enumerate(h):
        if x and x not in ix: ix[x]=i
    gv=lambda r,c:(num(r[ix[c]]) if c in ix and ix[c]<len(r) else None)
    pl=[]
    for r in rows:
        if len(r)<4: continue
        nm=r[ix['player']]
        if not nm or re.match(r'(?i)^(total|opponents?|team)',nm): continue
        gp=gv(r,'gp')
        if not gp: continue
        gl=gv(r,'g') or 0; asx=gv(r,'a') or 0
        pts=gv(r,'pts'); pts=pts if pts is not None else gl*2+asx
        pl.append([name(nm),gp,gv(r,'gs'),gv(r,'min'),gl,asx,pts,gv(r,'sh'),gv(r,'sog')])
    for t in o.get('t',[]):   # arqueras: tabla con GA/SV (minutos "mm:ss")
        hg=low(t['h'])
        if 'player' in hg and 'sv' in hg and 'ga' in hg:
            ig={x:i for i,x in reversed(list(enumerate(hg)))}
            for r in t['r']:
                if len(r)<4: continue
                nmg=r[ig['player']]
                if not nmg or re.match(r'(?i)^(total|opponents?|team)',nmg): continue
                gpg=num(r[ig['gp']]) if 'gp' in ig else None
                if not gpg: continue
                mn=None
                if 'min' in ig and ig['min']<len(r):
                    m_=re.match(r'^(\d+):(\d+)$',r[ig['min']].strip())
                    mn=int(m_.group(1)) if m_ else num(r[ig['min']])
                gn=name(nmg); gsv=num(r[ig['gs']]) if 'gs' in ig else None
                ex=[p for p in pl if p[0]==gn]
                if ex:
                    p=ex[0]; p[1]=max(p[1] or 0,gpg); p[2]=max(p[2] or 0,gsv or 0); p[3]=max(p[3] or 0,mn or 0) or None
                else: pl.append([gn,gpg,gsv,mn,0,0,0,None,None])
    pl.sort(key=lambda p:(-p[6],-p[4]))
    if len(pl)<8: rep.append(('pocas',school,g,len(pl))); continue
    S[g][school]=pl
    # bio
    rrows=[]
    for t in o.get('rt') or []:
        hh=[x.lower() for x in t['h']]
        if any(x in ('name','full name') for x in hh) and any(x.startswith('pos') for x in hh):
            for r in t['r']: rrows.append({hh[i]:r[i] for i in range(min(len(hh),len(r)))})
            break
    if not rrows:
        for c in o.get('cards') or []: rrows.append({'txt':c})
    idx={}
    for p in pl: idx.setdefault(key(p[0]),p[0])
    bio={}
    for r in rrows:
        try: pr=parse_row(r)
        except Exception: pr=None
        if not pr: continue
        nm,pos,cl,ht,hs=pr
        kk=key(nm)
        if kk in idx:
            hm,c=classify(ht); bio[idx[kk]]=[posn(pos_n(pos)),cls_n(cl),hm,c]
    B[g][school]=bio
    rep.append(('ok',school,g,len(pl),len(bio),sum(1 for b in bio.values() if b[3])))
oks=[r for r in rep if r[0]=='ok']
for g in 'H':
    n=[r for r in oks if r[2]==g]
    print(g,'programas',len(n),'jugadoras',sum(r[3] for r in n),'con bio',sum(r[4] for r in n),'con país',sum(r[5] for r in n))
print([r for r in rep if r[0]!='ok'])
nob=[(r[1],r[2],r[3],r[4]) for r in oks if r[4]<r[3]*0.5]; print('bio <50%:',len(nob),nob[:40])
for g in 'H':
    miss=[c for c in [] if c not in S[g]]
    print('catálogo sin stats',g,len(miss),miss)
json.dump({'S':S,'B':B},open(SC+'/fh_d2_built.json','w'),ensure_ascii=False)
js='const HOCKEY_D2_STATS_2026 = '+json.dumps(S,ensure_ascii=False,separators=(',',':'))+';\nconst HOCKEY_D2_BIO_2026 = '+json.dumps(B,ensure_ascii=False,separators=(',',':'))+';\n'
open(SC+'/fh_d2_const.js','w',encoding='utf8').write(js); print('bytes',len(js.encode()))
