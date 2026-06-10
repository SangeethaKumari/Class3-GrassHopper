import os
from dotenv import load_dotenv

# Load .env from parent directory
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from google.adk.agents import Agent
from google.adk.models import Gemini
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content

model = Gemini(model="gemini-2.5-flash")

hr_agent = Agent(
    name="HR_Agent",
    description="Handles questions regarding HR, such as maternity leave benefits.",
    instruction="You are an HR agent.",
    model=model
)

router_agent = Agent(
    name="Router_Agent",
    description="A router agent",
    instruction="DO NOT answer. Analyze and delegate to HR_Agent for maternity.",
    model=model,
    sub_agents=[hr_agent]
)

session_service = InMemorySessionService()
runner = Runner(
    app_name="router_app",
    agent=router_agent,
    session_service=session_service,
    auto_create_session=True
)

new_msg = Content(role="user", parts=[{"text": "maternity leave"}])
events = runner.run(
    user_id="user_123",
    session_id="session_456",
    new_message=new_msg
)

for event in events:
    print(type(event).__name__)
    if hasattr(event, "author"):
        print("author:", event.author)
    if hasattr(event, "content"):
        print(f"content type: {type(event.content)}")
        print(f"content: {event.content}")
    if hasattr(event, "agent_name"):
        print("agent_name:", getattr(event, "agent_name"))
