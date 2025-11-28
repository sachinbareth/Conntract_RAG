# from fastapi import APIRouter, Depends, HTTPException
# from pydantic import BaseModel
# from sqlalchemy.orm import Session

# from app.db.connection import SessionLocal
# from app.db import crud

# from langchain_groq import ChatGroq
# import os
# import json

# router = APIRouter(prefix="/audit", tags=["Audit API"])

# # LLM client (GROQ_API_KEY .env me hona chahiye)
# llm = ChatGroq(
#     model_name="llama-3.3-70b-versatile",
#     api_key=os.getenv("GROQ_API_KEY"),
# )


# # ---------- Request Body Model ----------

# class AuditRequest(BaseModel):
#     document_id: int


# # ---------- DB Session Dependency ----------

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


# # ---------- Prompt Template ----------

# AUDIT_PROMPT = """
# You are a contract compliance auditor.

# Analyze ONLY the contract text below and detect risky clauses.

# Risks to detect and how to rate them:

# 1) Auto-renewal with notice period < 30 days  => severity = "HIGH"
# 2) Unlimited liability or no liability cap     => severity = "HIGH"
# 3) Broad / one-sided indemnity                 => severity = "HIGH"
# 4) Termination clause missing or unclear       => severity = "MEDIUM"
# 5) Governing law / jurisdiction missing        => severity = "MEDIUM"

# Return STRICTLY valid JSON in this format:

# {{
#   "risks": [
#     {{
#       "category": "Auto-Renewal | Liability | Indemnity | Termination | Governing Law",
#       "severity": "HIGH" | "MEDIUM",
#       "reason": "short explanation of why this is risky",
#       "char_start": 0,
#       "char_end": 0
#     }}
#   ]
# }}

# Where:
# - char_start and char_end are 0-based character indices into the contract text
#   that best evidence the risky clause.
# If no risks are found, return: {{ "risks": [] }}

# CONTRACT TEXT:
# ----------------
# {contract_text}
# """


# # ---------- Main Audit Endpoint ----------

# @router.post("/")
# def audit(request: AuditRequest, db: Session = Depends(get_db)):
#     # 1) Get document from DB
#     doc = crud.get_document(db, request.document_id)
#     if not doc:
#         raise HTTPException(status_code=404, detail="Document not found")

#     contract_text = (doc.text or "")[:20000]  # safety limit

#     if not contract_text.strip():
#         return {"risks": []}

#     # 2) Build prompt
#     prompt = AUDIT_PROMPT.format(contract_text=contract_text)

#     # 3) Call LLM
#     response = llm.invoke(prompt)
#     raw = getattr(response, "content", str(response)).strip()

#     # 4) Parse JSON safely
#     try:
#         data = json.loads(raw)
#     except Exception:
#         # Model kabhi extra text de de to json part nikal lo
#         start = raw.find("{")
#         end = raw.rfind("}") + 1
#         data = json.loads(raw[start:end])

#     risks = data.get("risks", [])

#     # 5) Add document_id to each finding
#     for r in risks:
#         r["document_id"] = request.document_id

#     return {"risks": risks}



from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db.connection import SessionLocal
from app.db import crud
from langchain_groq import ChatGroq
import os
import json
from app.api.admin import METRICS

router = APIRouter(prefix="/audit", tags=["Audit"])

# ---------------- LLM -----------------
llm = ChatGroq(
    model_name="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
)

# ---------------- Request Schema -------------
class AuditRequest(BaseModel):
    document_id: int


# ---------------- DB Session Dependency -------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------- Prompt Template -------------

AUDIT_PROMPT = """
You are a Contract Risk Auditor AI.

Analyze the contract text below and detect risky clauses.
Return STRICT JSON only in this schema:

{{
  "risks": [
    {{
      "clause": "string",
      "severity": "Low | Medium | High | Critical",
      "description": "Why this clause is risky",
      "evidence": "Exact sentence from contract",
      "char_start": number,
      "char_end": number,
      "page": number,
      "risk_type": "Legal | Financial | Commercial | Compliance",
      "remediation": "How to fix or reduce risk",
      "confidence": number
    }}
  ]
}}

Rulebook:
- Auto-renewal < 30 day notice => Critical
- Unlimited liability => Critical
- Broad indemnity => High
- No termination clause => High
- No governing law => Medium
- Missing signatory details => Low
- Never hallucinate content
- If no risks found => {{ "risks": [] }}

CONTRACT TEXT:
\"\"\"{contract_text}\"\"\"
"""



# ---------------- Main: AUDIT API -----------------

@router.post("/")
def audit(request: AuditRequest, db: Session = Depends(get_db)):
    doc = crud.get_document(db, request.document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    contract_text = (doc.text or "")[:25000]  # limit for performance

    if not contract_text.strip():
        return {"risks": []}

    prompt = AUDIT_PROMPT.format(contract_text=contract_text)

    response = llm.invoke(prompt)
    raw = getattr(response, "content", str(response)).strip()

    # --- JSON extract & sanitization ---
    try:
        result = json.loads(raw)
    except:
        start = raw.find("{")
        end = raw.rfind("}") + 1
        cleaned = raw[start:end]
        try:
            result = json.loads(cleaned)
        except:
            return {"error": "Invalid LLM response", "raw": raw}

    risks = result.get("risks", [])

    # add doc_id in each finding
    for r in risks:
        r["document_id"] = request.document_id
        if "page" not in r or r["page"] is None:
            r["page"] = 1  # fallback
        
    METRICS["audit_count"] += 1

    return {"document_id": request.document_id, "risks": risks}
