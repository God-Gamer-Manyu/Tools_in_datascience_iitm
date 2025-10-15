RAG PoC for TypeScript Book

Setup

1. Clone the TypeScript Book into this folder:

   git clone --depth 1 https://github.com/basarat/typescript-book typescript-book

2. Create a Python venv and install dependencies:

   python -m venv .venv
   .\.venv\Scripts\activate
   pip install -r requirements.txt

Indexing

To index the book (may take a few minutes):

   python -m rag.cli --reindex

CLI query

   python -m rag.cli "What does the author affectionately call the => syntax?"

Server

   python -m rag.server

Test endpoint

   http://localhost:8000/search?q=What+does+the+author+affectionately+call+the+%3D%3E+syntax%3F

The server will return a JSON object {"answer": string, "sources": [...]}
