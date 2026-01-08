#!/usr/bin/env python3
"""Simple test script to verify kittiwake imports and basic functionality."""

import sys

print("Testing imports...")

try:
    from kittiwake.models.dataset import Dataset
    print("✓ Dataset model imported")
except Exception as e:
    print(f"✗ Failed to import Dataset: {e}")
    sys.exit(1)

try:
    from kittiwake.services.data_loader import DataLoader
    print("✓ DataLoader imported")
except Exception as e:
    print(f"✗ Failed to import DataLoader: {e}")
    sys.exit(1)

try:
    from kittiwake.widgets import DatasetTable, DatasetTabs, HelpOverlay
    print("✓ Widgets imported")
except Exception as e:
    print(f"✗ Failed to import widgets: {e}")
    sys.exit(1)

try:
    from kittiwake.screens.main_screen import MainScreen
    print("✓ MainScreen imported")
except Exception as e:
    print(f"✗ Failed to import MainScreen: {e}")
    sys.exit(1)

try:
    from kittiwake.app import KittiwakeApp
    print("✓ KittiwakeApp imported")
except Exception as e:
    print(f"✗ Failed to import KittiwakeApp: {e}")
    sys.exit(1)

print("\n✓ All imports successful!")

# Test DataLoader instantiation
try:
    loader = DataLoader()
    print(f"✓ DataLoader instantiated with cache_dir: {loader.cache_dir}")
except Exception as e:
    print(f"✗ Failed to instantiate DataLoader: {e}")
    sys.exit(1)

print("\n✓ All tests passed!")
