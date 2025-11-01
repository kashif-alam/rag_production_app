import asyncio
from pathlib import Path
import time

import streamlit as st
import inngest
from dotenv import load_dotenv
import os
import requests

load_dotenv()

# Custom CSS for professional styling
st.markdown("""
    <style>
    /* General styling */
    .stApp {
        background-color: #f8f9fc;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        max-width: 800px;
        margin: 0 auto;
    }
    h1, h2, h3 {
        color: #2c3e50;
    }
    .stButton > button {
        background-color: #3498db;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    .stButton > button:hover {
        background-color: #2980b9;
    }
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input {
        border: 1px solid #bdc3c7;
        border-radius: 4px;
        padding: 0.5rem;
    }
    .stFileUploader label {
        color: #34495e;
        font-weight: bold;
    }
    .stFileUploader > div > div {
        border: 1px dashed #bdc3c7;
        border-radius: 4px;
        padding: 1rem;
        text-align: center;
        background-color: white;
    }
    .stFileUploader > div > button {
        background-color: #27ae60;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    .stFileUploader > div > button:hover {
        background-color: #219a52;
    }
    .stSpinner > div {
        color: #7f8c8d;
    }
    .stSuccess {
        background-color: #dff0d8;
        color: #3c763d;
        border: 1px solid #d6e9c6;
        border-radius: 4px;
        padding: 0.5rem;
    }
    .stCaption {
        color: #7f8c8d;
    }
    .divider {
        border-top: 1px solid #bdc3c7;
        margin: 1rem 0;
    }
    /* Expander styling for clean look */
    .stExpander {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .stExpander > div > button {
        font-weight: bold;
        color: #2c3e50;
    }
    /* Reduce extra padding */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    .stMarkdown {
        margin-bottom: 0.5rem;
    }
    </style>
""", unsafe_allow_html=True)

st.set_page_config(page_title="Professional RAG PDF Processor", page_icon="📄", layout="centered")

@st.cache_resource
def get_inngest_client() -> inngest.Inngest:
    return inngest.Inngest(app_id="rag_app", is_production=False)

def save_uploaded_pdf(file) -> Path:
    uploads_dir = Path("uploads")
    uploads_dir.mkdir(parents=True, exist_ok=True)
    file_path = uploads_dir / file.name
    file_bytes = file.getbuffer()
    file_path.write_bytes(file_bytes)
    return file_path

async def send_rag_ingest_event(pdf_path: Path) -> None:
    client = get_inngest_client()
    await client.send(
        inngest.Event(
            name="rag/ingest_pdf",
            data={
                "pdf_path": str(pdf_path.resolve()),
                "source_id": pdf_path.name,
            },
        )
    )

# Header
st.markdown("<h1 style='text-align: center; color: #34495e;'>Professional RAG PDF Processor</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #7f8c8d;'>Upload PDFs for ingestion and query your documents intelligently.</p>", unsafe_allow_html=True)

# Ingest Section in Expander
with st.expander("📤 Upload PDF for Ingestion", expanded=True):
    uploaded = st.file_uploader("Choose a PDF file", type=["pdf"], accept_multiple_files=False, label_visibility="collapsed")

    if uploaded is not None:
        with st.spinner("Uploading and triggering ingestion..."):
            path = save_uploaded_pdf(uploaded)
            asyncio.run(send_rag_ingest_event(path))
            time.sleep(0.3)
        st.success(f"Triggered ingestion for: {path.name}")
        st.caption("You can upload another PDF if you like.")

st.markdown("<hr class='divider'>", unsafe_allow_html=True)

# Query Section in Expander
with st.expander("❓ Query Your PDFs", expanded=True):
    async def send_rag_query_event(question: str, top_k: int) -> None:
        client = get_inngest_client()
        result = await client.send(
            inngest.Event(
                name="rag/query_pdf_ai",
                data={
                    "question": question,
                    "top_k": top_k,
                },
            )
        )
        return result[0]

    def _inngest_api_base() -> str:
        return os.getenv("INNGEST_API_BASE", "http://127.0.0.1:8288/v1")

    def fetch_runs(event_id: str) -> list[dict]:
        url = f"{_inngest_api_base()}/events/{event_id}/runs"
        resp = requests.get(url)
        resp.raise_for_status()
        data = resp.json()
        return data.get("data", [])

    def wait_for_run_output(event_id: str, timeout_s: float = 120.0, poll_interval_s: float = 0.5) -> dict:
        start = time.time()
        last_status = None
        while True:
            runs = fetch_runs(event_id)
            if runs:
                run = runs[0]
                status = run.get("status")
                last_status = status or last_status
                if status in ("Completed", "Succeeded", "Success", "Finished"):
                    return run.get("output") or {}
                if status in ("Failed", "Cancelled"):
                    raise RuntimeError(f"Function run {status}")
            if time.time() - start > timeout_s:
                raise TimeoutError(f"Timed out waiting for run output (last status: {last_status})")
            time.sleep(poll_interval_s)

    with st.form("rag_query_form"):
        question = st.text_input("Your question", placeholder="Enter your question here...", label_visibility="collapsed")
        top_k = st.number_input("Number of chunks to retrieve", min_value=1, max_value=20, value=5, step=1)
        submitted = st.form_submit_button("Submit Query")

        if submitted and question.strip():
            with st.spinner("Processing your query..."):
                event_id = asyncio.run(send_rag_query_event(question.strip(), int(top_k)))
                output = wait_for_run_output(event_id)
                answer = output.get("answer", "")
                sources = output.get("sources", [])

            st.subheader("Answer")
            st.markdown(answer or "(No answer generated)")
            if sources:
                st.caption("Referenced Sources")
                for s in sources:
                    st.markdown(f"- {s}")