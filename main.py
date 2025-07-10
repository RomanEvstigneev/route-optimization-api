from flask import Flask, render_template, request, redirect, url_for, send_file, flash, jsonify
import requests
import json
import os
import logging
from datetime import datetime
from ortools.constraint_solver import routing_enums_pb2, pywrapcp
from google.maps import routeoptimization_v1 as ro
from google.auth import default
from google.oauth2 import service_account

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY')
GOOGLE_CLOUD_PROJECT_ID = os.environ.get('GOOGLE_CLOUD_PROJECT_ID')

# Initialize Route Optimization client
SERVICE_ACCOUNT_FILE = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
if SERVICE_ACCOUNT_FILE:
    credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE)
else:
    # Use default credentials (for Google Cloud environments like App Engine)
    credentials, project = default()

# Initialize the Route Optimization client
route_client = ro.RouteOptimizationClient(credentials=credentials)

# Health check endpoint for monitoring
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for App Engine monitoring"""
    return jsonify({
        'status': 'healthy',
        'service': 'route-optimization-api',
        'version': '2.0.0',
        'google_api_configured': bool(GOOGLE_MAPS_API_KEY),
        'route_optimization_configured': bool(GOOGLE_CLOUD_PROJECT_ID),
        'api_type': 'Route Optimization API with Geocoding',
        'geocoding_enabled': True
    }), 200

# Главная страница с формой загрузки
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

# Скачивание примера JSON
@app.route('/example', methods=['GET'])
def download_example():
    return send_file('static/example.json', as_attachment=True)

# Обработка загруженного файла и отображение результата
@app.route('/optimize', methods=['POST'])
def optimize():
    file = request.files.get('file')
    if not file:
        flash('No file uploaded')
        return redirect(url_for('index'))
    try:
        data = json.load(file)
        addresses = data.get('addresses')
        if not addresses or not isinstance(addresses, list) or len(addresses) < 2:
            flash('Invalid JSON format. "addresses" must be a list of at least 2 addresses.')
            return redirect(url_for('index'))
        
        if len(addresses) > 25:
            flash('Maximum 25 addresses allowed')
            return redirect(url_for('index'))
    except Exception as e:
        flash(f'Error reading JSON: {e}')
        return redirect(url_for('index'))

    if not GOOGLE_MAPS_API_KEY:
        flash('Google Maps API key is not set.')
        return redirect(url_for('index'))

    try:
        # Use Route Optimization API for better results
        route_info = optimize_route_with_api(addresses)
        
        if not route_info:
            flash("Could not find an optimal route.")
            return redirect(url_for('index'))
            
        return render_template('result.html', route=route_info)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        flash(f'Error processing route: {e}')
        return redirect(url_for('index'))

@app.route('/api/optimize', methods=['POST'])
def api_optimize():
    """
    API endpoint for route optimization
    Accepts JSON with addresses list and returns optimized route
    
    Expected JSON format:
    {
        "addresses": [
            "Address 1",
            "Address 2",
            "Address 3"
        ]
    }
    
    Returns JSON with optimized route
    """
    try:
        # Check if request contains JSON data
        if not request.is_json:
            return jsonify({
                'error': 'Content-Type must be application/json',
                'success': False
            }), 400
        
        data = request.get_json()
        
        # Validate input data
        if not data or 'addresses' not in data:
            return jsonify({
                'error': 'Missing "addresses" field in JSON',
                'success': False
            }), 400
        
        addresses = data['addresses']
        
        # Validate addresses
        if not isinstance(addresses, list):
            return jsonify({
                'error': 'Addresses must be a list',
                'success': False
            }), 400
        
        if len(addresses) < 2:
            return jsonify({
                'error': 'At least 2 addresses are required',
                'success': False
            }), 400
        
        if len(addresses) > 25:
            return jsonify({
                'error': 'Maximum 25 addresses allowed',
                'success': False
            }), 400
        
        # Check if Google Maps API key is set
        if not GOOGLE_MAPS_API_KEY:
            return jsonify({
                'error': 'Google Maps API key is not configured',
                'success': False
            }), 500
        
        # Perform route optimization
        logger.info(f"API request received - optimizing route for {len(addresses)} addresses")
        logger.info(f"Addresses: {addresses[:3]}{'...' if len(addresses) > 3 else ''}")  # Log first 3 addresses
        
        # Use Route Optimization API
        route_info = optimize_route_with_api(addresses)
        
        if not route_info:
            return jsonify({
                'error': 'Could not find optimal route',
                'success': False
            }), 500
        
        # Prepare response
        response_data = {
            'success': True,
            'original_addresses': addresses,
            'optimized_addresses': route_info['optimized_addresses'],
            'route_indices': route_info['route_indices'],
            'optimization_info': {
                'total_time_seconds': route_info['total_distance_seconds'],
                'total_time_minutes': route_info['total_distance_minutes'],
                'total_time_hours': round(route_info['total_distance_seconds'] / 3600, 2),
                'algorithm': route_info['algorithm'],
                'addresses_count': len(addresses)
            },
            'message': route_info['message']
        }
        
        logger.info(f"API response - optimization successful, total time: {route_info['total_distance_seconds']}s")
        
        return jsonify(response_data), 200
        
    except Exception as e:
        import traceback
        logger.error(f"API optimization failed: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        return jsonify({
            'error': f'Internal server error: {str(e)}',
            'success': False
        }), 500

def create_distance_matrix(addresses):
    """
    Create distance matrix using Google Maps Distance Matrix API with batching support.
    For large number of addresses, splits requests into smaller batches to avoid API limits.
    """
    num_addresses = len(addresses)
    
    # Initialize matrices
    matrix = [[0] * num_addresses for _ in range(num_addresses)]
    time_matrix = [[0] * num_addresses for _ in range(num_addresses)]
    
    # Maximum addresses per batch (10x10 = 100 elements, which is the API limit)
    MAX_BATCH_SIZE = 10
    
    if num_addresses <= MAX_BATCH_SIZE:
        # Single request for small number of addresses
        print(f"DEBUG: Single request for {num_addresses} addresses")
        return _create_distance_matrix_single(addresses)
    else:
        # Multiple requests for large number of addresses
        print(f"DEBUG: Batching {num_addresses} addresses into multiple requests")
        
        # Create batches
        batches = []
        for i in range(0, num_addresses, MAX_BATCH_SIZE):
            batch = addresses[i:i + MAX_BATCH_SIZE]
            batches.append(batch)
        
        print(f"DEBUG: Created {len(batches)} batches")
        
        # Process each batch combination
        for i, origins_batch in enumerate(batches):
            for j, destinations_batch in enumerate(batches):
                print(f"DEBUG: Processing batch {i}->{j}")
                
                # Get distance matrix for this batch combination
                batch_matrix, batch_time_matrix = _create_distance_matrix_batch(origins_batch, destinations_batch)
                
                # Insert batch results into main matrix
                origins_start = i * MAX_BATCH_SIZE
                origins_end = min(origins_start + len(origins_batch), num_addresses)
                destinations_start = j * MAX_BATCH_SIZE
                destinations_end = min(destinations_start + len(destinations_batch), num_addresses)
                
                for oi, origin_idx in enumerate(range(origins_start, origins_end)):
                    for di, dest_idx in enumerate(range(destinations_start, destinations_end)):
                        if oi < len(batch_matrix) and di < len(batch_matrix[0]):
                            matrix[origin_idx][dest_idx] = batch_matrix[oi][di]
                            time_matrix[origin_idx][dest_idx] = batch_time_matrix[oi][di]
        
        print(f"DEBUG: Completed batching for {num_addresses} addresses")
        return matrix, time_matrix

def _create_distance_matrix_single(addresses):
    """Single Distance Matrix API request for small number of addresses"""
    return _create_distance_matrix_batch(addresses, addresses)

def _create_distance_matrix_batch(origins, destinations):
    """Make a single Distance Matrix API request for a batch of origins and destinations"""
    url = "https://maps.googleapis.com/maps/api/distancematrix/json"
    params = {
        'origins': '|'.join(origins),
        'destinations': '|'.join(destinations),
        'mode': 'driving',
        'language': 'en',
        'avoid': 'tolls',
        'key': GOOGLE_MAPS_API_KEY
    }
    
    print(f"DEBUG: Distance Matrix API request - {len(origins)} origins, {len(destinations)} destinations")
    response = requests.get(url, params=params)
    print(f"DEBUG: Distance Matrix API response status: {response.status_code}")
    
    if response.status_code != 200:
        raise Exception(f"Google API Error (Distance Matrix): Status {response.status_code}, Response: {response.text}")
    
    try:
        result = response.json()
    except ValueError:  # json.JSONDecodeError is a subclass of ValueError
        raise Exception(f"Failed to decode JSON from Google API (Distance Matrix). Response: {response.text}")
    
    if result['status'] != 'OK':
        if result['status'] == 'MAX_ELEMENTS_EXCEEDED':
            raise Exception(f"Too many addresses in batch! Origins: {len(origins)}, Destinations: {len(destinations)}, Elements: {len(origins)*len(destinations)}")
        else:
            raise Exception(f"Google API returned error status: {result['status']}")
    
    if 'rows' not in result:
        raise Exception("API response does not contain 'rows' field")
    
    # Initialize matrices for this batch
    batch_matrix = [[0] * len(destinations) for _ in range(len(origins))]
    batch_time_matrix = [[0] * len(destinations) for _ in range(len(origins))]
    
    # Parse the Distance Matrix API response
    for i, row in enumerate(result['rows']):
        for j, element in enumerate(row['elements']):
            if element['status'] != 'OK':
                print(f"Warning: Route not available from {i} to {j}")
                # Use a large value to indicate unavailable route
                batch_matrix[i][j] = 999999
                batch_time_matrix[i][j] = 999999
                continue
                
            duration_val = element['duration']['value']  # in seconds
            distance_val = element['distance']['value']  # in meters
            
            # Use duration for optimization (can be changed to distance if needed)
            batch_matrix[i][j] = duration_val
            batch_time_matrix[i][j] = duration_val
    
    return batch_matrix, batch_time_matrix

def solve_tsp(matrix):
    num_locations = len(matrix)
    manager = pywrapcp.RoutingIndexManager(num_locations, 1, 0)
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return matrix[from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
    
    # Enhanced search parameters for better optimization
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )
    # Add local search metaheuristic for better solutions
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    )
    # Set time limit for optimization (30 seconds)
    search_parameters.time_limit.seconds = 30
    
    solution = routing.SolveWithParameters(search_parameters)
    
    if solution:
        index = routing.Start(0)
        optimized_indices = []
        route_distance = 0
        
        while not routing.IsEnd(index):
            optimized_indices.append(manager.IndexToNode(index))
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(previous_index, index, 0)
        
        # Add the last node (should be the depot/start point for TSP)
        optimized_indices.append(manager.IndexToNode(index))
        
        print(f"DEBUG: TSP solution found with total distance: {route_distance}")
        print(f"DEBUG: Optimized route indices: {optimized_indices}")
        
        return optimized_indices, route_distance
    else:
        print("ERROR: No solution found for TSP")
        return None, 0

def get_optimized_route_details(optimized_addresses):
    # Use the classic Directions API instead of Routes API v2 for better compatibility
    url = 'https://maps.googleapis.com/maps/api/directions/json'
    
    if len(optimized_addresses) < 2:
        raise Exception("Need at least 2 addresses for route calculation")
    
    origin = optimized_addresses[0]
    destination = optimized_addresses[-1]
    intermediates = optimized_addresses[1:-1]
    
    params = {
        'origin': origin,
        'destination': destination,
        'mode': 'driving',
        'language': 'en',
        'avoid': 'tolls',
        'key': GOOGLE_MAPS_API_KEY
    }
    
    # Add waypoints if there are intermediate addresses
    if intermediates:
        waypoints = '|'.join(intermediates)
        params['waypoints'] = f'optimize:true|{waypoints}'
    
    print("DEBUG: Directions API request URL:", url)
    print("DEBUG: Directions API request params:", params)
    
    response = requests.get(url, params=params)
    print("DEBUG: Directions API response status:", response.status_code)
    print("DEBUG: Directions API response text:", response.text[:500] + "..." if len(response.text) > 500 else response.text)

    if response.status_code != 200:
        raise Exception(f"Google API Error (Directions): Status {response.status_code}, Response: {response.text}")

    try:
        result = response.json()
    except ValueError:  # json.JSONDecodeError is a subclass of ValueError
        raise Exception(f"Failed to decode JSON from Google API (Directions). Response: {response.text}")

    if result['status'] != 'OK':
        raise Exception(f"Google Directions API returned error status: {result['status']}")

    if 'routes' not in result or not result['routes']:
        raise Exception("No routes found in the response")
        
    route = result['routes'][0]  # Get the first (and usually only) route
    
    total_distance = 0
    total_duration = 0
    
    for leg in route['legs']:
        total_distance += leg['distance']['value']  # in meters
        total_duration += leg['duration']['value']  # in seconds
            
    return {
        'total_distance_meters': total_distance,
        'total_duration_seconds': total_duration,
        'total_distance_km': round(total_distance / 1000, 2),
        'total_duration_minutes': round(total_duration / 60, 2),
        'total_duration_hours': round(total_duration / 3600, 2),
        'route_details': route
    }

def geocode_address(address):
    """
    Convert address to coordinates using Google Geocoding API.
    """
    try:
        import urllib.parse
        
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            'address': address,
            'key': GOOGLE_MAPS_API_KEY
        }
        
        logger.info(f"Geocoding address: {address}")
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'OK' and data['results']:
                location = data['results'][0]['geometry']['location']
                logger.info(f"Geocoded successfully: {address} -> {location['lat']}, {location['lng']}")
                return location['lat'], location['lng']
            else:
                logger.error(f"Geocoding API returned status: {data.get('status', 'UNKNOWN')} for address: {address}")
        else:
            logger.error(f"Geocoding API request failed with status {response.status_code} for address: {address}")
        
        return None, None
        
    except Exception as e:
        logger.error(f"Geocoding error for {address}: {str(e)}")
        return None, None


def optimize_route_with_api(addresses):
    """
    Use Google Route Optimization API to find the optimal route.
    This is more efficient than the old approach with multiple API calls.
    """
    if not GOOGLE_CLOUD_PROJECT_ID:
        raise Exception("Google Cloud Project ID is not configured")
    
    try:
        # First, geocode all addresses to get coordinates
        logger.info("Geocoding addresses to coordinates...")
        coordinates = []
        for address in addresses:
            lat, lng = geocode_address(address)
            if lat is None or lng is None:
                raise Exception(f"Failed to geocode address: {address}")
            coordinates.append((lat, lng))
        
        # Get depot coordinates (first address)
        depot_lat, depot_lng = coordinates[0]
        
        # Create shipments for each address (except the first one which is the depot)
        # Each shipment represents a visit to the location (pickup only)
        shipments = []
        for i, (lat, lng) in enumerate(coordinates[1:], 1):  # Skip depot
            shipment = {
                "pickups": [
                    {
                        "arrival_location": {
                            "latitude": lat,
                            "longitude": lng
                        }
                    }
                ]
                # No deliveries - just visit the location
            }
            shipments.append(shipment)
        
        # Create vehicle starting and ending at the depot
        vehicle = {
            "start_location": {
                "latitude": depot_lat,
                "longitude": depot_lng
            },
            "end_location": {
                "latitude": depot_lat,
                "longitude": depot_lng
            },
            "cost_per_kilometer": 1.0
        }
        
        # Create the optimization request (Python API uses snake_case)
        request = ro.OptimizeToursRequest(
            parent=f"projects/{GOOGLE_CLOUD_PROJECT_ID}",
            model={
                "shipments": shipments,
                "vehicles": [vehicle],
                "global_start_time": "2024-01-01T00:00:00Z",
                "global_end_time": "2024-01-01T23:59:59Z"
            }
        )
        
        # Initialize Route Optimization client
        credentials, project = default()
        route_client = ro.RouteOptimizationClient(credentials=credentials)
        
        logger.info(f"Sending request to Route Optimization API for {len(addresses)} addresses")
        response = route_client.optimize_tours(request=request)
        
        if not response.routes:
            logger.error("No routes found in optimization response")
            return None
            
        # Parse the response
        route = response.routes[0]
        visits = route.visits
        
        # Build the optimized address list
        optimized_addresses = [addresses[0]]  # Start with depot
        route_indices = [0]  # Start with depot index
        
        logger.info(f"Processing {len(visits)} visits from Route Optimization API")
        for visit in visits:
            # Find which shipment this visit corresponds to
            shipment_index = visit.shipment_index
            address_index = shipment_index + 1  # +1 because we skipped depot
            if address_index < len(addresses):  # Safety check
                optimized_addresses.append(addresses[address_index])
                route_indices.append(address_index)
        
        # Add return to depot
        optimized_addresses.append(addresses[0])
        route_indices.append(0)
        
        # Calculate total duration
        total_duration = 0
        if hasattr(route, 'metrics'):
            total_duration = route.metrics.total_duration.seconds
        
        logger.info(f"Route Optimization API completed successfully")
        logger.info(f"Optimized route indices: {route_indices}")
        logger.info(f"Total duration: {total_duration} seconds ({round(total_duration/60, 2)} minutes)")
        
        return {
            'optimized_addresses': optimized_addresses,
            'total_distance_seconds': total_duration,
            'total_distance_minutes': round(total_duration / 60, 2),
            'message': 'Route optimization completed successfully using Google Route Optimization API',
            'algorithm': 'Google Route Optimization API',
            'route_indices': route_indices,
            'original_addresses': addresses
        }
        
    except Exception as e:
        logger.error(f"Route Optimization API failed: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return None

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True) 