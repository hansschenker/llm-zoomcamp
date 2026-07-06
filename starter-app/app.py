"""Streamlit chat UI over the RAG pipeline.

Shows the answer plus - per rag-starter-advice.md #4 - the retrieved
chunks and the full assembled prompt, so every query is debuggable.

Run: uv run streamlit run app.py
"""

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

from rag import build_prompt, get_collection, llm, search

st.title("RAG Starter")

question = st.text_input("Ask a question about the course:")

if st.button("Ask") and question:
    with st.spinner("Retrieving and generating..."):
        collection = get_collection()
        hits = search(collection, question)
        prompt = build_prompt(question, hits)

        load_dotenv()
        answer = llm(OpenAI(), prompt)

    st.markdown("### Answer")
    st.write(answer)

    with st.expander(f"Retrieved chunks ({len(hits)})"):
        for i, hit in enumerate(hits, 1):
            st.markdown(f"**{i}. {hit['question']}**  \n"
                        f"*{hit['section']}* — distance {hit['distance']:.3f}")
            st.text(hit["answer"])
            st.divider()

    with st.expander("Full prompt sent to the LLM"):
        st.text(prompt)
