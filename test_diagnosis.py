#!/usr/bin/env python3
"""
Simple diagnosis test for API
"""

import requests
import json

# Configuration
API_URL = "https://items-routes-route-optimisation-dot-maibach-items-routes.ew.r.appspot.com/api/optimize"

def test_basic_api():
    """Test basic API without time windows"""
    print("🔍 Test 1: Basic API (no time windows)")
    print("=" * 50)
    
    # Simple test data
    addresses = [
        "Berlin Hauptbahnhof, Berlin, Germany",
        "Potsdamer Platz, Berlin, Germany",
        "Brandenburg Gate, Berlin, Germany"
    ]
    
    request_data = {
        "addresses": addresses
    }
    
    print(f"📤 Request: {json.dumps(request_data, indent=2)}")
    
    try:
        response = requests.post(API_URL, json=request_data, timeout=60)
        print(f"📥 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Basic API works!")
                return True
            else:
                print(f"❌ API failed: {result.get('error')}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_time_windows_simple():
    """Test simple time windows"""
    print("\n🔍 Test 2: Simple time windows")
    print("=" * 50)
    
    # Simple test data
    addresses = [
        "Berlin Hauptbahnhof, Berlin, Germany",
        "Potsdamer Platz, Berlin, Germany",
        "Brandenburg Gate, Berlin, Germany"
    ]
    
    request_data = {
        "addresses": addresses,
        "time_windows": {
            "enabled": True,
            "windows": [
                {
                    "address_index": 1,
                    "hard_start_time": "2025-07-15T10:00:00Z",
                    "hard_end_time": "2025-07-15T14:00:00Z"
                }
            ]
        }
    }
    
    print(f"📤 Request: {json.dumps(request_data, indent=2)}")
    
    try:
        response = requests.post(API_URL, json=request_data, timeout=60)
        print(f"📥 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Simple time windows work!")
                return True
            else:
                print(f"❌ Time windows failed: {result.get('error')}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_time_windows_soft():
    """Test soft time windows"""
    print("\n🔍 Test 3: Soft time windows")
    print("=" * 50)
    
    # Simple test data
    addresses = [
        "Berlin Hauptbahnhof, Berlin, Germany",
        "Potsdamer Platz, Berlin, Germany",
        "Brandenburg Gate, Berlin, Germany"
    ]
    
    request_data = {
        "addresses": addresses,
        "time_windows": {
            "enabled": True,
            "windows": [
                {
                    "address_index": 1,
                    "soft_start_time": "2025-07-15T10:00:00Z",
                    "soft_end_time": "2025-07-15T14:00:00Z",
                    "cost_per_hour_before": 5.0,
                    "cost_per_hour_after": 10.0
                }
            ]
        }
    }
    
    print(f"📤 Request: {json.dumps(request_data, indent=2)}")
    
    try:
        response = requests.post(API_URL, json=request_data, timeout=60)
        print(f"📥 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Soft time windows work!")
                return True
            else:
                print(f"❌ Soft time windows failed: {result.get('error')}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🚨 API Diagnosis - Step by Step")
    print("=" * 60)
    
    # Test 1: Basic API
    basic_works = test_basic_api()
    
    if basic_works:
        # Test 2: Hard time windows
        hard_works = test_time_windows_simple()
        
        if hard_works:
            # Test 3: Soft time windows
            soft_works = test_time_windows_soft()
            
            if soft_works:
                print("\n🎉 All tests passed! API is working correctly.")
            else:
                print("\n⚠️ Soft time windows not working.")
        else:
            print("\n⚠️ Hard time windows not working.")
    else:
        print("\n❌ Basic API not working.")
    
    print("\n📋 Summary:")
    print(f"   Basic API: {'✅' if basic_works else '❌'}")
    if basic_works:
        print(f"   Hard time windows: {'✅' if hard_works else '❌'}")
        if hard_works:
            print(f"   Soft time windows: {'✅' if soft_works else '❌'}") 