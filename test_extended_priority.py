#!/usr/bin/env python3
"""
Test script for Extended Priority System
Tests backwards compatibility and new features
"""

import json
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from priority_system_architecture import (
    PriorityLevel, TimeWindow, PrioritySystemValidator, 
    DefaultValueHandler, create_extended_priority_time_windows,
    PrioritySystemConfig
)
from datetime import datetime
import pytz

def test_backwards_compatibility():
    """Test that legacy format still works"""
    print("🔄 Testing Backwards Compatibility...")
    
    addresses = ["Start", "Priority Address 1", "Priority Address 2", "End"]
    legacy_config = [
        {
            "address": "Priority Address 1",
            "priority_level": "high",  # Legacy format
            "preferred_time_window": "early"  # Legacy format
        },
        {
            "address": "Priority Address 2",
            "priority_level": "medium"
            # Missing preferred_time_window - should default to "middle"
        }
    ]
    
    base_start_time = datetime.now(pytz.UTC)
    
    try:
        result = create_extended_priority_time_windows(addresses, legacy_config, base_start_time)
        if result and result.get('enabled'):
            print("✅ Legacy format compatibility: PASSED")
        else:
            print("❌ Legacy format compatibility: FAILED")
            return False
    except Exception as e:
        print(f"❌ Legacy format compatibility: FAILED - {e}")
        return False
    
    return True

def test_extended_features():
    """Test new extended priority levels and time windows"""
    print("🚀 Testing Extended Features...")
    
    addresses = ["Start", "Critical Hospital", "VIP Client", "Backup Location", "End"]
    extended_config = [
        {
            "address": "Critical Hospital",
            "priority_level": "critical_high",  # New level
            "preferred_time_window": "earliest",  # New window
            "penalty_cost": 2000.0  # Custom penalty
        },
        {
            "address": "VIP Client", 
            "priority_level": "high",
            "preferred_time_window": "early"
        },
        {
            "address": "Backup Location",
            "priority_level": "critical_low",  # New level
            "preferred_time_window": "latest"  # New window
        }
    ]
    
    base_start_time = datetime.now(pytz.UTC)
    
    try:
        result = create_extended_priority_time_windows(addresses, extended_config, base_start_time)
        if result and result.get('enabled') and len(result.get('windows', [])) == 3:
            print("✅ Extended features: PASSED")
        else:
            print("❌ Extended features: FAILED")
            return False
    except Exception as e:
        print(f"❌ Extended features: FAILED - {e}")
        return False
    
    return True

def test_input_validation():
    """Test input validation with error handling"""
    print("🛡️ Testing Input Validation...")
    
    addresses = ["Start", "Valid Address", "End"]
    
    # Test invalid priority level
    invalid_priority_config = [
        {
            "address": "Valid Address",
            "priority_level": "extreme",  # Invalid
            "preferred_time_window": "early"
        }
    ]
    
    try:
        PrioritySystemValidator.validate_priority_addresses_config(invalid_priority_config, addresses)
        print("❌ Input validation (invalid priority): FAILED - Should have raised error")
        return False
    except ValueError as e:
        if "Invalid priority_level" in str(e):
            print("✅ Input validation (invalid priority): PASSED")
        else:
            print(f"❌ Input validation (invalid priority): FAILED - Wrong error: {e}")
            return False
    
    # Test invalid time window
    invalid_time_config = [
        {
            "address": "Valid Address",
            "priority_level": "high", 
            "preferred_time_window": "never"  # Invalid
        }
    ]
    
    try:
        PrioritySystemValidator.validate_priority_addresses_config(invalid_time_config, addresses)
        print("❌ Input validation (invalid time window): FAILED - Should have raised error")
        return False
    except ValueError as e:
        if "Invalid preferred_time_window" in str(e):
            print("✅ Input validation (invalid time window): PASSED")
        else:
            print(f"❌ Input validation (invalid time window): FAILED - Wrong error: {e}")
            return False
    
    # Test missing address
    missing_address_config = [
        {
            "address": "Nonexistent Address",
            "priority_level": "high",
            "preferred_time_window": "early"
        }
    ]
    
    try:
        PrioritySystemValidator.validate_priority_addresses_config(missing_address_config, addresses)
        print("❌ Input validation (missing address): FAILED - Should have raised error")
        return False
    except ValueError as e:
        if "not found in addresses list" in str(e):
            print("✅ Input validation (missing address): PASSED")
        else:
            print(f"❌ Input validation (missing address): FAILED - Wrong error: {e}")
            return False
    
    return True

def test_default_values():
    """Test default value application"""
    print("⚙️ Testing Default Values...")
    
    addresses = ["Start", "Address 1", "Address 2", "End"]
    minimal_config = [
        {
            "address": "Address 1",
            "priority_level": "high"
            # Missing preferred_time_window
        },
        {
            "address": "Address 2"
            # Missing both priority_level and preferred_time_window
        }
    ]
    
    try:
        # Apply defaults
        processed_config = DefaultValueHandler.apply_defaults_to_priority_config(minimal_config)
        
        # Check that defaults were applied
        if (processed_config[0]["preferred_time_window"] == "middle" and
            processed_config[1]["priority_level"] == "medium" and 
            processed_config[1]["preferred_time_window"] == "middle"):
            print("✅ Default values: PASSED")
        else:
            print("❌ Default values: FAILED - Defaults not applied correctly")
            return False
    except Exception as e:
        print(f"❌ Default values: FAILED - {e}")
        return False
    
    return True

def test_priority_statistics():
    """Test priority statistics generation"""
    print("📊 Testing Priority Statistics...")
    
    addresses = ["Start", "Addr1", "Addr2", "Addr3", "End"]
    config = [
        {
            "address": "Addr1",
            "priority_level": "critical_high",
            "preferred_time_window": "earliest"
        },
        {
            "address": "Addr2", 
            "priority_level": "high",
            "preferred_time_window": "early"
        },
        {
            "address": "Addr3",
            "priority_level": "critical_high",  # Duplicate level
            "preferred_time_window": "middle"
        }
    ]
    
    try:
        validated_config = PrioritySystemValidator.validate_priority_addresses_config(config, addresses)
        stats = validated_config.get_priority_statistics()
        
        expected_priority_breakdown = {
            'critical_high': 2, 'high': 1, 'medium': 0, 'low': 0, 'critical_low': 0
        }
        expected_time_breakdown = {
            'earliest': 1, 'early': 1, 'middle': 1, 'late': 0, 'latest': 0
        }
        
        if (stats['total_priority_addresses'] == 3 and
            stats['priority_breakdown'] == expected_priority_breakdown and
            stats['time_window_breakdown'] == expected_time_breakdown):
            print("✅ Priority statistics: PASSED")
        else:
            print("❌ Priority statistics: FAILED")
            print(f"Expected: {expected_priority_breakdown}")
            print(f"Got: {stats['priority_breakdown']}")
            return False
    except Exception as e:
        print(f"❌ Priority statistics: FAILED - {e}")
        return False
    
    return True

def run_all_tests():
    """Run all tests and report results"""
    print("🧪 Running Extended Priority System Tests\n")
    
    tests = [
        test_backwards_compatibility,
        test_extended_features,
        test_input_validation,
        test_default_values,
        test_priority_statistics
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()  # Empty line between tests
    
    print(f"🏁 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Extended Priority System is working correctly.")
        return True
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)