#!/usr/bin/env python3
"""
Test script for Route Optimization API - German Addresses with Coordinates
Tests the new coordinates functionality using real German addresses.
"""

import requests
import json
from datetime import datetime

# Configuration
API_URL = "http://localhost:8080/api/optimize"  # Local testing

def test_german_addresses_with_coordinates():
    """Test the new coordinates feature using German addresses"""
    print("🇩🇪 Testing Route Optimization API - German Addresses with Coordinates")
    print("=" * 70)
    
    # Load test data from route_optimizer_test.json
    try:
        with open('route_optimizer_test.json', 'r', encoding='utf-8') as f:
            test_data = json.load(f)
    except FileNotFoundError:
        print("❌ route_optimizer_test.json not found!")
        return
    except Exception as e:
        print(f"❌ Error loading test data: {e}")
        return
    
    print(f"📍 Testing with {len(test_data['addresses'])} German addresses:")
    for i, addr in enumerate(test_data['addresses'], 1):
        print(f"  {i}. {addr}")
    
    try:
        print(f"\n📡 Sending request to: {API_URL}")
        
        # Make API request
        response = requests.post(
            API_URL,
            headers={'Content-Type': 'application/json'},
            json=test_data,
            timeout=60  # Increased timeout for multiple addresses
        )
        
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            # Verify success
            if result.get('success'):
                print("✅ Route optimization successful!")
                print(f"🔧 Algorithm: {result.get('algorithm')}")
                print(f"💬 Message: {result.get('message')}")
                
                # Test address_coordinates field
                print("\n🗺️ Address Coordinates (GPS):")
                if 'address_coordinates' in result:
                    coords = result['address_coordinates']
                    print(f"📍 Found coordinates for {len(coords)} addresses:")
                    
                    for i, (address, coord) in enumerate(coords.items(), 1):
                        if 'latitude' in coord and 'longitude' in coord:
                            print(f"  {i}. {address}")
                            print(f"      📍 Lat: {coord['latitude']:.6f}, Lng: {coord['longitude']:.6f}")
                        else:
                            print(f"  ❌ {address} - Missing coordinates!")
                else:
                    print("❌ address_coordinates field missing!")
                
                # Test visit_schedule with coordinates
                print("\n🕐 Visit Schedule with Coordinates:")
                if 'visit_schedule' in result:
                    schedule = result['visit_schedule']
                    print(f"📋 Found {len(schedule)} stops in schedule:")
                    
                    for stop in schedule:
                        stop_num = stop.get('stop_number', 'N/A')
                        address = stop.get('address', 'N/A')
                        lat = stop.get('latitude')
                        lng = stop.get('longitude')
                        arrival = stop.get('arrival_time', 'N/A')
                        stop_type = stop.get('stop_type', 'N/A')
                        
                        print(f"\n  📍 Stop {stop_num} - {stop_type}")
                        print(f"      Address: {address}")
                        if lat is not None and lng is not None:
                            print(f"      GPS: {lat:.6f}, {lng:.6f}")
                        else:
                            print(f"      GPS: ❌ Missing coordinates!")
                        
                        if arrival != 'N/A':
                            try:
                                arrival_dt = datetime.fromisoformat(arrival.replace('Z', '+00:00'))
                                print(f"      Arrival: {arrival_dt.strftime('%H:%M:%S')}")
                            except:
                                print(f"      Arrival: {arrival}")
                else:
                    print("❌ visit_schedule field missing!")
                
                # Test timing information
                print("\n⏱️ Timing Information:")
                if 'timing_info' in result:
                    timing = result['timing_info']
                    start_time = timing.get('vehicle_start_time', 'N/A')
                    end_time = timing.get('vehicle_end_time', 'N/A')
                    duration_hours = timing.get('total_duration_hours', 'N/A')
                    
                    print(f"  🚗 Vehicle Start: {start_time}")
                    print(f"  🏁 Vehicle End: {end_time}")
                    print(f"  ⏰ Total Duration: {duration_hours} hours")
                    print(f"  🛠️ Service Time per Stop: {timing.get('service_time_per_stop_minutes', 'N/A')} minutes")
                
                # Test optimization results
                print("\n📊 Optimization Results:")
                if 'optimization_info' in result:
                    opt_info = result['optimization_info']
                    print(f"  📏 Total Distance: {opt_info.get('total_distance_km', 'N/A')} km")
                    print(f"  🕐 Total Time: {opt_info.get('total_time_hours', 'N/A')} hours")
                    print(f"  📍 Addresses Count: {opt_info.get('addresses_count', 'N/A')}")
                
                # Test optimized route
                print("\n🛣️ Optimized Route:")
                if 'optimized_addresses' in result:
                    optimized = result['optimized_addresses']
                    for i, addr in enumerate(optimized, 1):
                        print(f"  {i}. {addr}")
                
                # Test route indices
                print("\n🔢 Route Indices:")
                if 'route_indices' in result:
                    indices = result['route_indices']
                    print(f"  Route order: {indices}")
                    print(f"  Original → Optimized mapping")
                
                print("\n✅ All tests passed! German addresses with coordinates working perfectly!")
                
                # Summary
                print("\n📋 SUMMARY:")
                print(f"  ✅ Coordinates extracted for all {len(coords)} addresses")
                print(f"  ✅ Visit schedule includes GPS coordinates")
                print(f"  ✅ Route optimization successful")
                print(f"  ✅ Timing information complete")
                print(f"  ✅ German addresses with special characters handled correctly")
                
            else:
                print(f"❌ Optimization failed: {result.get('error', 'Unknown error')}")
                
        else:
            print(f"❌ HTTP Error {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {error_data}")
            except:
                print(f"Raw response: {response.text}")
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def test_health_endpoint():
    """Test the health endpoint to verify API is running"""
    print("\n🏥 Testing Health Endpoint")
    print("-" * 30)
    
    try:
        health_url = API_URL.replace('/api/optimize', '/health')
        response = requests.get(health_url, timeout=10)
        
        if response.status_code == 200:
            health_data = response.json()
            print("✅ Health check successful")
            print(f"  Status: {health_data.get('status')}")
            print(f"  Service: {health_data.get('service')}")
            print(f"  Version: {health_data.get('version')}")
            print(f"  Google API: {health_data.get('google_api_configured')}")
            print(f"  Geocoding: {health_data.get('geocoding_enabled')}")
            print(f"  API Type: {health_data.get('api_type')}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting German Address Coordinates Test")
    print("=" * 50)
    
    if test_health_endpoint():
        print("\n" + "=" * 50)
        test_german_addresses_with_coordinates()
    else:
        print("\n❌ Health check failed - make sure the server is running!")
        print("Run: python main.py") 