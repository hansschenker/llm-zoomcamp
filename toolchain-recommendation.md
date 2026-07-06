# Toolchain Recommendation

Which of the two toolchains ([python-toolchain.md](python-toolchain.md)
vs [javascript-toolchain.md](javascript-toolchain.md)) to use for our
own RAG apps.

**Recommendation: start with the Python toolchain, and plan to
graduate to the hybrid split. Don't pick the pure TypeScript chain.**

## For the first app: pure Python

Three things stack up in its favor:

1. **Everything we're learning from is Python** — the course code,
   `rag_helper.py`, the evaluation notebooks — so every concept
   transfers directly instead of being translated.
2. **The two most consequential tools only fully work there.** IBM
   Docling has no JS version, and ChromaDB's embedded mode (no server,
   just a directory) is Python-only — in TypeScript you're running
   Docker before you've indexed a single document.
3. **Phase C is where RAG apps are won**, and evaluation work
   (ground-truth generation, Hit Rate/MRR sweeps, judge comparisons)
   is simply more ergonomic with pandas and notebooks than with TS
   scripts and CSV files.

You can have ingest → retrieve → generate → evaluate running
end-to-end in an afternoon, with Streamlit as a good-enough UI.

## When the app grows a real front end: the hybrid

This is where a TypeScript background pays off. Keep the offline side
in Python — indexing pipeline, Docling, evaluation scripts — and build
the user-facing app in TypeScript (Next.js or Hono, streaming to the
browser).

The two halves meet at exactly two well-defined seams:

- the **Chroma server** holding the index
- the **Postgres tables** holding conversations and feedback

Neither side needs to know the other's internals. The online half also
ports naturally to Cloudflare Workers + Vectorize later for edge
deployment.

## Why not pure TypeScript

You'd spend the effort on the weakest links: substituting for Docling
with per-format parsers or a paid parsing API, running infrastructure
Python doesn't need, and doing evaluation in an ecosystem with no real
data-analysis tooling.

The one scenario that reverses this advice: the app is the product and
the corpus is trivial (a few markdown files, no PDFs, no heavy eval) —
then a single TS codebase's simplicity wins.

## In one line

Python end-to-end now; when the "real" UI comes, keep Python as the
kitchen and let TypeScript run the dining room.
