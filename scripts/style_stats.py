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

Works on any language written in Unicode (English, German, Arabic, ...).
Sentence splitting is heuristic (. ! ? ؟ …), so treat numbers as good
approximations, not exact truth. Numbers describe the surface; the real style
lives in the qualitative analysis - use this as evidence, not as the goal.
"""
import argparse
import json
import re
import statistics
import sys
from collections import Counter

TASHKEEL = re.compile(r"[\u064B-\u0652\u0670\u0640]")  # Arabic diacritics + tatweel
WORD = re.compile(r"[^\W\d_]+(?:['\u2019\-][^\W\d_]+)*", re.UNICODE)
SENT_SPLIT = re.compile(r"(?<=[.!?\u061F\u2026])[\"'\u201D\u00BB)\]]*\s+|\n+")
QUOTED = re.compile(
    r"\u00AB[^\u00BB]*\u00BB|\u201C[^\u201D]*\u201D|\u201E[^\u201C\u201D]*[\u201C\u201D]|\"[^\"\n]{1,400}\""
)

STOP = {
    "en": set("the a an and or but of to in on at for with as by is are was were be been it this that these those i you he she we they not from so if then than there their his her its our your my me him them who which what when".split()),
    "de": set("der die das und oder aber von zu in im auf an für mit als bei ist sind war waren sein es dies diese ich du er sie wir ihr nicht aus den dem des ein eine einen einem einer auch so wie wenn dass zum zur um nach über noch nur schon mehr sich hat haben wird werden".split()),
    "ar": set("في من على إلى الى عن مع أن ان إن و ما لا هذا هذه ذلك تلك التي الذي الذين كان كانت كانوا هو هي هم هن أو ثم قد لم لن كل بعد قبل عند حتى أي كما إذا اذا لكن بل هنا هناك كي ليس".split()),
}
FIRST = {
    "en": set("i me my mine myself we us our ours".split()),
    "de": set("ich mich mir mein meine meinen meiner meines wir uns unser unsere unseren".split()),
    "ar": set("أنا انا نحن".split()),
}
SECOND = {
    "en": set("you your yours yourself".split()),
    "de": set("du dich dir dein deine deinen deiner ihr euch euer eure".split()),
    "ar": set("أنت انت أنتم انتم أنتما".split()),
}

PUNCT = {
    "comma": ",\u060C",
    "semicolon": ";\u061B",
    "colon": ":",
    "dash": "\u2014\u2013",
    "parens": "(",
    "quote_marks": "\"\u201C\u201D\u00AB\u00BB\u201E",
    "question": "?\u061F",
    "exclaim": "!",
}


def quantile(sorted_vals, q):
    if not sorted_vals:
        return 0.0
    pos = (len(sorted_vals) - 1) * q
    lo, hi = int(pos), min(int(pos) + 1, len(sorted_vals) - 1)
    return sorted_vals[lo] + (sorted_vals[hi] - sorted_vals[lo]) * (pos - lo)


def detect_lang(text, tokens):
    letters = [c for c in text if c.isalpha()]
    if letters:
        arabic = sum(1 for c in letters if "\u0600" <= c <= "\u06FF")
        if arabic / len(letters) > 0.5:
            return "ar"
    lw = [t.casefold() for t in tokens]
    de = sum(1 for t in lw if t in STOP["de"])
    en = sum(1 for t in lw if t in STOP["en"])
    return "de" if de > en else "en"


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
    stop = STOP[lang]

    # sentences
    sents = []
    for s in SENT_SPLIT.split(text):
        if s and s.strip():
            n = len(WORD.findall(s))
            if n:
                sents.append((s.strip(), n))
    lens = [n for _, n in sents]
    mean_len = statistics.fmean(lens)
    cv = statistics.pstdev(lens) / mean_len if mean_len else 0.0
    burst = (
        statistics.fmean(abs(a - b) for a, b in zip(lens, lens[1:])) / mean_len
        if len(lens) > 1 and mean_len
        else 0.0
    )
    sl = sorted(lens)

    # paragraphs
    paras = get_paragraphs(text)
    para_sents = [max(1, len([1 for s in SENT_SPLIT.split(p) if s and s.strip()])) for p in paras]
    para_words = [len(WORD.findall(p)) for p in paras]

    # punctuation per 1000 words
    per1k = {k: round(sum(text.count(c) for c in chars) * 1000 / n_words, 2) for k, chars in PUNCT.items()}
    per1k["ellipsis"] = round((text.count("\u2026") + len(re.findall(r"\.{3}", text))) * 1000 / n_words, 2)

    # quoted speech share
    quoted_words = sum(len(WORD.findall(m.group(0))) for m in QUOTED.finditer(text))

    # lexical texture
    windows = [lw[i : i + 500] for i in range(0, n_words - 499, 500)]
    ttr = statistics.fmean(len(set(w)) / len(w) for w in windows) if windows else len(set(lw)) / n_words
    avg_word_len = statistics.fmean(len(t) for t in tokens)

    # openers
    openers = Counter(WORD.findall(s)[0].casefold() for s, _ in sents)
    top_openers = [(w, round(c / len(sents), 3)) for w, c in openers.most_common(8)]

    # persons
    first = sum(1 for t in lw if t in FIRST[lang]) * 1000 / n_words
    second = sum(1 for t in lw if t in SECOND[lang]) * 1000 / n_words

    # content words and recurring phrases
    content = Counter(t for t in lw if t not in stop and len(t) > 2)
    min_count = 3 if n_words >= 3000 else 2
    phrases = []
    for n, keep in ((4, 8), (3, 12)):
        c = Counter(g for g in ngrams(lw, n) if not all(t in stop for t in g))
        found = [(" ".join(g), k) for g, k in c.most_common(keep * 3) if k >= min_count][:keep]
        # drop shorter phrases that only echo an already-listed longer one
        found = [(g, k) for g, k in found if not any(g in longer and k <= kl for longer, kl in phrases)]
        phrases += found

    return {
        "language": lang,
        "words": n_words,
        "sentences": len(sents),
        "paragraphs": len(paras),
        "mean_sentence_len": round(mean_len, 2),
        "median_sentence_len": round(statistics.median(lens), 2),
        "p10_sentence_len": round(quantile(sl, 0.10), 1),
        "p90_sentence_len": round(quantile(sl, 0.90), 1),
        "max_sentence_len": max(lens),
        "short_sentence_share": round(sum(1 for n in lens if n <= 8) / len(lens), 3),
        "long_sentence_share": round(sum(1 for n in lens if n >= 30) / len(lens), 3),
        "sentence_len_cv": round(cv, 3),
        "burstiness": round(burst, 3),
        "paragraph_len_sentences": round(statistics.fmean(para_sents), 2),
        "paragraph_len_words": round(statistics.fmean(para_words), 1),
        "avg_word_len": round(avg_word_len, 2),
        "ttr_500": round(ttr, 3),
        "quoted_share": round(quoted_words / n_words, 3),
        "first_person_per1k": round(first, 2),
        "second_person_per1k": round(second, 2),
        "opener_top1_share": top_openers[0][1] if top_openers else 0,
        "punct_per1k": per1k,
        "top_openers": top_openers,
        "top_content_words": content.most_common(25),
        "recurring_phrases": phrases,
    }


def report(p):
    L = []
    L.append(f"Language guess: {p['language']} | {p['words']} words, {p['sentences']} sentences, {p['paragraphs']} paragraphs")
    if p["words"] < 1500:
        L.append("  (!) Under ~1,500 words: treat these numbers as a rough sketch.")
    L.append("")
    L.append("SENTENCE RHYTHM")
    L.append(f"  mean {p['mean_sentence_len']} | median {p['median_sentence_len']} | p10 {p['p10_sentence_len']} | p90 {p['p90_sentence_len']} | max {p['max_sentence_len']} words")
    L.append(f"  short (<=8 words): {p['short_sentence_share']:.0%} | long (>=30 words): {p['long_sentence_share']:.0%}")
    L.append(f"  variation (cv): {p['sentence_len_cv']} | burstiness (avg jump between neighbours / mean): {p['burstiness']}")
    L.append("PARAGRAPHS")
    L.append(f"  {p['paragraph_len_sentences']} sentences / {p['paragraph_len_words']} words on average")
    L.append("PUNCTUATION (per 1,000 words)")
    L.append("  " + " | ".join(f"{k} {v}" for k, v in p["punct_per1k"].items()))
    L.append("VOICE")
    L.append(f"  first person {p['first_person_per1k']}/1k | second person {p['second_person_per1k']}/1k | quoted speech {p['quoted_share']:.0%} of words")
    if p["language"] == "ar":
        L.append("  (Arabic: counts pronouns only - person carried by verb endings is not counted)")
    L.append("VOCABULARY TEXTURE")
    L.append(f"  avg word length {p['avg_word_len']} | type-token ratio (500-word windows) {p['ttr_500']}")
    L.append("SENTENCE OPENERS (share of sentences)")
    L.append("  " + ", ".join(f"{w} {s:.0%}" for w, s in p["top_openers"]))
    L.append("TOP CONTENT WORDS (mostly topic - do not confuse with style)")
    L.append("  " + ", ".join(f"{w} ({c})" for w, c in p["top_content_words"]))
    L.append("RECURRING PHRASES (candidate signature moves - check them in context)")
    L.append("  " + (" | ".join(f"{g} ({c})" for g, c in p["recurring_phrases"]) or "none found"))
    return "\n".join(L)


HINTS = {
    "mean_sentence_len": ("sentences run long - split or cut", "sentences run short - let some clauses extend"),
    "sentence_len_cv": ("rhythm too uneven", "rhythm too uniform - vary sentence lengths"),
    "burstiness": ("jumps between short and long are stronger than the source", "not enough short/long alternation"),
    "paragraph_len_sentences": ("paragraphs too long - break them", "paragraphs too short - merge"),
    "avg_word_len": ("vocabulary heavier than the source", "vocabulary plainer than the source"),
    "ttr_500": ("vocabulary more varied than the source", "vocabulary more repetitive than the source"),
    "quoted_share": ("more quoted speech than the source", "less quoted speech than the source"),
    "first_person_per1k": ("more 'I/we' than the source", "less 'I/we' than the source"),
    "second_person_per1k": ("addresses the reader more than the source", "addresses the reader less than the source"),
    "opener_top1_share": ("sentence openers too repetitive", "sentence openers more varied than the source"),
}


def compare(profile, draft):
    rows = []
    for k, (hi, lo) in HINTS.items():
        rows.append((k, profile.get(k, 0), draft.get(k, 0), hi, lo))
    for k in profile["punct_per1k"]:
        hi, lo = f"more {k} than the source", f"fewer {k} than the source"
        rows.append((f"{k}/1k", profile["punct_per1k"][k], draft["punct_per1k"].get(k, 0), hi, lo))
    L = [f"{'metric':<26}{'source':>10}{'draft':>10}   verdict"]
    off = 0
    for name, s, d, hi, lo in rows:
        if max(abs(s), abs(d)) < 1 and "/1k" in name or (name in ("quoted_share", "opener_top1_share") and max(s, d) < 0.03):
            ok = True
        else:
            ok = abs(d - s) <= 0.25 * max(abs(s), 1e-9)
        if ok:
            verdict = "ok"
        else:
            off += 1
            verdict = "-> " + (hi if d > s else lo)
        L.append(f"{name:<26}{s:>10}{d:>10}   {verdict}")
    L.append("")
    L.append(f"{off} of {len(rows)} metrics outside +/-25% of the source.")
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
