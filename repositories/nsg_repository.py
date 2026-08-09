from google.cloud import bigquery

from common.bigquery_client import execute_query
from common.config import NSG_REPORT_TABLE


def get_latest_daily_summary(
    country: str,
) -> dict | None:

    sql = f"""
    WITH latest_date AS (
        SELECT
            MAX(alert_date) AS alert_date
        FROM `{NSG_REPORT_TABLE}`
        WHERE country = @country
          AND time_frame = 'DAILY'
    )

    SELECT
        r.alert_date,

        SUM(
            IF(
                r.metric = 'N_ON_SHELF',
                r.value,
                0
            )
        ) AS n_on_shelf,

        SUM(
            IF(
                r.metric = 'N_OOS_SHELF',
                r.value,
                0
            )
        ) AS n_oos_shelf,

        SUM(
            IF(
                r.metric = 'N_OOS_STORE',
                r.value,
                0
            )
        ) AS n_oos_store

    FROM `{NSG_REPORT_TABLE}` AS r
    CROSS JOIN latest_date AS d

    WHERE r.country = @country
      AND r.time_frame = 'DAILY'
      AND r.alert_date = d.alert_date

    GROUP BY r.alert_date
    """

    params = [
        bigquery.ScalarQueryParameter(
            "country",
            "STRING",
            country.upper(),
        )
    ]

    rows = execute_query(
        sql,
        params,
    )

    return rows[0] if rows else None