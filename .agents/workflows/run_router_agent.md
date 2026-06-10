---
description: Run the router_agent Python script using uv
---

## Prerequisites
1. Ensure you have **uv** installed. If not, install via:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
2. Have a valid **.env** file in the project root (one level above `backend/`) containing your Gemini API key:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```
   The script loads this file using `load_dotenv`.
3. The project dependencies are defined in `backend/pyproject.toml`. Ensure it exists.

## Steps
1. **Navigate to the backend directory**
   ```bash
   cd backend
   ```
2. **Synchronize dependencies** (install them)
   ```bash
   uv sync
   ```
   This reads `pyproject.toml` and creates a virtual environment under `.venv`.
3. **Activate the virtual environment** (optional if you prefer to run via uv directly)
   ```bash
   source .venv/bin/activate
   ```
4. **Run the router agent**
   ```bash
   uv run router_agent.py
   ```
   The script will start an interactive chatbot. Type your queries (e.g., "I need to know about my leave policy") and type `exit` or `quit` to stop.

## Common Issues & Fixes
- **`pyproject.toml` not found**: Make sure you are in the `backend/` directory when running `uv sync`. The file lives there.
- **Missing API key**: If the script prints a warning about `GEMINI_API_KEY` or `GOOGLE_API_KEY`, add the key to the `.env` file.
- **Import errors**: Ensure the `google-adk` package is listed in `pyproject.toml` and installed by `uv sync`.
- **Async thread errors**: These often arise when the model cannot be reached (invalid API key) or network issues. Verify connectivity and key validity.

## Optional: Run without activating the venv
If you prefer not to manually activate the venv, you can skip step 3 and directly run:
```bash
uv run --with google-adk router_agent.py
```
`uv run` will automatically use the environment created by `uv sync`.

---
*End of workflow*
