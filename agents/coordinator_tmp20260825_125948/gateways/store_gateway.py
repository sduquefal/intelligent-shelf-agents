from google.cloud import bigquery

from common.bigquery_client import BigQueryClient
from common.config import NSG_REPORT_TABLE


class StoreGateway:
    def __init__(
        self,
        client: BigQueryClient | None = None,
    ):
        self._client = client or BigQueryClient()

    def find_by_loc_cod(
        self,
        loc_cod: int,
        country: str | None = None,
    ) -> list[dict]:

        sql = f"""
        SELECT DISTINCT
            country,
            loc_cod,
            store_name,
            store_zone
        FROM `{NSG_REPORT_TABLE}`
        WHERE loc_cod = @loc_cod
          AND (
              @country IS NULL
              OR country = @country
          )
        ORDER BY country, loc_cod
        """

        params = [
            bigquery.ScalarQueryParameter(
                "loc_cod",
                "INT64",
                loc_cod,
            ),
            bigquery.ScalarQueryParameter(
                "country",
                "STRING",
                country.upper() if country else None,
            ),
        ]

        return self._client.execute_query(
            sql=sql,
            params=params,
        )

    def find_by_name(
        self,
        store_name: str,
        country: str | None = None,
    ) -> list[dict]:

        sql = f"""
        SELECT DISTINCT
            country,
            loc_cod,
            store_name,
            store_zone
        FROM `{NSG_REPORT_TABLE}`
        WHERE LOWER(store_name)
              LIKE CONCAT(
                  '%',
                  LOWER(@store_name),
                  '%'
              )
          AND (
              @country IS NULL
              OR country = @country
          )
        ORDER BY store_name
        LIMIT 20
        """

        params = [
            bigquery.ScalarQueryParameter(
                "store_name",
                "STRING",
                store_name.strip(),
            ),
            bigquery.ScalarQueryParameter(
                "country",
                "STRING",
                country.upper() if country else None,
            ),
        ]

        return self._client.execute_query(
            sql=sql,
            params=params,
        )