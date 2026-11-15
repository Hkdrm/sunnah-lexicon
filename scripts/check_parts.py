#!/usr/bin/env python3
"""Valide un fichier data/seed/parts/<nom>.json avant fusion.  Usage : python3 scripts/check_parts.py <fichier>"""
import json, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
f = Path(sys.argv[1])
part = json.loads(f.read_text(encoding="utf-8"))
H = {f"{h['collection']}:{h['number']}": h for h in json.loads((ROOT / "web/data.json").read_text(encoding="utf-8"))["hadiths"]}
base_tr = json.loads((ROOT / "data/seed/translations_fr.json").read_text(encoding="utf-8"))["translations"]
base = json.loads((ROOT / "data/seed/practices.json").read_text(encoding="utf-8"))
cats = {c["slug"] for c in base["categories"]} | {c["slug"] for c in part.get("categories", [])}
slugs = {p["slug"] for p in base["practices"]}
for g in (ROOT / "data/seed/parts").glob("*.json"):
    if g.resolve() != f.resolve():
        o = json.loads(g.read_text(encoding="utf-8"))
        slugs |= {p["slug"] for p in o.get("practices", [])}
        cats |= {c["slug"] for c in o.get("categories", [])}
        base_tr = {**base_tr, **o.get("translations", {})}
tr = {**base_tr, **part.get("translations", {})}
FORBID = re.compile(r"obligatoire|obligation|recommand[ée]|déconseill|makrouh|haram|wajib|mustahabb|illicite|est interdit|sunna mu'?akkada|il est permis|est permis", re.I)
err = []
for c in part.get("categories", []):
    if not re.fullmatch(r"[a-z0-9-]+", c["slug"]) or not c.get("label_fr"): err.append(f"catégorie invalide {c}")
mine = set()
for p in part.get("practices", []):
    s = p.get("slug", "?")
    if not re.fullmatch(r"[a-z0-9-]+", s): err.append(f"{s}: slug invalide")
    if s in slugs or s in mine: err.append(f"{s}: slug en double")
    mine.add(s)
    if p.get("category") not in cats: err.append(f"{s}: catégorie inconnue {p.get('category')}")
    if not (5 <= len(p.get("title_fr", "")) <= 90): err.append(f"{s}: titre trop court/long")
    sm = p.get("summary_fr", "")
    if not (40 <= len(sm) <= 600): err.append(f"{s}: résumé hors 40-600 caractères ({len(sm)})")
    if FORBID.search(sm) or FORBID.search(p.get("title_fr", "")): err.append(f"{s}: qualification juridique interdite → {FORBID.search(sm or p['title_fr']).group(0)}")
    if not p.get("refs"): err.append(f"{s}: aucune référence")
    for c, n in p.get("refs", []):
        k = f"{c}:{n}"
        if k not in H: err.append(f"{s}: référence introuvable {k}"); continue
        if not H[k].get("french") and k not in tr: err.append(f"{s}: {k} sans traduction française")
for k in part.get("translations", {}):
    if k not in H: err.append(f"traduction pour hadith introuvable {k}")
    elif H[k].get("french") and H[k].get("french_origin") == "jeu de données": err.append(f"{k}: déjà traduit par la source")
    t = part["translations"][k]
    if not (15 <= len(t) <= 2500): err.append(f"{k}: traduction de longueur suspecte")
    if "ﷺ" not in t and "Prophète" in t and "Messager" in t: err.append(f"{k}: ﷺ manquant ?")
print(f"{f.name}: {len(part.get('practices', []))} pratiques, {len(part.get('translations', {}))} traductions")
if err:
    print("\n".join("ERREUR " + e for e in err)); sys.exit(1)
print("OK")
