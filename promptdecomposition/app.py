import streamlit as st
import requests
import time

# --- Configuration ---
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "codegemma:7b"

def call_llm(prompt):
    """Calls the local Ollama API."""
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=90)
        if response.status_code == 200:
            return response.json().get("response", "Error: No response content.")
        else:
            return f"Error: LLM returned status code {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"

# --- UI Header ---
st.set_page_config(page_title="Prompt Deconstructor", page_icon="🧩", layout="wide")

st.markdown("""
    <style>
    .main {
        background-color: #0f172a;
    }
    .stMarkdown h1 {
        background: linear-gradient(135deg, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        text-align: center;
    }
    .step-card {
        background: rgba(30, 41, 59, 0.7);
        padding: 20px;
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🧩 Prompt Deconstructor")
st.markdown("<p style='text-align: center; color: #94a3b8;'>Breaking monolithic tasks into modular excellence.</p>", unsafe_allow_html=True)

# --- Input Area ---
with st.container():
    user_task = st.text_area("Enter a complex goal (e.g., 'Write a comprehensive guide on quantum computing for kids'):", height=100)
    compare_mode = st.checkbox("Show Monolithic Comparison (Baseline)", value=True)
    start_btn = st.button("Decompose & Build ✨", use_container_width=True)

if start_btn and user_task:
    if compare_mode:
        with st.status("🐢 Generating Monolithic Baseline...", expanded=False):
            mono_prompt = f"Write a complete, comprehensive guide about: {user_task}. Include all necessary details in one go."
            mono_result = call_llm(mono_prompt)
            st.session_state.mono_result = mono_result

    # --- Step 1: Decomposition ---
    with st.status("🛠️ Step 1: Decomposing Task...", expanded=True) as status:
        st.write("Analyzing goal for modular steps...")
        decomp_prompt = f"""
        Analyze the following task and break it down into exactly 3 modular sub-tasks that can be executed sequentially.
        Task: {user_task}
        Respond ONLY with a bulleted list of the 3 sub-tasks.
        """
        subtasks_raw = call_llm(decomp_prompt)
        st.session_state.subtasks = [s.strip("- ") for s in subtasks_raw.split("\n") if s.strip()]
        status.update(label="✅ Step 1: Task Decomposed", state="complete")

    # Display Subtasks
    cols = st.columns(len(st.session_state.subtasks))
    for i, task in enumerate(st.session_state.subtasks):
        with cols[i]:
            st.markdown(f"<div class='step-card'><b>Sub-task {i+1}</b><br>{task}</div>", unsafe_allow_html=True)

    # --- Step 2: Modular Execution ---
    st.divider()
    st.subheader("🚀 Modular Execution")
    
    final_content = []
    
    for i, task in enumerate(st.session_state.subtasks):
        with st.expander(f"Executing: {task}", expanded=True):
            with st.spinner(f"Generating content for Step {i+1}..."):
                exec_prompt = f"Complete the following specialized sub-task as part of a larger project on '{user_task}':\n\nTask: {task}\n\nProvide a high-quality, professional response."
                result = call_llm(exec_prompt)
                st.markdown(result)
                final_content.append(result)
    
    # --- Step 3: Synthesis ---
    st.divider()
    with st.status("🔗 Step 3: Synthesizing Final Result...", expanded=True) as status:
        st.write("Combining modular components into a unified guide...")
        synthesis_prompt = f"""
        Combine the following modular components into a cohesive, well-structured guide about '{user_task}'. 
        Ensure smooth transitions between sections.
        
        Components:
        {' '.join(final_content)}
        """
        final_guide = call_llm(synthesis_prompt)
        status.update(label="✅ Website Ready!", state="complete")

    # --- Final Comparison Reveal ---
    st.divider()
    if compare_mode:
        col1, col2 = st.columns(2)
        with col1:
            st.header("💩 Monolithic Output")
            st.info("Generated using a single 'all-in-one' prompt. Often less detailed or structured.")
            st.markdown(st.session_state.mono_result)
        with col2:
            st.header("✨ Modular Output")
            st.success("Generated via Decomposition. Each section handled by a specialized prompt segment.")
            st.markdown(final_guide)
    else:
        st.subheader("🌟 Final Dynamic Result")
        st.markdown(final_guide)
    
    st.download_button("Download Complete Guide", final_guide, file_name="modular_guide.md")
else:
    st.info("Paste a complex idea above to see how Prompt Decomposition works in real-time.")
