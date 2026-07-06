# Advice for Starting to Code RAG Apps

Process advice for the first weeks of RAG coding. Complements
[rag-lessons.md](rag-lessons.md) (architecture lessons from the course
codebase) — this is about *how to work*, not how to structure code.

## 1. Build the ugly walking skeleton on day one

Ingest → search → prompt → LLM → answer, end to end, in a single
notebook, before improving any single part. The classic beginner trap
is polishing ingestion for a week before ever seeing an answer. A RAG
app only teaches you things once the loop is closed — every
improvement after that is measurable against a working baseline.

## 2. Pick a corpus you know cold

Your own notes, docs from a project you built, course material you've
studied. When you know the source material, you can eyeball whether a
retrieved chunk is the *right* chunk and whether an answer is subtly
wrong — you're your own evaluation oracle during the early phase when
you don't have metrics yet. A corpus of strangers' documents makes
every debugging session a research project.

## 3. Keep it small enough to iterate in seconds

Fifty to two hundred chunks. Full re-index in under a minute. The
quality of a RAG app is a function of how many experiment cycles you
run, and cycle time is the denominator. Scale the corpus only after
the pipeline is settled.

## 4. Print the prompt. Always.

The single highest-value debugging habit in RAG: log the fully
assembled prompt — context block and all — for every query. Nearly
every "the LLM is being dumb" complaint dissolves when you read what
the model actually received: the right chunk wasn't there, the chunks
were truncated garbage, or the question got buried under ten
irrelevant passages. If you build one piece of tooling for yourself,
make it "show me the prompt for this query."

## 5. Diagnose the stage before touching anything

When an answer is bad, there are three failure points with three
different fixes:

1. **Retrieval missed** → fix search/chunking (prompt tweaks won't help)
2. **Context was right but the answer ignored it** → fix the prompt
   and instructions
3. **The source material doesn't contain the answer** → fix the
   corpus, or accept "I don't know" as correct behavior

The number-one beginner mistake is prompt-engineering around a
retrieval failure.

## 6. Freeze a tiny eval set before you start tuning

Twenty or thirty questions with known-good source chunks, written
down *before* you begin experimenting — otherwise you unconsciously
tune to the three questions you always test with. Even a crude Hit
Rate over 25 questions turns "feels better" into "went from 17/25 to
21/25," and that's the difference between progress and wandering.

## 7. Inspect what you actually indexed

After chunking, read twenty random chunks. You'll routinely find
headers glued to the wrong section, tables shredded into noise,
boilerplate repeated a hundred times. Bad retrieval is usually bad
chunks, and no embedding model rescues garbage input. This is where
Docling earns its place — but verify its output too.

## 8. Spend your caution on data and retrieval, not the model

The LLM is the most reliable component in the pipeline; given the
right context, current models nearly always answer well. Beginners
allocate their worry backwards. Correspondingly, develop with a cheap
model and track cost per query from day one — you'll be surprised how
affordable iteration is, which removes the false pressure to
under-experiment.

## 9. Name your knobs

Chunk size, overlap, top-k, boost weights, the embedding model — keep
them as constants at the top of the file, and commit after every
configuration that beats the last one. Two weeks in, "what settings
produced that good run on Tuesday?" is otherwise unanswerable.

## 10. Add persistence and infrastructure last

In-memory index, embedded Chroma, no server, no Docker, no LangChain
until the pipeline works and the eval numbers justify each addition.
Every piece of infrastructure added before the loop works is surface
area for bugs that look like RAG problems but aren't.

## In one sentence

Close the loop first, read your prompts and chunks, measure before
tuning, and blame retrieval before you blame the model.
