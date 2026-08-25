> 🚧 **Project Status:** Active Development (MVP)

# Intelligent Shelf AI Platform

An enterprise-grade AI platform for retail operations, built on Google ADK, Vertex AI and BigQuery.

The platform enables business users to interact with Intelligent Shelf data using natural language, transforming operational metrics into business insights.

---

## Vision

Intelligent Shelf AI Platform is designed as a multi-agent system where each AI agent specializes in a different business capability while sharing the same business services and data layer.

Instead of building isolated chatbots, the objective is to build reusable business services that can be consumed by multiple AI agents, dashboards and APIs.

---

## Current Architecture

```
                    Intelligent Shelf AI Platform

                    User Interfaces
      Teams │ Web │ Looker │ API │ Future Apps
                        │
                Google ADK Agents
                        │
    ┌────────────┬──────────────┬──────────────┐
    │            │              │
Shelf Analyst Store Coach Executive Agent
    │
    └──────────────┬──────────────────────────┐
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

## Project Structure

```
intelligent-shelf-agents/

├── agents/
│   ├── shelf_analyst/
│   ├── executive/
│   ├── root_cause/
│   └── store_coach/
│
├── common/
│   ├── config.py
│   └── bigquery_client.py
│
├── gateways/
│   ├── nsg_gateway.py
│   └── store_gateway.py
│
├── services/
│   ├── analytics_service.py
│   └── store_service.py
│
├── domain/
│
├── repositories/
│
└── tests/
```

---

## Business Terminology

| Business Term | Technical Metric |
|--------------|------------------|
| SNSG | N_ON_SHELF |
| En góndola | ON_SHELF |
| Bodega | OOS_SHELF |
| Quiebre | OOS_STORE |

Business users should interact using business terminology rather than technical metric names.

---

## Current Features

### Shelf Analyst

- Country summary
- Store summary
- Store name resolution
- Store code resolution
- Ambiguous store detection
- Natural language analytics

Example:

> How is Chile today?

> How is store 101?

> How is San Bernardo Plaza?

> How is San Bernardo?

---

## Technology Stack

- Google ADK
- Gemini 2.5 Flash
- Vertex AI
- BigQuery
- Python 3.12

Architecture:

- Clean Architecture
- Gateway Pattern
- Service Layer
- Domain Objects

---

## Roadmap

### Phase 1 ✅

- Country KPIs
- Store KPIs
- Store Resolution

### Phase 2

- Historical trends
- Daily / Weekly / Monthly comparisons
- Rankings

### Phase 3

- Root Cause Analysis

### Phase 4

- Executive Agent

### Phase 5

- Store Coach

### Phase 6

- Recommendation Engine

---

## Design Principles

- Business-first AI
- Reusable business services
- Clean separation between AI and business logic
- No SQL inside agents
- Business terminology over technical metrics
- Multi-agent architecture

---

## Long-Term Vision

The goal is to evolve Intelligent Shelf into an enterprise AI platform capable of supporting operations, category management, supply chain and executive decision-making through specialized AI agents sharing a common business foundation.

## Authentication

### Runtime Service Account

Production deployments use:

sa-tot-osa@corp-stro-salesinventory-prod.iam.gserviceaccount.com

### Required permissions

Secret Manager:

- roles/secretmanager.secretAccessor
  - secret: genai-gateway-jwt-prod

Service Usage:

- roles/serviceusage.serviceUsageConsumer

BigQuery:

- roles/bigquery.jobUser
- roles/bigquery.dataViewer

### Local development

For local development, use:

export GOOGLE_APPLICATION_CREDENTIALS=/path/to/sa-tot-osa.json

Production runtimes (Vertex Agent Engine) must use the runtime service account and must not rely on local JSON credentials.