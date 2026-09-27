# Changelog

## 1.2.0

- Merges the Style Forge line of work into PersonaWriter, so PersonaWriter is the one current version.
- `style_stats.py compare` now prints a 0-100 similarity score and the three most important fixes,
  and exits with 1 below 70. Per-metric tolerances and noise floors from 1.1 are kept.
- New `style_stats.py check`: counts signature-move dosage and never-list hits defined in the
  generated skill's `references/markers.json` (Arabic matched through diacritics and alef/ya variants).
- New `style_stats.py overlap`: finds passages copied verbatim from the source or anchors
  (Chinese/Japanese measured in characters).
- `--json` output for `compare`, `check` and `overlap`.
- Text cleaning before measuring: Markdown, code, HTML, URLs and front matter are removed, and
  hard-wrapped PDF/e-book text is re-joined into paragraphs.
- New `validate.py` (quality gate for a generated skill, including a copy check against the
  source) and `package.py` (validates and zips a skill into a `.skill` file).
- `scaffold.py` writes a starter `markers.json` (never overwritten on re-runs), checks that the
  samples exist, and requires an ASCII slug of at most 64 characters, as skill names must be.
- New **Profile only** mode; Update mode also refreshes markers and anchors and works on style
  skills built elsewhere.
- Generated skills get `markers.json`, the three-step drift check, and a "Rewriting a draft" section.
- Releases publish automatically: when `main` carries a version without a release, the workflow
  tests, tags and publishes `personawriter.zip`. No manual tags.
- SKILL.md: intake strips non-author material, one voice per skill, a manual path when code
  cannot run, a 70+ score target in the proving step, and a "drift watch-list" in the guide.

## 1.1.0

- **Quick mode:** "write X like this" now produces the text right away and offers to save the
  voice as a skill afterwards. **Update mode:** refine an existing style skill with new samples.
- Works outside claude.ai: no hard-coded sandbox paths, and packaging falls back to a plain zip.
- Clearer guardrails on impersonation and deceptive use.
- `style_stats.py`: French, Spanish, Portuguese and Italian word lists; an `other` fallback
  instead of wrongly using English lists; Chinese/Japanese measured in characters;
  abbreviation-aware sentence splitting (`Dr.`, `e.g.`, `z.B.`, initials); per-metric tolerances
  in `compare`; UTF-8 output on Windows consoles.
- `scaffold.py` keeps the old profile as `profile.previous.json` when re-run.
- Repository restructured as a Claude Code plugin (`skills/personawriter/`, `.claude-plugin/`),
  with tests, CI, and a release workflow that publishes an installable zip.

## 1.0.0

- Initial release.
