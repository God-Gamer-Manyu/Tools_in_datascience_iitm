Similarity service

POST /similarity accepts JSON {"docs": [...], "query": "..."} and returns the top 3 matching documents by cosine similarity using the OpenAI text-embedding-3-small model.

Environment:
- Set OPENAI_API_KEY environment variable before running.

Run locally:

```cmd
python -m pip install -r requirements.txt
uvicorn similarity_service:app --reload --port 8000
```
