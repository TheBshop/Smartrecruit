# Genera VB_D2_2026 (vóley femenino NCAA D2, temporada 2026 en curso) desde las tablas /stats y /roster de cada sitio Sidearm.
# Entrada: soc_D2V.json ({host:{V:{t:[tablas stats],rt:[tablas roster],cards:[...]}}}), d2v_hosts.json ({host:[universidades del catálogo]}).
# Uso: python3 voley_d2_2026.py <dir_scratch> <hockey_d1_bio.py>
import json,re,sys,unicodedata
SC=sys.argv[1]; HB=sys.argv[2]
src=open(HB,encoding='utf8').read()
a=src.index('STATES="'); b=src.index('out={};stats={}')
exec(compile('import re,unicodedata\n'+src[a:b],'hb','exec'),globals())   # classify, cls_n, key ...
D=json.load(open(SC+'/soc_D2V.json')); hosts=json.load(open(SC+'/d2v_hosts.json'))
ALIAS={'hsujacks.com':'humboldtathletics.com','gocatawbaindians.com':'catawbaathletics.com','gobucsgo.com':'cbubucs.com','csmorediggers.com':'minesathletics.com','athletics.dyc.edu':'dyusaints.com','felicianathletics.com':'felicianuathletics.com','goleeflames.com':'leeuflames.com','nmhucowboys.com':'nmhuathletics.com','ngcrusaders.com':'www.nguathletics.com','nsuwolvesathletics.com':'nsuwolves.com','www.obubison.com':'obubison.com','pacesettersathletics.com':'paceuathletics.com','athletics.roberts.edu':'robertsredhawks.com','siutigerpride.com':'salemtigers.com','www.shawbears.com':'shawbears.com','golhu.com':'www.lockhavenathletics.com','sbubearcats.com':'www.sbubearcats.com','gbcathletics.com':'www.gbcathletics.com'}
def getd(h):
    for x in (ALIAS.get(h),h,'www.'+h):
        if x and x in D: return D[x]
GROUPS={'attack','set','serve','bio link','dig','recept','block','defense','receptions','blocking',''}
def num(x):
    x=(x or '').replace(',','').strip()
    try: return float(x) if '.' in x else int(x)
    except: return None
def nm(s):
    s=re.split(r'\s\d+',re.sub(r'\s+',' ',s.strip()))[0].strip()
    if ',' in s:
        p,q=s.split(',',1); s=q.strip()+' '+p.strip()
    return s
def tab(t):
    h=[x.strip() for x in t['h'] if x.strip().lower() not in GROUPS]
    if 'Player' not in h: return None
    pi=h.index('Player'); cols=h[pi+1:]
    return pi,cols,t['r']
def pos_v(p):
    p=(p or '').upper().replace(' ','')
    if not p: return ''
    f=re.split(r'[/,-]',p)[0]
    m={'S':'S','SET':'S','OH':'OH','OS':'OH','MB':'MB','MH':'MB','MIDDLE':'MB','OPP':'OPP','RS':'OPP','OP':'OPP','L':'L','LIB':'L','DS':'L','DS/L':'L','LIBERO':'L'}
    return m.get(f,'')
def clsv(c):
    try: return cls_n(c)
    except Exception: return ''
S={};B={};rep=[];ok=0
for host,names in hosts.items():
    v=getd(host)
    if not v or not (v.get('V') or {}).get('t'): continue
    o=v['V']; att={};dfn={}
    for t in o['t']:
        r_=tab(t)
        if not r_: continue
        pi,cols,rows=r_
        ix={}
        for i,c in enumerate(cols):
            if c not in ix: ix[c]=i
        isatt='K/S' in ix; isdef='DIG/S' in ix
        for r in rows:
            if len(r)<pi+3: continue
            n=nm(r[pi]); d=r[pi+1:]
            g=lambda c:(num(d[ix[c]]) if c in ix and ix[c]<len(d) else None)
            if not n or re.match(r'(?i)^(total|opponents?|team)',n): continue
            if isatt and n not in att: att[n]={'sp':g('SP'),'ks':g('K/S'),'as':g('A/S'),'pts':g('PTS/S')}
            if isdef and n not in dfn: dfn[n]={'ds':g('DIG/S')}
    # roster
    bio={}
    for t in o.get('rt') or []:
        hh=[x.lower() for x in t['h']]
        nmc=[i for i,x in enumerate(hh) if x in ('name','player','full name')]
        if nmc and any(x.startswith('pos') for x in hh):
            ni=nmc[0]; pj=[i for i,x in enumerate(hh) if x.startswith('pos')][0]
            ci=[i for i,x in enumerate(hh) if x.startswith('cl') or x.startswith('year') or x.startswith('academic') or x=='yr.']; hi=[i for i,x in enumerate(hh) if x.startswith('hometown')]
            for r in t['r']:
                if len(r)<=max(ni,pj): continue
                ht=r[hi[0]] if hi and hi[0]<len(r) else ''
                hm,c=classify(ht)
                bio[nm(r[ni])]=[pos_v(r[pj]),clsv(r[ci[0]]) if ci and ci[0]<len(r) else '',hm,c]
            break
    rows=[]
    for n,a_ in att.items():
        sp=a_['sp']
        if not sp or sp<20 or a_['ks'] is None: continue
        b_=bio.get(n); pos=b_[0] if b_ else ''
        rows.append([n,pos,int(sp),a_['ks'],a_['as'] or 0.0,(dfn.get(n) or {}).get('ds') or 0.0,a_['pts'] or 0.0])
    rows.sort(key=lambda r:-r[6])
    if len(rows)<6: rep.append(('pocas',host,len(rows))); continue
    withpos=sum(1 for r in rows if r[1])
    for school in names:
        S[school]=rows; B[school]={n:b_[1:] for n,b_ in bio.items() if b_[1] or b_[2] or b_[3]}
        rep.append(('ok',school,len(rows),withpos,len(B[school]),sum(1 for b_ in B[school].values() if b_[2])))
oks=[r for r in rep if r[0]=='ok']
print('programas',len(oks),'jugadoras',sum(r[2] for r in oks),'con pos',sum(r[3] for r in oks),'con país',sum(r[5] for r in oks))
print([r for r in rep if r[0]!='ok'])
print('sin posición <50%:',[(r[1],r[2],r[3]) for r in oks if r[3]<r[2]*0.5])
cat=[n for n,_ in json.load(open(SC+'/cat_d2.json'))['Volleyball|F']]
miss=[c for c in cat if c not in S]; print('catálogo sin stats',len(miss),miss)
js='const VB_D2_2026 = '+json.dumps({'data':S,'bio':B},ensure_ascii=False,separators=(',',':'))+';\n'
open(SC+'/vb_d2_const.js','w',encoding='utf8').write(js); print('bytes',len(js.encode()))
