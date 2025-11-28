from .models import Document
from sqlalchemy.orm import Session


def save_document(db, file_name: str, text: str):
    doc = Document(file_name=file_name, text=text)
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc

def get_document(db, document_id: int):
    return db.query(Document).filter(Document.id == document_id).first()

def get_all_documents(db):
    return db.query(Document).all()

def update_document_text(db: Session, document_id: int, text: str):
    doc = db.query(Document).filter(Document.id == document_id).first()
    doc.text = text
    db.commit()
