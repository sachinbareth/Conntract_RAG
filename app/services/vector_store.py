from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

from config import EMBED_MODEL

embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)

def create_faiss_store(chunks):
    return FAISS.from_texts(chunks, embeddings)

def save_faiss(store, doc_id):
    store.save_local(f"vectorstores/{doc_id}")

def load_faiss(doc_id):
    return FAISS.load_local(f"vectorstores/{doc_id}", embeddings, allow_dangerous_deserialization=True)
