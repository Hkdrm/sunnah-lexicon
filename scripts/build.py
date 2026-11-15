#!/usr/bin/env python3
"""Construit db/sunnah.db et web/data.json à partir de sources ouvertes.

Collections :
  - nawawi40 : 42 hadiths, arabe + français      (fawazahmed0/hadith-api, Unlicense pour le code)
  - riyad, shamail, adab : arabe seulement          (AhmedBaset/hadith-json v1.2.0)

Choix de licence : pour Riyad as-Salihin, la traduction anglaise du jeu de données n'est PAS copiée
(provenance/licence non établies). Seuls le texte arabe (classique) et la structure en livres sont repris.

Degrés : jamais inventés. Ils sont lus dans la mention finale du texte (« رواه البخاري », « حديث حسن »…)
via scripts/arabic.py ; sinon « non renseigné ».
"""
import json
import sqlite3
import urllib.request
from pathlib import Path

from arabic import parse_attribution, stem, tokens

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "data" / "raw"
SRC = {
    "ara-nawawi": "https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions/ara-nawawi.min.json",
    "fra-nawawi": "https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions/fra-nawawi.min.json",
    "riyad": "https://raw.githubusercontent.com/AhmedBaset/hadith-json/v1.2.0/db/by_book/other_books/riyad_assalihin.json",
    "shamail": "https://raw.githubusercontent.com/AhmedBaset/hadith-json/v1.2.0/db/by_book/other_books/shamail_muhammadiyah.json",
    "adab": "https://raw.githubusercontent.com/AhmedBaset/hadith-json/v1.2.0/db/by_book/other_books/aladab_almufrad.json",
}
HJ = "AhmedBaset/hadith-json v1.2.0 (issu de sunnah.com) — licence du jeu de données à confirmer"
NUM_NOTE = "Numéro = ordre du jeu de données ; correspondance avec sunnah.com non vérifiée, donc pas de lien direct."


def fetch(name: str) -> dict:
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / f"{name}.json"
    if not path.exists():
        with urllib.request.urlopen(SRC[name], timeout=120) as r:
            path.write_bytes(r.read())
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    nawawi_idx = json.loads((ROOT / "data/seed/index_nawawi40.json").read_text(encoding="utf-8"))
    riyad_idx = json.loads((ROOT / "data/seed/index_riyad.json").read_text(encoding="utf-8"))

    db_path = ROOT / "db" / "sunnah.db"
    db_path.unlink(missing_ok=True)
    con = sqlite3.connect(db_path)
    con.executescript((ROOT / "db" / "schema.sql").read_text(encoding="utf-8"))

    COLL = [
        ("nawawi40", "Les 40 hadiths d'An-Nawawi", "الأربعون النووية", "Imam An-Nawawi",
         "https://sunnah.com/nawawi40", None),
        ("riyad", "Riyad as-Salihin (Les Jardins des vertueux)", "رياض الصالحين", "Imam An-Nawawi",
         "https://sunnah.com/riyadussalihin", None),
        ("shamail", "Ash-Shama'il al-Muhammadiyya (At-Tirmidhi)", "الشمائل المحمدية", "Imam At-Tirmidhi",
         "https://sunnah.com/shamail",
         "Décrit l'apparence, les habitudes et le comportement du Prophète ﷺ. Degrés non fournis par la source : vérifier chaque hadith."),
        ("adab", "Al-Adab al-Mufrad (Al-Boukhari)", "الأدب المفرد", "Imam Al-Boukhari",
         "https://sunnah.com/adab",
         "Recueil dont les hadiths sont de fiabilité variable (il n'est pas dans le Sahih). Degrés non fournis par la source : vérifier chaque hadith avant de s'y référer."),
    ]
    for c in COLL:
        con.execute("INSERT INTO collection (slug,name_fr,name_ar,author,site_url,note) VALUES (?,?,?,?,?,?)", c)

    # --- thèmes, situations, termes -------------------------------------------------------
    for kind, table in (("themes", "theme"), ("situations", "situation")):
        for it in nawawi_idx[kind]:
            con.execute(f"INSERT INTO {table} (slug,label_fr) VALUES (?,?)", (it["slug"], it["label_fr"]))
    for t in nawawi_idx["terms"]:
        con.execute("INSERT INTO term (slug,arabic,translit,definition_fr) VALUES (?,?,?,?)",
                    (t["slug"], t["arabic"], t["translit"], t["definition_fr"]))
    BOOKS = {}  # collection -> (raw, idx, slug_fn)
    for coll, key, seed, slug_fn in (
            ("riyad", "riyad", "index_riyad.json", lambda i, b: b["slug"]),
            ("shamail", "shamail", "index_shamail.json", lambda i, b: f"shamail-{i}"),
            ("adab", "adab", "index_adab.json", lambda i, b: f"adab-{i}")):
        raw = fetch(key)
        idx = json.loads((ROOT / "data/seed" / seed).read_text(encoding="utf-8"))
        book_ar = {c["id"]: c["arabic"].replace("ـ", "").strip() for c in raw["chapters"]}
        for bid, b in idx["books"].items():
            table = "theme" if b["kind"] == "theme" else "situation"
            con.execute(f"INSERT INTO {table} (slug,label_fr,label_ar) VALUES (?,?,?)",
                        (slug_fn(bid, b), b["label_fr"], book_ar.get(int(bid) if int(bid) != 99 else None)))
        BOOKS[coll] = (raw, idx, slug_fn)

    def ident(table, slug):
        return con.execute(f"SELECT id FROM {table} WHERE slug=?", (slug,)).fetchone()[0]

    def add_hadith(collection, number, arabic, french, verify_url, source_ar, source_fr, license_note):
        sources, grades = parse_attribution(arabic)
        grade, grade_by = ("non renseigné", None)
        if grades:
            grade, grade_by = grades[0]
        cur = con.execute(
            """INSERT INTO hadith (collection, number, arabic, french, verify_url, grade, grade_by, takhrij,
                                   source_arabic, source_french, license_note)
               VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
            (collection, number, arabic, french, verify_url, grade, grade_by,
             ", ".join(sources) or None, source_ar, source_fr, license_note))
        hid = cur.lastrowid
        for g, basis in grades:
            con.execute("INSERT INTO hadith_grade VALUES (?,?,?)", (hid, g, basis))
        return hid

    # --- Nawawi 40 ------------------------------------------------------------------------
    ara = {h["hadithnumber"]: h for h in fetch("ara-nawawi")["hadiths"]}
    fra = {h["hadithnumber"]: h for h in fetch("fra-nawawi")["hadiths"]}
    for n in sorted(ara):
        hid = add_hadith(
            "nawawi40", n, ara[n]["text"], fra.get(n, {}).get("text"), f"https://sunnah.com/nawawi40:{n}",
            "fawazahmed0/hadith-api (ara-nawawi)",
            "fawazahmed0/hadith-api (fra-nawawi) — traducteur non indiqué, à vérifier",
            "Texte arabe : domaine public. Traduction française : licence à confirmer.")
        meta = nawawi_idx["hadiths"].get(str(n), {})
        for s in meta.get("themes", []):
            con.execute("INSERT INTO hadith_theme VALUES (?,?)", (hid, ident("theme", s)))
        for s in meta.get("situations", []):
            con.execute("INSERT INTO hadith_situation VALUES (?,?)", (hid, ident("situation", s)))
        for s in meta.get("terms", []):
            con.execute("INSERT INTO hadith_term VALUES (?,?,'manual')", (hid, ident("term", s)))

    # --- Riyad, Shama'il, Adab al-Mufrad (arabe seulement) ------------------------------------
    for coll, (raw, idx, slug_fn) in BOOKS.items():
        for h in raw["hadiths"]:
            cid = h["chapterId"] if h["chapterId"] is not None else 99  # chapitre sans id (Shama'il)
            hid = add_hadith(coll, h["idInBook"], h["arabic"].strip(), None, None, HJ, None,
                             "Texte arabe uniquement. " + NUM_NOTE)
            b = idx["books"][str(cid)]
            if b["kind"] == "theme":
                con.execute("INSERT INTO hadith_theme VALUES (?,?)", (hid, ident("theme", slug_fn(str(cid), b))))
            else:
                con.execute("INSERT INTO hadith_situation VALUES (?,?)", (hid, ident("situation", slug_fn(str(cid), b))))

    # --- Liens termes <-> hadiths par radical (automatiques, à vérifier) ----------------------
    for t in nawawi_idx["terms"]:
        tid = ident("term", t["slug"])
        wanted = {stem(k) for k in t["keywords_ar"]}
        for hid, arabic in con.execute("SELECT id, arabic FROM hadith").fetchall():
            if wanted & {stem(x) for x in tokens(arabic)}:
                con.execute("INSERT OR IGNORE INTO hadith_term VALUES (?,?,'auto')", (hid, tid))
    con.commit()

    # --- Export JSON ------------------------------------------------------------------------
    con.row_factory = sqlite3.Row
    q = lambda sql, *a: [dict(r) for r in con.execute(sql, a)]
    hadiths = q("SELECT id, collection, number, arabic, french, verify_url, grade, grade_by, takhrij, review_status "
                "FROM hadith ORDER BY CASE collection WHEN 'nawawi40' THEN 0 WHEN 'riyad' THEN 1 WHEN 'shamail' THEN 2 ELSE 3 END, number")
    link = lambda table, link_tbl, col, hid: [r["slug"] for r in q(
        f"SELECT t.slug FROM {table} t JOIN {link_tbl} x ON x.{col}=t.id WHERE x.hadith_id=?", hid)]
    for h in hadiths:
        h["themes"] = link("theme", "hadith_theme", "theme_id", h["id"])
        h["situations"] = link("situation", "hadith_situation", "situation_id", h["id"])
        h["terms"] = link("term", "hadith_term", "term_id", h["id"])
        h["grades"] = q("SELECT grade, basis FROM hadith_grade WHERE hadith_id=?", h["id"])
        del h["id"]
    data = {
        "collections": q("SELECT slug, name_fr, name_ar, author, site_url, note FROM collection"),
        "themes": q("SELECT slug, label_fr, label_ar FROM theme"),
        "situations": q("SELECT slug, label_fr, label_ar FROM situation"),
        "terms": q("SELECT slug, arabic, translit, definition_fr, review_status FROM term"),
        "hadiths": hadiths,
    }
    (ROOT / "web" / "data.json").write_text(
        json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"{len(hadiths)} hadiths ({len(data['themes'])} thèmes, {len(data['situations'])} situations, "
          f"{len(data['terms'])} termes)")


if __name__ == "__main__":
    main()
