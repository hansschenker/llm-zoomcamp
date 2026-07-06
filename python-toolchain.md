# Python-Centered RAG Toolchain

The tool choices for building a RAG app entirely in Python, organized
by the phases of [rag-canonical-workflow.md](rag-canonical-workflow.md).
Python is the natural home for the whole pipeline: every tool in our
stack ([rag-technology-mapping.md](rag-technology-mapping.md)) has a
first-class Python API, and IBM Docling is Python-only.

## Project foundation

| Tool | Role |
|-|-|
| Python 3.12+ | Language |
| [uv](https://docs.astral.sh/uv/) | Package and project manager (`uv init`, `uv add`, `uv run`) |
| python-dotenv | Load `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` from `.env` |
| Jupyter | Exploration and prototyping notebooks |
| ruff | Linting and formatting |
| pytest | Tests |
| Docker | Postgres, Grafana, and deployment containers |

## Phase A — Indexing (offline)

| Step | Tool | Role |
|-|-|-|
| 1. Load documents | httpx / requests | Fetch sources; Docling reads local and remote files directly |
| 2. Parse / extract | **IBM Docling** | PDF, DOCX, PPTX, HTML, images (OCR), tables → structured `DoclingDocument` |
| 3. Chunk | **Docling** `HybridChunker` | Structure-aware chunking; plain Python for naturally-chunked data (FAQ entries) |
| 4. Embed | **openai** SDK (`text-embedding-3-small`) | Production embeddings; local free alternative: ChromaDB's default ONNX embedder or sentence-transformers |
| 5. Store | **chromadb** (`PersistentClient`) | Embedded mode — a local directory, no server process; register the embedding function on the collection |

## Phase B — Retrieval and generation (online)

| Step | Tool | Role |
|-|-|-|
| 6. User question | **Streamlit** (prototype UI) or **FastAPI** + uvicorn (API) | Streamlit for the course-style chat app; FastAPI when others integrate against you |
| 7. Retrieve | chromadb `collection.query()` | Embeds the query with the collection's registered function; `where` filters for metadata |
| 8. Build prompt | Plain Python | String assembly — no library |
| 9. Generate | **anthropic** SDK (`claude-opus-4-8`) and/or **openai** SDK | Stream responses in the UI; keep the provider swappable behind one function |

## Phase C — Evaluation and monitoring (ongoing)

| Step | Tool | Role |
|-|-|-|
| 10. Evaluate | pandas + tqdm | Ground-truth runs, Hit Rate / MRR |
| | **Pydantic** + `anthropic` `client.messages.parse()` | Schema-validated LLM-judge verdicts (cross-vendor judging avoids self-preference bias) |
| | Batch APIs (OpenAI Batch / Anthropic Message Batches) | Large eval sweeps at 50% price |
| 11. Monitor | **PostgreSQL** + psycopg | `conversations` + `feedback` tables (full prompt, tokens, cost, latency) |
| | Streamlit dashboard → **Grafana** | Streamlit while iterating; Grafana for real dashboards |

## Notes

- **Frameworks last.** Start with plain functions (the ~80-line
  `RAGBase` pattern from [rag-lessons.md](rag-lessons.md)); reach for
  LangChain/LlamaIndex only when you know what they'd abstract.
- **ChromaDB embedded mode is a Python privilege** — no server to run
  during development. Move to Chroma server (Docker) or pgvector when
  you need concurrent writers or a separate app process.
- **One project per app, managed by uv** — mirror the course's layout:
  `pyproject.toml`, `ingest.py`, `rag.py`, `app.py`, `evaluate.py`.
