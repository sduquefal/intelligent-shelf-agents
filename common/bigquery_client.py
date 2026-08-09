from typing import Any

from google.cloud import bigquery

from common.config import GCP_PROJECT


_client: bigquery.Client | None = None


def get_client() -> bigquery.Client:
    global _client

    if _client is None:
        _client = bigquery.Client(
            project=GCP_PROJECT
        )

    return _client


def execute_query(
    sql: str,
    params: list[Any] | None = None,
) -> list[dict]:

    job_config = bigquery.QueryJobConfig(
        query_parameters=params or [],
        use_query_cache=True,
        maximum_bytes_billed=1_000_000_000,
    )

    query_job = get_client().query(
        sql,
        job_config=job_config,
    )

    return [
        dict(row)
        for row in query_job.result()
    ]