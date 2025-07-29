#!/usr/bin/env python3
"""
Simple test for extended priority system
Tests the new priority levels and time windows according to the priority mapping:
- critical_high -> earliest window, 1000 penalty
- high -> early window, 500 penalty
- low -> late window, 200 penalty  
- critical_low -> latest window, 100 penalty
"""

import requests
import json

# Test configuration
API_URL = "http://localhost:8080/api/optimize"

def test_extended_priorities():
    """Test all extended priority levels and time windows"""
    
    test_data = {
        "addresses": [
            "Berlin Hauptbahnhof, Berlin, Germany",     # Start point
            "Critical High Priority, Munich, Germany",  # Should be first
            "High Priority, Hamburg, Germany",          # Should be second
            "Medium Priority, Dresden, Germany",        # Should be in middle
            "Low Priority, Frankfurt, Germany",         # Should be near end
            "Critical Low Priority, Cologne, Germany",  # Should be last
            "Alexanderplatz, Berlin, Germany"           # End point
        ],
        "priority_addresses": [
            {
                "address": "Critical High Priority, Munich, Germany",
                "priority_level": "critical_high",
                "preferred_time_window": "earliest"
            },
            {
                "address": "High Priority, Hamburg, Germany", 
                "priority_level": "high",
                "preferred_time_window": "early"
            },
            {
                "address": "Medium Priority, Dresden, Germany",
                "priority_level": "medium", 
                "preferred_time_window": "middle"
            },
            {
                "address": "Low Priority, Frankfurt, Germany",
                "priority_level": "low",
                "preferred_time_window": "late"
            },
            {
                "address": "Critical Low Priority, Cologne, Germany",
                "priority_level": "critical_low",
                "preferred_time_window": "latest"
            }
        ],
        "start_time": "2024-12-21T08:00:00Z"
    }
    
    print("🧪 Testing Extended Priority System")
    print("=" * 50)
    
    try:
        response = requests.post(API_URL, json=test_data, headers={'Content-Type': 'application/json'})
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Test PASSED - API accepted extended priorities")
            print(f"📋 Optimized route order:")
            
            for i, address in enumerate(result['optimized_addresses'], 1):
                print(f"  {i}. {address}")
            
            # Check if critical_high priority is early in route
            critical_high_addr = "Critical High Priority, Munich, Germany"
            for i, addr in enumerate(result['optimized_addresses']):
                if addr == critical_high_addr:
                    if i <= 2:  # Position 1 or 2 (excluding start)
                        print(f"✅ Critical high priority delivered early (position {i})")
                    else:
                        print(f"⚠️ Critical high priority not early enough (position {i})")
                    break
            
            print(f"\n📊 Optimization Details:")
            print(f"  - Algorithm: {result.get('algorithm', 'Unknown')}")
            print(f"  - Total time: {result['timing_info']['total_duration_minutes']} minutes")
            print(f"  - Service time per stop: {result['timing_info']['service_time_per_stop_minutes']} minutes")
            
        else:
            print(f"❌ Test FAILED - API returned {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error: {error_data.get('error', 'Unknown error')}")
            except:
                print(f"Response: {response.text}")
                
    except requests.exceptions.ConnectionError:
        print("❌ Test FAILED - Could not connect to API")
        print("Make sure the API is running locally: python main.py")
    except Exception as e:
        print(f"❌ Test FAILED - Unexpected error: {e}")

def test_validation():
    """Test validation of new priority values"""
    
    print("\n🔍 Testing Input Validation")
    print("=" * 30)
    
    # Test invalid priority level
    invalid_priority_data = {
        "addresses": ["Start", "Customer", "End"],
        "priority_addresses": [
            {
                "address": "Customer",
                "priority_level": "extreme",  # Invalid value
                "preferred_time_window": "early"
            }
        ]
    }
    
    try:
        response = requests.post(API_URL, json=invalid_priority_data, headers={'Content-Type': 'application/json'})
        
        if response.status_code == 400:
            error_data = response.json()
            print("✅ Validation PASSED - Invalid priority level rejected")
            print(f"   Error message: {error_data.get('error', 'No error message')}")
        else:
            print(f"⚠️ Validation test unexpected result: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Validation test failed: {e}")

def test_backwards_compatibility():
    """Test that old priority values still work"""
    
    print("\n🔄 Testing Backwards Compatibility")
    print("=" * 35)
    
    old_format_data = {
        "addresses": [
            "Berlin, Germany",
            "Munich, Germany", 
            "Hamburg, Germany"
        ],
        "priority_addresses": [
            {
                "address": "Munich, Germany",
                "priority_level": "high",      # Old format
                "preferred_time_window": "early"  # Old format
            }
        ]
    }
    
    try:
        response = requests.post(API_URL, json=old_format_data, headers={'Content-Type': 'application/json'})
        
        if response.status_code == 200:
            print("✅ Backwards compatibility PASSED - Old format still works")
        else:
            print(f"❌ Backwards compatibility FAILED - {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error: {error_data.get('error', 'Unknown error')}")
            except:
                pass
                
    except Exception as e:
        print(f"❌ Backwards compatibility test failed: {e}")

if __name__ == "__main__":
    print("🚀 Extended Priority System Test Suite")
    print("=" * 60)
    
    test_extended_priorities()
    test_validation()
    test_backwards_compatibility()
    
    print("\n" + "=" * 60)
    print("🏁 Test suite completed!")
    print("\nNote: Make sure the API server is running locally:")
    print("  python main.py")