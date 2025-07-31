#\!/usr/bin/env python3
"""
Test the specific scenario reported in the issue where priorities are ignored
"""

import requests
import json

# API Configuration  
PROD_API_URL = "https://items-routes-route-optimisation-dot-maibach-items-routes.ew.r.appspot.com/api/optimize"

def test_reported_issue():
    """Test the exact scenario from the issue report"""
    
    # Exact data from the issue report
    test_data = {
        "addresses": [
            "Neumarkter str. 39, 90584 Allersberg",
            "Neumarkter Strasse 39, 90584 Allersberg",
            "Am Festplatz 2/4, 90562 Heroldsberg",
            "Beuthener Straße 3, 91315 Höchstadt a.d.Aisch",
            "Brandstätterstrasse 17 b, 90556 Cadolzburg",
            "Johann-Zumpe-Strasse 6, 90763 Fürth",
            "Gaussstraße 33, 90766 Fürth"
        ],
        "start_time": "2025-07-31T19:00:00.000Z",
        "objective": "minimize_time",
        "priority_addresses": [
            {
                "address": "Johann-Zumpe-Strasse 6, 90763 Fürth",
                "priority_level": "critical_high",
                "preferred_time_window": "earliest"
            }
        ]
    }
    
    print("🧪 TESTING REPORTED ISSUE")
    print("=" * 50)
    
    print(f"📤 Sending request with {len(test_data['addresses'])} addresses")
    print(f"🎯 Priority address: {test_data['priority_addresses'][0]['address']}")
    print(f"📊 Priority level: {test_data['priority_addresses'][0]['priority_level']}")
    print(f"⏰ Time window: {test_data['priority_addresses'][0]['preferred_time_window']}")
    print(f"🚀 Start time: {test_data['start_time']}")
    print(f"🎯 Objective: {test_data['objective']}")
    
    # Find original position of priority address
    priority_address = test_data['priority_addresses'][0]['address']
    original_position = None
    for i, addr in enumerate(test_data['addresses']):
        if priority_address == addr:
            original_position = i + 1
            break
    
    print(f"📍 Original priority address position: {original_position}/{len(test_data['addresses'])}")
    
    try:
        response = requests.post(
            PROD_API_URL,
            headers={'Content-Type': 'application/json'},
            json=test_data,
            timeout=90
        )
        
        print(f"\n📥 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            analyze_specific_results(result, test_data, original_position)
            return True
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Error text: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Request failed: {str(e)}")
        return False


def analyze_specific_results(result, original_data, original_position):
    """Analyze the specific issue results"""
    
    print(f"\n🎉 SUCCESS\! Route optimization completed")
    print("=" * 50)
    
    # Show route indices
    route_indices = result.get('route_indices', [])
    print(f"🔢 Route indices: {route_indices}")
    
    # Check if it's the same order (the reported issue)
    expected_unchanged = list(range(len(original_data['addresses'])))
    if route_indices == expected_unchanged:
        print(f"⚠️  ISSUE CONFIRMED: Route indices show NO reordering occurred\!")
        print(f"   Expected: {expected_unchanged}")
        print(f"   Actual:   {route_indices}")
    else:
        print(f"✅ Route reordering DID occur")
        print(f"   Original order: {expected_unchanged}")
        print(f"   Optimized:      {route_indices}")
    
    # Find priority address position in optimized route
    priority_address = original_data['priority_addresses'][0]['address']
    optimized_addresses = result.get('optimized_addresses', [])
    
    optimized_position = None
    for i, addr in enumerate(optimized_addresses):
        if priority_address == addr:
            optimized_position = i + 1
            break
    
    print(f"\n🎯 PRIORITY ADDRESS MOVEMENT:")
    print(f"📍 Priority address: {priority_address}")
    print(f"🔢 Original position: {original_position}/{len(original_data['addresses'])}")
    print(f"🚀 Optimized position: {optimized_position}/{len(optimized_addresses)}")
    
    if optimized_position and original_position:
        if optimized_position < original_position:
            improvement = original_position - optimized_position
            print(f"📈 SUCCESS: Moved {improvement} positions EARLIER\! 🎉")
        elif optimized_position > original_position:
            decline = optimized_position - original_position  
            print(f"📉 ISSUE: Moved {decline} positions LATER")
        else:
            print(f"➡️  ISSUE: Position UNCHANGED (priority ignored)")
    
    # Show the full optimized route
    print(f"\n🗺️  OPTIMIZED ROUTE ORDER:")
    print("=" * 25)
    for i, address in enumerate(optimized_addresses, 1):
        is_priority = priority_address == address
        marker = "🎯 CRITICAL_HIGH" if is_priority else "📍"
        print(f"{i}. {marker} {address}")
    
    # Show timing details if available
    timing_info = result.get('timing_info', {})
    if timing_info:
        print(f"\n⏱️  TIMING INFO:")
        print(f"🚀 Start: {timing_info.get('vehicle_start_time', 'N/A')}")
        print(f"🏁 End: {timing_info.get('vehicle_end_time', 'N/A')}")
        print(f"⏱️  Duration: {timing_info.get('total_duration_minutes', 0)} minutes")


if __name__ == "__main__":
    success = test_reported_issue()
    success_msg = "🎉 TEST COMPLETED\!" if success else "❌ TEST FAILED\!"
    print(f"\n{success_msg}")
