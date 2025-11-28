# from fastapi import APIRouter, UploadFile, File, Depends
# from sqlalchemy.orm import Session
# from app.db.connection import SessionLocal
# from app.db import crud
# from app.services.text_splitter import split_text

# from langchain_community.document_loaders import PyPDFLoader
# from langchain_huggingface import HuggingFaceEmbeddings
# from langchain_community.vectorstores import FAISS

# import os
# import tempfile

# router = APIRouter(prefix="/ingest", tags=["Ingest API"])

# VECTOR_PATH = "vectorstore"
# embeddings = HuggingFaceEmbeddings(model_name="intfloat/multilingual-e5-base")


# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


# @router.post("/")
# async def ingest(file: UploadFile = File(...), db: Session = Depends(get_db)):

#     # Save temporary file
#     with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
#         tmp_file.write(await file.read())
#         file_path = tmp_file.name

#     # Load & Extract text from PDF
#     loader = PyPDFLoader(file_path)
#     pages = loader.load()
#     text = "\n".join([p.page_content for p in pages])

#     # Save metadata + raw text in Database
#     crud.save_document(db, file.filename, text)

#     # Split text to chunks
#     chunks = split_text(text)

#     # Initialize or update FAISS vectorstore
#     if os.path.exists(f"{VECTOR_PATH}/index.faiss"):
#         vectorstore = FAISS.load_local(
#             VECTOR_PATH,
#             embeddings,
#             allow_dangerous_deserialization=True
#         )
#         vectorstore.add_texts(chunks)
#     else:
#         vectorstore = FAISS.from_texts(chunks, embeddings)

#     vectorstore.save_local(VECTOR_PATH)

#     return {"message": "📥 Document successfully ingested & indexed!"}


from fastapi import APIRouter, UploadFile, Depends
from sqlalchemy.orm import Session
from app.db.connection import SessionLocal
from app.db import crud
from app.api.admin import METRICS

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from PyPDF2 import PdfReader
import os
import shutil

router = APIRouter(prefix="/ingest", tags=["Ingest API"])

VECTOR_DIR = "vectorstore"
embeddings = HuggingFaceEmbeddings(model_name="intfloat/multilingual-e5-base")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/")
def ingest(file: UploadFile, db: Session = Depends(get_db)):

    pdf_path = f"temp_{file.filename}"
    with open(pdf_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    reader = PdfReader(pdf_path)
    full_text = ""
    docs = []

    # 1️⃣ Save full doc to DB
    db_doc = crud.save_document(db, file.filename, "")
    db_doc_id = db_doc.id

    char_counter = 0

    # 2️⃣ Extract chunks per page + metadata
    for page_idx, page in enumerate(reader.pages):
        text = page.extract_text()
        if not text:
            continue

        full_text += text
        chunks = [text[i:i+500] for i in range(0, len(text), 500)]

        for chunk in chunks:
            char_start = char_counter
            char_end = char_counter + len(chunk)

            docs.append({
                "page_content": chunk,
                "metadata": {
                    "document_id": db_doc_id,
                    "page": page_idx + 1,
                    "char_start": char_start,
                    "char_end": char_end,
                }
            })
            char_counter += len(chunk)

    # Update DB document full text
    crud.update_document_text(db, db_doc_id, full_text)

    # 3️⃣ Store in FAISS
    if os.path.exists(VECTOR_DIR):
        vectorstore = FAISS.load_local(
            VECTOR_DIR, embeddings,
            allow_dangerous_deserialization=True
        )
        vectorstore.add_texts(
            [d["page_content"] for d in docs],
            metadatas=[d["metadata"] for d in docs]
        )
        vectorstore.save_local(VECTOR_DIR)
    else:
        vectorstore = FAISS.from_texts(
            [d["page_content"] for d in docs],
            embedding=embeddings,
            metadatas=[d["metadata"] for d in docs]
        )
        vectorstore.save_local(VECTOR_DIR)

    os.remove(pdf_path)
    METRICS["ingest_count"] += 1

    return {"message": "Ingested Successfully!", "document_id": db_doc_id}
