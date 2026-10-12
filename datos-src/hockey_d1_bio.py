# Une los planteles (ciudad, pais, posicion, clase) de cada universidad con HOCKEY_PARTIAL_STATS_2026.
# Entrada: fhr_ALL.json (paginas /roster bajadas el 12/10/2026) + roster_urls.json. Salida: fh_bio.js
import json,re,sys,unicodedata
SC=sys.argv[1]  # scratchpad fh dir
ALL=json.load(open(sys.argv[2])); URLS=json.load(open(SC+'/roster_urls.json')); NEW=json.load(open(SC+'/fh_new.json'))
host2cat={u.split('/')[2]:c for c,u in URLS.items()} if isinstance(URLS,dict) else {u.split('/')[2]:c for c,u in URLS}
host2cat.update({'0':'Appalachian State University','1':'Ball State University','2':'Bellarmine University','3':'Boston University'})
STATES="Ala. Alaska Ariz. Ark. Calif. Colo. Conn. Del. Fla. Ga. Hawaii Idaho Ill. Ind. Iowa Kan. Ky. La. Maine Md. Mass. Mich. Minn. Miss. Mo. Mont. Neb. Nev. N.H. N.J. N.M. N.Y. N.C. N.D. Ohio Okla. Ore. Pa. R.I. S.C. S.D. Tenn. Texas Utah Vt. Va. Wash. W.Va. Wis. Wyo. D.C. Puerto".split()
ST2="AL AK AZ AR CA CO CT DE FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY DC".split()
PROV={"Ont.":"Canada","B.C.":"Canada","Alta.":"Canada","Que.":"Canada","Ontario":"Canada","Manitoba":"Canada","Nova Scotia":"Canada","Alberta":"Canada","British Columbia":"Canada"}
FOREIGN="England Scotland Wales Ireland Northern Ireland Netherlands Germany Argentina Chile Spain India South Africa Canada Australia New Zealand Belgium France Mexico Japan Brazil Uruguay Italy Zimbabwe Kenya Nigeria Ghana Hong Kong China Singapore Malaysia Pakistan Switzerland Austria Sweden Denmark Norway Poland Czech Republic Colombia Peru Venezuela Ecuador Costa Rica Panama Trinidad Jamaica Bermuda Barbados Bahamas Namibia Zambia Botswana Egypt Turkey Greece Portugal Russia Ukraine Lithuania Latvia Estonia Finland Korea South Korea Philippines Thailand Vietnam Israel Cayman Islands".split(' ')
FOREIGN=sorted(set(["England","Scotland","Wales","Ireland","Northern Ireland","Netherlands","Germany","Argentina","Chile","Spain","India","South Africa","Canada","Australia","New Zealand","Belgium","France","Mexico","Japan","Brazil","Uruguay","Italy","Zimbabwe","Kenya","Nigeria","Ghana","Hong Kong","China","Singapore","Malaysia","Pakistan","Switzerland","Austria","Sweden","Denmark","Norway","Poland","Czech Republic","Colombia","Peru","Venezuela","Ecuador","Costa Rica","Panama","Trinidad","Jamaica","Bermuda","Barbados","Bahamas","Namibia","Zambia","Botswana","Egypt","Turkey","Greece","Portugal","Russia","Ukraine","Lithuania","Latvia","Estonia","Finland","South Korea","Korea","Philippines","Thailand","Vietnam","Israel","Cayman Islands","UK","United Kingdom","Luxembourg","Hungary","Slovakia","Romania","Serbia","Croatia","Slovenia","Bulgaria","Tanzania","Uganda","Rwanda","Malta","Cyprus","Iceland","Taiwan","Indonesia","Sri Lanka","Bangladesh","Nepal","Guatemala","Dominican Republic","Puerto Rico","The Netherlands","Paraguay","Belguim","U.K.","(U.K.)","Holland"]),key=lambda s:-len(s))
REG={"Netherlands":"Zuid-Holland Noord-Brabant Noord-Holland South-Holland North-Holland South Holland North Holland Utrecht Gelderland Limburg Overijssel Friesland Flevoland Zeeland Groningen Drenthe Brabant".split(),
"England":"Surrey Kent Essex Sussex Suffolk Yorkshire Devon Hampshire Cheshire Berkshire Hertfordshire Oxfordshire Lancashire Cornwall Somerset Norfolk Dorset Buckinghamshire Middlesex London Lincolnshire Cumbria Durham Northumberland Staffordshire Warwickshire Leicestershire Derbyshire Nottinghamshire Gloucestershire Wiltshire Bedfordshire Cambridgeshire".split()}
FULL="Alabama Alaska Arizona Arkansas California Colorado Connecticut Delaware Florida Georgia Hawaii Idaho Illinois Indiana Iowa Kansas Kentucky Louisiana Maine Maryland Massachusetts Michigan Minnesota Mississippi Missouri Montana Nebraska Nevada New_Hampshire New_Jersey New_Mexico New_York North_Carolina North_Dakota Ohio Oklahoma Oregon Pennsylvania Rhode_Island South_Carolina South_Dakota Tennessee Texas Utah Vermont Virginia Washington West_Virginia Wisconsin Wyoming".replace("_"," ").split() if False else [x.replace("_"," ") for x in "Alabama Alaska Arizona Arkansas California Colorado Connecticut Delaware Florida Georgia Hawaii Idaho Illinois Indiana Iowa Kansas Kentucky Louisiana Maine Maryland Massachusetts Michigan Minnesota Mississippi Missouri Montana Nebraska Nevada New_Hampshire New_Jersey New_Mexico New_York North_Carolina North_Dakota Ohio Oklahoma Oregon Pennsylvania Rhode_Island South_Carolina South_Dakota Tennessee Texas Utah Vermont Virginia Washington West_Virginia Wisconsin Wyoming".split()]
STATES=STATES+FULL
CNAME={"Belguim":"Belgium","The Netherlands":"Netherlands","U.K.":"United Kingdom","(U.K.)":"United Kingdom","Holland":"Netherlands","UK":"England","United Kingdom":"England","Korea":"South Korea","Trinidad":"Trinidad and Tobago"}
CLS=r"(?:Fr\.|So\.|Jr\.|Sr\.|Gr\.|R-Fr\.|R-So\.|R-Jr\.|R-Sr\.|Fr|So|Jr|Sr|Gr|Freshman|Sophomore|Junior|Senior|Graduate|Grad\.|5th|Gr\./Sr\.)"
def classify(h):
    """h = 'Ciudad, Estado/Pais'. Devuelve (hometown, country)."""
    for f in FOREIGN:
        if re.search(r'(?:^|,\s*)'+re.escape(f)+r'$',h,re.I): return h,CNAME.get(f,f.title() if f.islower() else f)
    for c,rs in REG.items():
        for r_ in rs:
            if re.search(r',\s*'+re.escape(r_)+r'$',h) or re.search(r',\s*'+re.escape(r_)+r'(?=\s*\(U\.K\.\))',h): return h,c
    for p,c in PROV.items():
        if re.search(r'(?:^|,\s*)'+re.escape(p)+r'$',h): return h,c
    if re.search(r',\s*(?:'+'|'.join(re.escape(s) for s in STATES)+'|'+'|'.join(ST2)+r')$',h): return h,'USA'
    return h,''
def split_txt(t):
    """texto 'Pos [alt] [#] Nombre Clase Ciudad, Est. Colegio Full Bio ...' """
    t=t.split(' Full Bio')[0]
    m=re.search(r'For (.+)$',t) # no esta: cortamos antes
    return t
def parse_txt(raw):
    mm=re.search(r'Hide/Show Additional Information For (.+)$',raw)
    if not mm: return None
    nm=mm.group(1).strip(); head=raw.split(' Full Bio')[0]
    i=head.lower().find(nm.lower())
    if i<0: return None
    pre=head[:i].strip(); post=head[i+len(nm):].strip()
    pos=re.sub(r"\s*(?:\d+['’]\s*\d+\"?|\d+)\s*$","",pre)
    pos=re.sub(r"\s*\d+['’]\s*\d+\"?\s*",' ',pre).strip()
    pos=re.sub(r"\s*\d+\s*$","",pos).strip()
    cm=re.match(r'('+CLS+r')\s+(.*)$',post)
    cl,rest=(cm.group(1),cm.group(2)) if cm else ('',post)
    # hometown = hasta el primer estado/pais
    best=None
    alts=[re.escape(s) for s in STATES]+ST2 and None
    pat=r',\s*('+'|'.join([re.escape(s) for s in FOREIGN]+[re.escape(p) for p in PROV]+[re.escape(s) for s in STATES]+ST2)+r')(?=\s|$)'
    pat=pat.replace(r',\s*(',r',\s*(?:\()?(',1)
    m=re.search(pat,rest,re.I)
    if m: ht=rest[:m.end()].strip(); hs=rest[m.end():].strip()
    else: ht,hs=rest,''
    return nm,pos,cl,ht,hs
def parse_row(r):
    if 'txt' in r: return parse_txt(r['txt'])
    nm=r.get('name') or r.get('full name')
    if not nm: return None
    pos=r.get('pos.') or r.get('pos') or r.get('position') or ''
    cl=r.get('class') or r.get('yr.') or r.get('yr') or r.get('year') or r.get('academic year') or r.get('cl.') or ''
    ht=(r.get('hometown / high school') or r.get('hometown/high school') or r.get('hometown / high school/club') or r.get('hometown') or '')
    hs=r.get('high school','')
    if ' / ' in ht: ht,hs=ht.split(' / ',1)
    elif '/' in ht and ',' in ht.split('/')[0]: ht,hs=ht.split('/',1)
    return nm,pos,cl,ht.strip(),hs.strip()
def norm(s):
    s=unicodedata.normalize('NFD',s); s=''.join(c for c in s if not unicodedata.combining(c))
    s=s.lower().replace("'",'').replace('.','').replace('-',' ')
    return re.sub(r'[^a-z ]','',s).split()
def key(nm):
    p=norm(nm)
    if ',' in nm: # "Last, First"
        a,b=nm.split(',',1); p=norm(b)+norm(a)
    return (p[0],p[-1]) if p else ('','')
POS={'b':'D','g':'GK','striker':'F','foward':'F','mid':'M','defensd':'D','midfielder':'M','forward':'F','midfielder':'M','midfield':'M','defender':'D','defense':'D','back':'D','goalkeeper':'GK','goalie':'GK','gk':'GK','f':'F','m':'M','d':'D','mf':'M','fw':'F','df':'D','m/f':'M/F','f/m':'M/F','d/m':'D/M','m/d':'D/M','f/d':'F/D','d/f':'F/D'}
def pos_n(p):
    p=p.strip(); q=p.lower().replace(' ','')
    if q in POS: return POS[q]
    parts=[POS.get(x,x) for x in re.split(r'[/,]',q)]
    return '/'.join(dict.fromkeys(parts)) if parts else p
def cls_n(c):
    c=c.strip().replace('R-','').replace('Redshirt ','')
    m={'fy':'Fr','rf':'Fr','fr':'Fr','so':'So','jr':'Jr','sr':'Sr','gr':'Gr','freshman':'Fr','sophomore':'So','junior':'Jr','senior':'Sr','graduate':'Gr','grad':'Gr','5th':'Gr'}
    return m.get(c.lower().replace('.',''),c)
out={};stats={}
for hostk,v in ALL.items():
    cat=host2cat.get(hostk)
    if not cat or cat not in NEW: continue
    rows=v['rows'] if isinstance(v,dict) else v
    players=NEW[cat]; idx={}
    for p in players: idx.setdefault(key(p[0]),[]).append(p[0])
    bio={};unm=0;nm_ct=0
    for r in rows:
        pr=parse_row(r)
        if not pr: continue
        nm,pos,cl,ht,hs=pr; nm_ct+=1
        h,c=classify(ht)
        k=key(nm)
        if k in idx:
            sn=idx[k][0]
            bio[sn]=[pos_n(pos),cls_n(cl),h,c]
    if cat=='Towson University':
        for b_ in bio.values(): b_[2]=''   # la pagina mezcla carrera y ciudad: solo pais
    out[cat]=bio
    stats[cat]=(len(players),nm_ct,len(bio),sum(1 for b in bio.values() if b[3]))
tot=sum(s[0] for s in stats.values()); mt=sum(s[2] for s in stats.values())
print('programas con bio',sum(1 for s in stats.values() if s[2]),'/',len(NEW),'| jugadoras en stats',tot,'| emparejadas',mt)
for c,s in sorted(stats.items(),key=lambda x:x[1][2]/max(x[1][0],1)): print(f'{c:42}stats={s[0]:3} roster={s[1]:3} match={s[2]:3} conPais={s[3]:3}')
missing=[c for c in NEW if c not in out]; print('sin roster leido:',missing)
json.dump(out,open(SC+'/fh_bio.json','w'),ensure_ascii=False)

open(SC+'/fh_bio.js','w',encoding='utf8').write('const HOCKEY_BIO_2026 = '+json.dumps(out,ensure_ascii=False,separators=(',',':'))+';\n')
