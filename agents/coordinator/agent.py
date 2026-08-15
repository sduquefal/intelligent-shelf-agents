from google.adk.agents import Agent

from agents.shelf_analyst.agent import root_agent as shelf_analyst
from agents.store_coach.agent import root_agent as store_coach
#from agents.executive.agent import root_agent as executive
#from agents.root_cause.agent import root_agent as root_cause

root_agent = Agent(
    name="intelligent_shelf",
    model="gemini-2.5-flash",
    description="Coordinator for Intelligent Shelf agents.",
    instruction="""
You are the Intelligent Shelf coordinator.

Never answer directly.

Always delegate to the most appropriate specialist.

Use Shelf Analyst when the user asks:

- How is a store performing?
- SNSG
- Bodega
- Quiebre
- Trends
- Rankings
- Comparisons
- Metrics
- Performance

Use Store Coach when the user asks:

- What should I do?
- How can I improve?
- Recommendations
- Action plans
- Priorities
- Next steps
- Corrective actions

The primary intent determines the specialist.
""",
    sub_agents=[
        shelf_analyst,
        store_coach,
        #executive,
        #root_cause,
    ],
)