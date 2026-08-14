export const executionScenarios = [
  {
    id: "store-status",
    question: "¿Cómo está San Bernardo Plaza?",

    steps: [
      {
        id: "understand",
        title: "Understanding request",
        detail: "Identifying business intent",
        target: "shelf-analyst",
      },
      {
        id: "resolve-store",
        title: "Resolving store",
        detail: "San Bernardo Plaza · Store 101",
        target: "store-service",
      },
      {
        id: "retrieve-kpis",
        title: "Retrieving KPIs",
        detail: "Latest Intelligent Shelf performance",
        target: "analytics-service",
      },
      {
        id: "business-reasoning",
        title: "Business reasoning",
        detail: "Interpreting SNSG, Bodega and Quiebre",
        target: "shared-intelligence",
      },
      {
        id: "generate-insight",
        title: "Generating insight",
        detail: "Preparing business response",
        target: "shelf-analyst",
      },
    ],

    resultType: "store",

    result: {
      store: "San Bernardo Plaza",
      storeCode: 101,
      date: "2026-08-12",
      snsg: 94.76,
      bodega: 2.35,
      quiebre: 2.89,
      total: 10524,

      change: {
        snsg: 0.39,
        bodega: -0.07,
        quiebre: -0.32,
      },

      insight:
        "SNSG improved versus the previous day. The main positive signal is the reduction in Quiebre.",

      action:
        "Review the SKUs that remain in Quiebre and prioritize the most recurrent cases.",
    },
  },

  {
    id: "store-trend",
    question: "¿Cómo evolucionó San Bernardo Plaza en los últimos 7 días?",

    steps: [
      {
        id: "understand",
        title: "Understanding request",
        detail: "Identifying trend analysis",
        target: "shelf-analyst",
      },
      {
        id: "resolve-store",
        title: "Resolving store",
        detail: "San Bernardo Plaza · Store 101",
        target: "store-service",
      },
      {
        id: "retrieve-trend",
        title: "Retrieving 7-day trend",
        detail: "Daily SNSG, Bodega and Quiebre",
        target: "analytics-service",
      },
      {
        id: "business-reasoning",
        title: "Analyzing evolution",
        detail: "Detecting deterioration and recovery signals",
        target: "shared-intelligence",
      },
      {
        id: "generate-insight",
        title: "Generating insight",
        detail: "Preparing trend interpretation",
        target: "shelf-analyst",
      },
    ],

    resultType: "trend",

    result: {
      store: "San Bernardo Plaza",
      storeCode: 101,
      days: 7,
      snsgChange: -0.62,
      bodegaChange: 0.6,
      quiebreChange: 0.01,

      insight:
        "SNSG deteriorated over the 7-day period, mainly driven by a higher share of products in Bodega.",

      action:
        "Review replenishment execution and recurrent Bodega cases before they become shelf availability issues.",
    },
  },

  {
    id: "store-ranking",
    question: "¿Cuáles son las 5 tiendas con peor SNSG en Chile?",

    steps: [
      {
        id: "understand",
        title: "Understanding request",
        detail: "Identifying store prioritization",
        target: "shelf-analyst",
      },
      {
        id: "retrieve-ranking",
        title: "Retrieving store performance",
        detail: "Latest Intelligent Shelf performance in Chile",
        target: "analytics-service",
      },
      {
        id: "rank-stores",
        title: "Ranking stores",
        detail: "Ordering stores by SNSG",
        target: "shared-intelligence",
      },
      {
        id: "identify-signals",
        title: "Identifying critical signals",
        detail: "Comparing Bodega and Quiebre",
        target: "shared-intelligence",
      },
      {
        id: "generate-priority",
        title: "Generating priorities",
        detail: "Preparing management focus",
        target: "shelf-analyst",
      },
    ],

    resultType: "ranking",

    result: {
      country: "Chile",
      date: "2026-08-12",

      ranking: [
        {
          storeCode: 223,
          store: "Tottus Francia",
          snsg: 88.82,
          bodega: 1.97,
          quiebre: 9.21,
        },
        {
          storeCode: 511,
          store: "Vallenar",
          snsg: 88.91,
          bodega: 2.52,
          quiebre: 8.57,
        },
        {
          storeCode: 513,
          store: "Antofagasta Norte",
          snsg: 89.0,
          bodega: 2.6,
          quiebre: 8.4,
        },
        {
          storeCode: 204,
          store: "Melipilla",
          snsg: 89.06,
          bodega: 3.15,
          quiebre: 7.8,
        },
        {
          storeCode: 120,
          store: "Vitacura",
          snsg: 89.19,
          bodega: 0.27,
          quiebre: 10.54,
        },
      ],

      insight:
        "Quiebre is the dominant availability issue across the lowest-SNSG stores.",

      action:
        "Prioritize investigation of stores with the highest Quiebre concentration.",
    },
  },
];