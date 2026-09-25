# Template for a generated style skill

The output of PersonaWriter is a folder named `<style-slug>-writer/`. Use the three
templates below, filling every `<...>` with what you learned from the sample. Delete
any section that has nothing distinctive to say - an empty section is noise.

## Contents
1. Folder layout
2. SKILL.md template
3. references/style-guide.md template
4. references/anchors.md template
5. Quality bar for the finished skill

---

## 1. Folder layout

```
<style-slug>-writer/
├── SKILL.md                  # workflow + essence (short, loads every time)
├── references/
│   ├── style-guide.md        # the full analysis (read on every writing task)
│   ├── anchors.md            # a few short excerpts to tune the ear
│   └── profile.json          # metrics saved by `style_stats.py analyze --json`
└── scripts/
    └── style_stats.py        # copied from PersonaWriter, used for the drift check
```

Slug: lowercase, hyphens, ends in `-writer` (e.g. `essayist-warm-writer`, `nahj-hikayat-writer`).
If the style belongs to a named author, the user may want the name in the slug - ask,
but default to a descriptive slug.

---

## 2. SKILL.md template

```markdown
---
name: <style-slug>-writer
description: Writes new text in the "<style name>" style - <one-line essence, e.g. "warm, self-deprecating first-person essays built from small domestic scenes">. Use whenever the user asks for <genres it should cover: essays, chapters, posts, letters, speeches...> "in this style", "in the style of <source>", "wie <source> schreiben", "اكتب بأسلوب <source>", or asks for a draft that should sound like <source/owner>, even if they never name the style explicitly. Also use to rewrite an existing draft into this voice.
---

# <Style name> Writer

<Two or three sentences: what this voice sounds like to a reader. Concrete, sensory,
no empty adjectives. This paragraph is the "north star" the model returns to.>

Source: <what the style was learned from - title, author or "the user's own texts", approx word count>.
Language(s): <language and register/dialect>.

## Before you write
1. Pin down the brief: topic, audience, length, genre. If something is missing, make a reasonable
   assumption and state it in one line - do not interrogate the user.
2. Read `references/style-guide.md` fully. Skim `references/anchors.md` to tune your ear
   (these are for *feel*; never copy from them).
3. Keep the topic and the style separate: the style is fixed, the content is new.

## Writing procedure
1. **Shape first.** Sketch the structure the way this voice would build it (see "Structure" in the
   style guide): how it opens, how paragraphs move, how it ends.
2. **Draft in one pass** with the load-bearing traits (the top of the style guide) in place from
   the first sentence. Do not write neutral prose and "add style" afterwards - that produces a
   costume instead of a voice.
3. **Check drift.** Save the draft to a file and run (`python` or `python3`):
   `python scripts/style_stats.py compare references/profile.json draft.txt`
   Treat flagged metrics as hints, not commands - fix the ones that make the voice feel off
   (typically sentence length and paragraph shape), ignore noise on short drafts.
4. **Read against the never-list** in the style guide and cut every violation.
5. **Deliver** the text. Add a one-line note only if you made an assumption or the user should
   choose between options. No commentary about the style unless asked.

## Dials the user may turn
<List 3-6 adjustable aspects with what "more" and "less" mean, e.g.:
- warmth: more = direct address and confession; less = observational distance
- density of signature moves: default is <x per page>; "lighter" = half, "stronger" = 1.5x>

## Guardrails
- Write original text. Do not reproduce passages from the source, and do not invent quotes
  attributed to real people.
- This style guide describes patterns for an original writer to follow; do not present the output
  as authored by the source's author, or as a message from any real person other than the user.
- Facts must still be correct. Style never justifies making things up.
```

Description tips: make it "pushy" - list the concrete genres and phrasings in the user's
languages, so the skill triggers on natural requests.

---

## 3. references/style-guide.md template

Order matters: the most recognizable traits go first, because a model applies early
instructions most reliably.

```markdown
# Style guide: <style name>

## 1. Load-bearing traits (get these right and it already sounds like it)
<3-6 traits. For each: the mechanism, the reason it works, and where it appears in the sample.
"Sentences alternate: two or three medium sentences, then a short one that lands the point
('Build for the one who does.'). This creates a spoken, confident cadence."
NOT: "Uses varied sentence length.">

## 2. Voice and stance
<Person, distance, attitude, how it treats the reader.>

## 3. Sentence and rhythm
<Numbers from profile.json in plain words: typical/short/long lengths, paragraph size, punctuation
habits, opener patterns. Give ranges, not single values.>

## 4. Diction and register
<Register, vocabulary texture, signature phrases (as patterns, e.g. "opens a turn with 'Here is
what I believe'"), avoided words. For Arabic/dialects: spelling conventions and code-switching.>

## 5. Rhetoric and imagery
<Image domains, humor style, favorite devices. Frequency of each.>

## 6. Structure
<How pieces open, how paragraphs are built, transitions, endings, formatting habits.>

## 7. Content moves
<How arguments and examples are handled.>

## 8. Never-list (what this voice does not do)
<5-10 items that would break the voice, e.g. "never uses bullet lists", "no exclamation marks",
"never explains the joke", "no motivational closing line".>

## 9. Dosage
<How often signature moves appear. A quirk repeated in every paragraph turns a voice into a
caricature. State e.g. "one aphorism per section, at most", "rhetorical question about once every
two paragraphs".>

## 10. Genre adaptations
<If the sample only covers one genre, say so. For other genres (email, post, speech), say which
traits carry over unchanged and which flex - and mark those as inference, not observation.>

## 11. Mini example
<One short before/after: a bland sentence pair rewritten in this style, with a note on
which traits did the work. Original, written by you - not lifted from the source.>
```

---

## 4. references/anchors.md template

```markdown
# Anchors (for ear-tuning only - never copy)

Each anchor is 1-2 sentences, with the trait it demonstrates.

1. "<short excerpt>" - <trait: e.g. short punch after two long sentences>
2. ...
```

Rules for anchors:
- 5-10 anchors, each one or two sentences. This is for feel, not reproduction.
- If the source is someone else's published work, keep the total quoted material small and
  prefer paraphrasing the pattern in the style guide over quoting.
- If the source is the user's own writing, they can allow more - still keep anchors short so the
  model absorbs the pattern rather than parroting passages.

---

## 5. Quality bar for the finished skill

- **Concrete:** every trait is a mechanism plus evidence, not an adjective.
- **Prioritized:** the top five traits are marked as load-bearing.
- **Bounded:** the never-list and dosage sections prevent caricature.
- **Portable:** works on topics unrelated to the source (validated in the test-writing step).
- **Lean:** SKILL.md under ~100 lines; the detail lives in the style guide.
