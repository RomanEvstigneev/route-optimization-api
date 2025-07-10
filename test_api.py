#!/usr/bin/env python3
"""
Test script for Route Optimization API
Demonstrates how to use the API endpoint from external systems
"""

import requests
import json
from pprint import pprint

# Configuration
API_BASE_URL = "http://localhost:8080"
API_ENDPOINT = f"{API_BASE_URL}/api/optimize"

def test_api_optimize():
    """Test the /api/optimize endpoint"""
    
    # Test data - German addresses
    test_data = {
        "addresses": [
            "Neumarkter Str. 39, 90584 Allersberg, Deutschland",
            "Kolpingstraße 2, 90584 Allersberg, Deutschland",
            "Dietkirchen 13, 92367 Pilsach, Deutschland",
            "Am Klosterberg, 84095 Furth, Deutschland",
            "Harrhof 7, 90584 Allersberg, Deutschland",
            "Guggenmühle 15, 90584 Allersberg, Deutschland",
            "Lippacher Str. 1, 84095 Furth, Deutschland",
            "Seelstraße 20, 92318 Neumarkt in der Oberpfalz, Deutschland"
        ]
    }
    
    print("=" * 60)
    print("TESTING ROUTE OPTIMIZATION API")
    print("=" * 60)
    
    print(f"API Endpoint: {API_ENDPOINT}")
    print(f"Input addresses: {len(test_data['addresses'])}")
    print("\nOriginal addresses:")
    for i, addr in enumerate(test_data['addresses'], 1):
        print(f"  {i}. {addr}")
    
    print("\nSending request...")
    
    try:
        # Send POST request
        headers = {
            'Content-Type': 'application/json'
        }
        
        response = requests.post(
            API_ENDPOINT,
            headers=headers,
            json=test_data,
            timeout=60  # 60 seconds timeout
        )
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            print("\n" + "=" * 60)
            print("OPTIMIZATION RESULT")
            print("=" * 60)
            
            print(f"Success: {result['success']}")
            print(f"Message: {result['message']}")
            
            # Optimization info
            opt_info = result['optimization_info']
            print(f"\nOptimization details:")
            print(f"  Algorithm: {opt_info['algorithm']}")
            print(f"  Total time: {opt_info['total_time_minutes']} minutes ({opt_info['total_time_hours']} hours)")
            print(f"  Addresses processed: {opt_info['addresses_count']}")
            
            # Optimized route
            print(f"\nOptimized route:")
            for i, addr in enumerate(result['optimized_addresses'], 1):
                print(f"  {i}. {addr}")
            
            print(f"\nRoute indices: {result['route_indices']}")
            
        else:
            print(f"Error: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {error_data}")
            except:
                print(f"Error response: {response.text}")
                
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
    except Exception as e:
        print(f"Error: {e}")

def test_api_errors():
    """Test API error handling"""
    
    print("\n" + "=" * 60)
    print("TESTING ERROR HANDLING")
    print("=" * 60)
    
    # Test 1: Missing addresses field
    print("\nTest 1: Missing addresses field")
    try:
        response = requests.post(
            API_ENDPOINT,
            headers={'Content-Type': 'application/json'},
            json={"invalid": "data"},
            timeout=10
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: Too few addresses
    print("\nTest 2: Too few addresses")
    try:
        response = requests.post(
            API_ENDPOINT,
            headers={'Content-Type': 'application/json'},
            json={"addresses": ["Only one address"]},
            timeout=10
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 3: Invalid content type
    print("\nTest 3: Invalid content type")
    try:
        response = requests.post(
            API_ENDPOINT,
            headers={'Content-Type': 'text/plain'},
            data="invalid data",
            timeout=10
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Route Optimization API Test")
    print("Make sure the Flask app is running on http://localhost:8080")
    print()
    
    # Test main functionality
    test_api_optimize()
    
    # Test error handling
    test_api_errors()
    
    print("\n" + "=" * 60)
    print("TESTING COMPLETE")
    print("=" * 60) 