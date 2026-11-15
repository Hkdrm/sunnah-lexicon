-- Schéma du lexique indexé de la Sunnah.
-- Principe : le hadith est l'unité de base ; thèmes et termes du lexique y renvoient.

PRAGMA foreign_keys = ON;

CREATE TABLE collection (
    slug        TEXT PRIMARY KEY,          -- ex. 'nawawi40'
    name_fr     TEXT NOT NULL,
    name_ar     TEXT,
    author      TEXT,
    site_url    TEXT                       -- URL de vérification (sunnah.com)
);

CREATE TABLE hadith (
    id              INTEGER PRIMARY KEY,
    collection      TEXT NOT NULL REFERENCES collection(slug),
    number          INTEGER NOT NULL,
    arabic          TEXT NOT NULL,
    french          TEXT,                  -- NULL si la licence ne permet pas la copie
    verify_url      TEXT,                  -- lien direct pour vérifier le hadith
    grade           TEXT NOT NULL DEFAULT 'non renseigné',  -- sahih / hasan / da'if / non renseigné
    grade_by        TEXT,                  -- savant ayant établi le degré
    source_arabic   TEXT,                  -- provenance du texte arabe
    source_french   TEXT,                  -- provenance de la traduction
    license_note    TEXT,
    review_status   TEXT NOT NULL DEFAULT 'à relire',      -- à relire / validé
    UNIQUE (collection, number)
);

CREATE TABLE theme (
    id          INTEGER PRIMARY KEY,
    slug        TEXT NOT NULL UNIQUE,
    label_fr    TEXT NOT NULL,
    parent_id   INTEGER REFERENCES theme(id)
);

CREATE TABLE hadith_theme (
    hadith_id   INTEGER NOT NULL REFERENCES hadith(id),
    theme_id    INTEGER NOT NULL REFERENCES theme(id),
    PRIMARY KEY (hadith_id, theme_id)
);

CREATE TABLE term (
    id              INTEGER PRIMARY KEY,
    slug            TEXT NOT NULL UNIQUE,
    arabic          TEXT NOT NULL,
    translit        TEXT NOT NULL,
    definition_fr   TEXT NOT NULL,
    review_status   TEXT NOT NULL DEFAULT 'à relire'
);

CREATE TABLE hadith_term (
    hadith_id   INTEGER NOT NULL REFERENCES hadith(id),
    term_id     INTEGER NOT NULL REFERENCES term(id),
    PRIMARY KEY (hadith_id, term_id)
);

-- Situations de vie (entrée par contexte : voyage, repas, colère...)
CREATE TABLE situation (
    id          INTEGER PRIMARY KEY,
    slug        TEXT NOT NULL UNIQUE,
    label_fr    TEXT NOT NULL
);

CREATE TABLE hadith_situation (
    hadith_id    INTEGER NOT NULL REFERENCES hadith(id),
    situation_id INTEGER NOT NULL REFERENCES situation(id),
    PRIMARY KEY (hadith_id, situation_id)
);
