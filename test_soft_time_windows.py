#!/usr/bin/env python3
"""
Test script for Route Optimization API - Soft Time Windows Feature
Tests the new soft time windows functionality in the API.
"""

import requests
import json
from datetime import datetime, timedelta
import pytz

# Configuration
API_URL = "http://localhost:8080/api/optimize"  # Local testing

def test_soft_time_windows():
    """Test the soft time windows feature"""
    print("🕐 Testing Route Optimization API - Soft Time Windows Feature")
    print("=" * 70)
    
    # Test data with German addresses
    test_data = {
        "addresses": [
            "Berlin Hauptbahnhof, Berlin, Germany",  # Depot
            "Potsdamer Platz, Berlin, Germany",      # Address 1
            "Brandenburg Gate, Berlin, Germany",      # Address 2  
            "Alexanderplatz, Berlin, Germany"        # Address 3
        ],
        "time_windows": {
            "enabled": True,
            "windows": [
                {
                    "address_index": 1,  # Potsdamer Platz
                    "soft_start_time": "2024-12-21T10:00:00Z",
                    "soft_end_time": "2024-12-21T14:00:00Z",
                    "cost_per_hour_before": 10.0,
                    "cost_per_hour_after": 5.0
                },
                {
                    "address_index": 2,  # Brandenburg Gate
                    "hard_start_time": "2024-12-21T11:00:00Z",
                    "hard_end_time": "2024-12-21T15:00:00Z"
                },
                {
                    "address_index": 3,  # Alexanderplatz
                    "soft_start_time": "2024-12-21T13:00:00Z",
                    "soft_end_time": "2024-12-21T17:00:00Z",
                    "cost_per_hour_before": 15.0,
                    "cost_per_hour_after": 8.0
                }
            ]
        }
    }
    
    print("📋 Test Configuration:")
    print(f"  Depot: {test_data['addresses'][0]}")
    print(f"  Total addresses: {len(test_data['addresses'])}")
    print(f"  Time windows: {len(test_data['time_windows']['windows'])} configured")
    
    for i, window in enumerate(test_data['time_windows']['windows']):
        addr_idx = window['address_index']
        print(f"    Address {addr_idx} ({test_data['addresses'][addr_idx]}):")
        if 'soft_start_time' in window:
            print(f"      Soft window: {window['soft_start_time']} - {window['soft_end_time']}")
            print(f"      Costs: {window.get('cost_per_hour_before', 0)} before, {window.get('cost_per_hour_after', 0)} after")
        elif 'hard_start_time' in window:
            print(f"      Hard window: {window['hard_start_time']} - {window['hard_end_time']}")
    
    print("\n🚀 Sending request to API...")
    
    try:
        # Send POST request
        headers = {
            'Content-Type': 'application/json'
        }
        
        response = requests.post(
            API_URL,
            headers=headers,
            json=test_data,
            timeout=60
        )
        
        print(f"📡 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            print("\n" + "=" * 60)
            print("✅ SOFT TIME WINDOWS OPTIMIZATION RESULT")
            print("=" * 60)
            
            print(f"Success: {result['success']}")
            print(f"Message: {result['message']}")
            
            # Timing information
            timing = result.get('timing_info', {})
            print(f"\n🕐 Timing Information:")
            print(f"  Vehicle start: {timing.get('vehicle_start_time', 'N/A')}")
            print(f"  Vehicle end: {timing.get('vehicle_end_time', 'N/A')}")
            print(f"  Total duration: {timing.get('total_duration_minutes', 0)} minutes")
            
            # Optimized route
            print(f"\n🚗 Optimized Route:")
            for i, addr in enumerate(result['optimized_addresses'], 1):
                print(f"  {i}. {addr}")
            
            # Detailed schedule with time windows
            print(f"\n📅 Detailed Schedule with Time Windows:")
            for stop in result.get('visit_schedule', []):
                print(f"  {stop['stop_number']}. {stop['address']}")
                print(f"     📍 Coordinates: {stop['latitude']}, {stop['longitude']}")
                print(f"     ⏰ Arrival: {stop['arrival_time']}")
                print(f"     🔧 Service: {stop['service_duration_minutes']}min")
                print(f"     ⏸️  Wait: {stop['wait_duration_minutes']}min")
                print(f"     🏷️  Type: {stop['stop_type']}")
                print()
            
            # Cost breakdown (if available)
            if 'costs' in result.get('optimization_info', {}):
                print(f"\n💰 Cost Breakdown:")
                costs = result['optimization_info']['costs']
                for cost_type, cost_value in costs.items():
                    print(f"  {cost_type}: {cost_value}")
            
            print(f"\n📊 Optimization Summary:")
            opt_info = result.get('optimization_info', {})
            print(f"  Total distance: {opt_info.get('total_distance_km', 0)} km")
            print(f"  Total time: {opt_info.get('total_time_minutes', 0)} minutes")
            print(f"  Addresses processed: {opt_info.get('addresses_count', 0)}")
            
        else:
            print(f"❌ Error: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {error_data}")
            except:
                print(f"Error response: {response.text}")
                
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_without_time_windows():
    """Test the API without time windows (default behavior)"""
    print("\n" + "=" * 70)
    print("🕐 Testing Route Optimization API - WITHOUT Time Windows (Default)")
    print("=" * 70)
    
    # Test data without time windows
    test_data = {
        "addresses": [
            "Berlin Hauptbahnhof, Berlin, Germany",
            "Potsdamer Platz, Berlin, Germany",
            "Brandenburg Gate, Berlin, Germany",
            "Alexanderplatz, Berlin, Germany"
        ]
    }
    
    print("📋 Test Configuration:")
    print(f"  Depot: {test_data['addresses'][0]}")
    print(f"  Total addresses: {len(test_data['addresses'])}")
    print(f"  Time windows: NOT configured (default behavior)")
    
    try:
        response = requests.post(
            API_URL,
            headers={'Content-Type': 'application/json'},
            json=test_data,
            timeout=60
        )
        
        print(f"📡 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ Success: {result['success']}")
            print(f"Message: {result['message']}")
            
            timing = result.get('timing_info', {})
            print(f"\n🕐 Total duration: {timing.get('total_duration_minutes', 0)} minutes")
            
            print(f"\n🚗 Route: {' → '.join(result['optimized_addresses'])}")
            
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🧪 Route Optimization API - Soft Time Windows Testing")
    print("=" * 70)
    
    # Test 1: With soft time windows
    test_soft_time_windows()
    
    # Test 2: Without time windows (default behavior)  
    test_without_time_windows()
    
    print("\n✅ Testing completed!") 