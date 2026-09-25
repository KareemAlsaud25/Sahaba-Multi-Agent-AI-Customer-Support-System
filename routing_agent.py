import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage

from customer_support_agent import run_customer_support_agent
from product_agent import run_product_agent

load_dotenv()

SESSIONS = {}

def get_session_history(session_id: str):
    if session_id not in SESSIONS:
        SESSIONS[session_id] = []
    return SESSIONS[session_id]

llm = ChatOpenAI(
    model="openai/gpt-4o-mini",
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    temperature=0
)

ROUTING_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "You are a routing classifier for TechStore's customer support system. "
     "Look at the recent chat history and classify the customer's latest message. "
     "Reply with exactly one word: 'support' or 'product'. "
     "'support' covers: company info, policies (return, shipping, warranty, payment), and order status questions. "
     "'product' covers: product details, specifications, availability, and product recommendations."),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{message}")
])

routing_chain = ROUTING_PROMPT | llm

def route_message(user_message: str, history) -> str:
    result = routing_chain.invoke({
        "history": history[-6:],
        "message": user_message
    })
    decision = result.content.strip().lower()
    return "product" if "product" in decision else "support"

def handle_message(user_message: str, session_id: str = "default_session") -> dict:
    history = get_session_history(session_id)
    agent_used = route_message(user_message, history)

    if agent_used == "product":
        response = run_product_agent(user_message, history=history[-6:])
    else:
        response = run_customer_support_agent(user_message, history=history[-6:])

    history.append(HumanMessage(content=user_message))
    history.append(AIMessage(content=response))

    return {
        "agent": agent_used,
        "response": response
    }
