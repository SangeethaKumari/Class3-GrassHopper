import os
import time
import warnings
import logging
from dotenv import load_dotenv

# Suppress annoying google-genai text parsing warnings
warnings.filterwarnings("ignore", message=".*non-text parts.*")
logging.getLogger("google.genai").setLevel(logging.ERROR)

# Load .env from parent's parent directory
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

from google.adk.agents import Agent
from google.adk.models import Gemini
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content

# ==========================================
# 1. Define the Tools
# ==========================================
def read_from_file(filepath: str) -> str:
    """Read contents from a file and return the text."""
    print(f"\n[Tool Execution Started: read_from_file('{filepath}')]")
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"!!! ROOT ERROR: File '{filepath}' mysteriously vanished! !!!")
        return f"Error: The file {filepath} does not exist. It may have been mysteriously deleted. You must recreate it by scanning the original transcript again."

def write_to_file(filepath: str, content: str) -> str:
    """Save content to a file. Call this tool when building the temporary action items list."""
    print(f"\n[Tool Execution Started: write_to_file('{filepath}')]")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    
    print("\n" + "="*50)
    print(f"-> SUCCESS: Saved {filepath} to the hard drive.")
    print("-> TIMER STARTED! YOU HAVE 10 SECONDS TO DELETE IT IN YOUR EDITOR!")
    print("="*50 + "\n")
    
    for i in range(10, 0, -1):
        print(f"Sabotage countdown... {i}s")
        time.sleep(1)
        
    print("\n-> TIMER FINISHED. The agent will now attempt its next step...")
    
    return f"Success: Content written to {filepath}"

# ==========================================
# 2. Define the Agent
# ==========================================
model = Gemini(model="gemini-2.5-flash")

backtrack_agent = Agent(
    name="Backtracking_Test_Agent",
    description="An agent capable of reading and writing to the local filesystem.",
    instruction=(
        "You have tools to read and write files in the current directory. Follow these steps exactly:\n"
        "1. Use the read tool on 'messy_transcript.txt'.\n"
        "2. Extract only the actionable to-do items from it.\n"
        "3. Use the write tool to save those action items to a new file named 'action_items.tmp'.\n"
        "4. Critical Step: Read 'action_items.tmp' to verify the contents.\n"
        "5. Translate those contents into Spanish and output it to the user.\n"
        "IMPORTANT: If a file you expect to read is suddenly missing, calmly rethink your plan from step 1 and completely recreate the missing file before proceeding."
    ),
    tools=[read_from_file, write_to_file],
    model=model
)

session_service = InMemorySessionService()
runner = Runner(
    app_name="backtrack_test",
    agent=backtrack_agent,
    session_service=session_service,
    auto_create_session=True
)

def run_experiment():
    # Make sure we are in the correct directory regardless of where it's run
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    print("=====================================================================")
    print("Starting Interrupted Agent Experiment...")
    print("Wait for the 10-second countdown, then quickly delete the .tmp file!")
    print("=====================================================================")
    
    prompt = "Hi! Please process messy_transcript.txt according to your system instructions!"
    new_msg = Content(role="user", parts=[{"text": prompt}])
    
    print("\n[Thinking...] The Agent is planning its actions...")
    events = runner.run(user_id="user_exp", session_id="exp_session", new_message=new_msg)
    
    for event in events:
        if hasattr(event, "content") and event.content and getattr(event.content, "role", "") == "model":
            text = ""
            for part in getattr(event.content, "parts", []):
                if getattr(part, "function_call", None) or getattr(part, "function_response", None):
                    continue
                if hasattr(part, "text") and part.text:
                    text += part.text
            if text.strip():
                print(f"\n[Agent Chat Output]:\n{text.strip()}")

if __name__ == "__main__":
    run_experiment()
