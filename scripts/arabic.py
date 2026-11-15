"""Outils arabes partagés : normalisation, radical approximatif et lecture des mentions de source.

Le radical (`stem`) est un *radical léger approximatif* (retrait des préfixes/suffixes courants),
pas une vraie racine trilitère. Il DOIT rester identique à la version JavaScript de web/index.html
(vérifié par scripts/check_stem.js).
"""
import re

_TASHKEEL = re.compile("[ً-ٰٟـۖ-ۭ]")


def normalize(s: str) -> str:
    s = _TASHKEEL.sub("", s or "")
    s = re.sub("[أإآٱ]", "ا", s).replace("ى", "ي")
    return s


def tokens(s: str):
    return re.findall("[ء-ي]+", normalize(s))


_PREFIXES = ["وبال", "وال", "فال", "بال", "كال", "لل", "ال"]


def stem(w: str) -> str:
    for p in _PREFIXES:
        if w.startswith(p) and len(w) - len(p) >= 3:
            w = w[len(p):]
            break
    if w.endswith("ات") and len(w) >= 4:
        w = w[:-2] + "ة"  # pluriel féminin -> singulier
    else:
        for suf in ("ون", "ين", "ان", "ها", "هم", "هن", "كم", "نا"):
            if w.endswith(suf) and len(w) - len(suf) >= 3:
                w = w[: -len(suf)]
                break
    return w


def stems(s: str):
    return {stem(t) for t in tokens(s)}


# --- Mentions de source (takhrij) écrites dans le texte lui-même --------------------------
_SOURCES = [
    ("البخاري", "Boukhari"), ("مسلم", "Mouslim"), ("الترمذي", "Tirmidhi"),
    ("ابو داود", "Abou Dawoud"), ("النسائي", "Nasa'i"), ("ابن ماجه", "Ibn Majah"),
    ("مالك", "Malik (Muwatta)"), ("احمد", "Ahmad"), ("الدارمي", "Darimi"),
    ("البيهقي", "Bayhaqi"), ("الدارقطني", "Daraqutni"), ("ابن حبان", "Ibn Hibban"),
    ("الحاكم", "Hakim"), ("الطبراني", "Tabarani"),
]
_GRADE_PATTERNS = [
    (r"حديث\s+حسن\s+صحيح", "Hasan sahih"),
    (r"حديث\s+صحيح", "Sahih"),
    (r"حديث\s+حسن", "Hasan"),
    (r"(?:ب)?اسناد\s+صحيح", "Isnad sahih"),
    (r"(?:ب)?اسناد\s+حسن", "Isnad hasan"),
    (r"(?:ب)?اسانيد\s+صحيحه?", "Isnad sahih"),
    (r"(?:ب)?اسناد\s+ضعيف", "Isnad da'if"),
]


def citation_tail(arabic: str) -> str:
    n = normalize(arabic)
    idx = max(n.rfind(m) for m in ("رواه", "رواها", "اخرجه", "متفق عليه", "رواهما"))
    return n[idx:] if idx >= 0 else ""


def parse_attribution(arabic: str):
    """Retourne (sources, grades) lus dans la mention finale du texte.

    sources : liste de noms français. grades : liste de (degré, basis) où basis cite la mention.
    """
    tail = citation_tail(arabic)
    if not tail:
        return [], []
    sources = []
    if "متفق عليه" in tail:
        sources = ["Boukhari", "Mouslim"]
    toks = set(tokens(tail))
    joined = " ".join(tokens(tail))
    for ar, fr in _SOURCES:
        found = (ar in joined) if " " in ar else (ar in toks or ("و" + ar) in toks)
        if found and fr not in sources:
            sources.append(fr)
    grades = []
    for pat, label in _GRADE_PATTERNS:
        m = re.search(pat, tail)
        if m:
            grades.append((label, "An-Nawawi — mention dans le texte : « " + m.group(0) + " »"))
            break
    if not grades and ("Boukhari" in sources or "Mouslim" in sources):
        grades.append(("Sahih", "Rapporté dans " + " / ".join(
            "Sahih " + s for s in sources if s in ("Boukhari", "Mouslim")) + " (selon la mention du texte)"))
    return sources, grades
