# The Canonical RAG Workflow

A corrected, general-purpose description of the steps needed for a RAG
application — independent of any specific project.

The most important structural point: a RAG app is **two pipelines, not
one sequence**. Indexing runs offline (once, or on a schedule);
retrieval + generation runs online on every user question. Plus a
third, ongoing loop — evaluation and monitoring — that turns a demo
into an app.

## Phase A — Indexing (offline)

**1. Load documents.** Ingest raw sources: files, websites, databases,
APIs. Track source identity so answers can cite where they came from.

**2. Parse and extract text.** Convert each format (PDF, HTML, Word,
transcripts) into clean text, preserving useful structure (titles,
sections, headings) and metadata (source, date, category). Metadata
becomes filterable fields later.

**3. Chunk the text.** Split documents into retrieval-sized pieces.
*Correction:* chunking is not necessarily "semantic" — that is one
strategy among several. Prefer natural units if the data has them
(FAQ entries, sections, paragraphs); otherwise fixed-size or recursive
splitting with overlap; semantic or LLM-assisted chunking only when
simpler methods fail. Each chunk keeps its text plus metadata.

**4. Embed each chunk.** Pass every chunk through an embedding model
to get a vector. *Correction:* tokenization is not a step you
implement — the embedding model tokenizes internally. What matters at
the app level: you embed *chunks* (not whole documents), and you must
record which embedding model you used, because queries must later be
embedded with the exact same model.

**5. Store in a vector database (index).** Save, for every chunk: the
vector, the **original chunk text**, and the metadata — not the vector
alone; the LLM will need the text, and filters need the metadata.
Optionally also build a keyword index over the same chunks to enable
hybrid search later.

## Phase B — Retrieval and generation (online, per question)

**6. User asks a question.** Optionally preprocess it first: rewrite
or expand the query, or apply metadata filters (e.g. restrict to one
product or course).

**7. Retrieve relevant chunks.** *Correction:* the query is not
"turned into tokens and searched" — it is **embedded into a vector
with the same model used at indexing time**, and the vector database
performs a nearest-neighbor similarity search (cosine or dot product),
returning the top-k most similar chunks with their text. Optional
improvements: hybrid search (combine keyword and vector results, e.g.
with Reciprocal Rank Fusion) and reranking the candidates with a
cross-encoder for higher precision.

**8. Build the prompt.** This step was missing from the original
list, and it is where "retrieval-augmented" actually happens: the
retrieved chunk *texts* (not vectors, not raw search results) are
assembled into a context block and combined with (a) standing
instructions ("answer only from the context; say 'I don't know'
otherwise") and (b) the user's question, into a single prompt.

**9. The LLM generates the answer.** The prompt goes to the LLM, which
produces an answer grounded in the supplied context; the answer (ideally
with source citations) is returned to the user. Agentic variants wrap
steps 7–9 in a loop: the LLM decides whether and what to search, via
function calling, until it has enough to answer.

## Phase C — Evaluation and monitoring (ongoing)

A production RAG app also needs the feedback loop:

**10. Evaluate offline.** Generate ground-truth questions per chunk
with an LLM; measure retrieval with Hit Rate / MRR; measure answer
quality with LLM-as-a-judge. Use the numbers to tune chunking, search
parameters, and models.

**11. Monitor online.** Log every conversation with its full prompt,
token counts, cost, and latency; judge answers automatically in the
request path; collect user feedback (thumbs up/down); watch it all on
a dashboard. Findings feed back into Phase A and B tuning.

## Corrections to the original 9-step list, summarized

| Original step | Correction |
|-|-|
| 3. "semantically chunk" | Chunking, yes — but semantic chunking is one option, not the default. Use natural document units first. |
| 4. "tokenize text and create an embedding" | Tokenization is internal to the embedding model, not an app-level step. You embed each *chunk* and keep the chunk text alongside the vector. |
| 5. "save embeddings in a vector database" | Save embeddings **plus chunk text plus metadata**; optionally a keyword index too. |
| 7. "search text is created as tokens and searched" | The query is **embedded with the same model** used for indexing; the database does nearest-neighbor **vector similarity** search, not token matching. |
| 8. "the result of the search is sent to an LLM" | Missing step: the retrieved chunk texts are first assembled into a **prompt** with instructions and the user's question — that prompt is what the LLM receives. |
| (missing) | The offline/online split: steps 1–5 run at indexing time, 6–9 at query time. |
| (missing) | Evaluation and monitoring — without them you cannot tell whether any change helped. |
