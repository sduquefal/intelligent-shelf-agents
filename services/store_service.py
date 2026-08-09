from domain.store import Store
from gateways.store_gateway import StoreGateway


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
            return {
                "status": "not_found",
                "query": query,
                "country": country,
                "message": "No matching store was found.",
            }

        if len(stores) == 1:
            return {
                "status": "resolved",
                "store": stores[0].to_dict(),
            }

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