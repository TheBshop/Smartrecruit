"""Empareja las universidades sin UNITID con College Scorecard (nombre + estado + ciudad) y refresca SCORECARD_BY_ID.
Uso: python3 datos-src/scorecard_match.py /ruta/Most-Recent-Cohorts-Institution.csv"""
import csv, json, re, sys, unicodedata, difflib, collections
csv.field_size_limit(10**9)
src = sys.argv[1]
D = 'datos/'
P = json.load(open(D+'PROGRAMS_ALL_SPORTS.json'))
E = json.load(open(D+'EADA_SITE_NAMES.json')); N = json.load(open(D+'SCORECARD_NAME_IDS.json'))
ST = {'Alabama':'AL','Alaska':'AK','Arizona':'AZ','Arkansas':'AR','California':'CA','Colorado':'CO','Connecticut':'CT','Delaware':'DE','District of Columbia':'DC','Florida':'FL','Georgia':'GA','Hawaii':'HI','Idaho':'ID','Illinois':'IL','Indiana':'IN','Iowa':'IA','Kansas':'KS','Kentucky':'KY','Louisiana':'LA','Maine':'ME','Maryland':'MD','Massachusetts':'MA','Michigan':'MI','Minnesota':'MN','Mississippi':'MS','Missouri':'MO','Montana':'MT','Nebraska':'NE','Nevada':'NV','New Hampshire':'NH','New Jersey':'NJ','New Mexico':'NM','New York':'NY','North Carolina':'NC','North Dakota':'ND','Ohio':'OH','Oklahoma':'OK','Oregon':'OR','Pennsylvania':'PA','Rhode Island':'RI','South Carolina':'SC','South Dakota':'SD','Tennessee':'TN','Texas':'TX','Utah':'UT','Vermont':'VT','Virginia':'VA','Washington':'WA','West Virginia':'WV','Wisconsin':'WI','Wyoming':'WY'}
def norm(s):
    s = unicodedata.normalize('NFD', s or '').encode('ascii','ignore').decode().lower()
    s = s.replace('&',' and ').replace('–','-').replace('—','-')
    s = re.sub(r"\bst\.?\b", 'saint', s); s = re.sub(r"\bmt\.?\b", 'mount', s)
    s = re.sub(r"[^a-z0-9]+", ' ', s)
    s = re.sub(r"\b(the|of|at|in|and|main|campus|district)\b", ' ', s)
    return re.sub(r"\s+", ' ', s).strip()
rows = list(csv.DictReader(open(src, encoding='utf-8', errors='replace')))
byst = collections.defaultdict(list)
for r in rows:
    if r['CURROPER'] == '0': continue
    byst[r['STABBR']].append((norm(r['INSTNM']), norm(r['CITY']), r['UNITID'], r['INSTNM']))
prog = {}
for p in P: prog.setdefault(p['School'], (ST.get(p['State'], p['State']), p['City']))
new = {}; unsure = []
for s,(st,city) in sorted(prog.items()):
    if E.get(s) or N.get(s): continue
    ns = norm(s); cands = byst.get(st, [])
    exact = [c for c in cands if c[0] == ns]
    if len(exact) == 1: new[s] = exact[0][2]; continue
    best = sorted(((difflib.SequenceMatcher(None, ns, c[0]).ratio() + (0.12 if c[1] == norm(city) else 0), c) for c in cands), key=lambda x: -x[0])[:2]
    if best and best[0][0] >= 0.93 and (len(best) < 2 or best[0][0] - best[1][0] >= 0.04):
        new[s] = best[0][1][2]
    else:
        unsure.append((s, st, city, [(round(b[0],2), b[1][3]) for b in best]))
json.dump(new, open('/tmp/claude-0/-home-claude/b4b3c9d2-db94-507a-8f16-9daea3bea23f/scratchpad/sc/new_ids.json','w'), indent=0, ensure_ascii=False)
print('emparejadas', len(new), 'sin emparejar', len(unsure))
for s,i in list(new.items())[:400]:
    print('OK', s, '->', next(r['INSTNM'] for r in rows if r['UNITID']==i))
for u in unsure: print('??', u)
