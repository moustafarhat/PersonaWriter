#!/usr/bin/env python3
"""package.py - zip a skill folder into an installable .skill file.

Usage:
  python package.py SKILL_DIR OUTPUT_DIR

Runs validate.py first and refuses to package a skill that fails it.
Skips caches, drafts and hidden files. Prints the path of the .skill file.
"""
import os
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import validate  # noqa: E402

SKIP_DIRS = {"__pycache__", ".git", "drafts"}
SKIP_FILES = {".DS_Store"}


def main():
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    root, outdir = os.path.normpath(sys.argv[1]), sys.argv[2]
    must, warn = validate.validate(root)
    for w in warn:
        print(f"warning: {w}")
    if must:
        for m in must:
            print(f"must fix: {m}")
        raise SystemExit("Not packaged: fix the problems above first.")
    name = os.path.basename(root)
    os.makedirs(outdir, exist_ok=True)
    out = os.path.join(outdir, f"{name}.skill")
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for dirpath, dirs, files in os.walk(root):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")]
            for f in files:
                if f in SKIP_FILES or f.startswith(".") or f.endswith(".pyc"):
                    continue
                full = os.path.join(dirpath, f)
                z.write(full, os.path.join(name, os.path.relpath(full, root)))
    print(out)


if __name__ == "__main__":
    main()
