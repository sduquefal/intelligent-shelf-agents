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

def resolve_store(
    query: str,
    country: str = "CL",
):
    """
    Resolve a store from its code or name.

    Examples:
        101
        San Bernardo
        Plaza Egaña
        Alameda

    Returns:
        resolved
        ambiguous
        not_found
    """

    from services.store_service import StoreService

    return StoreService().resolve_store(
        query=query,
        country=country,
    )
    
def get_store_summary(
    country: str,
    loc_cod: int,
):
    """
    Returns the latest Intelligent Shelf KPIs for a specific store.

    Args:
        country:
            CL or PE

        loc_cod:
            Store code.

    Returns:
        SNSG, Bodega and Quiebre KPIs.
    """

    return analytics_service.get_store_summary(
        country=country,
        loc_cod=loc_cod,
    )