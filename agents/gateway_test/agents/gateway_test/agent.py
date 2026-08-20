
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

root_agent = Agent(
    name="gateway_test",
    model=LiteLlm(
        model="openai/gemini-3.5-flash",
    ),
    instruction="Answer briefly.",
)