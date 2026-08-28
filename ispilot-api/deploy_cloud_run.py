#!/usr/bin/env python3
"""
Deploy ispilot-api to Google Cloud Run using Python client libraries.
This bypasses gcloud CLI and handles SSL certificate issues better.
"""

import os
import sys
import json
from google.cloud import run_v2
from google.auth import default
import urllib3

# Disable SSL warnings if using unverified connections
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def deploy_to_cloud_run():
    """Deploy the service to Cloud Run."""
    try:
        # Get credentials
        credentials, project_id = default()
        print(f"✓ Authenticated with project: {project_id}")
        
        # Initialize Cloud Run client
        client = run_v2.ServicesClient()
        
        # Service configuration
        service_name = "ispilot-api"
        region = "us-central1"
        image_uri = "us-central1-docker.pkg.dev/corp-stro-salesinventory-prod/ispilot-api/ispilot-api:latest"
        
        parent = f"projects/{project_id}/locations/{region}"
        
        # Create service configuration
        service = run_v2.Service(
            template=run_v2.RevisionTemplate(
                containers=[
                    run_v2.Container(
                        image=image_uri,
                        env=[
                            run_v2.EnvVar(
                                name="GOOGLE_CLOUD_PROJECT",
                                value="corp-stro-salesinventory-prod"
                            ),
                            run_v2.EnvVar(
                                name="VERTEX_PROJECT_ID",
                                value="corp-stro-salesinventory-prod"
                            ),
                            run_v2.EnvVar(
                                name="VERTEX_LOCATION",
                                value="us-central1"
                            ),
                            run_v2.EnvVar(
                                name="VERTEX_ENGINE_ID",
                                value="5375474415045705728"
                            ),
                        ],
                    )
                ],
                service_account="sa-ispilot-api@corp-stro-salesinventory-prod.iam.gserviceaccount.com",
            ),
            ingress=run_v2.Service.Ingress.INGRESS_ALL,
        )
        
        # Create or update the service
        request = run_v2.CreateServiceRequest(
            parent=parent,
            service=service,
            service_id=service_name,
        )
        
        print(f"📦 Deploying {service_name} to {region}...")
        operation = client.create_service(request=request)
        
        print(f"⏳ Waiting for deployment to complete...")
        response = operation.result()
        
        service_url = response.uri
        print(f"\n✅ Deployment successful!")
        print(f"Service URL: {service_url}")
        print(f"Service name: {response.name}")
        
        return service_url
        
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    url = deploy_to_cloud_run()
    sys.exit(0 if url else 1)
