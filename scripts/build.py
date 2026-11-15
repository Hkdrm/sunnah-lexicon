#!/usr/bin/env python3
"""Importe les 40 hadiths d'An-Nawawi (arabe + français) et construit :
  - db/sunnah.db       (SQLite, schéma db/schema.sql)
  - web/data.json      (données pour l'application web statique)

Source : https://github.com/fawazahmed0/hadith-api (code sous licence Unlicense).
Les textes arabes sont du domaine public. La provenance exacte de la traduction
française est 'inconnue' dans ce jeu de données : elle est marquée à vérifier.
"""
import json
import sqlite3
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "data" / "raw"
BASE = "https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions/{}.min.json"
COLLECTION = "nawawi40"


def fetch(edition: str) -> dict:
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / f"{edition}.json"
    if not path.exists():
        with urllib.request.urlopen(BASE.format(edition), timeout=60) as r:
            path.write_bytes(r.read())
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    ara = {h["hadithnumber"]: h for h in fetch("ara-nawawi")["hadiths"]}
    fra = {h["hadithnumber"]: h for h in fetch("fra-nawawi")["hadiths"]}
    index = json.loads((ROOT / "data/seed/index_nawawi40.json").read_text(encoding="utf-8"))

    db_path = ROOT / "db" / "sunnah.db"
    db_path.unlink(missing_ok=True)
    con = sqlite3.connect(db_path)
    con.executescript((ROOT / "db" / "schema.sql").read_text(encoding="utf-8"))

    con.execute(
        "INSERT INTO collection VALUES (?,?,?,?,?)",
        (COLLECTION, "Les 40 hadiths d'An-Nawawi", "الأربعون النووية",
         "Imam An-Nawawi", "https://sunnah.com/nawawi40"),
    )

    for slug_kind, table in (("themes", "theme"), ("situations", "situation")):
        for it in index[slug_kind]:
            con.execute(f"INSERT INTO {table} (slug,label_fr) VALUES (?,?)", (it["slug"], it["label_fr"]))
    for t in index["terms"]:
        con.execute(
            "INSERT INTO term (slug,arabic,translit,definition_fr) VALUES (?,?,?,?)",
            (t["slug"], t["arabic"], t["translit"], t["definition_fr"]),
        )

    def ident(table: str, slug: str) -> int:
        return con.execute(f"SELECT id FROM {table} WHERE slug=?", (slug,)).fetchone()[0]

    for n in sorted(ara):
        grades = fra.get(n, {}).get("grades") or []
        grade, grade_by = ("non renseigné", None)
        if grades:
            grade, grade_by = grades[0].get("grade", grade), grades[0].get("name")
        cur = con.execute(
            """INSERT INTO hadith (collection, number, arabic, french, verify_url, grade, grade_by,
                                   source_arabic, source_french, license_note)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (COLLECTION, n, ara[n]["text"], fra.get(n, {}).get("text"),
             f"https://sunnah.com/nawawi40:{n}", grade, grade_by,
             "fawazahmed0/hadith-api (ara-nawawi)",
             "fawazahmed0/hadith-api (fra-nawawi) — traducteur non indiqué, à vérifier",
             "Texte arabe : domaine public. Traduction française : licence à confirmer."),
        )
        hid = cur.lastrowid
        meta = index["hadiths"].get(str(n), {})
        for s in meta.get("themes", []):
            con.execute("INSERT INTO hadith_theme VALUES (?,?)", (hid, ident("theme", s)))
        for s in meta.get("situations", []):
            con.execute("INSERT INTO hadith_situation VALUES (?,?)", (hid, ident("situation", s)))
        for s in meta.get("terms", []):
            con.execute("INSERT INTO hadith_term VALUES (?,?)", (hid, ident("term", s)))
    con.commit()

    # Export JSON pour le front statique.
    con.row_factory = sqlite3.Row
    q = lambda sql, *a: [dict(r) for r in con.execute(sql, a)]
    hadiths = q("SELECT id, collection, number, arabic, french, verify_url, grade, grade_by, review_status FROM hadith ORDER BY number")
    for h in hadiths:
        h["themes"] = [r["slug"] for r in q("SELECT t.slug FROM theme t JOIN hadith_theme x ON x.theme_id=t.id WHERE x.hadith_id=?", h["id"])]
        h["situations"] = [r["slug"] for r in q("SELECT t.slug FROM situation t JOIN hadith_situation x ON x.situation_id=t.id WHERE x.hadith_id=?", h["id"])]
        h["terms"] = [r["slug"] for r in q("SELECT t.slug FROM term t JOIN hadith_term x ON x.term_id=t.id WHERE x.hadith_id=?", h["id"])]
    data = {
        "collection": q("SELECT * FROM collection")[0],
        "themes": q("SELECT slug, label_fr FROM theme"),
        "situations": q("SELECT slug, label_fr FROM situation"),
        "terms": q("SELECT slug, arabic, translit, definition_fr, review_status FROM term"),
        "hadiths": hadiths,
    }
    (ROOT / "web" / "data.json").write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(hadiths)} hadiths, {len(data['themes'])} thèmes, {len(data['terms'])} termes")


if __name__ == "__main__":
    main()
