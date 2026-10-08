"""Planteles de básquet masculino NCAA D2 (RealGM) -> constantes de RosterReal.jsx.

Uso:
    python3 basquet_d2.py <RosterReal.jsx> 2026=<carpeta CSV 2026-27> 2025=<carpeta CSV 2025-26> ... [stats=<archivo>]

Cada carpeta tiene los CSV de los listados de planteles por conferencia de RealGM de UNA temporada
(2026 = temporada 2026-27). Genera, en la carpeta actual:
  - BBALL_D2_ROSTERS.json      {universidad: [temporada, [[jugador, posición, clase, ciudad, país, PJ, PPG, APG], ...]]}
                               (PJ, PPG y APG solo si el jugador tiene estadísticas en el archivo stats=)
  - BBALL_D2_CONFERENCES.json  {universidad: conferencia}
Su contenido reemplaza al de las constantes del mismo nombre en RosterReal.jsx.

Reglas:
  - Por universidad se usa la temporada más nueva que tenga al menos MIN_PLAYERS jugadores; si el plantel
    nuevo está incompleto (RealGM todavía no lo cargó), se conserva el de la temporada anterior.
  - Las columnas de los CSV vienen corridas según el archivo: cada celda se reconoce por su contenido.
  - El país es el de la ciudad de nacimiento (no la nacionalidad deportiva).
  - OVERRIDES: equipos que no se pueden cruzar solos con el catálogo (None = no está en el catálogo).
  - stats=: CSV "id_realgm,pj,ppg,apg" (promedios por partido de la temporada anterior, de /ncaa-dii/stats de RealGM).
    Se cruza por el id del jugador en RealGM, que viene en el link de cada fila de los CSV de planteles.
"""
import collections
import csv
import difflib
import glob
import json
import re
import sys
import unicodedata

MIN_PLAYERS = 8
POS = {'G', 'F', 'C', 'PG', 'SG', 'SF', 'PF', 'GF', 'FC'}
CLS = {'Fr', 'So', 'Jr', 'Sr', '5th', 'Gr', 'RS'}
OVERRIDES = {
    # estas cinco no estaban en el catálogo: se cargan con los nombres de BBALL_D2_EXTRA_SCHOOLS (RosterReal.jsx)
    'Puerto Rico-Bayamon': 'University of Puerto Rico – Bayamón', 'Simon Fraser': 'Simon Fraser University',
    'Staten Island': 'College of Staten Island', 'Queens College': 'Queens College – New York', 'Texas-Tyler': 'University of Texas at Tyler',
    'USC Beaufort': 'University of South Carolina – Beaufort', 'Edinboro': 'Edinboro University',
    'Lincoln (MO)': 'Lincoln University – Missouri', 'Vanguard': 'Vanguard University of Southern California',
    'California (PA)': 'California University of Pennsylvania', 'District of Columbia': 'University of the District of Columbia',
    'Clarion': 'Clarion University of Pennsylvania', 'UC Merced': 'University of California – Merced',
    'Jamestown (ND)': 'University of Jamestown', 'Cal Poly - Pomona': 'California State Polytechnic University – Pomona',
    'Georgia College': 'Georgia College & State University', 'Metro State': 'Metropolitan State University of Denver',
    'Jefferson': 'Thomas Jefferson University (Formerly Philadelphia University)',
}


def parse_dir(folder):
    """Devuelve la lista de jugadores de todos los CSV de una carpeta."""
    players = []
    for path in sorted(glob.glob(folder.rstrip('/') + '/*.csv')):
        rows = list(csv.reader(open(path, encoding='utf-8-sig')))
        for r in rows[1:]:
            cells = [c.strip() for c in r]
            rest = cells[2:]
            d = {'name': cells[0], 'pos': '', 'cls': '', 'city': '', 'country': '', 'team': '', 'conf': ''}
            m = re.search(r'/player/[^/]+/Summary/(\d+)', cells[1] if len(cells) > 1 else '')
            d['id'] = m.group(1) if m else ''
            birth = None
            for i, c in enumerate(rest):
                m = re.search(r'/ncaa-dii/conferences/([^/]+)/\d+/([^/]+)/(\d+)/rosters', c)
                if m:
                    d['conf'] = m.group(1).replace('-', ' ')
                    d['team'] = rest[i - 1]
                    continue
                m = re.search(r'/info/birth-cities/\d+/(.+)$', c)
                if m:
                    birth = m.group(1)
                    continue
                if c in POS and not d['pos']:
                    d['pos'] = c
                elif c in CLS and not d['cls']:
                    d['cls'] = c
            if birth:
                best = ''
                for c in rest:
                    if not c or c.startswith('http') or c in POS or c in CLS or len(c) < 3:
                        continue
                    slug = re.sub(r'[^A-Za-z0-9]+', '-', c).strip('-')
                    if slug and birth.lower().startswith(slug.lower() + '-') and len(slug) > len(best):
                        best, d['city'] = slug, c
                if best:
                    d['country'] = birth[len(best):].strip('-').replace('-', ' ')
                else:
                    parts = birth.split('--')
                    d['city'] = parts[0].replace('-', ' ')
                    d['country'] = (parts[1] if len(parts) > 1 else '').replace('-', ' ')
            if d['team']:
                players.append(d)
    return players


STOP = {'university', 'college', 'of', 'the', 'at'}


def norm(x):
    x = unicodedata.normalize('NFKD', x).encode('ascii', 'ignore').decode().lower()
    x = x.replace('&', ' and ').replace('st.', 'saint').replace("'", '')
    x = re.sub(r'\bcal state\b', 'california state university', x)
    x = re.sub(r'\bwv\b', 'west virginia', x)
    x = re.sub(r'[^a-z0-9 ]', ' ', x)
    return [t for t in x.split() if t not in STOP]


def score(a, b):
    A, B = set(norm(a)), set(norm(b))
    if not A or not B:
        return 0
    return len(A & B) / len(A | B) + 0.3 * difflib.SequenceMatcher(None, ' '.join(norm(a)), ' '.join(norm(b))).ratio()


def match_teams(teams, catalog):
    """teams: {(equipo, conferencia)} -> {equipo: (universidad | None, puntaje, segunda opción)}"""
    out = {}
    cn = lambda c: ' '.join(norm(c or ''))
    for team, conf in sorted(teams):
        if team in OVERRIDES:
            out[team] = (OVERRIDES[team], 9, '')
            continue
        cands = sorted(((score(team, p['School']) + (0.5 if difflib.SequenceMatcher(None, cn(conf), cn(p.get('Conference'))).ratio() > 0.8 else 0), p['School']) for p in catalog), reverse=True)[:2]
        out[team] = (cands[0][1], cands[0][0], cands[1][1])
    return out


def main():
    src = open(sys.argv[1], encoding='utf-8').read()
    i = src.index('const PROGRAMS_ALL_SPORTS = ') + len('const PROGRAMS_ALL_SPORTS = ')
    catalog, _ = json.JSONDecoder().raw_decode(src[i:])
    catalog = [p for p in catalog if p['sport'] == 'Basketball' and p.get('Gender') == 'M']
    seasons, stats = {}, {}
    for arg in sys.argv[2:]:
        year, folder = arg.split('=', 1)
        if year == 'stats':
            for line in open(folder, encoding='utf-8').read().split():
                pid, gp, ppg, apg = line.split(',')
                stats[pid] = [int(gp), float(ppg), float(apg)]
            continue
        seasons[int(year)] = parse_dir(folder)
    teams = {(p['team'], p['conf']) for ps in seasons.values() for p in ps}
    mp = match_teams(teams, catalog)
    weak = sorted((s, t, u, alt) for t, (u, s, alt) in mp.items() if s < 1.3)
    print('cruces a revisar (puntaje < 1.3):')
    for s, t, u, alt in weak:
        print(f'  {s:.2f}  {t} -> {u}   (2ª: {alt})')
    print('fuera del catálogo:', sorted(t for t, (u, s, alt) in mp.items() if not u))

    rosters, confs, kept_old = {}, {}, []
    for year in sorted(seasons, reverse=True):
        by_school = collections.OrderedDict()
        for p in seasons[year]:
            school = mp[p['team']][0]
            if not school:
                continue
            country = 'USA' if p['country'] == 'United States' else p['country']
            by_school.setdefault(school, []).append([p['name'], p['pos'], p['cls'], p['city'], country] + stats.get(p['id'], []))
            confs.setdefault(school, p['conf'])
        for school, rows in by_school.items():
            if school in rosters:
                continue
            if len(rows) < MIN_PLAYERS and any(school in {mp[q['team']][0] for q in seasons[y]} for y in seasons if y < year):
                kept_old.append((school, year, len(rows)))
                continue
            rosters[school] = [year, rows]
    dup = [s for s, n in collections.Counter(u for u, _, _ in mp.values() if u).items() if n > 1]
    print('universidades con dos equipos cruzados (revisar):', dup)
    print('plantel nuevo incompleto, se conserva el anterior:', kept_old)
    with_stats = sum(1 for v in rosters.values() for r in v[1] if len(r) > 5)
    print('jugadores con estadísticas:', with_stats, 'de', sum(len(v[1]) for v in rosters.values()), '| planteles con alguna:', sum(1 for v in rosters.values() if any(len(r) > 5 for r in v[1])))
    print('planteles por temporada:', dict(collections.Counter(v[0] for v in rosters.values())), '| jugadores:', sum(len(v[1]) for v in rosters.values()))
    rosters = collections.OrderedDict(sorted(rosters.items()))
    dump = lambda o: json.dumps(o, ensure_ascii=False, separators=(',', ':'))
    open('BBALL_D2_ROSTERS.json', 'w', encoding='utf-8').write(dump(rosters))
    open('BBALL_D2_CONFERENCES.json', 'w', encoding='utf-8').write(dump({s: confs[s] for s in rosters}))


if __name__ == '__main__':
    main()
