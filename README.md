[README.md](https://github.com/user-attachments/files/31531094/README.md)
# TechStore AI Customer Support Multi-Agent System

An AI-powered customer support system for a fictional online electronics store, **TechStore**. The system uses a routing agent to direct customer questions to one of two specialized agents, combining **RAG (Retrieval-Augmented Generation)** for unstructured knowledge with **structured tool calls** for exact data lookups.

Built as part of the Sahaba AI Internship (Week 7&8: AI Customer Support Multi-Agent System).

## Architecture

```
Customer → HTML/CSS/JS Frontend → FastAPI Backend → Routing Agent → Customer Support Agent
                                                                   → Product Agent
```

- **Frontend**: A single-page HTML/CSS/JS chat interface that sends messages to the backend and displays responses, tagged with which agent answered.
- **Backend**: FastAPI, exposing a single `POST /chat` endpoint.
- **Routing Agent**: A lightweight LLM classifier that reads the customer's message and decides whether it belongs to the Customer Support Agent or the Product Agent.
- **Customer Support Agent**: Answers company/policy questions using RAG over 5 policy PDFs, and answers order-status questions using a structured tool that queries `orders.csv` directly.
- **Product Agent**: Answers product questions and gives recommendations using RAG over `products.csv`, plus a structured filtering tool for exact constraints like price, category, and rating.

## Key Design Decision: RAG vs. Structured Tool Calls

A core architectural choice in this project is that **order lookups and product filtering are NOT done through RAG.**

- `orders.csv` and `products.csv` contain **structured, exact data** (order IDs, statuses, prices, categories). Retrieving this kind of data via semantic similarity search is the wrong tool for the job — it's approximate by nature and can't reliably guarantee it respects a hard constraint like "price ≤ $600" or return the *exact* record for order `O0001`.
- Instead, both agents expose **tool functions** (`check_order_status`, `filter_products`) that perform direct, deterministic `pandas` lookups/filters. The LLM decides *when* to call these tools based on the nature of the question, but the actual data retrieval is exact, not embedding-based.
- RAG is reserved for genuinely unstructured, descriptive content: the 5 policy PDFs (Customer Support Agent) and free-text product descriptions used for descriptive/semantic product search (Product Agent).

This split is intentional and is the main technical distinction this project is built to demonstrate.

## Tech Stack

- **LLM orchestration**: LangChain (`create_agent`, LCEL)
- **LLM provider**: OpenRouter (via `ChatOpenAI`, OpenAI-compatible interface)
- **Embeddings**: `sentence-transformers/all-MiniLM-L6-v2` (HuggingFace)
- **Vector database**: Chroma (two separate collections — one for company policies, one for products)
- **Backend**: FastAPI + Uvicorn
- **Frontend**: Plain HTML, CSS, and JavaScript (single file)
- **Data handling**: pandas

## Project Structure

```
.
├── data/
│   ├── orders.csv              # 500 orders (structured, tool-based lookup only)
│   └── products.csv            # 50 products (RAG + structured filtering)
├── knowledge_base/
│   ├── company_info.pdf
│   ├── return_policy.pdf
│   ├── shipping_policy.pdf
│   ├── warranty_policy.pdf
│   └── payment_policy.pdf
├── ingest_kb.py                 # Builds the company policy Chroma vector store
├── order_tool.py                # Structured lookup functions over orders.csv
├── customer_support_agent.py    # Agent 1: policy RAG + order tool
├── ingest_products.py           # Builds the product Chroma vector store
├── product_agent.py             # Agent 2: product RAG + filtering tool
├── routing_agent.py             # Classifies and routes each message
├── main.py                      # FastAPI backend (/chat endpoint)
├── index.html                   # Frontend chat UI
├── requirements.txt
└── README.md
```

Note: the `chroma_kb/` and `chroma_products/` vector store folders, the `venv/` virtual environment, and the `.env` file are **not included** in this repository. They are either rebuildable or environment/secret-specific — see setup steps below.

## Setup & Running Locally

**1. Clone the repository and create a virtual environment**

```
python -m venv venv
venv\Scripts\Activate.ps1      # Windows PowerShell
```

**2. Install dependencies**

```
pip install -r requirements.txt
```

**3. Create a `.env` file** in the project root with your OpenRouter API key:

```
OPENROUTER_API_KEY=your_key_here
```

**4. Build the vector databases** (must be run once before starting the server)

```
python ingest_kb.py
python ingest_products.py
```

**5. Start the backend**

```
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`, with interactive docs at `http://127.0.0.1:8000/docs`.

**6. Open the frontend**

Open `index.html` directly in your browser (double-click it). Make sure the backend from step 5 is still running.

## Example Questions to Try

**Customer Support Agent** (policies, company info, order status):
- "What is your return policy?"
- "What does the warranty cover?"
- "What's the status of order O0001?"

**Product Agent** (product info, recommendations):
- "Can you recommend a laptop under $600?"
- "Do you have any noise cancelling headphones?"
- "Show me monitors with a high rating"

## Known Limitations

- **Stateless conversations**: Each message is processed independently, with no memory of prior turns in the same session. Follow-up questions that rely on earlier context (e.g. "tell me more about the first one") are not supported in the current version. This was a deliberate scope decision for this stage of the project rather than an oversight.
- **CORS is fully open** (`allow_origins=["*"]`) for local development simplicity. In a production deployment, this should be restricted to the actual frontend's origin.
