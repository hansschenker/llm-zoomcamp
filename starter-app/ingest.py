"""Phase A: load the corpus and index it into embedded ChromaDB.

The corpus is the DataTalks.Club course FAQ - naturally chunked
(one Q&A entry per chunk, no splitter needed) and small enough to
re-index in seconds. To use your own corpus later, replace
load_faq_documents() with a loader that returns dicts with
question/answer/section/course keys (Docling goes here eventually).

Run: uv run python ingest.py
"""

import hashlib

import chromadb
import requests

from config import CHROMA_DIR, COLLECTION_NAME, COURSE

DOCS_URL = "https://datatalks.club/faq/json/courses.json"
URL_PREFIX = "https://datatalks.club/faq"

BATCH_SIZE = 100


def load_faq_documents(course=COURSE):
    courses = requests.get(DOCS_URL, timeout=30).json()

    documents = []
    for c in courses:
        course_docs = requests.get(f"{URL_PREFIX}{c['path']}", timeout=30)
        course_docs.raise_for_status()
        documents.extend(course_docs.json())

    if course is not None:
        documents = [d for d in documents if d["course"] == course]
    return documents


def doc_id(doc):
    key = f"{doc['course']}|{doc['question']}"
    return hashlib.md5(key.encode("utf-8")).hexdigest()


def index_documents(documents):
    client = chromadb.PersistentClient(path=CHROMA_DIR)

    # Recreate for a clean re-index; cheap at this corpus size.
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    collection = client.create_collection(COLLECTION_NAME)

    for start in range(0, len(documents), BATCH_SIZE):
        batch = documents[start : start + BATCH_SIZE]
        collection.add(
            ids=[doc_id(d) for d in batch],
            documents=[f"{d['question']}\n{d['answer']}" for d in batch],
            metadatas=[
                {
                    "course": d["course"],
                    "section": d["section"],
                    "question": d["question"],
                    "answer": d["answer"],
                }
                for d in batch
            ],
        )
        print(f"indexed {min(start + BATCH_SIZE, len(documents))}/{len(documents)}")

    return collection


if __name__ == "__main__":
    docs = load_faq_documents()
    print(f"loaded {len(docs)} documents for course={COURSE!r}")
    index_documents(docs)
    print(f"done -> {CHROMA_DIR}/ collection={COLLECTION_NAME!r}")
