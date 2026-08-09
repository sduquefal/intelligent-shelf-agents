from services.analytics_service import latest_daily_summary


def get_latest_daily_summary(country: str) -> dict:
    """
    Get the latest available daily Intelligent Shelf business KPIs.

    Args:
        country: Country code. Use CL for Chile or PE for Peru.

    Returns:
        A business-oriented daily summary including:
        - SNSG / En góndola
        - Bodega
        - Quiebre
        with percentage and count.
    """
    return latest_daily_summary(country)