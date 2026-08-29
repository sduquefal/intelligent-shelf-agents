import time
import logging

from domain.summary import DailySummary, MetricSummary
from gateways.nsg_gateway import NSGGateway

logger = logging.getLogger(__name__)

SUPPORTED_COUNTRIES = {"CL", "PE"}


class AnalyticsService:
    def __init__(
        self,
        nsg_gateway: NSGGateway | None = None,
    ):
        self._nsg_gateway = nsg_gateway or NSGGateway()

    @staticmethod
    def _percentage(
        value: int,
        total: int,
    ) -> float:
        if total == 0:
            return 0.0

        return round(
            (value / total) * 100,
            2,
        )

    def get_latest_daily_summary(
        self,
        country: str,
    ) -> dict:
        start_time = time.time()
        operation_name = f"get_latest_daily_summary({country})"
        
        try:
            country = country.upper().strip()

            if country not in SUPPORTED_COUNTRIES:
                return {
                    "status": "error",
                    "message": "Supported countries are CL and PE.",
                }

            row = self._nsg_gateway.get_latest_daily_summary(
                country
            )

            if row is None:
                return {
                    "status": "not_found",
                    "country": country,
                    "message": (
                        "No daily Intelligent Shelf data was found."
                    ),
                }

            on_shelf = int(row["n_on_shelf"] or 0)
            oos_shelf = int(row["n_oos_shelf"] or 0)
            oos_store = int(row["n_oos_store"] or 0)

            total = (
                on_shelf
                + oos_shelf
                + oos_store
            )

            summary = DailySummary(
                country=country,
                date=row["alert_date"],
                total=total,
                en_gondola=MetricSummary(
                    count=on_shelf,
                    percentage=self._percentage(
                        on_shelf,
                        total,
                    ),
                ),
                bodega=MetricSummary(
                    count=oos_shelf,
                    percentage=self._percentage(
                        oos_shelf,
                        total,
                    ),
                ),
                quiebre=MetricSummary(
                    count=oos_store,
                    percentage=self._percentage(
                        oos_store,
                        total,
                    ),
                ),
            )

            latency_ms = (time.time() - start_time) * 1000
            logger.info(
                f"[ANALYTICS_METRICS] {operation_name} completed successfully",
                extra={
                    "operation": operation_name,
                    "latency_ms": round(latency_ms, 2),
                    "country": country,
                    "status": "success",
                }
            )
            print(f"✓ [ANALYTICS] {operation_name} took {latency_ms:.2f}ms")

            return {
                "status": "success",
                "summary": summary.to_dict(),
            }
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            logger.error(
                f"[ANALYTICS_METRICS] {operation_name} failed",
                extra={
                    "operation": operation_name,
                    "latency_ms": round(latency_ms, 2),
                    "error": str(e),
                    "status": "error",
                }
            )
            print(f"✗ [ANALYTICS] {operation_name} failed after {latency_ms:.2f}ms: {e}")
            raise
    
    def get_store_summary(
        self,
        country: str,
        loc_cod: int,
    ):

        row = self._nsg_gateway.get_store_daily_summary(
            country,
            loc_cod,
        )

        if row is None:
            return {
                "status":"not_found"
            }

        on_shelf = int(row["n_on_shelf"] or 0)
        oos_shelf = int(row["n_oos_shelf"] or 0)
        oos_store = int(row["n_oos_store"] or 0)

        total = on_shelf + oos_shelf + oos_store

        return {
            "status":"success",
            "summary":{
                "country":country,
                "loc_cod":loc_cod,
                "date":str(row["alert_date"]),
                "total":total,
                "snsg":{
                    "count":on_shelf,
                    "percentage":self._percentage(on_shelf,total),
                },
                "bodega":{
                    "count":oos_shelf,
                    "percentage":self._percentage(oos_shelf,total),
                },
                "quiebre":{
                    "count":oos_store,
                    "percentage":self._percentage(oos_store,total),
                },
            },
        }
    def compare_store_daily(
        self,
        country: str,
        loc_cod: int,
    ) -> dict:

        rows = self._nsg_gateway.get_store_daily_comparison(
            country,
            loc_cod,
        )

        if len(rows) < 2:
            return {
                "status": "not_found",
                "message": "Not enough daily data to compare.",
            }

        def build_metrics(row):
            on_shelf = int(row["n_on_shelf"] or 0)
            oos_shelf = int(row["n_oos_shelf"] or 0)
            oos_store = int(row["n_oos_store"] or 0)

            total = on_shelf + oos_shelf + oos_store

            return {
                "date": str(row["alert_date"]),
                "snsg": self._percentage(on_shelf, total),
                "bodega": self._percentage(oos_shelf, total),
                "quiebre": self._percentage(oos_store, total),
            }

        current = build_metrics(rows[0])
        previous = build_metrics(rows[1])

        return {
            "status": "success",
            "country": country.upper(),
            "loc_cod": loc_cod,
            "current": current,
            "previous": previous,
            "change": {
                "snsg_pp": round(
                    current["snsg"] - previous["snsg"], 2
                ),
                "bodega_pp": round(
                    current["bodega"] - previous["bodega"], 2
                ),
                "quiebre_pp": round(
                    current["quiebre"] - previous["quiebre"], 2
                ),
            },
        }
    
    def get_store_trend(
        self,
        country: str,
        loc_cod: int,
        days: int = 7,
    ) -> dict:

        rows = self._nsg_gateway.get_store_daily_trend(
            country,
            loc_cod,
            days,
        )

        if not rows:
            return {
                "status": "not_found",
                "message": "No daily data found.",
            }

        trend = []

        for row in rows:
            on_shelf = int(row["n_on_shelf"] or 0)
            oos_shelf = int(row["n_oos_shelf"] or 0)
            oos_store = int(row["n_oos_store"] or 0)

            total = on_shelf + oos_shelf + oos_store

            trend.append({
                "date": str(row["alert_date"]),
                "snsg": self._percentage(on_shelf, total),
                "bodega": self._percentage(oos_shelf, total),
                "quiebre": self._percentage(oos_store, total),
            })

        first = trend[0]
        latest = trend[-1]

        return {
            "status": "success",
            "country": country.upper(),
            "loc_cod": loc_cod,
            "days": len(trend),
            "trend": trend,
            "change": {
                "snsg_pp": round(latest["snsg"] - first["snsg"], 2),
                "bodega_pp": round(latest["bodega"] - first["bodega"], 2),
                "quiebre_pp": round(latest["quiebre"] - first["quiebre"], 2),
            },
        }
    def get_store_ranking(
        self,
        country: str,
        limit: int = 5,
    ) -> dict:

        rows = self._nsg_gateway.get_store_ranking(
            country=country,
            limit=limit,
        )

        stores = []

        for row in rows:
            on_shelf = int(row["n_on_shelf"] or 0)
            oos_shelf = int(row["n_oos_shelf"] or 0)
            oos_store = int(row["n_oos_store"] or 0)

            total = on_shelf + oos_shelf + oos_store

            stores.append({
                "loc_cod": row["loc_cod"],
                "store_name": row["store_name"],
                "snsg": self._percentage(on_shelf, total),
                "bodega": self._percentage(oos_shelf, total),
                "quiebre": self._percentage(oos_store, total),
            })

        stores.sort(key=lambda x: x["snsg"])

        return {
            "status": "success",
            "country": country.upper(),
            "date": str(rows[0]["alert_date"]) if rows else None,
            "ranking": stores[:limit],
        }