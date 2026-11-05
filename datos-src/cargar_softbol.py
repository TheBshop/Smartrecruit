#!/usr/bin/env python3
"""Carga planteles de softbol pegados (datos-src/planteles_pegados/softbol_*.txt) en datos/SOFTBALL_ROSTERS.json.
Formato: `## Escuela | fuente | fecha | temporada` y por jugadora `nombre|posición|año|ciudad natal`.
Guarda solo conteos por año y grupo de posición (P/C/IF/OF) y las jugadoras con ciudad natal fuera de EE.UU. Reemplaza la escuela si ya estaba."""
import json, re, sys, glob, os
root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
out = os.path.join(root, "datos", "SOFTBALL_ROSTERS.json")
data = json.load(open(out))
CLS = {"fr": "Fr", "freshman": "Fr", "r-fr": "Fr", "so": "So", "sophomore": "So", "jr": "Jr", "junior": "Jr", "sr": "Sr", "senior": "Sr", "grd": "Gr", "gr": "Gr", "graduate": "Gr"}
P = {"p", "rhp", "lhp", "pitcher"}; C = {"c", "catcher"}
IF = {"if", "inf", "mif", "mi", "1b", "2b", "3b", "ss", "infield", "infielder", "middle", "corner infield", "shortstop", "second base", "first base", "third base"}
OF = {"of", "cf", "lf", "rf", "outfield", "outfielder"}
def grp(pos):
    for t in re.split(r"[/,]", pos.lower()):
        t = t.strip()
        if t in P: return "P"
        if t in C: return "C"
        if t in IF: return "IF"
        if t in OF: return "OF"
    return None
FOREIGN = re.compile(r"Canada|Alberta|Ontario|British Columbia|B\\.C\\.|Manitoba|Saskatchewan|Quebec|Nova Scotia|Japan|New Zealand|Australia|Denmark|Germany|Spain|Brazil|Venezuela|(?<!New )Mexico|Colombia|Argentina|England|Scotland|Ireland|Netherlands|Italy|France|Sweden|Norway|Finland|Bahamas|Jamaica|Dominican|Cuba|Panama|Korea|China|Philippines", re.I)
def foreign(h): return bool(FOREIGN.search(h))
cur = None; rows = {}
for f in sorted(glob.glob(os.path.join(root, "datos-src", "planteles_pegados", "softbol_*.txt"))):
    for ln in open(f, encoding="utf-8"):
        ln = ln.rstrip("\n")
        if ln.startswith("## "):
            parts = [x.strip() for x in ln[3:].split("|")]; cur = parts[0]; rows[cur] = {"season": int(parts[3]) if len(parts) > 3 else 2026, "p": []}
        elif ln.strip() and cur:
            nm, pos, cl, ht = (ln.split("|") + ["", "", "", ""])[:4]; rows[cur]["p"].append((nm.strip(), pos.strip(), CLS.get(cl.strip().lower(), ""), ht.strip()))
for school, r in rows.items():
    cls, pos, intl = {}, {}, []
    for nm, ps, cl, ht in r["p"]:
        if cl: cls[cl] = cls.get(cl, 0) + 1
        g = grp(ps)
        if g and cl: pos[g + cl] = pos.get(g + cl, 0) + 1
        if ht and foreign(ht): intl.append(f"{nm} ({ht})")
    data[school] = {"n": len(r["p"]), "cls": cls, "pos": pos, "intl": intl, "season": r["season"]}
    print(school, len(r["p"]), "cls", sum(cls.values()), "pos", sum(pos.values()), "intl", intl)
json.dump(data, open(out, "w"), ensure_ascii=False, separators=(",", ":"))
print("total escuelas", len(data))
