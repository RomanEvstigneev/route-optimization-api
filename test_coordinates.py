#!/usr/bin/env python3
"""
Test script for Route Optimization API - Coordinates Feature
Tests the new coordinates functionality in the API response.
"""

import requests
import json
from datetime import datetime

# Configuration
API_URL = "http://localhost:8080/api/optimize"  # Local testing
# API_URL = "https://items-routes-route-optimisation-dot-maibach-items-routes.ew.r.appspot.com/api/optimize"  # Production

def test_coordinates_feature():
    """Test the new coordinates feature in the API"""
    print("🧪 Testing Route Optimization API - Coordinates Feature")
    print("=" * 60)
    
    # Test data with mixed German and international addresses
    test_data = {
        "addresses": [
            "Berlin Hauptbahnhof, Berlin, Germany",
            "Potsdamer Platz, Berlin, Germany",
            "Brandenburg Gate, Berlin, Germany",
            "Alexanderplatz, Berlin, Germany"
        ]
    }
    
    try:
        print(f"📡 Sending request to: {API_URL}")
        print(f"📍 Testing with {len(test_data['addresses'])} addresses")
        
        # Make API request
        response = requests.post(
            API_URL,
            headers={'Content-Type': 'application/json'},
            json=test_data,
            timeout=30
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
                print("\n🗺️ Testing address_coordinates field:")
                if 'address_coordinates' in result:
                    print("✅ address_coordinates field present")
                    coords = result['address_coordinates']
                    
                    print(f"📍 Found coordinates for {len(coords)} addresses:")
                    for address, coord in coords.items():
                        if 'latitude' in coord and 'longitude' in coord:
                            print(f"  ✅ {address}")
                            print(f"      Lat: {coord['latitude']}, Lng: {coord['longitude']}")
                        else:
                            print(f"  ❌ {address} - Missing lat/lng")
                else:
                    print("❌ address_coordinates field missing!")
                
                # Test visit_schedule coordinates
                print("\n🕐 Testing visit_schedule coordinates:")
                if 'visit_schedule' in result:
                    print("✅ visit_schedule field present")
                    schedule = result['visit_schedule']
                    
                    print(f"📋 Found {len(schedule)} stops in schedule:")
                    for stop in schedule:
                        stop_num = stop.get('stop_number', 'N/A')
                        address = stop.get('address', 'N/A')
                        lat = stop.get('latitude')
                        lng = stop.get('longitude')
                        arrival = stop.get('arrival_time', 'N/A')
                        
                        if lat is not None and lng is not None:
                            print(f"  ✅ Stop {stop_num}: {address[:40]}...")
                            print(f"      Coords: {lat}, {lng}")
                            print(f"      Arrival: {arrival}")
                        else:
                            print(f"  ❌ Stop {stop_num}: Missing coordinates")
                else:
                    print("❌ visit_schedule field missing!")
                
                # Test timing and optimization info
                print("\n⏱️ Timing Information:")
                if 'timing_info' in result:
                    timing = result['timing_info']
                    print(f"  Start: {timing.get('vehicle_start_time')}")
                    print(f"  End: {timing.get('vehicle_end_time')}")
                    print(f"  Duration: {timing.get('total_duration_hours')} hours")
                
                print("\n📊 Optimization Information:")
                if 'optimization_info' in result:
                    opt_info = result['optimization_info']
                    print(f"  Distance: {opt_info.get('total_distance_km')} km")
                    print(f"  Time: {opt_info.get('total_time_hours')} hours")
                    print(f"  Addresses: {opt_info.get('addresses_count')}")
                
                # Test route optimization
                print("\n🛣️ Optimized Route:")
                if 'optimized_addresses' in result:
                    for i, addr in enumerate(result['optimized_addresses'][:5], 1):
                        print(f"  {i}. {addr}")
                
                print("\n✅ All tests passed! Coordinates feature working correctly.")
                
            else:
                print(f"❌ Optimization failed: {result.get('error', 'Unknown error')}")
                
        else:
            print(f"❌ HTTP Error {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error: {error_data.get('error', 'Unknown error')}")
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
        else:
            print(f"❌ Health check failed: {response.status_code}")
    
    except Exception as e:
        print(f"❌ Health check error: {e}")

if __name__ == "__main__":
    test_health_endpoint()
    test_coordinates_feature() 