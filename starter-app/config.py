"""All tunable knobs in one place (rag-starter-advice.md #9)."""

# Corpus
COURSE = "llm-zoomcamp"  # which course's FAQ to index; None = all courses

# Vector store
CHROMA_DIR = "chroma_db"
COLLECTION_NAME = "faq"

# Retrieval
TOP_K = 5

# Generation
MODEL = "gpt-5.4-mini"

# Evaluation
EVAL_FILE = "eval/questions.json"
