# TechStore AI Customer Support Multi-Agent System

An AI-powered customer support system for a fictional online electronics store, **TechStore**. The system uses a routing agent to direct customer questions to one of two specialized agents, combining **RAG (Retrieval-Augmented Generation)** for unstructured knowledge with **structured tool calls** for exact data lookups, plus **session-based conversation memory** for natural follow-up questions.

Originally built as part of the Sahaba AI Internship (Week 7&8: AI Customer Support Multi-Agent System), later extended independently for portfolio purposes.

## Architecture

```
Customer → HTML/CSS/JS Frontend → FastAPI Backend → Routing Agent → Customer Support Agent
                                                                   → Product Agent
```

- **Frontend**: A single-page HTML/CSS/JS chat interface. Generates a persistent `session_id` on page load and sends it with every message, so the backend can track conversation history per session.
- **Backend**: FastAPI, exposing a single `POST /chat` endpoint that accepts `{ message, session_id }`.
- **Routing Agent**: An LLM classifier that reads the customer's message — along with recent conversation history — and decides whether it belongs to the Customer Support Agent or the Product Agent. Using history here lets it correctly interpret follow-ups like "when will it arrive?" that only make sense in context.
- **Customer Support Agent**: Answers company/policy questions using RAG over 5 policy PDFs, and answers order-related questions using a structured tool that queries `orders.csv` directly.
- **Product Agent**: Answers product questions and gives recommendations using RAG over `products.csv`, plus a structured filtering tool for exact constraints like price, category, and rating.

## Key Design Decision: RAG vs. Structured Tool Calls

A core architectural choice in this project is that **order lookups and product filtering are NOT done through RAG.**

- `orders.csv` and `products.csv` contain **structured, exact data** (order IDs, statuses, prices, categories). Retrieving this kind of data via semantic similarity search is the wrong tool for the job — it's approximate by nature and can't reliably guarantee it respects a hard constraint like "price ≤ $600" or return the *exact* record for order `O0001`.
- Instead, both agents expose **tool functions** (`check_order_status`, `filter_products`) that perform direct, deterministic `pandas` lookups/filters. The LLM decides *when* to call these tools based on the nature of the question, but the actual data retrieval is exact, not embedding-based.
- RAG is reserved for genuinely unstructured, descriptive content: the 5 policy PDFs (Customer Support Agent) and free-text product descriptions used for descriptive/semantic product search (Product Agent).

**This design was validated by direct experimentation.** An earlier version of this project replaced the order tool with a pure-RAG approach (embedding every order row and retrieving by semantic similarity), as an exercise in seeing how far RAG-only retrieval could go for structured identifier lookups. That version consistently failed to reliably retrieve exact orders — hit rates around 50-60% even with a larger `k` and a stronger embedding model, with failures clustering around order IDs that were numerically similar to many other IDs in the dataset (e.g. `O0002` competing against `O0022`, `O0200`, `O1002`, etc.). This is a well-documented RAG limitation: embedding models are built to capture semantic meaning, not to guarantee exact-match retrieval over arbitrary identifier strings. The current hybrid design exists specifically because of this finding, not as an untested assumption.

**The order tool also returns fully structured, labeled fields** (`order_id`, `customer_id`, `product_id`, `quantity`, `status`, `order_date`, `delivery_date`, `total_amount`, each on its own line) rather than a single pre-formatted sentence. This lets the LLM precisely extract just the field a customer asks about (e.g. "what's the delivery date?") instead of always returning the full order summary.

## Conversation Memory

The system maintains **session-based conversation history**, so follow-up questions work naturally within a session:

- The frontend generates a unique `session_id` when the page loads and includes it with every request.
- The backend keeps an in-memory history of messages per session, and both the routing agent and the specialized agents receive recent history alongside each new message.
- This means a question like "what's the status of order O0001?" followed by "when will it arrive?" correctly resolves the second question in context.

**Limitations of this implementation:**
- History is stored **in memory only** — restarting the backend clears all sessions.
- History is **not automatically trimmed or summarized** for very long conversations, which could eventually grow the context sent to the LLM.
- Sessions are identified only by a randomly generated ID with no authentication — this is a portfolio/demo-appropriate implementation, not a production-ready session system (no persistence layer, no user accounts, no expiry).

## Tech Stack

- **LLM orchestration**: LangChain (`create_agent`, LCEL, `MessagesPlaceholder`)
- **LLM provider**: OpenRouter (via `ChatOpenAI`, OpenAI-compatible interface)
- **Embeddings**: `sentence-transformers/all-MiniLM-L6-v2` (HuggingFace)
- **Vector database**: Chroma (two collections — company policies and products)
- **Backend**: FastAPI + Uvicorn
- **Frontend**: Plain HTML, CSS, and JavaScript (single file), with client-side session ID generation
- **Data handling**: pandas

## Project Structure

```
.
├── data/
│   ├── orders.csv              # 500 orders (structured, exact tool-based lookup)
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
├── routing_agent.py             # Classifies and routes each message, tracks session history
├── main.py                      # FastAPI backend (/chat endpoint, session_id handling)
├── index.html                   # Frontend chat UI with session tracking
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
- "What's the delivery date for order O0001?" (tests precise single-field extraction)

**Follow-up questions** (tests conversation memory):
- "What's the status of order O0001?" → "When will it arrive?"

**Product Agent** (product info, recommendations):
- "Can you recommend a laptop under $600?"
- "Do you have any noise cancelling headphones?"
- "Show me monitors with a high rating"

## Known Limitations

- **In-memory session history**: conversation memory does not persist across backend restarts and has no size cap or expiry (see Conversation Memory section above).
- **CORS is fully open** (`allow_origins=["*"]`) for local development simplicity. In a production deployment, this should be restricted to the actual frontend's origin.
- **Order/product lookups use exact structured matching, not RAG** — this is a deliberate design decision, validated by direct experimentation showing pure semantic retrieval is unreliable for exact identifier lookups (see Key Design Decision section above).
