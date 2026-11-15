# Lexique de la Sunnah

Lexique indexé des hadiths : recherche par mot (français/arabe), thème, situation de vie et terme du lexique.
Chaque hadith renvoie à sa source et à un lien de vérification sur sunnah.com.

**Cette application présente et référence des textes ; elle ne rend pas de fatwa.**

## État
- Corpus (3666 hadiths) : les 40 hadiths d'An-Nawawi (42, arabe + français), **Riyad as-Salihin** (1896), **Ash-Shama'il** (402) et **Al-Adab al-Mufrad** (1326), ces trois derniers en arabe seulement.
- Shama'il (57 chapitres) et Adab (57 livres) : un thème ou une situation par chapitre/livre, libellés français rédigés par nous (brouillon).
- Al-Adab al-Mufrad contient des hadiths de fiabilité variable : un avertissement s'affiche sur chaque hadith ; degrés non fournis par la source.
- Index : thèmes, situations de vie (repas, voyage, sommeil, salutations…) et 10 termes de lexique — **brouillon, à faire valider par un relecteur qualifié**.
- **Degrés** : jamais inventés. Ils sont lus dans la mention finale du texte (« رواه البخاري », « حديث حسن »…) ou déduits de la présence dans Boukhari/Mouslim ; sinon « non renseigné ». Plusieurs degrés par hadith possibles (`hadith_grade`).
- **Recherche arabe par radical léger** (النية trouve النيات). Approximation, pas une vraie racine trilitère ; identique en Python et JS (`node scripts/check_stem.js`).
- Liens terme ↔ hadith : manuels (Nawawi) ou **automatiques** par radical (à vérifier).
- Web statique hors ligne (PWA), sans serveur.

## Utilisation
```
python3 scripts/build.py          # télécharge les sources, génère db/sunnah.db et web/data.json
node scripts/check_stem.js        # vérifie JS == Python pour le radical arabe
cd web && python3 -m http.server  # puis ouvrir http://localhost:8000
```

## Relecture
Tableurs à faire valider dans `review/` ; mode d'emploi dans [REVIEW.md](REVIEW.md) (`python3 scripts/export_review.py` pour les régénérer).

## Structure
- `db/schema.sql` : schéma (hadith, collection, thème, terme, situation, liens).
- `data/seed/index_nawawi40.json` : index (thèmes, termes, situations) par hadith.
- `scripts/build.py` : import + génération.
- `web/` : application.

## Sources et licences
- Nawawi : [fawazahmed0/hadith-api](https://github.com/fawazahmed0/hadith-api) (code : Unlicense). Texte arabe : domaine public. **Traduction française : traducteur non indiqué ; licence à confirmer avant publication.**
- Riyad, Shama'il, Adab : [AhmedBaset/hadith-json](https://github.com/AhmedBaset/hadith-json) v1.2.0, issu de sunnah.com ; **licence du jeu de données à confirmer**. La traduction anglaise n'est volontairement **pas** reprise.
- **Numérotation** : le numéro affiché suit l'ordre du jeu de données. Pour Riyad (livre « Fondements » en dernier) il **ne correspond pas** à sunnah.com ; pour Shama'il et Adab la correspondance n'est pas vérifiée (sunnah.com bloque l'accès automatisé). Pas de lien direct par hadith tant que ce n'est pas établi.
- Vérification : https://sunnah.com

## Limites connues
- Riyad : seulement les 20 livres (pas les ~370 chapitres), pas de traduction française.
- Degrés « mention du texte » = l'avis d'An-Nawawi ou l'attribution à Boukhari/Mouslim, pas un grading indépendant (Albani, etc.).

## Feuille de route
1. Relecture de l'index et des définitions par un savant.
2. Correspondance de numérotation avec sunnah.com (à faire à la main ou avec accès autorisé), puis liens de vérification par hadith.
3. Traductions françaises sous licence claire ; degrés de savants nommés (Albani, Arnaout…).
4. Bukhari/Muslim ; degrés de l'Adab al-Mufrad par un savant nommé.
5. Recherche sémantique qui retrouve et cite, sans jamais paraphraser ni produire d'avis.

## Mise en ligne (GitHub Pages)
Le workflow `.github/workflows/pages.yml` publie le dossier `web/` à chaque push sur `main`.
Réglages à faire une fois : **Settings → Pages → Source : GitHub Actions**. Sur iPhone : Safari → Partager → « Sur l'écran d'accueil » (fonctionne ensuite hors ligne).

## Traductions
`data/seed/translations_fr.json` : traductions françaises rédigées par IA pour les hadiths cités dans les fiches (là où la source n'en fournit pas). Marquées « traduction automatique » dans l'app, à relire (`review/7_traductions.csv`). Elles n'ont pas de problème de licence puisqu'elles sont de notre fait.

## Interface
Pensée pour iPhone : titres larges, listes groupées, barre d'onglets (Pratiques · Hadiths · Infos), écran de détail par pratique, mode sombre.

## Pratiques
`data/seed/practices.json` : fiches concrètes (manger de la main droite, siwak avant la prière, sommeil, salutations…). Chaque fiche cite des hadiths du corpus ; `build.py` échoue si une référence n'existe pas. Les résumés sont rédigés par nous (brouillon) et ne donnent aucune qualification juridique.
