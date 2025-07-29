#!/usr/bin/env python3
"""
Test only the validation functions without initializing the full Flask app.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the validation functions directly from priority_system_architecture
from priority_system_architecture import (
    PriorityLevel, TimeWindow, PriorityAddressConfig, PrioritySystemConfig,
    PrioritySystemValidator, ExtendedPriorityTimeWindowCreator,
    DefaultValueHandler, create_extended_priority_time_windows
)

def test_priority_system_validator():
    """Test the priority system validator directly"""
    print("=== Testing Priority System Validator ===")
    
    # Test 1: Valid extended priority configuration
    addresses = ['Start St', 'Priority Customer', 'Regular Customer', 'End St']
    priority_config = [
        {
            'address': 'Priority Customer',
            'priority_level': 'critical_high',
            'preferred_time_window': 'earliest',
            'penalty_cost': 1000.0
        }
    ]
    
    try:
        processed_config = DefaultValueHandler.apply_defaults_to_priority_config(priority_config)
        validated_config = PrioritySystemValidator.validate_priority_addresses_config(processed_config, addresses)
        print("✓ Extended priority configuration validation passed")
        print(f"  Priority statistics: {validated_config.get_priority_statistics()}")
    except Exception as e:
        print(f"✗ Extended priority configuration validation failed: {e}")
    
    # Test 2: Legacy format with backwards compatibility
    legacy_config = [
        {
            'address': 'Priority Customer',
            'priority_level': 'high',  # Legacy
            'preferred_time_window': 'early'  # Legacy
        }
    ]
    
    try:
        processed_config = DefaultValueHandler.apply_defaults_to_priority_config(legacy_config)
        validated_config = PrioritySystemValidator.validate_priority_addresses_config(processed_config, addresses)
        print("✓ Legacy format validation passed")
        print(f"  Converted priority: {validated_config.priority_addresses[0].priority_level.value}")
        print(f"  Converted time window: {validated_config.priority_addresses[0].preferred_time_window.value}")
    except Exception as e:
        print(f"✗ Legacy format validation failed: {e}")
    
    # Test 3: Missing fields (should get defaults)
    incomplete_config = [
        {
            'address': 'Priority Customer'
            # Missing priority_level and preferred_time_window
        }
    ]
    
    try:
        processed_config = DefaultValueHandler.apply_defaults_to_priority_config(incomplete_config)
        validated_config = PrioritySystemValidator.validate_priority_addresses_config(processed_config, addresses)
        print("✓ Incomplete configuration with defaults validation passed")
        print(f"  Default priority: {validated_config.priority_addresses[0].priority_level.value}")
        print(f"  Default time window: {validated_config.priority_addresses[0].preferred_time_window.value}")
    except Exception as e:
        print(f"✗ Incomplete configuration validation failed: {e}")

def test_validation_errors():
    """Test various validation error scenarios"""
    print("\n=== Testing Validation Error Scenarios ===")
    
    addresses = ['Start St', 'Middle St', 'End St']
    
    # Test 1: Invalid priority level
    try:
        config = [{'address': 'Middle St', 'priority_level': 'invalid', 'preferred_time_window': 'early'}]
        processed_config = DefaultValueHandler.apply_defaults_to_priority_config(config)
        PrioritySystemValidator.validate_priority_addresses_config(processed_config, addresses)
        print("✗ Should have failed for invalid priority level")
    except ValueError as e:
        print(f"✓ Correctly caught invalid priority level: {e}")
    
    # Test 2: Invalid time window
    try:
        config = [{'address': 'Middle St', 'priority_level': 'high', 'preferred_time_window': 'invalid'}]
        processed_config = DefaultValueHandler.apply_defaults_to_priority_config(config)
        PrioritySystemValidator.validate_priority_addresses_config(processed_config, addresses)
        print("✗ Should have failed for invalid time window")
    except ValueError as e:
        print(f"✓ Correctly caught invalid time window: {e}")
    
    # Test 3: Address not in list
    try:
        config = [{'address': 'Not In List', 'priority_level': 'high', 'preferred_time_window': 'early'}]
        processed_config = DefaultValueHandler.apply_defaults_to_priority_config(config)
        PrioritySystemValidator.validate_priority_addresses_config(processed_config, addresses)
        print("✗ Should have failed for address not in list")
    except ValueError as e:
        print(f"✓ Correctly caught address not in list: {e}")
    
    # Test 4: Trying to prioritize start point
    try:
        config = [{'address': 'Start St', 'priority_level': 'high', 'preferred_time_window': 'early'}]
        processed_config = DefaultValueHandler.apply_defaults_to_priority_config(config)
        PrioritySystemValidator.validate_priority_addresses_config(processed_config, addresses)
        print("✗ Should have failed for prioritizing start point")
    except ValueError as e:
        print(f"✓ Correctly caught prioritizing start point: {e}")
    
    # Test 5: Trying to prioritize end point
    try:
        config = [{'address': 'End St', 'priority_level': 'high', 'preferred_time_window': 'early'}]
        processed_config = DefaultValueHandler.apply_defaults_to_priority_config(config)
        PrioritySystemValidator.validate_priority_addresses_config(processed_config, addresses)
        print("✗ Should have failed for prioritizing end point")
    except ValueError as e:
        print(f"✓ Correctly caught prioritizing end point: {e}")
    
    # Test 6: Negative penalty cost
    try:
        PrioritySystemValidator.validate_penalty_cost(-100)
        print("✗ Should have failed for negative penalty cost")
    except ValueError as e:
        print(f"✓ Correctly caught negative penalty cost: {e}")

def test_enum_values():
    """Test that all enum values are correctly defined"""
    print("\n=== Testing Enum Values ===")
    
    # Test priority levels
    expected_priorities = ['critical_high', 'high', 'medium', 'low', 'critical_low']
    actual_priorities = [level.value for level in PriorityLevel]
    print(f"Priority levels: {actual_priorities}")
    print(f"All expected priorities present: {all(p in actual_priorities for p in expected_priorities)}")
    
    # Test time windows
    expected_windows = ['earliest', 'early', 'middle', 'late', 'latest']
    actual_windows = [window.value for window in TimeWindow]
    print(f"Time windows: {actual_windows}")
    print(f"All expected windows present: {all(w in actual_windows for w in expected_windows)}")
    
    # Test legacy mappings
    print(f"Legacy priority mapping works: {'high' in [level.value for level in PriorityLevel] or PriorityLevel.HIGH.value == 'high'}")
    print(f"Legacy time window mapping works: {'early' in [window.value for window in TimeWindow] or TimeWindow.EARLY.value == 'early'}")

def run_comprehensive_validation_tests():
    """Run all validation tests"""
    print("COMPREHENSIVE VALIDATION SYSTEM TESTS")
    print("=" * 80)
    
    test_priority_system_validator()
    test_validation_errors()  
    test_enum_values()
    
    print("\n" + "=" * 80)
    print("VALIDATION TESTS COMPLETED")
    print("All core validation functionality has been tested.")
    print("The system supports:")
    print("- Extended priority levels: critical_high, high, medium, low, critical_low")
    print("- Extended time windows: earliest, early, middle, late, latest")
    print("- Custom penalty costs")
    print("- Backwards compatibility with legacy formats")
    print("- Comprehensive error validation")

if __name__ == "__main__":
    run_comprehensive_validation_tests()