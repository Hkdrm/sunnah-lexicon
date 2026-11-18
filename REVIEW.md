# Guide de relecture

Ce projet présente des textes de la Sunnah ; la qualité de l'index et des degrés repose sur une relecture par une personne qualifiée.
Les tableurs sont dans `review/` (CSV UTF-8, ouvrables dans Excel ou LibreOffice). Remplir **décision** (OK / à corriger / rejeter) et **correction**.

| Fichier | Quoi vérifier | Priorité |
|---|---|---|
| `6_pratiques.csv` | Les fiches « Pratiques » (siwak, main droite…) : le résumé français est-il fidèle aux hadiths cités ? Aucune qualification juridique n'est donnée volontairement. | **Très haute** |
| `8_duaa.csv` | Les invocations : **la vocalisation de l'arabe** (les voyelles sont écrites par une IA ; la phonétique en est déduite, donc une voyelle fausse donne une phonétique fausse), puis la traduction. | **Très haute** |
| `7_traductions.csv` | Les 36 traductions françaises faites par IA, avec l'arabe en regard : sens fidèle, formules et invocations correctes. | **Très haute** |
| `1_termes.csv` | Les 10 définitions du lexique : exactes, neutres, suffisantes ? | Haute |
| `5_degres.csv` | Les degrés « lus dans le texte » : à confirmer par un savant nommé (le degré affiché est celui d'An-Nawawi ou une déduction de la présence dans Boukhari/Mouslim, pas un grading indépendant). | Haute |
| `3_nawawi_index.csv` | Le rattachement des 42 hadiths aux thèmes, situations et termes. | Moyenne |
| `2_themes_situations.csv` | Les 146 libellés français (thèmes/situations) rédigés à partir des titres arabes. | Moyenne |
| `4_liens_auto.csv` | Les 153 liens terme↔hadith détectés par radical : faux positifs à rejeter. | Basse |

Régénérer après modification des données : `python3 scripts/build.py && python3 scripts/export_review.py`.
Les corrections validées sont à reporter dans `data/seed/*.json` (puis rebuild).
