#!/usr/bin/env python3
"""Valide un fichier data/seed/dua_parts/<nom>.json.  Usage : python3 scripts/check_duas.py <fichier>
Une dua = {slug, category, title_fr, when_fr, arabic (VOCALISÉ), translation_fr, refs:[[coll,n],...], repeat_fr?}
Contrôles : champs, catégorie, références existantes, arabe vocalisé (assez de voyelles), arabe retrouvé dans un hadith cité
(squelette consonantique), phonétique générable, pas de qualification juridique."""
import json, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from arabic import normalize
from translit import transliterate

ROOT = Path(__file__).resolve().parent.parent
f = Path(sys.argv[1])
part = json.loads(f.read_text(encoding="utf-8"))
H = {f"{h['collection']}:{h['number']}": h for h in json.loads((ROOT / "web/data.json").read_text(encoding="utf-8"))["hadiths"]}
cats = {c["slug"] for c in json.loads((ROOT / "data/seed/duas.json").read_text(encoding="utf-8"))["categories"]}
slugs = set()
for g in (ROOT / "data/seed/dua_parts").glob("*.json"):
    if g.resolve() != f.resolve():
        slugs |= {d["slug"] for d in json.loads(g.read_text(encoding="utf-8")).get("duas", [])}
FORBID = re.compile(r"obligatoire|obligation|recommand[ée]|déconseill|makrouh|haram|wajib|mustahabb|illicite|sunna mu'?akkada", re.I)
TASHKEEL = re.compile("[ً-ْ]")
skel = lambda s: re.sub(r"[^ء-ي]", "", normalize(s)).replace("ى", "ي").replace("ة", "ه")
err, warn, mine = [], [], set()
for d in part.get("duas", []):
    s = d.get("slug", "?")
    if not re.fullmatch(r"[a-z0-9-]+", s): err.append(f"{s}: slug invalide")
    if s in slugs or s in mine: err.append(f"{s}: slug en double")
    mine.add(s)
    if d.get("category") not in cats: err.append(f"{s}: catégorie inconnue {d.get('category')}")
    for k in ("title_fr", "when_fr", "arabic", "translation_fr"):
        if not d.get(k): err.append(f"{s}: champ manquant {k}")
    ar = d.get("arabic", "")
    letters = len(re.findall("[ء-ي]", ar)); marks = len(TASHKEEL.findall(ar))
    if letters and marks < letters * 0.6: err.append(f"{s}: arabe insuffisamment vocalisé ({marks} signes pour {letters} lettres)")
    if re.search("[A-Za-z]", ar): err.append(f"{s}: lettres latines dans l'arabe")
    refs = d.get("refs", [])
    if not refs: err.append(f"{s}: aucune référence")
    texts = []
    for c, n in refs:
        k = f"{c}:{n}"
        if k not in H: err.append(f"{s}: référence introuvable {k}")
        else: texts.append(skel(H[k]["arabic"]))
    # l'arabe de la dua (sans « ... » ni ponctuation) doit se retrouver dans un hadith cité, morceau par morceau
    parts = [p for p in re.split(r"[.،؛:؟!…]|\.\.\.", ar) if len(skel(p)) >= 6]
    for p in parts:
        sp = skel(p)
        if texts and not any(sp in t for t in texts):
            err.append(f"{s}: segment absent des hadiths cités : « {p.strip()[:50]} »")
    try:
        ph = transliterate(ar)
        if not ph or re.search("[؀-ۿ]", ph): err.append(f"{s}: phonétique invalide : {ph}")
    except Exception as e:
        err.append(f"{s}: phonétique impossible ({e})")
    if FORBID.search(d.get("translation_fr", "") + d.get("when_fr", "") + d.get("title_fr", "")): err.append(f"{s}: qualification juridique interdite")
    if len(d.get("translation_fr", "")) < 8: err.append(f"{s}: traduction trop courte")
print(f"{f.name}: {len(part.get('duas', []))} duaa")
print("\n".join("ERREUR " + e for e in err) or "OK")
sys.exit(1 if err else 0)
