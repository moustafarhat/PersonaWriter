"""Tests for cleaning, scoring, markers, copy checks, validate.py and package.py.
Run: python -m unittest discover tests"""
import io
import json
import os
import subprocess
import sys
import tempfile
import textwrap
import unittest
import zipfile
from contextlib import redirect_stdout

HERE = os.path.dirname(__file__)
SCRIPTS = os.path.join(HERE, "..", "skills", "personawriter", "scripts")
sys.path.insert(0, SCRIPTS)
import style_stats as ss  # noqa: E402
import validate  # noqa: E402

SAMPLE = os.path.join(HERE, "fixtures", "sample_en.txt")
with open(SAMPLE, encoding="utf-8") as f:
    TEXT = f.read()


class Cleaning(unittest.TestCase):
    def test_hard_wrapped_text_gives_the_same_sentences(self):
        prof = ss.analyze_text(TEXT)
        wrapped = "\n\n".join(textwrap.fill(p, 70) for p in TEXT.split("\n\n"))
        self.assertEqual(ss.analyze_text(wrapped)["sentences"], prof["sentences"])

    def test_markdown_code_and_urls_are_ignored(self):
        md = "# Heading\n\n```\ncode block\n```\n\nSee https://example.com and `x()`.\n\n" + TEXT
        self.assertLessEqual(abs(ss.analyze_text(md)["words"] - ss.analyze_text(TEXT)["words"]), 4)


class Score(unittest.TestCase):
    def test_identical_profile_scores_100(self):
        prof = ss.analyze_text(TEXT)
        res = ss.compare_data(prof, prof)
        self.assertEqual(res["score"], 100)
        self.assertEqual(res["top_fixes"], [])

    def test_flat_uniform_draft_scores_below_70(self):
        prof = ss.analyze_text(TEXT)
        flat = ss.analyze_text(" ".join(["The system processes the request and returns the result to the user."] * 12))
        res = ss.compare_data(prof, flat)
        self.assertLess(res["score"], 70)
        self.assertTrue(res["top_fixes"])

    def test_compare_cli_exit_code_follows_score(self):
        with tempfile.TemporaryDirectory() as tmp:
            prof, same = os.path.join(tmp, "p.json"), os.path.join(tmp, "d.txt")
            with open(prof, "w", encoding="utf-8") as f:
                json.dump(ss.analyze_text(TEXT), f)
            with open(same, "w", encoding="utf-8") as f:
                f.write(TEXT)
            r = subprocess.run([sys.executable, os.path.join(SCRIPTS, "style_stats.py"), "compare", prof, same],
                               capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(r.returncode, 0)
            self.assertIn("Similarity score: 100/100", r.stdout)


class Markers(unittest.TestCase):
    MARKERS = {"dosage": [{"name": "belief pivot", "patterns": [r"\bhere is what i believe\b"], "per1k": [1, 5]}],
               "never": [{"name": "exclamation", "pattern": "!"},
                         {"name": "non-space run", "pattern": r"\S{40,}"}]}

    def test_never_list_violation_found(self):
        res = ss.check_data(self.MARKERS, "Here is what I believe! " * 30)
        names = [v["name"] for v in res["never"]]
        self.assertIn("exclamation", names)
        self.assertNotIn("non-space run", names, "regex escapes like \\S must not be case-folded")

    def test_arabic_patterns_match_through_diacritics(self):
        res = ss.check_data({"never": [{"name": "khitam", "pattern": "في الختام"}]}, "وفي الختامِ نقول شيئًا.")
        self.assertTrue(res["never"])

    def test_dosage_out_of_range_is_a_problem(self):
        res = ss.check_data(self.MARKERS, "A quiet sentence without the move. " * 60)
        self.assertEqual(res["dosage"][0]["status"], "too few")
        self.assertGreater(res["problems"], 0)


class Overlap(unittest.TestCase):
    def test_copied_run_found_and_merged(self):
        ov = ss.overlap_data("Yesterday she had kept it of course she had and left.", [TEXT], n=6)
        self.assertEqual(ov["shared_sequences"], ["she had kept it of course she had"])

    def test_original_text_passes(self):
        self.assertFalse(ss.overlap_data("An entirely new sentence about trains and weather.", [TEXT])["shared_sequences"])

    def test_cjk_counts_characters(self):
        src = "町が目を覚ます前に、私は港まで歩いた。船はまだ杭につながれていた。"
        self.assertTrue(ss.overlap_data("昨日、町が目を覚ます前に、私は港まで歩いた。", [src])["shared_sequences"])
        self.assertFalse(ss.overlap_data("昨日は町が静かだった。", [src])["shared_sequences"])


GOOD_SKILL = {
    "SKILL.md": "---\nname: test-voice-writer\ndescription: Writes short personal essays in a calm, "
                "observant first-person voice built from small objects and plain sentences. Use whenever "
                "the user asks for an essay, column or post in this style, or wants a draft rewritten in this voice.\n"
                "---\n\n# Test Voice Writer\n\nCalm and observant.\n",
    "references/style-guide.md": "# Style guide\n\n## 1. Load-bearing traits\nSentences run 6-18 words.\n\n"
                                 "## 8. Never-list\n- no exclamation marks\n\n## 9. Dosage\nOne pivot per 500 words.\n",
    "references/anchors.md": "# Anchors\n\n1. \"I bought the kettle on a Tuesday.\" - flat opener\n"
                             "2. \"He wrapped it in newspaper.\" - short beat\n"
                             "3. \"I did not ask him to.\" - short beat\n",
    "references/markers.json": json.dumps({"dosage": [{"name": "pivot", "patterns": ["here is what i"], "per1k": [0, 3]}],
                                           "never": [{"name": "exclamation", "pattern": "!"}]}),
}


class ValidateAndPackage(unittest.TestCase):
    def scaffold(self, tmp):
        r = subprocess.run([sys.executable, os.path.join(SCRIPTS, "scaffold.py"), "test-voice-writer", tmp, SAMPLE],
                           capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(r.returncode, 0, r.stderr)
        return os.path.join(tmp, "test-voice-writer")

    def write(self, root, files):
        for rel, content in files.items():
            with open(os.path.join(root, rel), "w", encoding="utf-8") as f:
                f.write(content)

    def test_scaffold_writes_starter_markers_and_keeps_filled_ones(self):
        with tempfile.TemporaryDirectory() as tmp:
            sk = self.scaffold(tmp)
            path = os.path.join(sk, "references", "markers.json")
            with open(path, encoding="utf-8") as f:
                self.assertEqual(json.load(f)["dosage"], [])
            self.write(sk, {"references/markers.json": GOOD_SKILL["references/markers.json"]})
            self.scaffold(tmp)  # update mode must not wipe the user's markers
            with open(path, encoding="utf-8") as f:
                self.assertTrue(json.load(f)["dosage"])

    def test_incomplete_skill_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            must, _ = validate.validate(self.scaffold(tmp))
            self.assertTrue(any("SKILL.md" in m for m in must))

    def test_leftover_placeholders_are_caught(self):
        with tempfile.TemporaryDirectory() as tmp:
            sk = self.scaffold(tmp)
            self.write(sk, dict(GOOD_SKILL, **{"SKILL.md": "---\nname: test-voice-writer\n"
                                               "description: Writes <genres> in this voice.\n---\n# X\n"}))
            must, _ = validate.validate(sk)
            self.assertTrue(any("placeholder" in m or "angle" in m for m in must))

    def test_complete_skill_passes_validates_crlf_and_packages(self):
        with tempfile.TemporaryDirectory() as tmp:
            sk = self.scaffold(tmp)
            crlf = {k: v.replace("\n", "\r\n") if k.endswith(".md") else v for k, v in GOOD_SKILL.items()}
            self.write(sk, crlf)
            must, _ = validate.validate(sk, [SAMPLE])
            self.assertEqual(must, [])
            out = os.path.join(tmp, "dist")
            r = subprocess.run([sys.executable, os.path.join(SCRIPTS, "package.py"), sk, out],
                               capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            with zipfile.ZipFile(os.path.join(out, "test-voice-writer.skill")) as z:
                names = [n.replace("\\", "/") for n in z.namelist()]
            self.assertIn("test-voice-writer/SKILL.md", names)
            self.assertIn("test-voice-writer/scripts/style_stats.py", names)

    def test_copied_passage_in_style_guide_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            sk = self.scaffold(tmp)
            copied = " ".join(TEXT.split()[:30])
            self.write(sk, dict(GOOD_SKILL, **{"references/style-guide.md":
                                               GOOD_SKILL["references/style-guide.md"] + "\n" + copied + "\n"}))
            must, _ = validate.validate(sk, [SAMPLE])
            self.assertTrue(any("reproduces" in m for m in must))


class CheckCli(unittest.TestCase):
    def test_check_cli_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            markers, draft = os.path.join(tmp, "m.json"), os.path.join(tmp, "d.txt")
            with open(markers, "w", encoding="utf-8") as f:
                json.dump({"never": [{"name": "exclamation", "pattern": "!"}]}, f)
            with open(draft, "w", encoding="utf-8") as f:
                f.write("Wow! " * 10)
            sys.argv = ["style_stats.py", "check", markers, draft, "--json"]
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = ss.main()
            self.assertEqual(code, 1)
            self.assertEqual(json.loads(buf.getvalue())["never"][0]["count"], 10)


if __name__ == "__main__":
    unittest.main()
