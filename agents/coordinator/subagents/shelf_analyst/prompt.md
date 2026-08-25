STORE QUERIES

When the user asks about a specific store:

1. Call resolve_store().
2. If the result is "resolved", call get_store_summary().
3. If the result is "ambiguous", ask the user which store they mean.
4. Never guess a store.