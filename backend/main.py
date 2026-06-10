from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import pickle
import numpy as np
import sqlite3
import os
from sentence_transformers import SentenceTransformer
import contextlib

# --- Configuration ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "wiki_chunks.db")
VECTOR_STORE_PATH = os.path.join(DATA_DIR, "vector_store.pkl")

# --- In-Memory State ---
memory_store = []
model = None

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    # Load resources on startup
    global memory_store, model
    print("Loading Model...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    if os.path.exists(VECTOR_STORE_PATH):
        print(f"Loading Vector Store from {VECTOR_STORE_PATH}...")
        with open(VECTOR_STORE_PATH, "rb") as f:
            raw_data = pickle.load(f)
            
        # Reconstruct objects
        memory_store = [
            {
                "chunk_id": item['chunk_id'],
                "document_id": item['document_id'],
                "source": item.get('source', 'Unknown'),
                "embedding": item['embedding']
            }
            for item in raw_data
        ]
        print(f"✅ Loaded {len(memory_store)} vectors.")
    else:
        print("⚠️ Warning: Vector store not found. Did you run ingest.py?")
        
    yield
    # Clean up resources on shutdown
    memory_store.clear()

app = FastAPI(title="Vector Search API", lifespan=lifespan)

# Enable CORS for Frontend Access (Important for separating services)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Models ---
class SearchRequest(BaseModel):
    query: str
    top_k: int = 5

class SearchResult(BaseModel):
    chunk_id: int
    document_id: int
    score: float
    content: str
    source: str

# --- Logic ---
def get_text_from_db(chunk_id: int) -> str:
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT content FROM chunks WHERE id = ?", (chunk_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else "Text not found (DB Error)"
    except Exception as e:
        return f"DB Error: {str(e)}"

def cosine_similarity(v1, v2):
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

@app.post("/search", response_model=List[SearchResult])
async def search(request: SearchRequest):
    if not memory_store:
        raise HTTPException(status_code=503, detail="System initializing or no data found.")
        
    query_vector = model.encode(request.query)
    
    scores = []
    for record in memory_store:
        score = cosine_similarity(query_vector, record['embedding'])
        scores.append({
            **record,
            "score": float(score)  # Convert for JSON serialization
        })
        
    # Sort descending
    scores.sort(key=lambda x: x["score"], reverse=True)
    top_results = scores[:request.top_k]
    
    final_results = []
    for item in top_results:
        text = get_text_from_db(item["chunk_id"])
        final_results.append(SearchResult(
            chunk_id=item["chunk_id"],
            document_id=item["document_id"],
            score=item["score"],
            content=text,
            source=item["source"]
        ))
        
    return final_results

@app.get("/health")
def health():
    return {"status": "ok", "vectors": len(memory_store)}
