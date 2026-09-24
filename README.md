# PersonaWriter

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white" />
  <img alt="License" src="https://img.shields.io/badge/License-MIT-green.svg" />
  <img alt="AI Writing" src="https://img.shields.io/badge/Type-AI%20Writing%20Skill-8A2BE2" />
</p>

A style-capture system for turning a writing sample into a reusable writer persona.

PersonaWriter reads a text, measures the patterns that actually define its voice, and produces a dedicated writing skill that can generate new content in that same style without copying the source.

## Overview

Most writing styles are not just adjectives like "warm" or "formal." They are repeatable decisions about rhythm, structure, paragraph flow, rhetorical habits, punctuation, diction, and what the writer deliberately avoids.

PersonaWriter is built around that idea. It helps you:

- analyze a sample text for voice and rhythm
- isolate the traits that matter most
- store them as a reusable style profile
- generate a dedicated skill that writes in that persona
- validate draft output against the original style signals

## How it works

1. Feed in a source text or article sample.
2. Measure sentence rhythm, paragraph shape, punctuation habits, and recurring patterns.
3. Extract the style guide: load-bearing traits, never-list, and dosage rules.
4. Scaffold a writer skill that follows the learned voice.
5. Compare new drafts to the stored profile to catch drift and keep the style consistent.

## Example workflow

```bash
python scripts/scaffold.py my-style-writer /tmp/out /path/to/sample.txt
python scripts/style_stats.py compare references/profile.json draft.txt
```

This gives you a generated persona-style writer folder that can then be refined with a style guide, anchors, and writing instructions.

## Features

- sentence and paragraph rhythm analysis
- punctuation and stylistic drift checking
- recurring phrase and vocabulary tracking
- persona-style writer scaffolding
- multilingual text support
- reusable writing skill generation

## Use cases

- preserve your own writing voice as a reusable skill
- build a brand voice from prior articles or posts
- imitate a style for study or creative adaptation without copying source text
- generate new drafts for essays, articles, or narrative writing using a known persona

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

## Notes

This project is designed for style analysis and guided writing workflows rather than production deployment. It is best used as a reusable tool for AI-assisted writing, persona modeling, and creative drafting.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
