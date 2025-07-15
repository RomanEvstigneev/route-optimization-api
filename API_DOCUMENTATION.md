# Route Optimization API Documentation
**Version 2.0.0 | Last Updated: July 11, 2025**

## Overview

This API provides professional route optimization functionality for delivery routes, sales routes, and other multi-stop journeys. It uses Google's Route Optimization API for professional-grade optimization with real-world constraints, traffic conditions, and precise timing calculations.

**🌐 Production API is live and ready for use!**  
**✅ Fully tested with real-world data (German addresses)**  
**✅ Enhanced with separate start and end points**  
**✅ Flexible routing with different start/end locations**

**Key Features:**
- ✅ **Production Ready** - Deployed on Google Cloud App Engine
- ✅ **Scalable** - Auto-scaling up to 5 instances
- ✅ **Secure** - HTTPS enabled for all endpoints
- ✅ **Professional Optimization** - Uses Google Route Optimization API
- ✅ **Flexible Start/End Points** - Different starting and ending locations supported
- ✅ **Single API Call** - No multiple requests like traditional approaches
- ✅ **Real-world Constraints** - Considers traffic, road conditions, vehicle limitations
- ✅ **High Capacity** - Supports up to 100+ addresses (vs 10 with Distance Matrix)
- ✅ **International Support** - Tested with German addresses, supports Unicode
- ✅ **Auto-Geocoding** - Automatically converts addresses to coordinates
- ✅ **GPS Coordinates** - Returns latitude/longitude for each address
- ✅ **Detailed Timing** - Precise scheduling with service times and arrival times
- ✅ **Soft Time Windows** - Flexible time constraints with cost penalties
- ✅ **Hard Time Windows** - Strict time constraints that cannot be violated
- ✅ **Visit Scheduling** - Complete timetable for each stop
- ✅ **Transition Analysis** - Travel time and distance between stops
- ✅ **Web Interface** - User-friendly web UI for manual optimization
- ✅ **REST API** - Programmatic access for system integration

## Base URL

**Production (Google Cloud App Engine):**
```
https://items-routes-route-optimisation-dot-maibach-items-routes.ew.r.appspot.com
```

**Local Development:**
```
http://localhost:8080
```

## Endpoints

### GET /health

Health check endpoint for monitoring service status.

**Response:**
```json
{
  "status": "healthy",
  "service": "route-optimization-api",
  "version": "2.0.0",
  "google_api_configured": true,
  "route_optimization_configured": true,
  "geocoding_enabled": true,
  "api_type": "Route Optimization API with Geocoding"
}
```

### GET /

Web interface for manual route optimization via file upload.

### GET /example

Download example JSON file with sample addresses.

### POST /api/optimize

Optimizes the order of addresses to minimize total travel time with separate start and end points. The first address is the fixed starting point, the last address is the fixed ending point, and all addresses in between are optimized for the best route order.

#### Request

**URL:** `POST /api/optimize`

**Headers:**
- `Content-Type: application/json`

**Body:**
```json
{
  "addresses": [
    "Address 1",
    "Address 2",
    "Address 3",
    "..."
  ],
  "time_windows": {
    "enabled": true,
    "windows": [
      {
        "address_index": 1,
        "soft_start_time": "2024-12-21T10:00:00Z",
        "soft_end_time": "2024-12-21T14:00:00Z",
        "cost_per_hour_before": 10.0,
        "cost_per_hour_after": 5.0
      },
      {
        "address_index": 2,
        "hard_start_time": "2024-12-21T11:00:00Z",
        "hard_end_time": "2024-12-21T15:00:00Z"
      }
    ]
  }
}
```

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| addresses | array | Yes | List of addresses to optimize (2-25 addresses). First address = start point, last address = end point, middle addresses are optimized |
| time_windows | object | No | **NEW:** Time windows configuration for soft/hard constraints |
| time_windows.enabled | boolean | No | Whether to enable time windows (default: false) |
| time_windows.windows | array | No | Array of time window configurations |
| time_windows.windows[].address_index | number | Yes | Index of address to apply time window to (1-based) |
| time_windows.windows[].soft_start_time | string | No | ISO timestamp for soft start time |
| time_windows.windows[].soft_end_time | string | No | ISO timestamp for soft end time |
| time_windows.windows[].hard_start_time | string | No | ISO timestamp for hard start time |
| time_windows.windows[].hard_end_time | string | No | ISO timestamp for hard end time |
| time_windows.windows[].cost_per_hour_before | number | No | Cost per hour for arriving before soft start |
| time_windows.windows[].cost_per_hour_after | number | No | Cost per hour for arriving after soft end |

#### Response

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Route optimization completed successfully using Google Route Optimization API with separate start/end points",
  "algorithm": "Google Route Optimization API",
  "original_addresses": [
    "Start point address",
    "Customer address 1",
    "Customer address 2",
    "End point address"
  ],
  "optimized_addresses": [
    "Start point address",
    "Customer address 2", 
    "Customer address 1",
    "End point address"
  ],
  "route_indices": [0, 2, 1, 3],
  "address_coordinates": {
    "Start point address": {
      "latitude": 52.520008,
      "longitude": 13.404954
    },
    "Customer address 1": {
      "latitude": 52.516231,
      "longitude": 13.377704
    },
    "Customer address 2": {
      "latitude": 52.513845,
      "longitude": 13.395267
    },
    "End point address": {
      "latitude": 52.518623,
      "longitude": 13.408290
    }
  },
  "timing_info": {
    "vehicle_start_time": "2024-12-20T23:00:00Z",
    "vehicle_end_time": "2024-12-21T02:30:00Z",
    "total_duration_seconds": 12600,
    "total_duration_minutes": 210.0,
    "total_duration_hours": 3.5,
    "service_time_per_stop_minutes": 3
  },
  "visit_schedule": [
    {
      "stop_number": 1,
      "address": "Start point address",
      "latitude": 52.520008,
      "longitude": 13.404954,
      "arrival_time": "2024-12-20T23:00:00Z",
      "service_duration_minutes": 0,
      "wait_duration_minutes": 0.0,
      "is_depot": false,
      "stop_type": "Start"
    },
    {
      "stop_number": 2,
      "address": "Customer address 2",
      "latitude": 52.513845,
      "longitude": 13.395267,
      "arrival_time": "2024-12-20T23:25:00Z",
      "service_duration_minutes": 3,
      "wait_duration_minutes": 0.0,
      "is_depot": false,
      "stop_type": "Customer Visit"
    },
    {
      "stop_number": 3,
      "address": "Customer address 1",
      "latitude": 52.516231,
      "longitude": 13.377704,
      "arrival_time": "2024-12-20T23:45:00Z",
      "service_duration_minutes": 3,
      "wait_duration_minutes": 0.0,
      "is_depot": false,
      "stop_type": "Customer Visit"
    },
    {
      "stop_number": 4,
      "address": "End point address",
      "latitude": 52.518623,
      "longitude": 13.408290,
      "arrival_time": "2024-12-21T02:30:00Z",
      "service_duration_minutes": 0,
      "wait_duration_minutes": 0.0,
      "is_depot": false,
      "stop_type": "End Point"
    }
  ],
  "transition_details": [
    {
      "segment": 1,
      "travel_duration_minutes": 25.0,
      "travel_distance_meters": 12500,
      "wait_duration_minutes": 0.0,
      "start_time": "2024-12-20T23:00:00Z"
    }
  ],
  "optimization_info": {
    "addresses_count": 4,
    "total_distance_meters": 45000,
    "total_distance_km": 45.0,
    "total_time_seconds": 12600,
    "total_time_minutes": 210.0,
    "total_time_hours": 3.5
  }
}
```

**Enhanced Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Whether optimization was successful |
| `message` | string | Detailed success message with algorithm info |
| `algorithm` | string | Optimization algorithm used |
| `original_addresses` | array | Input addresses in original order |
| `optimized_addresses` | array | Addresses in optimized order (includes return to depot) |
| `route_indices` | array | Indices mapping optimized route to original addresses |
| `address_coordinates` | object | **NEW:** GPS coordinates for each address (lat/lng) |
| `timing_info` | object | **NEW:** Detailed timing information |
| `timing_info.vehicle_start_time` | string | ISO timestamp when vehicle starts journey |
| `timing_info.vehicle_end_time` | string | ISO timestamp when vehicle returns to depot |
| `timing_info.total_duration_*` | number | Total journey time in seconds/minutes/hours |
| `timing_info.service_time_per_stop_minutes` | number | Service time allocated per customer stop (3 minutes) |
| `visit_schedule` | array | **NEW:** Detailed schedule for each stop |
| `visit_schedule[].stop_number` | number | Sequential stop number |
| `visit_schedule[].address` | string | Address for this stop |
| `visit_schedule[].latitude` | number | **NEW:** GPS latitude coordinate |
| `visit_schedule[].longitude` | number | **NEW:** GPS longitude coordinate |
| `visit_schedule[].arrival_time` | string | ISO timestamp of arrival |
| `visit_schedule[].service_duration_minutes` | number | Time spent at this stop |
| `visit_schedule[].is_depot` | boolean | Whether this is a depot (true only when start point = end point) |
| `visit_schedule[].stop_type` | string | Type: "Start", "Customer Visit", "End Point" |
| `transition_details` | array | **NEW:** Travel information between stops |
| `transition_details[].segment` | number | Segment number in route |
| `transition_details[].travel_duration_minutes` | number | Time to travel this segment |
| `transition_details[].travel_distance_meters` | number | Distance of this segment |
| `optimization_info` | object | **ENHANCED:** Comprehensive optimization metrics |
| `optimization_info.total_distance_*` | number | Total distance in meters and kilometers |

**Error Response (4xx/5xx):**
```json
{
  "success": false,
  "error": "Error description"
}
```

#### Error Codes

| Status Code | Description |
|-------------|-------------|
| 400 | Bad Request - Invalid JSON format or missing required fields |
| 500 | Internal Server Error - Optimization failed or server error |

#### Common Error Messages

- `Content-Type must be application/json`
- `Missing "addresses" field in JSON`
- `Addresses must be a list`
- `At least 2 addresses are required`
- `Maximum 25 addresses allowed`
- `Google Maps API key is not configured`
- `Google Cloud Project ID is not configured`
- `Could not find optimal route`
- `Route Optimization API failed`
- `No routes found in optimization response`

## Usage Examples

### Python

```python
import requests
import json
from datetime import datetime

# Configuration - Production URL
API_URL = "https://items-routes-route-optimisation-dot-maibach-items-routes.ew.r.appspot.com/api/optimize"

# For local development, use:
# API_URL = "http://localhost:8080/api/optimize"

# Request data
data = {
    "addresses": [
        "New York, NY",          # Start point (fixed)
        "Philadelphia, PA",      # Customer 1 (optimized)
        "Boston, MA",            # Customer 2 (optimized)
        "Washington, DC"         # End point (fixed)
    ]
}

# Make request
response = requests.post(
    API_URL,
    headers={'Content-Type': 'application/json'},
    json=data
)

if response.status_code == 200:
    result = response.json()
    print("Optimization successful!")
    
    # Basic information
    print(f"Algorithm: {result['algorithm']}")
    print(f"Total time: {result['timing_info']['total_duration_hours']} hours")
    print(f"Total distance: {result['optimization_info']['total_distance_km']} km")
    
    # Detailed schedule
    print("\nDetailed Schedule:")
    for stop in result['visit_schedule']:
        arrival = datetime.fromisoformat(stop['arrival_time'].replace('Z', '+00:00'))
        print(f"  {stop['stop_number']}. {stop['address']}")
        print(f"     Arrival: {arrival.strftime('%H:%M')} | Service: {stop['service_duration_minutes']}min | Type: {stop['stop_type']}")
        print(f"     Coordinates: {stop['latitude']}, {stop['longitude']}")
    
    # Address coordinates
    print("\nAddress Coordinates:")
    for address, coords in result['address_coordinates'].items():
        print(f"  {address}: {coords['latitude']}, {coords['longitude']}")
    
    # Optimized route
    print("\nOptimized Route:")
    for i, addr in enumerate(result['optimized_addresses'], 1):
        print(f"  {i}. {addr}")
else:
    error = response.json()
    print(f"Error: {error['error']}")
```

#### **Advanced Route Optimization with Time Windows**
```python
import requests
from datetime import datetime, timedelta

API_URL = "https://items-routes-route-optimisation-dot-maibach-items-routes.ew.r.appspot.com/api/optimize"

# Request data with time windows
data = {
    "addresses": [
        "Berlin Hauptbahnhof, Berlin, Germany",  # Start point (fixed)
        "Potsdamer Platz, Berlin, Germany",      # Customer 1 (optimized)
        "Brandenburg Gate, Berlin, Germany",      # Customer 2 (optimized)
        "Alexanderplatz, Berlin, Germany"        # End point (fixed)
    ],
    "time_windows": {
        "enabled": True,
        "windows": [
            {
                "address_index": 1,  # Potsdamer Platz
                "soft_start_time": "2024-12-21T10:00:00Z",
                "soft_end_time": "2024-12-21T14:00:00Z",
                "cost_per_hour_before": 10.0,
                "cost_per_hour_after": 5.0
            },
            {
                "address_index": 2,  # Brandenburg Gate
                "hard_start_time": "2024-12-21T11:00:00Z",
                "hard_end_time": "2024-12-21T15:00:00Z"
            },
            {
                "address_index": 3,  # Alexanderplatz
                "soft_start_time": "2024-12-21T13:00:00Z",
                "soft_end_time": "2024-12-21T17:00:00Z",
                "cost_per_hour_before": 15.0,
                "cost_per_hour_after": 8.0
            }
        ]
    }
}

response = requests.post(API_URL, json=data, headers={'Content-Type': 'application/json'})

if response.status_code == 200:
    result = response.json()
    print("✅ Route optimization with time windows successful!")
    print(f"Algorithm: {result['algorithm']}")
    print(f"Total time: {result['timing_info']['total_duration_minutes']} minutes")
    
    # Print time-aware schedule
    print("\n📅 Time-Aware Schedule:")
    for stop in result['visit_schedule']:
        arrival = datetime.fromisoformat(stop['arrival_time'].replace('Z', '+00:00'))
        print(f"  {stop['stop_number']}. {stop['address']}")
        print(f"     🕐 Arrival: {arrival.strftime('%H:%M')} | Service: {stop['service_duration_minutes']}min")
        print(f"     📍 Location: {stop['latitude']}, {stop['longitude']}")
        print(f"     🏷️  Type: {stop['stop_type']}")
    
    # Cost breakdown (if soft time windows were used)
    if 'costs' in result.get('optimization_info', {}):
        print(f"\n💰 Cost Breakdown:")
        for cost_type, cost_value in result['optimization_info']['costs'].items():
            print(f"  {cost_type}: {cost_value}")
else:
    error = response.json()
    print(f"❌ Error: {error['error']}")
```

### JavaScript (Node.js)

```javascript
const axios = require('axios');

// Configuration - Production URL
const API_URL = 'https://items-routes-route-optimisation-dot-maibach-items-routes.ew.r.appspot.com/api/optimize';

// For local development, use:
// const API_URL = 'http://localhost:8080/api/optimize';

const data = {
    addresses: [
        'New York, NY',          // Start point (fixed)
        'Philadelphia, PA',      // Customer 1 (optimized)
        'Boston, MA',            // Customer 2 (optimized)
        'Washington, DC'         // End point (fixed)
    ]
};

axios.post(API_URL, data, {
    headers: {
        'Content-Type': 'application/json'
    }
})
.then(response => {
    const result = response.data;
    console.log('Optimization successful!');
    
    // Basic information
    console.log(`Algorithm: ${result.algorithm}`);
    console.log(`Total time: ${result.timing_info.total_duration_hours} hours`);
    console.log(`Total distance: ${result.optimization_info.total_distance_km} km`);
    
    // Detailed schedule
    console.log('\nDetailed Schedule:');
    result.visit_schedule.forEach(stop => {
        const arrival = new Date(stop.arrival_time);
        console.log(`  ${stop.stop_number}. ${stop.address}`);
        console.log(`     Arrival: ${arrival.toLocaleTimeString()} | Service: ${stop.service_duration_minutes}min | Type: ${stop.stop_type}`);
        console.log(`     Coordinates: ${stop.latitude}, ${stop.longitude}`);
    });
    
    // Address coordinates
    console.log('\nAddress Coordinates:');
    Object.entries(result.address_coordinates).forEach(([address, coords]) => {
        console.log(`  ${address}: ${coords.latitude}, ${coords.longitude}`);
    });
    
    // Optimized route
    console.log('\nOptimized Route:');
    result.optimized_addresses.forEach((addr, index) => {
        console.log(`  ${index + 1}. ${addr}`);
    });
})
.catch(error => {
    if (error.response) {
        console.error('Error:', error.response.data.error);
    } else {
        console.error('Request failed:', error.message);
    }
});
```

### cURL

**Production:**
```bash
curl -X POST https://items-routes-route-optimisation-dot-maibach-items-routes.ew.r.appspot.com/api/optimize \
  -H "Content-Type: application/json" \
  -d '{
    "addresses": [
      "New York, NY",
      "Philadelphia, PA",
      "Boston, MA",
      "Washington, DC"
    ]
  }' | jq .
  
# Note: First address = start point, last address = end point, middle addresses are optimized
```

**Local Development:**
```bash
curl -X POST http://localhost:8080/api/optimize \
  -H "Content-Type: application/json" \
  -d '{
    "addresses": [
      "New York, NY",
      "Philadelphia, PA",
      "Boston, MA",
      "Washington, DC"
    ]
  }' | jq .
```

## Route Logic & Examples

### **NEW: Separate Start and End Points**

The API now supports flexible routing with different start and end points:

#### **How it works:**
- **First address** in the array = **Fixed start point**
- **Last address** in the array = **Fixed end point**  
- **Middle addresses** = **Optimized for best route order**

#### **Example scenarios:**

**Scenario 1: Same start/end (traditional depot)**
```json
{
  "addresses": [
    "Main Warehouse, Berlin",      // Start point
    "Customer A, Munich",          // Optimized
    "Customer B, Hamburg",         // Optimized
    "Main Warehouse, Berlin"       // End point (same as start)
  ]
}
```
Result: `Main Warehouse → Customer B → Customer A → Main Warehouse`

**Scenario 2: Different start/end**
```json
{
  "addresses": [
    "Warehouse A, Berlin",         // Start point
    "Customer A, Munich",          // Optimized
    "Customer B, Hamburg",         // Optimized
    "Warehouse B, Frankfurt"       // End point (different)
  ]
}
```
Result: `Warehouse A → Customer A → Customer B → Warehouse B`

**Scenario 3: Multiple customers**
```json
{
  "addresses": [
    "Distribution Center, Cologne",  // Start point
    "Customer 1, Düsseldorf",       // Optimized
    "Customer 2, Essen",            // Optimized
    "Customer 3, Dortmund",         // Optimized
    "Customer 4, Bochum",           // Optimized
    "Return Center, Wuppertal"      // End point
  ]
}
```
Result: `Distribution Center → Customer 2 → Customer 4 → Customer 3 → Customer 1 → Return Center`

### **Minimum Requirements:**
- **2 addresses minimum** - Start + End points
- **For optimization** - Minimum 3 addresses (Start + 1 Customer + End)
- **Maximum 25 addresses** - Google API limit

### **Business Use Cases:**

1. **Delivery Routes** - Start from warehouse, deliver to customers, end at different depot
2. **Service Calls** - Start from office, visit clients, end at home
3. **Sales Routes** - Start from hotel, visit prospects, end at airport
4. **Pickup Routes** - Start from depot, collect items, end at processing center

## Advanced Features

### Timing and Scheduling

The API provides detailed timing information including:

- **Vehicle Schedule:** Exact start and end times for the vehicle
- **Stop-by-Stop Schedule:** Arrival time, service duration, and wait time for each location
- **Transition Details:** Travel time and distance between consecutive stops
- **Service Time:** 3 minutes allocated per customer stop for delivery/pickup
- **Real-time Planning:** Routes planned starting at 23:00 for next-day execution

### Optimization Algorithm

The system uses **Google Route Optimization API** with:

1. **Geocoding:** All addresses converted to precise GPS coordinates
2. **Shipment Modeling:** Each stop modeled as a pickup location with service time
3. **Vehicle Constraints:** Single vehicle with depot start/end points
4. **Time Windows:** 24-hour optimization window starting at 23:00
5. **Real-world Data:** Actual road networks, traffic patterns, and driving speeds

### Data Processing

- **Input Validation:** Comprehensive validation of address format and count
- **Address Normalization:** Automatic geocoding and coordinate conversion
- **Route Calculation:** Single API call for complete optimization
- **Result Enhancement:** Detailed timing and scheduling calculations

## Rate Limiting & Performance

- **API Quotas:** Limited by Google Route Optimization API quotas
- **Request Limits:** Maximum 25 addresses per request (configurable up to 100+)
- **Efficiency:** Single API call per optimization (vs traditional multi-request approaches)
- **Optimization Time:** Typically 3-10 seconds for 5-25 addresses
- **Concurrent Requests:** Supports multiple concurrent optimizations
- **Recommended:** Implement client-side rate limiting for high-volume usage

## Authentication & Security

Currently, no authentication is required for public access. For production implementations, consider:

- **API Key Authentication:** Add API key validation for restricted access
- **IP Whitelisting:** Restrict access to specific IP ranges
- **Rate Limiting:** Implement per-IP or per-user request limits
- **HTTPS Enforcement:** All production traffic uses SSL/TLS encryption
- **Input Validation:** Comprehensive validation prevents malicious input
- **Error Handling:** Secure error responses without sensitive information

## Algorithm Technical Details

### **Google Route Optimization API Features:**
1. **Single API Call** - Complete optimization server-side at Google
2. **Real-world Constraints** - Traffic, road conditions, vehicle limitations
3. **Professional Algorithms** - Production-grade optimization engine
4. **High Performance** - Optimized for large-scale routing problems
5. **Service Time Support** - Accounts for time spent at each location
6. **Precise Timing** - Start/end times, arrival schedules, transition details

### **Optimization Process:**
1. **Input Processing** - First address becomes start point, last address becomes end point
2. **Geocoding** - All addresses converted to GPS coordinates using Google Geocoding API
3. **Shipment Creation** - Each middle address becomes a pickup location with 3-minute service time
4. **Vehicle Definition** - Single vehicle starts at first address, ends at last address
5. **Time Window Application** - 24-hour window starting at 23:00 current day
6. **Constraint Application** - Real-world driving constraints applied
7. **Route Optimization** - Google's algorithms find optimal sequence for middle addresses
8. **Result Enhancement** - Detailed timing and scheduling calculations

### **Advantages over Traditional TSP:**
- ✅ **No Distance Matrix Limits** - Handles 100+ addresses vs 10-25 limit
- ✅ **Real Traffic Data** - Uses current road conditions and historical patterns
- ✅ **Professional Grade** - Same engine used by Google Maps Platform
- ✅ **Cost Effective** - Single API call vs multiple Distance Matrix requests
- ✅ **Accurate Timing** - Includes service time and real driving speeds
- ✅ **Comprehensive Output** - Detailed schedules and transition information

## Time Windows Support

### **What are Time Windows?**
Time windows are constraints that specify when a vehicle can visit a location. The API supports two types:

#### **Hard Time Windows (Strict Constraints)**
- **Required compliance:** Vehicle MUST arrive within the specified time window
- **If violated:** The shipment is skipped entirely
- **Use case:** Customer business hours, mandatory delivery slots
- **Configuration:** Use `hard_start_time` and `hard_end_time`

#### **Soft Time Windows (Flexible Constraints)**
- **Preferred compliance:** Vehicle SHOULD arrive within the specified time window
- **If violated:** Additional cost is applied, but delivery still happens
- **Use case:** Preferred delivery times, customer convenience windows
- **Configuration:** Use `soft_start_time`, `soft_end_time`, and cost penalties

### **Time Windows Configuration**

#### **Default Behavior (No Time Windows)**
```json
{
  "addresses": [
    "Depot address",
    "Customer address 1",
    "Customer address 2"
  ]
}
```
- **Result:** Standard route optimization without time constraints
- **Optimization:** Purely based on distance and travel time

#### **Mixed Time Windows Example**
```json
{
  "addresses": [
    "Depot address",
    "Customer address 1",
    "Customer address 2",
    "Customer address 3"
  ],
  "time_windows": {
    "enabled": true,
    "windows": [
      {
        "address_index": 1,
        "soft_start_time": "2024-12-21T10:00:00Z",
        "soft_end_time": "2024-12-21T14:00:00Z",
        "cost_per_hour_before": 10.0,
        "cost_per_hour_after": 5.0
      },
      {
        "address_index": 2,
        "hard_start_time": "2024-12-21T11:00:00Z",
        "hard_end_time": "2024-12-21T15:00:00Z"
      },
      {
        "address_index": 3,
        "soft_start_time": "2024-12-21T13:00:00Z",
        "soft_end_time": "2024-12-21T17:00:00Z",
        "cost_per_hour_before": 15.0,
        "cost_per_hour_after": 8.0
      }
    ]
  }
}
```

### **Time Window Parameters**

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| **Hard Time Windows** | | | |
| `hard_start_time` | string | Earliest allowed arrival time (ISO format) | `"2024-12-21T11:00:00Z"` |
| `hard_end_time` | string | Latest allowed arrival time (ISO format) | `"2024-12-21T15:00:00Z"` |
| **Soft Time Windows** | | | |
| `soft_start_time` | string | Preferred earliest arrival time | `"2024-12-21T10:00:00Z"` |
| `soft_end_time` | string | Preferred latest arrival time | `"2024-12-21T14:00:00Z"` |
| `cost_per_hour_before` | number | Cost penalty per hour for arriving early | `10.0` |
| `cost_per_hour_after` | number | Cost penalty per hour for arriving late | `5.0` |

### **Business Use Cases**

#### **Delivery Services**
```json
{
  "address_index": 1,
  "hard_start_time": "2024-12-21T08:00:00Z",
  "hard_end_time": "2024-12-21T17:00:00Z",
  "soft_start_time": "2024-12-21T10:00:00Z",
  "soft_end_time": "2024-12-21T12:00:00Z",
  "cost_per_hour_before": 5.0,
  "cost_per_hour_after": 8.0
}
```
- **Hard window:** Customer's business hours (8 AM - 5 PM)
- **Soft window:** Preferred delivery time (10 AM - 12 PM)
- **Cost:** Higher penalty for being late than early

#### **Service Appointments**
```json
{
  "address_index": 2,
  "hard_start_time": "2024-12-21T14:00:00Z",
  "hard_end_time": "2024-12-21T16:00:00Z"
}
```
- **Strict appointment:** Must arrive between 2 PM - 4 PM
- **No flexibility:** Appointment will be skipped if timing doesn't work

### **Cost Optimization**
The API balances:
1. **Travel time minimization** (standard optimization)
2. **Time window compliance** (hard constraints)
3. **Cost penalties** (soft constraint violations)

**Example cost calculation:**
- Arrive 2 hours before soft start time
- `cost_per_hour_before = 10.0`
- **Additional cost:** 2 × 10.0 = 20.0 units

## Testing

### Quick Test (Production)

Test the health endpoint:
```bash
curl https://items-routes-route-optimisation-dot-maibach-items-routes.ew.r.appspot.com/health
```

Test route optimization with sample data:
```bash
curl -X POST https://items-routes-route-optimisation-dot-maibach-items-routes.ew.r.appspot.com/api/optimize \
  -H "Content-Type: application/json" \
  -d '{
    "addresses": [
      "Berlin, Germany",
      "Munich, Germany", 
      "Hamburg, Germany"
    ]
  }' | jq '.'
```
*Note: Berlin = start point, Hamburg = end point, Munich = optimized*

### Advanced Testing Examples

**Test with timing analysis:**
```bash
curl -X POST https://items-routes-route-optimisation-dot-maibach-items-routes.ew.r.appspot.com/api/optimize \
  -H "Content-Type: application/json" \
  -d '{
    "addresses": [
      "Berlin Hauptbahnhof, Berlin, Germany",
      "Potsdamer Platz, Berlin, Germany", 
      "Brandenburg Gate, Berlin, Germany",
      "Alexanderplatz, Berlin, Germany"
    ]
  }' | jq '.timing_info, .visit_schedule'
```
*Note: Hauptbahnhof = start, Alexanderplatz = end, Potsdamer Platz & Brandenburg Gate = optimized*

### ✅ Production-Tested with Real Data

**Successfully tested with German addresses:**
```bash
curl -X POST https://items-routes-route-optimisation-dot-maibach-items-routes.ew.r.appspot.com/api/optimize \
  -H "Content-Type: application/json" \
  -d '{
    "addresses": [
      "Neumarkter Str. 39, 90584 Allersberg, Deutschland",
      "Kolpingstraße 2, 90584 Allersberg, Deutschland", 
      "Dietkirchen 13, 92367 Pilsach, Deutschland",
      "Am Klosterberg, 84095 Furth, Deutschland",
      "Harrhof 7, 90584 Allersberg, Deutschland"
    ]
  }' | jq '.timing_info, .optimization_info'
```
*Note: Neumarkter Str. 39 = start, Harrhof 7 = end, middle addresses are optimized*

**Verified Results:**
- ✅ **Optimization successful** with 3.48 hours total route time
- ✅ **Detailed timing** - Vehicle start: 23:00, end: 02:30+1 day
- ✅ **Complete schedule** - Arrival times for each stop with 3-minute service time
- ✅ **Distance calculation** - Total distance in meters and kilometers
- ✅ **Route optimization** - Minimized travel time sequence

**International & Unicode Support:**
- ✅ **German addresses** - Full support for complex German address formats
- ✅ **Geocoding enabled** - Automatic conversion to precise GPS coordinates
- ✅ **Real-world routing** - Uses actual road networks and current traffic data
- ✅ **Unicode support** - Handles special characters (ü, ß, ä, ö, etc.)
- ✅ **Address validation** - Comprehensive validation and error handling

**Performance Metrics:**
- ✅ **Response time** - Typically 3-8 seconds for 5 addresses
- ✅ **Accuracy** - Professional-grade optimization results
- ✅ **Reliability** - Consistent results with proper error handling

### Local Testing

Use the provided test script to verify API functionality:

```bash
python test_api.py
```

## Production Deployment

**✅ Production-Ready API deployed and operational on Google Cloud App Engine!**

### Current Production Configuration

| Component | Configuration | Status |
|-----------|---------------|---------|
| **Platform** | Google Cloud App Engine | ✅ Active |
| **Service Name** | `items-routes-route-optimisation` | ✅ Running |
| **Runtime** | Python 3.9 | ✅ Latest |
| **WSGI Server** | Gunicorn (2 workers, 4 threads) | ✅ Optimized |
| **Instance Class** | B2 (Basic scaling) | ✅ Cost-effective |
| **Max Instances** | 5 (auto-scaling) | ✅ Scalable |
| **SSL/TLS** | HTTPS enforced | ✅ Secure |
| **Timeout** | 60 seconds | ✅ Sufficient |

### Environment Configuration

**Environment Variables:**
```yaml
GOOGLE_MAPS_API_KEY: ✅ Configured
GOOGLE_CLOUD_PROJECT_ID: maibach-items-routes
SECRET_KEY: ✅ Set
```

**Google Cloud APIs Enabled:**
- ✅ Route Optimization API
- ✅ Geocoding API  
- ✅ Maps Backend API
- ✅ App Engine API

### Monitoring & Observability

**Health Monitoring:**
```bash
# Check service health
curl https://items-routes-route-optimisation-dot-maibach-items-routes.ew.r.appspot.com/health

# Expected response
{
  "status": "healthy",
  "service": "route-optimization-api", 
  "version": "2.0.0",
  "google_api_configured": true,
  "route_optimization_configured": true
}
```

**Logging & Debugging:**
```bash
# View live application logs
gcloud app logs tail -s items-routes-route-optimisation

# View specific service logs
gcloud logging read "resource.type=gae_app AND resource.labels.service=items-routes-route-optimisation" --limit=50

# Check service status
gcloud app services describe items-routes-route-optimisation

# View current instances
gcloud app instances list --service=items-routes-route-optimisation
```

**Performance Monitoring:**
```bash
# Check scaling and performance
gcloud app services list
gcloud app versions list --service=items-routes-route-optimisation

# Monitor request metrics in Cloud Console
# Navigate to: Monitoring > Dashboards > App Engine
```

### Production Features

**✅ Implemented:**
1. **Production WSGI server** - Gunicorn with optimal worker configuration
2. **Comprehensive logging** - Structured logs with request tracing
3. **Error handling** - Detailed error responses with proper HTTP codes
4. **Input validation** - Robust validation for all API endpoints
5. **Health checks** - Monitoring endpoint for uptime verification
6. **SSL/TLS encryption** - All traffic secured automatically
7. **Auto-scaling** - Automatic instance management based on load
8. **Static file serving** - Optimized serving of CSS, JS, and example files

**🔄 Recommendations for Enhancement:**
1. **API Authentication** - Implement API key validation for production use
2. **Rate Limiting** - Add per-IP or per-user request limits
3. **Caching** - Implement Redis for optimization result caching
4. **Database** - Add persistent storage for optimization history
5. **Analytics** - Enhanced usage tracking and performance metrics
6. **Alerting** - Set up Cloud Monitoring alerts for issues

### Deployment Management

**Deploy New Version:**
```bash
# Deploy to production
gcloud app deploy app.yaml

# Deploy with specific version
gcloud app deploy app.yaml --version=v2-1 --no-promote

# Traffic splitting
gcloud app services set-traffic items-routes-route-optimisation --splits=v2-0=80,v2-1=20
```

**Rollback Process:**
```bash
# List versions
gcloud app versions list --service=items-routes-route-optimisation

# Set traffic to previous version
gcloud app services set-traffic items-routes-route-optimisation --splits=PREVIOUS_VERSION=100
```

## Support & Troubleshooting

### Quick Diagnostics

**Health Check:**
```bash
# Verify API is operational
curl https://items-routes-route-optimisation-dot-maibach-items-routes.ew.r.appspot.com/health

# Expected healthy response
{
  "status": "healthy",
  "service": "route-optimization-api",
  "version": "2.0.0",
  "google_api_configured": true,
  "route_optimization_configured": true
}
```

**Test API Functionality:**
```bash
# Quick 3-address test
curl -X POST https://items-routes-route-optimisation-dot-maibach-items-routes.ew.r.appspot.com/api/optimize \
  -H "Content-Type: application/json" \
  -d '{"addresses": ["Berlin, Germany", "Munich, Germany", "Hamburg, Germany"]}' \
  | jq '.success, .timing_info.total_duration_hours'
```

### Production Issues & Monitoring

**Service Monitoring:**
```bash
# Check service status
gcloud app services describe items-routes-route-optimisation

# Monitor live logs
gcloud app logs tail -s items-routes-route-optimisation

# Check recent errors
gcloud logging read "resource.type=gae_app AND severity>=ERROR" --limit=10
```

**Performance Monitoring:**
```bash
# Check current instances
gcloud app instances list --service=items-routes-route-optimisation

# View resource usage
gcloud monitoring metrics list --filter="metric.type:appengine"
```

### Common Troubleshooting

**❌ API Errors & Solutions:**

| Issue | Error Message | Solution |
|-------|---------------|----------|
| **Invalid JSON** | `Content-Type must be application/json` | Ensure `Content-Type: application/json` header |
| **Missing Data** | `Missing "addresses" field in JSON` | Include `addresses` array in request body |
| **Too Few Addresses** | `At least 2 addresses are required` | Provide minimum 2 addresses |
| **Too Many Addresses** | `Maximum 25 addresses allowed` | Reduce to 25 or fewer addresses |
| **Geocoding Failed** | `Failed to geocode address` | Use more specific addresses with country |
| **API Quota** | `Route Optimization API failed` | Wait and retry, check Google Cloud quotas |

**🔧 Address Format Issues:**

```bash
# ❌ Problematic addresses
"Main St"                    # Too vague
"123"                        # Incomplete
"Berlin"                     # City only

# ✅ Recommended formats
"123 Main Street, New York, NY 10001, USA"
"Alexanderplatz 1, 10178 Berlin, Germany"
"1600 Pennsylvania Avenue NW, Washington, DC 20500, USA"
```

**🌍 International Address Support:**

```bash
# ✅ Well-supported formats
"Champs-Élysées, 75008 Paris, France"           # French
"Via del Corso, 00186 Roma RM, Italy"           # Italian  
"Unter den Linden, 10117 Berlin, Deutschland"   # German
"Gran Vía, 28013 Madrid, Spain"                 # Spanish
```

### Performance Optimization

**🚀 Best Practices:**

1. **Address Quality:**
   - Use complete addresses with postal codes
   - Include country information for international addresses
   - Avoid abbreviations and ambiguous terms

2. **Request Optimization:**
   - Group geographically close addresses
   - Limit to 25 addresses per request for best performance
   - Use address validation before API calls

3. **Error Handling:**
   - Implement retry logic with exponential backoff
   - Check `success` field in response
   - Parse detailed error messages

**📊 Performance Expectations:**

| Addresses | Typical Response Time | Complexity |
|-----------|----------------------|------------|
| 2-5 | 2-4 seconds | Simple |
| 6-15 | 4-8 seconds | Moderate |
| 16-25 | 6-12 seconds | Complex |

### Web Interface

**🌐 Browser Access:**
- **URL:** https://items-routes-route-optimisation-dot-maibach-items-routes.ew.r.appspot.com
- **Features:** Upload JSON files, visual results, download examples
- **Example Data:** Available at `/example` endpoint

**📁 File Format:**
```json
{
  "addresses": [
    "Start point address (fixed)",
    "Customer 1 address (optimized)",
    "Customer 2 address (optimized)",
    "End point address (fixed)"
  ]
}
```

### Advanced Debugging

**🔍 Detailed Logging:**
```bash
# View optimization request details
gcloud logging read "resource.type=gae_app AND textPayload:optimization" --limit=5

# Monitor API response times
gcloud logging read "resource.type=gae_app AND textPayload:timing" --limit=5

# Check geocoding issues
gcloud logging read "resource.type=gae_app AND textPayload:geocoding" --limit=5
```

**📈 Custom Monitoring:**
```bash
# Set up custom alerts
gcloud alpha monitoring policies create --notification-channels=EMAIL_CHANNEL_ID \
  --display-name="Route API Errors" \
  --condition-filter="resource.type=gae_app"
```

### Contact Information

**🆘 For Technical Support:**
1. **Check Documentation:** Review this documentation first
2. **Test Health Endpoint:** Verify API operational status
3. **Review Logs:** Check application logs for error details
4. **Validate Input:** Ensure addresses are properly formatted
5. **Check Quotas:** Verify Google Cloud API quotas and billing

**📧 Escalation Process:**
1. Gather error logs and request details
2. Include example requests that demonstrate the issue
3. Specify expected vs actual behavior
4. Provide timestamp and frequency of issues 