#!/usr/bin/env python3
"""
Test priority address integration with main API
Tests the new priority_addresses functionality
"""

import requests
import json
from datetime import datetime

# API Configuration
API_URL = "https://items-routes-route-optimisation-dot-maibach-items-routes.ew.r.appspot.com/api/optimize"
# For local testing: API_URL = "http://localhost:8080/api/optimize"

def test_priority_address_integration():
    """
    Test the priority address functionality with the main API
    """
    print("🧪 Testing Priority Address Integration")
    print("=" * 50)
    
    # Test data with our specific priority address
    test_data = {
        "addresses": [
            "Neumarkter Str. 39, 90584 Allersberg, Deutschland",  # Start point
            "Kolpingstraße 2, 90584 Allersberg, Deutschland",     # Customer 1
            "Dietkirchen 13, 92367 Pilsach, Deutschland",         # Customer 2
            "Am Klosterberg, 84095 Furth, Deutschland",           # Customer 3
            "Harrhof 7, 90584 Allersberg, Deutschland",           # Customer 4
            "Guggenmühle 15, 90584 Allersberg, Deutschland",      # Customer 5
            "Lippacher Str. 1, 84095 Furth, Deutschland",         # Customer 6 (PRIORITY!)
            "Seelstraße 20, 92318 Neumarkt in der Oberpfalz, Deutschland",  # Customer 7
            "Neumarkter Str. 39, 90584 Allersberg, Deutschland"   # End point
        ],
        "priority_addresses": [
            {
                "address": "Lippacher Str. 1, 84095 Furth, Deutschland",
                "priority_level": "high",
                "preferred_time_window": "early"
            }
        ]
    }
    
    print(f"📤 Testing with {len(test_data['addresses'])} addresses")
    print(f"🎯 Priority address: {test_data['priority_addresses'][0]['address']}")
    print(f"📊 Priority level: {test_data['priority_addresses'][0]['priority_level']}")
    print(f"⏰ Preferred time window: {test_data['priority_addresses'][0]['preferred_time_window']}")
    
    # Make API request
    try:
        response = requests.post(
            API_URL,
            headers={'Content-Type': 'application/json'},
            json=test_data,
            timeout=30
        )
        
        print(f"\n📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            analyze_priority_results(result, test_data)
            return True
        else:
            error_data = response.json()
            print(f"❌ Error: {error_data.get('error', 'Unknown error')}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {str(e)}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False


def analyze_priority_results(result, test_data):
    """
    Analyze the results to see if priority address was prioritized
    """
    print("\n🔍 ANALYZING PRIORITY RESULTS")
    print("=" * 50)
    
    # Extract data
    original_addresses = result.get('original_addresses', [])
    optimized_addresses = result.get('optimized_addresses', [])
    route_indices = result.get('route_indices', [])
    visit_schedule = result.get('visit_schedule', [])
    
    priority_address = test_data['priority_addresses'][0]['address']
    
    print(f"✅ Success: {result.get('success', False)}")
    print(f"🗺️  Original addresses: {len(original_addresses)}")
    print(f"🚀 Optimized addresses: {len(optimized_addresses)}")
    
    # Find the position of priority address in the optimized route
    priority_position = None
    for i, addr in enumerate(optimized_addresses):
        if addr == priority_address:
            priority_position = i
            break
    
    if priority_position is not None:
        total_stops = len(optimized_addresses) - 2  # Exclude start and end points
        priority_position_adjusted = priority_position - 1  # Adjust for start point
        
        print(f"\n🎯 PRIORITY ADDRESS ANALYSIS:")
        print(f"   Address: {priority_address}")
        print(f"   Position in route: {priority_position} of {len(optimized_addresses)}")
        print(f"   Position among customers: {priority_position_adjusted} of {total_stops}")
        
        # Check if it's in the first half
        first_half_threshold = total_stops // 2
        is_in_first_half = priority_position_adjusted <= first_half_threshold
        
        print(f"   First half threshold: {first_half_threshold}")
        print(f"   Is in first half: {'✅ YES' if is_in_first_half else '❌ NO'}")
        
        if is_in_first_half:
            print(f"   🎉 SUCCESS: Priority address is in the first half of the route!")
        else:
            print(f"   ⚠️  WARNING: Priority address is NOT in the first half of the route")
    else:
        print(f"❌ Priority address not found in optimized route!")
    
    # Show the full route
    print(f"\n🗺️  FULL OPTIMIZED ROUTE:")
    for i, addr in enumerate(optimized_addresses, 1):
        is_priority = addr == priority_address
        marker = "🎯" if is_priority else "📍"
        print(f"   {i}. {marker} {addr}")
    
    # Show timing information
    if visit_schedule:
        print(f"\n⏰ TIMING ANALYSIS:")
        for stop in visit_schedule:
            if stop['address'] == priority_address:
                print(f"   🎯 Priority address timing:")
                print(f"      Arrival: {stop.get('arrival_time', 'N/A')}")
                print(f"      Service duration: {stop.get('service_duration_minutes', 'N/A')} minutes")
                print(f"      Stop type: {stop.get('stop_type', 'N/A')}")
                break
    
    # Show route indices
    print(f"\n🔢 Route indices: {route_indices}")
    
    # Show timing info
    if 'timing_info' in result:
        timing = result['timing_info']
        print(f"\n⏱️  TIMING INFO:")
        print(f"   Total duration: {timing.get('total_duration_minutes', 'N/A')} minutes")
        print(f"   Vehicle start: {timing.get('vehicle_start_time', 'N/A')}")
        print(f"   Vehicle end: {timing.get('vehicle_end_time', 'N/A')}")


def test_without_priority():
    """
    Test the same addresses without priority to compare results
    """
    print("\n🧪 Testing WITHOUT Priority (Comparison)")
    print("=" * 50)
    
    # Same addresses but without priority configuration
    test_data = {
        "addresses": [
            "Neumarkter Str. 39, 90584 Allersberg, Deutschland",  # Start point
            "Kolpingstraße 2, 90584 Allersberg, Deutschland",     # Customer 1
            "Dietkirchen 13, 92367 Pilsach, Deutschland",         # Customer 2
            "Am Klosterberg, 84095 Furth, Deutschland",           # Customer 3
            "Harrhof 7, 90584 Allersberg, Deutschland",           # Customer 4
            "Guggenmühle 15, 90584 Allersberg, Deutschland",      # Customer 5
            "Lippacher Str. 1, 84095 Furth, Deutschland",         # Customer 6 (NO priority)
            "Seelstraße 20, 92318 Neumarkt in der Oberpfalz, Deutschland",  # Customer 7
            "Neumarkter Str. 39, 90584 Allersberg, Deutschland"   # End point
        ]
    }
    
    print(f"📤 Testing same addresses WITHOUT priority")
    
    try:
        response = requests.post(
            API_URL,
            headers={'Content-Type': 'application/json'},
            json=test_data,
            timeout=30
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            # Find position of the same address
            target_address = "Lippacher Str. 1, 84095 Furth, Deutschland"
            optimized_addresses = result.get('optimized_addresses', [])
            
            position = None
            for i, addr in enumerate(optimized_addresses):
                if addr == target_address:
                    position = i
                    break
            
            if position is not None:
                total_stops = len(optimized_addresses) - 2
                position_adjusted = position - 1
                
                print(f"📍 WITHOUT priority:")
                print(f"   Position in route: {position} of {len(optimized_addresses)}")
                print(f"   Position among customers: {position_adjusted} of {total_stops}")
                
                first_half_threshold = total_stops // 2
                is_in_first_half = position_adjusted <= first_half_threshold
                print(f"   Is in first half: {'✅ YES' if is_in_first_half else '❌ NO'}")
            
            return True
        else:
            error_data = response.json()
            print(f"❌ Error: {error_data.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def test_multiple_priority_addresses():
    """
    Test with multiple priority addresses
    """
    print("\n🧪 Testing Multiple Priority Addresses")
    print("=" * 50)
    
    test_data = {
        "addresses": [
            "Berlin Hauptbahnhof, Berlin, Germany",      # Start point
            "Potsdamer Platz, Berlin, Germany",          # Customer 1
            "Brandenburg Gate, Berlin, Germany",         # Customer 2
            "Alexanderplatz, Berlin, Germany",           # Customer 3
            "Checkpoint Charlie, Berlin, Germany",       # Customer 4
            "Berlin TV Tower, Berlin, Germany",          # Customer 5
            "Berlin Hauptbahnhof, Berlin, Germany"       # End point
        ],
        "priority_addresses": [
            {
                "address": "Brandenburg Gate, Berlin, Germany",
                "priority_level": "high",
                "preferred_time_window": "early"
            },
            {
                "address": "Berlin TV Tower, Berlin, Germany",
                "priority_level": "medium",
                "preferred_time_window": "early"
            }
        ]
    }
    
    print(f"📤 Testing with {len(test_data['priority_addresses'])} priority addresses")
    for i, priority in enumerate(test_data['priority_addresses'], 1):
        print(f"   {i}. {priority['address']} (level: {priority['priority_level']})")
    
    try:
        response = requests.post(
            API_URL,
            headers={'Content-Type': 'application/json'},
            json=test_data,
            timeout=30
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            optimized_addresses = result.get('optimized_addresses', [])
            
            print(f"🗺️  Optimized route:")
            for i, addr in enumerate(optimized_addresses, 1):
                is_priority = any(p['address'] == addr for p in test_data['priority_addresses'])
                marker = "🎯" if is_priority else "📍"
                print(f"   {i}. {marker} {addr}")
            
            return True
        else:
            error_data = response.json()
            print(f"❌ Error: {error_data.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def main():
    """
    Main test function
    """
    print("🚀 Testing Priority Address Integration")
    print("=" * 60)
    
    # Run tests
    results = []
    
    # Test 1: With priority
    results.append(test_priority_address_integration())
    
    # Test 2: Without priority (comparison)
    results.append(test_without_priority())
    
    # Test 3: Multiple priority addresses
    results.append(test_multiple_priority_addresses())
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"✅ Tests passed: {passed}/{total}")
    print(f"❌ Tests failed: {total - passed}/{total}")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Priority address integration is working!")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")


if __name__ == "__main__":
    main() 