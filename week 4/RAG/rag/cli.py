import os
import argparse
from glob import glob
from embeddings import EmbeddingStore
import re

BOOK_DIR = "typescript-book"

def load_markdown_files(base_dir):
    patterns = [os.path.join(base_dir, "**", "*.md")]
    files = []
    for p in patterns:
        files.extend(glob(p, recursive=True))
    return files

def split_text(text, max_tokens=400):
    # naive splitter: split by headings and paragraphs, fallback to fixed window
    parts = re.split(r"(?m)^#{1,6} .*$", text)
    chunks = []
    for p in parts:
        p = p.strip()
        if not p:
            continue
        if len(p) <= 2000:
            chunks.append(p)
        else:
            # split into approximate 1000-char slices
            for i in range(0, len(p), 1000):
                chunks.append(p[i:i+1000])
    return chunks


def build_or_load_index(book_dir, force_reindex=False):
    store = EmbeddingStore()
    if not force_reindex and store.load():
        print("Loaded existing index")
        return store
    files = load_markdown_files(book_dir)
    texts = []
    sources = []
    for f in files:
        try:
            with open(f, "r", encoding="utf-8") as fh:
                content = fh.read()
        except Exception as e:
            print("skip", f, e)
            continue
        chunks = split_text(content)
        for i, c in enumerate(chunks):
            texts.append(c)
            sources.append({"file": os.path.relpath(f, book_dir), "chunk": i})
    store.build_index(texts)
    store.metadatas = [{"text": t, "source": s} for t, s in zip(texts, sources)]
    store.save()
    print(f"Indexed {len(texts)} chunks from {len(files)} files")
    return store


def answer_query(store, q):
    res = store.query(q, k=3)
    # return the best snippet with sources
    snippets = []
    for dist, meta in res:
        snippets.append({"score": dist, "text": meta["text"], "source": meta.get("source")})
    # naive answer selection: return the first snippet that contains '=>' or '!!' if those are asked for
    return snippets


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--reindex", action="store_true")
    parser.add_argument("query", nargs="?")
    args = parser.parse_args()
    store = build_or_load_index(BOOK_DIR, force_reindex=args.reindex)
    if args.query:
        res = answer_query(store, args.query)
        import json
        print(json.dumps(res, indent=2, ensure_ascii=False))
    else:
        print("Index ready. Use: cli.py \"Your question\"")
