# test_bq_identity.py

import google.auth
from google.cloud import bigquery


client = bigquery.Client(
    project="corp-stro-salesinventory-prod"
)

for ds in client.list_datasets():
    print(ds.dataset_id)
    break