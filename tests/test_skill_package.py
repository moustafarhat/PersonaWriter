"""Checks that the skill stays installable. Run: python -m unittest discover tests"""
import json
import os
import re
import shutil
import tempfile
import unittest
import zipfile

ROOT = os.path.join(os.path.dirname(__file__), "..")
SKILLS = os.path.join(ROOT, "skills")


def read(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def frontmatter(skill_md):
    m = re.match(r"---\n(.*?)\n---\n", skill_md.replace("\r\n", "\n"), re.S)
    if not m:
        raise AssertionError("SKILL.md must start with a --- frontmatter block ---")
    return dict(re.findall(r"^(\w[\w-]*):\s*(.*)$", m.group(1), re.M))


class SkillFormat(unittest.TestCase):
    def test_every_skill_has_valid_frontmatter(self):
        names = os.listdir(SKILLS)
        self.assertTrue(names)
        for folder in names:
            with self.subTest(skill=folder):
                fm = frontmatter(read("skills", folder, "SKILL.md"))
                self.assertEqual(fm.get("name"), folder, "name must match the folder name")
                self.assertRegex(fm["name"], r"^[a-z0-9]+(-[a-z0-9]+)*$")
                self.assertLessEqual(len(fm["name"]), 64)
                self.assertTrue(fm.get("description"), "description is required")
                self.assertLessEqual(len(fm["description"]), 1024, "description over 1024 characters")

    def test_referenced_files_exist(self):
        for folder in os.listdir(SKILLS):
            text = read("skills", folder, "SKILL.md")
            for path in set(re.findall(r"`((?:references|scripts)/[\w./-]+\.\w+)`", text)):
                if path.startswith("references/profile") or path.startswith("references/style-guide") \
                        or path.startswith("references/anchors"):
                    continue  # files of the *generated* skill, not this one
                with self.subTest(skill=folder, path=path):
                    self.assertTrue(os.path.exists(os.path.join(SKILLS, folder, path)), f"{path} is missing")


class PluginManifests(unittest.TestCase):
    def test_versions_and_names_match(self):
        plugin = json.loads(read(".claude-plugin", "plugin.json"))
        market = json.loads(read(".claude-plugin", "marketplace.json"))
        entry = next(p for p in market["plugins"] if p["name"] == plugin["name"])
        self.assertEqual(entry["version"], plugin["version"], "bump both manifests together")
        self.assertIn(f"## {plugin['version']}", read("CHANGELOG.md"), "CHANGELOG has no entry for this version")


class ReleaseZip(unittest.TestCase):
    def test_zip_has_skill_folder_at_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            archive = shutil.make_archive(os.path.join(tmp, "personawriter"), "zip", SKILLS, "personawriter")
            with zipfile.ZipFile(archive) as z:
                names = [n.replace("\\", "/") for n in z.namelist()]
        self.assertIn("personawriter/SKILL.md", names)
        self.assertTrue(all(n.startswith("personawriter/") for n in names))


if __name__ == "__main__":
    unittest.main()
