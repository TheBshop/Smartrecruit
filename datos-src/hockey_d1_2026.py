# Regenera HOCKEY_PARTIAL_STATS_2026: lee all.json (tablas de cada sitio, bajadas el 12/10/2026) y existing.json (programas con plantel). Usa parse.find().
import json,sys,re
sys.path.insert(0,".")
from hockey_d1_parse import find
MAP={"American":"American University","App State":"Appalachian State University","Ball St.":"Ball State University","Bellarmine":"Bellarmine University","Boston College":"Boston College","Boston U.":"Boston University","Brown":"Brown University","Bryant":"Bryant University","Bucknell":"Bucknell University","California":"University of California – Berkeley","Central Mich.":"Central Michigan University","Colgate":"Colgate University","Columbia":"Columbia University","Cornell":"Cornell University","Dartmouth":"Dartmouth College","Davidson":"Davidson College","Delaware":"University of Delaware","Drexel":"Drexel University","Duke":"Duke University","Fairfield":"Fairfield University","Georgetown":"Georgetown University","Harvard":"Harvard University","Hofstra":"Hofstra University","Holy Cross":"College of the Holy Cross","Indiana":"Indiana University","James Madison":"James Madison University","Kent St.":"Kent State University","LIU":"Long Island University","La Salle":"La Salle University","Lafayette":"Lafayette College","Lehigh":"Lehigh University","Liberty":"Liberty University","Longwood":"Longwood University","Louisville":"University of Louisville","Maine":"University of Maine","Maryland":"University of Maryland","Massachusetts":"University of Massachusetts – Amherst","Merrimack":"Merrimack College","Miami (OH)":"Miami University","Michigan":"University of Michigan","Michigan St.":"Michigan State University","Monmouth":"Monmouth University","New Hampshire":"University of New Hampshire","North Carolina":"University of North Carolina at Chapel Hill","Northeastern":"Northeastern University","Ohio St.":"Ohio State University","Penn":"University of Pennsylvania – Penn","Princeton":"Princeton University","Providence":"Providence College","Queens (NC)":"Queens University of Charlotte","Richmond":"University of Richmond","Rider":"Rider University","Rutgers":"Rutgers University","Sacred Heart":"Sacred Heart University","Saint Joseph's":"Saint Joseph's University","Saint Louis":"Saint Louis University","Stonehill":"Stonehill College","Syracuse":"Syracuse University","Temple":"Temple University","Towson":"Towson University","UAlbany":"SUNY University at Albany","UC Davis":"University of California – Davis","UConn":"University of Connecticut","UMass Lowell":"University of Massachusetts – Lowell","VCU":"Virginia Commonwealth University","Vermont":"University of Vermont","Villanova":"Villanova University","Wagner":"Wagner College","Wake Forest":"Wake Forest University","William & Mary":"William & Mary","Yale":"Yale University"}
def num(x):
    x=x.replace(',','').strip()
    try: return float(x) if '.' in x else int(x)
    except: return None
def name(s):
    s=re.split(r'\s+\d+',s.strip())[0].strip()
    if ',' in s:
        a,b=s.split(',',1); s=b.strip()+' '+a.strip()
    return re.sub(r'\s+',' ',s)
d=json.load(open('all.json')); ex=set(json.load(open('existing.json')))
out={};skipped=[];have=[]
for team,v in d.items():
    r=find(v)
    if not r: continue
    cat=MAP.get(team)
    if not cat: skipped.append(('sin mapa',team));continue
    if cat in ex: have.append(team);continue
    h,rows=r; ix={k:h.index(k) for k in h if k}
    g=lambda row,k:(num(row[ix[k]]) if k in ix and ix[k]<len(row) else None)
    pl=[]
    for row in rows:
        nm=row[ix['player']]
        if not nm or re.match(r'(?i)^(total|opponents?|team)',nm): continue
        gp=g(row,'gp')
        if not gp: continue
        pl.append([name(nm),gp,g(row,'gs'),g(row,'min'),g(row,'g') or 0,g(row,'a') or 0,g(row,'pts') if g(row,'pts') is not None else (g(row,'g') or 0)*2+(g(row,'a') or 0),g(row,'sh'),g(row,'sog')])
    pl.sort(key=lambda p:-p[6])
    if len(pl)<5: skipped.append(('pocas',team,len(pl)));continue
    out[cat]=pl
print(len(out),'nuevos |','ya con plantel:',len(have),have,'| skipped',skipped)
tot=sum(len(v) for v in out.values());print('jugadoras',tot)
json.dump(out,open('fh_new.json','w',encoding='utf8'),ensure_ascii=False,separators=(',',':'))
print('const HOCKEY_PARTIAL_STATS_2026 = '+json.dumps(out,ensure_ascii=False,separators=(',',':'))+';',file=open('fh_const.js','w',encoding='utf8'))
for k in list(out)[:2]: print(k,out[k][:3])
