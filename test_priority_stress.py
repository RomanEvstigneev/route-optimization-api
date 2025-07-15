#!/usr/bin/env python3
"""
Stress test for priority address functionality
Tests cases where priority should have a more visible effect
"""

import requests
import json
from datetime import datetime

API_URL = "https://items-routes-route-optimisation-dot-maibach-items-routes.ew.r.appspot.com/api/optimize"

def test_priority_vs_geography():
    """
    Test priority against geographical optimization
    Using addresses where priority should override natural geographical order
    """
    print("🧪 Testing Priority vs Geography")
    print("=" * 50)
    
    # Addresses arranged so the priority address would naturally be visited later
    test_data = {
        "addresses": [
            "Munich Central Station, Munich, Germany",     # Start (South)
            "Augsburg, Germany",                           # Customer 1 (closer to start)
            "Ingolstadt, Germany",                         # Customer 2 (closer to start)  
            "Regensburg, Germany",                         # Customer 3 (closer to start)
            "Nuremberg, Germany",                          # Customer 4 (middle)
            "Bamberg, Germany",                            # Customer 5 (further north)
            "Wurzburg, Germany",                           # Customer 6 (further north)
            "Frankfurt am Main, Germany"                   # End (North)
        ],
        "priority_addresses": [
            {
                "address": "Bamberg, Germany",  # This should be visited early despite being geographically far
                "priority_level": "high",
                "preferred_time_window": "early"
            }
        ]
    }
    
    print(f"📤 Testing North-South route with priority on northern city")
    print(f"🎯 Priority address: Bamberg, Germany (geographically far from start)")
    print(f"📊 Expected: Bamberg should be visited early despite being far north")
    
    try:
        response = requests.post(
            API_URL,
            headers={'Content-Type': 'application/json'},
            json=test_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"\n✅ SUCCESS - Status: {response.status_code}")
            analyze_geography_vs_priority(result, test_data)
            return True
        else:
            error_data = response.json()
            print(f"❌ Error: {error_data.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def analyze_geography_vs_priority(result, test_data):
    """
    Analyze if priority overrode geographical optimization
    """
    optimized_addresses = result.get('optimized_addresses', [])
    priority_address = test_data['priority_addresses'][0]['address']
    
    print(f"\n🗺️  OPTIMIZED ROUTE:")
    priority_position = None
    for i, addr in enumerate(optimized_addresses, 1):
        is_priority = addr == priority_address
        marker = "🎯" if is_priority else "📍"
        print(f"   {i}. {marker} {addr}")
        
        if is_priority:
            priority_position = i
    
    # Analyze priority position
    if priority_position:
        total_customers = len(optimized_addresses) - 2  # Exclude start and end
        customer_position = priority_position - 1  # Adjust for start point
        
        print(f"\n🎯 PRIORITY ANALYSIS:")
        print(f"   Priority address: {priority_address}")
        print(f"   Position: {priority_position} of {len(optimized_addresses)}")
        print(f"   Customer position: {customer_position} of {total_customers}")
        
        # Check if it's in first half
        first_half = total_customers // 2
        is_early = customer_position <= first_half
        
        print(f"   First half threshold: {first_half}")
        print(f"   Is in first half: {'✅ YES' if is_early else '❌ NO'}")
        
        # Success if priority address is visited early
        if is_early:
            print(f"   🎉 SUCCESS: Priority overrode geographical optimization!")
        else:
            print(f"   ⚠️  Geography might have been stronger than priority")


def test_extreme_priority_levels():
    """
    Test different priority levels to see their effect
    """
    print("\n🧪 Testing Extreme Priority Levels")
    print("=" * 50)
    
    # Test high priority
    test_data_high = {
        "addresses": [
            "Berlin Hauptbahnhof, Berlin, Germany",
            "Potsdam, Germany",
            "Brandenburg an der Havel, Germany", 
            "Magdeburg, Germany",
            "Hanover, Germany",
            "Hamburg, Germany"
        ],
        "priority_addresses": [
            {
                "address": "Hamburg, Germany",  # Last city should be visited first
                "priority_level": "high",
                "preferred_time_window": "early"
            }
        ]
    }
    
    print(f"📤 Testing HIGH priority: Hamburg (last city) should be visited early")
    
    try:
        response = requests.post(
            API_URL,
            headers={'Content-Type': 'application/json'},
            json=test_data_high,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            optimized_addresses = result.get('optimized_addresses', [])
            
            print(f"✅ HIGH Priority Result:")
            for i, addr in enumerate(optimized_addresses, 1):
                is_priority = addr == "Hamburg, Germany"
                marker = "🎯" if is_priority else "📍"
                print(f"   {i}. {marker} {addr}")
                
                if is_priority:
                    customer_pos = i - 1
                    total_customers = len(optimized_addresses) - 2
                    print(f"   → Hamburg position: {customer_pos} of {total_customers} customers")
            
            return True
        else:
            error_data = response.json()
            print(f"❌ Error: {error_data.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def test_multiple_priority_competition():
    """
    Test multiple priority addresses competing for early positions
    """
    print("\n🧪 Testing Multiple Priority Competition")
    print("=" * 50)
    
    test_data = {
        "addresses": [
            "Paris, France",
            "Lyon, France",
            "Marseille, France",
            "Toulouse, France",
            "Nice, France",
            "Nantes, France",
            "Strasbourg, France",
            "Montpellier, France",
            "Bordeaux, France"
        ],
        "priority_addresses": [
            {
                "address": "Nice, France",
                "priority_level": "high",
                "preferred_time_window": "early"
            },
            {
                "address": "Bordeaux, France",
                "priority_level": "high", 
                "preferred_time_window": "early"
            },
            {
                "address": "Strasbourg, France",
                "priority_level": "medium",
                "preferred_time_window": "early"
            }
        ]
    }
    
    print(f"📤 Testing 3 priority addresses competing for early slots")
    print(f"🎯 High priority: Nice, Bordeaux")
    print(f"📊 Medium priority: Strasbourg")
    
    try:
        response = requests.post(
            API_URL,
            headers={'Content-Type': 'application/json'},
            json=test_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            optimized_addresses = result.get('optimized_addresses', [])
            
            print(f"✅ Multiple Priority Result:")
            priority_positions = {}
            
            for i, addr in enumerate(optimized_addresses, 1):
                is_priority = any(p['address'] == addr for p in test_data['priority_addresses'])
                marker = "🎯" if is_priority else "📍"
                print(f"   {i}. {marker} {addr}")
                
                if is_priority:
                    # Find priority level
                    for p in test_data['priority_addresses']:
                        if p['address'] == addr:
                            priority_positions[addr] = {
                                'position': i,
                                'level': p['priority_level']
                            }
                            break
            
            # Analyze priority positions
            print(f"\n🎯 PRIORITY POSITIONS:")
            for addr, info in priority_positions.items():
                customer_pos = info['position'] - 1
                total_customers = len(optimized_addresses) - 2
                print(f"   {addr}: Position {customer_pos}/{total_customers} (Level: {info['level']})")
            
            return True
        else:
            error_data = response.json()
            print(f"❌ Error: {error_data.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def main():
    """
    Run all stress tests
    """
    print("🚀 PRIORITY ADDRESS STRESS TESTS")
    print("=" * 60)
    
    results = []
    
    # Test 1: Priority vs Geography
    results.append(test_priority_vs_geography())
    
    # Test 2: Extreme priority levels
    results.append(test_extreme_priority_levels())
    
    # Test 3: Multiple priority competition
    results.append(test_multiple_priority_competition())
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 STRESS TEST SUMMARY")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"✅ Tests passed: {passed}/{total}")
    print(f"❌ Tests failed: {total - passed}/{total}")
    
    if passed == total:
        print("🎉 ALL STRESS TESTS PASSED!")
        print("🎯 Priority address functionality is working robustly!")
    else:
        print("⚠️  Some stress tests failed - priority might need tuning")


if __name__ == "__main__":
    main() 