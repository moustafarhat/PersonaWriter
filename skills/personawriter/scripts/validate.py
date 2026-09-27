#!/usr/bin/env python3
"""validate.py - quality gate for a generated style skill.

Usage:
  python validate.py SKILL_DIR [--source SAMPLE ...]

Checks structure, frontmatter, leftover template placeholders, required style-guide
sections, anchor size, markers.json syntax, and (with --source) that the skill files
do not reproduce long passages of the source.
Exit code: 0 = ready to package, 1 = must fix, 2 = usage error.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import style_stats  # noqa: E402

REQUIRED = ["SKILL.md", "references/style-guide.md", "references/anchors.md",
            "references/profile.json", "references/markers.json", "scripts/style_stats.py"]
GUIDE_SECTIONS = {  # section -> accepted heading keywords (any language the guide was written in)
    "load-bearing traits": ["load-bearing"],
    "never-list": ["never"],
    "dosage": ["dosage", "dosierung", "dosis", "dosaggio", "الجرعة"],
}


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read().replace("\r\n", "\n")


def frontmatter(text):
    m = re.match(r"\A---\n(.*?)\n---\n", text, re.S)
    if not m:
        return None
    fm = {}
    for line in m.group(1).splitlines():
        if ":" in line and not line.startswith(" "):
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip().strip('"').strip("'")
    return fm


def validate(root, sources=()):
    must, warn = [], []
    for rel in REQUIRED:
        if not os.path.isfile(os.path.join(root, rel)):
            must.append(f"missing file: {rel}")
    have = lambda rel: os.path.isfile(os.path.join(root, rel))
    if not have("SKILL.md"):
        return must, warn

    skill = read(os.path.join(root, "SKILL.md"))
    fm = frontmatter(skill)
    if not fm:
        must.append("SKILL.md has no YAML frontmatter")
    else:
        name, desc = fm.get("name", ""), fm.get("description", "")
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name) or len(name) > 64:
            must.append(f"frontmatter name must be lowercase-hyphenated, <=64 chars: '{name}'")
        if name != os.path.basename(os.path.normpath(root)):
            warn.append(f"folder name '{os.path.basename(os.path.normpath(root))}' differs from skill name '{name}'")
        if not desc:
            must.append("frontmatter description is empty")
        elif len(desc) > 1024:
            must.append(f"description is {len(desc)} chars (max 1024)")
        elif len(desc) < 150:
            warn.append("description is short: name genres and the phrasings users will say, so it triggers")
        if "<" in desc or ">" in desc:
            must.append("description contains angle brackets (template placeholder left?)")
    n_lines = skill.count("\n")
    if n_lines > 150:
        warn.append(f"SKILL.md is {n_lines} lines; keep it under ~100 and move detail to the style guide")

    for rel in ("SKILL.md", "references/style-guide.md", "references/anchors.md"):
        if not have(rel):
            continue
        left = re.findall(r"<(?:[a-z][^<>\n]{2,60})>", read(os.path.join(root, rel)))
        left = [x for x in left if not re.match(r"</?(?:br|b|i|em|strong|code|p)>", x)]
        if left:
            must.append(f"{rel}: unfilled placeholders {left[:3]}")

    if not all(have(r) for r in REQUIRED):
        return must, warn
    guide = read(os.path.join(root, "references/style-guide.md")).lower()
    heads = " ".join(re.findall(r"^#{1,3}\s+(.+)$", guide, re.M))
    for sec, keys in GUIDE_SECTIONS.items():
        if not any(k in heads for k in keys):
            must.append(f"style-guide.md lacks a '{sec}' section")
    if not re.search(r"\b\d+\s*(?:-|–|to|bis|à|a|إلى)\s*\d+\b", guide):
        warn.append("style-guide.md has no numeric ranges; quantify rhythm from profile.json")

    anchors = [l for l in read(os.path.join(root, "references/anchors.md")).splitlines()
               if re.match(r"^\s*\d+[.)]\s", l)]
    if not 3 <= len(anchors) <= 12:
        warn.append(f"{len(anchors)} anchors; aim for 5-10")
    quoted = 0
    for a in anchors:
        q = re.findall(r"[\"“«„](.+?)[\"”»“]", a)
        words = sum(len(style_stats.WORD.findall(x)) for x in q)
        quoted += words
        if words > 45:
            must.append(f"anchor too long ({words} words): {a[:60]}...")
    if quoted > 350:
        must.append(f"anchors quote {quoted} words in total; keep it under ~350")

    try:
        markers = json.loads(read(os.path.join(root, "references/markers.json")))
        for d in markers.get("dosage", []):
            for p in d["patterns"]:
                re.compile(p)
            lo, hi = d["per1k"]
            if lo > hi:
                must.append(f"markers.json: dosage '{d['name']}' has min > max")
        for v in markers.get("never", []):
            re.compile(v["pattern"])
        if not markers.get("dosage"):
            warn.append("markers.json has no dosage entries")
        if not markers.get("never"):
            warn.append("markers.json has no never-list entries")
    except (ValueError, KeyError, TypeError, re.error) as e:
        must.append(f"markers.json invalid: {e}")

    try:
        prof = json.loads(read(os.path.join(root, "references/profile.json")))
        if prof.get("words", 0) < 1000:
            warn.append(f"profile based on {prof.get('words')} words: mark the style as provisional")
    except ValueError as e:
        must.append(f"profile.json invalid: {e}")

    if sources:
        src = [read(s) for s in sources]
        for rel in ("SKILL.md", "references/style-guide.md"):
            ov = style_stats.overlap_data(read(os.path.join(root, rel)), src, n=12)
            if ov["shared_sequences"]:
                must.append(f"{rel} reproduces {len(ov['shared_sequences'])} passage(s) of 12+ words from the source")
    return must, warn


def main():
    ap = argparse.ArgumentParser(description="Validate a generated style skill.")
    ap.add_argument("skill_dir")
    ap.add_argument("--source", nargs="*", default=[])
    a = ap.parse_args()
    if not os.path.isdir(a.skill_dir):
        print(f"error: not a folder: {a.skill_dir}", file=sys.stderr)
        return 2
    must, warn = validate(a.skill_dir, a.source)
    print(f"VALIDATION: {'PASS' if not must else 'FAIL'}")
    for m in must:
        print(f"  must fix: {m}")
    for w in warn:
        print(f"  warning:  {w}")
    return 1 if must else 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
