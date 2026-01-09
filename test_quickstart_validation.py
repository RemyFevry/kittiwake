"""Automated validation of Feature 002 quickstart guide.

This script validates that the Feature 002 (Column Type Display and Quick Filter) 
quickstart guide steps work as expected.
"""

import sys
from pathlib import Path
from typing import cast

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from kittiwake.services.type_detector import detect_column_type_category
from kittiwake.utils.type_colors import (
    TypeCategory,
    get_type_icon,
    get_type_color,
    get_operators_for_type,
    map_operator_to_symbol,
)
from kittiwake.widgets.modals.filter_modal import FilterModal


def validate_step1_type_colors():
    """Step 1: Validate type detection and colors for expected Titanic columns."""
    print("\n=== Step 1: Type Colors and Icons ===")
    
    # Expected type mappings from quickstart guide (dtype name -> expected type)
    test_dtypes = {
        "PassengerId": ("Int64", "numeric", "#", "blue"),
        "Survived": ("Int64", "numeric", "#", "blue"),  # Int64 detected as numeric
        "Pclass": ("Int64", "numeric", "#", "blue"),
        "Name": ("String", "text", '"', "green"),
        "Sex": ("String", "text", '"', "green"),
        "Age": ("Float64", "numeric", "#", "blue"),
        "Fare": ("Float64", "numeric", "#", "blue"),
        "Ticket": ("String", "text", '"', "green"),
    }
    
    all_correct = True
    for col_name, (dtype, expected_type, expected_icon, expected_color) in test_dtypes.items():
        detected_type = detect_column_type_category(dtype)
        icon = get_type_icon(detected_type)
        color = get_type_color(detected_type)
        
        status = "✓" if detected_type == expected_type else "❌"
        
        if detected_type != expected_type:
            all_correct = False
            print(f"  {status} {col_name} ({dtype}): expected {expected_type}, got {detected_type}")
        else:
            print(f"  {status} {col_name} ({dtype}): {detected_type} ({icon} {color})")
    
    if all_correct:
        print("✓ Step 1 PASSED: All column types detected correctly")
        return True
    else:
        print("❌ Step 1 FAILED: Some type detections incorrect")
        return False


def validate_step2_quick_filter():
    """Step 2: Validate quick filter creation from column header."""
    print("\n=== Step 2: Quick Filter from Column Header ===")
    
    # Simulate clicking on Age column header
    column_name = "Age"
    dtype = "Int64"
    
    # Detect type
    type_category = detect_column_type_category(dtype)
    print(f"✓ Column: {column_name}, Type: {type_category}")
    
    # Get operators for numeric type
    operators = get_operators_for_type(type_category)
    print(f"✓ Available operators: {operators}")
    
    # Expected numeric operators from quickstart
    expected_operators = ["equals (=)", "not equals (!=)", "greater than (>)", 
                         "less than (<)", "greater than or equal (>=)", 
                         "less than or equal (<=)"]
    
    if all(op in operators for op in expected_operators[:6]):
        print("✓ Numeric operators available")
    else:
        print("❌ FAIL: Missing expected numeric operators")
        return False
    
    # Simulate user selecting operator and value
    filter_data = {
        "column": column_name,
        "operator": "greater than (>)",  # Display name
        "value": "30"
    }
    
    # Map operator to symbol (as done in main_screen.py)
    filter_data["operator"] = map_operator_to_symbol(filter_data["operator"])
    print(f"✓ Operator mapped: 'greater than (>)' -> '{filter_data['operator']}'")
    
    # Build operation using FilterModal
    columns = [column_name]
    modal = FilterModal(columns=columns)
    
    try:
        code, display, params = modal._build_filter_operation(filter_data)
        print(f"✓ Generated code: {code}")
        print(f"✓ Display: {display}")
        
        # Validate generated code
        expected_code = 'df = df.filter(nw.col("Age") > 30.0)'
        if code == expected_code:
            print("✓ Step 2 PASSED: Quick filter generates correct operation")
            return True
        else:
            print(f"❌ FAIL: Expected code {expected_code}, got {code}")
            return False
    except Exception as e:
        print(f"❌ FAIL: Filter generation failed: {e}")
        return False


def validate_step3_text_filter():
    """Step 3: Validate text column filtering."""
    print("\n=== Step 3: Filter Text Columns ===")
    
    # Simulate clicking on Sex column header
    column_name = "Sex"
    dtype = "String"
    
    # Detect type
    type_category = detect_column_type_category(dtype)
    print(f"✓ Column: {column_name}, Type: {type_category}")
    
    if type_category != "text":
        print(f"❌ FAIL: Expected text type, got {type_category}")
        return False
    
    # Get operators for text type
    operators = get_operators_for_type(type_category)
    print(f"✓ Available operators: {operators}")
    
    # Expected text operators from quickstart
    expected_operators = ["equals", "not equals", "contains"]
    
    if all(op in operators for op in expected_operators):
        print("✓ Text operators available")
    else:
        print("❌ FAIL: Missing expected text operators")
        return False
    
    # Verify no numeric operators are present
    numeric_operators = ["greater than (>)", "less than (<)"]
    if any(op in operators for op in numeric_operators):
        print("❌ FAIL: Numeric operators should not be available for text columns")
        return False
    
    print("✓ No numeric operators for text columns")
    
    # Simulate creating a text filter
    filter_data = {
        "column": column_name,
        "operator": "equals",
        "value": "female"
    }
    
    # Map operator
    filter_data["operator"] = map_operator_to_symbol(filter_data["operator"])
    
    # Build operation
    modal = FilterModal(columns=[column_name])
    
    try:
        code, display, params = modal._build_filter_operation(filter_data)
        print(f"✓ Generated code: {code}")
        print(f"✓ Display: {display}")
        
        # Validate it's a text comparison
        if 'nw.col("Sex") == "female"' in code:
            print("✓ Step 3 PASSED: Text filter generates correct operation")
            return True
        else:
            print(f"❌ FAIL: Unexpected code generated: {code}")
            return False
    except Exception as e:
        print(f"❌ FAIL: Filter generation failed: {e}")
        return False


def validate_step5_icon_identification():
    """Step 5: Validate icon-only identification (accessibility)."""
    print("\n=== Step 5: Accessibility - Icon-Only Identification ===")
    
    # Test all type categories have unique icons
    categories: list[TypeCategory] = ["numeric", "text", "date", "boolean", "unknown"]
    icons = {}
    
    for category in categories:
        icon = get_type_icon(category)
        if icon in icons.values():
            print(f"❌ FAIL: Duplicate icon for {category}")
            return False
        icons[category] = icon
        print(f"  ✓ {category}: '{icon}'")
    
    # Verify expected icons from quickstart
    expected_icons = {
        "numeric": "#",
        "text": '"',
        "date": "@",
        "boolean": "?",
        "unknown": "·"
    }
    
    all_correct = True
    for category_str, expected_icon in expected_icons.items():
        category = cast(TypeCategory, category_str)
        actual_icon = icons[category]
        if actual_icon != expected_icon:
            print(f"  ❌ {category}: expected '{expected_icon}', got '{actual_icon}'")
            all_correct = False
    
    if all_correct:
        print("✓ Step 5 PASSED: All icons match quickstart guide")
        return True
    else:
        print("❌ FAIL: Icon mismatch")
        return False


def main():
    """Run all validation steps."""
    print("=" * 60)
    print("Feature 002 Quickstart Validation")
    print("=" * 60)
    
    results = {
        "Step 1 - Type Colors": validate_step1_type_colors(),
        "Step 2 - Quick Filter": validate_step2_quick_filter(),
        "Step 3 - Text Filter": validate_step3_text_filter(),
        "Step 5 - Icon Identification": validate_step5_icon_identification(),
    }
    
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for step, passed in results.items():
        status = "✓ PASSED" if passed else "❌ FAILED"
        print(f"{status}: {step}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n✓✓✓ ALL VALIDATION STEPS PASSED ✓✓✓")
        print("\nThe quickstart guide is accurate and all features work as documented.")
        return 0
    else:
        print("\n❌ SOME VALIDATION STEPS FAILED")
        print("\nThe quickstart guide needs updates to match implementation.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
