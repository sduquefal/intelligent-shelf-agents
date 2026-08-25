from google.adk.agents import Agent
from common.models import get_default_model

from .subagents.shelf_analyst.agent import root_agent as shelf_analyst
from .subagents.store_coach.agent import root_agent as store_coach

# from .subagents.executive.agent import root_agent as executive
# from .subagents.root_cause.agent import root_agent as root_cause

root_agent = Agent(
    name="intelligent_shelf",
    model=get_default_model(),
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