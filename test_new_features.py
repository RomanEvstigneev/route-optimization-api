#!/usr/bin/env python3
"""
Test script for new Route Optimization API features
Tests custom start time and optimization objectives
"""

import requests
import json
from datetime import datetime, timedelta
from pprint import pprint

# Configuration
API_BASE_URL = "http://localhost:8080"
API_ENDPOINT = f"{API_BASE_URL}/api/optimize"

def test_custom_start_time():
    """Test custom start time feature"""
    
    print("=" * 60)
    print("TESTING CUSTOM START TIME")
    print("=" * 60)
    
    # Test data with custom start time
    tomorrow_morning = (datetime.now() + timedelta(days=1)).replace(hour=8, minute=0, second=0, microsecond=0)
    start_time_str = tomorrow_morning.isoformat() + "Z"
    
    test_data = {
        "addresses": [
            "Berlin Hauptbahnhof, Berlin, Germany",
            "Potsdamer Platz, Berlin, Germany",
            "Brandenburg Gate, Berlin, Germany",
            "Alexanderplatz, Berlin, Germany"
        ],
        "start_time": start_time_str
    }
    
    print(f"Testing with start time: {start_time_str}")
    
    try:
        response = requests.post(
            API_ENDPOINT,
            headers={'Content-Type': 'application/json'},
            json=test_data,
            timeout=60
        )
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            print("\n✅ Custom start time test successful!")
            print(f"Vehicle start time: {result['timing_info']['vehicle_start_time']}")
            print(f"Custom start time used: {result['timing_info']['custom_start_time_used']}")
            print(f"Message: {result['message']}")
            
            # Verify start time matches
            if start_time_str.replace("Z", "+00:00") in result['timing_info']['vehicle_start_time']:
                print("✅ Start time correctly applied")
            else:
                print("❌ Start time mismatch")
                
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

def test_optimization_objectives():
    """Test different optimization objectives"""
    
    print("\n" + "=" * 60)
    print("TESTING OPTIMIZATION OBJECTIVES")
    print("=" * 60)
    
    objectives = ["minimize_time", "minimize_distance", "minimize_cost"]
    
    base_data = {
        "addresses": [
            "Munich Central Station, Munich, Germany",
            "Marienplatz, Munich, Germany",
            "English Garden, Munich, Germany",
            "Oktoberfest Grounds, Munich, Germany"
        ]
    }
    
    for objective in objectives:
        print(f"\n--- Testing objective: {objective} ---")
        
        test_data = base_data.copy()
        test_data["objective"] = objective
        
        try:
            response = requests.post(
                API_ENDPOINT,
                headers={'Content-Type': 'application/json'},
                json=test_data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                
                print(f"✅ {objective} successful")
                print(f"Optimization objective: {result['optimization_objective']}")
                print(f"Cost per km: {result['optimization_info']['cost_per_kilometer']}")
                print(f"Cost per hour: {result['optimization_info']['cost_per_hour']}")
                print(f"Total distance: {result['optimization_info']['total_distance_km']} km")
                print(f"Total time: {result['timing_info']['total_duration_minutes']} minutes")
                
            else:
                print(f"❌ {objective} failed: {response.status_code}")
                print(response.text[:200])
                
        except Exception as e:
            print(f"❌ {objective} request failed: {e}")

def test_combined_features():
    """Test combination of new features with existing ones"""
    
    print("\n" + "=" * 60)
    print("TESTING COMBINED FEATURES")
    print("=" * 60)
    
    # Test data combining all features
    test_data = {
        "addresses": [
            "Hamburg Central Station, Hamburg, Germany",
            "Speicherstadt, Hamburg, Germany",
            "Elbphilharmonie, Hamburg, Germany",
            "St. Pauli, Hamburg, Germany",
            "Hamburg Airport, Hamburg, Germany"
        ],
        "start_time": "2024-12-21T07:30:00Z",
        "objective": "minimize_cost",
        "priority_addresses": [
            {
                "address": "Elbphilharmonie, Hamburg, Germany",
                "priority_level": "high",
                "preferred_time_window": "early"
            }
        ]
    }
    
    print("Testing combined features:")
    print("- Custom start time: 07:30 UTC")
    print("- Objective: minimize_cost")
    print("- Priority address: Elbphilharmonie (high priority, early)")
    
    try:
        response = requests.post(
            API_ENDPOINT,
            headers={'Content-Type': 'application/json'},
            json=test_data,
            timeout=60
        )
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            print("\n✅ Combined features test successful!")
            print(f"Optimization objective: {result['optimization_objective']}")
            print(f"Vehicle start time: {result['timing_info']['vehicle_start_time']}")
            print(f"Custom start time used: {result['timing_info']['custom_start_time_used']}")
            print(f"Cost parameters: {result['optimization_info']['cost_per_kilometer']}/km, {result['optimization_info']['cost_per_hour']}/hour")
            
            print("\nOptimized route:")
            for i, addr in enumerate(result['optimized_addresses'], 1):
                print(f"  {i}. {addr}")
                
            # Check if priority address is early in route
            priority_addr = "Elbphilharmonie, Hamburg, Germany"
            for i, addr in enumerate(result['optimized_addresses']):
                if addr == priority_addr:
                    position = i
                    total_stops = len(result['optimized_addresses'])
                    print(f"\nPriority address position: {position+1} of {total_stops}")
                    if position <= len(result['optimized_addresses']) // 2:
                        print("✅ Priority address in first half of route")
                    break
                    
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

def test_error_handling():
    """Test error handling for new parameters"""
    
    print("\n" + "=" * 60)
    print("TESTING ERROR HANDLING")
    print("=" * 60)
    
    # Test invalid start time
    print("--- Testing invalid start time ---")
    test_data = {
        "addresses": ["Berlin, Germany", "Munich, Germany"],
        "start_time": "invalid-time-format"
    }
    
    try:
        response = requests.post(API_ENDPOINT, json=test_data, headers={'Content-Type': 'application/json'})
        if response.status_code != 200:
            result = response.json()
            print(f"✅ Invalid start time correctly rejected: {result.get('error', 'Unknown error')}")
        else:
            print("❌ Invalid start time should have been rejected")
    except Exception as e:
        print(f"Request failed: {e}")
    
    # Test invalid objective
    print("\n--- Testing invalid objective ---")
    test_data = {
        "addresses": ["Berlin, Germany", "Munich, Germany"],
        "objective": "invalid_objective"
    }
    
    try:
        response = requests.post(API_ENDPOINT, json=test_data, headers={'Content-Type': 'application/json'})
        if response.status_code != 200:
            result = response.json()
            print(f"✅ Invalid objective correctly rejected: {result.get('error', 'Unknown error')}")
        else:
            print("❌ Invalid objective should have been rejected")
    except Exception as e:
        print(f"Request failed: {e}")

def main():
    """Run all tests"""
    print("ROUTE OPTIMIZATION API - NEW FEATURES TEST SUITE")
    print("Testing custom start time and optimization objectives")
    print(f"API Endpoint: {API_ENDPOINT}")
    
    # Test individual features
    test_custom_start_time()
    test_optimization_objectives()
    
    # Test combined features
    test_combined_features()
    
    # Test error handling
    test_error_handling()
    
    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    main()