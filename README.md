# PersonaWriter

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white" />
  <img alt="License" src="https://img.shields.io/badge/License-MIT-green.svg" />
  <img alt="AI Writing" src="https://img.shields.io/badge/Type-AI%20Writing%20Skill-8A2BE2" />
</p>

PersonaWriter is a style-capture system for building writer personas from real text. It analyzes a sample, extracts the traits that actually define the voice, and generates a reusable writing skill that can produce new text in that same style without copying the source verbatim.

## Why this project exists

Writing style is more than a list of adjectives. It is a set of repeatable decisions: cadence, rhetorical habits, sentence structure, paragraph rhythm, diction, and the things the writer deliberately avoids. PersonaWriter turns those patterns into a structured profile so a future writing task can stay faithful to the original voice while staying original in content.

## Features

- analyzes writing samples for rhythm, sentence length, punctuation, voice, and paragraph structure
- extracts style signals rather than generic tone labels
- scaffolds a dedicated writer skill for a given persona
- compares drafts against a saved style profile to check drift
- keeps output creative and original while preserving a recognizable voice
- works with multilingual writing samples and flexible writing genres

## Quick start

1. Prepare a source text sample such as `sample.txt`.
2. Run the scaffold command:

```bash
python scripts/scaffold.py my-style-writer /tmp/out /path/to/sample.txt
```

3. Fill in the generated skill files using the project instructions.
4. Validate a draft against the profile:

```bash
python scripts/style_stats.py compare references/profile.json draft.txt
```

## Project structure

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

## Use cases

- clone your own voice into a reusable writing assistant
- build a brand voice from past content
- study a published author or essayist without copying text
- generate drafts that match a target stylistic profile for essays, articles, or narrative writing

## Notes

This project is designed for style analysis and guided writing workflows rather than production deployment. It is best used as a reusable skill-layer for AI-assisted writing and persona modeling.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
