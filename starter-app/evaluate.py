"""Phase C: retrieval evaluation - Hit Rate@k and MRR.

Two modes:

  uv run python evaluate.py --generate 25
      Sample 25 indexed docs and have the LLM write one user-style
      question per doc. Saves eval/questions.json - commit that file:
      it's your frozen eval set (rag-starter-advice.md #6).

  uv run python evaluate.py
      Run retrieval over the frozen questions and report Hit Rate@k
      and MRR. Retrieval-only: no generation cost per run.
"""

import json
import random
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from config import EVAL_FILE, MODEL, TOP_K
from rag import get_collection, search

GENERATE_PROMPT = """
You are a student in an online course. Below is an FAQ entry.
Write ONE question a student might ask that this entry answers.
Do not copy the original question - paraphrase, as a real user would.
Reply with the question only, no quotes, no explanation.

SECTION: {section}
Q: {question}
A: {answer}
""".strip()


def generate_eval_set(n):
    collection = get_collection()
    records = collection.get(include=["metadatas"])
    population = list(zip(records["ids"], records["metadatas"]))
    sample = random.sample(population, min(n, len(population)))

    load_dotenv()
    client = OpenAI()

    entries = []
    for doc_id, meta in sample:
        prompt = GENERATE_PROMPT.format(
            section=meta["section"], question=meta["question"], answer=meta["answer"]
        )
        response = client.responses.create(
            model=MODEL, input=[{"role": "user", "content": prompt}]
        )
        question = response.output_text.strip()
        entries.append({"question": question, "doc_id": doc_id})
        print(f"[{len(entries)}/{len(sample)}] {question}")

    path = Path(EVAL_FILE)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(entries, indent=2), encoding="utf-8")
    print(f"\nwrote {len(entries)} questions -> {EVAL_FILE} (commit this file)")


def run_eval():
    entries = json.loads(Path(EVAL_FILE).read_text(encoding="utf-8"))
    collection = get_collection()

    hits = 0
    reciprocal_ranks = []
    for entry in entries:
        result_ids = [h["id"] for h in search(collection, entry["question"], TOP_K)]
        if entry["doc_id"] in result_ids:
            hits += 1
            reciprocal_ranks.append(1 / (result_ids.index(entry["doc_id"]) + 1))
        else:
            reciprocal_ranks.append(0.0)
            print(f"MISS: {entry['question']}")

    n = len(entries)
    print(f"\nquestions:      {n}")
    print(f"hit rate@{TOP_K}:     {hits / n:.3f}  ({hits}/{n})")
    print(f"MRR:            {sum(reciprocal_ranks) / n:.3f}")


if __name__ == "__main__":
    if "--generate" in sys.argv:
        idx = sys.argv.index("--generate")
        count = int(sys.argv[idx + 1]) if len(sys.argv) > idx + 1 else 25
        generate_eval_set(count)
    else:
        run_eval()
