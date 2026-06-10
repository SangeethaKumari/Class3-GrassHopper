import os
import warnings
import logging
from dotenv import load_dotenv

# Suppress annoying google-genai text parsing warnings
warnings.filterwarnings("ignore", message=".*non-text parts.*")
logging.getLogger("google.genai").setLevel(logging.ERROR)

# Load .env from parent directory
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from google.adk.agents import Agent
from google.adk.models import Gemini
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content

# Ensure API key is set or prompt the user
if "GEMINI_API_KEY" not in os.environ and "GOOGLE_API_KEY" not in os.environ:
    print("WARNING: GEMINI_API_KEY or GOOGLE_API_KEY is not set. Please set it to use the Gemini model.")

# Initialize the model
# The ADK uses the native Gemini integration directly.
model = Gemini(model="gemini-2.5-flash")

# Define Specialist Agents
hr_agent = Agent(
    name="HR_Agent",
    description="Handles questions regarding HR, such as maternity leave benefits, vacation durations, and company policies. Route here for employee benefits.",
    instruction="You are an HR agent. Answer questions specifically related to HR policies like leave benefits and holidays clearly and kindly.",
    model=model
)

insurance_agent = Agent(
    name="Insurance_Agent",
    description="Handles questions about health insurance, dental, vision, life insurance, out-of-pocket costs, and claims. Route here for medical coverage.",
    instruction="You are an Insurance agent. Help the user with their insurance policy questions accurately and guide them on coverage definitions.",
    model=model
)

billing_agent = Agent(
    name="Billing_Agent",
    description="Handles questions about billing issues, missing refunds, overcharges, credit card payments, and invoices. Route here for money matters.",
    instruction="You are a Billing agent. Process refund requests, clarify billing questions, and provide timelines for reversed charges.",
    model=model
    
)

account_mgmt_agent = Agent(
    name="Account_Management_Agent",
    description="Handles questions about account context, identifying who people are, updating profile info, or managing user roles. Route here for personal data.",
    instruction="You are an Account Management agent. Help users understand who someone is, fix login info, or manage their account settings securely.",
    model=model
    
)


general_agent = Agent(
    name="General_Agent",
    description="Handles general questions, casual conversation, and any queries that do not fit into HR, Insurance, Billing, or Account Management.",
    instruction="You are a helpful General Assistant. For general knowledge questions like weather or news, answer based on your capabilities (noting if you lack real-time data) or just be friendly for casual talk.",
    model=model
)
# Define Router Agent
router_agent = Agent(
    name="Router_Agent",
    description="A router agent that delegates queries to the appropriate specialist agent based on user intent.",
    global_instruction="USER CONTEXT: The user is an engineer who has been working with the company for 5 years and currently has health insurance.",
    instruction=(
        "You are a router coordinator. DO NOT answer questions directly. "
        "Analyze the user's query and delegate it to the best specialist agent. "
        "If you do not know the answer or lack an agent, apologize to the user."
    ),
    model=model,
    sub_agents=[hr_agent, insurance_agent, billing_agent, account_mgmt_agent, general_agent]
)

# Setup Session and Runner
session_service = InMemorySessionService()
runner = Runner(
    app_name="router_app",
    agent=router_agent,
    session_service=session_service,
    auto_create_session=True
)

def run_chatbot():
    print("\n=======================================================")
    print("Welcome to the Company Support Portal Chatbot!")
    print("I can route your request to HR, Insurance, Billing, or Account Management.")
    print("Type 'exit' or 'quit' to end the session.")
    print("=======================================================\n")
    
    user_id = "user_123"
    session_id = "session_456"

    while True:
        try:
            user_input = input("You: ")
            if user_input.lower() in ['exit', 'quit']:
                print("Goodbye!")
                break
            
            if not user_input.strip():
                continue

            # In ADK, we typically pass the query wrapped in a Content object,
            # or simply as a Content generation argument. 
            # The Runner.run() expects new_message of type genai.types.Content 
            # or a dictionary that can be parsed as Content.
            # Using raw string or proper Content formatting:
            new_msg = Content(role="user", parts=[{"text": user_input}])
            
            print("Chatbot: ", end="", flush=True)
            events = runner.run(
                user_id=user_id,
                session_id=session_id,
                new_message=new_msg
            )
            
            output = ""
            active_agent_name = None
            
            for event in events:
                # Check for the agent authoring the query component (excluding the Router)
                if hasattr(event, "author") and event.author and "Router" not in event.author:
                    active_agent_name = event.author

                # Look for model messages in the event.content
                if hasattr(event, "content") and event.content and getattr(event.content, "role", "") == "model":
                    text = ""
                    for part in getattr(event.content, "parts", []):
                        # Skip parts that invoke tools to prevent the SDK from printing a warning
                        if getattr(part, "function_call", None) or getattr(part, "function_response", None):
                            continue
                        text_val = getattr(part, "text", None)
                        if text_val:
                            text += text_val
                    output += text
            
            if output:
                print(output)
            else:
                print("... (Routed or waiting for completion -- no plain text received)")
                
            if active_agent_name:
                print(f"\n--- [Handled by Specialist Agent: {active_agent_name}] ---")
                
                # File logic: Create/Append to a file with the agent name
                file_name = f"{active_agent_name.lower()}_questions.txt"
                try:
                    with open(file_name, "a", encoding="utf-8") as f:
                        f.write(f"{user_input}\n")
                    print(f"--- [Success: Question logged to {file_name}] ---\n")
                except Exception as file_err:
                    print(f"--- [Warning: Failed to create or write to file {file_name}: {file_err}] ---\n")
        except Exception as e:
            print(f"\n[Error] {str(e)}")

if __name__ == "__main__":
    run_chatbot()
