# Changelog

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
