import streamlit as st
import requests
import json
import os

# --- Configuration ---
# Use Env Var for Deployment URL (Defaults to localhost for dev)
API_BASE_URL = os.getenv("API_URL", "http://127.0.0.1:8000")
SEARCH_ENDPOINT = f"{API_BASE_URL}/search"

st.set_page_config(page_title="Deep Search", layout="centered")

# Custom CSS for that "Google" feel
st.markdown("""
<style>
    .main {
        background-color: #ffffff;
    }
    .stTextInput > div > div > input {
        border-radius: 24px;
        padding: 12px 24px;
        font-size: 16px; 
        border: 1px solid #dfe1e5;
        box-shadow: 0 1px 6px rgba(32,33,36,.28);
    }
    .stTextInput > div > div > input:focus {
        outline: none;
        box-shadow: 0 1px 6px rgba(32,33,36,.28); 
    }
    .result-card {
        background-color: white;
        padding: 18px;
        border-radius: 12px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border: 1px solid #f0f0f0;
        transition: transform 0.2s;
    }
    .result-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.1);
    }
    .result-score {
        float: right;
        font-size: 0.8em;
        color: #006400; /* Green for high score */
        font-weight: bold;
        background-color: #e6f4ea;
        padding: 2px 8px;
        border-radius: 4px;
    }
    .result-source {
        color: #5f6368;
        font-size: 0.85em;
        margin-bottom: 8px;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        font-weight: 600;
    }
    .result-content {
        font-size: 1.1em;
        color: #202124;
        line-height: 1.6;
        font-family: 'Georgia', serif; /* Serif for better reading */
    }
</style>
""", unsafe_allow_html=True)

st.title("🔎 Vector Search Engine")
st.caption(f"Connected to Backend: `{API_BASE_URL}`")

query = st.text_input("", placeholder="Ask a question about physics, politics, or anthropology...")

if query:
    try:
        with st.spinner("Searching knowledge base..."):
            response = requests.post(SEARCH_ENDPOINT, json={"query": query, "top_k": 5}, timeout=10)
            
        if response.status_code == 200:
            results = response.json()
            
            st.markdown(f"### Top Results for: *{query}*")
            st.markdown("---")
            
            if not results:
                st.warning("No relevant documents found.")
            
            for res in results:
                # Calculate percentage
                score_pct = f"{res['score']:.1%}"
                
                # Dynamic Card
                st.markdown(f"""
                <div class="result-card">
                    <span class="result-score">Matcher: {score_pct}</span>
                    <div class="result-source">{res['source']} • ID: {res['document_id']}</div>
                    <div class="result-content">{res['content']}</div>
                </div>
                """, unsafe_allow_html=True)
                
        else:
            st.error(f"Backend Error: {response.status_code}")
            st.json(response.json())
            
    except requests.exceptions.ConnectionError:
        st.error("🚨 **Connection Failed**")
        st.info(f"Could not reach `{API_BASE_URL}`. Is the backend running?")
    except Exception as e:
        st.error(f"An error occurred: {e}")

# Sidebar for debug info
with st.sidebar:
    st.header("Debug Info")
    if st.button("Check Backend Health"):
        try:
            health = requests.get(f"{API_BASE_URL}/health", timeout=2)
            st.success(f"Backend Online! Loaded Vectors: {health.json().get('vectors')}")
        except:
            st.error("Backend Offline")
