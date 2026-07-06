"""Phase B: the four-step RAG pipeline - search, context, prompt, LLM.

Same shape as the course's RAGBase, with ChromaDB as the index.
Chroma embeds the query with the same embedding function it used at
indexing time, so the same-model rule is handled for us.

Run: uv run python rag.py "How do I join the course?"
     uv run python rag.py --show-prompt "How do I join the course?"
"""

import sys

import chromadb
from dotenv import load_dotenv
from openai import OpenAI

from config import CHROMA_DIR, COLLECTION_NAME, MODEL, TOP_K

INSTRUCTIONS = """
Your task is to answer questions from course participants based on
the provided context. Use only the context to answer. If the answer
is not in the context, say "I don't know."
""".strip()

PROMPT_TEMPLATE = """
QUESTION: {question}

CONTEXT:
{context}
""".strip()


def get_collection():
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    return client.get_collection(COLLECTION_NAME)


def search(collection, query, top_k=TOP_K):
    results = collection.query(query_texts=[query], n_results=top_k)
    hits = []
    for i, hit_id in enumerate(results["ids"][0]):
        meta = results["metadatas"][0][i]
        hits.append(
            {
                "id": hit_id,
                "section": meta["section"],
                "question": meta["question"],
                "answer": meta["answer"],
                "distance": results["distances"][0][i],
            }
        )
    return hits


def build_context(hits):
    lines = []
    for hit in hits:
        lines.append(hit["section"])
        lines.append("Q: " + hit["question"])
        lines.append("A: " + hit["answer"])
        lines.append("")
    return "\n".join(lines).strip()


def build_prompt(query, hits):
    return PROMPT_TEMPLATE.format(question=query, context=build_context(hits))


def llm(client, prompt):
    response = client.responses.create(
        model=MODEL,
        input=[
            {"role": "developer", "content": INSTRUCTIONS},
            {"role": "user", "content": prompt},
        ],
    )
    return response.output_text


def rag(query, show_prompt=False):
    collection = get_collection()
    hits = search(collection, query)
    prompt = build_prompt(query, hits)

    if show_prompt:  # rag-starter-advice.md #4: print the prompt. always.
        print("=" * 60)
        print(prompt)
        print("=" * 60)

    load_dotenv()
    return llm(OpenAI(), prompt)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--show-prompt"]
    question = args[0] if args else "How do I join the course?"
    print(rag(question, show_prompt="--show-prompt" in sys.argv))
