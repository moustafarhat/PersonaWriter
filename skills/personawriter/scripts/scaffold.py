#!/usr/bin/env python3
"""scaffold.py - create the folder for a new style skill and measure the source.

Usage:
  python scaffold.py SLUG OUTDIR SAMPLE [SAMPLE ...]

Creates OUTDIR/SLUG/ containing references/profile.json (metrics measured from
the samples), a starter references/markers.json, and scripts/style_stats.py
(copied so the finished skill is self-contained). Re-running on an existing
folder (update mode) keeps the old profile as references/profile.previous.json
and never overwrites markers.json. Claude then writes SKILL.md,
references/style-guide.md, references/anchors.md and fills markers.json,
following references/generated-skill-template.md.
"""
import json
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import style_stats  # noqa: E402

STARTER_MARKERS = {
    "_help": "Fill from the style guide. dosage: regexes counting a signature move, with the target "
             "rate per 1,000 words measured on the sample. never: regexes for never-list items. "
             "Patterns match normalised text (lowercase, no Arabic diacritics, unified alef/ya).",
    "dosage": [],
    "never": [],
}


def main():
    if hasattr(sys.stdout, "reconfigure"):  # Windows consoles default to a legacy code page
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if len(sys.argv) < 4:
        raise SystemExit(__doc__)
    slug, outdir, samples = sys.argv[1], sys.argv[2], sys.argv[3:]
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug) or len(slug) > 64:
        raise SystemExit("SLUG must be lowercase a-z/0-9 words joined by hyphens (max 64 chars), "
                         "e.g. warm-essayist-writer. Transliterate non-Latin names.")
    for sample in samples:
        if not os.path.isfile(sample):
            raise SystemExit(f"Sample not found: {sample}")

    root = os.path.join(outdir, slug)
    os.makedirs(os.path.join(root, "references"), exist_ok=True)
    os.makedirs(os.path.join(root, "scripts"), exist_ok=True)
    shutil.copy(os.path.join(HERE, "style_stats.py"), os.path.join(root, "scripts", "style_stats.py"))

    profile = style_stats.analyze_text(style_stats.read_files(samples))
    profile_path = os.path.join(root, "references", "profile.json")
    if os.path.exists(profile_path):  # update mode: keep the old numbers for comparison
        shutil.copy(profile_path, os.path.join(root, "references", "profile.previous.json"))
        print("Existing profile kept as references/profile.previous.json\n")
    with open(profile_path, "w", encoding="utf-8") as f:
        json.dump(profile, f, ensure_ascii=False, indent=2)
    markers_path = os.path.join(root, "references", "markers.json")
    if not os.path.exists(markers_path):
        with open(markers_path, "w", encoding="utf-8") as f:
            json.dump(STARTER_MARKERS, f, ensure_ascii=False, indent=2)

    print(style_stats.report(profile))
    print(f"\nScaffold ready: {root}")
    print("Next: write SKILL.md, references/style-guide.md, references/anchors.md, fill references/markers.json")


if __name__ == "__main__":
    main()
