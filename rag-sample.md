# Workflow of the RAG Sample App

This document explains how the course's sample RAG application works,
end to end. The core pipeline is introduced in `01-agentic-rag/code/`
and the complete runnable app — a Streamlit course assistant with
metrics, storage, an LLM judge, and a dashboard — lives in
`05-monitoring/code/`.

## The big picture

```
                ┌─────────────────────────────────────────────┐
                │              one-time ingestion             │
                │  FAQ JSON (datatalks.club) → minsearch index│
                └─────────────────────┬───────────────────────┘
                                      │
user question → Streamlit app (app.py)
                  │
                  ├─ 1. search index          (RAGBase.search)
                  ├─ 2. build context+prompt  (RAGBase.build_prompt)
                  ├─ 3. call the LLM          (RAGWithMetrics.llm)
                  │      └─ records time, tokens, cost
                  ├─ 4. show answer + metrics to the user
                  ├─ 5. save conversation → PostgreSQL
                  ├─ 6. LLM judge scores relevance → feedback table
                  └─ 7. user clicks +1 / -1   → feedback table
                                      │
                       dashboard.py reads PostgreSQL
                       (stats, cost/latency charts)
```

## 1. Ingestion (`ingest.py`)

`load_faq_data()` downloads the DataTalks.Club course FAQ dataset:
first the course list from `https://datatalks.club/faq/json/courses.json`,
then each course's FAQ documents. Every document has `question`,
`section`, `answer`, and `course` fields.

`build_index(documents)` indexes them with **minsearch**, an in-memory
keyword search engine: `question`, `section`, and `answer` are text
fields; `course` is a keyword field used for exact filtering. The index
is rebuilt from the live FAQ on every app start — there is no local
data store for documents.

## 2. The core RAG pipeline (`rag_helper.py`)

`RAGBase` wires the four classic RAG steps together. `rag(query)` is
the entry point:

1. **`search(query)`** queries the minsearch index for the top 5
   documents, filtered to one course (`llm-zoomcamp` by default) and
   boosted so that matches in `question` count 3x and matches in
   `section` count 0.5x relative to `answer`.
2. **`build_context(search_results)`** flattens the hits into a plain
   text block of `section / Q: ... / A: ...` entries.
3. **`build_prompt(query, search_results)`** inserts the user question
   and that context into `PROMPT_TEMPLATE`.
4. **`llm(prompt)`** sends two messages to the OpenAI Responses API
   (`gpt-5.4-mini` by default): a `developer` message with the standing
   instructions ("answer from the context; say 'I don't know'
   otherwise") and a `user` message with the prompt. The model's
   `output_text` is the answer.

This is deliberately a *fixed* pipeline: search always runs exactly
once before the LLM call. (Module 1's later lessons turn the same
pieces into an agent by exposing `search` as a tool the LLM can decide
to call; the monitoring app uses the fixed pipeline.)

## 3. Metrics instrumentation (`metrics.py`)

`RAGWithMetrics` subclasses `RAGBase` and overrides only `llm()`. Each
call is timed and its `response.usage` is converted into an
`LLMCallRecord` dataclass: model, prompt, instructions, answer, prompt/
completion/total tokens, response time, and dollar cost (computed from
per-token pricing in `calculate_cost`). The record is kept on
`assistant.last_call` so the UI and storage layer can pick it up after
each question.

`assistant.py` is the factory and CLI: `create_assistant()` loads
`.env`, ingests the FAQ, builds the index, and returns a
`RAGWithMetrics` instance. Run directly (`make run`), it answers one
question from the command line and saves the conversation.

## 4. The chat app (`app.py`)

The Streamlit app (`make chat`) drives one full request cycle per
"Ask" click:

1. `assistant.rag(user_input)` produces the answer.
2. The answer plus the metrics from `assistant.last_call` (response
   time, tokens, cost) are displayed.
3. `save_conversation()` inserts the full record into the
   `conversations` table and returns its id, which is kept in
   `st.session_state` so later feedback can reference it.
4. `evaluate_relevance()` (`judge.py`) immediately asks a second LLM to
   classify the answer as `RELEVANT` / `PARTLY_RELEVANT` /
   `NON_RELEVANT` with an explanation, using structured output
   validated by a Pydantic model (with retry via
   `evaluation_utils.llm_structured_retry`). The verdict is stored in
   the `feedback` table with `source = "judge"`.
5. The **+1 / -1** buttons store explicit user feedback for the same
   conversation with `source = "user"` and a numeric score.

So every conversation gets two kinds of online evaluation: an
automatic LLM-as-a-judge verdict and optional human thumbs up/down —
distinguishable by the `source` column.

## 5. Storage (`db_init.py`, `db_save.py`, `db_feedback.py`)

PostgreSQL (started with `make postgres`, a `postgres:17` container)
holds two tables:

- **`conversations`** — one row per question: question, answer, course,
  model, instructions, full prompt, token counts, response time, cost,
  timestamp.
- **`feedback`** — one row per evaluation, referencing
  `conversations.id`: `source` (`judge` or `user`), the judge's
  `relevance`/`explanation`, or the user's `score`.

`db_init.py` creates both tables; connection settings come from
`POSTGRES_*` environment variables with local-dev defaults.

## 6. Monitoring (`dashboard.py`, `db_query.py`)

`dashboard.py` is a second Streamlit app that reads the stored data
back via `db_query.py`: headline stats (total conversations, average
response time, total cost, average tokens), cost-over-time and
latency-over-time line charts, and a list of recent conversations.
Module 5's later lessons replace/augment this with Grafana dashboards
over the same tables, and `generate_data.py` can synthesize traffic so
the dashboards have something to show.

## Running it

From `05-monitoring/code/` (a self-contained uv project, needs
`OPENAI_API_KEY` in `.env`):

```bash
make postgres              # start PostgreSQL in Docker
uv run python db_init.py   # create the tables
make chat                  # Streamlit chat app (app.py)
make run                   # or: one-shot CLI query (assistant.py)
uv run streamlit run dashboard.py   # metrics dashboard
```
