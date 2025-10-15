from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import openai
import dotenv

import os

dotenv.load_dotenv("week 4/.env")

try:
    # New official OpenAI python library import style
    from openai import OpenAI
except Exception:
    # Fallback for older packaging
    import openai

import numpy as np


class SimilarityRequest(BaseModel):
    docs: List[str]
    query: str


class SimilarityResponse(BaseModel):
    matches: List[str]


app = FastAPI()

# Allow all origins for simplicity in internal app — restrict in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "OPTIONS", "GET"],
    allow_headers=["*"],
)


def get_client():
    # Prefer explicit API key via env var OPENAI_API_KEY
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        # allow a test mode that doesn't require OpenAI credentials
        if os.environ.get("SIM_TEST_MODE") == "1":
            return None
        raise RuntimeError("OPENAI_API_KEY environment variable is required")
    # The new split library uses client object
    try:
        return openai.OpenAI(api_key=api_key, base_url=os.environ.get("OPENAI_BASE_URL"))
    except Exception:
        # older openai lib
        openai.api_key = api_key
        return openai


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    if a.ndim != 1 or b.ndim != 1:
        raise ValueError("cosine_similarity expects 1-D vectors")
    denom = (np.linalg.norm(a) * np.linalg.norm(b))
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)


def _compute_top_matches(docs: List[str], query: str, top_k: int = 3) -> SimilarityResponse:
    if not docs or not isinstance(docs, list):
        raise HTTPException(status_code=400, detail="'docs' must be a non-empty list of strings")
    if not query or not isinstance(query, str):
        raise HTTPException(status_code=400, detail="'query' must be a non-empty string")

    client = get_client()

    # Generate embeddings for docs in batches
    try:
        doc_embeddings = []
        if client is None:
            # SIM_TEST_MODE: create deterministic small embeddings for testing
            def simple_embed(text: str):
                arr = np.array([float(sum(ord(c) for c in text) % 1000), float(len(text) % 100)], dtype=float)
                return arr

            for d in docs:
                doc_embeddings.append(simple_embed(d or ""))
            qemb = simple_embed(query or "")
        else:
            for d in docs:
                if d is None:
                    d = ""
                resp = client.embeddings.create(model="text-embedding-3-small", input=d)
                emb = np.array(resp.data[0].embedding, dtype=float)
                doc_embeddings.append(emb)

            # query embedding
            qresp = client.embeddings.create(model="text-embedding-3-small", input=query)
            qemb = np.array(qresp.data[0].embedding, dtype=float)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"embedding generation failed: {e}")

    # compute similarities
    sims = [cosine_similarity(qemb, de) for de in doc_embeddings]

    # get indices of top k
    top_k = min(top_k, len(docs))
    idx_sorted = sorted(range(len(sims)), key=lambda i: sims[i], reverse=True)
    top_idx = idx_sorted[:top_k]

    matches = [docs[i] for i in top_idx]

    return SimilarityResponse(matches=matches)


@app.post("/similarity", response_model=SimilarityResponse)
async def similarity(req: SimilarityRequest):
    return _compute_top_matches(req.docs, req.query, top_k=3)


@app.get("/similarity", response_model=SimilarityResponse)
async def similarity_get(docs: Optional[List[str]] = None, query: Optional[str] = None):
    """Support simple testing via GET: /similarity?docs=one&docs=two&query=hello"""
    # FastAPI already parses repeated query params into list for the docs arg
    return _compute_top_matches(docs or [], query or "", top_k=3)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("similarity_service:app", host="127.0.0.2", port=8000, reload=True)
