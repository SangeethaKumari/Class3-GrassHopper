import os
import warnings
import logging
import uuid
import json
from datetime import datetime
from typing import Literal, Optional
from dataclasses import dataclass
from dotenv import load_dotenv

warnings.filterwarnings("ignore", message=".*non-text parts.*")
logging.getLogger("google.genai").setLevel(logging.ERROR)

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from google.adk.agents import Agent
from google.adk.models import Gemini
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content

if "GEMINI_API_KEY" not in os.environ and "GOOGLE_API_KEY" not in os.environ:
    print("WARNING: GEMINI_API_KEY or GOOGLE_API_KEY is not set.")

model = Gemini(model="gemini-2.5-flash")


@dataclass
class DomainHandler:
    """Defines a support domain with its classifier hints and system prompt."""
    name: str
    category: Literal["hr", "insurance", "billing", "account", "general"]
    classifier_hints: str  # Words/phrases that indicate this domain
    system_prompt: str  # Instructions for handling this domain


# Domain definitions centralized
DOMAINS = [
    DomainHandler(
        name="HR",
        category="hr",
        classifier_hints="maternity leave, vacation, holidays, benefits, pto, sick days, policy",
        system_prompt=(
            "You are an HR specialist. Answer questions about leave benefits, company policies, "
            "and employee rights clearly and kindly. If unsure, offer to escalate."
        )
    ),
    DomainHandler(
        name="Insurance",
        category="insurance",
        classifier_hints="health insurance, dental, vision, life insurance, coverage, claims, deductible, premium",
        system_prompt=(
            "You are an insurance expert. Help with policy questions, coverage definitions, "
            "and claims guidance. Be accurate and reference plan documents when relevant."
        )
    ),
    DomainHandler(
        name="Billing",
        category="billing",
        classifier_hints="invoice, refund, charge, payment, billing, credit card, overcharge, receipt",
        system_prompt=(
            "You are a billing specialist. Process refund requests, explain charges, and provide "
            "timelines for dispute resolution. Keep communication professional."
        )
    ),
    DomainHandler(
        name="Account Management",
        category="account",
        classifier_hints="login, password, profile, account, user, identity, role, permission",
        system_prompt=(
            "You are an account management specialist. Help users update profile info, reset credentials, "
            "manage roles, and secure their accounts. Always verify identity before sensitive changes."
        )
    ),
    DomainHandler(
        name="General",
        category="general",
        classifier_hints="",
        system_prompt=(
            "You are a helpful general assistant. Answer knowledge questions, make friendly conversation, "
            "or clarify what the user needs. If it sounds like a specific domain, suggest they rephrase."
        )
    ),
]


def build_classifier_prompt(user_query: str) -> str:
    """Build a prompt to classify user intent."""
    domains_list = "\n".join([
        f"- {d.category}: {d.name} ({d.classifier_hints})"
        for d in DOMAINS
    ])
    return f"""
Classify the following user query into one of these categories:

{domains_list}

Query: "{user_query}"

Respond ONLY with the category name (one word, lowercase). No explanation.
"""


def classify_intent(user_query: str) -> str:
    """Use a single LLM call to classify the user's intent."""
    # In production, you'd use a structured output or simpler model.
    # For now, we do a single inference to get the category.
    
    classifier_agent = Agent(
        name="Classifier",
        description="Classifies user queries into support domains",
        instruction=build_classifier_prompt(user_query),
        model=model
    )
    
    classifier_session = InMemorySessionService()
    classifier_runner = Runner(
        app_name="classifier",
        agent=classifier_agent,
        session_service=classifier_session,
        auto_create_session=True
    )
    
    new_msg = Content(role="user", parts=[{"text": "Classify this"}])
    
    category = "general"
    for event in classifier_runner.run(user_id="classifier", session_id="1", new_message=new_msg):
        if hasattr(event, "content") and event.content and getattr(event.content, "role", "") == "model":
            for part in getattr(event.content, "parts", []):
                text_val = getattr(part, "text", None)
                if text_val:
                    result = text_val.strip().lower()
                    for domain in DOMAINS:
                        if domain.category in result:
                            category = domain.category
                            break
    
    return category


def get_domain_handler(category: str) -> DomainHandler:
    """Fetch the domain handler for a category."""
    for domain in DOMAINS:
        if domain.category == category:
            return domain
    return DOMAINS[-1]  # Return "General" as fallback


def log_interaction(
    user_query: str,
    category: str,
    response: str,
    user_id: str,
    session_id: str
) -> None:
    """Structured logging to JSON file."""
    log_file = "support_interactions.jsonl"
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "user_id": user_id,
        "session_id": session_id,
        "query": user_query,
        "category": category,
        "response_preview": response[:100],  # First 100 chars
    }
    
    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")
    except Exception as e:
        print(f"[Warning] Logging failed: {e}")


def run_chatbot() -> None:
    """Main chatbot loop with classifier-based dispatch."""
    print("\n" + "=" * 55)
    print("Support Portal Chatbot (Classifier Pattern)")
    print("Ask about HR, Insurance, Billing, or Account issues.")
    print("Type 'exit' or 'quit' to end.\n")
    print("=" * 55 + "\n")
    
    user_id = str(uuid.uuid4())
    session_id = str(uuid.uuid4())
    
    print(f"Session ID: {session_id[:8]}...\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['exit', 'quit']:
                print("Goodbye!")
                break
            
            if not user_input:
                continue
            
            # STEP 1: Classify intent (single LLM call)
            print("[Classifying query...]", end=" ", flush=True)
            category = classify_intent(user_input)
            domain = get_domain_handler(category)
            print(f"→ {domain.name}\n")
            
            # STEP 2: Get response from domain-optimized agent (single call with context)
            response_agent = Agent(
                name=f"{domain.name}_Responder",
                description=f"Handles {domain.name} queries",
                instruction=domain.system_prompt,
                model=model
            )
            
            response_session = InMemorySessionService()
            response_runner = Runner(
                app_name=f"{domain.name.lower()}_response",
                agent=response_agent,
                session_service=response_session,
                auto_create_session=True
            )
            
            new_msg = Content(role="user", parts=[{"text": user_input}])
            
            print("Chatbot: ", end="", flush=True)
            output = ""
            
            for event in response_runner.run(
                user_id=user_id,
                session_id=session_id,
                new_message=new_msg
            ):
                if hasattr(event, "content") and event.content and getattr(event.content, "role", "") == "model":
                    for part in getattr(event.content, "parts", []):
                        if getattr(part, "function_call", None) or getattr(part, "function_response", None):
                            continue
                        text_val = getattr(part, "text", None)
                        if text_val:
                            output += text_val
            
            if output:
                print(output)
                log_interaction(user_input, domain.category, output, user_id, session_id)
            else:
                print("(No response generated)")
            
            print(f"\n--- [{domain.name}] ---\n")
            
        except Exception as e:
            print(f"\n[Error] {str(e)}\n")


if __name__ == "__main__":
    run_chatbot()
