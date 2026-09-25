FastAPI backend is running.

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
