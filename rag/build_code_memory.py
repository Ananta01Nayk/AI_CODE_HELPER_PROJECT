# build_code_memory.py
import json
import os
from sentence_transformers import SentenceTransformer
from langchain_community.vectorstores import FAISS
from langchain_core.embeddings import Embeddings

BASE = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE, "DATA")
VECTOR_DIR = os.path.join(DATA_DIR, "VECTOR_DB")
JSON_FILE = os.path.join(DATA_DIR, "code_knowledge.json")


class LocalSentenceEmbeddings(Embeddings):
    """
    LangChain-compatible embedding wrapper
    """

    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def embed_documents(self, texts):
        return self.model.encode(texts, show_progress_bar=False).tolist()

    def embed_query(self, text):
        return self.model.encode([text])[0].tolist()


def build():
    if not os.path.exists(JSON_FILE):
        raise RuntimeError("code_knowledge.json not found. Run extraction first.")

    knowledge = json.load(open(JSON_FILE, encoding="utf8"))

    texts = []

    for fn in knowledge.get("functions", {}).values():
        texts.append(
            f"""
TYPE: FUNCTION
NAME: {fn['name']}
FILE: {fn['file']}
LINES: {fn['start']} - {fn['end']}

CODE:
{fn['code']}
"""
        )

    for cls in knowledge.get("classes", {}).values():
        texts.append(
            f"""
TYPE: CLASS
NAME: {cls['name']}
FILE: {cls['file']}
LINES: {cls['start']} - {cls['end']}

CODE:
{cls['code']}
"""
        )

    for err in knowledge.get("syntax_errors", []):
        texts.append(
            f"""
TYPE: SYNTAX_ERROR
FILE: {err['file']}
LINE: {err['line']}
MESSAGE: {err['message']}
"""
        )

    for bug in knowledge.get("logical_bugs", []):
        texts.append(
            f"""
TYPE: LOGICAL_BUG
BUG: {bug['type']}
NAME: {bug.get('name', 'N/A')}
FILE: {bug['file']}
"""
        )

    if not texts:
        raise RuntimeError("No code content to embed.")

    embeddings = LocalSentenceEmbeddings()

    db = FAISS.from_texts(
        texts=texts,
        embedding=embeddings
    )

    os.makedirs(VECTOR_DIR, exist_ok=True)
    db.save_local(VECTOR_DIR)
