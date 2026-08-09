from services.analytics_service import AnalyticsService


analytics_service = AnalyticsService()


def get_latest_daily_summary(
    country: str,
) -> dict:
    """
    Get the latest available daily Intelligent Shelf KPIs.

    Args:
        country:
            Country code.
            Use CL for Chile or PE for Peru.

    Returns:
        Business-oriented Intelligent Shelf summary
        with SNSG, Bodega and Quiebre,
        including percentages and counts.
    """

    return analytics_service.get_latest_daily_summary(
        country
    )