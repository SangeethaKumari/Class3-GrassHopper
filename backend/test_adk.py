from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

model = LiteLlm("gemini/gemini-2.5-flash")

hr_agent = Agent(
    name="HR",
    description="HR agent",
    model=model
)

router = Agent(
    name="Router",
    description="Router",
    model=model,
    downstream_agents=[hr_agent]
)

print("ADK import and init successful.")
