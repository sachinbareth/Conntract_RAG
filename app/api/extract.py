from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.connection import SessionLocal
from app.db import crud
from app.api.admin import METRICS

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
import os
import json
from dotenv import load_dotenv
load_dotenv()

router = APIRouter(prefix="/extract", tags=["Extract API"])

llm = ChatGroq(
    model_name="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY")
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/")
def extract(document_id: int, db: Session = Depends(get_db)):
    doc = crud.get_document(db, document_id)
    if not doc:
        return {"error": "❌ Document not found"}

    text = doc.text[:20000]  # limit to avoid long prompt issues

    prompt = f"""
    Extract the following structured fields from this contract text:

    - parties[]: List both party names involved
    - effective_date: Date the contract becomes effective
    - term: Duration of contract
    - governing_law: Jurisdiction/law mentioned
    - payment_terms: Any financial/payment obligations
    - termination: Termination clause summary
    - auto_renewal: Whether it renews automatically (Yes/No + details)
    - confidentiality: Confidentiality obligations summary
    - indemnity: Indemnification clauses summary
    - liability_cap: number + currency if present
    - signatories[]: List of names and titles signing contract

    Return ONLY valid JSON in this exact format:

    {{
        "parties": [],
        "effective_date": "",
        "term": "",
        "governing_law": "",
        "payment_terms": "",
        "termination": "",
        "auto_renewal": "",
        "confidentiality": "",
        "indemnity": "",
        "liability_cap": {{
            "amount": "",
            "currency": ""
        }},
        "signatories": []
    }}

    TEXT:
    {text}
    """

    response = llm.invoke([HumanMessage(content=prompt)])
    result = response.content

    # Validate JSON (if model adds extra text)
    try:
        clean = json.loads(result)
    except:
        start = result.find("{")
        end = result.rfind("}") + 1
        clean = json.loads(result[start:end])
        
    METRICS["extract_count"] += 1
        

    return clean
