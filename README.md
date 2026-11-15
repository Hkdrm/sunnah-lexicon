# Lexique de la Sunnah

Lexique indexé des hadiths : recherche par mot (français/arabe), thème, situation de vie et terme du lexique.
Chaque hadith renvoie à sa source et à un lien de vérification sur sunnah.com.

**Cette application présente et référence des textes ; elle ne rend pas de fatwa.**

## État
- Corpus : les 40 hadiths d'An-Nawawi (42 hadiths, arabe + français) et **Riyad as-Salihin** (1896 hadiths, arabe seulement).
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

## Structure
- `db/schema.sql` : schéma (hadith, collection, thème, terme, situation, liens).
- `data/seed/index_nawawi40.json` : index (thèmes, termes, situations) par hadith.
- `scripts/build.py` : import + génération.
- `web/` : application.

## Sources et licences
- Nawawi : [fawazahmed0/hadith-api](https://github.com/fawazahmed0/hadith-api) (code : Unlicense). Texte arabe : domaine public. **Traduction française : traducteur non indiqué ; licence à confirmer avant publication.**
- Riyad as-Salihin : [AhmedBaset/hadith-json](https://github.com/AhmedBaset/hadith-json) v1.2.0, issu de sunnah.com ; **licence du jeu de données à confirmer**. La traduction anglaise n'est volontairement **pas** reprise.
- **Numérotation Riyad** : le numéro affiché suit l'ordre du jeu de données (livre « Fondements » en dernier) et **ne correspond pas** à la numérotation de sunnah.com. Pas de lien direct par hadith tant que la correspondance n'est pas établie.
- Vérification : https://sunnah.com

## Limites connues
- Riyad : seulement les 20 livres (pas les ~370 chapitres), pas de traduction française.
- Degrés « mention du texte » = l'avis d'An-Nawawi ou l'attribution à Boukhari/Mouslim, pas un grading indépendant (Albani, etc.).

## Feuille de route
1. Relecture de l'index et des définitions par un savant.
2. Correspondance de numérotation Riyad ↔ sunnah.com, puis liens de vérification par hadith.
3. Traductions françaises sous licence claire ; degrés de savants nommés (Albani, Arnaout…).
4. Ash-Shama'il, Al-Adab al-Mufrad, Bukhari/Muslim.
5. Recherche sémantique qui retrouve et cite, sans jamais paraphraser ni produire d'avis.
