#!/usr/bin/env python3
"""
Script para fazer upload automático de dashboards para Grafana Cloud.

Autor: Anderson Henrique da Silva
Localização: Minas Gerais, Brasil
Data: 2025-10-30

Uso:
    python scripts/upload_dashboards_to_grafana_cloud.py

Requer:
    - GRAFANA_CLOUD_API_KEY: API key do Grafana Cloud (Service Account Token)
    - GRAFANA_CLOUD_STACK_ID: ID da sua stack (ex: cidadaoai)
"""

import glob
import json
import os
import sys

import requests


def upload_dashboard(
    stack_id: str, api_key: str, dashboard_path: str
) -> tuple[bool, str]:
    """
    Upload dashboard JSON to Grafana Cloud.

    Args:
        stack_id: Grafana Cloud stack ID
        api_key: Grafana Cloud API key (Service Account Token)
        dashboard_path: Path to dashboard JSON file

    Returns:
        Tuple of (success, message)
    """
    # Read dashboard JSON
    try:
        with open(dashboard_path) as f:
            dashboard_json = json.load(f)
    except Exception as e:
        return False, f"Failed to read {dashboard_path}: {e}"

    # Prepare payload for Grafana API
    payload = {
        "dashboard": dashboard_json,
        "overwrite": True,
        "message": "Uploaded via script",
    }

    # Grafana Cloud API endpoint
    url = f"https://{stack_id}.grafana.net/api/dashboards/db"

    # Headers
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    # Make request
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()

        result = response.json()
        dashboard_url = result.get("url", "")
        return (
            True,
            f"✅ Uploaded successfully! URL: https://{stack_id}.grafana.net{dashboard_url}",
        )

    except requests.exceptions.RequestException as e:
        return False, f"❌ Upload failed: {e}"


def main():
    """Main function."""
    # Get credentials from environment
    stack_id = os.getenv("GRAFANA_CLOUD_STACK_ID", "")
    api_key = os.getenv("GRAFANA_CLOUD_API_KEY", "")

    if not stack_id or not api_key:
        print("❌ Missing required environment variables:")
        print("")
        print("  GRAFANA_CLOUD_STACK_ID: Your Grafana Cloud stack ID")
        print("  GRAFANA_CLOUD_API_KEY: Service Account Token from Grafana Cloud")
        print("")
        print("How to get these:")
        print("  1. Stack ID: Found in your Grafana Cloud URL")
        print("     Example: https://cidadaoai.grafana.net → stack_id = 'cidadaoai'")
        print("")
        print("  2. API Key:")
        print("     - Grafana Cloud → Administration → Service Accounts")
        print("     - Create Service Account")
        print("     - Add Token with 'Editor' role")
        print("     - Copy the token")
        print("")
        sys.exit(1)

    # Find all dashboard JSON files
    dashboard_dir = "monitoring/grafana/dashboards"
    dashboard_files = sorted(glob.glob(f"{dashboard_dir}/*.json"))

    if not dashboard_files:
        print(f"❌ No dashboard files found in {dashboard_dir}/")
        sys.exit(1)

    print(f"🔍 Found {len(dashboard_files)} dashboards to upload")
    print("")

    # Upload each dashboard
    success_count = 0
    failed_count = 0

    for dashboard_path in dashboard_files:
        dashboard_name = os.path.basename(dashboard_path)
        print(f"📊 Uploading {dashboard_name}...")

        success, message = upload_dashboard(stack_id, api_key, dashboard_path)

        if success:
            print(f"   {message}")
            success_count += 1
        else:
            print(f"   {message}")
            failed_count += 1

        print("")

    # Summary
    print("=" * 60)
    print(f"✅ Successfully uploaded: {success_count}")
    print(f"❌ Failed: {failed_count}")
    print("=" * 60)

    if failed_count > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
