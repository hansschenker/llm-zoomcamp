# Lessons from LLM Zoomcamp for Building Our Own RAG Apps

Transferable lessons for our own RAG applications, distilled from how
this course's codebase is actually structured — not just what the
lessons say.

## 1. The core pipeline should be embarrassingly small

The entire RAG engine (`rag_helper.py`) is ~80 lines:
`search → build_context → build_prompt → llm`, each a separate method.
No framework. That decomposition is the load-bearing decision — every
later feature (metrics, agents, evaluation) works by wrapping or
overriding exactly one of those four steps. Frameworks like LangChain
appear only in module 6, as an option, once you understand what they
abstract.

## 2. Design for a swappable search backend, and start simpler than you think

`RAGBase` takes any `index` with a `.search()` method. The course swaps
minsearch (in-memory) → sqlitesearch (SQLite file) → pgvector
(production Postgres) without touching the pipeline. And notably: the
baseline is *keyword* search, not vectors. Field boosting (question 3x,
section 0.5x) plus a keyword filter field gets you a surprisingly
strong retriever for zero infrastructure. Vectors, then hybrid/RRF and
reranking, are introduced as measured improvements over that baseline —
not as the default starting point.

## 3. Evaluation before features

The most transferable workflow in the repo: generate ground truth with
an LLM (N questions per document), then compute Hit Rate and MRR for
retrieval, then use those numbers to tune parameters like boosts.
Retrieval quality is measurable cheaply and offline; answer quality
uses LLM-as-a-judge. Without this, you can't tell whether hybrid
search or a new embedding model actually helped. Most homegrown RAG
efforts skip this and tune blind.

## 4. Instrument at the narrowest point

`RAGWithMetrics` overrides only `llm()` — timing the call and capturing
tokens and computed dollar cost into an `LLMCallRecord`. Because
instrumentation lives at one choke point, the app, CLI, and future
variants all get metrics for free. Cost-per-call tracking from
`response.usage` is trivial to add on day one and painful to retrofit.

## 5. Store everything, key feedback to conversations

The monitoring schema is worth copying directly: a `conversations`
table with the *full prompt and instructions* (not just Q&A — you need
them to debug bad answers later), and a `feedback` table referencing
the conversation id with a `source` column distinguishing the
automatic LLM judge from human thumbs up/down. Every answer gets
judged immediately in the request path; humans are optional extra
signal. Dashboards (Streamlit, then Grafana) are just queries over
these two tables.

## 6. Structured outputs need validation and retry

Anything machine-consumed — the judge verdict, ground-truth
generation — goes through a Pydantic model with a retry wrapper
(`llm_structured_retry`). Never parse free-text LLM output for
programmatic use.

## 7. Agentic is a thin layer, not a rewrite

The "agent" in module 1 is the same `search()` function exposed as a
tool via function calling, plus a loop that runs until the model stops
calling tools. If your fixed pipeline is well-factored, going agentic
is additive. The course also implicitly warns: the fixed pipeline is
what they run in production (the monitoring app) — agents are for when
one-shot retrieval genuinely isn't enough.

## 8. Keep the ops surface boring

Per-app uv project, `.env` for keys, OpenAI-compatible `base_url` so
the provider is a config change (Groq/Gemini/Ollama), one `docker run`
for Postgres, a Makefile for run commands. Everything runs on a laptop
with a few dollars of API credit — that cheap iteration loop is what
makes the evaluation-driven workflow practical.

## 9. Chunking is data-dependent, not step one

The FAQ corpus has natural units (question/answer pairs), so the
course does no chunking until the project-example module. If your
source data has natural structure, use it before reaching for
fixed-size splitters.

## Definition of done

The capstone rubric doubles as a definition of done for any RAG app:

1. A searchable knowledge base
2. The retrieval pipeline
3. An evaluation process
4. A user-facing interface
5. Monitoring with feedback loops

If one of those five is missing, it's a demo, not an app.
