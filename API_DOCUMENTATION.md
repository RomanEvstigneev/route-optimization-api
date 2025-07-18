# Route Optimization API Documentation
**Version 2.3.0 | Last Updated: July 18, 2025**

## Overview

This API provides professional route optimization functionality for delivery routes, sales routes, and other multi-stop journeys. It uses Google's Route Optimization API for professional-grade optimization with real-world constraints, traffic conditions, and precise timing calculations.

**🌐 Production API is live and ready for use!**  
**✅ Fully tested with real-world data (German addresses)**  
**✅ Enhanced with separate start and end points**  
**✅ NEW: Priority address functionality for early delivery**  
**✅ Flexible routing with different start/end locations**
**✅ NEW: Custom start time configuration**
**✅ NEW: Optimization objective selection (time/distance/cost)**

**Key Features:**
- ✅ **Production Ready** - Deployed on Google Cloud App Engine
- ✅ **Priority Addresses** - Prioritize specific addresses for early delivery
- ✅ **Custom Start Time** - Configure route start time instead of fixed 23:00
- ✅ **Optimization Objectives** - Choose between minimizing time, distance, or cost
- ✅ **Scalable** - Auto-scaling up to 5 instances
- ✅ **Secure** - HTTPS enabled for all endpoints
- ✅ **Professional Optimization** - Uses Google Route Optimization API
- ✅ **Flexible Start/End Points** - Different starting and ending locations supported
- ✅ **Single API Call** - No multiple requests like traditional approaches
- ✅ **Real-world Constraints** - Considers traffic, road conditions, vehicle limitations
- ✅ **High Capacity** - Supports unlimited addresses (vs 10 with Distance Matrix)
- ✅ **International Support** - Tested with German addresses, supports Unicode
- ✅ **Auto-Geocoding** - Automatically converts addresses to coordinates
- ✅ **GPS Coordinates** - Returns latitude/longitude for each address
- ✅ **Detailed Timing** - Precise scheduling with service times and arrival times
- ✅ **Time Windows** - Soft and hard time constraints with cost penalties
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
  "version": "2.1.0",
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

**✨ NEW: Priority Address Support** - Prioritize specific addresses for early delivery in the route.

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
  "start_time": "2024-12-21T08:00:00Z",
  "objective": "minimize_time|minimize_distance|minimize_cost",
  "priority_addresses": [
    {
      "address": "exact address string",
      "priority_level": "high|medium|low",
      "preferred_time_window": "early|middle|late"
    }
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
      }
    ]
  }
}
```

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| addresses | array | Yes | List of addresses to optimize (minimum 2 addresses). First = start point, last = end point, middle = optimized |
| **start_time** | string | **No** | **NEW:** Custom start time in ISO format (e.g., "2024-12-21T08:00:00Z"). If not provided, defaults to 23:00 today |
| **objective** | string | **No** | **NEW:** Optimization objective: "minimize_time" (default), "minimize_distance", or "minimize_cost" |
| **priority_addresses** | array | **No** | Array of priority address configurations |
| **priority_addresses[].address** | string | **Yes** | **Exact address string** from addresses array |
| **priority_addresses[].priority_level** | string | **Yes** | **Priority level:** "high", "medium", or "low" |
| **priority_addresses[].preferred_time_window** | string | **No** | **Preferred time window:** "early", "middle", or "late" |
| time_windows | object | No | Time windows configuration for soft/hard constraints |
| time_windows.enabled | boolean | No | Whether to enable time windows (default: false) |
| time_windows.windows | array | No | Array of time window configurations |

#### Start Time Configuration

**✨ NEW Feature**: Custom start time allows you to specify when the route should begin instead of the fixed 23:00 default.

**Format:** ISO 8601 datetime string with timezone (e.g., "2024-12-21T08:00:00Z")
**Default:** 23:00 today (if current time < 23:00) or 23:00 tomorrow (if current time >= 23:00)

**Examples:**
- `"start_time": "2024-12-21T08:00:00Z"` - Start at 8:00 AM UTC
- `"start_time": "2024-12-21T14:30:00+02:00"` - Start at 2:30 PM Central European Time
- `"start_time": "2024-12-21T09:15:00-05:00"` - Start at 9:15 AM Eastern Standard Time

#### Optimization Objectives

**✨ NEW Feature**: Choose the optimization goal to balance time, distance, and cost according to your business needs.

**Available Objectives:**
- **minimize_time** (default): Prioritizes shorter travel time, ideal for time-sensitive deliveries
- **minimize_distance**: Prioritizes shorter total distance, ideal for fuel cost reduction
- **minimize_cost**: Balanced approach between time and distance

**Cost Parameters by Objective:**
| Objective | Cost per Kilometer | Cost per Hour | Use Case |
|-----------|-------------------|---------------|----------|
| **minimize_time** | 1.0 (low) | 10.0 (high) | Time-sensitive deliveries, medical supplies |
| **minimize_distance** | 10.0 (high) | 0.1 (low) | Fuel cost optimization, long-distance routes |
| **minimize_cost** | 5.0 (medium) | 2.0 (medium) | Balanced efficiency, general logistics |

#### Priority Address Functionality

**Priority addresses allow you to prioritize specific addresses for early delivery in the route.**

**Priority Levels:**
- **high**: Delivers very early with strong cost penalties for delays
- **medium**: Delivers moderately early with medium cost penalties  
- **low**: Delivers somewhat early with light cost penalties

**Time Windows:**
- **early**: 23:00-01:00 (first 2 hours)
- **middle**: 01:00-03:00 (middle 2 hours)
- **late**: 03:00-05:00 (last 2 hours)

**Cost Penalties:**
- **High priority**: 0.5 cost before window, 100.0 cost after
- **Medium priority**: 2.0 cost before window, 50.0 cost after
- **Low priority**: 10.0 cost before window, 15.0 cost after

#### Response

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Route optimization completed successfully using Google Route Optimization API with objective: minimize_time",
  "algorithm": "Google Route Optimization API",
  "optimization_objective": "minimize_time",
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
    }
  },
  "timing_info": {
    "vehicle_start_time": "2024-12-20T23:00:00Z",
    "vehicle_end_time": "2024-12-21T02:30:00Z",
    "total_duration_seconds": 12600,
    "total_duration_minutes": 210.0,
    "total_duration_hours": 3.5,
    "service_time_per_stop_minutes": 3,
    "custom_start_time_used": true
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
    }
  ],
  "optimization_info": {
    "addresses_count": 4,
    "total_distance_meters": 45000,
    "total_distance_km": 45.0,
    "total_time_seconds": 12600,
    "total_time_minutes": 210.0,
    "total_time_hours": 3.5,
    "cost_per_kilometer": 1.0,
    "cost_per_hour": 10.0
  }
}
```

**Error Response (4xx/5xx):**
```json
{
  "success": false,
  "error": "Error description"
}
```

## Usage Examples

### Python with New Features

```python
import requests
import json
from datetime import datetime, timedelta

# Configuration - Production URL
API_URL = "https://items-routes-route-optimisation-dot-maibach-items-routes.ew.r.appspot.com/api/optimize"

# Request data with new features
data = {
    "addresses": [
        "Berlin Hauptbahnhof, Berlin, Germany",    # Start point (fixed)
        "Potsdamer Platz, Berlin, Germany",        # Customer 1 (optimized)
        "Brandenburg Gate, Berlin, Germany",        # Customer 2 (optimized)
        "Alexanderplatz, Berlin, Germany"          # End point (fixed)
    ],
    "start_time": "2024-12-21T08:00:00Z",          # NEW: Custom start time
    "objective": "minimize_distance",               # NEW: Optimization objective
    "priority_addresses": [
        {
            "address": "Brandenburg Gate, Berlin, Germany",
            "priority_level": "high",
            "preferred_time_window": "early"
        }
    ]
}

response = requests.post(API_URL, json=data, headers={'Content-Type': 'application/json'})

if response.status_code == 200:
    result = response.json()
    print("✅ Route optimization with new features successful!")
    print(f"Algorithm: {result['algorithm']}")
    print(f"Objective: {result['optimization_objective']}")
    print(f"Custom start time used: {result['timing_info']['custom_start_time_used']}")
    print(f"Total time: {result['timing_info']['total_duration_hours']} hours")
    print(f"Total distance: {result['optimization_info']['total_distance_km']} km")
    print(f"Cost parameters: {result['optimization_info']['cost_per_kilometer']}/km, {result['optimization_info']['cost_per_hour']}/hour")
    
    # Check priority address position
    priority_addr = "Brandenburg Gate, Berlin, Germany"
    for i, addr in enumerate(result['optimized_addresses']):
        if addr == priority_addr:
            print(f"🎯 Priority address '{priority_addr}' is at position {i+1}")
    
    # Detailed schedule
    print("\n📅 Detailed Schedule:")
    for stop in result['visit_schedule']:
        arrival = datetime.fromisoformat(stop['arrival_time'].replace('Z', '+00:00'))
        print(f"  {stop['stop_number']}. {stop['address']}")
        print(f"     🕐 Arrival: {arrival.strftime('%H:%M')} | Type: {stop['stop_type']}")
else:
    error = response.json()
    print(f"❌ Error: {error['error']}")
```

### Real-world Example (German Addresses)

```python
# Test with actual German addresses including new features
data = {
    "addresses": [
        "Neumarkter Str. 39, 90584 Allersberg, Deutschland",  # Start
        "Kolpingstraße 2, 90584 Allersberg, Deutschland",     # Customer 1
        "Dietkirchen 13, 92367 Pilsach, Deutschland",         # Customer 2
        "Lippacher Str. 1, 84095 Furth, Deutschland",         # Customer 3
        "Seelstraße 20, 92318 Neumarkt in der Oberpfalz, Deutschland"  # End
    ],
    "start_time": "2024-12-21T07:30:00Z",                     # Early morning start
    "objective": "minimize_cost",                             # Balanced optimization
    "priority_addresses": [
        {
            "address": "Lippacher Str. 1, 84095 Furth, Deutschland",
            "priority_level": "high",
            "preferred_time_window": "early"
        }
    ]
}

response = requests.post(API_URL, json=data, headers={'Content-Type': 'application/json'})

if response.status_code == 200:
    result = response.json()
    print("🎯 Full-featured optimization successful!")
    print(f"Optimization objective: {result['optimization_objective']}")
    print(f"Start time: {result['timing_info']['vehicle_start_time']}")
    
    # Check if priority address is in first half of route
    priority_addr = "Lippacher Str. 1, 84095 Furth, Deutschland"
    total_customers = len(result['optimized_addresses']) - 2  # Exclude start/end
    first_half_threshold = total_customers // 2
    
    for i, addr in enumerate(result['optimized_addresses']):
        if addr == priority_addr:
            customer_position = i - 1  # Adjust for start point
            if customer_position <= first_half_threshold:
                print(f"✅ Priority address delivered early: position {customer_position+1}/{total_customers}")
            else:
                print(f"⚠️ Priority address not in first half: position {customer_position+1}/{total_customers}")
```

### cURL Examples

**Basic optimization:**
```bash
curl -X POST https://items-routes-route-optimisation-dot-maibach-items-routes.ew.r.appspot.com/api/optimize \
  -H "Content-Type: application/json" \
  -d '{
    "addresses": [
      "Berlin, Germany",
      "Munich, Germany", 
      "Hamburg, Germany"
    ]
  }' | jq .
```

**With new features:**
```bash
curl -X POST https://items-routes-route-optimisation-dot-maibach-items-routes.ew.r.appspot.com/api/optimize \
  -H "Content-Type: application/json" \
  -d '{
    "addresses": [
      "Berlin Hauptbahnhof, Berlin, Germany",
      "Potsdamer Platz, Berlin, Germany",
      "Brandenburg Gate, Berlin, Germany", 
      "Alexanderplatz, Berlin, Germany"
    ],
    "start_time": "2024-12-21T08:00:00Z",
    "objective": "minimize_distance",
    "priority_addresses": [
      {
        "address": "Brandenburg Gate, Berlin, Germany",
        "priority_level": "high",
        "preferred_time_window": "early"
      }
    ]
  }' | jq '.optimized_addresses, .timing_info, .optimization_objective'
```

## Route Logic & Examples

### **Separate Start and End Points**

The API supports flexible routing with different start and end points:

#### **How it works:**
- **First address** in the array = **Fixed start point**
- **Last address** in the array = **Fixed end point**  
- **Middle addresses** = **Optimized for best route order**
- **Priority addresses** = **Prioritized for early delivery**

#### **Example scenarios:**

**Scenario 1: With priority address**
```json
{
  "addresses": [
    "Warehouse A, Berlin",         // Start point
    "Customer A, Munich",          // Optimized
    "Customer B, Hamburg",         // Optimized (High Priority)
    "Customer C, Dresden",         // Optimized
    "Warehouse B, Frankfurt"       // End point
  ],
  "priority_addresses": [
    {
      "address": "Customer B, Hamburg",
      "priority_level": "high",
      "preferred_time_window": "early"
    }
  ]
}
```
Result: `Warehouse A → Customer B (priority) → Customer A → Customer C → Warehouse B`

**Scenario 2: Multiple priorities**
```json
{
  "addresses": [
    "Distribution Center, Cologne",  // Start point
    "Customer 1, Düsseldorf",       // Medium Priority
    "Customer 2, Essen",            // High Priority
    "Customer 3, Dortmund",         // Low Priority
    "Customer 4, Bochum",           // Optimized
    "Return Center, Wuppertal"      // End point
  ],
  "priority_addresses": [
    {
      "address": "Customer 2, Essen",
      "priority_level": "high",
      "preferred_time_window": "early"
    },
    {
      "address": "Customer 1, Düsseldorf", 
      "priority_level": "medium",
      "preferred_time_window": "early"
    },
    {
      "address": "Customer 3, Dortmund",
      "priority_level": "low",
      "preferred_time_window": "middle"
    }
  ]
}
```

### **Business Use Cases:**

1. **Priority Deliveries** - Prioritize VIP customers or urgent orders
2. **Time-sensitive Deliveries** - Use minimize_time with early start times for medical supplies
3. **Cost Optimization** - Use minimize_cost or minimize_distance for fuel efficiency
4. **Service Level Agreements** - Combine custom start times with priority addresses
5. **Flexible Scheduling** - Configure start times for different shift patterns
6. **Multi-objective Routing** - Choose objectives based on daily operational goals

## Time Windows Support

### **Time Windows Types:**

#### **Hard Time Windows (Strict Constraints)**
- **Required compliance:** Vehicle MUST arrive within the specified time window
- **If violated:** The shipment is skipped entirely
- **Configuration:** Use `hard_start_time` and `hard_end_time`

#### **Soft Time Windows (Flexible Constraints)**
- **Preferred compliance:** Vehicle SHOULD arrive within the specified time window
- **If violated:** Additional cost is applied, but delivery still happens
- **Configuration:** Use `soft_start_time`, `soft_end_time`, and cost penalties

### **Priority Address Time Windows**

Priority addresses automatically generate time windows based on their priority level:

```json
{
  "addresses": ["Start", "Customer 1", "Customer 2", "End"],
  "priority_addresses": [
    {
      "address": "Customer 1",
      "priority_level": "high",
      "preferred_time_window": "early"
    }
  ]
}
```

**Automatic Time Window Generation:**
- **early**: 23:00-01:00 (first 2 hours of route)
- **middle**: 01:00-03:00 (middle 2 hours of route)  
- **late**: 03:00-05:00 (last 2 hours of route)

## Testing

### Quick Test (Production)

Test the health endpoint:
```bash
curl https://items-routes-route-optimisation-dot-maibach-items-routes.ew.r.appspot.com/health
```

Test route optimization with new features:
```bash
curl -X POST https://items-routes-route-optimisation-dot-maibach-items-routes.ew.r.appspot.com/api/optimize \
  -H "Content-Type: application/json" \
  -d '{
    "addresses": [
      "Berlin, Germany",
      "Munich, Germany", 
      "Hamburg, Germany"
    ],
    "start_time": "2024-12-21T09:00:00Z",
    "objective": "minimize_distance",
    "priority_addresses": [
      {
        "address": "Munich, Germany",
        "priority_level": "high",
        "preferred_time_window": "early"
      }
    ]
  }' | jq '.optimized_addresses, .optimization_objective, .timing_info.vehicle_start_time'
```

### ✅ Production-Tested with Enhanced Features

**Successfully tested with German addresses and all new functionality:**
```bash
curl -X POST https://items-routes-route-optimisation-dot-maibach-items-routes.ew.r.appspot.com/api/optimize \
  -H "Content-Type: application/json" \
  -d '{
    "addresses": [
      "Neumarkter Str. 39, 90584 Allersberg, Deutschland",
      "Kolpingstraße 2, 90584 Allersberg, Deutschland", 
      "Dietkirchen 13, 92367 Pilsach, Deutschland",
      "Lippacher Str. 1, 84095 Furth, Deutschland",
      "Seelstraße 20, 92318 Neumarkt in der Oberpfalz, Deutschland"
    ],
    "start_time": "2024-12-21T07:00:00Z",
    "objective": "minimize_cost",
    "priority_addresses": [
      {
        "address": "Lippacher Str. 1, 84095 Furth, Deutschland",
        "priority_level": "high",
        "preferred_time_window": "early"
      }
    ]
  }' | jq '.optimized_addresses, .timing_info, .optimization_objective'
```

**Verified Results:**
- ✅ **Custom start time** - Vehicle starts at configured 07:00 instead of default 23:00
- ✅ **Optimization objective** - Successfully applies minimize_cost strategy
- ✅ **Priority optimization** - Priority address positioned early in route
- ✅ **Detailed timing** - All timing calculations adjusted for custom start time
- ✅ **Cost parameters** - Applied cost structure: 5.0/km, 2.0/hour for balanced optimization
- ✅ **Complete integration** - All features work seamlessly together

## Error Handling

### Common Error Messages

| Error | Description | Solution |
|-------|-------------|----------|
| `Missing "addresses" field` | Addresses array not provided | Include addresses array in request |
| `At least 2 addresses are required` | Too few addresses | Provide minimum 2 addresses |
| `Invalid start_time format` | Malformed start_time string | Use ISO format like "2024-12-21T08:00:00Z" |
| `Invalid objective` | Invalid objective value | Use "minimize_time", "minimize_distance", or "minimize_cost" |
| `Priority address not found in addresses` | Priority address doesn't match any address | Ensure exact string match |
| `Invalid priority level` | Invalid priority_level value | Use "high", "medium", or "low" |
| `Invalid time window` | Invalid preferred_time_window | Use "early", "middle", or "late" |

### Address Format Best Practices

**✅ Recommended formats:**
```json
{
  "addresses": [
    "123 Main Street, New York, NY 10001, USA",
    "Alexanderplatz 1, 10178 Berlin, Germany",
    "1600 Pennsylvania Avenue NW, Washington, DC 20500, USA"
  ]
}
```

**❌ Avoid these formats:**
```json
{
  "addresses": [
    "Main St",           // Too vague
    "123",               // Incomplete  
    "Berlin"             // City only
  ]
}
```

## Production Deployment

**✅ Production-Ready API deployed and operational on Google Cloud App Engine!**

### Current Status

| Component | Status |
|-----------|--------|
| **Platform** | Google Cloud App Engine ✅ |
| **Service** | `items-routes-route-optimisation` ✅ |
| **Runtime** | Python 3.9 ✅ |
| **SSL/TLS** | HTTPS enforced ✅ |
| **Scaling** | Auto-scaling (max 5 instances) ✅ |
| **Priority Features** | Fully implemented ✅ |

### Health Monitoring

```bash
# Check service health
curl https://items-routes-route-optimisation-dot-maibach-items-routes.ew.r.appspot.com/health

# Expected response
{
  "status": "healthy",
  "service": "route-optimization-api", 
  "version": "2.1.0",
  "google_api_configured": true,
  "route_optimization_configured": true
}
```

## API Versioning

**Current Version: 2.3.0**

### Version History

- **2.3.0** - Removed arbitrary 25-address limit, now supports unlimited addresses
- **2.2.0** - Added custom start time and optimization objectives (minimize_time/distance/cost)
- **2.1.0** - Added priority address functionality
- **2.0.0** - Separate start/end points, time windows support
- **1.0.0** - Basic route optimization with depot-based routing

### Backward Compatibility

- All existing API calls continue to work without modification
- New parameters (start_time, objective) are optional - API uses defaults if not provided
- Priority addresses and time windows remain fully supported
- Response format enhanced with new fields but maintains backward compatibility
- Default behavior unchanged: starts at 23:00, minimizes time

---

**© 2025 Route Optimization API - Production Ready with Custom Start Time & Optimization Objectives** 