# Genera SOCCER_D2M_STATS_2026 y SOCCER_D2M_BIO_2026 (fútbol masculino NCAA D2, temporada 2026 en curso).
# Entrada: soc_D2M.json (tablas /stats y /roster de cada sitio Sidearm), d2m_hosts.json ({sitio: [universidades del catálogo]}), cat_d2.json.
# Uso: python3 futbol_d1_2026.py <dir_scratch> <hockey_d1_bio.py>
import json,re,sys,unicodedata
SC=sys.argv[1]; HB=sys.argv[2]

src=open(HB,encoding='utf8').read()
a=src.index('STATES="'); b=src.index('out={};stats={}')
exec(compile('import re,unicodedata\n'+src[a:b],'hb','exec'),globals())   # classify, parse_row, parse_txt, key, pos_n, cls_n
D=json.load(open(SC+'/soc_D2M.json')); hosts=json.load(open(SC+'/d2m_hosts.json')); cat={'F':[],'M':[n for n,_ in json.load(open(SC+'/cat_d2.json'))['Soccer|M']]}
res={f'{h}|M':ns[0] for h,ns in hosts.items()}
ALIAS={'hsujacks.com':'humboldtathletics.com','gocatawbaindians.com':'catawbaathletics.com','gobucsgo.com':'cbubucs.com','csmorediggers.com':'minesathletics.com','athletics.dyc.edu':'dyusaints.com','felicianathletics.com':'felicianuathletics.com','goleeflames.com':'leeuflames.com','nmhucowboys.com':'nmhuathletics.com','ngcrusaders.com':'www.nguathletics.com','nsuwolvesathletics.com':'nsuwolves.com','www.obubison.com':'obubison.com','pacesettersathletics.com':'paceuathletics.com','athletics.roberts.edu':'robertsredhawks.com','siutigerpride.com':'salemtigers.com','www.shawbears.com':'shawbears.com'}
_unused={'hurricanesports.com':'miamihurricanes.com','icgaels.com':'ionagaels.com','omavs.com':'omahamavs.com','und.com':'fightingirish.com','texassports.com':'texaslonghorns.com','orugoldeneagles.com':'www.orugoldeneagles.com','kstatesports.com':'www.kstatesports.com','www.usctrojans.com':'usctrojans.com'}
def getd(host):
    for h in (ALIAS.get(host),host,'www.'+host):
        if h and h in D: return D[h]
def num(x):
    x=(x or '').replace(',','').strip()
    try: return float(x) if '.' in x else int(x)
    except: return None
def name(s):
    s=re.sub(r'\s+',' ',s.strip())
    if ',' in s:
        a,b=s.split(',',1); s=b.strip()+' '+a.strip()
    return s
def low(h): return [x.lower().split(' ')[0] for x in h]
def stats_table(o):
    for t in o.get('t',[]):
        h=low(t['h'])
        if 'player' in h and 'g' in h and 'a' in h: return h,t['r']
SEAS='2026 (en curso)'
S={'F':{},'M':{}}; B={'F':{},'M':{}}; rep=[]
for k,school in res.items():
    host,g=k.split('|'); v=getd(host)
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
            hm,c=classify(ht); bio[idx[kk]]=[pos_n(pos),cls_n(cl),hm,c]
    B[g][school]=bio
    rep.append(('ok',school,g,len(pl),len(bio),sum(1 for b in bio.values() if b[3])))
oks=[r for r in rep if r[0]=='ok']
for g in 'M':
    n=[r for r in oks if r[2]==g]
    print(g,'programas',len(n),'jugadoras',sum(r[3] for r in n),'con bio',sum(r[4] for r in n),'con país',sum(r[5] for r in n))
print([r for r in rep if r[0]!='ok'])
nob=[(r[1],r[2],r[3],r[4]) for r in oks if r[4]<r[3]*0.5]; print('bio <50%:',len(nob),nob[:40])
for g in 'M':
    miss=[c for c in cat[g] if c not in S[g]]
    print('catálogo sin stats',g,len(miss),miss)
json.dump({'S':S,'B':B},open(SC+'/soc_d2m_built.json','w'),ensure_ascii=False)
js='const SOCCER_D2M_STATS_2026 = '+json.dumps(S,ensure_ascii=False,separators=(',',':'))+';\nconst SOCCER_D2M_BIO_2026 = '+json.dumps(B,ensure_ascii=False,separators=(',',':'))+';\n'
open(SC+'/soc_d2m_const.js','w',encoding='utf8').write(js); print('bytes',len(js.encode()))
