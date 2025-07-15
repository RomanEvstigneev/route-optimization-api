#!/usr/bin/env python3
"""
Test script for Route Optimization API - Simple Priority Test
Tests both without time windows and with gentle time windows.
"""

import requests
import json
from datetime import datetime, timedelta
import pytz

# Configuration
API_URL = "https://items-routes-route-optimisation-dot-maibach-items-routes.ew.r.appspot.com/api/optimize"

def test_without_time_windows():
    """Test basic route optimization without time windows"""
    print("🚚 Testing Route Optimization API - Basic Test (No Time Windows)")
    print("=" * 70)
    
    # Load addresses from route_optimizer_test.json
    try:
        with open('route_optimizer_test.json', 'r', encoding='utf-8') as f:
            test_data = json.load(f)
            addresses = test_data['addresses']
    except FileNotFoundError:
        print("❌ route_optimizer_test.json not found")
        return None
    
    priority_address = "Lippacher Str. 1, 84095 Furth, Deutschland"
    
    request_data = {
        "addresses": addresses
    }
    
    print(f"📋 Test Configuration:")
    print(f"   Priority address: {priority_address}")
    print(f"   Total addresses: {len(addresses)}")
    print(f"   Mode: Basic optimization (no time windows)")
    
    try:
        print(f"\n📤 Sending request to API...")
        response = requests.post(API_URL, json=request_data, timeout=60)
        
        print(f"📥 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('success'):
                print(f"\n✅ Route optimization successful!")
                print(f"   Algorithm: {result.get('algorithm', 'N/A')}")
                print(f"   Total duration: {result['timing_info']['total_duration_hours']} hours")
                
                # Check priority address position
                visit_schedule = result['visit_schedule']
                customer_visits = [v for v in visit_schedule if not v['is_depot']]
                
                total_customers = len(customer_visits)
                first_half_size = total_customers // 2
                
                print(f"\n🎯 Priority Address Analysis (without time windows):")
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
                
                # Display brief schedule
                print(f"\n📅 Brief Schedule:")
                for i, visit in enumerate(customer_visits):
                    arrival = datetime.fromisoformat(visit['arrival_time'].replace('Z', '+00:00'))
                    marker = "🎯" if priority_address in visit['address'] else "📍"
                    position = i + 1
                    half_marker = "🟢" if position <= first_half_size else "🔴"
                    
                    print(f"   {marker} {position}/{total_customers} {half_marker} {visit['address'][:40]}... - {arrival.strftime('%H:%M')}")
                
                return result
                
            else:
                print(f"❌ Optimization failed: {result.get('error', 'Unknown error')}")
                return None
                
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error details: {error_data}")
            except:
                print(f"   Error text: {response.text}")
            return None
                
    except requests.exceptions.Timeout:
        print("❌ Request timeout - optimization took too long")
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None

def test_with_gentle_time_windows():
    """Test with very gentle time windows"""
    print("\n\n🚚 Testing Route Optimization API - Gentle Time Windows")
    print("=" * 70)
    
    # Load addresses from route_optimizer_test.json
    try:
        with open('route_optimizer_test.json', 'r', encoding='utf-8') as f:
            test_data = json.load(f)
            addresses = test_data['addresses']
    except FileNotFoundError:
        print("❌ route_optimizer_test.json not found")
        return None
    
    priority_address = "Lippacher Str. 1, 84095 Furth, Deutschland"
    try:
        priority_index = addresses.index(priority_address)
    except ValueError:
        print(f"❌ Priority address not found: {priority_address}")
        return None
    
    # Very gentle time windows - wide window, low penalties
    berlin_tz = pytz.timezone('Europe/Berlin')
    start_time = datetime.now(berlin_tz).replace(hour=23, minute=0, second=0, microsecond=0)
    
    # Create wide soft time window for priority address
    priority_start = start_time + timedelta(minutes=15)  # 23:15 - very early
    priority_end = start_time + timedelta(hours=3)       # 02:00 - wide window
    
    request_data = {
        "addresses": addresses,
        "time_windows": {
            "enabled": True,
            "windows": [
                {
                    "address_index": priority_index,
                    "soft_start_time": priority_start.isoformat(),
                    "soft_end_time": priority_end.isoformat(),
                    "cost_per_hour_before": 5.0,   # Very low penalty
                    "cost_per_hour_after": 10.0    # Low penalty
                }
            ]
        }
    }
    
    print(f"📋 Test Configuration:")
    print(f"   Priority address: {priority_address}")
    print(f"   Priority window: {priority_start.strftime('%H:%M')} - {priority_end.strftime('%H:%M')}")
    print(f"   Penalties: 5.0 (before) / 10.0 (after) per hour")
    print(f"   Total addresses: {len(addresses)}")
    
    try:
        print(f"\n📤 Sending request to API...")
        response = requests.post(API_URL, json=request_data, timeout=60)
        
        print(f"📥 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('success'):
                print(f"\n✅ Route optimization successful!")
                print(f"   Algorithm: {result.get('algorithm', 'N/A')}")
                print(f"   Total duration: {result['timing_info']['total_duration_hours']} hours")
                
                # Check priority address position
                visit_schedule = result['visit_schedule']
                customer_visits = [v for v in visit_schedule if not v['is_depot']]
                
                total_customers = len(customer_visits)
                first_half_size = total_customers // 2
                
                print(f"\n🎯 Priority Address Analysis (with gentle time windows):")
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
                    
                    # Check if within priority window
                    arrival_time = datetime.fromisoformat(priority_visit['arrival_time'].replace('Z', '+00:00'))
                    within_window = priority_start <= arrival_time <= priority_end
                    print(f"   Within priority window: {'✅ YES' if within_window else '❌ NO'}")
                
                # Display brief schedule
                print(f"\n📅 Brief Schedule:")
                for i, visit in enumerate(customer_visits):
                    arrival = datetime.fromisoformat(visit['arrival_time'].replace('Z', '+00:00'))
                    marker = "🎯" if priority_address in visit['address'] else "📍"
                    position = i + 1
                    half_marker = "🟢" if position <= first_half_size else "🔴"
                    
                    print(f"   {marker} {position}/{total_customers} {half_marker} {visit['address'][:40]}... - {arrival.strftime('%H:%M')}")
                
                return result
                
            else:
                print(f"❌ Optimization failed: {result.get('error', 'Unknown error')}")
                return None
                
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error details: {error_data}")
            except:
                print(f"   Error text: {response.text}")
            return None
                
    except requests.exceptions.Timeout:
        print("❌ Request timeout - optimization took too long")
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None

if __name__ == "__main__":
    # Test without time windows first
    basic_result = test_without_time_windows()
    
    # If basic test works, try gentle time windows
    if basic_result:
        gentle_result = test_with_gentle_time_windows()
        
        # Compare results
        print("\n\n🔍 Comparison Summary:")
        print("=" * 50)
        print(f"Basic optimization: {'✅ SUCCESS' if basic_result else '❌ FAILED'}")
        print(f"Gentle time windows: {'✅ SUCCESS' if gentle_result else '❌ FAILED'}")
        
        if basic_result and gentle_result:
            print("\n📊 Both methods worked! Time windows functionality is operational.")
        elif basic_result:
            print("\n⚠️  Basic optimization works, but time windows need adjustment.")
        else:
            print("\n❌ Basic optimization failed - check API status.") 