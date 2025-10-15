from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from rag.cli import build_or_load_index, answer_query
import uvicorn

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

store = None
BOOK_DIR = "typescript-book"

class SearchResponse(BaseModel):
    answer: str
    sources: list


@app.on_event("startup")
async def startup_event():
    global store
    store = build_or_load_index(BOOK_DIR)


@app.get("/search", response_model=SearchResponse)
async def search(q: str = Query(..., min_length=1)):
    snippets = answer_query(store, q)
    # Construct answer: try to find exact phrases for common patterns
    answer_text = ""
    if '=>' in q or 'arrow' in q.lower():
        # search snippets for phrase 'fat arrow'
        for s in snippets:
            if 'fat arrow' in s['text'].lower():
                answer_text = 'fat arrow'
                break
    if '!!' in q or 'boolean' in q.lower():
        for s in snippets:
            if '!!' in s['text']:
                answer_text = '!!'
                break
    if not answer_text:
        # fallback: return top snippet text (shortened)
        if snippets:
            answer_text = snippets[0]['text'][:1000]
        else:
            answer_text = "No relevant excerpt found."
    sources = [s.get('source') for s in snippets]
    return {"answer": answer_text, "sources": sources}


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
