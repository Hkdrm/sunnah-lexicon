#!/usr/bin/env python3
"""Exporte des tableurs (CSV UTF-8 avec BOM, lisibles dans Excel/LibreOffice) pour la relecture
par un savant ou un relecteur qualifié. Lire d'abord `python3 scripts/build.py`.

Fichiers générés dans review/ :
  1_termes.csv           définitions du lexique à valider
  2_themes_situations.csv libellés français des thèmes/situations
  3_nawawi_index.csv     rattachement des 42 hadiths d'An-Nawawi aux thèmes/termes
  4_liens_auto.csv       liens terme<->hadith détectés automatiquement (à confirmer ou rejeter)
  5_degres.csv           degrés déduits du texte (à confirmer par un savant nommé)

Colonnes à remplir par le relecteur : « décision » (OK / à corriger / rejeter) et « correction ».
"""
import csv
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "review"


def write(name, header, rows):
    OUT.mkdir(exist_ok=True)
    with open(OUT / name, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(header + ["décision", "correction"])
        for r in rows:
            w.writerow(list(r) + ["", ""])
    print(f"{name}: {len(rows)} lignes")


def main():
    con = sqlite3.connect(ROOT / "db" / "sunnah.db")
    q = lambda sql, *a: con.execute(sql, a).fetchall()

    write("1_termes.csv", ["slug", "arabe", "translittération", "définition (FR)", "nb hadiths liés"],
          q("""SELECT t.slug, t.arabic, t.translit, t.definition_fr, COUNT(x.hadith_id)
               FROM term t LEFT JOIN hadith_term x ON x.term_id=t.id GROUP BY t.id"""))

    rows = []
    for kind in ("theme", "situation"):
        link = f"hadith_{kind}"
        rows += q(f"""SELECT '{kind}', k.slug, COALESCE(MIN(h.collection),''), k.label_fr, COALESCE(k.label_ar,''),
                             COUNT(x.hadith_id)
                      FROM {kind} k LEFT JOIN {link} x ON x.{kind}_id=k.id
                      LEFT JOIN hadith h ON h.id=x.hadith_id GROUP BY k.id ORDER BY 3, 2""")
    write("2_themes_situations.csv",
          ["type", "slug", "recueil", "libellé (FR)", "titre arabe de la source", "nb hadiths"], rows)

    write("3_nawawi_index.csv", ["n°", "début de la traduction", "thèmes", "situations", "termes (manuels)"],
          q("""SELECT h.number, SUBSTR(h.french,1,140),
                      (SELECT GROUP_CONCAT(t.label_fr,' ; ') FROM theme t JOIN hadith_theme x ON x.theme_id=t.id WHERE x.hadith_id=h.id),
                      (SELECT GROUP_CONCAT(t.label_fr,' ; ') FROM situation t JOIN hadith_situation x ON x.situation_id=t.id WHERE x.hadith_id=h.id),
                      (SELECT GROUP_CONCAT(t.translit,' ; ') FROM term t JOIN hadith_term x ON x.term_id=t.id
                         WHERE x.hadith_id=h.id AND x.link_source='manual')
               FROM hadith h WHERE h.collection='nawawi40' ORDER BY h.number"""))

    write("4_liens_auto.csv", ["terme", "recueil", "n°", "texte arabe (début)"],
          q("""SELECT t.translit, h.collection, h.number, SUBSTR(h.arabic,1,160)
               FROM hadith_term x JOIN term t ON t.id=x.term_id JOIN hadith h ON h.id=x.hadith_id
               WHERE x.link_source='auto' ORDER BY t.translit, h.collection, h.number"""))

    write("5_degres.csv", ["recueil", "n°", "degré", "base", "recueils cités", "texte arabe (début)"],
          q("""SELECT h.collection, h.number, g.grade, g.basis, COALESCE(h.takhrij,''), SUBSTR(h.arabic,1,120)
               FROM hadith_grade g JOIN hadith h ON h.id=g.hadith_id
               WHERE h.collection='nawawi40' OR h.grade NOT IN ('Sahih')
               ORDER BY h.collection, h.number"""))


if __name__ == "__main__":
    main()
