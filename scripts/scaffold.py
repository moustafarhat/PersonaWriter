#!/usr/bin/env python3
"""scaffold.py - create the folder for a new style skill and measure the source.

Usage:
  python scaffold.py SLUG OUTDIR SAMPLE [SAMPLE ...]

Creates OUTDIR/SLUG/ containing references/profile.json (metrics measured from
the samples) and scripts/style_stats.py (copied so the finished skill is
self-contained). Claude then writes SKILL.md, references/style-guide.md and
references/anchors.md following references/generated-skill-template.md.
"""
import json
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import style_stats  # noqa: E402


def main():
    if len(sys.argv) < 4:
        raise SystemExit(__doc__)
    slug, outdir, samples = sys.argv[1], sys.argv[2], sys.argv[3:]
    if not re.fullmatch(r"[a-z0-9\u0600-\u06FF]+(?:-[a-z0-9\u0600-\u06FF]+)*", slug):
        raise SystemExit("SLUG must be lowercase letters/digits separated by hyphens, e.g. warm-essayist-writer")

    root = os.path.join(outdir, slug)
    os.makedirs(os.path.join(root, "references"), exist_ok=True)
    os.makedirs(os.path.join(root, "scripts"), exist_ok=True)
    shutil.copy(os.path.join(HERE, "style_stats.py"), os.path.join(root, "scripts", "style_stats.py"))

    profile = style_stats.analyze_text(style_stats.read_files(samples))
    with open(os.path.join(root, "references", "profile.json"), "w", encoding="utf-8") as f:
        json.dump(profile, f, ensure_ascii=False, indent=2)

    print(style_stats.report(profile))
    print(f"\nScaffold ready: {root}")
    print("Next: write SKILL.md, references/style-guide.md, references/anchors.md")


if __name__ == "__main__":
    main()
