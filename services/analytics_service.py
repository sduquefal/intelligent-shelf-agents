from domain.summary import DailySummary, MetricSummary
from repositories.nsg_repository import get_latest_daily_summary


SUPPORTED_COUNTRIES = {"CL", "PE"}


def _percentage(value: int, total: int) -> float:
    if total == 0:
        return 0.0

    return round((value / total) * 100, 2)


def latest_daily_summary(country: str) -> dict:
    country = country.upper().strip()

    if country not in SUPPORTED_COUNTRIES:
        return {
            "status": "error",
            "message": "Supported countries are CL and PE.",
        }

    row = get_latest_daily_summary(country)

    if row is None:
        return {
            "status": "not_found",
            "country": country,
            "message": "No daily Intelligent Shelf data was found.",
        }

    on_shelf = int(row["n_on_shelf"] or 0)
    oos_shelf = int(row["n_oos_shelf"] or 0)
    oos_store = int(row["n_oos_store"] or 0)

    # Current business universe.
    # Keep this calculation centralized so it can be changed
    # if the official Intelligent Shelf denominator differs.
    total = on_shelf + oos_shelf + oos_store

    summary = DailySummary(
        country=country,
        date=row["alert_date"],
        total=total,
        en_gondola=MetricSummary(
            count=on_shelf,
            percentage=_percentage(on_shelf, total),
        ),
        bodega=MetricSummary(
            count=oos_shelf,
            percentage=_percentage(oos_shelf, total),
        ),
        quiebre=MetricSummary(
            count=oos_store,
            percentage=_percentage(oos_store, total),
        ),
    )

    return {
        "status": "success",
        "summary": summary.to_dict(),
    }