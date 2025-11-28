from langchain_groq import ChatGroq

from config import GROQ_API_KEY
from dotenv import load_dotenv
load_dotenv()

llm = ChatGroq(
    api_key=GROQ_API_KEY,
    model="llama-3.3-70b-versatile",
)

def extract_fields(text):
    prompt = f"""
    Extract these fields from contract:
    parties, effective_date, governing_law, term, payment_terms.

    Return JSON only.

    Contract:
    {text}
    """

    response = llm.invoke(prompt)
    return response.content
