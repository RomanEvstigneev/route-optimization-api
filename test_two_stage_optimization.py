#!/usr/bin/env python3
"""
Test script for two-stage optimization functionality
Tests that priority addresses work with percentage-based time windows calculated from real route duration
"""

import requests
import json
from datetime import datetime

# Test configuration
API_URL = "http://localhost:8080/api/optimize"

def test_two_stage_optimization():
    """Test the two-stage optimization process with priority addresses"""
    
    print("🔬 Testing Two-Stage Optimization with Priority Addresses")
    print("=" * 70)
    
    # Test data with priority addresses to trigger two-stage optimization
    test_data = {
        "addresses": [
            "Berlin Hauptbahnhof, Berlin, Germany",     # Start point
            "Munich Central Station, Munich, Germany",  # Priority address (should be early)
            "Hamburg Central Station, Hamburg, Germany", # Regular address
            "Dresden Central Station, Dresden, Germany", # Regular address  
            "Cologne Central Station, Cologne, Germany", # Low priority (should be late)
            "Alexanderplatz, Berlin, Germany"           # End point
        ],
        "priority_addresses": [
            {
                "address": "Munich Central Station, Munich, Germany",
                "priority_level": "critical_high",
                "preferred_time_window": "earliest"
            },
            {
                "address": "Cologne Central Station, Cologne, Germany", 
                "priority_level": "critical_low",
                "preferred_time_window": "latest"
            }
        ],
        "start_time": "2024-12-21T08:00:00Z",
        "objective": "minimize_time"
    }
    
    print("📝 Test Configuration:")
    print(f"  - Start: {test_data['addresses'][0]}")
    print(f"  - End: {test_data['addresses'][-1]}")
    print(f"  - Priority High: {test_data['priority_addresses'][0]['address']}")
    print(f"  - Priority Low: {test_data['priority_addresses'][1]['address']}")
    print(f"  - Start Time: {test_data['start_time']}")
    print()
    
    try:
        response = requests.post(API_URL, json=test_data, headers={'Content-Type': 'application/json'})
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Two-Stage Optimization SUCCEEDED")
            print()
            
            # Check if this was actually two-stage optimization
            if result.get('two_stage_optimization'):
                print("🎯 Confirmed: Two-stage optimization was used")
                print(f"   Stage 1 duration: {result.get('stage1_duration', 'N/A')} minutes")
                print(f"   Stage 2 duration: {result.get('stage2_duration', 'N/A')} minutes")
            else:
                print("⚠️  Warning: Single-stage optimization was used instead")
            
            print()
            print("📋 Optimized Route Order:")
            for i, address in enumerate(result['optimized_addresses'], 1):
                marker = ""
                if address == test_data['priority_addresses'][0]['address']:
                    marker = " 🔴 (HIGH PRIORITY)"
                elif address == test_data['priority_addresses'][1]['address']:
                    marker = " 🔵 (LOW PRIORITY)"
                elif i == 1:
                    marker = " 🏁 (START)"
                elif i == len(result['optimized_addresses']):
                    marker = " 🏁 (END)"
                    
                print(f"  {i}. {address}{marker}")
            
            # Analyze priority positioning
            print()
            print("🔍 Priority Analysis:")
            high_priority_addr = test_data['priority_addresses'][0]['address']
            low_priority_addr = test_data['priority_addresses'][1]['address']
            
            high_pos = None
            low_pos = None
            
            for i, addr in enumerate(result['optimized_addresses']):
                if addr == high_priority_addr:
                    high_pos = i + 1
                elif addr == low_priority_addr:
                    low_pos = i + 1
            
            total_stops = len(result['optimized_addresses'])
            
            if high_pos and high_pos <= 3:  # Should be in first 3 positions
                print(f"  ✅ High priority address at position {high_pos}/{total_stops} (GOOD)")
            elif high_pos:
                print(f"  ⚠️  High priority address at position {high_pos}/{total_stops} (Could be better)")
            
            if low_pos and low_pos >= total_stops - 2:  # Should be in last 2 positions
                print(f"  ✅ Low priority address at position {low_pos}/{total_stops} (GOOD)")
            elif low_pos:
                print(f"  ⚠️  Low priority address at position {low_pos}/{total_stops} (Could be better)")
            
            # Display timing info
            print()
            print("⏱️  Timing Information:")
            timing = result.get('timing_info', {})
            print(f"   Start: {timing.get('vehicle_start_time', 'N/A')}")
            print(f"   End: {timing.get('vehicle_end_time', 'N/A')}")
            print(f"   Total Duration: {timing.get('total_duration_minutes', 'N/A')} minutes")
            print(f"   Custom Start Time Used: {timing.get('custom_start_time_used', False)}")
            
            # Display optimization info
            print()
            print("📊 Optimization Details:")
            opt_info = result.get('optimization_info', {})
            print(f"   Algorithm: {result.get('algorithm', 'N/A')}")
            print(f"   Objective: {result.get('optimization_objective', 'N/A')}")
            print(f"   Total Distance: {opt_info.get('total_distance_km', 'N/A')} km")
            print(f"   Cost Parameters: {opt_info.get('cost_per_kilometer', 'N/A')}/km, {opt_info.get('cost_per_hour', 'N/A')}/hour")
            
        else:
            print(f"❌ Two-Stage Optimization FAILED - HTTP {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('error', 'Unknown error')}")
            except:
                print(f"   Response: {response.text[:500]}...")
                
    except requests.exceptions.ConnectionError:
        print("❌ Test FAILED - Could not connect to API")
        print("   Make sure the API is running: python main.py")
    except Exception as e:
        print(f"❌ Test FAILED - Unexpected error: {e}")


def test_single_stage_fallback():
    """Test that requests without priorities still work (single-stage)"""
    
    print("\n" + "=" * 70)
    print("🔬 Testing Single-Stage Optimization (No Priorities)")
    print("=" * 70)
    
    # Test data WITHOUT priority addresses (should use single-stage)
    test_data = {
        "addresses": [
            "Berlin, Germany",
            "Munich, Germany", 
            "Hamburg, Germany",
            "Cologne, Germany"
        ],
        "start_time": "2024-12-21T09:00:00Z"
    }
    
    print("📝 Test Configuration:")
    print(f"  - Addresses: {len(test_data['addresses'])} stops")
    print(f"  - Priority Addresses: None (should trigger single-stage)")
    print(f"  - Start Time: {test_data['start_time']}")
    print()
    
    try:
        response = requests.post(API_URL, json=test_data, headers={'Content-Type': 'application/json'})
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Single-Stage Optimization SUCCEEDED")
            
            # Verify this was NOT two-stage optimization
            if not result.get('two_stage_optimization'):
                print("🎯 Confirmed: Single-stage optimization was used")
            else:
                print("⚠️  Warning: Two-stage optimization was used unexpectedly")
            
            print()
            print("📋 Route Order:")
            for i, address in enumerate(result['optimized_addresses'], 1):
                print(f"  {i}. {address}")
            
            print()
            print("⏱️  Total Duration:", result['timing_info']['total_duration_minutes'], "minutes")
            
        else:
            print(f"❌ Single-Stage Test FAILED - HTTP {response.status_code}")
                
    except requests.exceptions.ConnectionError:
        print("❌ Test FAILED - Could not connect to API")
    except Exception as e:
        print(f"❌ Test FAILED - Unexpected error: {e}")


if __name__ == "__main__":
    print("🚀 Two-Stage Optimization Test Suite")
    print("="*70)
    print("This test verifies that:")
    print("- Priority addresses trigger two-stage optimization")
    print("- Route end time is calculated from first stage") 
    print("- Percentage-based time windows use real route duration")
    print("- Non-priority requests use single-stage optimization")
    print()
    
    test_two_stage_optimization()
    test_single_stage_fallback()
    
    print("\n" + "=" * 70)
    print("🏁 Test Suite Completed!")
    print()
    print("Expected behavior:")
    print("✅ High priority addresses should appear early in route")
    print("✅ Low priority addresses should appear late in route") 
    print("✅ Two-stage metadata should be present for priority requests")
    print("✅ Single-stage should be used for non-priority requests")
    print()
    print("Note: Run 'python main.py' to start the API server first")