# Contributing to PersonaWriter

Thanks for helping. The most useful contributions, roughly in order:

1. **Failure reports.** A style that came out as a caricature, a generic voice, or with the
   source's topic leaking in. Include a short sample (or a description if it is private), what you
   asked for, and what felt wrong. These drive most improvements to `SKILL.md`.
2. **New languages.** See below. Usually a small PR.
3. **Example skills** built from **public-domain** texts (e.g. authors who died more than 70 years
   ago), placed in `examples/<slug>-writer/`, with the two test drafts included.
4. **Skills and outputs you built.** Add a row to the "Built with PersonaWriter? Share it" table
   in the README, linking to your skill's own repo and one example output with its
   `compare` / `check` / `overlap` results. Outputs written with an existing skill go to that
   skill's examples, e.g. the Arabic skill's
   [Share your essays](https://github.com/moustafarhat/arabic-critic-essay-writer#share-your-essays) guide.
5. Fixes to the scripts, docs and translations of the README.

## Adding a language

In `skills/personawriter/scripts/style_stats.py`:

1. Add ~60 of the most common function words to `STOP["xx"]`.
2. Add first- and second-person pronouns to `FIRST["xx"]` and `SECOND["xx"]`.
3. Add abbreviations that end with a period (e.g. `bzw`, `p.ex`) to `ABBREV` if the language has them.
4. Add any language-specific punctuation to `PUNCT` (like `؟` or `。`).
5. Add a sample paragraph to `SAMPLES` in `tests/test_style_stats.py` so detection is tested.
6. Optionally add close-reading notes to `skills/personawriter/references/style-dimensions.md`
   (register, address forms, punctuation conventions).

Run the tests:

```bash
python -m unittest discover tests -v
```

## Guidelines

- Scripts use the Python standard library only (3.9+). No dependencies.
- Keep `SKILL.md` lean. Detail belongs in `references/`.
- Changes to the skill's instructions should say *which failure they fix*. Ideally show a
  before/after draft.
- Never commit copyrighted sample texts. Use your own writing or public-domain material.

## Releasing (maintainers)

Bump `version` in `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` and add a
`## <version>` section to `CHANGELOG.md` (the tests check all three agree). When that reaches
`main`, the release workflow sees a version without a release, runs the tests, creates the
`v<version>` tag and publishes a GitHub Release with `personawriter.zip` and the changelog
section as notes. No manual tagging. Pushes that don't change the version do nothing.
