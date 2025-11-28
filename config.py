import os

POSTGRES_URL = os.getenv(
    "POSTGRES_URL",
    "postgresql://postgres:Sach1234@localhost:5432/contractdb"
)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

EMBED_MODEL = "intfloat/multilingual-e5-base"
CHUNK_SIZE = 800
CHUNK_OVERLAP = 100
