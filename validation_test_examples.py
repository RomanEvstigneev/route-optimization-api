#!/usr/bin/env python3
"""
Test examples for the comprehensive validation system.
This file contains example requests to test both backwards compatibility 
and the new extended priority system functionality.
"""

import json
import requests

# Test server URL (adjust as needed)
BASE_URL = "http://localhost:8080"

# =============================================================================
# BASIC TESTS
# =============================================================================

def test_basic_request():
    """Test basic route optimization without any optional parameters"""
    data = {
        "addresses": [
            "123 Start Street, City, State",
            "456 Customer Ave, City, State", 
            "789 Another St, City, State",
            "999 End Road, City, State"
        ]
    }
    
    print("=== Testing Basic Request ===")
    print(f"Request: {json.dumps(data, indent=2)}")
    return data

def test_invalid_addresses():
    """Test various invalid address configurations"""
    invalid_cases = [
        # Missing addresses
        {},
        # Non-list addresses
        {"addresses": "not a list"},
        # Too few addresses
        {"addresses": ["only one"]},
        # Empty address
        {"addresses": ["start", "", "end"]},
        # Non-string address
        {"addresses": ["start", 123, "end"]}
    ]
    
    print("=== Testing Invalid Address Cases ===")
    for i, case in enumerate(invalid_cases):
        print(f"Invalid case {i+1}: {json.dumps(case)}")
    
    return invalid_cases

# =============================================================================
# BACKWARDS COMPATIBILITY TESTS
# =============================================================================

def test_legacy_priority_system():
    """Test backwards compatibility with old priority system"""
    data = {
        "addresses": [
            "123 Start Street, City, State",
            "456 High Priority Customer, City, State",
            "789 Medium Priority Customer, City, State", 
            "321 Low Priority Customer, City, State",
            "999 End Road, City, State"
        ],
        "priority_addresses": [
            {
                "address": "456 High Priority Customer, City, State",
                "priority_level": "high",  # Legacy format
                "preferred_time_window": "early"  # Legacy format
            },
            {
                "address": "789 Medium Priority Customer, City, State",
                "priority_level": "medium",  # Legacy format
                "preferred_time_window": "middle"  # Legacy format
            },
            {
                "address": "321 Low Priority Customer, City, State",
                "priority_level": "low",  # Legacy format
                "preferred_time_window": "late"  # Legacy format
            }
        ]
    }
    
    print("=== Testing Legacy Priority System ===")
    print(f"Request: {json.dumps(data, indent=2)}")
    return data

def test_mixed_legacy_new_format():
    """Test mixing legacy and new priority formats (should work with defaults)"""
    data = {
        "addresses": [
            "123 Start Street, City, State",
            "456 Old Format Customer, City, State",
            "789 Partial New Format Customer, City, State",
            "999 End Road, City, State"
        ],
        "priority_addresses": [
            # Legacy format - should get defaults applied
            {
                "address": "456 Old Format Customer, City, State"
                # Missing priority_level and preferred_time_window - should get defaults
            },
            # Partial new format
            {
                "address": "789 Partial New Format Customer, City, State",
                "priority_level": "critical_high"
                # Missing preferred_time_window - should get default
            }
        ]
    }
    
    print("=== Testing Mixed Legacy/New Format ===")
    print(f"Request: {json.dumps(data, indent=2)}")
    return data

# =============================================================================
# EXTENDED PRIORITY SYSTEM TESTS
# =============================================================================

def test_extended_priority_system():
    """Test the new extended priority system with all features"""
    data = {
        "addresses": [
            "123 Start Street, City, State",
            "456 Critical High Customer, City, State",
            "789 High Priority Customer, City, State",
            "321 Medium Priority Customer, City, State",
            "654 Low Priority Customer, City, State",
            "987 Critical Low Customer, City, State",
            "999 End Road, City, State"
        ],
        "priority_addresses": [
            {
                "address": "456 Critical High Customer, City, State",
                "priority_level": "critical_high",
                "preferred_time_window": "earliest",
                "penalty_cost": 2000.0  # Custom high penalty
            },
            {
                "address": "789 High Priority Customer, City, State", 
                "priority_level": "high",
                "preferred_time_window": "early"
                # No penalty_cost - should use default
            },
            {
                "address": "321 Medium Priority Customer, City, State",
                "priority_level": "medium",
                "preferred_time_window": "middle"
            },
            {
                "address": "654 Low Priority Customer, City, State",
                "priority_level": "low", 
                "preferred_time_window": "late"
            },
            {
                "address": "987 Critical Low Customer, City, State",
                "priority_level": "critical_low",
                "preferred_time_window": "latest",
                "penalty_cost": 1.0  # Very low penalty
            }
        ],
        "start_time": "2024-12-21T08:00:00Z",
        "objective": "minimize_time",
        "service_time_minutes": 5,
        "route_name": "Extended Priority Test Route"
    }
    
    print("=== Testing Extended Priority System ===")
    print(f"Request: {json.dumps(data, indent=2)}")
    return data

def test_priority_validation_errors():
    """Test various priority system validation errors"""
    error_cases = [
        # Invalid priority level
        {
            "addresses": ["start", "middle", "end"],
            "priority_addresses": [
                {
                    "address": "middle",
                    "priority_level": "invalid_priority",
                    "preferred_time_window": "early"
                }
            ]
        },
        # Invalid time window
        {
            "addresses": ["start", "middle", "end"],
            "priority_addresses": [
                {
                    "address": "middle", 
                    "priority_level": "high",
                    "preferred_time_window": "invalid_window"
                }
            ]
        },
        # Priority address not in addresses list
        {
            "addresses": ["start", "middle", "end"],
            "priority_addresses": [
                {
                    "address": "not_in_list",
                    "priority_level": "high",
                    "preferred_time_window": "early"
                }
            ]
        },
        # Trying to prioritize start point
        {
            "addresses": ["start", "middle", "end"],
            "priority_addresses": [
                {
                    "address": "start",  # Start point - should be rejected
                    "priority_level": "high",
                    "preferred_time_window": "early"
                }
            ]
        },
        # Trying to prioritize end point
        {
            "addresses": ["start", "middle", "end"],
            "priority_addresses": [
                {
                    "address": "end",  # End point - should be rejected
                    "priority_level": "high", 
                    "preferred_time_window": "early"
                }
            ]
        },
        # Invalid penalty cost
        {
            "addresses": ["start", "middle", "end"],
            "priority_addresses": [
                {
                    "address": "middle",
                    "priority_level": "high",
                    "preferred_time_window": "early",
                    "penalty_cost": -100  # Negative - should be rejected
                }
            ]
        },
        # Duplicate priority addresses
        {
            "addresses": ["start", "middle", "end"],
            "priority_addresses": [
                {
                    "address": "middle",
                    "priority_level": "high",
                    "preferred_time_window": "early"
                },
                {
                    "address": "middle",  # Duplicate - should be rejected
                    "priority_level": "low",
                    "preferred_time_window": "late"
                }
            ]
        }
    ]
    
    print("=== Testing Priority Validation Errors ===")
    for i, case in enumerate(error_cases):
        print(f"Error case {i+1}: {json.dumps(case, indent=2)}")
    
    return error_cases

# =============================================================================
# FULL SYSTEM TESTS
# =============================================================================

def test_complete_system():
    """Test complete system with all optional parameters"""
    data = {
        "addresses": [
            "123 Start Street, City, State",
            "456 Customer 1, City, State",
            "789 Customer 2, City, State",
            "321 Customer 3, City, State",
            "999 End Road, City, State"
        ],
        "priority_addresses": [
            {
                "address": "456 Customer 1, City, State",
                "priority_level": "critical_high",
                "preferred_time_window": "earliest",
                "penalty_cost": 1500.0
            },
            {
                "address": "789 Customer 2, City, State",
                "priority_level": "medium",
                "preferred_time_window": "middle"
            }
        ],
        "time_windows": {
            "enabled": True,
            "windows": [
                {
                    "address_index": 3,
                    "soft_start_time": "2024-12-21T10:00:00Z",
                    "soft_end_time": "2024-12-21T12:00:00Z",
                    "cost_per_hour_before": 5.0,
                    "cost_per_hour_after": 15.0
                }
            ]
        },
        "start_time": "2024-12-21T08:00:00Z",
        "objective": "minimize_time",
        "service_time_minutes": 4,
        "route_name": "Complete System Test"
    }
    
    print("=== Testing Complete System ===")
    print(f"Request: {json.dumps(data, indent=2)}")
    return data

# =============================================================================
# API TESTING FUNCTIONS
# =============================================================================

def make_api_request(data, endpoint="/api/optimize"):
    """Make an API request and return the response"""
    url = BASE_URL + endpoint
    headers = {'Content-Type': 'application/json'}
    
    try:
        response = requests.post(url, json=data, headers=headers)
        return {
            'status_code': response.status_code,
            'response_data': response.json(),
            'success': response.status_code == 200
        }
    except Exception as e:
        return {
            'status_code': None,
            'response_data': {'error': str(e)},
            'success': False
        }

def run_all_tests():
    """Run all validation tests"""
    print("=" * 80)
    print("COMPREHENSIVE VALIDATION SYSTEM TESTS")
    print("=" * 80)
    
    # Test cases to run
    test_cases = [
        ("Basic Request", test_basic_request()),
        ("Legacy Priority System", test_legacy_priority_system()),
        ("Mixed Format", test_mixed_legacy_new_format()),
        ("Extended Priority System", test_extended_priority_system()),
        ("Complete System", test_complete_system())
    ]
    
    # Run valid test cases
    for name, data in test_cases:
        print(f"\n{'-' * 60}")
        print(f"Testing: {name}")
        print(f"{'-' * 60}")
        
        result = make_api_request(data)
        print(f"Status Code: {result['status_code']}")
        print(f"Success: {result['success']}")
        
        if result['success']:
            response = result['response_data']
            print(f"Validation Version: {response.get('validation_version', 'N/A')}")
            print(f"Validation Passed: {response.get('validation_passed', 'N/A')}")
            if 'validation_summary' in response:
                print(f"Validation Summary: {response['validation_summary']}")
            if 'priority_statistics' in response:
                print(f"Priority Statistics: {response['priority_statistics']}")
        else:
            print(f"Error: {result['response_data']}")
    
    # Test error cases
    print(f"\n{'-' * 60}")
    print("Testing Invalid Cases")
    print(f"{'-' * 60}")
    
    invalid_cases = test_invalid_addresses()
    for i, case in enumerate(invalid_cases):
        result = make_api_request(case)
        print(f"Invalid case {i+1} - Status: {result['status_code']}, "
              f"Expected error: {'YES' if not result['success'] else 'NO'}")
    
    priority_error_cases = test_priority_validation_errors()
    for i, case in enumerate(priority_error_cases):
        result = make_api_request(case)
        print(f"Priority error case {i+1} - Status: {result['status_code']}, "
              f"Expected error: {'YES' if not result['success'] else 'NO'}")

if __name__ == "__main__":
    print("This file contains test examples for the validation system.")
    print("To run tests against a live server, uncomment the run_all_tests() call below.")
    print("Make sure to update BASE_URL to point to your running server.")
    print()
    print("Example usage:")
    print("  python validation_test_examples.py")
    print()
    
    # Uncomment to run tests against live server
    # run_all_tests()
    
    # Just show the test data for now
    print("Sample test data:")
    basic_test = test_basic_request()
    extended_test = test_extended_priority_system()
    print("\nBasic request example:")
    print(json.dumps(basic_test, indent=2))
    print("\nExtended priority system example:")
    print(json.dumps(extended_test, indent=2))