#!/usr/bin/env python3
"""
Deploy to Cloud Run using subprocess to bypass PowerShell wrapper issues.
"""
import subprocess
import sys
import os

def deploy_to_cloud_run():
    """Deploy ispilot-api to Cloud Run."""
    
    # Get the path to gcloud executable
    # On Windows, we'll use gcloud.cmd
    gcloud_cmd = "gcloud.cmd" if sys.platform == "win32" else "gcloud"
    
    # Build the deployment command
    deploy_args = [
        gcloud_cmd,
        "run", "deploy",
        "ispilot-api",
        "--image=us-central1-docker.pkg.dev/corp-stro-salesinventory-prod/ispilot-api/ispilot-api:latest",
        "--region=us-central1",
        "--platform=managed",
        "--allow-unauthenticated",
        "--set-env-vars=GOOGLE_CLOUD_PROJECT=corp-stro-salesinventory-prod,VERTEX_PROJECT_ID=corp-stro-salesinventory-prod,VERTEX_LOCATION=us-central1,VERTEX_ENGINE_ID=5375474415045705728",
        "--update-secrets=ISPILOT_API_KEY=ispilot-api-key:latest",
        "--project=corp-stro-salesinventory-prod",
    ]
    
    print(f"Executing: {' '.join(deploy_args)}")
    print("=" * 80)
    
    try:
        # Run the command directly
        result = subprocess.run(
            deploy_args,
            check=False,
            capture_output=False,
            text=True
        )
        
        if result.returncode == 0:
            print("=" * 80)
            print("✅ Deployment completed successfully!")
            return 0
        else:
            print("=" * 80)
            print(f"❌ Deployment failed with exit code {result.returncode}")
            return result.returncode
            
    except FileNotFoundError:
        print(f"❌ Error: Could not find '{gcloud_cmd}' command")
        print("Please ensure Google Cloud SDK is installed and in PATH")
        return 1
    except Exception as e:
        print(f"❌ Error during deployment: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(deploy_to_cloud_run())
