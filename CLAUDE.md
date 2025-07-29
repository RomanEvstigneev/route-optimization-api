# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a production-ready Flask API service for route optimization deployed on Google Cloud App Engine. It provides professional route optimization using Google's Route Optimization API with advanced features like priority addresses, custom start times, and flexible optimization objectives.

**Production URL:** `https://items-routes-route-optimisation-dot-maibach-items-routes.ew.r.appspot.com`

## Key Architecture Components

### Core Application (main.py)
- **Flask web application** with both web interface and REST API endpoints
- **Google Route Optimization API integration** for professional-grade route optimization
- **Geocoding functionality** to convert addresses to GPS coordinates
- **Separate start/end point support** with optimized intermediate stops
- **Priority address system** for early delivery prioritization
- **Time windows support** (both hard and soft constraints)
- **Custom optimization objectives** (minimize_time, minimize_distance, minimize_cost)

### API Endpoints
- `GET /health` - Health check and service status
- `GET /` - Web interface for manual route optimization
- `POST /api/optimize` - Main route optimization API endpoint
- `GET /example` - Download sample JSON file

### Key Features
- **Priority Addresses**: Prioritize specific addresses for early delivery with configurable priority levels (high/medium/low) and time windows (early/middle/late)
- **Custom Start Times**: Configure route start time instead of fixed 23:00 default
- **Optimization Objectives**: Choose between minimizing time, distance, or cost
- **Unlimited Address Support**: No longer limited to 25 addresses (removed in v2.3.0)
- **International Support**: Tested with Unicode addresses (German addresses with ü, ß, ä, ö)
- **Real-world Constraints**: Considers traffic, road conditions, vehicle limitations

## Development Commands

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GOOGLE_MAPS_API_KEY="your_google_maps_api_key"
export GOOGLE_CLOUD_PROJECT_ID="your_google_cloud_project_id"
export SECRET_KEY="your_secret_key"
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"  # Optional

# Run locally
python main.py
```

### Testing
```bash
# Run API tests
python test_api.py

# Run deployment tests  
python test_deployment.py

# Test priority functionality
python test_priority_address.py

# Test with German addresses
python test_german_addresses.py

# Test new features (start_time, objectives)
python test_new_features.py

# Test objectives specifically
python test_objectives.py
```

### Deployment
```bash
# Deploy to Google Cloud App Engine
./deploy.sh

# Or manually
gcloud app deploy --quiet

# View logs
gcloud app logs tail -s default
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GOOGLE_MAPS_API_KEY` | Yes | Google Maps API key for geocoding |
| `GOOGLE_CLOUD_PROJECT_ID` | Yes | Google Cloud Project ID for Route Optimization API |
| `SECRET_KEY` | Yes | Flask secret key for sessions |
| `GOOGLE_APPLICATION_CREDENTIALS` | No | Path to service account JSON (auto-detected on GCP) |

## Google Cloud APIs Required

Enable these APIs in your Google Cloud project:
- Route Optimization API
- Geocoding API  
- Maps Backend API

## Route Optimization Logic

### Address Processing
1. **First address** = Fixed start point
2. **Last address** = Fixed end point  
3. **Middle addresses** = Optimized for best route order
4. **Priority addresses** = Prioritized for early delivery using time windows

### Priority System
- **Priority Levels**: high, medium, low
- **Time Windows**: early (23:00-01:00), middle (01:00-03:00), late (03:00-05:00)
- **Cost Penalties**: Higher priority = stronger penalties for late delivery

### Optimization Objectives
- **minimize_time**: Fast delivery (cost: 1.0/km, 10.0/hour)
- **minimize_distance**: Fuel efficiency (cost: 10.0/km, 0.1/hour) 
- **minimize_cost**: Balanced approach (cost: 5.0/km, 2.0/hour)

## Code Architecture Notes

### Function Organization (main.py)
- **Route endpoints**: `index()`, `optimize()`, `api_optimize()`, `health_check()`
- **Geocoding**: `geocode_address()` - converts addresses to coordinates
- **Route optimization**: `optimize_route_with_api()` - main optimization logic using Google's API
- **Priority handling**: `create_priority_time_windows()` - converts priority configs to time windows
- **Time window creation**: `_create_time_window()` - formats time windows for API
- **Legacy functions**: `create_distance_matrix()`, `solve_tsp()` - kept for compatibility but not used with Route Optimization API

### Response Format
The API returns comprehensive route information including:
- Optimized address order with GPS coordinates
- Detailed timing information (arrival times, service durations)
- Route metrics (total time, distance, cost parameters)
- Visit schedule with stop-by-stop breakdown
- Transition details between stops

### Error Handling
- Input validation for addresses, priority configurations, time formats
- Google API error handling with detailed error messages
- Geocoding fallbacks and retry logic
- Comprehensive logging for debugging

## Testing Strategy

The repository includes extensive test coverage:
- **API functionality tests** (`test_api.py`)
- **Priority address tests** (`test_priority_*.py`)
- **International address tests** (`test_german_addresses.py`)
- **New feature tests** (`test_new_features.py`, `test_objectives.py`)
- **Time window tests** (`test_*_time_windows.py`)
- **Deployment validation** (`test_deployment.py`)

## Version Information

- **Current Version**: 2.3.0
- **Major Changes**: 
  - v2.3.0: Removed 25-address limit, unlimited addresses support
  - v2.2.0: Added custom start_time and optimization objectives  
  - v2.1.0: Added priority address functionality
  - v2.0.0: Separate start/end points, Google Route Optimization API integration

## Common Development Tasks

### Adding New Features
1. Update `main.py` with new functionality
2. Add corresponding tests in `test_*.py` files
3. Update API documentation in `API_DOCUMENTATION.md`
4. Test locally before deployment

### Debugging Issues
1. Check logs: `gcloud app logs tail -s default`
2. Test health endpoint: `curl /health`
3. Validate environment variables are set correctly
4. Use test files to isolate specific functionality

### Performance Optimization
- The app uses Google Route Optimization API which handles optimization efficiently
- Batching is handled automatically for large address sets
- Consider caching geocoding results for frequently used addresses
- Monitor Google Cloud quotas and API usage

## Production Deployment Notes

- Deployed on Google Cloud App Engine with auto-scaling (max 5 instances)
- Uses Gunicorn WSGI server with 2 workers, 4 threads
- HTTPS enforced for all endpoints
- Static files served with caching headers
- Health check endpoint available for monitoring