from services.analytics_service import AnalyticsService

from ..shelf_analyst.tools import (
    resolve_store,
    get_store_summary,
    compare_store_daily,
    get_store_trend,
    get_store_ranking,
)

def diagnose_store(
    store_name: str,
    country: str = "CL",
):
    store_result = resolve_store(
        query=store_name,
        country=country,
    )

    if store_result["status"] != "resolved":
        return store_result

    store = store_result["store"]

    return {
        "store": store,
        "summary": get_store_summary(
            country=country,
            loc_cod=store["loc_cod"],
        ),
        "comparison": compare_store_daily(
            country=country,
            loc_cod=store["loc_cod"],
        ),
        "trend": get_store_trend(
            country=country,
            loc_cod=store["loc_cod"],
        ),
    }

def identify_priority_stores(
    country: str = "CL",
):
    return get_store_ranking(
        country=country,
        limit=10,
    )
def generate_action_plan(
    store_name: str,
    country: str = "CL",
):
    diagnosis = diagnose_store(
        store_name=store_name,
        country=country,
    )

    summary_result = diagnosis["summary"]

    if summary_result.get("status") != "success":
        return {
            "status": "summary_not_available",
            "diagnosis": diagnosis,
        }

    summary = summary_result["summary"]

    snsg = summary["snsg"]["percentage"]

    actions = []

    if snsg < 90:
        actions.append(
            "Priorizar revisión inmediata de disponibilidad."
        )

    if snsg < 95:
        actions.append(
            "Revisar ejecución de reposición en sala."
        )

    actions.append(
        "Monitorear SNSG diariamente."
    )

    actions.append(
        "Validar cumplimiento operacional de la tienda."
    )

    return {
        "store": store_name,
        "snsg": snsg,
        "recommended_actions": actions,
    }