# PersonaWriter

PersonaWriter is a Claude-style skill that turns a writing sample into a reusable style profile and a dedicated writing skill. The project captures rhythm, syntax, structure, diction, and recurring habits from a source text, then helps generate new text that feels like that voice without copying the source verbatim.

## What this project does

- analyzes a sample text and turns it into measurable style signals
- records the load-bearing traits, never-list, and dosage rules
- scaffolds a new writer skill for a given style
- compares a draft against the saved profile to catch drift
- keeps the output original while preserving the target voice

## Repository structure

```text
.
├── SKILL.md
├── README.md
├── .gitignore
├── LICENSE
├── references/
│   ├── generated-skill-template.md
│   ├── style-dimensions.md
│   └── ...
├── scripts/
│   ├── scaffold.py
│   └── style_stats.py
└── .git/
```

## Quick start

1. Prepare a sample text file such as `sample.txt`.
2. Run the scaffold command:

```bash
python scripts/scaffold.py my-style-writer /tmp/out /path/to/sample.txt
```

3. Fill in the generated skill files using the instructions in the skill itself.
4. Validate the output with:

```bash
python scripts/style_stats.py compare references/profile.json draft.txt
```

## Notes

This project is designed for style analysis and guided writing, not for direct production deployment. It is best used as a reusable writing assistant pattern for content generation workflows.
