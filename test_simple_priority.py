#!/usr/bin/env python3
"""
Simple Priority Test with known good addresses
"""

import requests
import json

# API Configuration  
PROD_API_URL = "https://items-routes-route-optimisation-dot-maibach-items-routes.ew.r.appspot.com/api/optimize"

def test_simple_priority():
    """Test with simple, well-known addresses"""
    
    # Simple test data with known good addresses
    test_data = {
        "addresses": [
            "Berlin Hauptbahnhof, Berlin, Germany",      # Start
            "Brandenburg Gate, Berlin, Germany",          # Customer 1
            "Potsdamer Platz, Berlin, Germany",          # Customer 2 - PRIORITY!
            "Alexanderplatz, Berlin, Germany",           # Customer 3
            "Berlin TV Tower, Berlin, Germany",          # Customer 4
            "Berlin Hauptbahnhof, Berlin, Germany"       # End (same as start)
        ],
        "start_time": "2024-12-21T08:00:00Z",
        "objective": "minimize_time",
        "service_time_minutes": 3,
        "priority_addresses": [
            {
                "address": "Potsdamer Platz, Berlin, Germany",
                "priority_level": "high",
                "preferred_time_window": "early"
            }
        ]
    }
    
    print("🧪 SIMPLE PRIORITY TEST")
    print("=" * 40)
    
    print(f"📤 Testing with {len(test_data['addresses'])} addresses")
    print(f"🎯 Priority address: {test_data['priority_addresses'][0]['address']}")
    print(f"📊 Priority level: {test_data['priority_addresses'][0]['priority_level']}")
    print(f"⏰ Expected position: EARLY (first half of route)")
    
    print(f"\n📋 Request data:")
    print(json.dumps(test_data, indent=2))
    
    print(f"\n🔄 Sending request...")
    
    try:
        response = requests.post(
            PROD_API_URL,
            headers={'Content-Type': 'application/json'},
            json=test_data,
            timeout=60
        )
        
        print(f"📥 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            analyze_simple_results(result, test_data)
            return True
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Error text: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Request failed: {str(e)}")
        return False


def analyze_simple_results(result, original_data):
    """Analyze the simple priority test results"""
    
    print(f"\n🎉 SUCCESS! API Response Received")
    print("=" * 35)
    
    # Basic validation
    success = result.get('success', False)
    print(f"✅ Success: {success}")
    
    if not success:
        print(f"❌ Optimization failed!")
        return
    
    # Get addresses
    priority_address = original_data['priority_addresses'][0]['address']
    original_addresses = result.get('original_addresses', [])
    optimized_addresses = result.get('optimized_addresses', [])
    
    print(f"🗺️  Algorithm: {result.get('algorithm', 'N/A')}")
    print(f"🎯 Objective: {result.get('optimization_objective', 'N/A')}")
    
    # Timing
    timing = result.get('timing_info', {})
    print(f"⏱️  Duration: {timing.get('total_duration_minutes', 0)} min")
    print(f"🚀 Start: {timing.get('vehicle_start_time', 'N/A')}")
    
    print(f"\n🎯 PRIORITY ANALYSIS")
    print("=" * 20)
    
    # Find priority address position
    priority_pos_original = None
    priority_pos_optimized = None
    
    for i, addr in enumerate(original_addresses):
        if priority_address == addr:
            priority_pos_original = i + 1
    
    for i, addr in enumerate(optimized_addresses):
        if priority_address == addr:
            priority_pos_optimized = i + 1
    
    print(f"🎯 Priority address: {priority_address}")
    print(f"📍 Original position: {priority_pos_original}/{len(original_addresses)}")
    print(f"🚀 Optimized position: {priority_pos_optimized}/{len(optimized_addresses)}")
    
    # Check if in first half
    if priority_pos_optimized:
        total_customers = len(optimized_addresses) - 2  # Exclude start/end
        customer_position = priority_pos_optimized - 1  # Adjust for start
        first_half = total_customers // 2
        
        if customer_position <= first_half:
            print(f"✅ SUCCESS: Priority address in FIRST HALF! ({customer_position}/{total_customers})")
        else:
            print(f"⚠️  Priority address in second half ({customer_position}/{total_customers})")
    
    # Show route comparison
    print(f"\n📋 ROUTE COMPARISON")
    print("=" * 18)
    
    print("📥 Original:")
    for i, addr in enumerate(original_addresses, 1):
        marker = "🎯" if addr == priority_address else "📍"
        print(f"  {i}. {marker} {addr}")
    
    print("\n🚀 Optimized:")
    for i, addr in enumerate(optimized_addresses, 1):
        marker = "🎯 HIGH PRIORITY" if addr == priority_address else "📍"
        print(f"  {i}. {marker} {addr}")
    
    # Check if priority moved earlier
    if priority_pos_original and priority_pos_optimized:
        if priority_pos_optimized < priority_pos_original:
            improvement = priority_pos_original - priority_pos_optimized
            print(f"\n📈 🎉 PRIORITY WORKED! Moved {improvement} positions EARLIER!")
        else:
            print(f"\n📉 Priority address didn't move earlier")
    
    print(f"\n✨ Priority system is {'WORKING' if priority_pos_optimized and priority_pos_optimized <= 3 else 'needs adjustment'}")


if __name__ == "__main__":
    success = test_simple_priority()
    if success:
        print(f"\n🎉 PRIORITY TEST PASSED!")
    else:
        print(f"\n❌ PRIORITY TEST FAILED!") 