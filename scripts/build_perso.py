#!/usr/bin/env python3
"""Assemble web/perso.json : contenu PERSONNEL issu de livrets achetés (usage privé).
NE JAMAIS COMMITER ni publier ce fichier (voir .gitignore). Sources : data/private/*.json
Usage : python3 scripts/build.py && python3 scripts/build_perso.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PRIV = ROOT / "data" / "private"
D = json.loads((ROOT / "web/data.json").read_text(encoding="utf-8"))
H = {f"{h['collection']}:{h['number']}": h for h in D["hadiths"]}

TITLES_FR = """Les actes valent par les intentions|L'islam, la foi et l'excellence (ihsan)|Les piliers de l'islam|Le décret divin|L'innovation en religion|Le licite est clair, l'illicite est clair|La religion est le conseil sincère|Le combat dans la voie d'Allah|Selon ses capacités|Se limiter à ce qui est licite et bon|S'écarter du douteux|Laisser ce qui ne nous concerne pas|La perfection de la foi|Le caractère sacré du sang du musulman|Les bonnes manières en islam|Ne te mets pas en colère|Le bon geste lors de l'abattage|Le bon caractère|Garde Allah, Il te gardera|La pudeur fait partie de la foi|Dis « Je crois en Allah », puis sois droit|Se limiter aux obligations|Se hâter vers le bien|L'interdiction de l'injustice|Les différentes bonnes actions|La réconciliation entre les gens|La piété, c'est le bon caractère|S'attacher à la Sunnah|Ce qui fait entrer au Paradis|Les droits d'Allah|Le vrai sens du renoncement (zuhd)|Ne pas nuire à soi-même ni aux autres|La preuve incombe au demandeur|Ordonner le bien et interdire le blâmable|La fraternité en islam|Se réunir pour évoquer Allah|La générosité d'Allah|Ce qui rapproche d'Allah|Passer sur les erreurs|Cultiver l'au-delà|Contrarier ses passions|Le repentir|Éviter de trop manger|Les traits de l'hypocrite|S'en remettre à Allah|Le mérite du dhikr|Chercher la science|La médisance|Propager le salut|S'aimer pour Allah""".split("|")
assert len(TITLES_FR) == 50
CORPUS = {n: f"nawawi40:{n}" for n in range(1, 43)}
CORPUS.update({44: "riyad:10", 45: "riyad:1296", 46: "riyad:759", 47: "riyad:702", 48: "riyad:844", 49: "riyad:168", 50: "riyad:1594"})
# 43 : pas d'arabe dans le corpus -> traduction du texte du livret
FR_43 = ("Al-Miqdam ibn Ma'dikarib (qu'Allah l'agrée) a rapporté que le Messager d'Allah ﷺ a dit : « Le fils d'Adam ne remplit "
         "pas de récipient pire que son ventre. Il suffit au fils d'Adam de quelques bouchées pour tenir son dos droit. "
         "S'il ne peut faire autrement, qu'il réserve un tiers à sa nourriture, un tiers à sa boisson et un tiers à son souffle. »")

import re
def clean(lines):
    txt = " ".join(lines)
    parts = re.split(r"\s*Source:\s*", txt)
    body, srcs = parts[0].strip(), []
    for part in parts[1:]:
        m = re.match(r"(.*?)(?:,\s*Grade:\s*(.*))?$", part.strip())
        srcs.append((m.group(1).strip(), (m.group(2) or "").strip()))
    if not srcs:  # fin de livret : « ... (Muslim) »
        m = re.search(r"\(([A-Za-z' ]+)\)\s*$", body)
        if m: srcs, body = [(m.group(1), "")], body[:m.start()].strip()
    return body, srcs


ah = []
for o in json.loads((PRIV / "ahadith_en.json").read_text(encoding="utf-8")):
    n = o["n"]
    body_en, sources = clean(o["lines"])
    h = H.get(CORPUS.get(n, ""))
    ah.append({"n": n, "title_fr": TITLES_FR[n - 1], "title_en": o["title"], "body_en": body_en,
               "sources": [{"ref": s, "grade": g} for s, g in sources],
               "arabic": h["arabic"] if h else None,
               "french": (h["french"] if h and h["french"] else (FR_43 if n == 43 else None)),
               "corpus": CORPUS.get(n)})

en = {o["n"]: o for o in json.loads((PRIV / "lessons_en.json").read_text(encoding="utf-8"))}
fr = {}
for f in sorted(PRIV.glob("lessons_fr_*.json")):
    for o in json.loads(f.read_text(encoding="utf-8")): fr[o["n"]] = o
lessons = [{"n": n, "title_fr": fr.get(n, {}).get("title_fr"), "text_fr": fr.get(n, {}).get("text_fr"),
            "title_en": en[n]["title"], "text_en": " ".join(en[n]["lines"])} for n in sorted(en)]
out = {"ahadith": ah, "lessons": lessons,
       "credit": "Contenu personnel : « The 50 Important Ahadith in Islam » et « The 50 Most Important Lessons of Quran » (Quran Memorization Guide, 2022), usage privé."}
(ROOT / "web" / "perso.json").write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
print(f"{len(ah)} hadiths ({sum(1 for a in ah if a['arabic'])} avec arabe, {sum(1 for a in ah if a['french'])} avec français), "
      f"{len(lessons)} leçons ({sum(1 for l in lessons if l['text_fr'])} traduites)")
