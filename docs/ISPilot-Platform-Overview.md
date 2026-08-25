# ISPilot Platform Overview

## Executive Summary

ISPilot is an enterprise AI platform designed to provide retail business users with natural language access to Intelligent Shelf operational data.

The platform transforms operational metrics into actionable business insights through a specialized multi-agent architecture powered by:

- Google ADK
- Vertex AI Agent Engine
- Gemini
- BigQuery
- Secret Manager

Instead of requiring dashboards, SQL knowledge or analyst intervention, ISPilot enables users to interact with retail performance data using natural language.

---

# Business Vision

ISPilot is not a chatbot.

ISPilot is a retail intelligence platform powered by AI agents.

The objective is to create reusable business capabilities that can be consumed through:

- AI Agents
- APIs
- Microsoft Teams
- Copilot Studio
- Future applications

Business users should be able to ask:

```text
How is Talca Colin performing?

How can Talca Colin improve?

What are today's priorities?

What stores require immediate attention?
```

without needing direct access to dashboards or reports.

---

# Functional Architecture

```text
User
 │
 ▼
Coordinator Agent
 │
 ├── Shelf Analyst
 ├── Store Coach
 ├── Root Cause Agent (future)
 └── Executive Agent (future)
```

---

## Coordinator Agent

Responsible for:

- Intent classification
- Request routing
- Agent orchestration

Does not perform analytics.

Does not access data directly.

---

## Shelf Analyst

Answers:

```text
What is happening?
```

Examples:

```text
How is Chile today?

How is Talca Colin performing?

What are the rankings?

What are the trends?
```

---

## Store Coach

Answers:

```text
What should I do?
```

Examples:

```text
How can Talca Colin improve?

What actions should be prioritized?

What should be fixed first?
```

---

# Technology Stack

- Google ADK
- Vertex AI Agent Engine
- Gemini 2.5 Flash
- BigQuery
- Secret Manager
- Python 3.12

---

# Current Status

✅ Coordinator Agent

✅ Shelf Analyst

✅ Store Coach

✅ Multi-Agent Routing

✅ Vertex AI Agent Engine

✅ BigQuery Integration

✅ Secret Manager Integration

✅ REST API

✅ Vertex Playground Validation

✅ Ready for Copilot Studio Integration

✅ Ready for Microsoft Teams

---

# Production Runtime

Current production deployment:

```text
projects/390358249123/locations/us-central1/reasoningEngines/4655320687131492352
```

---

# Deployment

```bash
adk deploy agent_engine \
  --project=corp-stro-salesinventory-prod \
  --region=us-central1 \
  --display_name=intelligent-shelf-coordinator \
  --extra_packages common \
  --extra_packages services \
  --extra_packages gateways \
  --extra_packages repositories \
  --extra_packages domain \
  agents/coordinator
```

---

# Strategic Roadmap

## Phase 1

✅ Shelf Analyst

## Phase 2

✅ Store Coach

## Phase 3

Root Cause Agent

## Phase 4

Executive Agent

## Phase 5

Recommendation Engine

## Phase 6

Microsoft Teams Integration

## Phase 7

Enterprise Observability

## Phase 8

Enterprise AI Platform Expansion