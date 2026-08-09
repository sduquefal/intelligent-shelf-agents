export const executionConfig = {
  question: "¿Cómo está San Bernardo Plaza?",

  steps: [
    {
      id: "understand",
      title: "Understanding request",
      detail: "Identifying business intent",
      status: "complete",
      target: "shelf-analyst",
    },
    {
      id: "resolve-store",
      title: "Resolving store",
      detail: "San Bernardo Plaza · Store 101",
      status: "complete",
      target: "store-service",
    },
    {
      id: "retrieve-kpis",
      title: "Retrieving KPIs",
      detail: "Latest Intelligent Shelf performance",
      status: "complete",
      target: "analytics-service",
    },
    {
      id: "business-reasoning",
      title: "Business reasoning",
      detail: "Interpreting SNSG, Bodega and Quiebre",
      status: "active",
      target: "shared-intelligence",
    },
    {
      id: "generate-insight",
      title: "Generating insight",
      detail: "Preparing business response",
      status: "pending",
      target: "shelf-analyst",
    },
  ],

  result: {
    store: "San Bernardo Plaza",
    storeCode: 101,
    snsg: 95.8,
    bodega: 1.67,
    quiebre: 2.54,
    total: 10560,
  },
};