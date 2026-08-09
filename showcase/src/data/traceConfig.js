export const traceConfig = [
  {
    id: 1,
    actor: "Shelf Analyst",
    direction: "out",
    target: "Store Service",
    message: 'resolve_store("San Bernardo Plaza")',
  },
  {
    id: 2,
    actor: "Store Service",
    direction: "in",
    target: "Shelf Analyst",
    message: "Store resolved → 101",
  },
  {
    id: 3,
    actor: "Analytics Service",
    direction: "out",
    target: "Analytics Engine",
    message: "get_latest_daily_summary(101)",
  },
  {
    id: 4,
    actor: "Analytics Service",
    direction: "in",
    target: "Shelf Analyst",
    message: "SNSG = 95.8%",
  },
  {
    id: 5,
    actor: "Retail Intelligence",
    direction: "out",
    target: "Shelf Analyst",
    message: "Generate business insight",
  },
];