from typing import Any

from google.cloud import bigquery

from common.config import GCP_PROJECT


class BigQueryClient:
    def __init__(
        self,
        project: str = GCP_PROJECT,
        maximum_bytes_billed: int = 1_000_000_000,
    ):
        self._client = bigquery.Client(project=project)
        self._maximum_bytes_billed = maximum_bytes_billed

    def execute_query(
        self,
        sql: str,
        params: list[Any] | None = None,
    ) -> list[dict]:

        job_config = bigquery.QueryJobConfig(
            query_parameters=params or [],
            use_query_cache=True,
            maximum_bytes_billed=self._maximum_bytes_billed,
        )

        query_job = self._client.query(
            sql,
            job_config=job_config,
        )

        return [dict(row) for row in query_job.result()]