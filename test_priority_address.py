#!/usr/bin/env python3
"""
Test script for Route Optimization API - Priority Address Feature
Tests prioritizing a specific address using soft time windows.
"""

import requests
import json
from datetime import datetime, timedelta
import pytz

# Configuration
API_URL = "https://items-routes-route-optimisation-dot-maibach-items-routes.ew.r.appspot.com/api/optimize"  # Production

def test_priority_address():
    """Test prioritizing a specific address using soft time windows"""
    print("🚚 Testing Route Optimization API - Priority Address Feature")
    print("=" * 70)
    
    # Load addresses from route_optimizer_test.json
    try:
        with open('route_optimizer_test.json', 'r', encoding='utf-8') as f:
            test_data = json.load(f)
            addresses = test_data['addresses']
    except FileNotFoundError:
        print("❌ route_optimizer_test.json not found")
        return
    
    # Find the priority address index
    priority_address = "Lippacher Str. 1, 84095 Furth, Deutschland"
    try:
        priority_index = addresses.index(priority_address)
        print(f"🎯 Priority address found at index {priority_index}: {priority_address}")
    except ValueError:
        print(f"❌ Priority address not found: {priority_address}")
        return
    
    # Setup time windows to prioritize the address in first half of route
    # Start at 23:00, give priority window from 23:30 to 01:00
    berlin_tz = pytz.timezone('Europe/Berlin')
    start_time = datetime.now(berlin_tz).replace(hour=23, minute=0, second=0, microsecond=0)
    
    # Create soft time window for priority address (first half of route)
    priority_start = start_time + timedelta(minutes=30)  # 23:30
    priority_end = start_time + timedelta(hours=2)       # 01:00
    
    request_data = {
        "addresses": addresses,
        "time_windows": {
            "enabled": True,
            "windows": [
                {
                    "address_index": priority_index,
                    "soft_start_time": priority_start.isoformat(),
                    "soft_end_time": priority_end.isoformat(),
                    "cost_per_hour_before": 50.0,  # High cost for visiting before 23:30
                    "cost_per_hour_after": 100.0   # Very high cost for visiting after 01:00
                }
            ]
        }
    }
    
    print(f"\n📋 Test Configuration:")
    print(f"   Start time: {start_time.strftime('%H:%M %Z')}")
    print(f"   Priority address: {priority_address}")
    print(f"   Priority window: {priority_start.strftime('%H:%M')} - {priority_end.strftime('%H:%M')}")
    print(f"   Total addresses: {len(addresses)}")
    
    print(f"\n🔍 Request payload:")
    print(json.dumps(request_data, indent=2, ensure_ascii=False))
    
    try:
        print(f"\n📤 Sending request to: {API_URL}")
        response = requests.post(API_URL, json=request_data, timeout=60)
        
        print(f"📥 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('success'):
                print(f"\n✅ Route optimization successful!")
                print(f"   Algorithm: {result.get('algorithm', 'N/A')}")
                print(f"   Total duration: {result['timing_info']['total_duration_hours']} hours")
                
                # Check if priority address is in first half
                visit_schedule = result['visit_schedule']
                depot_visits = [v for v in visit_schedule if v['is_depot']]
                customer_visits = [v for v in visit_schedule if not v['is_depot']]
                
                total_customers = len(customer_visits)
                first_half_size = total_customers // 2
                
                print(f"\n🎯 Priority Address Analysis:")
                print(f"   Total customer visits: {total_customers}")
                print(f"   First half size: {first_half_size}")
                
                # Find priority address in schedule
                priority_visit = None
                for visit in customer_visits:
                    if priority_address in visit['address']:
                        priority_visit = visit
                        break
                
                if priority_visit:
                    visit_position = customer_visits.index(priority_visit) + 1
                    is_in_first_half = visit_position <= first_half_size
                    
                    print(f"   Priority address position: {visit_position} of {total_customers}")
                    print(f"   In first half: {'✅ YES' if is_in_first_half else '❌ NO'}")
                    print(f"   Arrival time: {priority_visit['arrival_time']}")
                    print(f"   Coordinates: {priority_visit['latitude']}, {priority_visit['longitude']}")
                else:
                    print(f"   ❌ Priority address not found in schedule")
                
                # Display detailed schedule
                print(f"\n📅 Detailed Visit Schedule:")
                for i, visit in enumerate(visit_schedule):
                    arrival = datetime.fromisoformat(visit['arrival_time'].replace('Z', '+00:00'))
                    marker = "🎯" if priority_address in visit['address'] else "📍"
                    depot_marker = "🏠" if visit['is_depot'] else ""
                    
                    print(f"   {marker}{depot_marker} {visit['stop_number']}. {visit['address'][:50]}...")
                    print(f"      Arrival: {arrival.strftime('%H:%M')} | Service: {visit['service_duration_minutes']}min")
                    
                    if not visit['is_depot']:
                        customer_position = len([v for v in visit_schedule[:i+1] if not v['is_depot']])
                        half_marker = "🟢" if customer_position <= first_half_size else "🔴"
                        print(f"      Position: {customer_position}/{total_customers} {half_marker}")
                
                # Display optimization summary
                print(f"\n📊 Optimization Summary:")
                print(f"   Original order: {[addr[:30] + '...' for addr in addresses]}")
                print(f"   Optimized order: {[addr[:30] + '...' for addr in result['optimized_addresses']]}")
                
            else:
                print(f"❌ Optimization failed: {result.get('error', 'Unknown error')}")
                
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error details: {error_data}")
            except:
                print(f"   Error text: {response.text}")
                
    except requests.exceptions.Timeout:
        print("❌ Request timeout - optimization took too long")
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    test_priority_address() 