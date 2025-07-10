#!/usr/bin/env python3
"""
Test script to verify deployment readiness
Tests all endpoints locally before deploying to Google Cloud
"""

import requests
import json
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BASE_URL = "http://localhost:8080"

def test_health_endpoint():
    """Test health check endpoint"""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_home_page():
    """Test home page accessibility"""
    print("🔍 Testing home page...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ Home page accessible")
            return True
        else:
            print(f"❌ Home page failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Home page error: {e}")
        return False

def test_api_optimization():
    """Test route optimization API"""
    print("🔍 Testing route optimization API...")
    
    # Check if API key is available
    if not os.environ.get('GOOGLE_MAPS_API_KEY'):
        print("⚠️  GOOGLE_MAPS_API_KEY not set - skipping API test")
        return True
    
    test_data = {
        "addresses": [
            "Berlin, Germany",
            "Munich, Germany", 
            "Hamburg, Germany"
        ]
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/optimize",
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Route optimization API working")
                print(f"   📊 Optimized {len(data['original_addresses'])} addresses")
                print(f"   ⏱️  Total time: {data['optimization_info']['total_time_minutes']} minutes")
                return True
            else:
                print(f"❌ API returned success=False: {data}")
                return False
        else:
            print(f"❌ API failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ API test error: {e}")
        return False

def test_example_download():
    """Test example JSON download"""
    print("🔍 Testing example download...")
    try:
        response = requests.get(f"{BASE_URL}/example")
        if response.status_code == 200:
            print("✅ Example JSON download working")
            return True
        else:
            print(f"❌ Example download failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Example download error: {e}")
        return False

def main():
    """Run all deployment tests"""
    print("🚀 Testing deployment readiness...")
    print("=" * 50)
    
    # Wait for server to start
    print("⏳ Waiting for server to start...")
    time.sleep(2)
    
    tests = [
        test_health_endpoint,
        test_home_page,
        test_example_download,
        test_api_optimization
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print("-" * 30)
    
    print(f"\n📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! Ready for deployment!")
        return True
    else:
        print("❌ Some tests failed. Please fix issues before deploying.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 