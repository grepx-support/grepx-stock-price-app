#!/usr/bin/env python
"""Test application initialization without Airflow"""

import sys
import os
from pathlib import Path

# Setup paths
PROJECT_ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

print("=" * 70)
print("TESTING APPLICATION INITIALIZATION")
print("=" * 70)

print("\n[1] Checking library paths...")
libs = [
    PROJECT_ROOT.parent / "libs" / "grepx-orm-libs" / "src",
    PROJECT_ROOT.parent / "libs" / "grepx-connection-registry" / "src",
    PROJECT_ROOT.parent / "libs" / "prefect_framework" / "src"
]
for lib in libs:
    status = "✓ EXISTS" if lib.exists() else "✗ MISSING"
    print(f"  {status}: {lib}")

print("\n[2] Testing main.py import...")
try:
    from main import get_connection, get_config
    print("  ✓ Successfully imported main")
except Exception as e:
    print(f"  ✗ Failed to import main: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n[3] Testing get_config()...")
try:
    config = get_config()
    print(f"  ✓ Config loaded: environment = {getattr(config.app, 'environment', '?')}")
except Exception as e:
    print(f"  ✗ Failed to get config: {e}")
    import traceback
    traceback.print_exc()

print("\n[4] Testing get_connection('primary_celery')...")
try:
    conn = get_connection("primary_celery")
    print(f"  ✓ Celery connection: {conn}")
except Exception as e:
    print(f"  ✗ Failed to get celery connection: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("TEST COMPLETE")
print("=" * 70)