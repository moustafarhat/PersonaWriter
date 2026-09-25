"""Tests for style_stats.py and scaffold.py. Run: python -m unittest discover tests"""
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout

SCRIPTS = os.path.join(os.path.dirname(__file__), "..", "skills", "personawriter", "scripts")
sys.path.insert(0, SCRIPTS)
import style_stats as ss  # noqa: E402


def para(text, times=4):
    return "\n\n".join([text] * times)


SAMPLES = {
    "en": para("I walked to the harbour before the town woke up. The boats were still tied to the posts, "
               "and the water had that grey calm it only keeps for an hour. You notice things at that time. "
               "A gull on a rope. A light in a window that should be dark."),
    "de": para("Ich ging zum Hafen, bevor die Stadt aufwachte. Die Boote lagen noch an den Pfählen, und das "
               "Wasser hatte diese graue Ruhe, die es nur für eine Stunde hat. Man bemerkt dann Dinge, die "
               "sonst im Lärm untergehen. Eine Möwe auf einem Seil."),
    "fr": para("Je suis allé au port avant que la ville ne se réveille. Les bateaux étaient encore attachés "
               "aux poteaux, et l'eau avait ce calme gris qu'elle ne garde qu'une heure. On remarque alors "
               "des choses que le bruit cache. Une mouette sur une corde."),
    "es": para("Fui al puerto antes de que el pueblo despertara. Los barcos seguían atados a los postes, y el "
               "agua tenía esa calma gris que solo guarda durante una hora. Uno nota entonces cosas que el "
               "ruido esconde. Una gaviota sobre una cuerda."),
    "ar": para("مشيت إلى الميناء قبل أن تستيقظ المدينة. كانت القوارب ما تزال مربوطة إلى الأعمدة، وكان الماء "
               "هادئا بذلك الهدوء الرمادي الذي لا يبقى إلا ساعة. في ذلك الوقت تلاحظ أشياء يخفيها الضجيج. "
               "نورس على حبل. ضوء في نافذة كان يجب أن تكون مظلمة."),
    "cjk": para("町が目を覚ます前に、私は港まで歩いた。船はまだ杭につながれていて、水は一時間だけの灰色の静けさを"
                "保っていた。その時間には、ふだん騒音に隠れているものに気づく。ロープの上のカモメ。暗いはずの窓の明かり。"),
    # Dutch: no built-in word lists -> "other"
    "other": para("Ik liep naar de haven voordat de stad wakker werd. De boten lagen nog vast aan de palen, en "
                  "het water had die grijze rust die het maar een uur houdt. Je ziet dan dingen die het lawaai "
                  "verbergt. Een meeuw op een touw."),
}


class LanguageDetection(unittest.TestCase):
    def test_each_language(self):
        for lang, text in SAMPLES.items():
            with self.subTest(lang=lang):
                self.assertEqual(ss.analyze_text(text)["language"], lang)

    def test_unknown_language_skips_person_counts(self):
        p = ss.analyze_text(SAMPLES["other"])
        self.assertIsNone(p["first_person_per1k"])
        self.assertIn("person counts", ss.report(p))

    def test_cjk_counts_characters(self):
        p = ss.analyze_text(SAMPLES["cjk"])
        self.assertEqual(p["unit"], "characters")
        self.assertEqual(p["sentences"], 5 * 4)


class SentenceSplitting(unittest.TestCase):
    def test_abbreviations_do_not_split(self):
        self.assertEqual(len(ss.split_sentences("Dr. Smith arrived at noon. He sat down, e.g. near the door.")), 2)
        self.assertEqual(len(ss.split_sentences("Das gilt z.B. für Hunde. Katzen sind anders.")), 2)
        self.assertEqual(len(ss.split_sentences("J. K. Rowling wrote it. Then she rested.")), 2)

    def test_lowercase_follow_on_is_not_a_new_sentence(self):
        self.assertEqual(len(ss.split_sentences("It cost approx. ten dollars. Fine.")), 2)

    def test_line_breaks_always_split(self):
        self.assertEqual(len(ss.split_sentences("A heading etc.\nThe body starts here.")), 2)

    def test_arabic_and_cjk_marks(self):
        self.assertEqual(len(ss.split_sentences("هل أتيت؟ نعم أتيت.")), 2)
        self.assertEqual(len(ss.split_sentences("今日は晴れです。明日は雨です！")), 2)


class Metrics(unittest.TestCase):
    def test_too_short_is_rejected(self):
        with self.assertRaises(SystemExit):
            ss.analyze_text("Too short.")

    def test_first_person_detected(self):
        self.assertGreater(ss.analyze_text(SAMPLES["en"])["first_person_per1k"], 0)
        self.assertGreater(ss.analyze_text(SAMPLES["fr"])["first_person_per1k"], 0)

    def test_compare_with_itself_is_clean(self):
        for lang, text in SAMPLES.items():
            with self.subTest(lang=lang):
                p = ss.analyze_text(text)
                self.assertIn("0 of", ss.compare(p, p))

    def test_compare_flags_drift(self):
        src = ss.analyze_text(SAMPLES["en"])
        draft = ss.analyze_text(para("This sentence is deliberately long and keeps going with clause after clause "
                                     "and comma after comma, because it wants to drift far away from the short "
                                     "clipped rhythm of the source text, and it never really stops to breathe at all, "
                                     "does it, no, it simply goes on and on until the paragraph finally ends.", 3))
        self.assertIn("sentences run long", ss.compare(src, draft))

    def test_compare_accepts_old_profiles_without_new_fields(self):
        p = ss.analyze_text(SAMPLES["en"])
        old = {k: v for k, v in p.items() if k != "unit"}
        ss.compare(old, p)


class Scaffold(unittest.TestCase):
    def test_scaffold_creates_skill_and_keeps_previous_profile(self):
        with tempfile.TemporaryDirectory() as tmp:
            sample = os.path.join(tmp, "sample.txt")
            with open(sample, "w", encoding="utf-8") as f:
                f.write(SAMPLES["ar"])
            cmd = [sys.executable, os.path.join(SCRIPTS, "scaffold.py"), "test-writer", tmp, sample]
            for _ in range(2):
                subprocess.run(cmd, check=True, capture_output=True)
            root = os.path.join(tmp, "test-writer")
            with open(os.path.join(root, "references", "profile.json"), encoding="utf-8") as f:
                self.assertEqual(json.load(f)["language"], "ar")
            self.assertTrue(os.path.exists(os.path.join(root, "references", "profile.previous.json")))
            self.assertTrue(os.path.exists(os.path.join(root, "scripts", "style_stats.py")))

    def test_bad_slug_is_rejected(self):
        r = subprocess.run([sys.executable, os.path.join(SCRIPTS, "scaffold.py"), "Bad Slug", ".", "x.txt"],
                           capture_output=True)
        self.assertNotEqual(r.returncode, 0)


class Cli(unittest.TestCase):
    def test_analyze_cli_writes_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            sample, out = os.path.join(tmp, "s.txt"), os.path.join(tmp, "p.json")
            with open(sample, "w", encoding="utf-8") as f:
                f.write(SAMPLES["de"])
            sys.argv = ["style_stats.py", "analyze", sample, "--json", out]
            with redirect_stdout(io.StringIO()):
                ss.main()
            with open(out, encoding="utf-8") as f:
                self.assertEqual(json.load(f)["language"], "de")


if __name__ == "__main__":
    unittest.main()
