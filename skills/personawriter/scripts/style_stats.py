#!/usr/bin/env python3
"""style_stats.py - quantitative fingerprint of a writing style.

Two commands:

  analyze FILE [FILE ...] [--json OUT.json]
      Measure sentence rhythm, paragraph shape, punctuation habits, vocabulary
      texture, sentence openers and recurring phrases. Prints a readable report
      and optionally saves the numbers as a JSON "profile".

  compare PROFILE.json DRAFT_FILE
      Measure a new draft and show, metric by metric, how far it is from the
      profile. Use it as a sanity check while writing in a captured style.

Works on any language written in Unicode. Stop-words and person pronouns are
built in for English, German, French, Spanish, Portuguese, Italian and Arabic;
other languages get every metric except the person counts. Chinese and
Japanese are measured in characters instead of words.
Sentence splitting is heuristic, so treat numbers as good approximations, not
exact truth. Numbers describe the surface; the real style lives in the
qualitative analysis - use this as evidence, not as the goal.
"""
import argparse
import json
import re
import statistics
import sys
from collections import Counter

TASHKEEL = re.compile(r"[ً-ْٰـ]")  # Arabic diacritics + tatweel
CJK = "぀-ヿ㐀-䶿一-鿿豈-﫿"  # kana + Han (not Hangul: Korean uses spaces)
CJK_CHAR = re.compile(f"[{CJK}]")
# a token is one CJK character, or a run of letters (with inner apostrophes/hyphens)
WORD = re.compile(
    rf"[{CJK}]|(?:(?![{CJK}])[^\W\d_])+(?:['’\-](?:(?![{CJK}])[^\W\d_])+)*", re.UNICODE
)
CLOSERS = "\"'”’»)\\]」』"
SENT_SPLIT = re.compile(
    rf"(?<=[.!?؟…])[{CLOSERS}]*\s+"  # Latin/Arabic: end mark + whitespace
    rf"|(?<=[。！？])[{CLOSERS}]*"  # CJK: end mark, no space needed
)
QUOTED = re.compile(
    r"«[^»]*»|“[^”]*”|„[^“”]*[“”]"
    r"|「[^」]*」|\"[^\"\n]{1,400}\""
)

# Abbreviations that end in a period but do not end a sentence (casefolded, without final dot).
ABBREV = set(
    "mr mrs ms dr prof st jr sr vs etc e.g i.e cf fig no vol ch pp approx dept est inc ltd co "
    "z.b d.h u.a usw bzw ca nr vgl evtl ggf s bzgl inkl sog str "
    "m mme mlle p.ex av apr env "
    "sra srta dra p.ej pág núm "
    "sig dott ecc".split()
)

STOP = {
    "en": set("the a an and or but of to in on at for with as by is are was were be been it this that these those i you he she we they not from so if then than there their his her its our your my me him them who which what when".split()),
    "de": set("der die das und oder aber von zu in im auf an für mit als bei ist sind war waren sein es dies diese ich du er sie wir ihr nicht aus den dem des ein eine einen einem einer auch so wie wenn dass zum zur um nach über noch nur schon mehr sich hat haben wird werden".split()),
    "fr": set("le la les un une des et ou mais de du au aux à en dans sur pour par avec ce cette ces il elle ils elles nous vous je tu on ne pas que qui est sont était être a ont son sa ses leur leurs plus se comme si".split()),
    "es": set("el la los las un una unos unas y o pero de del al a en con por para que es son era fue ser se su sus lo le les no como más mi me te yo tú él ella nosotros ellos este esta estos si ya muy".split()),
    "pt": set("o a os as um uma uns umas e ou mas de do da dos das no na nos nas em com por para que é são era foi ser se seu sua seus não como mais eu me te você ele ela nós eles este esta isso muito já".split()),
    "it": set("il lo la i gli le un una e o ma di del della dei delle a al alla in nel nella con per che è sono era essere si suo sua non come più io mi ti tu lui lei noi voi loro questo questa anche già".split()),
    "ar": set("في من على إلى الى عن مع أن ان إن و ما لا هذا هذه ذلك تلك التي الذي الذين كان كانت كانوا هو هي هم هن أو ثم قد لم لن كل بعد قبل عند حتى أي كما إذا اذا لكن بل هنا هناك كي ليس".split()),
}
FIRST = {
    "en": set("i me my mine myself we us our ours".split()),
    "de": set("ich mich mir mein meine meinen meiner meines wir uns unser unsere unseren".split()),
    "fr": set("je j me m moi mon ma mes nous notre nos".split()),
    "es": set("yo me mí mi mis conmigo nosotros nosotras nos nuestro nuestra nuestros nuestras".split()),
    "pt": set("eu me mim meu minha meus minhas nós nos nosso nossa nossos nossas".split()),
    "it": set("io me mi mio mia miei mie noi ci nostro nostra nostri nostre".split()),
    "ar": set("أنا انا نحن".split()),
}
SECOND = {
    "en": set("you your yours yourself".split()),
    "de": set("du dich dir dein deine deinen deiner ihr euch euer eure".split()),
    "fr": set("tu te t toi ton ta tes vous votre vos".split()),
    "es": set("tú tu te ti tus contigo usted ustedes vosotros vosotras os vuestro vuestra".split()),
    "pt": set("tu te ti teu tua teus tuas você vocês vos".split()),
    "it": set("tu te ti tuo tua tuoi tue voi vi vostro vostra".split()),
    "ar": set("أنت انت أنتم انتم أنتما".split()),
}

PUNCT = {
    "comma": ",،、，",
    "semicolon": ";؛；",
    "colon": ":：",
    "dash": "—–",
    "parens": "(（",
    "quote_marks": "\"“”«»„「」",
    "question": "?؟？",
    "exclaim": "!！",
}


def quantile(sorted_vals, q):
    if not sorted_vals:
        return 0.0
    pos = (len(sorted_vals) - 1) * q
    lo, hi = int(pos), min(int(pos) + 1, len(sorted_vals) - 1)
    return sorted_vals[lo] + (sorted_vals[hi] - sorted_vals[lo]) * (pos - lo)


def detect_lang(text, tokens):
    """Return a language code with built-in word lists, 'cjk', or 'other'."""
    letters = [c for c in text if c.isalpha()]
    if letters and sum(1 for c in letters if CJK_CHAR.match(c)) / len(letters) > 0.3:
        return "cjk"
    lw = [t.casefold() for t in tokens]
    n = max(len(lw), 1)
    ratios = sorted(((sum(1 for t in lw if t in words) / n, lang) for lang, words in STOP.items()), reverse=True)
    (best, lang), (second, _) = ratios[0], ratios[1]
    # prose in a listed language is ~30-50% stop-words; an unlisted language that shares a few
    # short words (Dutch "de/en", Persian in Arabic script) scores lower and without a clear winner
    return lang if best >= 0.20 or (best >= 0.12 and best >= 2 * second) else "other"


def _continues(prev, nxt):
    """True if a split after `prev` was a false sentence break (abbreviation, lowercase follow-on)."""
    if not prev.endswith("."):
        return False
    if nxt[:1].islower():
        return True
    last = prev.rsplit(None, 1)[-1].casefold().rstrip(".")
    return last in ABBREV or (len(last) == 1 and last.isalpha())  # "J. K. Rowling"


def split_sentences(text):
    out = []
    for line in text.split("\n"):  # never merge across line breaks
        parts = [p.strip() for p in SENT_SPLIT.split(line) if p and p.strip()]
        merged = []
        for p in parts:
            if merged and _continues(merged[-1], p):
                merged[-1] += " " + p
            else:
                merged.append(p)
        out += merged
    return out


def get_paragraphs(text):
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    if len(paras) < 3 and text.count("\n") > 5:  # one paragraph per line
        paras = [p.strip() for p in text.split("\n") if p.strip()]
    return paras


def ngrams(tokens, n):
    return zip(*[tokens[i:] for i in range(n)])


def analyze_text(text):
    text = TASHKEEL.sub("", text.replace("\r\n", "\n"))
    tokens = WORD.findall(text)
    n_words = len(tokens)
    if n_words < 50:
        raise SystemExit("Sample too short to measure (need at least ~50 words; 1,500+ is far better).")
    lw = [t.casefold() for t in tokens]
    lang = detect_lang(text, tokens)
    stop = STOP.get(lang, set())

    # sentences
    sents = []
    for s in split_sentences(text):
        n = len(WORD.findall(s))
        if n:
            sents.append((s, n))
    lens = [n for _, n in sents]
    mean_len = statistics.fmean(lens)
    cv = statistics.pstdev(lens) / mean_len if mean_len else 0.0
    burst = (
        statistics.fmean(abs(a - b) for a, b in zip(lens, lens[1:])) / mean_len
        if len(lens) > 1 and mean_len
        else 0.0
    )
    sl = sorted(lens)
    # thresholds for "short" / "long" scale with the unit (CJK characters run ~2x a word count)
    short_max, long_min = (16, 60) if lang == "cjk" else (8, 30)

    # paragraphs
    paras = get_paragraphs(text)
    para_sents = [max(1, len(split_sentences(p))) for p in paras]
    para_words = [len(WORD.findall(p)) for p in paras]

    # punctuation per 1000 words
    per1k = {k: round(sum(text.count(c) for c in chars) * 1000 / n_words, 2) for k, chars in PUNCT.items()}
    per1k["ellipsis"] = round((text.count("…") + len(re.findall(r"\.{3}", text))) * 1000 / n_words, 2)

    # quoted speech share
    quoted_words = sum(len(WORD.findall(m.group(0))) for m in QUOTED.finditer(text))

    # lexical texture
    windows = [lw[i : i + 500] for i in range(0, n_words - 499, 500)]
    ttr = statistics.fmean(len(set(w)) / len(w) for w in windows) if windows else len(set(lw)) / n_words
    avg_word_len = statistics.fmean(len(t) for t in tokens)

    # openers
    openers = Counter(WORD.findall(s)[0].casefold() for s, _ in sents)
    top_openers = [(w, round(c / len(sents), 3)) for w, c in openers.most_common(8)]

    # persons (only where we have pronoun lists)
    if lang in FIRST:
        first = round(sum(1 for t in lw if t in FIRST[lang]) * 1000 / n_words, 2)
        second = round(sum(1 for t in lw if t in SECOND[lang]) * 1000 / n_words, 2)
    else:
        first = second = None

    # content words and recurring phrases
    min_len = 1 if lang == "cjk" else 3
    content = Counter(t for t in lw if t not in stop and len(t) >= min_len)
    min_count = 3 if n_words >= 3000 else 2
    joiner = "" if lang == "cjk" else " "
    phrases = []
    for n, keep in ((4, 8), (3, 12)):
        c = Counter(g for g in ngrams(lw, n) if not all(t in stop for t in g))
        found = [(joiner.join(g), k) for g, k in c.most_common(keep * 3) if k >= min_count][:keep]
        # drop shorter phrases that only echo an already-listed longer one
        found = [(g, k) for g, k in found if not any(g in longer and k <= kl for longer, kl in phrases)]
        phrases += found

    return {
        "language": lang,
        "unit": "characters" if lang == "cjk" else "words",
        "words": n_words,
        "sentences": len(sents),
        "paragraphs": len(paras),
        "mean_sentence_len": round(mean_len, 2),
        "median_sentence_len": round(statistics.median(lens), 2),
        "p10_sentence_len": round(quantile(sl, 0.10), 1),
        "p90_sentence_len": round(quantile(sl, 0.90), 1),
        "max_sentence_len": max(lens),
        "short_sentence_share": round(sum(1 for n in lens if n <= short_max) / len(lens), 3),
        "long_sentence_share": round(sum(1 for n in lens if n >= long_min) / len(lens), 3),
        "sentence_len_cv": round(cv, 3),
        "burstiness": round(burst, 3),
        "paragraph_len_sentences": round(statistics.fmean(para_sents), 2),
        "paragraph_len_words": round(statistics.fmean(para_words), 1),
        "avg_word_len": round(avg_word_len, 2),
        "ttr_500": round(ttr, 3),
        "quoted_share": round(quoted_words / n_words, 3),
        "first_person_per1k": first,
        "second_person_per1k": second,
        "opener_top1_share": top_openers[0][1] if top_openers else 0,
        "punct_per1k": per1k,
        "top_openers": top_openers,
        "top_content_words": content.most_common(25),
        "recurring_phrases": phrases,
    }


def report(p):
    unit = p.get("unit", "words")
    short_max, long_min = (16, 60) if p["language"] == "cjk" else (8, 30)
    L = []
    L.append(f"Language guess: {p['language']} | {p['words']} {unit}, {p['sentences']} sentences, {p['paragraphs']} paragraphs")
    if p["words"] < 1500:
        L.append("  (!) Under ~1,500 words: treat these numbers as a rough sketch.")
    if p["language"] == "other":
        L.append("  (language without built-in word lists: person counts skipped, phrase lists may include function words)")
    L.append("")
    L.append(f"SENTENCE RHYTHM ({unit})")
    L.append(f"  mean {p['mean_sentence_len']} | median {p['median_sentence_len']} | p10 {p['p10_sentence_len']} | p90 {p['p90_sentence_len']} | max {p['max_sentence_len']}")
    L.append(f"  short (<={short_max}): {p['short_sentence_share']:.0%} | long (>={long_min}): {p['long_sentence_share']:.0%}")
    L.append(f"  variation (cv): {p['sentence_len_cv']} | burstiness (avg jump between neighbours / mean): {p['burstiness']}")
    L.append("PARAGRAPHS")
    L.append(f"  {p['paragraph_len_sentences']} sentences / {p['paragraph_len_words']} {unit} on average")
    L.append(f"PUNCTUATION (per 1,000 {unit})")
    L.append("  " + " | ".join(f"{k} {v}" for k, v in p["punct_per1k"].items()))
    L.append("VOICE")
    if p["first_person_per1k"] is None:
        L.append(f"  quoted speech {p['quoted_share']:.0%} of {unit} (person counts not available for this language)")
    else:
        L.append(f"  first person {p['first_person_per1k']}/1k | second person {p['second_person_per1k']}/1k | quoted speech {p['quoted_share']:.0%} of words")
    if p["language"] in ("ar", "es", "pt", "it"):
        L.append("  (pronouns only - person carried by verb endings is not counted)")
    L.append("VOCABULARY TEXTURE")
    L.append(f"  avg word length {p['avg_word_len']} | type-token ratio (500-{unit[:-1]} windows) {p['ttr_500']}")
    L.append("SENTENCE OPENERS (share of sentences)")
    L.append("  " + ", ".join(f"{w} {s:.0%}" for w, s in p["top_openers"]))
    L.append("TOP CONTENT WORDS (mostly topic - do not confuse with style)")
    L.append("  " + ", ".join(f"{w} ({c})" for w, c in p["top_content_words"]))
    L.append("RECURRING PHRASES (candidate signature moves - check them in context)")
    L.append("  " + (" | ".join(f"{g} ({c})" for g, c in p["recurring_phrases"]) or "none found"))
    return "\n".join(L)


# metric: (hint if draft is higher, hint if lower, relative tolerance)
# rhythm-variation metrics are noisy on short drafts, so they get more room
HINTS = {
    "mean_sentence_len": ("sentences run long - split or cut", "sentences run short - let some clauses extend", 0.25),
    "sentence_len_cv": ("rhythm too uneven", "rhythm too uniform - vary sentence lengths", 0.35),
    "burstiness": ("jumps between short and long are stronger than the source", "not enough short/long alternation", 0.35),
    "paragraph_len_sentences": ("paragraphs too long - break them", "paragraphs too short - merge", 0.35),
    "avg_word_len": ("vocabulary heavier than the source", "vocabulary plainer than the source", 0.10),
    "ttr_500": ("vocabulary more varied than the source", "vocabulary more repetitive than the source", 0.15),
    "quoted_share": ("more quoted speech than the source", "less quoted speech than the source", 0.50),
    "first_person_per1k": ("more 'I/we' than the source", "less 'I/we' than the source", 0.40),
    "second_person_per1k": ("addresses the reader more than the source", "addresses the reader less than the source", 0.40),
    "opener_top1_share": ("sentence openers too repetitive", "sentence openers more varied than the source", 0.50),
}
PUNCT_TOL = 0.40
# below these absolute levels a difference is noise, not style
FLOOR = {"quoted_share": 0.03, "opener_top1_share": 0.05, "first_person_per1k": 2, "second_person_per1k": 2}
PUNCT_FLOOR = 1.5


def compare(profile, draft):
    scale = 1.5 if draft["words"] < 400 else 1.0  # short drafts: widen every tolerance
    rows = []
    for k, (hi, lo, tol) in HINTS.items():
        s, d = profile.get(k), draft.get(k)
        if s is None or d is None:
            continue
        rows.append((k, s, d, hi, lo, tol, FLOOR.get(k, 0)))
    for k, s in profile["punct_per1k"].items():
        d = draft["punct_per1k"].get(k, 0)
        rows.append((f"{k}/1k", s, d, f"more {k} than the source", f"fewer {k} than the source", PUNCT_TOL, PUNCT_FLOOR))

    L = [f"{'metric':<26}{'source':>10}{'draft':>10}   verdict"]
    off = 0
    for name, s, d, hi, lo, tol, floor in rows:
        ok = max(abs(s), abs(d)) < floor or abs(d - s) <= tol * scale * max(abs(s), 1e-9)
        if ok:
            verdict = "ok"
        else:
            off += 1
            verdict = "-> " + (hi if d > s else lo)
        L.append(f"{name:<26}{s:>10}{d:>10}   {verdict}")
    L.append("")
    L.append(f"{off} of {len(rows)} metrics outside their tolerance.")
    if draft["words"] < 200:
        L.append("(!) Draft under 200 words: these numbers are noisy - weigh them lightly.")
    L.append("Reminder: metrics catch surface drift only. Re-read the draft against the style guide's signature moves and never-list.")
    return "\n".join(L)


def read_files(paths):
    chunks = []
    for p in paths:
        with open(p, encoding="utf-8", errors="replace") as f:
            chunks.append(f.read())
    return "\n\n".join(chunks)


def main():
    if hasattr(sys.stdout, "reconfigure"):  # Windows consoles default to a legacy code page
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("analyze", help="fingerprint one or more text files")
    a.add_argument("files", nargs="+")
    a.add_argument("--json", help="save the profile as JSON")
    c = sub.add_parser("compare", help="compare a draft to a saved profile")
    c.add_argument("profile")
    c.add_argument("draft")
    args = ap.parse_args()

    if args.cmd == "analyze":
        prof = analyze_text(read_files(args.files))
        print(report(prof))
        if args.json:
            with open(args.json, "w", encoding="utf-8") as f:
                json.dump(prof, f, ensure_ascii=False, indent=2)
            print(f"\nProfile saved to {args.json}")
    else:
        with open(args.profile, encoding="utf-8") as f:
            prof = json.load(f)
        print(compare(prof, analyze_text(read_files([args.draft]))))


if __name__ == "__main__":
    sys.exit(main())
