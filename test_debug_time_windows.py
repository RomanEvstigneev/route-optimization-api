#!/usr/bin/env python3
"""
Debug test for time windows functionality
"""

import requests
import json
from datetime import datetime, timedelta
import pytz

# Configuration
API_URL = "https://items-routes-route-optimisation-dot-maibach-items-routes.ew.r.appspot.com/api/optimize"

def test_debug_time_windows():
    """Debug test for time windows"""
    print("🔍 Debug Test - Time Windows Functionality")
    print("=" * 60)
    
    # Load addresses from route_optimizer_test.json
    with open('route_optimizer_test.json', 'r', encoding='utf-8') as f:
        test_data = json.load(f)
        addresses = test_data['addresses']
    
    print(f"📋 Loaded {len(addresses)} addresses:")
    for i, addr in enumerate(addresses):
        print(f"   {i}: {addr}")
    
    priority_address = "Lippacher Str. 1, 84095 Furth, Deutschland"
    priority_index = addresses.index(priority_address)
    print(f"\n🎯 Priority address: {priority_address}")
    print(f"   Original array index: {priority_index}")
    
    # Very wide and gentle time window
    berlin_tz = pytz.timezone('Europe/Berlin')
    now = datetime.now(berlin_tz)
    start_time = now.replace(hour=23, minute=0, second=0, microsecond=0)
    
    # Create very wide time window
    priority_start = start_time + timedelta(minutes=10)  # 23:10
    priority_end = start_time + timedelta(hours=4)       # 03:00
    
    request_data = {
        "addresses": addresses,
        "time_windows": {
            "enabled": True,
            "windows": [
                {
                    "address_index": priority_index,  # Use original array index
                    "soft_start_time": priority_start.isoformat(),
                    "soft_end_time": priority_end.isoformat(),
                    "cost_per_hour_before": 1.0,   # Very low penalty
                    "cost_per_hour_after": 2.0     # Very low penalty
                }
            ]
        }
    }
    
    print(f"\n⏰ Time Window Configuration:")
    print(f"   Start time: {start_time.strftime('%H:%M %Z')}")
    print(f"   Priority window: {priority_start.strftime('%H:%M')} - {priority_end.strftime('%H:%M')}")
    print(f"   Address index: {priority_index}")
    print(f"   Penalties: 1.0 (before) / 2.0 (after) per hour")
    
    print(f"\n📤 Request payload:")
    print(json.dumps(request_data, indent=2, ensure_ascii=False))
    
    try:
        print(f"\n🔄 Sending request to: {API_URL}")
        response = requests.post(API_URL, json=request_data, timeout=90)
        
        print(f"📥 Response status: {response.status_code}")
        print(f"📥 Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success! Result keys: {list(result.keys())}")
            
            if result.get('success'):
                print(f"✅ Route optimization successful!")
                
                # Check priority address
                visit_schedule = result['visit_schedule']
                customer_visits = [v for v in visit_schedule if not v['is_depot']]
                
                print(f"\n🎯 Priority Address Analysis:")
                for i, visit in enumerate(customer_visits):
                    marker = "🎯" if priority_address in visit['address'] else "📍"
                    arrival = datetime.fromisoformat(visit['arrival_time'].replace('Z', '+00:00'))
                    position = i + 1
                    
                    print(f"   {marker} {position}. {visit['address'][:50]}...")
                    print(f"      Arrival: {arrival.strftime('%H:%M')}")
                    if marker == "🎯":
                        within_window = priority_start <= arrival <= priority_end
                        print(f"      Within window: {'✅ YES' if within_window else '❌ NO'}")
                
            else:
                print(f"❌ Optimization failed: {result.get('error', 'Unknown error')}")
                
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response content: {response.text}")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_debug_time_windows() 