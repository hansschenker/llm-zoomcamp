# Python Learning Path for RAG Development

What Python to learn (and what to skip) for building RAG apps with the
[Python toolchain](python-toolchain.md), coming from a TypeScript
background. Scope caveat: this is not "advanced Python" in the general
sense — it's a fairly small subset that RAG code actually exercises,
and most of it is renaming concepts TypeScript already has.

## The workhorses — worth deliberate practice

- **Dicts and lists of dicts** (the "kv store" of Python). The entire
  course dataset is `list[dict]` (documents with
  `question`/`answer`/`course` keys); search results, prompts, and API
  payloads all flow through this shape. `dict.get()`, unpacking, and
  merging are daily tools.
- **Comprehensions and generator expressions** — Python's replacement
  for `map`/`filter` chains:
  `[d for d in docs if d["course"] == course]`, and the idiom
  `next(b.text for b in response.content if b.type == "text")` appears
  constantly in LLM client code.
- **f-strings and `.format()`** — prompt building is string assembly;
  `PROMPT_TEMPLATE.format(question=..., context=...)` is the heart of
  the prompt-building step.
- **Plain classes with inheritance** — the course's key pattern is
  `RAGWithMetrics(RAGBase)` overriding one method. That's the whole OO
  surface you need.
- **Dataclasses and Pydantic** — `@dataclass` for records like
  `LLMCallRecord`, Pydantic for validated LLM outputs. Pydantic is Zod
  with the arrow pointing the other way (class → schema instead of
  schema → type).
- **Context managers** — `with open(...)`,
  `with conn.cursor() as cur`, `with client.messages.stream(...)`.
  TypeScript's `try/finally` (or `using`) with nicer syntax.
- **Type hints** — modern Python code is annotated; coming from TS
  you'll want this anyway, and it makes the ecosystem feel much less
  foreign.

## Worth knowing — lighter touch

- `enumerate` / `zip`
- `*args` / `**kwargs` (Python's options-object equivalent)
- Modules and imports
- Enough pandas to slice an evaluation DataFrame

## Explicitly skip for now

- **asyncio** — the entire course codebase is synchronous (a genuine
  relief coming from JS); you only meet async when you adopt FastAPI
- Writing decorators (using them is enough)
- Metaclasses
- Threading / GIL lore
- Performance tuning

None of it appears anywhere in the RAG path.

## TS → Python translation table

| TypeScript | Python |
|-|-|
| object / `Map` | `dict` |
| `array.map(...).filter(...)` | list comprehension |
| template literal | f-string |
| interface + constructor | `@dataclass` |
| Zod schema → inferred type | Pydantic class → schema |
| options object | `**kwargs` |
| `try/finally`, `using` | `with` (context manager) |
| `camelCase` | `snake_case` |

## How to learn it

Skip a general Python course — the llm-zoomcamp repo is the syllabus:

1. Retype `rag_helper.py`, `ingest.py`, and `metrics.py` yourself
   (don't copy-paste) — that covers dicts, classes, inheritance,
   f-strings, and dataclasses in context.
2. Do module 4's evaluation notebooks by hand — comprehensions,
   pandas, Pydantic, and tqdm in context.
3. Build the first own app per
   [toolchain-recommendation.md](toolchain-recommendation.md).

A week of that beats a month of abstract exercises, because RAG code
is honestly not advanced Python — it's intermediate Python used
confidently.
