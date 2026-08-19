from google.cloud import bigquery

from common.bigquery_client import BigQueryClient
from common.config import CLASSIFICATION_TABLE


class ClassificationGateway:
    def __init__(
        self,
        client: BigQueryClient | None = None,
    ):
        self._client = client or BigQueryClient()

    def get_store_critical_skus(
        self,
        country: str,
        loc_cod: int,
        limit: int = 10,
    ) -> list:
        sql = f"""
        WITH latest_date AS (
            SELECT MAX(alert_date) AS alert_date
            FROM `{CLASSIFICATION_TABLE}`
            WHERE country = @country
        )

        SELECT
            sku_cod,
            name,
            department_desc,
            shelf_status,
            proba_predicted
        FROM `{CLASSIFICATION_TABLE}`
        CROSS JOIN latest_date d
        WHERE country = @country
          AND loc_cod = @loc_cod
          AND alert_date = d.alert_date
          AND shelf_status = 'OOS_SHELF'
        ORDER BY proba_predicted DESC
        LIMIT @limit
        """

        params = [
            bigquery.ScalarQueryParameter(
                "country",
                "STRING",
                country.upper(),
            ),
            bigquery.ScalarQueryParameter(
                "loc_cod",
                "INT64",
                loc_cod,
            ),
            bigquery.ScalarQueryParameter(
                "limit",
                "INT64",
                limit,
            ),
        ]

        return self._client.execute_query(
            sql=sql,
            params=params,
        )

    def get_store_oos_categories(
        self,
        country: str,
        loc_cod: int,
        limit: int = 10,
    ) -> list:
        sql = f"""
        WITH latest_date AS (
            SELECT MAX(alert_date) AS alert_date
            FROM `{CLASSIFICATION_TABLE}`
            WHERE country = @country
        )

        SELECT
            department_desc,
            COUNT(*) AS oos_skus
        FROM `{CLASSIFICATION_TABLE}`
        CROSS JOIN latest_date d
        WHERE country = @country
          AND loc_cod = @loc_cod
          AND alert_date = d.alert_date
          AND shelf_status = 'OOS_SHELF'
        GROUP BY department_desc
        ORDER BY oos_skus DESC
        LIMIT @limit
        """

        params = [
            bigquery.ScalarQueryParameter(
                "country",
                "STRING",
                country.upper(),
            ),
            bigquery.ScalarQueryParameter(
                "loc_cod",
                "INT64",
                loc_cod,
            ),
            bigquery.ScalarQueryParameter(
                "limit",
                "INT64",
                limit,
            ),
        ]

        return self._client.execute_query(
            sql=sql,
            params=params,
        )