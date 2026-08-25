# 🚧 Project Status

**Active Development (MVP)**

# Intelligent Shelf AI Platform

An enterprise-grade AI platform for retail operations built on Google ADK, Vertex AI and BigQuery.

The platform enables business users to interact with Intelligent Shelf data using natural language, transforming operational metrics into actionable business insights.

---

# Vision

Intelligent Shelf AI Platform is designed as a multi-agent system where each AI agent specializes in a different business capability while sharing the same business services and data layer.

Instead of building isolated chatbots, the objective is to build reusable business services that can be consumed by multiple AI agents, dashboards and APIs.

---

# Current Architecture

```text
                    Intelligent Shelf AI Platform

                    User Interfaces

      Teams │ Web │ Looker │ API │ Future Apps
                        │
                Google ADK Agents
                        │
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

The platform uses a hierarchical multi-agent architecture implemented with Google ADK.

The Coordinator Agent acts as the single entry point and delegates requests to specialized business agents.

Current agents:

- Coordinator Agent
- Shelf Analyst
- Store Coach

Planned agents:

- Executive Agent
- Root Cause Agent

Example flow:

```text
User
  │
  ▼
Coordinator Agent
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

The Coordinator never implements business analytics directly.

Its responsibility is orchestration and delegation.

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
| En góndola | ON_SHELF |
| Bodega | OOS_SHELF |
| Quiebre | OOS_STORE |

Business users should interact using business terminology rather than technical metric names.

---

# Current Features

## Shelf Analyst

Current capabilities:

- Country summary
- Store summary
- Store name resolution
- Store code resolution
- Ambiguous store detection
- Natural language analytics

Examples:

```text
How is Chile today?

How is store 101?

How is San Bernardo Plaza?

How is San Bernardo?
```

---

## Store Coach

Current capabilities:

- Operational recommendations
- Store improvement guidance
- Corrective actions
- Prioritization support

Examples:

```text
How can store 101 improve?

What should I do to improve SNSG?

What are the main priorities for this store?
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

- Clean Architecture
- Gateway Pattern
- Service Layer
- Domain Objects
- Multi-Agent Architecture

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

Agent Engine runtime configuration is centralized in:

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

# Required Environment Variables

The platform requires the following runtime variables:

```text
GOOGLE_CLOUD_PROJECT

IS_BQ_PROJECT

IS_BQ_DATASET

IS_NSG_REPORT_VIEW

IS_CLASSIFICATION_VIEW
```

---

# Authentication

## Runtime Service Account

Production deployments use:

```text
sa-tot-osa@corp-stro-salesinventory-prod.iam.gserviceaccount.com
```

## Required Permissions

### Secret Manager

```text
roles/secretmanager.secretAccessor
```

Required secret:

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

Use:

```bash
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/sa-tot-osa.json
```

Production runtimes running in Vertex Agent Engine must use the runtime service account and must not rely on local JSON credentials.

---

# Required Dependencies

Core dependencies:

```toml
dependencies = [
    "google-adk>=2.6.3",
    "google-cloud-bigquery>=3.43.0",
    "google-cloud-secret-manager>=2.24.0",
    "google-genai",
    "python-dotenv"
]
```

---

# Design Principles

- Business-first AI
- Reusable business services
- Clean separation between AI and business logic
- No SQL inside agents
- Business terminology over technical metrics
- Multi-agent architecture
- Agent orchestration through Coordinator
- Shared services and gateways

---

# Roadmap

## Phase 1 ✅

- Country KPIs
- Store KPIs
- Store Resolution

## Phase 2

- Historical trends
- Daily comparisons
- Weekly comparisons
- Monthly comparisons
- Rankings

## Phase 3

- Root Cause Analysis Agent

## Phase 4

- Executive Agent

## Phase 5

- Store Coach Expansion

## Phase 6

- Recommendation Engine

## Phase 7

- Teams Integration
- Enterprise APIs
- Agent Evaluations
- Observability & Telemetry

---

# Long-Term Vision

The goal is to evolve Intelligent Shelf into an enterprise AI platform capable of supporting operations, category management, supply chain and executive decision-making through specialized AI agents sharing a common business foundation.

The platform should allow business users to interact with operational data through natural language while preserving a clean separation between AI orchestration, business rules, analytics services and data access layers.