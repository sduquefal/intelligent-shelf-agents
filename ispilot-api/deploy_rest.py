#!/usr/bin/env python3
"""
Deploy ispilot-api to Google Cloud Run using REST API.
This bypasses gcloud CLI and handles SSL certificate issues better.
"""

import os
import sys
import json
import time
import requests
from datetime import datetime
from google.oauth2 import service_account

# Suppress SSL warnings
requests.packages.urllib3.disable_warnings()

def get_access_token():
    """Get Google Cloud access token from service account."""
    try:
        # Try to get from environment first
        creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        if not creds_path:
            # Fall back to shared key location
            creds_path = "../../../sa/key.json"
            creds_path = os.path.abspath(creds_path)
        
        print(f"📋 Using service account: {creds_path}")
        
        credentials = service_account.Credentials.from_service_account_file(
            creds_path,
            scopes=['https://www.googleapis.com/auth/cloud-platform']
        )
        
        credentials.refresh(requests.Request(verify=False))
        return credentials.token
        
    except Exception as e:
        print(f"❌ Failed to get access token: {e}")
        return None

def deploy_to_cloud_run():
    """Deploy the service to Cloud Run using REST API."""
    try:
        # Get access token
        access_token = get_access_token()
        if not access_token:
            return None
            
        print(f"✓ Got access token")
        
        # Configuration
        project_id = "corp-stro-salesinventory-prod"
        region = "us-central1"
        service_name = "ispilot-api"
        image_uri = "us-central1-docker.pkg.dev/corp-stro-salesinventory-prod/ispilot-api/ispilot-api:latest"
        
        # API endpoint
        api_url = f"https://{region}-run.googleapis.com/apis/serving.knative.dev/v1/namespaces/{project_id}/services/{service_name}"
        
        # Service definition
        service_spec = {
            "apiVersion": "serving.knative.dev/v1",
            "kind": "Service",
            "metadata": {
                "name": service_name,
                "namespace": project_id,
                "labels": {
                    "cloud.googleapis.com/location": region
                }
            },
            "spec": {
                "template": {
                    "spec": {
                        "containers": [
                            {
                                "image": image_uri,
                                "env": [
                                    {"name": "GOOGLE_CLOUD_PROJECT", "value": "corp-stro-salesinventory-prod"},
                                    {"name": "VERTEX_PROJECT_ID", "value": "corp-stro-salesinventory-prod"},
                                    {"name": "VERTEX_LOCATION", "value": "us-central1"},
                                    {"name": "VERTEX_ENGINE_ID", "value": "5375474415045705728"},
                                ],
                                "resources": {
                                    "limits": {
                                        "cpu": "2",
                                        "memory": "1Gi"
                                    },
                                    "requests": {
                                        "cpu": "1",
                                        "memory": "512Mi"
                                    }
                                }
                            }
                        ],
                        "timeoutSeconds": 300,
                        "serviceAccountName": "sa-ispilot-api"
                    }
                },
                "traffic": [
                    {
                        "percent": 100,
                        "latestRevision": True
                    }
                ]
            }
        }
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        print(f"📦 Deploying {service_name} to {region}...")
        print(f"Image: {image_uri}")
        
        # Try to create service (will update if exists)
        response = requests.post(
            f"https://{region}-run.googleapis.com/apis/serving.knative.dev/v1/namespaces/{project_id}/services",
            json=service_spec,
            headers=headers,
            verify=False,
            timeout=30
        )
        
        if response.status_code == 409:
            # Service already exists, update it
            print("⏳ Service exists, updating...")
            response = requests.put(
                api_url,
                json=service_spec,
                headers=headers,
                verify=False,
                timeout=30
            )
        
        if response.status_code in [200, 201, 202]:
            print(f"✅ Deployment request accepted (HTTP {response.status_code})")
            
            # Extract service URL from response
            try:
                result = response.json()
                if "status" in result and "url" in result["status"]:
                    service_url = result["status"]["url"]
                    print(f"\n🎉 Service URL: {service_url}")
                    return service_url
                else:
                    print(f"📄 Response: {json.dumps(result, indent=2)}")
                    return "pending"
            except:
                print(f"Response text: {response.text}")
                return "pending"
        else:
            print(f"❌ Deployment failed (HTTP {response.status_code})")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Deployment error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    url = deploy_to_cloud_run()
    sys.exit(0 if url else 1)
