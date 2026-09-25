---
name: personawriter
description: Extracts the writing style of a sample text (an article, essay, book chapter, speech, blog, newsletter, or the user's own past writing) into a precise style profile, then writes new text in that style or builds a ready-to-install writing skill that does. Use whenever the user wants to capture, learn, absorb, clone, imitate, mimic or match a writing style, voice or tone; wants text that "sounds like" a given article, author, brand or their own writing; wants a skill or agent that "writes like" someone; wants to rewrite a draft in a given voice; or wants to update or refine a style skill they built earlier. Triggers on phrases like "write like this", "in my voice", "match this tone", "استخرج أسلوب هالنص", "اكتب بأسلوبي", "اعمل سكيل بهالأسلوب", "im Stil dieses Textes schreiben", "écris comme ce texte", "escribe con este estilo" - even if they never say "skill". Works for English, German, Arabic (Modern Standard and dialects), French, Spanish and other languages.
---

# PersonaWriter

Turns a writing sample into a **voice you can reuse**: either a text written in that voice
right now (Quick mode), or a self-contained style skill that any future session can load
(Build mode).

The core insight: a style is not a list of adjectives ("warm, witty, simple"). It is a set
of repeatable *decisions* - how long sentences run, what a paragraph does first, which
images the writer reaches for, what the writer refuses to do. Adjectives give a model
nothing to act on; decisions do. Everything below pushes toward decisions that can be seen
in the text and applied to a new topic.

## Paths and environment

This skill runs anywhere (Claude Code, claude.ai, Claude Desktop, the API, other agents).
- `<skill-dir>` = the folder containing this SKILL.md.
- `<work>` = a scratch folder: the session's temp/scratchpad directory if there is one,
  otherwise a `personawriter-work/` folder in the current directory.
- `<out>` = where the finished skill goes: the user's skills folder if they name one
  (e.g. `~/.claude/skills/` in Claude Code), otherwise an outputs folder the user can
  download from (e.g. `/mnt/user-data/outputs` on claude.ai), otherwise the current directory.
- Uploaded files may already be in context; if not, look for them (on claude.ai:
  `/mnt/user-data/uploads/`) and extract plain text from PDF/DOCX/EPUB with whatever
  file-reading tools are available.
- Run the scripts with `python` or `python3`, whichever exists. They need only the standard library.

## Choose the mode

- **Quick mode** - the user wants a text now ("write X like this", "rewrite my draft in this
  voice") and did not ask for a reusable skill. Do stages 1-4 lightly (no questions, no
  scaffold), write the requested text, then offer in one line: "Want me to save this voice as a
  reusable skill?" If yes, continue with Build mode from stage 2.
- **Build mode** - the user asks for a skill, agent, reusable voice, or brand voice, or accepts
  the offer above. Do all stages.
- **Update mode** - the user has an existing style skill (built by PersonaWriter) and gives more
  samples or feedback. Re-run stage 2 into the same folder on all samples you have (the originals
  are usually not stored in the skill - that is fine, measure the new ones; the scaffold keeps the
  old numbers as `references/profile.previous.json` so you can weigh the two). Re-read against the existing style guide and revise it: keep what
  still holds, fix what the new material contradicts, and tell the user what changed.

When unsure, use Quick mode - a good first text is the best argument for building the skill.

## Workflow

Work through these stages in order. Keep the user informed in plain language at each stage,
but do not ask for permission at every step - this is a build task.

### 1. Intake

- **Get the sample** (pasted or uploaded) and save the plain text to `<work>/sample.txt`
  (several files are fine).
- **Judge if it is enough.** Under ~1,000 words gives only a sketch; 3,000-10,000 words across
  different parts is the sweet spot. For a book, choose a spread (opening, middle, a dialogue-heavy
  stretch, a reflective stretch) rather than only chapter one. If the sample is thin, say so, build
  anyway, and mark the profile as provisional.
- **Build mode only: ask only what you cannot infer**, at most three short questions, in one message:
  1. What will the finished skill write (essays, chapters, posts, emails...)? This sets the genres in its description.
  2. Whose writing is it - the user's own, or someone else's? (Affects how many excerpts to keep.)
  3. Preferred name for the style, if they have one; otherwise choose a descriptive slug yourself.
  If the request already answers these, skip the questions.

### 2. Measure

Run the scaffold script. It measures the sample, writes `references/profile.json`, and
copies the stats script into the new skill so it is self-contained:

```bash
python <skill-dir>/scripts/scaffold.py <style-slug>-writer <out> <work>/sample.txt
```

In Quick mode, measure without scaffolding: `python <skill-dir>/scripts/style_stats.py analyze <work>/sample.txt`.

Read the printed report: sentence-length distribution, rhythm variation, paragraph size,
punctuation per 1,000 words, sentence openers, person usage, quoted-speech share, and recurring
phrases. These are evidence for the next stage, not the goal: a numeric match with a bland
voice is worthless.

### 3. Read closely

Read `references/style-dimensions.md` now. Then read the sample twice: once for feel, once
annotating against the dimensions. Ground every observation in something you can point to.

Apply two tests to each candidate trait:
- **Swap test** - if the topic changed entirely, would the trait remain? If not, it is content, not style.
- **Frequency test** - does it recur across sections? One occurrence is an accident; a habit is style. Record *how often*, because dosage is part of the style.

Look especially for what is **absent**. The things a writer never does (no exclamation marks,
no lists, no explaining the joke) are often the strongest signal, and they are what keeps
imitations from turning generic.

### 4. Distill

Write the style guide following `references/generated-skill-template.md` (section 3).
(In Quick mode, keep it as working notes: load-bearing traits, never-list, dosage.)
- **Mechanisms over adjectives.** "Two medium sentences, then a short one that lands the point" beats "varied rhythm".
- **Rank by load.** Put the 3-6 traits that carry most of the recognizability first; early instructions get applied most reliably.
- **Quantify with ranges** from the profile ("sentences mostly 6-18 words, occasional 25+"), in plain words.
- **Include the never-list and dosage.** Without them the model overuses signature moves and produces caricature.
- **Separate observation from inference.** If the sample covers only one genre, say so and mark genre adaptations as inference.
- **Write one original mini-example** (bland sentence -> styled version) so the guide shows the traits at work.

### 5. Assemble the skill

Create, inside the scaffolded folder, using the templates in `references/generated-skill-template.md`:
- `SKILL.md` - essence, writing procedure, dials, guardrails. Keep it short (under ~100 lines).
- `references/style-guide.md` - the full analysis from stage 4.
- `references/anchors.md` - 5-10 short excerpts (one or two sentences each), each labelled with the trait it shows. If the source is a third party's published work, keep quoted material minimal and lean on paraphrased patterns; if it is the user's own writing you can be more generous while still keeping each anchor short.

Make the generated skill's `description` pushy and concrete: name the genres, the phrasings
users will actually say (in the user's languages), and the "rewrite my draft in this voice" case.

Write the skill's instructions in English unless the user prefers otherwise, but keep
anchors and examples in the sample's original language, and describe dialect and spelling
conventions explicitly when the sample uses them.

### 6. Prove it

A style skill is only as good as what it writes on topics the source never touched.
1. Choose two test topics unrelated to the source, one close to the source's genre and one further away (e.g. a product update, a short story scene).
2. Following the generated skill's own procedure, write ~300-500 words for each, then run its drift check (`python scripts/style_stats.py compare references/profile.json draft.txt`).
3. Read both drafts critically against the never-list. Fix the guide (not just the draft) where something felt off.
4. Show the user one draft and ask what feels right and what feels off. For a sharper test, offer a blind check: three short paragraphs on the same topic, one original and two generated - can they tell which is real?
5. Revise the style guide once or twice based on feedback. Stop when the user is satisfied; subjective work needs human judgment, not a benchmark.

### 7. Package and deliver

- If the skill was written straight into the user's skills folder, it is already installed - say so.
- Otherwise zip the folder so the zip contains `<style-slug>-writer/` at its root (use a
  skill-creator packager if one is available, else any zip tool or
  `python -c "import shutil; shutil.make_archive('<out>/<slug>', 'zip', '<out>', '<slug>')"`),
  and hand the user the file with whatever file-sharing mechanism the environment offers.

Finish with a short message: the style's essence (one or two sentences), what was tested,
where the skill is, and how to use it ("ask for a text and mention the style name" or "paste a
draft and ask me to rewrite it in this voice").

## Guardrails

- **Patterns, not passages.** Learning rhythm, structure and diction habits from a published work
  is ordinary stylistic study. Store patterns plus at most a few short anchors - never large passages.
- **Original text in a manner, not forgery.** The output is new writing *in a style*. Do not
  present it as written by the source's author, invent quotes for real people, or write messages
  meant to be taken as coming from a real, identifiable person (e.g. an email "from" a CEO, a
  statement "by" a politician) - unless that person is the user themself.
- **No deception at scale.** Decline to build voices meant for fake reviews, astroturfing, scams,
  or academic work that the user's institution forbids ghost-writing for.
- **Facts stay facts.** Style never justifies making things up.

## Common failure modes

- **Costume, not voice** - writing neutral prose and sprinkling in signature phrases. The fix is drafting with the load-bearing traits from the first sentence.
- **Caricature** - every quirk in every paragraph. The fix is the dosage section.
- **Topic contamination** - encoding the sample's subject vocabulary as "style". The fix is the swap test.
- **Averaging** - smoothing away exactly the odd choices that make the voice recognizable. Keep the oddities, with dosage.
- **Over-fitting one genre** - a novelist's narration rules will not automatically fit a tweet. Flag what is inference.
- **Copying** - reusing the sample's actual sentences. Anchors tune the ear; they are never source material.

## Files in this skill

- `references/style-dimensions.md` - the analysis lens (voice, syntax, diction, rhetoric, structure, fiction, language notes, swap test). Read in stage 3.
- `references/generated-skill-template.md` - folder layout and templates for the generated skill's SKILL.md, style guide and anchors. Read in stages 4-5.
- `scripts/style_stats.py` - `analyze` fingerprints a text; `compare` checks a draft against a saved profile.
- `scripts/scaffold.py` - creates the new skill folder, measures the sample, copies the stats script.
