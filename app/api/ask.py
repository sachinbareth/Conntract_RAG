# from fastapi import APIRouter
# from pydantic import BaseModel
# from app.services.rag_engine import ask_question

# router = APIRouter(prefix="/ask", tags=["Ask API"])

# class AskRequest(BaseModel):
#     question: str

# @router.post("/")
# def ask(request: AskRequest):
#     return {"answer": ask_question(request.question)}




from fastapi import APIRouter
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
import json
from app.api.admin import METRICS

from app.services import rag_engine

router = APIRouter(prefix="/ask", tags=["Ask API"])


class AskRequest(BaseModel):
    question: str


# ---------- Normal RAG Answer (Already Working) ----------

@router.post("/")
def ask(request: AskRequest):
    """Non-streaming RAG answer."""
    METRICS["ask_count"] += 1 
    return rag_engine.ask_question(request.question)


# ---------- Streaming RAG Answer (SSE) ----------

@router.get("/stream")
def ask_stream(question: str):
    """
    SSE streaming version of /ask.

    Client receives events like:
      data: {"type":"meta", "citations":[...]}
      data: {"type":"token", "text":"First part "}
      data: {"type":"token", "text":"next..."}
      data: {"type":"end"}

    Frontend (JS) example:

      const evtSource = new EventSource('/ask/stream?question=...');
      evtSource.onmessage = (e) => {
          const event = JSON.parse(e.data);
          if (event.type === "token") { appendToUI(event.text); }
          if (event.type === "meta") { showCitations(event.citations); }
          if (event.type === "end") { evtSource.close(); }
      };
    """

    def event_generator():
        for event in rag_engine.stream_answer(question):
            yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
