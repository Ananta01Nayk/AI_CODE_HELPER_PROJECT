# ai_code_brain.py
import os
import json
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from build_code_memory import build
from extract_code_knowledge import extract
from sentence_transformers import SentenceTransformer
from langchain_core.embeddings import Embeddings

load_dotenv()

BASE = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE, "DATA")
VECTOR_DIR = os.path.join(DATA_DIR, "VECTOR_DB")
META_FILE = os.path.join(DATA_DIR, "last_file.json")


#EMBEDDINGS

class LocalEmbeddings(Embeddings):
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def embed_documents(self, texts):
        return self.model.encode(texts).tolist()

    def embed_query(self, text):
        return self.model.encode([text])[0].tolist()


#LLM

llm = ChatGoogleGenerativeAI(
    model="models/gemini-2.5-flash",
    api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0
)


#MAIN PIPELINE

def process_and_ask(file_path: str, question: str) -> str:
    os.makedirs(DATA_DIR, exist_ok=True)

    previous_file = None
    if os.path.exists(META_FILE):
        previous_file = json.load(open(META_FILE)).get("file")

    needs_rebuild = (
        not os.path.exists(VECTOR_DIR)
        or not os.path.exists(os.path.join(VECTOR_DIR, "index.faiss"))
        or previous_file != file_path
    )

    if needs_rebuild:
        extract(file_path)
        build()
        json.dump({"file": file_path}, open(META_FILE, "w"))

    embeddings = LocalEmbeddings()

    db = FAISS.load_local(
        VECTOR_DIR,
        embeddings=embeddings,
        allow_dangerous_deserialization=True
    )

    docs = db.similarity_search(question, k=4)
    context = "\n\n".join(d.page_content for d in docs)

    prompt = f"""
You are a senior execution-aware Python engineer reviewing a real production codebase.

Your task is to answer strictly based on the provided code context.

Rules (MANDATORY):
- Use ONLY the given context (do not assume or guess)
- Clearly mention:
  • file path(s)
  • function name(s)
  • class name(s) if present
  • exact line number ranges
- Explain the EXECUTION FLOW step-by-step (entry point → calls → outcomes)
- If the file is a config, utility, or hook, explain its ROLE in the system
- If information is missing, explicitly say: "Not present in the provided context"
- Do NOT hallucinate or invent logic

Response Structure (FOLLOW THIS ORDER):
1. File Overview
2. Key Functions / Classes
3. Execution Flow (bullet points, sequential)
4. Dependencies & Call Relationships
5. Observations or Limitations (if any)

CODE CONTEXT:
{context}

QUESTION:
{question}
"""


    return llm.invoke(prompt).content
