export const platformConfig = {
  name: "Intelligent Shelf AI",

  agent: {
    id: "shelf-analyst",
    name: "Shelf Analyst",
    subtitle: "Business Intelligence Coordinator",
    status: "active",
  },

  services: [
    {
      id: "store-service",
      name: "Store Service",
      description: "Store identity and hierarchy",
      type: "store",
    },
    {
      id: "analytics-service",
      name: "Analytics Service",
      description: "KPIs, metrics and trends",
      type: "analytics",
    },
    {
      id: "alert-service",
      name: "Alert Service",
      description: "Operational signals",
      type: "alerts",
    },
  ],

  intelligence: {
    name: "Shared Retail Intelligence",
    items: [
      "Business semantics",
      "Context",
      "Rules",
      "Shared services",
    ],
  },

  foundation: {
    name: "Data & AI Foundation",
    items: [
      "BigQuery",
      "Vertex AI",
      "Operational Data",
      "Future APIs",
    ],
  },
};