# RAG Production App

[![Last Commit](https://img.shields.io/github/last-commit/kashif-alam/rag_production_app?label=Last%20Commit\&style=flat-square)](https://github.com/kashif-alam/rag_production_app/commits/main) [![Python](https://img.shields.io/badge/Python-92.3%25-3776AB?style=flat-square\&logo=python\&logoColor=white)](https://github.com/kashif-alam/rag_production_app/search?l=python) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)

---

> **Turn PDFs into conversational knowledge — fast, reliable, and production-ready.**

RAG Production App is an opinionated, production-focused reference implementation for building retrieval-augmented generation (RAG) systems over PDF documentation. It provides clean ingestion pipelines, robust embedding orchestration, and a developer-friendly UI to enable fast iteration and reliable deployments.

---

## Table of Contents

* [Highlights](#highlights)
* [Quick Start](#quick-start)
* [Principles & Design](#principles--design)
* [Architecture](#architecture)
* [Installation](#installation)
* [Configuration](#configuration)
* [Running the App](#running-the-app)
* [Testing](#testing)
* [Production Considerations](#production-considerations)
* [Contributing](#contributing)
* [Support & Contact](#support--contact)
* [License](#license)

---

## Highlights

* **Robust PDF ingestion** with intelligent chunking and metadata extraction.
* **Scalable embeddings pipeline** using OpenAI (with batching, retry/backoff, and rate-limit handling).
* **Vector storage** with Qdrant for low-latency semantic search.
* **FastAPI backend** with event-driven ingestion (Inngest) for background processing.
* **Streamlit frontend** for quick exploration, QA, and developer demos.
* **Tested & extensible**: `pytest`-driven test-suite and modular code structure.

---

## Quick Start

1. Clone the repository:

```bash
git clone https://github.com/kashif-alam/rag_production_app.git
cd rag_production_app
```

2. Create a virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

3. Create a `.env` file (see [Configuration](#configuration)).

4. Start the backend and frontend:

```bash
# Backend (FastAPI)
uv run uvicorn main:app --reload

# Frontend (Streamlit)
streamlit run app.py
```

Open the Streamlit URL to upload PDFs and ask questions.

---

## Principles & Design

This repository follows pragmatic production guidelines:

* **Observability first** — add logging, metrics, and traces (recommended: Prometheus + Grafana).
* **Resiliency** — graceful retries, exponential backoff, idempotent ingestion, and atomic storage operations.
* **Separation of concerns** — ingestion, embedding, and query layers are pluggable.
* **Security & secrets** — keep API keys and credentials out of source control; use `.env` or a secret manager in production.

---

## Architecture

```
[Client] -> Streamlit UI
   |            |
   v            v
[FastAPI] ----> [Inngest Worker] -> [Embedding Service (OpenAI)]
                      |
                      v
                  [Qdrant Vector DB]
                      |
                      v
                  [Query / RAG Generator]
```

* **FastAPI** exposes endpoints for ingesting files and querying documents.
* **Inngest** handles background tasks (long-running PDF parsing and embedding).
* **OpenAI embeddings** produce dense vectors for semantic retrieval.
* **Qdrant** stores vectors and supports fast nearest-neighbor searches used during query time.

---

## Installation

See Quick Start for local setup. For typical development you'll want to install extras for testing and linting:

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # if present
```

---

## Configuration

Create a `.env` in the project root with at least the following keys:

```env
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxx
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=optional_key_if_used
INNGEST_API_KEY=optional_inngest_key
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8000
```

> **Tip:** In production use a secret manager (AWS Secrets Manager, GCP Secret Manager, Vault) rather than plaintext `.env` files.

---

## Running the App

### Backend (FastAPI)

```bash
uv run uvicorn main:app --host $FASTAPI_HOST --port $FASTAPI_PORT --reload
```

The backend exposes endpoints for:

* `POST /ingest` — upload a PDF to ingest and index
* `POST /query` — query indexed documents

### Frontend (Streamlit)

```bash
streamlit run app.py
```

Streamlit provides a simple UI for uploading PDFs and running conversational queries against indexed content.

---

## Example API Requests

**Ingest a PDF**

```bash
curl -X POST "http://localhost:8000/ingest" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -F "file=@/path/to/manual.pdf"
```

**Query the index**

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"query":"What safety procedures are recommended for Model X?"}'
```

Adjust headers and authentication to match your deployment.

---

## Testing

Run unit and integration tests with `pytest`:

```bash
pytest -q
```

* Tests that require external services (OpenAI, Qdrant) should be marked and run separately, or configured to use test doubles / fixtures.

---

## Production Considerations

* **Scaling**: Run Qdrant in a cluster for high-throughput and shard/replica needs.
* **Costs**: Monitor embedding usage (API calls to OpenAI) and batch requests where possible.
* **Security**: Validate and sanitize uploads; enforce file-size limits and scan for malware in production.
* **Observability**: Instrument requests, background jobs, and DB calls. Export metrics and set alerts.
* **Backups**: Regularly snapshot Qdrant data and retain raw PDFs in durable storage (S3 / GCS).

---

## Troubleshooting

* **Embeddings fail / rate limited**: Implement exponential backoff and request batching. Ensure API keys are valid and quota is sufficient.
* **Qdrant errors**: Check connectivity, index health, and resource limits (RAM/CPU). Confirm `QDRANT_URL` and API key.
* **Streamlit issues**: Check console logs and browser devtools for CORS or JS errors.

---

## Contributing

Contributions are welcome. Suggested workflow:

1. Fork the repo and create a feature branch: `git checkout -b feature/your-feature`
2. Open a draft PR describing the change and tests.
3. Keep PRs focused and include tests for new behavior.

Please follow these standards:

* Use `black` or `ruff` for formatting/linting.
* Write unit tests and document public APIs.
* Significantly disruptive changes should be discussed in an Issue first.

---

## Support & Contact

If you find a bug or have a feature request, please open an Issue on GitHub. For design discussions, start a new issue and tag maintainers.

---

## License

This project is distributed under the MIT License. See the [LICENSE](LICENSE) file for full details.

---

**Made with ❤️ · RAG Production App**