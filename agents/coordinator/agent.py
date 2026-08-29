import time
import logging
from contextlib import contextmanager

from google.adk.agents import Agent
from common.models import get_default_model

from .subagents.shelf_analyst.agent import root_agent as shelf_analyst
from .subagents.store_coach.agent import root_agent as store_coach

# from .subagents.executive.agent import root_agent as executive
# from .subagents.root_cause.agent import root_agent as root_cause

# Setup logging for metrics
logger = logging.getLogger(__name__)


@contextmanager
def track_agent_operation(agent_name: str, operation: str):
    """Context manager to track agent operation latency.
    
    Args:
        agent_name: Name of the agent
        operation: Operation being tracked (e.g., 'invoke', 'route')
    
    Yields:
        None
        
    Example:
        with track_agent_operation("shelf_analyst", "query_handler"):
            response = await agent.invoke(message)
    """
    start_time = time.time()
    try:
        yield
    finally:
        latency_ms = (time.time() - start_time) * 1000
        log_msg = f"[AGENT_METRICS] {agent_name}.{operation} latency_ms={latency_ms:.2f}"
        logger.info(log_msg)
        print(f"✓ {log_msg}")


root_agent = Agent(
    name="ispilot_coordinator",
    model=get_default_model(),
    description="Coordinator for IsPilot agents.",
    instruction="""
You are the IsPilot coordinator.

Never answer directly.

Always delegate to the most appropriate specialist.

Use IsPilot Analyst when the user asks:

- How is a store performing?
- SNSG
- Bodega
- Quiebre
- Trends
- Rankings
- Comparisons
- Metrics
- Performance

Use IsPilot Coach when the user asks:

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