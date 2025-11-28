from sqlalchemy import Column, Integer, Text
from app.db.connection import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(Text, nullable=False)
    text = Column(Text, nullable=False)
