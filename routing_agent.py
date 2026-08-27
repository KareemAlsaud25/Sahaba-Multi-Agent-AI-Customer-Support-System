from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import os

from customer_support_agent import run_customer_support_agent
from product_agent import run_product_agent

load_dotenv()

llm = ChatOpenAI(
    model="openai/gpt-4o-mini",
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    temperature=0
)

ROUTING_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "You are a routing classifier for TechStore's customer support system. "
     "Read the customer's message and decide which agent should handle it. "
     "Reply with exactly one word: 'support' or 'product'. "
     "'support' covers: company info, policies (return, shipping, warranty, payment), and order status questions. "
     "'product' covers: product details, specifications, availability, and product recommendations. "
     "If the message could reasonably fit either, choose the one that matches the main intent of the question."),
    ("human", "{message}")
])

routing_chain = ROUTING_PROMPT | llm

def route_message(user_message: str) -> str:
    result = routing_chain.invoke({"message": user_message})
    decision = result.content.strip().lower()

    if "product" in decision:
        return "product"
    return "support"

def handle_message(user_message: str) -> dict:
    agent_used = route_message(user_message)

    if agent_used == "product":
        response = run_product_agent(user_message)
    else:
        response = run_customer_support_agent(user_message)

    return {
        "agent": agent_used,
        "response": response
    }