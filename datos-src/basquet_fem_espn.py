#!/usr/bin/env python3
"""Básquet femenino NCAA D1: estadísticas individuales 2025-26 (ESPN, /womens-college-basketball/team/stats/_/id/<id>/season/2026).
Entrada: JSON con una lista de equipos [{id, loc, name, ts:{GP}, players:[{n,pos,GP,MIN,PTS,REB,AST}]}] (bajado de ESPN el 12/10/2026).
Salida (stdout): línea JS `const WBB_ESPN_STATS_2025_26 = {...};` para pegar en RosterReal.jsx.
Uso: python3 basquet_fem_espn.py espn_wbb.json RosterReal.jsx
"""
import json, re, sys, unicodedata

# ESPN -> clave del plantel 2026-27 ya cargado (WBB_ROSTERS_2026_27)
TO_WBB_KEY = {
  "UAlbany": "Albany", "App State": "Appalachian State", "Little Rock": "Arkansas-Little Rock", "BYU": "Brigham Young",
  "UCF": "Central Florida", "UIC": "Illinois-Chicago", "McNeese": "McNeese State", "Ole Miss": "Mississippi",
  "NJIT": "New Jersey Institute of Technology", "LSU New Orleans": "New Orleans", "Nicholls": "Nicholls State",
  "UL Monroe": "Louisiana Monroe", "Sam Houston": "Sam Houston State", "SE Louisiana": "Southeastern Louisiana",
  "TCU": "Texas Christian", "UT Arlington": "Texas-Arlington", "UTEP": "Texas-El Paso", "VCU": "Virginia Commonwealth",
  "Charleston": "College of Charleston", "Presbyterian": "Presbyterian College", "Seattle U": "Seattle",
}
# ESPN -> nombre del catálogo (programas sin plantel 2026-27 cargado)
TO_CATALOG = {
  "UAB": "University of Alabama – Birmingham", "Cal Poly": "California Polytechnic State University",
  "Sacramento State": "California State University – Sacramento", "UCLA": "University of California – Los Angeles – UCLA",
  "UC Riverside": "University of California – Riverside", "UC San Diego": "University of California – San Diego",
  "USC": "University of Southern California", "UConn": "University of Connecticut", "Florida A&M": "Florida A&M University",
  "Hawai'i": "University of Hawaii at Manoa", "Southern Illinois": "Southern Illinois University Carbondale",
  "IU Indianapolis": "Indiana University-Purdue University – Indianapolis (IUPUI)", "Southern Indiana": "University of Southern Indiana",
  "Western Kentucky": "Western Kentucky University", "LSU": "Louisiana State University (LSU)",
  "Massachusetts": "University of Massachusetts – Amherst", "Kansas City": "University of Missouri – Kansas City",
  "NC State": "North Carolina State University", "Miami (OH)": "Miami University", "Chattanooga": "University of Tennessee – Chattanooga",
  "Virginia": "University of Virginia", "Washington": "University of Washington", "Milwaukee": "University of Wisconsin – Milwaukee",
  "Fresno State": "California State University – Fresno", "UT Rio Grande Valley": "University of Texas – Rio Grande Valley",
  "Jacksonville": "Jacksonville University", "Long Beach State": "California State University – Long Beach",
  "UC Irvine": "University of California – Irvine", "UC Davis": "University of California – Davis",
  "Army": "United States Military Academy", "UNC Wilmington": "University of North Carolina – Wilmington",
  "Texas A&M-Corpus Christi": "Texas A&M University – Corpus Christi", "Air Force": "United States Air Force Academy",
  "Arkansas-Pine Bluff": "University of Arkansas at Pine Bluff", "Binghamton": "SUNY Binghamton University",
  "Buffalo": "SUNY University at Buffalo", "Chicago State": "Chicago State University",
  "Florida International": "Florida International University", "Cal State Fullerton": "California State University – Fullerton",
  "Houston Christian": "Houston Christian University", "UMass Lowell": "University of Massachusetts – Lowell",
  "UMBC": "University of Maryland – Baltimore County", "Navy": "United States Naval Academy",
  "UNC Asheville": "University of North Carolina Asheville", "Charlotte": "University of North Carolina at Charlotte",
  "UNC Greensboro": "University of North Carolina – Greensboro", "Omaha": "University of Nebraska at Omaha",
  "UNLV": "University of Nevada – Las Vegas", "Nevada": "University of Nevada – Reno", "North Carolina A&T": "North Carolina A&T State University",
  "Cal State Northridge": "California State University – Northridge", "Prairie View A&M": "Prairie View A & M University",
  "Queens University": "Queens University of Charlotte", "Robert Morris": "Robert Morris University – Pennsylvania",
  "UC Santa Barbara": "University of California – Santa Barbara", "SIU Edwardsville": "Southern Illinois University Edwardsville",
  "SMU": "Southern Methodist University – SMU", "Southern Miss": "University of Southern Mississippi", "Southern": "Southern University & A&M College",
  "St. John's": "St. John's University – New York", "Saint Joseph's": "Saint Joseph's University", "Saint Mary's": "Saint Mary's College of California",
  "Stony Brook": "SUNY Stony Brook University", "Tarleton State": "Tarleton State University", "UT Martin": "University of Tennessee – Martin",
  "Tennessee Tech": "Tennessee Technological University", "UTSA": "University of Texas – San Antonio", "Texas Southern": "Texas Southern University",
  "Green Bay": "University of Wisconsin – Green Bay", "Lindenwood": "Lindenwood University", "East Texas A&M": "Texas A&M University – Commerce",
  "St. Thomas": "University of St. Thomas – Minnesota", "South Carolina Upstate": "University of South Carolina – Upstate",
  "Cal State Bakersfield": "California State University – Bakersfield", "Utah Tech": "Utah Tech University",
  "Long Island University": "Long Island University", "California": "University of California – Berkeley",
  "Pennsylvania": "University of Pennsylvania – Penn", "Jacksonville State": "Jacksonville State University",
}

def nk(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower()
    s = s.replace('&', 'and').replace('.', '').replace("'", '')
    s = re.sub(r'\bst\b', 'state', s)
    s = re.sub(r'\buniversity of\b|\buniversity\b', '', s)
    return re.sub(r'[^a-z0-9]', '', s)

def f(x):
    return None if x in ('', None) else round(float(x), 1)

def main(espn_path, jsx_path):
    src = open(jsx_path, encoding='utf8').read()
    wbb = json.loads(re.search(r'const WBB_ROSTERS_2026_27 = (\{.*\});', src).group(1))
    L = src.split('\n')
    line = next(l for l in L if l.startswith('const PROGRAMS_ALL_SPORTS = '))
    cat, _ = json.JSONDecoder().raw_decode(line[line.index('=') + 1:].strip())
    cat_names = {p['School'] for p in cat}
    wk = {nk(k): k for k in wbb}
    out, unresolved, nw, nc = {}, [], 0, 0
    for t in json.load(open(espn_path)):
        loc = t['loc']
        key = TO_WBB_KEY.get(loc) or wk.get(nk(loc))
        kind = 'w'
        if not key:
            key = TO_CATALOG.get(loc)
            kind = 'c'
            if key and key not in cat_names:
                unresolved.append((loc, 'catálogo sin ' + key)); continue
        if not key:
            unresolved.append((loc, 'sin alias')); continue
        ps = [p for p in t['players'] if (p.get('GP') or 0) >= 3 and p.get('PTS') != '']
        ps.sort(key=lambda p: -((p.get('MIN') or 0) * p['GP']))
        rows = [[p['n'], p.get('pos') or '', p['GP'], f(p.get('MIN')), f(p.get('PTS')), f(p.get('REB')), f(p.get('AST'))] for p in ps[:13]]
        if len(rows) < 5: unresolved.append((loc, 'menos de 5 jugadoras')); continue
        out[key] = {'k': kind, 'p': rows}
        nw += kind == 'w'; nc += kind == 'c'
    sys.stderr.write(f'plantel existente: {nw}, solo catálogo: {nc}, sin resolver: {unresolved}\n')
    print('const WBB_ESPN_STATS_2025_26 = ' + json.dumps(out, ensure_ascii=False, separators=(',', ':')) + ';')

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
