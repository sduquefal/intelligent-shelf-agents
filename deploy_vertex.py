import vertexai
from vertexai import agent_engines
from vertexai.agent_engines import AdkApp

from agents.coordinator.agent import root_agent

vertexai.init(
    project="corp-stro-salesinventory-prod",
    location="us-central1",
    staging_bucket="gs://is_data",
)

app = AdkApp(
    agent=root_agent,
)

remote_agent = agent_engines.create(
    app,
    display_name="ispilot-coordinator",
    service_account=(
        "sa-tot-osa@corp-stro-salesinventory-prod.iam.gserviceaccount.com"
    ),
    requirements=[
        "google-adk==2.7.1",
        "google-cloud-bigquery",
        "google-cloud-secret-manager",
        "google-cloud-aiplatform",
        "google-genai",
    ],
    extra_packages=[
        "dist/intelligent_shelf_agents-0.1.0-py3-none-any.whl"
    ],
)

print(remote_agent.resource_name)