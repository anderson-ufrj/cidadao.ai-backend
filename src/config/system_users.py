"""
System Users Configuration
Author: Anderson Henrique da Silva
Date: 2025-10-09

Configuration for system-level users used by automated processes.
"""

import os

# System user for auto-investigations
# This should be a valid UUID from Supabase auth.users table
# User: system@cidadao.ai (created 2025-10-09)
# Default: Use from environment variable, fallback to system user UUID
SYSTEM_AUTO_MONITOR_USER_ID = os.getenv(
    "SYSTEM_AUTO_MONITOR_USER_ID",
    "58050609-2fe2-49a6-a342-7cf66d83d216"  # system@cidadao.ai
)

# System user for scheduled tasks
SYSTEM_SCHEDULER_USER_ID = os.getenv(
    "SYSTEM_SCHEDULER_USER_ID",
    SYSTEM_AUTO_MONITOR_USER_ID  # Use same as auto-monitor by default
)

# System user for data sync operations
SYSTEM_SYNC_USER_ID = os.getenv(
    "SYSTEM_SYNC_USER_ID",
    SYSTEM_AUTO_MONITOR_USER_ID
)
