from google.adk.agents import Agent

root_agent = Agent(
    name="test_gem_native",
    model="gemini-3.5-flash",
    instruction="You are a helpful assistant.",
)