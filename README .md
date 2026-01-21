# AI Code Helper – VS Code RAG-Based Code Intelligence

## Overview
AI Code Helper is a VS Code extension integrated with a Python-based RAG (Retrieval-Augmented Generation) system.
It answers developer questions strictly based on the selected file using AST-based static analysis and vector retrieval.

---

## Key Features
- File-aware code analysis (no guessing)
- AST-based extraction
- JSON-based code knowledge
- Local embeddings (SentenceTransformers)
- FAISS vector database
- CLI-based Python pipeline
- VS Code chat UI

---

## Architecture
VS Code UI  
→ VS Code Extension  
→ Python CLI  
→ AST Extraction  
→ JSON  
→ Embeddings  
→ FAISS  
→ LLM  
→ Answer

---

## Project Structure
AI_CODE_HELPER_PROJECT/
- extension/
- rag/
  - extract_code_knowledge.py
  - build_code_memory.py
  - ai_code_brain.py
  - rag_query.py
  - DATA/

---

## Execution Flow
1. Open Python file
2. Open AI Code Helper chat
3. Ask question
4. Extension calls Python CLI
5. RAG processes file
6. Answer returned to UI

---

## Author
Ananta Nayak
