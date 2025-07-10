# Route Optimization API Documentation
**Version 2.0.0 | Last Updated: July 10, 2025**

## Overview

This API provides route optimization functionality for delivery routes, sales routes, and other multi-stop journeys. It uses Google's Route Optimization API for professional-grade optimization with real-world constraints and road conditions.

**🌐 Production API is live and ready for use!**  
**✅ Fully tested with real-world data (German addresses)**

**Key Features:**
- ✅ **Production Ready** - Deployed on Google Cloud App Engine
- ✅ **Scalable** - Auto-scaling up to 5 instances
- ✅ **Secure** - HTTPS enabled for all endpoints
- ✅ **Professional Optimization** - Uses Google Route Optimization API
- ✅ **Single API Call** - No multiple requests like traditional approaches
- ✅ **Real-world Constraints** - Considers traffic, road conditions, vehicle limitations
- ✅ **High Capacity** - Supports up to 100+ addresses (vs 10 with Distance Matrix)
- ✅ **International Support** - Tested with German addresses, supports Unicode
- ✅ **Auto-Geocoding** - Automatically converts addresses to coordinates
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

Optimizes the order of addresses to minimize total travel time.

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
  ]
}
```

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| addresses | array | Yes | List of addresses to optimize (2-25 addresses) |

#### Response

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Route optimization completed successfully using Google Route Optimization API",
  "original_addresses": [
    "Original address 1",
    "Original address 2",
    "..."
  ],
  "optimized_addresses": [
    "Optimized address 1",
    "Optimized address 2", 
    "...",
    "Original address 1"
  ],
  "route_indices": [0, 3, 1, 2, 0],
  "optimization_info": {
    "total_time_seconds": 3600,
    "total_time_minutes": 60.0,
    "total_time_hours": 1.0,
    "algorithm": "Google Route Optimization API",
    "addresses_count": 4
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

# Configuration - Production URL
API_URL = "https://items-routes-route-optimisation-dot-maibach-items-routes.ew.r.appspot.com/api/optimize"

# For local development, use:
# API_URL = "http://localhost:8080/api/optimize"

# Request data
data = {
    "addresses": [
        "New York, NY",
        "Philadelphia, PA", 
        "Boston, MA",
        "Washington, DC"
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
    print(f"Total time: {result['optimization_info']['total_time_minutes']} minutes")
    print("Optimized route:")
    for i, addr in enumerate(result['optimized_addresses'], 1):
        print(f"  {i}. {addr}")
else:
    error = response.json()
    print(f"Error: {error['error']}")
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
        'New York, NY',
        'Philadelphia, PA',
        'Boston, MA',
        'Washington, DC'
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
    console.log(`Total time: ${result.optimization_info.total_time_minutes} minutes`);
    console.log('Optimized route:');
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
  }'
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
  }'
```

## Rate Limiting

- The API is limited by Google Route Optimization API quotas
- Maximum 25 addresses per request (configurable up to 100+)
- Single API call per optimization (more efficient than traditional approaches)
- Recommended to implement client-side rate limiting for high-volume usage

## Authentication

Currently, no authentication is required. For production use, consider implementing:
- API key authentication
- IP whitelisting
- Rate limiting by IP/user

## Algorithm Details

The optimization uses **Google Route Optimization API** which provides:

### **Advanced Features:**
1. **Single API Call** - All optimization happens server-side at Google
2. **Real-world Constraints** - Considers actual traffic, road conditions, vehicle limitations
3. **Professional Algorithms** - Uses Google's production-grade optimization engine
4. **High Performance** - Optimized for large-scale routing problems
5. **Service Time Support** - Accounts for time spent at each location

### **Optimization Process:**
1. **Input Processing** - First address becomes depot/starting point
2. **Geocoding** - All addresses converted to GPS coordinates using Google Geocoding API
3. **Shipment Creation** - Each subsequent address becomes a pickup location
4. **Vehicle Definition** - Single vehicle starts and ends at depot
5. **Constraint Application** - Real-world driving constraints applied
6. **Route Optimization** - Google's algorithms find optimal sequence
7. **Result Parsing** - Optimized route with timing information returned

### **Advantages over Traditional TSP:**
- ✅ **No Distance Matrix Limits** - Handles 100+ addresses vs 10-25 limit
- ✅ **Real Traffic Data** - Uses current road conditions
- ✅ **Professional Grade** - Same engine used by Google Maps
- ✅ **Cost Effective** - Single API call vs multiple requests
- ✅ **Accurate Timing** - Includes service time and real driving speeds

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
  }'
```

### ✅ Tested with Real Data

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
  }'
```

**Response:** ✅ Optimization successful with 3.48 hours total time
**Route:** Optimized sequence minimizing travel time between locations

**International Support:**
- ✅ **German addresses** - Fully tested and working
- ✅ **Geocoding enabled** - Automatically converts addresses to coordinates
- ✅ **Real-world routing** - Uses actual road networks and traffic data
- ✅ **Unicode support** - Handles special characters (ü, ß, ä, ö, etc.)

### Local Testing

Use the provided test script to verify API functionality:

```bash
python test_api.py
```

## Production Deployment

**✅ This API is already deployed to Google Cloud App Engine!**

**Current Production Configuration:**
- **Platform:** Google Cloud App Engine
- **Runtime:** Python 3.9
- **WSGI Server:** Gunicorn (2 workers, 4 threads)
- **Scaling:** Basic scaling (max 5 instances)
- **SSL/TLS:** ✅ Enabled (all traffic secure)
- **Monitoring:** Health check endpoint at `/health`

**Additional Production Considerations:**
1. ✅ **Production WSGI server** - Gunicorn configured
2. **Logging** - Available via `gcloud app logs tail`
3. **Authentication** - Consider implementing API keys
4. **Caching** - Consider Redis for optimization results
5. **Error Handling** - Comprehensive error responses implemented
6. **Rate Limiting** - Consider implementing per-IP limits
7. ✅ **SSL/TLS** - Automatically provided by App Engine

**Monitoring & Logs:**
```bash
# View live logs
gcloud app logs tail -s items-routes-route-optimisation

# Check service status
gcloud app services describe items-routes-route-optimisation
```

## Support

For issues or questions:

**Production Issues:**
- Check logs: `gcloud app logs tail -s items-routes-route-optimisation`
- Monitor health: `curl https://items-routes-route-optimisation-dot-maibach-items-routes.ew.r.appspot.com/health`
- Service status: `gcloud app services describe items-routes-route-optimisation`

**Common Troubleshooting:**
- Verify Google Maps API key configuration
- Ensure all addresses are valid and geocodable
- Test with fewer addresses if timeouts occur (max 25 addresses)
- Check that addresses are in English or include country codes

**Web Interface:**
- Access at: https://items-routes-route-optimisation-dot-maibach-items-routes.ew.r.appspot.com
- Upload JSON file with addresses array
- Download example file from `/example` endpoint 