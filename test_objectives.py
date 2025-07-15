#!/usr/bin/env python3
"""
Test Objectives functionality for Google Route Optimization API
This is an experimental feature that defines optimization targets
"""

import json
import requests
import os
from datetime import datetime, timezone

def test_objectives_basic():
    """Test basic objectives functionality with MIN_TRAVEL_TIME"""
    
    # Load the test data
    with open('route_optimizer_test.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Get the first 5 addresses for testing
    addresses = data['addresses'][:5]
    print(f"Testing with {len(addresses)} addresses:")
    for i, addr in enumerate(addresses):
        print(f"  {i}: {addr}")
    
    # Prepare shipments
    shipments = []
    for i, address in enumerate(addresses):
        shipment = {
            "deliveries": [{
                "arrivalLocation": {
                    "latitude": 48.774265,  # Depot location
                    "longitude": 11.4233402
                },
                "duration": "300s"
            }],
            "pickups": [{
                "arrivalLocation": {
                    "latitude": 48.774265,  # Will be geocoded in real implementation
                    "longitude": 11.4233402  # Using depot for now
                },
                "duration": "180s"
            }]
        }
        shipments.append(shipment)
    
    # Create request with objectives instead of cost model
    request_data = {
        "model": {
            "shipments": shipments,
            "vehicles": [{
                "startLocation": {
                    "latitude": 48.774265,
                    "longitude": 11.4233402
                },
                "endLocation": {
                    "latitude": 48.774265,
                    "longitude": 11.4233402
                },
                "travelMode": "DRIVING"
            }],
            "objectives": [{
                "type": "MIN_TRAVEL_TIME"
            }]
        }
    }
    
    print("\nTesting objectives with MIN_TRAVEL_TIME...")
    print(json.dumps(request_data, indent=2))
    
    # Test the request
    url = f"https://routeoptimization.googleapis.com/v1/projects/{os.getenv('GOOGLE_CLOUD_PROJECT')}:optimizeTours"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {get_access_token()}"
    }
    
    try:
        response = requests.post(url, headers=headers, json=request_data)
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print("\nSuccess! Objectives work!")
            analyze_objectives_response(result)
        else:
            print("Failed - investigating error...")
            
    except Exception as e:
        print(f"Error: {e}")


def test_transform_and_return():
    """Test TRANSFORM_AND_RETURN_REQUEST mode to see what objectives generate"""
    
    # Simple request with objectives
    request_data = {
        "model": {
            "shipments": [{
                "deliveries": [{
                    "arrivalLocation": {
                        "latitude": 48.774265,
                        "longitude": 11.4233402
                    },
                    "duration": "300s"
                }],
                "pickups": [{
                    "arrivalLocation": {
                        "latitude": 48.780000,
                        "longitude": 11.430000
                    },
                    "duration": "180s"
                }]
            }],
            "vehicles": [{
                "startLocation": {
                    "latitude": 48.774265,
                    "longitude": 11.4233402
                },
                "endLocation": {
                    "latitude": 48.774265,
                    "longitude": 11.4233402
                },
                "travelMode": "DRIVING"
            }],
            "objectives": [{
                "type": "MIN_TRAVEL_TIME"
            }]
        },
        "solvingMode": "TRANSFORM_AND_RETURN_REQUEST"
    }
    
    print("\nTesting TRANSFORM_AND_RETURN_REQUEST mode...")
    print(json.dumps(request_data, indent=2))
    
    url = f"https://routeoptimization.googleapis.com/v1/projects/{os.getenv('GOOGLE_CLOUD_PROJECT')}:optimizeTours"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {get_access_token()}"
    }
    
    try:
        response = requests.post(url, headers=headers, json=request_data)
        print(f"\nResponse Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("\nTransformed request:")
            print(json.dumps(result, indent=2))
            
            # Show what cost model was generated
            if 'processedRequest' in result:
                processed = result['processedRequest']
                if 'model' in processed and 'vehicles' in processed['model']:
                    vehicle = processed['model']['vehicles'][0]
                    print(f"\nGenerated cost model:")
                    for key, value in vehicle.items():
                        if 'cost' in key.lower():
                            print(f"  {key}: {value}")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")


def test_other_objective_types():
    """Test different objective types to find all available options"""
    
    objective_types = [
        "MIN_TRAVEL_TIME",
        "MIN_TRAVEL_DISTANCE", 
        "MIN_VEHICLES",
        "MINIMIZE_COST",
        "BALANCE_WORKLOAD",
        "MAX_ON_TIME_DELIVERIES",
        "MINIMIZE_LATE_DELIVERIES"
    ]
    
    base_request = {
        "model": {
            "shipments": [{
                "deliveries": [{
                    "arrivalLocation": {
                        "latitude": 48.774265,
                        "longitude": 11.4233402
                    },
                    "duration": "300s"
                }],
                "pickups": [{
                    "arrivalLocation": {
                        "latitude": 48.780000,
                        "longitude": 11.430000
                    },
                    "duration": "180s"
                }]
            }],
            "vehicles": [{
                "startLocation": {
                    "latitude": 48.774265,
                    "longitude": 11.4233402
                },
                "endLocation": {
                    "latitude": 48.774265,
                    "longitude": 11.4233402
                },
                "travelMode": "DRIVING"
            }]
        },
        "solvingMode": "TRANSFORM_AND_RETURN_REQUEST"
    }
    
    url = f"https://routeoptimization.googleapis.com/v1/projects/{os.getenv('GOOGLE_CLOUD_PROJECT')}:optimizeTours"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {get_access_token()}"
    }
    
    print("\nTesting different objective types...")
    
    for obj_type in objective_types:
        request_data = base_request.copy()
        request_data["model"]["objectives"] = [{"type": obj_type}]
        
        print(f"\nTesting objective: {obj_type}")
        
        try:
            response = requests.post(url, headers=headers, json=request_data)
            
            if response.status_code == 200:
                print(f"  ✅ {obj_type} - SUCCESS")
            else:
                print(f"  ❌ {obj_type} - FAILED: {response.status_code}")
                error_details = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
                print(f"     Error: {error_details}")
                
        except Exception as e:
            print(f"  ❌ {obj_type} - ERROR: {e}")


def analyze_objectives_response(result):
    """Analyze the response from objectives optimization"""
    print(f"\nAnalyzing objectives response...")
    
    if 'routes' in result:
        print(f"Number of routes: {len(result['routes'])}")
        for i, route in enumerate(result['routes']):
            print(f"\nRoute {i}:")
            print(f"  Visits: {len(route.get('visits', []))}")
            if 'metrics' in route:
                metrics = route['metrics']
                print(f"  Travel duration: {metrics.get('travelDuration', 'N/A')}")
                print(f"  Travel distance: {metrics.get('travelDistanceMeters', 'N/A')}m")
            
            if 'routeCosts' in route:
                print(f"  Route costs: {route['routeCosts']}")
    
    if 'metrics' in result:
        print(f"\nOverall metrics:")
        print(f"  Total cost: {result['metrics'].get('totalCost', 'N/A')}")
        if 'costs' in result['metrics']:
            print(f"  Cost breakdown: {result['metrics']['costs']}")


def get_access_token():
    """Get access token for Google Cloud API"""
    try:
        import subprocess
        result = subprocess.run(
            ['gcloud', 'auth', 'application-default', 'print-access-token'],
            capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except Exception as e:
        print(f"Error getting access token: {e}")
        return None


if __name__ == "__main__":
    print("=== Testing Google Route Optimization API Objectives ===")
    print(f"Time: {datetime.now(timezone.utc).isoformat()}")
    
    # Test 1: Basic objectives functionality
    test_objectives_basic()
    
    # Test 2: Transform and return mode
    test_transform_and_return()
    
    # Test 3: Different objective types
    test_other_objective_types()
    
    print("\n=== Objectives Testing Complete ===") 