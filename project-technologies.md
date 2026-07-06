# Technologies, Tools, and Libraries Used in LLM Zoomcamp

An inventory of everything the course materials use, grouped by
purpose, with pointers to where each item appears.

## Language and development environment

| Technology | Role | Where |
|-|-|-|
| Python (>= 3.12, lessons recommend 3.14+) | Course language | all module `code/` projects |
| [uv](https://docs.astral.sh/uv/) | Package/project manager; every module's `code/` dir is a standalone uv project | `pyproject.toml` in modules 1, 4, 5 |
| Jupyter | Notebooks are the primary teaching artifact | `code/*.ipynb` in modules 1, 2, 4 |
| python-dotenv | Load API keys from `.env` | all modules |
| [dirdotenv](https://github.com/alexeygrigorev/dirdotenv) | Optional auto-loading of `.env` per directory | module 1 environment lesson |
| GitHub Codespaces | Recommended uniform dev environment | module 1 environment lesson |
| Docker / Docker Compose | Postgres, Kestra, and full-app containers | modules 3, 5, 7 |
| requests | Fetching the FAQ dataset | `ingest.py` in modules 1, 4, 5 |

## LLM APIs and providers

| Technology | Role | Where |
|-|-|-|
| OpenAI API (`openai` client, Responses API) | The course LLM; default model `gpt-5.4-mini` | `rag_helper.py`, all modules |
| Groq, Gemini, Ollama | OpenAI-compatible alternatives (swap `base_url` + key) | environment lesson; `awesome-llms.md` lists many more |
| Google Gemini (`gemini-2.5-flash`) | Powers Kestra's AI Copilot and flows | `03-orchestration/docker-compose.yml` |
| Tavily | Web search API used by agent flows | module 3 flows |
| pydantic | Structured LLM outputs (judge verdicts, ground-truth generation) | `judge.py`, module 4 |

## Search and retrieval

| Technology | Role | Where |
|-|-|-|
| [minsearch](https://github.com/alexeygrigorev/minsearch) | In-memory keyword and vector search; the course's first search engine | modules 1, 2, 4, 5 |
| [sqlitesearch](https://github.com/alexeygrigorev/sqlitesearch) | Persistent SQLite-backed search (keyword and vector) | modules 1, 2 |
| PostgreSQL + pgvector | Production-grade vector search | module 2 (`vector_search_pgvector.ipynb`) |
| psycopg | Postgres client | modules 1, 2, 5 |
| Elasticsearch | Search backend in the LangChain lesson and project example | modules 6, 7 |
| Hybrid search (weighted sum, Reciprocal Rank Fusion) and reranking | Retrieval-quality techniques | module 6 |

## Embeddings

| Technology | Role | Where |
|-|-|-|
| sentence-transformers | Generating embeddings (PyTorch-based) | module 2 |
| ONNX Runtime + tokenizers + numpy | Lightweight PyTorch-free embedder (`Xenova/all-MiniLM-L6-v2`) | `02-vector-search/embed/` |
| huggingface_hub | Downloading the ONNX model | `02-vector-search/embed/download.py` |

## Agents and frameworks

| Technology | Role | Where |
|-|-|-|
| OpenAI function calling | Turning the RAG pipeline into an agent | module 1, part 2 |
| [toyaikit](https://github.com/alexeygrigorev/toyaikit) | Teaching framework for the agentic loop | module 1 |
| LangChain (`langchain`, `langchain-elasticsearch`, `langchain-huggingface`) | Production framework tour | module 6 |

## Orchestration and data ingestion

| Technology | Role | Where |
|-|-|-|
| [Kestra](https://kestra.io/) (v1.3.21) | AI workflow orchestration: RAG flows, agents, multi-agent systems, AI Copilot | module 3 (YAML flows in `flows/`, Docker Compose setup) |
| PostgreSQL 18 | Kestra's backing store | `03-orchestration/docker-compose.yml` |
| [dlt](https://dlthub.com/) | Pulling LLM traces from a monitoring service for analytics | 2026 data-ingestion workshop |

## Evaluation

| Technology | Role | Where |
|-|-|-|
| pandas, tqdm | Working with ground-truth data and batch runs | module 4 |
| Hit Rate, MRR | Retrieval metrics | module 4 |
| LLM-as-a-judge | Answer-quality evaluation (offline in module 4, online in module 5) | modules 4, 5 |

## Monitoring and app layer

| Technology | Role | Where |
|-|-|-|
| Streamlit | Chat app (`app.py`) and metrics dashboard (`dashboard.py`) | module 5 |
| PostgreSQL 17 | Storing conversations and feedback | module 5 (`make postgres`) |
| Grafana | Production monitoring dashboards over the same tables | modules 5, 7 |
| Flask | API interface in the fitness-assistant project example | module 7 |

## Datasets

| Dataset | Role | Where |
|-|-|-|
| DataTalks.Club course FAQ (`https://datatalks.club/faq/json/courses.json`) | The shared corpus indexed and queried throughout the course | modules 1, 2, 4, 5 |
| Exercise dataset | Corpus for the fitness-assistant project example | module 7 |
