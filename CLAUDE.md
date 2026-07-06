# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

The DataTalksClub **LLM Zoomcamp** course: a free 10-week course on building
LLM applications with RAG, agents, and vector search. This repo holds the
course *content* — markdown lessons, Jupyter notebooks, and small example
code projects — not a single deployable application. Changes are typically
edits to lesson text, notebooks, homework, or example code, contributed via
PRs to `DataTalksClub/llm-zoomcamp`.

## Repository layout

- `01-agentic-rag/` … `07-project-example/` — the **current (2026) course
  modules**. Each module has:
  - `README.md` — module overview plus an ordered, linked lesson index with
    one-line descriptions. Keep it in sync when adding/renaming lessons.
  - `lessons/NN-name.md` — numbered lesson write-ups.
  - `code/` (most modules) — a self-contained example project with notebooks
    and scripts.
- `cohorts/2026/` — the current cohort: homework lives at
  `cohorts/2026/<module>/homework.md` (module READMEs link there).
- `cohorts/2024/`, `cohorts/2025/` — **archived** materials from earlier
  cohorts that taught modules differently. Don't update these when changing
  current content; they are historical.
- `awesome-llms.md` — curated list of LLM providers/tools.
- `project.md` — capstone project guidelines.
- `docs/README.md` — pointer only; the video-production tooling moved to the
  separate `youtube-manager-agent` repo.

Several files (`rag_helper.py`, `ingest.py`, `evaluation_utils.py`) are
intentionally duplicated across module `code/` dirs — each module's code is
meant to stand alone for students; don't "deduplicate" them.

## Running the code

There is no build, test suite, or linter. Each module's `code/` directory is
an independent **uv** project (`pyproject.toml`, Python >= 3.12):

```bash
cd 04-evaluation/code
uv sync                     # install deps (04-evaluation has a uv.lock)
uv run jupyter notebook     # notebooks are the main artifact
uv run python ingest.py     # scripts
```

API keys go in a `.env` file (loaded with `python-dotenv`), primarily
`OPENAI_API_KEY`. Lessons also support OpenAI-compatible providers (Groq,
Gemini, Ollama) via `base_url`. Never commit `.env`.

Module-specific:

- **03-orchestration (Kestra):** `docker-compose up` in `03-orchestration/`
  starts Kestra (UI at `localhost:8080`, login `admin@kestra.io` /
  `Admin1234!`) plus Postgres. Expects `SECRET_OPENAI_API_KEY`,
  `SECRET_GEMINI_API_KEY`, `SECRET_TAVILY_API_KEY` in the environment.
  Lessons are backed by YAML flows in `flows/`, not Python.
- **05-monitoring:** `Makefile` targets — `make chat` (Streamlit chat app),
  `make run` (assistant CLI), `make postgres` (Postgres 17 in Docker on the
  `monitoring` network), `make query`.

The teaching stack across modules: `minsearch` (in-memory search) →
`sqlitesearch` (persistent) → PGVector; `openai` client; `toyaikit`
(teaching agent framework, module 1); `sentence-transformers` and an ONNX
embedder (`02-vector-search/embed/`). All modules use the same course FAQ
dataset.

## Content conventions

- Lessons start with a `Video: [Watch this lesson](...)` link and end with
  prev/next navigation like `[← Environment](02-environment.md) | [Dataset →](04-dataset.md)`.
  Preserve both when editing, and fix neighbors' links when inserting or
  renumbering lessons.
- Lesson prose is hand-wrapped at roughly 70–75 characters; match that when
  editing.
- Module READMEs (and the root README) end with a community **Notes**
  section ("Add your notes above this line") where students PR links to
  their own notes — append, don't reorganize.
- The root `README.md` syllabus links each module and the cohort homework;
  update it if modules are added or renamed.
