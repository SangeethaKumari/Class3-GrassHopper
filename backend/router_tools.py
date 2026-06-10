import os
import warnings
import logging
import uuid
import json
from datetime import datetime
from typing import Any, Literal
from dataclasses import dataclass
from dotenv import load_dotenv

warnings.filterwarnings("ignore", message=".*non-text parts.*")
logging.getLogger("google.genai").setLevel(logging.ERROR)

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from google.adk.agents import Agent
from google.adk.models import Gemini
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Tool, FunctionDeclaration

if "GEMINI_API_KEY" not in os.environ and "GOOGLE_API_KEY" not in os.environ:
    print("WARNING: GEMINI_API_KEY or GOOGLE_API_KEY is not set.")

model = Gemini(model="gemini-2.5-flash")


@dataclass
class ToolConfig:
    """Configuration for a support domain tool."""
    name: str
    category: Literal["hr", "insurance", "billing", "account", "general"]
    description: str
    system_prompt: str


# Define domain tools
DOMAIN_TOOLS = [
    ToolConfig(
        name="handle_hr_query",
        category="hr",
        description="Handles HR-related questions about leave benefits, vacation, holidays, and company policies",
        system_prompt=(
            "You are an HR specialist. When the user asks about maternity leave, vacation, holidays, "
            "sick days, PTO, or company policies, use this tool. Answer clearly and kindly."
        )
    ),
    ToolConfig(
        name="handle_insurance_query",
        category="insurance",
        description="Handles questions about health insurance, dental, vision, life insurance, coverage, claims, deductibles, and premiums",
        system_prompt=(
            "You are an insurance expert. When the user asks about insurance coverage, claims, deductibles, "
            "or policy details, use this tool. Be accurate and reference plan documents when relevant."
        )
    ),
    ToolConfig(
        name="handle_billing_query",
        category="billing",
        description="Handles billing questions including invoices, refunds, charges, payments, credit cards, and overcharges",
        system_prompt=(
            "You are a billing specialist. When the user asks about invoices, refunds, charges, or payments, "
            "use this tool. Process requests professionally and provide timelines for resolution."
        )
    ),
    ToolConfig(
        name="handle_account_query",
        category="account",
        description="Handles account management including login, password reset, profile updates, roles, and permissions",
        system_prompt=(
            "You are an account management specialist. When the user asks about login, passwords, profiles, "
            "roles, or account access, use this tool. Always be security-conscious."
        )
    ),
]


def create_tool_definitions() -> list[Tool]:
    """Generate Tool definitions for the agent."""
    tools = []
    
    for tool_config in DOMAIN_TOOLS:
        tool = Tool(
            function_declarations=[
                FunctionDeclaration(
                    name=tool_config.name,
                    description=tool_config.description,
                    parameters={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The user's question or request"
                            },
                            "context": {
                                "type": "string",
                                "description": "Additional context about the user (employee tenure, benefits, etc.)"
                            }
                        },
                        "required": ["query"]
                    }
                )
            ]
        )
        tools.append(tool)
    
    return tools


def execute_tool(
    tool_name: str,
    query: str,
    context: str = ""
) -> dict[str, Any]:
    """Execute a domain-specific tool (stub implementation).
    
    In production, this would call actual backend APIs or databases.
    For this POC, we return structured responses.
    """
    response = {
        "tool": tool_name,
        "query": query,
        "status": "success",
        "category": None
    }
    
    # Map tool names to categories and response logic
    if "hr" in tool_name:
        response["category"] = "hr"
        response["answer"] = (
            f"As an HR specialist, I can help with: {query}\n\n"
            "Typical HR topics include:\n"
            "- Maternity/paternity leave (6-12 weeks typically)\n"
            "- Vacation: 20 days/year, can carry over 5 days\n"
            "- Sick days: Unlimited with manager approval\n"
            "- Company policies are in the employee handbook"
        )
    elif "insurance" in tool_name:
        response["category"] = "insurance"
        response["answer"] = (
            f"As an insurance expert, regarding: {query}\n\n"
            "Key coverage details:\n"
            "- Health insurance: $500 deductible, 80/20 coinsurance\n"
            "- Dental: Covered up to 80% after $100 deductible\n"
            "- Vision: Annual eye exam + $200 glasses allowance\n"
            "- Life insurance: 2x annual salary, company-paid"
        )
    elif "billing" in tool_name:
        response["category"] = "billing"
        response["answer"] = (
            f"As a billing specialist, addressing: {query}\n\n"
            "For billing issues:\n"
            "- Refund requests: 3-5 business days after approval\n"
            "- Dispute resolution: Submit within 30 days\n"
            "- Payment methods: Credit card, ACH, check\n"
            "- All invoices available in your account portal"
        )
    elif "account" in tool_name:
        response["category"] = "account"
        response["answer"] = (
            f"As an account specialist, helping with: {query}\n\n"
            "Account management:\n"
            "- Password reset: Use 'Forgot Password' on login page\n"
            "- Profile updates: Available in account settings\n"
            "- Role changes: Requires manager approval\n"
            "- 2FA: Recommended for security"
        )
    else:
        response["status"] = "error"
        response["answer"] = "Tool not found"
    
    return response


def log_interaction(
    user_query: str,
    category: str,
    tool_used: str,
    response: str,
    user_id: str,
    session_id: str
) -> None:
    """Log interaction to JSONL file."""
    log_file = "support_interactions.jsonl"
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "user_id": user_id,
        "session_id": session_id,
        "query": user_query,
        "category": category,
        "tool_used": tool_used,
        "response_preview": response[:100],
    }
    
    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")
    except Exception as e:
        print(f"[Warning] Logging failed: {e}")


def build_system_prompt() -> str:
    """Build the main system prompt with tool instructions."""
    tool_list = "\n".join([
        f"- {t.name}: {t.description}"
        for t in DOMAIN_TOOLS
    ])
    
    return f"""You are a support coordinator agent. Your job is to help users with their questions.

You have access to these tools:
{tool_list}

When a user asks a question:
1. Determine which tool best handles their query
2. Call that tool with the user's question
3. Format the tool's response into a helpful answer

If the query doesn't fit any tool, answer directly as a helpful general assistant.

IMPORTANT: Only call ONE tool per user query. Don't call multiple tools unless the user asks about multiple domains.

USER CONTEXT: The user is an engineer who has been working with the company for 5 years.
They currently have health insurance. Use this context to personalize your responses."""


def run_chatbot() -> None:
    """Main chatbot loop with tools-based dispatch."""
    print("\n" + "=" * 55)
    print("Support Portal Chatbot (Tools-Based)")
    print("Ask about HR, Insurance, Billing, or Account issues.")
    print("Type 'exit' or 'quit' to end.\n")
    print("=" * 55 + "\n")
    
    user_id = str(uuid.uuid4())
    session_id = str(uuid.uuid4())
    
    print(f"Session ID: {session_id[:8]}...\n")
    
    # Create tool definitions
    tools = create_tool_definitions()
    
    # Create single multi-purpose agent with tools
    coordinator_agent = Agent(
        name="Support_Coordinator",
        description="Routes user queries to appropriate support tools",
        instruction=build_system_prompt(),
        model=model,
        tools=tools  # Pass all tools to the agent
    )
    
    session_service = InMemorySessionService()
    runner = Runner(
        app_name="support_chatbot",
        agent=coordinator_agent,
        session_service=session_service,
        auto_create_session=True
    )
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['exit', 'quit']:
                print("Goodbye!")
                break
            
            if not user_input:
                continue
            
            # Send user query to agent
            new_msg = Content(role="user", parts=[{"text": user_input}])
            
            print("Chatbot: ", end="", flush=True)
            
            output = ""
            tool_calls = []
            tool_results = []
            
            # Stream events from the agent
            for event in runner.run(
                user_id=user_id,
                session_id=session_id,
                new_message=new_msg
            ):
                # Handle tool calls made by the agent
                if hasattr(event, "content") and event.content:
                    for part in getattr(event.content, "parts", []):
                        # Detect function calls
                        if hasattr(part, "function_call") and part.function_call:
                            tool_name = part.function_call.name
                            tool_args = part.function_call.args
                            
                            tool_calls.append(tool_name)
                            
                            # Execute the tool
                            result = execute_tool(
                                tool_name=tool_name,
                                query=tool_args.get("query", ""),
                                context=tool_args.get("context", "")
                            )
                            tool_results.append(result)
                            print(f"[Using {tool_name}]", end=" ", flush=True)
                        
                        # Extract text responses
                        elif hasattr(part, "text") and part.text:
                            output += part.text
                
                # Handle model responses
                if hasattr(event, "content") and event.content and getattr(event.content, "role", "") == "model":
                    for part in getattr(event.content, "parts", []):
                        if getattr(part, "function_response", None):
                            continue
                        text_val = getattr(part, "text", None)
                        if text_val:
                            output += text_val
            
            if output:
                print(output)
                
                # Log the interaction
                category = "general"
                tool_used = "none"
                if tool_results:
                    category = tool_results[0].get("category", "general")
                    tool_used = tool_results[0].get("tool", "none")
                
                log_interaction(
                    user_query=user_input,
                    category=category,
                    tool_used=tool_used,
                    response=output,
                    user_id=user_id,
                    session_id=session_id
                )
            else:
                print("(No response generated)")
            
            if tool_results:
                print(f"\n--- [Tool: {tool_results[0].get('tool', 'unknown')}] ---\n")
            else:
                print()
            
        except Exception as e:
            print(f"\n[Error] {str(e)}\n")


if __name__ == "__main__":
    run_chatbot()
