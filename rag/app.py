import streamlit as st
import subprocess

st.title("AI Code Helper (AST + RAG)")

file = st.file_uploader("Upload Python file", type=["py"])

if file:
    with open("TEMP.py", "wb") as f:
        f.write(file.read())

    if st.button("Index File"):
        subprocess.run(["python", "rag_query.py", "index", "TEMP.py"])
        st.success("Indexed")

question = st.text_input("Ask question")

if question:
    res = subprocess.run(
        ["python", "rag_query.py", "ask", question],
        capture_output=True,
        text=True
    )
    st.write(res.stdout)
