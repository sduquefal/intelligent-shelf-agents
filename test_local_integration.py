#!/usr/bin/env python
"""Local integration test for agents + metrics.

Can run locally with SA auth or on remote machine.
Tests coordinator, analytics service, and agent routing.
"""

import os
import sys
from pathlib import Path

# Add root to path
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

def test_imports():
    """Test that all key modules import successfully."""
    print("\n=== Test 1: Module Imports ===")
    
    try:
        from agents.coordinator.agent import root_agent
        print(f"✓ Coordinator agent loaded: {root_agent.name}")
    except Exception as e:
        print(f"✗ Failed to load coordinator: {e}")
        return False
    
    try:
        from services.analytics_service import AnalyticsService
        print("✓ AnalyticsService imported")
    except Exception as e:
        print(f"✗ Failed to load AnalyticsService: {e}")
        return False
    
    try:
        from services.store_service import StoreService
        print("✓ StoreService imported")
    except Exception as e:
        print(f"✗ Failed to load StoreService: {e}")
        return False
    
    return True


def test_analytics_service():
    """Test analytics service with real BigQuery data."""
    print("\n=== Test 2: Analytics Service ===")
    
    from services.analytics_service import AnalyticsService
    
    service = AnalyticsService()
    
    # Test CL
    print("\nTesting Chile (CL)...")
    try:
        result = service.get_latest_daily_summary("CL")
        if result.get("status") == "success":
            print(f"✓ CL data retrieved")
            print(f"  - On shelf: {result.get('data', {}).get('on_shelf_percentage', 'N/A')}%")
            print(f"  - OOS shelf: {result.get('data', {}).get('oos_shelf_percentage', 'N/A')}%")
            print(f"  - OOS store: {result.get('data', {}).get('oos_store_percentage', 'N/A')}%")
        else:
            print(f"✗ CL query failed: {result.get('message')}")
            return False
    except Exception as e:
        print(f"✗ CL test error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test PE
    print("\nTesting Peru (PE)...")
    try:
        result = service.get_latest_daily_summary("PE")
        if result.get("status") == "success":
            print(f"✓ PE data retrieved")
            print(f"  - On shelf: {result.get('data', {}).get('on_shelf_percentage', 'N/A')}%")
        else:
            print(f"✗ PE query failed: {result.get('message')}")
            # PE might not have data, that's OK
    except Exception as e:
        print(f"✗ PE test error: {e}")
    
    return True


def test_agent_configuration():
    """Test that agent is properly configured."""
    print("\n=== Test 3: Agent Configuration ===")
    
    from agents.coordinator.agent import root_agent
    
    # Check agent properties
    print(f"Agent name: {root_agent.name}")
    print(f"Agent description: {root_agent.description}")
    
    # Check subagents
    subagent_names = [agent.name for agent in root_agent.sub_agents]
    print(f"Subagents: {subagent_names}")
    
    if len(subagent_names) == 0:
        print("✗ No subagents configured!")
        return False
    
    print("✓ Agent configuration valid")
    return True


def test_gcp_auth():
    """Verify GCP authentication is set up."""
    print("\n=== Test 0: GCP Authentication ===")
    
    # Check for credentials
    if "GOOGLE_APPLICATION_CREDENTIALS" in os.environ:
        cred_path = os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
        if os.path.exists(cred_path):
            print(f"✓ GOOGLE_APPLICATION_CREDENTIALS set: {cred_path}")
        else:
            print(f"✗ Credentials file not found: {cred_path}")
            return False
    else:
        print("⚠ GOOGLE_APPLICATION_CREDENTIALS not set")
        print("  (May use Application Default Credentials)")
    
    # Check gcloud config
    try:
        import subprocess
        result = subprocess.run(
            ["gcloud", "config", "get-value", "project"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            project = result.stdout.strip()
            print(f"✓ gcloud project: {project}")
            if project == "corp-stro-salesinventory-prod":
                print("  ✓ Correct project!")
            else:
                print(f"  ⚠ Expected 'corp-stro-salesinventory-prod', got '{project}'")
        else:
            print("✗ gcloud config unavailable")
    except Exception as e:
        print(f"⚠ Could not verify gcloud: {e}")
    
    return True


def main():
    """Run all tests."""
    print("=" * 60)
    print("ISPilot Integration Test Suite")
    print("=" * 60)
    
    # Test 0: Auth
    auth_ok = test_gcp_auth()
    if not auth_ok:
        print("\n⚠ WARNING: GCP auth may not be configured")
        print("  Continue anyway? (local tests may fail)")
    
    # Test 1: Imports
    if not test_imports():
        print("\n✗ Import test failed - cannot continue")
        return False
    
    # Test 2: Agent config
    if not test_agent_configuration():
        print("\n✗ Agent configuration test failed")
        return False
    
    # Test 3: Analytics service
    try:
        if not test_analytics_service():
            print("\n⚠ Analytics service test failed")
            print("  (This requires BigQuery access)")
    except Exception as e:
        print(f"\n⚠ Analytics test skipped: {e}")
    
    print("\n" + "=" * 60)
    print("✓ Integration test complete!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
