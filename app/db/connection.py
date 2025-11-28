from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import POSTGRES_URL

Base = declarative_base()

engine = create_engine(POSTGRES_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
