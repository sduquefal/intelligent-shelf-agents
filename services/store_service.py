import time
import logging

from domain.store import Store
from gateways.store_gateway import StoreGateway

logger = logging.getLogger(__name__)


class StoreService:
    def __init__(
        self,
        store_gateway: StoreGateway | None = None,
    ):
        self._store_gateway = store_gateway or StoreGateway()

    @staticmethod
    def _to_store(row: dict) -> Store:
        return Store(
            country=row["country"],
            loc_cod=int(row["loc_cod"]),
            store_name=row["store_name"],
            store_zone=row.get("store_zone"),
        )

    def resolve_store(
        self,
        query: str,
        country: str | None = None,
    ) -> dict:
        start_time = time.time()
        operation_name = f"resolve_store(query='{query}', country={country})"
        
        try:
            query = query.strip()

            if not query:
                return {
                    "status": "error",
                    "message": "Store query cannot be empty.",
                }

            if country:
                country = country.upper().strip()

            # If query is purely numeric, treat it as loc_cod.
            if query.isdigit():
                rows = self._store_gateway.find_by_loc_cod(
                    loc_cod=int(query),
                    country=country,
                )
            else:
                rows = self._store_gateway.find_by_name(
                    store_name=query,
                    country=country,
                )

            stores = [
                self._to_store(row)
                for row in rows
            ]

            if not stores:
                latency_ms = (time.time() - start_time) * 1000
                logger.info(
                    f"[STORE_METRICS] {operation_name} - not found",
                    extra={
                        "operation": operation_name,
                        "latency_ms": round(latency_ms, 2),
                        "status": "not_found",
                    }
                )
                return {
                    "status": "not_found",
                    "query": query,
                    "country": country,
                    "message": "No matching store was found.",
                }

            if len(stores) == 1:
                latency_ms = (time.time() - start_time) * 1000
                logger.info(
                    f"[STORE_METRICS] {operation_name} - resolved",
                    extra={
                        "operation": operation_name,
                        "latency_ms": round(latency_ms, 2),
                        "status": "resolved",
                        "store_count": 1,
                    }
                )
                print(f"✓ [STORE] {operation_name} resolved in {latency_ms:.2f}ms")
                return {
                    "status": "resolved",
                    "store": stores[0].to_dict(),
                }

            latency_ms = (time.time() - start_time) * 1000
            logger.info(
                f"[STORE_METRICS] {operation_name} - ambiguous",
                extra={
                    "operation": operation_name,
                    "latency_ms": round(latency_ms, 2),
                    "status": "ambiguous",
                    "store_count": len(stores),
                }
            )
            print(f"⚠ [STORE] {operation_name} ambiguous ({len(stores)} matches) in {latency_ms:.2f}ms")
            
            return {
                "status": "ambiguous",
                "query": query,
                "country": country,
                "matches": [
                    store.to_dict()
                    for store in stores
                ],
                "message": (
                    "More than one store matches the query. "
                    "Ask the user to choose one."
                ),
            }
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            logger.error(
                f"[STORE_METRICS] {operation_name} failed",
                extra={
                    "operation": operation_name,
                    "latency_ms": round(latency_ms, 2),
                    "error": str(e),
                    "status": "error",
                }
            )
            print(f"✗ [STORE] {operation_name} failed after {latency_ms:.2f}ms: {e}")
            raise