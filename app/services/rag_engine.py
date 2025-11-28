# # import os
# # from langchain_huggingface import HuggingFaceEmbeddings
# # from langchain_community.vectorstores import FAISS
# # from langchain_groq import ChatGroq
# # from langchain_core.messages import HumanMessage

# # VECTOR_PATH = "vectorstore"

# # embeddings = HuggingFaceEmbeddings(model_name="intfloat/multilingual-e5-base")
# # llm = ChatGroq(model_name="llama-3.3-70b-versatile", api_key=os.getenv("GROQ_API_KEY"))


# # def get_vector_db():
# #     if not os.path.exists(f"{VECTOR_PATH}/index.faiss"):
# #         return None

# #     return FAISS.load_local(
# #         VECTOR_PATH,
# #         embeddings,
# #         allow_dangerous_deserialization=True
# #     )


# # def ask_question(question: str) -> str:
# #     vector_db = get_vector_db()
# #     if not vector_db:
# #         return "❌ No documents ingested yet. Please ingest/upload files first."

# #     # Retrieve top chunks
# #     docs = vector_db.similarity_search(question, k=3)
# #     context = "\n\n".join([d.page_content for d in docs])

# #     # Construct prompt
# #     prompt = f"""
# #     You are a legal contract assistant. Answer the question based ONLY on this context:

# #     CONTEXT:
# #     {context}

# #     QUESTION:
# #     {question}

# #     Provide a concise and accurate answer. If answer not found in context, say "Not mentioned".
# #     """

# #     response = llm.invoke([HumanMessage(content=prompt)])
# #     return response.content



# from langchain_groq import ChatGroq
# from langchain_community.vectorstores import FAISS
# from langchain_huggingface import HuggingFaceEmbeddings
# from langchain_core.prompts import ChatPromptTemplate
# from config import GROQ_API_KEY
# import os

# VECTOR_DIR = "vectorstore"

# embeddings = HuggingFaceEmbeddings(model_name="intfloat/multilingual-e5-base")

# llm = ChatGroq(
#     model_name="llama-3.3-70b-versatile",
#     api_key=GROQ_API_KEY,
# )

# def load_vectorstore():
#     if not os.path.exists(VECTOR_DIR):
#         return None

#     return FAISS.load_local(
#         VECTOR_DIR,
#         embeddings,
#         allow_dangerous_deserialization=True,
#     )


# def ask_question(question: str):

#     vectorstore = load_vectorstore()
#     if not vectorstore:
#         return {
#             "answer": "❌ No documents ingested yet",
#             "citations": []
#         }

#     retriever = vectorstore.as_retriever(
#         search_kwargs={"k": 3}
#     )
#     docs = retriever.invoke(question)

#     if not docs:
#         return {"answer": "❌ No relevant information found", "citations": []}

#     context = ""
#     citations = []

#     for d in docs:
#         meta = d.metadata
#         citations.append({
#             "document_id": meta.get("document_id"),
#             "page": meta.get("page"),
#             "char_start": meta.get("char_start"),
#             "char_end": meta.get("char_end"),
#         })
#         context += f"\n\n{d.page_content}"

#     prompt = ChatPromptTemplate.from_template("""
#     You are a Contract Q&A bot.
#     STRICT RULE: Answer ONLY from the provided text below.
#     If answer is not found, reply: "Not available in uploaded document".

#     Text Context:
#     {context}

#     Question: {question}
#     """)

#     messages = prompt.format_messages(
#         context=context,
#         question=question
#     )
#     response = llm.invoke(messages)

#     return {
#         "answer": response.content.strip(),
#         "citations": citations
#     }




import os
from typing import Generator, Dict, Any, Tuple, List

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_groq import ChatGroq

VECTOR_DIR = "vectorstore"

# Embeddings – same as ingest
embeddings = HuggingFaceEmbeddings(model_name="intfloat/multilingual-e5-base")

# LLM – Groq
llm = ChatGroq(
    model_name="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0,
)


def _load_vectorstore():
    """Load FAISS vectorstore if it exists."""
    if not os.path.exists(f"{VECTOR_DIR}/index.faiss"):
        return None
    return FAISS.load_local(
        VECTOR_DIR,
        embeddings,
        allow_dangerous_deserialization=True,
    )


def _build_context_and_citations(question: str) -> Tuple[str, List[Dict[str, Any]], str | None]:
    """Retrieve relevant chunks + build context + citations."""
    vectorstore = _load_vectorstore()
    if not vectorstore:
        return "", [], "❌ No documents ingested yet. Please ingest/upload files first."

    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    docs = retriever.invoke(question)

    if not docs:
        return "", [], "No relevant information found in uploaded documents."

    context_parts = []
    citations = []

    for idx, d in enumerate(docs):
        meta = d.metadata or {}
        context_parts.append(f"[Chunk {idx+1}]\n{d.page_content}")
        citations.append({
            "document_id": meta.get("document_id"),
            "page": meta.get("page"),
            "char_start": meta.get("char_start"),
            "char_end": meta.get("char_end"),
        })

    context = "\n\n".join(context_parts)
    return context, citations, None


PROMPT_TEMPLATE = """You are a contract Q&A assistant.

You MUST answer ONLY using the information in the provided context.
If the answer is not present, reply exactly: "Not available in the uploaded documents."

Context:
{context}

Question: {question}

Answer:
"""


def ask_question(question: str) -> Dict[str, Any]:
    """Normal (non-streaming) RAG answer."""
    context, citations, error = _build_context_and_citations(question)

    if error:
        return {
            "answer": error,
            "citations": []
        }

    prompt = PROMPT_TEMPLATE.format(context=context, question=question)
    resp = llm.invoke(prompt)
    text = getattr(resp, "content", str(resp)).strip()

    return {
        "answer": text,
        "citations": citations
    }


def stream_answer(question: str) -> Generator[Dict[str, Any], None, None]:
    """
    Streaming RAG answer as events:
    - first event: {"type": "meta", "citations": [...]}
    - token events: {"type": "token", "text": "..."}
    - last event: {"type": "end"}
    """
    context, citations, error = _build_context_and_citations(question)

    if error:
        yield {"type": "error", "message": error}
        return

    prompt = PROMPT_TEMPLATE.format(context=context, question=question)

    # send citations first (client can show "sources" sidebar)
    yield {"type": "meta", "citations": citations}

    # now stream tokens
    for chunk in llm.stream(prompt):
        piece = getattr(chunk, "content", "") or ""
        if not piece:
            continue
        yield {"type": "token", "text": piece}

    # done
    yield {"type": "end"}
