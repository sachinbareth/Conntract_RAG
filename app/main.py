# from fastapi import FastAPI
# from app.api import ingest, extract, ask, audit, admin
# from app.db.connection import Base, engine

# app = FastAPI(
#     title="Contract Intelligence API",
#     version="1.0.0"
# )

# # Create DB tables
# Base.metadata.create_all(bind=engine)

# app.include_router(ingest.router)
# app.include_router(ask.router)
# app.include_router(extract.router)
# app.include_router(audit.router)  # 👈 ADD THIS
# app.include_router(admin.router)

# @app.get("/")
# def root():
#     return {"message": "Contract Intelligence RAG System is Live 🚀"}

from fastapi import FastAPI
from app.api import ingest, extract, ask, audit, admin
from app.db.connection import Base, engine

app = FastAPI(
    title="Contract Intelligence API",
    version="1.0.0"
)

# Run migrations only when app starts (not during import)
@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)

# Routers
app.include_router(ingest.router)
app.include_router(ask.router)
app.include_router(extract.router)
app.include_router(audit.router)
app.include_router(admin.router)

@app.get("/")
def root():
    return {"message": "Contract Intelligence RAG System is Live 🚀"}
