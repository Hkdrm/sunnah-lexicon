#!/usr/bin/env python3
"""Cherche des hadiths dans le corpus (web/data.json).
  python3 scripts/find.py "عبارة arabe" [--col riyad|nawawi40|shamail|adab] [-n 15] [--sahih]
  python3 scripts/find.py --show riyad:517        # texte arabe complet + degré + français éventuel
Recherche sur le texte arabe normalisé (sans voyelles) ; plusieurs mots = tous présents.
"""
import argparse, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from arabic import normalize

ROOT = Path(__file__).resolve().parent.parent
H = json.loads((ROOT / "web/data.json").read_text(encoding="utf-8"))["hadiths"]
IDX = {f"{h['collection']}:{h['number']}": h for h in H}

ap = argparse.ArgumentParser()
ap.add_argument("q", nargs="?")
ap.add_argument("--col"); ap.add_argument("-n", type=int, default=15)
ap.add_argument("--sahih", action="store_true", help="seulement degré Sahih / Hasan")
ap.add_argument("--show")
a = ap.parse_args()

if a.show:
    for key in a.show.split(","):
        h = IDX.get(key.strip())
        if not h: print(key, "INTROUVABLE"); continue
        print(f"== {key} | degré: {h['grade']} | cité par: {h.get('takhrij')}")
        print(h["arabic"].replace("\n", " "))
        if h.get("french"): print("FR:", h["french"])
        print()
    sys.exit()

words = [normalize(w) for w in (a.q or "").split()]
n = 0
for h in H:
    if a.col and h["collection"] != a.col: continue
    if a.sahih and not any(x in h["grade"].lower() for x in ("sahih", "hasan")): continue
    t = normalize(h["arabic"])
    if all(w in t for w in words):
        i = t.find(words[0])
        print(f"{h['collection']}:{h['number']} [{h['grade']}] …{t[max(0,i-40):i+160]}")
        n += 1
        if n >= a.n: break
print(f"({n} résultat(s) affiché(s))")
