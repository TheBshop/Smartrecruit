"""Arma datos/SCORECARD_BY_ID.json desde College Scorecard (Most Recent Cohorts - Institution).
Uso: python3 datos-src/scorecard_build.py CSV [--check]  (--check compara contra el JSON actual sin escribir)"""
import csv, json, sys
csv.field_size_limit(10**9)
src = sys.argv[1]; check = '--check' in sys.argv
D = 'datos/'
E = json.load(open(D+'EADA_SITE_NAMES.json')); N = json.load(open(D+'SCORECARD_NAME_IDS.json'))
ids = {str(v) for v in E.values()} | {str(v) for v in N.values()} | set(json.load(open(D+'SCORECARD_BY_ID.json')).keys())
def f(x):
    try: return float(x)
    except: return None
def build(r):
    o = {}
    a = f(r['ADM_RATE'])
    if a is not None: o['a'] = f"{round(a*100, 1)}%" if a < 0.1 else f"{round(a*100)}%"
    sv, sm = f(r['SATVR25']), f(r['SATMT25']); sv7, sm7 = f(r['SATVR75']), f(r['SATMT75'])
    if None not in (sv, sm, sv7, sm7): o['s'] = f"{int(sv+sm)}-{int(sv7+sm7)}"
    a25, a75 = f(r['ACTCM25']), f(r['ACTCM75'])
    if None not in (a25, a75): o['t'] = f"{int(a25)}-{int(a75)}"
    cost = f(r['COSTT4_A']) or f(r['COSTT4_P'])
    if cost:
        ti, to = f(r['TUITIONFEE_IN']), f(r['TUITIONFEE_OUT'])
        o['ci'] = int(cost)
        o['co'] = int(cost - ti + to) if (r['CONTROL'] == '1' and ti is not None and to is not None) else int(cost)
    e = f(r['UGDS'])
    if e is not None: o['e'] = int(e)
    g = f(r['C150_4']); g = g if g is not None else f(r['C150_L4'])
    if g is not None: o['g'] = f"{round(g*100)}%"
    w = r['INSTURL'] or ''
    if w and w != 'NA': o['w'] = w
    return o
out = {}
for r in csv.DictReader(open(src, encoding='utf-8', errors='replace')):
    if r['UNITID'] in ids: out[r['UNITID']] = build(r)
if check:
    old = json.load(open(D+'SCORECARD_BY_ID.json')); diff = {k: 0 for k in 'a s t ci co e g w'.split()}; same = {k: 0 for k in diff}
    for u, v in old.items():
        for k in diff:
            if k in v:
                (same if out.get(u, {}).get(k) == v[k] else diff)[k] += 1
    print('iguales', same); print('distintos', diff); sys.exit()
json.dump(out, open(D+'SCORECARD_BY_ID.json', 'w'), ensure_ascii=False, separators=(',', ':'))
print('escrito', len(out))
