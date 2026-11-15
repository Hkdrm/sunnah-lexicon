# Lexique de la Sunnah

Lexique indexé des hadiths : recherche par mot (français/arabe), thème, situation de vie et terme du lexique.
Chaque hadith renvoie à sa source et à un lien de vérification sur sunnah.com.

**Cette application présente et référence des textes ; elle ne rend pas de fatwa.**

## État (MVP)
- Corpus : les 40 hadiths d'An-Nawawi (42 hadiths), arabe + français.
- Index : 8 thèmes, 4 situations, 10 termes — **brouillon, à faire valider par un relecteur qualifié**.
- Degré d'authenticité : « non renseigné » tant qu'une source de grading n'est pas intégrée (jamais inventé).
- Web statique hors ligne (PWA), sans serveur.

## Utilisation
```
python3 scripts/build.py          # télécharge les sources, génère db/sunnah.db et web/data.json
cd web && python3 -m http.server  # puis ouvrir http://localhost:8000
```

## Structure
- `db/schema.sql` : schéma (hadith, collection, thème, terme, situation, liens).
- `data/seed/index_nawawi40.json` : index (thèmes, termes, situations) par hadith.
- `scripts/build.py` : import + génération.
- `web/` : application.

## Sources et licences
- Données : [fawazahmed0/hadith-api](https://github.com/fawazahmed0/hadith-api) (code : Unlicense).
- Texte arabe : domaine public. **Traduction française : traducteur non indiqué dans le jeu de données ; licence à confirmer avant toute publication.**
- Vérification : https://sunnah.com/nawawi40

## Feuille de route
1. Relecture de l'index et des définitions par un savant.
2. Source de degrés d'authenticité (par hadith, avec le savant).
3. Riyad as-Salihin, Ash-Shama'il, Al-Adab al-Mufrad, puis Bukhari/Muslim.
4. Recherche sémantique qui retrouve et cite, sans jamais paraphraser ni produire d'avis.
