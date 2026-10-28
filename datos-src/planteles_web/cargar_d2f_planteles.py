# Cruza crudo/planteles_d2f_2026.txt (planteles Sidearm 2026) con datos/SOCCER_D2F_BIO_2026.json y completa país/ciudad.
# Bloques con "|soloextranjeras|N": solo se listan jugadoras no-USA; las demás del programa con país vacío pasan a USA.
# Uso: python3 cargar_d2f_planteles.py   (desde datos-src/planteles_web)
import json,re,os,unicodedata,sys,collections
R=os.path.dirname(os.path.abspath(__file__)); D=os.path.join(R,'..','..','datos')
src=open(os.path.join(R,'cargar_d2f_2025.py'),encoding='utf8').read()
ns={}; exec(src.split('def blocks')[0].replace('R=os.path.dirname(os.path.abspath(__file__))',f'R={R!r}'),ns)
hosts=ns['hosts']
hosts.update({'smcathletics.com':"Saint Michael's College",'tnutrojans.com':'Trevecca Nazarene University','athletics.holyfamily.edu':'Holy Family University','gvsulakers.com':'Grand Valley State University','csusmcougars.com':'California State University – San Marcos','obubison.com':'Oklahoma Baptist University','saintleolions.com':'Saint Leo University','shawbears.com':'Shaw University','spufalcons.com':'Seattle Pacific University','goeasternathletics.com':'Eastern New Mexico University','gbcathletics.com':'Goldey-Beacom College','claytonstatesports.com':'Clayton State University','lubluetigers.com':'Lincoln University – Missouri'})
def ak(n): return re.sub(r'\s+',' ',''.join(c for c in unicodedata.normalize('NFD',n) if unicodedata.category(c)!='Mn')).strip().lower()
ST="AL AK AZ AR CA CO CT DE FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY DC".split()
STN="alabama alaska arizona arkansas california colorado connecticut delaware florida georgia hawaii idaho illinois indiana iowa kansas kentucky louisiana maine maryland massachusetts michigan minnesota mississippi missouri montana nebraska nevada new hampshire new jersey new mexico new york north carolina north dakota ohio oklahoma oregon pennsylvania rhode island south carolina south dakota tennessee texas utah vermont virginia washington west virginia wisconsin wyoming".split()
STN=set(re.findall(r'new \w+|north \w+|south \w+|west \w+|rhode island|\w+',' '.join(STN)))
ABBR={'calif':'CA','ariz':'AZ','wash':'WA','penn':'PA','pa':'PA','mich':'MI','minn':'MN','wis':'WI','neb':'NE','nev':'NV','colo':'CO','fla':'FL','tenn':'TN','ala':'AL','ark':'AR','okla':'OK','mass':'MA','conn':'CT','ill':'IL','ind':'IN','kan':'KS','miss':'MS','mo':'MO','ore':'OR','tex':'TX','va':'VA','vt':'VT','wva':'WV','nh':'NH','nj':'NJ','nm':'NM','ny':'NY','nc':'NC','nd':'ND','sc':'SC','sd':'SD','ga':'GA','md':'MD','ri':'RI','de':'DE','az':'AZ','wv':'WV','wa':'WA','ca':'CA','tx':'TX','ct':'CT','ky':'KY','la':'LA','ma':'MA','me':'ME','mt':'MT','id':'ID','ut':'UT','hi':'HI','wy':'WY','ak':'AK','dc':'DC'}
PAIS={'canada':'Canada','canda':'Canada','ontario':'Canada','ont':'Canada','bc':'Canada','qc':'Canada','quebec':'Canada','manitoba':'Canada','alberta':'Canada','on':'Canada','county durham england':'England','texass':'USA','uk':'United Kingdom','united kingdom':'United Kingdom','england':'England','scotland':'Scotland','wales':'Wales','ireland':'Ireland','the netherlands':'Netherlands','grand cayman':'Cayman Islands','antigua':'Antigua and Barbuda'}
def pais(h):
    h=(h or '').strip()
    if not h: return ''
    t=h.split(',')[-1].strip().rstrip('.,').strip()
    k=re.sub(r'[^a-z ]','',t.lower().replace("'",'').replace('’','')).strip()
    if k in PAIS: return PAIS[k]
    if k in ABBR or t.upper() in ST or k in STN or k=='hawaii' or 'hawai' in k: return 'USA'
    if ',' not in h:
        if k in PAIS: return PAIS[k]
        return 'USA' if k not in ('gibraltar',) else 'Gibraltar'
    return t.rstrip('.').title() if t.islower() else t.rstrip('.')
def blocks(path):
    out=[];cur=None
    for l in open(path,encoding='utf8'):
        l=l.rstrip('\n')
        if l.startswith('#'):
            p=l[1:].split('|'); cur={'host':re.sub(r'^www\.','',p[0]),'solo':'soloextranjeras' in p,'rows':[]}; out.append(cur)
        elif cur is not None and l.startswith('P|'): cur['rows'].append(l.split('|')[1:])
    return {b['host']:b for b in out}  # el último bloque de cada host manda
bio=json.load(open(os.path.join(D,'SOCCER_D2F_BIO_2026.json'),encoding='utf8'))
F=bio['F']; rep=collections.Counter(); nomatch=[]; unmapped=[]
for h,b in blocks(os.path.join(R,'crudo','planteles_d2f_2026.txt')).items():
    sc=hosts.get(h) or hosts.get('www.'+h)
    if not sc or sc not in F: unmapped.append((h,sc)); continue
    idx={ak(n):n for n in F[sc]}
    listed=set()
    for r in b['rows']:
        name,pos,cl,home=(r+['','','',''])[:4]
        c=pais(home); n=idx.get(ak(name))
        if not n: nomatch.append((sc,name,c)); continue
        listed.add(n); e=F[sc][n]; e+=['']*(4-len(e))
        if not e[2] and home: e[2]=home; rep['ciudad']+=1
        if not e[3] and c: e[3]=c; rep['pais_nuevo']+=1
        elif c and e[3]!=c and c!='USA': rep['conflicto']+=1; e[3]=c
        F[sc][n]=e
    if b['solo']:
        for n,e in F[sc].items():
            e+=['']*(4-len(e))
            if n not in listed and not e[3]: e[3]='USA'; rep['usa_por_defecto']+=1
json.dump(bio,open(os.path.join(D,'SOCCER_D2F_BIO_2026.json'),'w',encoding='utf8'),ensure_ascii=False,separators=(',',':'))
print(dict(rep)); print('sin mapa:',unmapped); print('no están en el BIO:',len(nomatch)); [print(' ',x) for x in nomatch[:40]]
vac=sum(1 for s in F.values() for e in s.values() if len(e)<4 or not e[3]); print('país aún vacío:',vac)
