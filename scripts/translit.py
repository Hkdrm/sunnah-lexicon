#!/usr/bin/env python3
"""Phonétique française approximative à partir d'un texte arabe VOCALISÉ.

La phonétique est générée (jamais écrite à la main) pour rester cohérente avec l'arabe affiché ;
si une voyelle est fausse dans l'arabe, la phonétique le sera aussi : l'arabe doit être relu.

Convention : ou = u, â î û = voyelles longues, dj = ج, kh = خ, gh = غ, ch = ش, th = ث (anglais « think »),
dh = ذ (anglais « this »), ‘ = ع, ' = hamza. Les emphatiques ص ض ط ظ sont rendues s d t dh
(approximation) ; ح et ه sont toutes deux h.
Les assimilations (lettres solaires), l'élision du alif de liaison (hamzat al-wasl) et les terminaisons
(i'rab) sont rendues comme dans la récitation continue.
"""
import re
import unicodedata

FATHA, DAMMA, KASRA, SHADDA, SUKUN = "َ", "ُ", "ِ", "ّ", "ْ"
TAN_F, TAN_D, TAN_K, DAGGER, MADDA, WASLA = "ً", "ٌ", "ٍ", "ٰ", "ٓ", "ٱ"
MARKS = {FATHA, DAMMA, KASRA, SHADDA, SUKUN, TAN_F, TAN_D, TAN_K, DAGGER, MADDA}
LET = {
    "ب": "b", "ت": "t", "ث": "th", "ج": "dj", "ح": "h", "خ": "kh", "د": "d", "ذ": "dh", "ر": "r", "ز": "z",
    "س": "s", "ش": "ch", "ص": "s", "ض": "d", "ط": "t", "ظ": "dh", "ع": "‘", "غ": "gh", "ف": "f", "ق": "q",
    "ك": "k", "ل": "l", "م": "m", "ن": "n", "ه": "h", "و": "w", "ي": "y",
}
SUN = set("تثدذرزسشصضطظلن")
HAMZA_CARRIERS = set("ءأإؤئ")
SHORT = {FATHA: "a", DAMMA: "ou", KASRA: "i"}
TANWIN = {TAN_F: "an", TAN_D: "oun", TAN_K: "in"}
LONG = {"a": "â", "ou": "û", "i": "î"}
PAUSE = set(".،؛:؟!…\n")


def clusters(word):
    """Découpe un mot en [lettre, ensemble de signes]."""
    out = []
    for ch in word:
        if ch in MARKS:
            if out: out[-1][1].add(ch)
        elif ch == "ـ":
            continue
        else:
            out.append([("ا" if ch == WASLA else ch), set(), ch == WASLA])
    return out


def vowel_of(marks):
    for m, v in SHORT.items():
        if m in marks: return v
    for m, v in TANWIN.items():
        if m in marks: return v
    return None


def ends_with_vowel(phon):
    return bool(phon) and phon[-1] in "aiouâîû" and not phon.endswith("‘")


def word_phon(word, prev_open):
    """Phonétique d'un mot. prev_open : le mot précédent finit par une voyelle (donc le alif de liaison s'élide)."""
    cl = clusters(word)
    base = re.sub("[" + "".join(MARKS) + "]", "", word)
    if not cl:
        return ""
    # --- cas particulier : Allah / Allahumma, avec ou sans préfixe (bi, li, wa, fa) ---
    m = re.fullmatch(r"([وفبلك]?)(ا|ٱ)?لل[هـ]م?", base)
    if m and base.replace("ٱ", "ا").endswith(("لله", "اللهم", "لهم")) and "ل" in base:
        pass  # géré par la boucle générale (assimilation lam/lam) ci-dessous
    out, i, n = [], 0, len(cl)
    first_done = False
    while i < n:
        ch, marks, wasl_flag = cl[i]
        nxt = cl[i + 1] if i + 1 < n else None
        v = vowel_of(marks)
        # --- alif initial : article ou alif de liaison ---
        prefix_ok = 0 < i <= 2 and all(c[0] in "وفبلك" and not (c[1] & {SUKUN}) for c in cl[:i])  # wa-bi-l-... : préfixes collés
        if ch == "ا" and (i == 0 or prefix_ok):
            starts_word = i == 0
            prefixed = i > 0
            if nxt and nxt[0] == "ل" and not (nxt[1] & {FATHA, DAMMA, KASRA, TAN_F, TAN_D, TAN_K}):  # article défini (la lam ne porte pas de voyelle)
                elide = prev_open if starts_word else True
                after = cl[i + 2] if i + 2 < n else None
                lam_marks = nxt[1]
                # assimilation si la lettre suivante est solaire (avec chadda) ou si la lam elle-même porte la chadda (Allah)
                if SHADDA in lam_marks:  # الَّـ : la lam article + lettre doublée = « Allah », « allâdhî »...
                    c = "l"
                    vv = vowel_of(lam_marks - {SHADDA}) or ""
                    pre = "" if elide else "a"
                    out.append(pre + c + c + (vv if vv else ""))
                    i += 2
                    first_done = True
                    continue
                if after and after[0] in SUN and SHADDA in after[1]:
                    c = LET[after[0]]
                    vv = vowel_of(after[1] - {SHADDA}) or ""
                    pre = "" if elide else "a"
                    sep = "" if c == "l" else "-"  # « Allah » : pas de trait d'union (llah)
                    out.append(pre + c + sep + c + vv)
                    i += 3
                    first_done = True
                    continue
                out.append(("l-" if elide else "al-"))
                i += 2
                first_done = True
                continue
            # alif de liaison d'un verbe/nom (اغْفِرْ, اسْمِ…)
            if v is None and nxt and SUKUN in nxt[1] and not (nxt[0] in "اويى"):  # alif de liaison : la consonne suivante porte un soukoun (اغْفِرْ, اسْمِ)
                elide = prev_open if starts_word else True
                third = cl[i + 2] if i + 2 < n else None
                init = "ou" if (third and DAMMA in third[1]) else "i"
                if not elide:
                    out.append(init)
                i += 1
                first_done = True
                continue
        # --- lettres de prolongation ---
        if ch in "اىو" + "ي" and out and not (marks & {FATHA, DAMMA, KASRA, TAN_F, TAN_D, TAN_K}) :
            prev_ch, prev_marks = cl[i - 1][0], cl[i - 1][1]
            pv = vowel_of(prev_marks)
            if ch in "اى" and pv == "a" and SHADDA not in marks:
                out[-1] = out[-1][:-1] + "â" if out[-1].endswith("a") else out[-1] + "â"
                i += 1; continue
            if ch == "و" and pv == "ou" and not (marks & {SHADDA}):
                out[-1] = out[-1][:-2] + "û" if out[-1].endswith("ou") else out[-1]
                i += 1; continue
            if ch == "ي" and pv == "i" and not (marks & {SHADDA}):
                out[-1] = out[-1][:-1] + "î" if out[-1].endswith("i") else out[-1]
                i += 1; continue
            if ch == "و" and pv == "a" and (SUKUN in marks or not marks):
                out[-1] = out[-1][:-1] + "aw"; i += 1; continue
            if ch == "ي" and pv == "a" and (SUKUN in marks or not marks):
                out[-1] = out[-1][:-1] + "ay"; i += 1; continue
            if ch in "اى" and not marks and not v:
                i += 1; continue
        # --- ta marbouta ---
        if ch == "ة":
            if v: out.append("t" + v)
            i += 1; continue
        # --- hamza ---
        if ch in HAMZA_CARRIERS:
            sound = "'"
            if ch in "أإ" and i == 0:
                sound = ""
            elif out and out[-1].endswith("-"):
                sound = ""  # al-amni : pas d'apostrophe après l'article
            elif ch in "أإ" and 0 < i <= 2 and all(c[0] in "وفبلك" for c in cl[:i]) and not out[-1].endswith("-"):
                sound = "-"  # wa-innâ, wa-ilayhi : pas d'apostrophe après une particule
            if MADDA in marks or (ch == "آ"):
                out.append((sound + "â")); i += 1; continue
            out.append(sound + (v if v else "")); i += 1; continue
        if ch == "آ":
            out.append("â"); i += 1; continue
        # --- consonne ---
        c = LET.get(ch)
        if c is None:
            i += 1; continue
        if ch == "ا":
            i += 1; continue
        if SHADDA in marks:
            c = c + c
        vv = v or ""
        if DAGGER in marks:
            vv = (vv + "") if vv else "a"
            vv = "â" if vv == "a" else vv
        # voyelle longue par lettre suivante déjà gérée ; tanwin
        out.append(c + vv)
        i += 1
    return "".join(out)


def transliterate(text):
    """Texte arabe vocalisé -> phonétique."""
    text = unicodedata.normalize("NFC", text)
    tokens = re.findall(r"[ء-يٱٰ-ٳً-ٓـ]+|[.،؛:؟!…\n]|\S", text)
    out, prev_open = [], False
    for t in tokens:
        if t in PAUSE:
            out.append(t if t != "\n" else " / ")
            prev_open = False
            continue
        if not re.match(r"[ء-يٱ]", t):
            out.append(t); continue
        w = word_phon(t, prev_open)
        # fin de mot : pause = on ne prononce pas la terminaison ? (ici : récitation continue, terminaisons gardées)
        out.append(w)
        prev_open = ends_with_vowel(w)
    s = " ".join(x for x in out if x != "")
    s = re.sub(r"\s+([،.؛:!?…])", r"\1", s)
    s = s.replace(" ،", ",").replace("،", ",").replace("؛", ";").replace("؟", "?")
    s = re.sub(r"\s+", " ", s).strip()
    s = re.sub(r"\ba(l{2})", lambda m: "A" + m.group(1), s)  # Allah, Allahoumma au début
    return s
