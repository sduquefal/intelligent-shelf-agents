# 🚧 Project Status

**Active Development (MVP)**

# ISPilot

ISPilot is an enterprise AI platform designed to provide retail business users with natural language access to Intelligent Shelf operational data.

The platform transforms operational metrics into actionable business insights through a specialized multi-agent architecture built on:

- Google ADK
- Vertex AI Agent Engine
- Gemini
- BigQuery
- Secret Manager

Instead of navigating dashboards, reports, or SQL queries, users can interact directly with retail data using natural language.

---

# Business Vision

ISPilot is not a chatbot.

ISPilot is a business intelligence platform powered by AI agents.

The objective is to create reusable business capabilities that can be consumed through:

- AI Agents
- APIs
- Microsoft Teams
- Copilot Studio
- Future Enterprise Applications

Business users should be able to ask:

```text
How is Talca Colin performing?

How can Talca Colin improve?

What are today's priorities?

Which stores need immediate attention?
```

without requiring dashboards, reports or analyst intervention.

---

# What Makes ISPilot Different

## Traditional Model

```text
Business User
      │
      ▼
 Dashboard
      │
      ▼
  Analyst
      │
      ▼
 Decision
```

## ISPilot Model

```text
Business User
        │
        ▼
  Coordinator Agent
        │
        ▼
 Specialized Agent
        │
        ▼
 Business Services
        │
        ▼
    BigQuery
        │
        ▼
 Business Insight
```

Benefits:

- Faster decision making
- Reduced analyst dependency
- Consistent recommendations
- Natural language interaction
- Reusable business services

---

# Current Architecture

```text
                    ISPilot

                User Interfaces

      Teams │ Web │ Looker │ API │ Future Apps
                        │
                        ▼
                 Coordinator Agent
                        │
        ┌───────────────┼───────────────┐
        │               │               │
  Shelf Analyst    Store Coach   Future Agents
        │
        └───────────────┬────────────────────┐
                        │
                 Business Services
                        │
      Analytics │ Stores │ Alerts │ Inventory
                        │
                     Gateways
                        │
         BigQuery │ Vertex AI │ Future APIs
```

---

# Multi-Agent Architecture

ISPilot uses a hierarchical multi-agent architecture implemented with Google ADK.

The Coordinator Agent acts as the single entry point and delegates requests to specialized business agents.

## Agent Responsibilities

| Agent | Business Question |
|---------|---------|
| Coordinator | Who should answer? |
| Shelf Analyst | What is happening? |
| Store Coach | What should I do? |
| Root Cause Agent | Why is it happening? *(future)* |
| Executive Agent | What does it mean for the business? *(future)* |

---

## Coordinator Agent

Responsibilities:

- Intent detection
- Agent routing
- Delegation
- Conversation orchestration

Coordinator does **not**:

- Query BigQuery
- Execute business logic
- Generate recommendations

Its responsibility is orchestration.

---

## Shelf Analyst

Mission:

```text
What is happening?
```

Examples:

```text
How is Chile today?

How is Talca Colin performing?

What are the rankings?

What are the trends?

Compare today versus yesterday.
```

Current Capabilities:

- Country Summary
- Store Summary
- Store Name Resolution
- Store Code Resolution
- Ambiguous Store Detection
- Rankings
- Daily Comparisons
- Historical Trends
- Natural Language Analytics

Example Flow:

```text
User
 │
 ▼
Coordinator
 │
 ▼
Shelf Analyst
 │
 ▼
Business Services
 │
 ▼
BigQuery
```

---

## Store Coach

Mission:

```text
What should I do?
```

Examples:

```text
How can Talca Colin improve?

What should the manager do?

What actions should be prioritized?

What should be fixed first?
```

Current Capabilities:

- Operational Recommendations
- Store Improvement Guidance
- Corrective Actions
- Prioritization Support
- Action Plans

Store Coach consumes analytical outputs and converts them into actionable recommendations.

---

# Project Structure

```text
intelligent-shelf-agents/

├── agents/
│   └── coordinator/
│       ├── agent.py
│       ├── requirements.txt
│       ├── .agent_engine_config.json
│       └── subagents/
│           ├── shelf_analyst/
│           ├── store_coach/
│           ├── executive/
│           └── root_cause/
│
├── common/
│   ├── config.py
│   ├── bigquery_client.py
│   ├── gateway_gemini.py
│   └── gateway_token.py
│
├── gateways/
│   ├── nsg_gateway.py
│   └── store_gateway.py
│
├── services/
│   ├── analytics_service.py
│   └── store_service.py
│
├── repositories/
│
├── domain/
│
└── tests/
```

---

# Business Terminology

| Business Term | Technical Metric |
|--------------|------------------|
| SNSG | N_ON_SHELF |
| En Góndola | ON_SHELF |
| Bodega | OOS_SHELF |
| Quiebre | OOS_STORE |

Business users should interact using business terminology rather than technical metric names.

---

# Current Features

## Shelf Analyst

### Current Capabilities

- Country KPIs
- Store KPIs
- Store Name Resolution
- Store Code Resolution
- Rankings
- Daily Comparisons
- Historical Trends
- Natural Language Analytics

### Examples

```text
How is Chile today?

How is store 101?

How is San Bernardo Plaza?

How is San Bernardo?

What are the worst performing stores?
```

---

## Store Coach

### Current Capabilities

- Recommendations
- Prioritization
- Operational Guidance
- Action Plans
- Store Coaching

### Examples

```text
How can store 101 improve?

What should I do to improve SNSG?

What are the main priorities for this store?

What actions should be taken first?
```

---

# Technology Stack

## Core Platform

- Google ADK
- Gemini 2.5 Flash
- Vertex AI Agent Engine
- BigQuery
- Secret Manager
- Python 3.12

## Architectural Patterns

- Multi-Agent Architecture
- Clean Architecture
- Gateway Pattern
- Service Layer
- Domain Objects
- Coordinator Orchestration Pattern

---

# Current Status

## Operational

✅ Coordinator Agent

✅ Shelf Analyst

✅ Store Coach

✅ Vertex AI Agent Engine

✅ BigQuery Integration

✅ Secret Manager Integration

✅ Multi-Agent Routing

✅ REST API Validation

✅ Vertex Playground Validation

---

## Next Milestones

- Root Cause Agent
- Executive Agent
- Recommendation Engine
- Microsoft Teams Integration
- Copilot Studio Integration
- Enterprise APIs
- Observability & Telemetry

---

# Deployment

Production deployments use Google ADK Agent Engine.

## Deploy Command

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

# Runtime Configuration

Runtime configuration is centralized in:

```text
agents/coordinator/.agent_engine_config.json
```

Example:

```json
{
  "service_account": "sa-tot-osa@corp-stro-salesinventory-prod.iam.gserviceaccount.com",
  "env_vars": {
    "IS_BQ_PROJECT": "corp-stro-salesinventory-prod",
    "IS_BQ_DATASET": "acc_tot_cp_is_prd",
    "IS_NSG_REPORT_VIEW": "vw_nsg_report",
    "IS_CLASSIFICATION_VIEW": "vw_smartnsg_classification_cl_v2"
  }
}
```

Subagents do not require their own deployment configuration.

---

# Authentication

## Runtime Service Account

```text
sa-tot-osa@corp-stro-salesinventory-prod.iam.gserviceaccount.com
```

## Required Permissions

### Secret Manager

```text
roles/secretmanager.secretAccessor
```

Required Secret:

```text
genai-gateway-jwt-prod
```

### Service Usage

```text
roles/serviceusage.serviceUsageConsumer
```

### BigQuery

```text
roles/bigquery.jobUser

roles/bigquery.dataViewer
```

---

# Local Development

Authentication:

```bash
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/sa-tot-osa.json
```

Start locally:

```bash
adk web agents/coordinator
```

Production runtimes running in Vertex Agent Engine must use the runtime service account and should not rely on local JSON credentials.

---

# Future Channels

ISPilot is designed to be consumed through:

- Vertex Playground
- REST APIs
- Microsoft Teams
- Copilot Studio
- Enterprise Applications
- Future Mobile Experiences

---
# Documentation

Additional documentation is available in:

```text
docs/
├── ISPilot-Platform-Overview.md
└── ISPilot-Enterprise-Architecture-And-Vertex-Agent-Engine-Guide.md
```

## Document Purpose

### ISPilot-Platform-Overview.md

Executive overview of the platform including:

- Business vision
- Multi-agent architecture
- Current capabilities
- Technology stack
- Strategic roadmap

### ISPilot-Enterprise-Architecture-And-Vertex-Agent-Engine-Guide.md

Technical reference covering:

- Business architecture
- Multi-agent design
- ADK implementation
- Vertex Agent Engine deployment
- Security model
- REST API integration
- Troubleshooting history
- Operational runbook
- Teams and Copilot Studio integration strategy
```

---

# Strategic Roadmap

## Phase 1 ✅

- Country KPIs
- Store KPIs
- Store Resolution

## Phase 2 ✅

- Store Coach
- Recommendations
- Action Plans

## Phase 3

- Root Cause Analysis Agent

## Phase 4

- Executive Agent

## Phase 5

- Recommendation Engine

## Phase 6

- Microsoft Teams Integration
- Copilot Studio Integration

## Phase 7

- Enterprise APIs
- Agent Evaluations
- Observability & Telemetry

## Phase 8

- Enterprise AI Platform Expansion

---

# Long-Term Vision

The goal is to evolve ISPilot into an enterprise AI platform capable of supporting:

- Retail Operations
- Category Management
- Supply Chain
- Commercial Execution
- Executive Decision-Making

through a collection of specialized AI agents sharing a common business foundation.

The platform should provide natural language interaction while maintaining a clean separation between:

- AI Orchestration
- Business Rules
- Analytics Services
- Data Access Layers
- Enterprise Integrations