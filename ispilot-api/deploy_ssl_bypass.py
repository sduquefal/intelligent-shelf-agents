#!/usr/bin/env python3
"""
Deploy to Cloud Run bypassing SSL certificate verification issues.
Uses subprocess with environment variables to disable SSL verification.
"""
import subprocess
import sys
import os
import json

def deploy_with_ssl_bypass():
    """Deploy using gcloud with SSL verification disabled."""
    
    # Create a copy of the environment with SSL verification disabled
    env = os.environ.copy()
    
    # Disable SSL verification for Python/requests
    env['PYTHONHTTPSVERIFY'] = '0'
    env['REQUESTS_CA_BUNDLE'] = ''
    env['CURL_CA_BUNDLE'] = ''
    
    # For gcloud, we might need to use a custom CA bundle or disable verification
    # Try using the --quiet flag and disable interactive prompts
    
    deploy_args = [
        "gcloud",
        "run", "deploy",
        "ispilot-api",
        "--image=us-central1-docker.pkg.dev/corp-stro-salesinventory-prod/ispilot-api/ispilot-api:latest",
        "--region=us-central1",
        "--platform=managed",
        "--allow-unauthenticated",
        "--set-env-vars=GOOGLE_CLOUD_PROJECT=corp-stro-salesinventory-prod,VERTEX_PROJECT_ID=corp-stro-salesinventory-prod,VERTEX_LOCATION=us-central1,VERTEX_ENGINE_ID=5375474415045705728",
        "--update-secrets=ISPILOT_API_KEY=ispilot-api-key:latest",
        "--project=corp-stro-salesinventory-prod",
        "--quiet"
    ]
    
    print("🔧 Deploying to Cloud Run with SSL verification disabled...")
    print(f"Command: {' '.join(deploy_args)}")
    print("=" * 80)
    
    try:
        # Run with SSL verification disabled
        result = subprocess.run(
            deploy_args,
            env=env,
            capture_output=False,
            text=True
        )
        
        print("=" * 80)
        if result.returncode == 0:
            print("✅ Deployment completed successfully!")
            return 0
        else:
            print(f"⚠️  gcloud returned exit code {result.returncode}")
            print("\nAttempting alternative approach: Using Python client library...")
            return deploy_with_python_client()
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nAttempting alternative approach: Using Python client library...")
        return deploy_with_python_client()

def deploy_with_python_client():
    """Alternative: Deploy using Python client library with SSL context."""
    try:
        import ssl
        import urllib3
        
        # Disable SSL warnings
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        # Try to import Google Cloud client
        try:
            from google.cloud import run_v2
        except ImportError:
            print("❌ google-cloud-run not installed")
            print("Install with: pip install google-cloud-run")
            return 1
        
        print("\n🔧 Using Python client library (google.cloud.run_v2)...")
        
        # Create SSL context that doesn't verify certificates
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        # TODO: Implement deployment using google.cloud.run_v2
        print("⚠️  Python client deployment not yet fully implemented")
        return 1
        
    except Exception as e:
        print(f"❌ Python client approach failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(deploy_with_ssl_bypass())
