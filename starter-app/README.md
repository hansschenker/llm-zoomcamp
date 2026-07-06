# RAG Starter — Walking Skeleton

The minimal end-to-end RAG app from
[../rag-starter-advice.md](../rag-starter-advice.md): ingest →
retrieve → prompt → LLM → evaluate, closed loop first, everything
else later.

Stack: embedded ChromaDB (local directory, no server; embeds with its
built-in local model — free, no API key needed for indexing or
retrieval), OpenAI `gpt-5.4-mini` for generation, the DataTalks.Club
course FAQ as the corpus (naturally chunked, small, familiar).

## Quickstart

```bash
cd starter-app
uv sync

cp .env.example .env      # then put your OPENAI_API_KEY in .env

uv run python ingest.py                             # index the corpus
uv run python rag.py "How do I join the course?"    # one-shot answer
uv run python rag.py --show-prompt "..."            # see the full prompt
uv run streamlit run app.py                         # chat UI
```

First run of `ingest.py` downloads Chroma's local embedding model
(~80 MB) — one-time cost.

## Evaluation loop

```bash
uv run python evaluate.py --generate 25   # LLM writes 25 eval questions
git add eval/questions.json               # freeze the eval set — commit it
uv run python evaluate.py                 # Hit Rate@k + MRR (retrieval only)
```

Now change one knob in `config.py` (e.g. `TOP_K`), re-run
`evaluate.py`, and compare numbers. That's the whole improvement
loop.

## Layout

| File | Role |
|-|-|
| `config.py` | All tunable knobs (course, top-k, model, paths) |
| `ingest.py` | Phase A: load FAQ → index into embedded Chroma |
| `rag.py` | Phase B: search → context → prompt → LLM (+ CLI) |
| `app.py` | Streamlit UI showing answer, chunks, and full prompt |
| `evaluate.py` | Phase C: generate frozen eval set, Hit Rate@k + MRR |

## Next steps (in order, each justified by eval numbers)

1. Swap in your own corpus: replace `load_faq_documents()` in
   `ingest.py` (IBM Docling for PDFs/DOCX — see
   [../python-toolchain.md](../python-toolchain.md))
2. Wrap `llm()` with metrics (tokens, cost, latency) — the
   `RAGWithMetrics` pattern from module 5
3. Add LLM-as-a-judge answer evaluation (Pydantic +
   `client.messages.parse` / structured outputs)
4. Store conversations + feedback in Postgres, dashboard on top
5. Only then: hybrid search, reranking, better embeddings — measured
   against the frozen eval set
