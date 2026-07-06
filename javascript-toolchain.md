# JavaScript/TypeScript-Centered RAG Toolchain

The tool choices for building a RAG app centered on TypeScript,
organized by the phases of
[rag-canonical-workflow.md](rag-canonical-workflow.md).

The one structural gap versus the Python chain: **IBM Docling is
Python-only**, so document parsing needs either a JS-native substitute,
a hosted parsing API, or a small Python sidecar for indexing (the
hybrid split recommended in
[rag-technology-mapping.md](rag-technology-mapping.md)). Everything
else — ChromaDB, OpenAI, Anthropic — has first-class TypeScript
clients.

## Project foundation

| Tool | Role |
|-|-|
| Node.js 22+ | Runtime (Bun is a viable alternative) |
| TypeScript | Language — types on schemas and API payloads pay off fast in RAG code |
| pnpm | Package manager |
| dotenv | Load `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` from `.env` |
| Biome (or ESLint + Prettier) | Linting and formatting |
| Vitest | Tests |
| Docker | Chroma server, Postgres, Grafana |

## Phase A — Indexing (offline)

| Step | Tool | Role |
|-|-|-|
| 1. Load documents | fetch / undici | Pull sources; Node's built-in `fetch` covers most of it |
| 2. Parse / extract | **pdfjs-dist / pdf-parse** (PDF), **mammoth** (DOCX), **cheerio** (HTML) | JS-native parsing, one library per format |
| | *or* a hosted parsing API (LlamaParse, Unstructured API) | One API for all formats when quality matters more than offline operation |
| | *or* a Python Docling sidecar | Best parsing quality; run indexing in Python, keep the app in TS |
| 3. Chunk | **@langchain/textsplitters** (`RecursiveCharacterTextSplitter`) | Standalone splitter package — no need to adopt the rest of LangChain |
| 4. Embed | **openai** npm (`text-embedding-3-small`) | Production embeddings; local free alternative: **@huggingface/transformers** (transformers.js) running `all-MiniLM-L6-v2` on ONNX — the same model the course's `embed/` uses |
| 5. Store | **chromadb** npm client + Chroma server (Docker) | No embedded mode in JS — the client talks to a server; register the embedding function on the collection |

## Phase B — Retrieval and generation (online)

| Step | Tool | Role |
|-|-|-|
| 6. User question | **Next.js** (full-stack UI) or **Hono/Fastify** (API-only) | React chat UI, or a lean API if the front end lives elsewhere |
| 7. Retrieve | chromadb `collection.query()` | Same-model query embedding handled by the collection; `where` filters for metadata |
| 8. Build prompt | Plain TypeScript | Template literals — no library |
| 9. Generate | **@anthropic-ai/sdk** (`claude-opus-4-8`) and/or **openai** npm | Stream tokens to the browser via SSE / `ReadableStream` |

## Phase C — Evaluation and monitoring (ongoing)

| Step | Tool | Role |
|-|-|-|
| 10. Evaluate | TS scripts + CSV/JSON | Ground-truth runs, Hit Rate / MRR — plain code, no pandas needed |
| | **Zod** + `zodOutputFormat` (Anthropic) / `zodResponseFormat` (OpenAI) | Schema-validated LLM-judge verdicts |
| | Batch APIs (OpenAI Batch / Anthropic Message Batches) | Large eval sweeps at 50% price |
| 11. Monitor | **PostgreSQL** + **Drizzle ORM** (or plain `pg`) | `conversations` + `feedback` tables (full prompt, tokens, cost, latency) |
| | **Grafana** | Dashboards over the same tables |

## Notes

- **Zod is the TS counterpart of Pydantic** — one schema drives judge
  validation, API request validation, and TypeScript types.
- **The Vercel AI SDK is optional glue**, useful for streaming UI hooks
  in Next.js, but the same "frameworks last" advice applies: the core
  pipeline is four small functions; don't bury it.
- **Cloudflare path:** if deploying on Workers, the same shape works
  with **Vectorize** replacing the Chroma server and Workers AI or
  OpenAI for embeddings — worth considering since the app layer is
  already fetch-based.
- **Recommended split for best of both:** Python (uv + Docling +
  chromadb) for the offline indexing and evaluation scripts, TypeScript
  for the user-facing app — they meet at the Chroma server and the
  Postgres monitoring tables.
