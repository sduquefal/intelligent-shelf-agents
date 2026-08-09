from domain.summary import DailySummary, MetricSummary
from gateways.nsg_gateway import NSGGateway


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

        return {
            "status": "success",
            "summary": summary.to_dict(),
        }
    
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