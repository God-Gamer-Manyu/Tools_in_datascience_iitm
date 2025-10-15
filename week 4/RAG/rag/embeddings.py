from typing import List, Tuple
import os
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import pickle

MODEL_NAME = os.environ.get("EMBED_MODEL", "all-MiniLM-L6-v2")
INDEX_PATH = "rag_index.faiss"
META_PATH = "rag_meta.pkl"

class EmbeddingStore:
    def __init__(self, model_name: str = MODEL_NAME):
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.metadatas = []

    def build_index(self, texts: List[str]):
        # Guard: no texts => nothing to index
        if not texts:
            raise ValueError("No texts provided to build index")

        vecs = self.model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
        # Ensure we have a numpy array and a 2D shape (n, d)
        vecs = np.asarray(vecs)
        if vecs.size == 0:
            raise ValueError("Embeddings call returned empty vectors")
        if vecs.ndim == 1:
            # single vector returned as 1D -> make it (1, d)
            vecs = vecs.reshape(1, -1)

        # FAISS requires float32
        if vecs.dtype != np.float32:
            vecs = vecs.astype('float32')

        d = int(vecs.shape[1])
        self.index = faiss.IndexFlatL2(d)
        self.index.add(vecs)
        self.metadatas = [{"text": t, "id": i} for i, t in enumerate(texts)]
        return

    def save(self, index_path=INDEX_PATH, meta_path=META_PATH):
        if self.index is None:
            raise RuntimeError("Index not built")
        faiss.write_index(self.index, index_path)
        with open(meta_path, "wb") as f:
            pickle.dump(self.metadatas, f)

    def load(self, index_path=INDEX_PATH, meta_path=META_PATH):
        if not os.path.exists(index_path) or not os.path.exists(meta_path):
            return False
        self.index = faiss.read_index(index_path)
        with open(meta_path, "rb") as f:
            self.metadatas = pickle.load(f)
        return True

    def query(self, query: str, k=3) -> List[Tuple[float, dict]]:
        if self.index is None:
            raise RuntimeError("Index not built or loaded")

        qvec = self.model.encode([query], convert_to_numpy=True)
        qvec = np.asarray(qvec)
        if qvec.ndim == 1:
            qvec = qvec.reshape(1, -1)
        if qvec.dtype != np.float32:
            qvec = qvec.astype('float32')

        D, I = self.index.search(qvec, k)
        results = []
        for dist, idx in zip(D[0], I[0]):
            meta = self.metadatas[int(idx)]
            results.append((float(dist), meta))
        return results
