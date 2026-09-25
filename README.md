# TechStore AI Customer Support Multi-Agent System

An AI-powered customer support system for a fictional online electronics store, **TechStore**. The system uses a routing agent to direct customer questions to one of two specialized agents, combining **RAG (Retrieval-Augmented Generation)** for unstructured knowledge with **structured tool calls** for exact data lookups, backed by **multi-turn session memory**.

Built as part of the Sahaba AI Internship (Week 7&8: AI Customer Support Multi-Agent System).

## Architecture

```
Customer → HTML/CSS/JS Frontend → FastAPI Backend → Routing Agent (w/ History) → Customer Support Agent
                                                                               → Product Agent
```

- **Frontend**: A single-page HTML/CSS/JS chat interface that establishes a per-browser `session_id`, communicates with the backend, and tags each response with the agent that answered.
- **Backend**: FastAPI, exposing a `POST /chat` endpoint handling messages and session states.
- **Routing Agent**: A context-aware LLM classifier that analyzes both the ongoing conversation window and the latest user prompt to route seamlessly between agents.
- **Customer Support Agent**: Answers company/policy questions using RAG over 5 policy PDFs, and resolves order status inquiries using direct deterministic tool lookups on `orders.csv`.
- **Product Agent**: Answers product questions and gives recommendations using RAG over `products.csv`, alongside a structured tool for exact criteria filtering (category, price limit, rating).
- **Session Memory**: In-memory message store maintaining a sliding context window across turns, enabling seamless follow-up questions and multi-turn dialogues.

## Key Design Decision: RAG vs. Structured Tool Calls

A core architectural choice in this project is that **order lookups and product filtering are NOT done through RAG.**

- `orders.csv` and `products.csv` contain **structured, exact data** (order IDs, statuses, prices, categories). Retrieving this kind of data via semantic similarity search is approximate by nature and cannot reliably guarantee exact string matching on non-semantic keys (like `O0001` or `C096`) or strict arithmetic filters (like `price <= 600`).
- Instead, both agents expose **deterministic tool functions** (`check_order_status`, `list_customer_orders`, `filter_products`) running direct `pandas` queries. The LLM decides *when* to invoke these tools and extracts the relevant parameters, ensuring 100% precision.
- RAG is reserved for genuinely unstructured, descriptive content: the 5 company policy PDFs (Customer Support Agent) and free-text semantic product descriptions (Product Agent).

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
├── customer_support_agent.py    # Agent 1: policy RAG + order tool (memory-enabled)
├── ingest_products.py           # Builds the product Chroma vector store
├── product_agent.py             # Agent 2: product RAG + filtering tool (memory-enabled)
├── routing_agent.py             # Classifies, manages session memory, and routes
├── main.py                      # FastAPI backend (/chat endpoint with session tracking)
├── index.html                   # Frontend chat UI (session-aware)
├── requirements.txt
└── README.md
```

> **Note**: Vector store caches (`chroma_kb/`, `chroma_products/`), local environments (`venv/`), and environment secrets (`.env`) are excluded from version control. Run the ingestion scripts to build the local vector stores before launching the API.

## Setup & Running Locally

**1. Clone the repository and create a virtual environment**

```powershell
python -m venv venv
venv\Scripts\Activate.ps1      # Windows PowerShell
```

**2. Install dependencies**

```powershell
pip install -r requirements.txt
```

**3. Create a `.env` file** in the project root:

```env
OPENROUTER_API_KEY=your_key_here
```

**4. Build the vector databases** (must be run once before starting the server)

```powershell
python ingest_kb.py
python ingest_products.py
```

**5. Start the backend**

```powershell
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`, with interactive documentation at `http://127.0.0.1:8000/docs`.

**6. Open the frontend**

Open `index.html` directly in your browser. Ensure the FastAPI backend is running.

## Example Questions & Multi-Turn Flows

**Customer Support Agent** (policies, company info, order tracking):
- "What is your return policy?"
- "What does the warranty cover?"
- "What's the status of order O0001?"
- *Follow-up:* "What is its delivery date?"

**Product Agent** (product info, recommendations):
- "Can you recommend a laptop under $600?"
- *Follow-up:* "Does it come with a warranty?" *(Routes contextually across agents)*
- "Do you have any noise cancelling headphones?"
- "Show me monitors with a high rating"

## Notes & Production Considerations

- **In-Memory History**: Session histories are stored in an in-memory dictionary keyed by `session_id`. In a multi-worker production environment, this should be backed by an external distributed store like Redis.
- **CORS Configuration**: CORS is open (`allow_origins=["*"]`) for local testing convenience. Restrict this to the production client origin prior to production deployment.
