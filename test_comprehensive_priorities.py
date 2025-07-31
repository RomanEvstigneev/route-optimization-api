#\!/usr/bin/env python3
"""
Comprehensive test for different priority levels and time windows
"""

import requests
import json
from datetime import datetime

PROD_API_URL = "https://items-routes-route-optimisation-dot-maibach-items-routes.ew.r.appspot.com/api/optimize"

def test_multiple_priorities():
    """Test multiple priority addresses with different levels"""
    
    test_data = {
        "addresses": [
            "Neumarkter str. 39, 90584 Allersberg",          # Start
            "Kugelpoint 1, 83629 Weyarn",                    # Customer 1
            "Pichlmayrstraße 21 a, 83024 Rosenheim",        # Customer 2 - LOW priority
            "Innsbrucker Ring 153, 81669 München",           # Customer 3 - CRITICAL_HIGH priority
            "Amtmannsdorf 31, 92339 Beilngries",            # Customer 4
            "Horneckerweg 28, 90408 Nürnberg",              # Customer 5 - HIGH priority
            "Erlenstraße 3, 90441 Nürnberg"                 # End
        ],
        "start_time": "2025-07-31T08:00:00.000Z",
        "objective": "minimize_time",
        "priority_addresses": [
            {
                "address": "Innsbrucker Ring 153, 81669 München",
                "priority_level": "critical_high",
                "preferred_time_window": "earliest"
            },
            {
                "address": "Horneckerweg 28, 90408 Nürnberg",
                "priority_level": "high",
                "preferred_time_window": "early"
            },
            {
                "address": "Pichlmayrstraße 21 a, 83024 Rosenheim",
                "priority_level": "low",
                "preferred_time_window": "late"
            }
        ]
    }
    
    print("🧪 TESTING MULTIPLE PRIORITY LEVELS")
    print("=" * 50)
    
    print(f"📤 Testing {len(test_data['priority_addresses'])} priority addresses:")
    for i, p in enumerate(test_data['priority_addresses'], 1):
        print(f"  {i}. {p['address']}")
        print(f"     Priority: {p['priority_level']} | Window: {p['preferred_time_window']}")
    
    try:
        response = requests.post(
            PROD_API_URL,
            headers={'Content-Type': 'application/json'},
            json=test_data,
            timeout=90
        )
        
        print(f"\n📥 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            analyze_multiple_priorities(result, test_data)
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


def analyze_multiple_priorities(result, original_data):
    """Analyze results for multiple priority addresses"""
    
    print(f"\n🎉 SUCCESS\! Multiple priority optimization completed")
    print("=" * 50)
    
    optimized_addresses = result.get('optimized_addresses', [])
    route_indices = result.get('route_indices', [])
    
    print(f"🔢 Route indices: {route_indices}")
    print(f"⏱️  Total time: {result.get('timing_info', {}).get('total_duration_minutes', 0)} minutes")
    
    print(f"\n🎯 PRIORITY ADDRESS POSITIONS:")
    print("=" * 30)
    
    priority_results = []
    
    for priority_config in original_data['priority_addresses']:
        priority_address = priority_config['address']
        priority_level = priority_config['priority_level']
        time_window = priority_config['preferred_time_window']
        
        # Find original and optimized positions
        original_pos = None
        optimized_pos = None
        
        for i, addr in enumerate(original_data['addresses']):
            if priority_address == addr:
                original_pos = i + 1
                break
        
        for i, addr in enumerate(optimized_addresses):
            if priority_address == addr:
                optimized_pos = i + 1
                break
        
        if original_pos and optimized_pos:
            improvement = original_pos - optimized_pos
            priority_results.append({
                'address': priority_address,
                'level': priority_level,
                'time_window': time_window,
                'original_pos': original_pos,
                'optimized_pos': optimized_pos,
                'improvement': improvement
            })
            
            status = "✅ IMPROVED" if improvement > 0 else "⚠️ SAME/WORSE" if improvement <= 0 else "➡️ UNCHANGED"
            
            print(f"📍 {priority_level.upper()} priority ({time_window}):")
            print(f"   {priority_address.split(',')[0]}...")
            print(f"   {original_pos} → {optimized_pos} ({status})")
            if improvement > 0:
                print(f"   📈 Moved {improvement} positions EARLIER\! 🎉")
            elif improvement < 0:
                print(f"   📉 Moved {abs(improvement)} positions later")
            else:
                print(f"   ➡️ Position unchanged")
    
    # Check priority ordering logic
    print(f"\n🏆 PRIORITY EFFECTIVENESS ANALYSIS:")
    print("=" * 35)
    
    # Sort by priority level (critical_high should be earliest)
    priority_order = {'critical_high': 1, 'high': 2, 'medium': 3, 'low': 4, 'critical_low': 5}
    priority_results.sort(key=lambda x: priority_order.get(x['level'], 99))
    
    for i, result in enumerate(priority_results):
        expected_rank = i + 1  # 1st priority should be position 1, 2nd should be position 2, etc.
        actual_customer_pos = result['optimized_pos'] - 1  # Adjust for start point
        
        total_customers = len(optimized_addresses) - 2  # Exclude start/end
        
        print(f"🎯 {result['level'].upper()} priority:")
        print(f"   Customer position: {actual_customer_pos}/{total_customers}")
        
        # Check if it's in the expected part of the route
        if result['level'] == 'critical_high' and actual_customer_pos <= 2:
            print(f"   ✅ EXCELLENT: In first 2 customer positions\!")
        elif result['level'] == 'high' and actual_customer_pos <= total_customers // 2:
            print(f"   ✅ GOOD: In first half of route")
        elif result['level'] == 'low' and actual_customer_pos > total_customers // 2:
            print(f"   ✅ CORRECT: In second half of route (as expected for low priority)")
        else:
            print(f"   ⚠️ Could be better positioned")
    
    # Show final route
    print(f"\n🗺️  FINAL OPTIMIZED ROUTE:")
    print("=" * 25)
    for i, address in enumerate(optimized_addresses, 1):
        # Check if this address has priority
        priority_marker = "📍"
        for p in original_data['priority_addresses']:
            if p['address'] == address:
                level = p['priority_level'].upper()
                priority_marker = f"🎯 {level}"
                break
        
        short_address = address.split(',')[0] + "..."
        print(f"{i}. {priority_marker} {short_address}")


def test_single_critical_high():
    """Test single critical_high priority (should be very early)"""
    
    test_data = {
        "addresses": [
            "München Hauptbahnhof, München",
            "Rosenheim Zentrum, Rosenheim", 
            "Salzburg Altstadt, Salzburg",
            "Passau Zentrum, Passau",
            "Regensburg Dom, Regensburg",
            "Ingolstadt Zentrum, Ingolstadt",  # This should be CRITICAL_HIGH priority
            "Augsburg Rathaus, Augsburg"
        ],
        "start_time": "2025-07-31T09:00:00.000Z",
        "objective": "minimize_time",
        "priority_addresses": [
            {
                "address": "Ingolstadt Zentrum, Ingolstadt",
                "priority_level": "critical_high",
                "preferred_time_window": "earliest"
            }
        ]
    }
    
    print("\n🧪 TESTING SINGLE CRITICAL_HIGH PRIORITY")
    print("=" * 50)
    
    try:
        response = requests.post(PROD_API_URL, headers={'Content-Type': 'application/json'}, json=test_data, timeout=90)
        
        if response.status_code == 200:
            result = response.json()
            optimized_addresses = result.get('optimized_addresses', [])
            
            # Find position of priority address
            priority_address = test_data['priority_addresses'][0]['address']
            optimized_pos = None
            
            for i, addr in enumerate(optimized_addresses):
                if priority_address in addr:
                    optimized_pos = i + 1
                    break
            
            print(f"🎯 Critical priority address position: {optimized_pos}/{len(optimized_addresses)}")
            
            # Critical high should be in position 2 or 3 (after start point)
            if optimized_pos and optimized_pos <= 3:
                print(f"✅ EXCELLENT: Critical priority in position {optimized_pos} (early delivery\!)")
                return True
            else:
                print(f"⚠️ Warning: Critical priority in position {optimized_pos} (could be earlier)")
                return False
        else:
            print(f"❌ Request failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


if __name__ == "__main__":
    print("🚀 COMPREHENSIVE PRIORITY TESTING")
    print("=" * 60)
    
    # Test 1: Multiple priorities
    success1 = test_multiple_priorities()
    
    # Test 2: Single critical high
    success2 = test_single_critical_high()
    
    print(f"\n📊 FINAL RESULTS:")
    print("=" * 20)
    print(f"Multiple priorities test: {'✅ PASSED' if success1 else '❌ FAILED'}")
    print(f"Critical high test: {'✅ PASSED' if success2 else '❌ FAILED'}")
    
    overall_success = success1 and success2
    success_msg = "🎉 ALL TESTS PASSED\!" if overall_success else "⚠️ SOME TESTS FAILED"
    print(f"\n🎯 OVERALL: {success_msg}")
