#!/usr/bin/env python3
"""
Test Priority Address Request
Based on the screenshot data with German addresses
"""

import requests
import json
from datetime import datetime

# API Configuration
LOCAL_API_URL = "http://localhost:8080/api/optimize"
PROD_API_URL = "https://items-routes-route-optimisation-dot-maibach-items-routes.ew.r.appspot.com/api/optimize"

def test_priority_request():
    """Test the priority address request from screenshot"""
    
    # Data from screenshot
    test_data = {
        "addresses": [
            "Neumarkter str. 39, 90584 Allersberg",
            "Kugelpoint 1, 83629 Weyarn",
            "Pichlmayrstraße 21 a, 83024 Rosenheim",
            "Innsbrucker Ring 153, 81669 München",
            "Amtmannsdorf 31, 92339 Beilngries",
            "Horneckerweg 28, 90408 Nürnberg",
            "Erlenstraße 3, 90441 Nürnberg"
        ],
        "start_time": "2025-07-21T13:56:00.000Z",
        "priority_addresses": [
            {
                "address": "Horneckerweg 28, 90408 Nürnberg",
                "priority_level": "high",
                "preferred_time_window": "early"
            }
        ]
    }
    
    print("🧪 TESTING PRIORITY ADDRESS REQUEST")
    print("=" * 50)
    
    print(f"📤 Sending request with {len(test_data['addresses'])} addresses")
    print(f"🎯 Priority address: {test_data['priority_addresses'][0]['address']}")
    print(f"📊 Priority level: {test_data['priority_addresses'][0]['priority_level']}")
    print(f"⏰ Time window: {test_data['priority_addresses'][0]['preferred_time_window']}")
    print(f"🚀 Start time: {test_data['start_time']}")
    
    print(f"\n📋 Full request data:")
    print(json.dumps(test_data, indent=2, ensure_ascii=False))
    
    # Try production API first
    print(f"\n🔄 Sending request to Production API...")
    print(f"URL: {PROD_API_URL}")
    
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
            analyze_priority_results(result, test_data)
            return True
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Error text: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False


def analyze_priority_results(result, original_data):
    """Analyze if priority address was properly prioritized"""
    
    print(f"\n🎉 SUCCESS! Route optimization completed")
    print("=" * 50)
    
    # Basic info
    print(f"✅ Success: {result.get('success', False)}")
    print(f"🗺️  Algorithm: {result.get('algorithm', 'N/A')}")
    print(f"🎯 Objective: {result.get('optimization_objective', 'N/A')}")
    
    # Timing info
    timing_info = result.get('timing_info', {})
    print(f"⏱️  Total time: {timing_info.get('total_duration_minutes', 0)} minutes")
    print(f"🚀 Vehicle start: {timing_info.get('vehicle_start_time', 'N/A')}")
    print(f"🏁 Vehicle end: {timing_info.get('vehicle_end_time', 'N/A')}")
    
    # Distance info
    opt_info = result.get('optimization_info', {})
    print(f"📏 Total distance: {opt_info.get('total_distance_km', 0)} km")
    print(f"🕐 Service time per stop: {timing_info.get('service_time_per_stop_minutes', 3)} minutes")
    
    # Priority analysis
    priority_address = original_data['priority_addresses'][0]['address']
    original_addresses = result.get('original_addresses', [])
    optimized_addresses = result.get('optimized_addresses', [])
    
    print(f"\n🎯 PRIORITY ADDRESS ANALYSIS")
    print("=" * 30)
    
    # Find positions
    original_pos = None
    optimized_pos = None
    
    for i, addr in enumerate(original_addresses):
        if priority_address in addr:
            original_pos = i + 1
            break
    
    for i, addr in enumerate(optimized_addresses):
        if priority_address in addr:
            optimized_pos = i + 1
            break
    
    if original_pos and optimized_pos:
        print(f"📍 Priority address: {priority_address}")
        print(f"🔢 Original position: {original_pos}/{len(original_addresses)}")
        print(f"🚀 Optimized position: {optimized_pos}/{len(optimized_addresses)}")
        
        # Check if it moved earlier
        total_customers = len(optimized_addresses) - 2  # Exclude start/end
        customer_position = optimized_pos - 1  # Adjust for start point
        first_half_threshold = total_customers // 2
        
        if customer_position <= first_half_threshold:
            print(f"✅ SUCCESS: Priority address is in FIRST HALF of route!")
            print(f"   Position {customer_position}/{total_customers} customers")
        else:
            print(f"⚠️  WARNING: Priority address is in second half")
            print(f"   Position {customer_position}/{total_customers} customers")
        
        # Position improvement
        if original_pos and optimized_pos < original_pos:
            improvement = original_pos - optimized_pos
            print(f"📈 IMPROVEMENT: Moved {improvement} positions EARLIER! 🎉")
        elif optimized_pos > original_pos:
            print(f"📉 Moved {optimized_pos - original_pos} positions later")
        else:
            print(f"➡️  Position unchanged")
    
    # Show optimized route
    print(f"\n🗺️  OPTIMIZED ROUTE ORDER:")
    print("=" * 25)
    for i, address in enumerate(optimized_addresses, 1):
        is_priority = priority_address in address
        marker = "🎯 HIGH PRIORITY" if is_priority else "📍"
        print(f"{i}. {marker} {address}")
    
    # Show visit schedule if available
    visit_schedule = result.get('visit_schedule', [])
    if visit_schedule:
        print(f"\n📅 VISIT SCHEDULE (First 5 stops):")
        print("=" * 30)
        for i, visit in enumerate(visit_schedule[:5]):
            arrival_time = visit.get('arrival_time', 'TBD')
            if arrival_time != 'TBD':
                time_only = arrival_time.split('T')[1][:5]
            else:
                time_only = 'TBD'
            
            address = visit.get('address', '').split(',')[0]  # Short name
            stop_type = visit.get('stop_type', 'Visit')
            service_time = visit.get('service_duration_minutes', 0)
            
            is_priority = priority_address.split(',')[0] in address
            marker = "🎯" if is_priority else "📍"
            
            print(f"  {marker} {time_only} - {address} ({stop_type}, {service_time}min)")


if __name__ == "__main__":
    success = test_priority_request()
    print(f"\n{'🎉 TEST PASSED!' if success else '❌ TEST FAILED!'}") 