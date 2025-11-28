🚀 Contract Intelligence RAG System — README.md
📘 Contract Intelligence RAG System

A fully-functional LLM-powered Contract Intelligence System built using:

FastAPI (Backend Framework)

FAISS (Vector Database)

HuggingFace Embeddings (intfloat/multilingual-e5-base)

Groq Llama-3.3-70B (LLM for Q&A, Extraction, Audit)

PostgreSQL (Document Storage)

PyPDF2 (PDF Text Extraction)

This system supports:

✅ Contract Ingestion
✅ Contract Information Extraction (structured fields)
✅ RAG-based Question Answering with citations
✅ Contract Risk Auditing (clause severity, evidence, remediation)
✅ SSE Streaming for real-time answers
✅ Admin Metrics + Health Check

🧱 Architecture Overview
          ┌──────────────────┐
          │   PDF Upload     │
          └────────┬─────────┘
                   │
                   ▼
          ┌──────────────────┐
          │  Ingest Service  │
          │ - PyPDF2         │
          │ - Chunking       │
          │ - Metadata       │
          └────────┬─────────┘
                   │
         ┌─────────┴──────────┐
         ▼                    ▼
 ┌─────────────────┐   ┌─────────────────┐
 │ PostgreSQL DB   │   │ FAISS Vector DB │
 │ (full text)     │   │ (embeddings)    │
 └─────────────────┘   └─────────────────┘
                   │
                   ▼
         ┌────────────────────┐
         │ RAG Engine + LLM   │
         │ - Groq Llama-70B   │
         │ - Context Builder  │
         └────────┬───────────┘
                  │
 ┌────────────────┴─────────────────┐
 │ /ask     – Q&A + citations       │
 │ /extract – structured fields     │
 │ /audit   – contract risk analysis│
 └──────────────────────────────────┘

🛠 Tech Stack
Component	Technology
Backend	FastAPI
LLM	Groq Llama-3.3-70B
Embeddings	intfloat/multilingual-e5-base
Vector DB	FAISS
Database	PostgreSQL
PDF Parsing	PyPDF2
Streaming	SSE (Server Sent Events)
📦 Project Setup
1. Clone Repo
git clone https://github.com/<username>/<repo>.git
cd contract-intelligence

2. Create Virtual Environment
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
.venv\Scripts\activate      # Windows

3. Install Requirements
pip install -r requirements.txt

4. Setup PostgreSQL

Create a database:

CREATE DATABASE contractdb;

5. Create .env File

Inside project root:

POSTGRES_URL=postgresql://postgres:<password>@localhost:5432/contractdb
GROQ_API_KEY=xxxxxxxxxxxxxxxxxxxx

▶️ Run FastAPI Server
uvicorn app.main:app --reload


Server will start at:

👉 http://127.0.0.1:8000

👉 Docs: http://127.0.0.1:8000/docs

🐳 Docker Setup
Build Image
docker build -t contract-intel .

Run Container
docker run -p 8000:8000 --env-file .env contract-intel

🔌 API Endpoints
✔ /ingest — Upload + Process Contract

Method: POST
Type: multipart/form-data (PDF)

Stores:

full text in PostgreSQL

chunk embeddings to FAISS

📄 Code Ref: ingest.py

Example CURL
curl -X POST "http://localhost:8000/ingest/" \
  -F "file=@sample.pdf"

✔ /ask — RAG Question Answering

Returns:

LLM answer

citations (page, char start/end)

📄 Code Ref: ask.py

Example CURL
curl -X POST "http://localhost:8000/ask/" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the governing law?"}'

✔ /ask/stream — Streaming RAG Answer (SSE)
curl http://localhost:8000/ask/stream?question=What+is+the+payment+term

✔ /extract — Extract Structured Fields

📄 Code Ref: extract.py

Extracts:

parties

effective_date

governing_law

term

payment terms

indemnity

liability cap

signatories

auto renewal

confidentiality

Example CURL
curl -X POST "http://localhost:8000/extract/" \
  -d "document_id=1"

✔ /audit — Contract Risk Analysis

📄 Code Ref: audit.py

Returns risk JSON:

severity

clause

evidence text

char indexes

page number

remediation

confidence

Example CURL
curl -X POST "http://localhost:8000/audit/" \
  -H "Content-Type: application/json" \
  -d '{"document_id": 1}'

✔ /admin/metrics

Shows API usage counts:

ingest_count

extract_count

ask_count

audit_count

uptime

✔ /healthz

Health check endpoint
📄 Code Ref: admin.py

📂 Project Structure
app/
│── api/
│   ├── ingest.py
│   ├── ask.py
│   ├── extract.py
│   ├── audit.py
│   └── admin.py
│
│── services/
│   ├── rag_engine.py
│   ├── text_splitter.py
│   ├── llm_extractor.py
│
│── db/
│   ├── models.py
│   ├── crud.py
│   ├── connection.py
│
│── main.py
│── config.py

⚠️ Trade-offs & Decisions
1. FAISS over PGVector

✔ Faster
✔ Lightweight
✔ Local index
✖ Not distributed horizontally

2. Groq Llama-3.3-70B

✔ Extremely fast inference
✔ High accuracy
✖ Requires API key

3. PyPDF2 for extraction

✔ Simple
✖ Less accurate for complex PDFs (tables, scanned docs)

4. Character Index Based Citations

✔ Exact pinpointing
✔ Helpful for UI highlighting
✖ Dependent on clean PDF text

5. JSON Schema Force Prompts

✔ Reliable outputs
✖ Needs fallback JSON cleaning

🧪 Testing Tips
Reset vectorstore
rm -rf vectorstore

Reset DB
DROP TABLE documents;

🎯 Conclusion

This system is a full production-grade Contract Intelligence pipeline supporting:

Vector-based retrieval

LLM Q&A

Structured extraction

Risk auditing

Streaming answers

Monitoring

It is scalable, modular, and easily deployable with Docker.
