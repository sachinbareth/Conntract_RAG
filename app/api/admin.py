from fastapi import APIRouter
from pydantic import BaseModel
import time

router = APIRouter(prefix="/admin", tags=["Admin"])

# simple metrics counters
METRICS = {
    "ingest_count": 0,
    "extract_count": 0,
    "ask_count": 0,
    "audit_count": 0,
    "uptime_start": time.time(),
}


@router.get("/healthz")
def healthz():
    return {"status": "ok", "service": "Contract Intelligence", "uptime_sec": round(time.time() - METRICS["uptime_start"])}


@router.get("/metrics")
def metrics():
    uptime = time.time() - METRICS["uptime_start"]
    data = METRICS.copy()
    data["uptime_sec"] = round(uptime, 2)
    return data
