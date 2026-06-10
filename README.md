# Vector Search Engine (From First Principles)

This project demonstrates a Retrieval Augmented Generation (RAG) system built without specialized Vector Databases. It manually handles embedding generation, storage, and similarity search.

## project Structure

- **`backend/ingest.py`**: 
  - Reads `backend/data/dataset.csv`.
  - Splits text into chunks.
  - Generates embeddings using `sentence-transformers`.
  - Saves TEXT to SQLite (`backend/data/wiki_chunks.db`).
  - Saves VECTORS to a Pickle file (`backend/data/vector_store.pkl`).

- **`backend/main.py`**:
  - FastAPI Microservice.
  - Loads `vector_store.pkl` into memory on startup.
  - Provides a `/search` endpoint.
  - Calculates Cosine Similarity manually using NumPy.

- **`frontend/app.py`**:
  - Streamlit Frontend.
  - Accepts user queries.
  - Calls the API to get results.
  - Displays the matched text and similarity score.

## How to Run

### 1. Install Requirements
```bash
# Backend
pip install -r backend/pyproject.toml 
# Frontend
pip install -r frontend/pyproject.toml
```

### 2. Ingest Data
Run this once to process the CSV file.
```bash
python backend/ingest.py
```
*Expected Output: "--- Ingestion Complete ---"*

### 3. Start Backend API
Open a terminal and run:
```bash
uvicorn backend.main:app --reload
```
*Wait for: "Application startup complete."*

### 4. Start Frontend UI
Open a new terminal and run:
```bash
streamlit run frontend/app.py
```
This will automatically open your web browser.

## Tech Stack
- **Python 3.12**
- **FastAPI** (Backend)
- **Streamlit** (Frontend)
- **SQLite** (Text Storage)
- **Pydantic & NumPy** (Vector Management)
