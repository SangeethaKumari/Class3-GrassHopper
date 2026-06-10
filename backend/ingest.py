import os
import sqlite3
import pandas as pd
from sentence_transformers import SentenceTransformer
import numpy as np
import pickle

# --- Configuration ---
# Use relative paths for cloud deployment compatibility
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
SOURCE_CSV = os.path.join(DATA_DIR, "dataset.csv")

# Ensure the data directory exists
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

DB_PATH = os.path.join(DATA_DIR, "wiki_chunks.db")
VECTOR_STORE_PATH = os.path.join(DATA_DIR, "vector_store.pkl")

def init_db():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            full_text TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE chunks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id INTEGER,
            content TEXT,
            FOREIGN KEY(document_id) REFERENCES documents(id)
        )
    ''')
    conn.commit()
    return conn

def ingest_data():
    print(f"--- Starting Ingestion using {SOURCE_CSV} ---")
    
    if not os.path.exists(SOURCE_CSV):
        print(f"ERROR: Dataset not found at {SOURCE_CSV}")
        # In a real build pipeline, we might download it here if missing
        return

    print("Loading SentenceTransformer model...")
    # This might take a while on a small instance
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    conn = init_db()
    cursor = conn.cursor()
    
    print("Reading CSV...")
    data = []
    with open(SOURCE_CSV, 'r', encoding='utf-8') as f:
        # Skip header
        header = next(f)
        for line in f:
            line = line.strip()
            if not line:
                continue
            # Split only on the first comma
            parts = line.split(',', 1)
            if len(parts) == 2:
                data.append({'label': parts[0], 'text': parts[1]})
    
    df = pd.DataFrame(data)

    unique_labels = df['label'].unique()
    label_to_doc_id = {}
    
    print(f"Found {len(unique_labels)} documents. Creating DB entries...")
    for label in unique_labels:
        full_text = " ".join(df[df['label'] == label]['text'].tolist())
        cursor.execute("INSERT INTO documents (title, full_text) VALUES (?, ?)", (label, full_text))
        doc_id = cursor.lastrowid
        label_to_doc_id[label] = doc_id

    print("Generating Embeddings & Storing Chunks...")
    vector_data = []
    chunk_count = 0
    
    for index, row in df.iterrows():
        text = row['text']
        label = row['label']
        doc_id = label_to_doc_id[label]
        
        cursor.execute("INSERT INTO chunks (document_id, content) VALUES (?, ?)", (doc_id, text))
        chunk_id = cursor.lastrowid
        
        embedding = model.encode(text)
        
        vector_data.append({
            "chunk_id": chunk_id,
            "document_id": doc_id,
            "embedding": embedding,
            "source": label
        })
        
        chunk_count += 1
        if chunk_count % 50 == 0:
            print(f"   Processed {chunk_count} chunks...")

    conn.commit()
    conn.close()
    
    print(f"Saving vector store to {VECTOR_STORE_PATH}...")
    with open(VECTOR_STORE_PATH, "wb") as f:
        pickle.dump(vector_data, f)
        
    print("--- Ingestion Complete ---")

if __name__ == "__main__":
    ingest_data()
