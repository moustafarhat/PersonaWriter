<h1 align="center">PersonaWriter</h1>

<p align="center">
  <b>Give it a few pages of writing. Get back a skill that writes like that.</b><br/>
  Your own voice, your brand's voice, or the manner of a writer you admire, captured as a reusable Claude skill.
</p>

<p align="center">
  <a href="https://github.com/moustafarhat/PersonaWriter/actions/workflows/tests.yml"><img alt="tests" src="https://github.com/moustafarhat/PersonaWriter/actions/workflows/tests.yml/badge.svg" /></a>
  <a href="https://github.com/moustafarhat/PersonaWriter/releases/latest"><img alt="release" src="https://img.shields.io/github/v/release/moustafarhat/PersonaWriter?label=download" /></a>
  <img alt="Agent Skill" src="https://img.shields.io/badge/Agent%20Skill-SKILL.md-8A2BE2" />
  <img alt="Languages" src="https://img.shields.io/badge/languages-EN%20·%20DE%20·%20AR%20·%20FR%20·%20ES%20·%20more-0A7" />
  <img alt="License" src="https://img.shields.io/badge/License-MIT-green.svg" />
</p>

<p align="center">
  <a href="#install">Install</a> ·
  <a href="#use-it">Use it</a> ·
  <a href="#why-it-works">Why it works</a> ·
  <a href="#languages">Languages</a> ·
  <a href="#ethics--fair-use">Ethics</a>
</p>

---

Ask an AI to "write like this" and you usually get a costume: neutral prose with a few
borrowed phrases sprinkled on top. PersonaWriter does something different. It **measures** the
sample, **reads** it the way an editor would, and writes down the *decisions* that make the voice
recognizable: how long sentences run, what a paragraph does first, which images the writer
reaches for, and, just as important, **what the writer never does**. Those decisions become a
self-contained skill you can use again and again.

```text
You:     Here are five of my newsletter issues. Make a skill that writes like me.
Claude:  Measured 6,200 words. Your load-bearing traits: you open on a small concrete
         scene, never a thesis; two medium sentences then a short one that lands the point;
         no exclamation marks, ever; one aside in parentheses per section, at most ...
         Built `my-newsletter-writer`. Test drafts on two unrelated topics attached.
         Can you spot which of these three paragraphs is really yours?
```

<!-- DEMO: add a real blind test here (one original paragraph + two generated, answer in a <details> block) or a GIF of the full flow. -->

## Install

**Claude Code** (plugin marketplace):

```text
/plugin marketplace add moustafarhat/PersonaWriter
/plugin install personawriter@personawriter
```

**Claude Code** (manual):

```bash
git clone https://github.com/moustafarhat/PersonaWriter.git
cp -r PersonaWriter/skills/personawriter ~/.claude/skills/
```

<details>
<summary>Windows (PowerShell)</summary>

```powershell
git clone https://github.com/moustafarhat/PersonaWriter.git
Copy-Item -Recurse PersonaWriter\skills\personawriter "$HOME\.claude\skills\"
```
</details>

**claude.ai / Claude Desktop:** download `personawriter.zip` from the
[latest release](https://github.com/moustafarhat/PersonaWriter/releases/latest), then open
*Settings → Capabilities → Skills* and upload it. (Code execution must be enabled.)

**Other agents** that read the open `SKILL.md` format: copy `skills/personawriter/` into the
agent's skills folder.

Requirements: Python 3.9+ for the measuring scripts (standard library only, nothing to `pip install`).

## Use it

Just talk to Claude. No special syntax needed.

| You say | What happens |
|---|---|
| "Write a LinkedIn post about our launch, in the style of this article: …" | **Quick mode:** analyzes the sample and writes the post right away, then offers to save the voice as a skill. |
| "Turn my old blog posts into a skill that writes like me." | **Build mode:** full analysis, builds `<name>-writer`, tests it on unrelated topics, and refines it with your feedback. |
| "Here are three more of my essays. Update my voice skill." | **Update mode:** re-measures, revises the style guide, and tells you what changed. |
| "اكتب مقالاً عن العمل عن بعد بأسلوب هذا النص" | Works the same in Arabic (MSA or dialect). |
| "Schreib eine Produktankündigung im Stil dieses Textes." | …and in German, French, Spanish, and more. |

Once a style skill is built, use it by name: *"Write the welcome email with my-newsletter-writer"*,
or paste a draft and say *"rewrite this in my voice."*

### What gets built

```text
my-newsletter-writer/
├── SKILL.md                 # the voice in three sentences + writing procedure + guardrails
├── references/
│   ├── style-guide.md       # load-bearing traits, rhythm, diction, structure, never-list, dosage
│   ├── anchors.md           # 5-10 short labelled excerpts, to tune the ear, never to copy
│   └── profile.json         # the measured fingerprint
└── scripts/
    └── style_stats.py       # drift check: compares every new draft to the fingerprint
```

## Why it works

- **Decisions, not adjectives.** "Warm, witty, simple" gives a model nothing to act on.
  "Two medium sentences, then a short one that lands the point" does.
- **The swap test.** Every trait must survive a complete change of topic. Otherwise it is
  content, not style, and it would leak the source's subject into everything you write.
- **The never-list.** What a writer *refuses* to do (no exclamation marks, no bullet lists, no
  explaining the joke) is often the strongest signal, and the thing generic imitations miss.
- **Dosage.** Signature moves get a frequency ("one aside per section, at most"). Without it you
  get a caricature.
- **Measured drift.** Every draft can be checked against the source's numbers: sentence rhythm,
  paragraph shape, punctuation habits, person, openers.
- **Proven on new topics.** Each skill is tested on subjects the source never touched before it is
  handed over, with an optional blind test: can *you* tell which paragraph is real?

## Languages

| | Rhythm, paragraphs, punctuation | Person & stop-words | Close-reading notes |
|---|:-:|:-:|:-:|
| English, German, Arabic (MSA + dialects) | ✅ | ✅ | ✅ detailed |
| French, Spanish, Portuguese, Italian | ✅ | ✅ | ✅ |
| Chinese, Japanese (measured in characters) | ✅ | - | general |
| Any other Unicode language | ✅ | - | general |

Want your language to be first-class? It is usually a 20-line PR, see [CONTRIBUTING.md](CONTRIBUTING.md).

## Command-line tools

The scripts work on their own too:

```bash
# fingerprint one or more texts
python skills/personawriter/scripts/style_stats.py analyze essay1.txt essay2.txt --json profile.json

# how far is a draft from that fingerprint?
python skills/personawriter/scripts/style_stats.py compare profile.json draft.txt

# scaffold a new style skill folder from samples
python skills/personawriter/scripts/scaffold.py my-style-writer ./out sample.txt
```

## Ethics & fair use

PersonaWriter learns **patterns**: rhythm, structure, diction habits. Studying and imitating
those is how writers have always learned. The skill is built to stay on the right side of the line:

- It stores patterns plus at most a few short anchor excerpts, **never large passages** of the source.
- Output is **original text in a manner**, not text passed off as the source author's work.
- It declines to write messages meant to be taken as coming from a real, identifiable person
  (other than you), to invent quotes, or to produce fake reviews and astroturfing.

Using it on your own writing or your organization's writing is the most common and most useful
case, and there is no ambiguity there.

## Repository layout

```text
.
├── .claude-plugin/          # plugin + marketplace manifests (Claude Code)
├── skills/personawriter/    # the skill itself (this folder is what gets installed)
│   ├── SKILL.md
│   ├── references/          # analysis lens + templates for generated skills
│   └── scripts/             # style_stats.py, scaffold.py
└── tests/                   # python -m unittest discover tests
```

## Contributing

Issues and PRs are welcome, especially new languages, real-world failure cases ("it turned my
voice into a caricature when…") and example skills built from public-domain authors.
See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT. See [LICENSE](LICENSE).
