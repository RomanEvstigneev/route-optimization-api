#!/usr/bin/env python3
"""
Test script for hard time windows functionality
"""

import requests
import json
from datetime import datetime, timedelta
import pytz

# Configuration
API_URL = "https://items-routes-route-optimisation-dot-maibach-items-routes.ew.r.appspot.com/api/optimize"

def test_hard_time_windows():
    """Test hard time windows"""
    print("🔍 Debug Test - Hard Time Windows Functionality")
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
    
    # Create hard time window
    berlin_tz = pytz.timezone('Europe/Berlin')
    now = datetime.now(berlin_tz)
    start_time = now.replace(hour=23, minute=0, second=0, microsecond=0)
    
    # Create hard time window for priority address
    priority_start = start_time + timedelta(minutes=30)  # 23:30
    priority_end = start_time + timedelta(hours=2)       # 01:00
    
    request_data = {
        "addresses": addresses,
        "time_windows": {
            "enabled": True,
            "windows": [
                {
                    "address_index": priority_index,
                    "hard_start_time": priority_start.isoformat(),
                    "hard_end_time": priority_end.isoformat()
                }
            ]
        }
    }
    
    print(f"\n⏰ Hard Time Window Configuration:")
    print(f"   Start time: {start_time.strftime('%H:%M %Z')}")
    print(f"   Priority window: {priority_start.strftime('%H:%M')} - {priority_end.strftime('%H:%M')}")
    print(f"   Address index: {priority_index}")
    print(f"   Type: Hard time window (strict)")
    
    print(f"\n📤 Request payload:")
    print(json.dumps(request_data, indent=2, ensure_ascii=False))
    
    try:
        print(f"\n🔄 Sending request to: {API_URL}")
        response = requests.post(API_URL, json=request_data, timeout=90)
        
        print(f"📥 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('success'):
                print(f"✅ Route optimization successful with hard time windows!")
                
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
                        print(f"      Within hard window: {'✅ YES' if within_window else '❌ NO'}")
                
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
    test_hard_time_windows() 