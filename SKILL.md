---
name: personawriter
description: Extracts the writing style of a sample text (an article, essay, book chapter, speech, blog, or the user's own past writing) into a precise style profile, then builds a ready-to-install, dedicated writing skill that produces new text in that style. Use whenever the user wants to capture, learn, absorb, clone, imitate, mimic or match a writing style, voice or tone; wants a skill or agent that "writes like" a given article, book, author or their own texts; wants a personal or brand voice built from samples; or says things like "write like this", "استخرج أسلوب هالنص", "اعمل سكيل بهالأسلوب", "im Stil dieses Textes schreiben" - even if they never say "skill". Works for English, German, Arabic (Modern Standard and dialects) and other languages.
---

# PersonaWriter

Turns a writing sample into a **dedicated style skill**: a self-contained folder that any
future Claude session can load to write new text in that voice.

The core insight: a style is not a list of adjectives ("warm, witty, simple"). It is a set
of repeatable *decisions* - how long sentences run, what a paragraph does first, which
images the writer reaches for, what the writer refuses to do. Adjectives give a model
nothing to act on; decisions do. Everything below pushes toward decisions that can be seen
in the text and applied to a new topic.

## Workflow

Work through these stages in order. Keep the user informed in plain language at each stage,
but do not ask for permission at every step - this is a build task.

### 1. Intake

- **Get the sample.** It may be pasted, or uploaded (look in `/mnt/user-data/uploads/`; if the
  content is not already in context, use the file-reading skill for PDF/DOCX/EPUB). Save the
  plain text to `/home/claude/work/sample.txt` (several files are fine).
- **Judge if it is enough.** Under ~1,000 words gives only a sketch; 3,000-10,000 words across
  different parts is the sweet spot. For a book, choose a spread (opening, middle, a dialogue-heavy
  stretch, a reflective stretch) rather than only chapter one. If the sample is thin, say so, build
  anyway, and mark the profile as provisional.
- **Ask only what you cannot infer**, at most two or three short questions, in one message:
  1. What will the finished skill write (essays, chapters, posts, emails...)? This sets the genres in its description.
  2. Whose writing is it - the user's own, or someone else's? (Affects how many excerpts to keep, see below.)
  3. Preferred name for the style, if they have one; otherwise choose a descriptive slug yourself.
  If the request already answers these, skip the questions.
- **A note on fairness.** Learning patterns (rhythm, structure, diction habits) from a published
  work is ordinary stylistic study. The generated skill must store *patterns*, plus at most a few
  short anchor excerpts, never large passages, and must be framed as writing original text in a
  manner - not as passing text off as the author's own or inventing quotes for real people.

### 2. Measure

Run the scaffold script. It measures the sample, writes `references/profile.json`, and
copies the stats script into the new skill so it is self-contained:

```bash
python <this-skill-dir>/scripts/scaffold.py <style-slug>-writer /home/claude/work /home/claude/work/sample.txt
```

(`<this-skill-dir>` is the folder containing this SKILL.md.) Read the printed report. It gives
sentence-length distribution, rhythm variation, paragraph size, punctuation per 1,000 words,
sentence openers, person usage, quoted-speech share, and recurring phrases. These are
evidence for the next stage, not the goal: a numeric match with a bland voice is worthless.

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
Principles that make it work:
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
- `references/anchors.md` - 5-10 short excerpts (one or two sentences each), each labelled with the trait it shows. If the source is a third party's published work keep quoted material minimal and lean on paraphrased patterns; if it is the user's own writing you can be more generous while still keeping each anchor short.

Make the generated skill's `description` pushy and concrete: name the genres, the phrasings
users will actually say (in the user's languages), and the "rewrite my draft in this voice" case.

Write the skill's instructions in English unless the user prefers otherwise, but keep
anchors and examples in the sample's original language, and describe dialect and spelling
conventions explicitly when the sample uses them.

### 6. Prove it

A style skill is only as good as what it writes on topics the source never touched.
1. Choose two test topics unrelated to the source, one close to the source's genre and one further away (e.g. a product update, a short story scene).
2. Following the generated skill's own procedure, write ~300-500 words for each, then run its drift check (`scripts/style_stats.py compare references/profile.json draft.txt`).
3. Read both drafts critically against the never-list. Fix the guide (not just the draft) where something felt off.
4. Show the user one draft and ask what feels right and what feels off. For a sharper test, offer a blind check: three short paragraphs on the same topic, one original and two generated - can they tell which is real?
5. Revise the style guide once or twice based on feedback. Stop when the user is satisfied; subjective work needs human judgment, not a benchmark.

### 7. Package and deliver

Use the skill-creator's packager (`python -m scripts.package_skill <skill-folder> <output-dir>`, run from the
skill-creator directory, `/mnt/skills/examples/skill-creator` when available) with the new folder and
`/mnt/user-data/outputs` as the output directory. Then call `present_files` with the resulting `.skill` file so the user can save it. Finish
with a short message: what the style's essence is (one or two sentences), what was tested,
and how to use it ("ask for a text and mention the style name" or "paste a draft and ask me
to rewrite it in this voice").

## Common failure modes

- **Costume, not voice** - writing neutral prose and sprinkling in signature phrases. The fix is drafting with the load-bearing traits from the first sentence.
- **Caricature** - every quirk in every paragraph. The fix is the dosage section.
- **Topic contamination** - encoding the sample's subject vocabulary as "style". The fix is the swap test.
- **Averaging** - smoothing away exactly the odd choices that make the voice recognizable. Keep the oddities, with dosage.
- **Over-fitting one genre** - a novelist's narration rules will not automatically fit a tweet. Flag what is inference.
- **Copying** - reusing the sample's actual sentences. Anchors tune the ear; they are never source material.

## Files in this skill

- `references/style-dimensions.md` - the analysis lens (voice, syntax, diction, rhetoric, structure, fiction, Arabic/German/English notes, swap test). Read in stage 3.
- `references/generated-skill-template.md` - folder layout and templates for the generated skill's SKILL.md, style guide and anchors. Read in stages 4-5.
- `scripts/style_stats.py` - `analyze` fingerprints a text; `compare` checks a draft against a saved profile.
- `scripts/scaffold.py` - creates the new skill folder, measures the sample, copies the stats script.
