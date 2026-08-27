import pandas as pd
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langchain.agents import create_agent
from dotenv import load_dotenv
import os

load_dotenv()

PRODUCTS_PATH = "data/products.csv"
CHROMA_PATH = "chroma_products"
COLLECTION_NAME = "products_kb"

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

vector_store = Chroma(
    collection_name=COLLECTION_NAME,
    embedding_function=embeddings,
    persist_directory=CHROMA_PATH
)

retriever = vector_store.as_retriever(search_kwargs={"k": 5})

llm = ChatOpenAI(
    model="openai/gpt-4o-mini",
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    temperature=0
)

@tool
def search_products(question: str) -> str:
    """Search for products by description, use case, or general product questions (e.g. 'lightweight laptop for students', 'noise cancelling headphones')."""
    docs = retriever.invoke(question)
    return "\n\n".join(doc.page_content for doc in docs)

@tool
def filter_products(category: str = "", max_price: float = 0, min_rating: float = 0) -> str:
    """Filter products by exact criteria: category (Laptop, Smartphone, Accessories, Monitor, Audio), max_price, and/or min_rating. Leave a field empty/0 to skip that filter."""
    df = pd.read_csv(PRODUCTS_PATH)

    if category:
        df = df[df["category"].str.lower() == category.lower()]
    if max_price:
        df = df[df["price"] <= max_price]
    if min_rating:
        df = df[df["rating"] >= min_rating]

    if df.empty:
        return "No products match those criteria."

    lines = []
    for _, row in df.iterrows():
        lines.append(
            f"{row['product_name']} ({row['category']}) - ${row['price']}, "
            f"rating {row['rating']}, stock {row['stock']}: {row['description']}"
        )
    return "\n".join(lines)

SYSTEM_PROMPT = """You are TechStore's product agent.
You answer questions about products and give recommendations based on customer needs and budget.
Use search_products for general or descriptive product questions.
Use filter_products when the customer gives exact constraints like category, a price limit, or a minimum rating.
You can use both tools together if needed.
Only recommend products that were returned by your tools. Do not invent products or specifications.
Keep answers concise and mention price and key specs."""

product_agent = create_agent(
    model=llm,
    tools=[search_products, filter_products],
    system_prompt=SYSTEM_PROMPT
)

def run_product_agent(user_message: str) -> str:
    result = product_agent.invoke({"messages": [{"role": "user", "content": user_message}]})
    return result["messages"][-1].content