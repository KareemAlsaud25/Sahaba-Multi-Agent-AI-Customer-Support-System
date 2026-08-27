from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langchain.agents import create_agent
from dotenv import load_dotenv
import os

from order_tool import get_order_status, get_orders_by_customer

load_dotenv()

CHROMA_PATH = "chroma_kb"
COLLECTION_NAME = "company_kb"

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

vector_store = Chroma(
    collection_name=COLLECTION_NAME,
    embedding_function=embeddings,
    persist_directory=CHROMA_PATH
)

retriever = vector_store.as_retriever(search_kwargs={"k": 3})

llm = ChatOpenAI(
    model="openai/gpt-4o-mini",
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    temperature=0
)

@tool
def search_company_policies(question: str) -> str:
    """Search company policies and general company info (returns, shipping, warranty, payment, contact info, hours)."""
    docs = retriever.invoke(question)
    return "\n\n".join(doc.page_content for doc in docs)

@tool
def check_order_status(order_id: str) -> str:
    """Look up the status and details of a single order by its order ID (e.g. O0001)."""
    return get_order_status(order_id)

@tool
def list_customer_orders(customer_id: str) -> str:
    """List all orders placed by a specific customer ID (e.g. C096)."""
    return get_orders_by_customer(customer_id)

SYSTEM_PROMPT = """You are TechStore's customer support agent.
You answer questions about company policies (returns, shipping, warranty, payment) and company information using the search_company_policies tool.
You answer questions about order status using check_order_status or list_customer_orders.
Only use information returned by your tools. If the tools do not contain the answer, say you don't have that information and suggest the customer contact support@techstore.example.
Keep answers concise and clear."""

customer_support_agent = create_agent(
    model=llm,
    tools=[search_company_policies, check_order_status, list_customer_orders],
    system_prompt=SYSTEM_PROMPT
)

def run_customer_support_agent(user_message: str) -> str:
    result = customer_support_agent.invoke({"messages": [{"role": "user", "content": user_message}]})
    return result["messages"][-1].content