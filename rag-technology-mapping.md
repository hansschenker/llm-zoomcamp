# Technology Mapping for the Canonical RAG Workflow

How a concrete technology stack — IBM Docling, ChromaDB, Python,
TypeScript, OpenAI, Anthropic — maps onto the steps in
[rag-canonical-workflow.md](rag-canonical-workflow.md).

The short version: Docling owns Phase A's document processing, ChromaDB
owns storage and retrieval, OpenAI or Anthropic owns generation and
judging, and Python/TypeScript are the glue — with one important
constraint in the embedding step.

## Step-by-step mapping

| Workflow step | Technology | Role |
|-|-|-|
| 1. Load documents | Python (+ Docling) | Your code gathers sources; Docling reads the files |
| 2. Parse / extract text | **IBM Docling** | Its core job: PDF, DOCX, PPTX, HTML, images (OCR), tables → clean structured text + metadata |
| 3. Chunk | **IBM Docling** | Its `HybridChunker` / `HierarchicalChunker` split along the document's real structure — the "natural units first" advice |
| 4. Embed chunks | **OpenAI** (`text-embedding-3-small/large`) or ChromaDB's built-in local embedder | See the Anthropic note below |
| 5. Store vectors + text + metadata | **ChromaDB** | Stores embedding, original chunk text, and metadata together; supports metadata filters |
| 6. User asks a question | **TypeScript** or Python app layer | Chat UI or API endpoint |
| 7. Retrieve | **ChromaDB** | `collection.query()` embeds the query with the *same* embedding function registered on the collection, runs nearest-neighbor search, applies `where` filters |
| 8. Build the prompt | Plain Python/TypeScript | No library needed — string assembly |
| 9. Generate the answer | **OpenAI** or **Anthropic** | Both have first-class Python and TypeScript SDKs |
| 10. Evaluate (ground truth, LLM-judge) | Python + **Anthropic** or OpenAI | Structured outputs make the judge reliable |
| 11. Monitor | Python/TypeScript + your DB | Both APIs return per-call `usage` token counts for cost tracking |

## Key decisions

### Anthropic has no embeddings API — the one gap in this stack

The Anthropic API is the Messages API: generation, tool use, batches,
files — but no embedding endpoint. So step 4 and the query-embedding
half of step 7 must come from **OpenAI** or from **ChromaDB's built-in
default embedder** (a local ONNX `all-MiniLM-L6-v2`, free and offline —
the same model the LLM Zoomcamp course uses; fine for prototypes, with
OpenAI embeddings for production quality). Anthropic's role is steps 9
and 10, not step 4.

### Where Anthropic fits best: generation and especially the judge

For step 9, the current default model choice is `claude-opus-4-8`
(Claude Sonnet 4.6 for high-volume or cost-sensitive routes). For
step 10, Claude with **structured outputs** is a strong judge:
`client.messages.parse()` with a Pydantic model (or `zodOutputFormat`
in TypeScript) gives schema-validated verdicts — the same goal as the
course's `llm_structured_retry`, but enforced at the API level rather
than by retry loops.

A practical bonus: if OpenAI generates your answers and Claude judges
them (or vice versa), you avoid the self-preference bias of a model
grading its own output.

For large offline eval runs (step 10 over thousands of ground-truth
questions), both vendors' **batch APIs run at 50% price** — the right
way to run evaluation sweeps.

### Python vs TypeScript splits along the offline/online boundary

IBM Docling is Python-only, so the Phase A indexing pipeline
(steps 1–5) must be Python — which also suits evaluation (step 10:
pandas, notebooks). The Phase B online app (steps 6–9) can be either:
ChromaDB, OpenAI, and Anthropic all have TypeScript clients, so a
Next.js/Node front end talking to a Chroma server is a natural fit. If
you don't need a web stack, all-Python (with Streamlit, as in the
course) is the simpler choice.

Note that ChromaDB's embedded/in-process mode is Python-only; from
TypeScript you run Chroma as a small server and connect via the JS
client.

### ChromaDB quietly solves two correctness traps

Two of the corrections in the canonical workflow are enforced by
Chroma's design:

1. You register the embedding function on the collection once, and
   Chroma uses it for both indexing and queries — enforcing the "same
   model at index time and query time" rule.
2. It stores documents and metadata alongside vectors, so step 8 gets
   the chunk *text* back from the query result directly — no separate
   text store needed.
