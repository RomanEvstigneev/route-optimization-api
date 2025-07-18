from flask import Flask, render_template, request, redirect, url_for, send_file, flash, jsonify
import requests
import json
import os
import logging
from datetime import datetime, timedelta
import pytz
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
            flash('Invalid JSON format. "addresses" must be a list of at least 2 addresses (start and end points).')
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
                'error': 'At least 2 addresses are required (start and end points)',
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
        
        # Extract optional time windows configuration
        time_windows_config = data.get('time_windows', None)
        
        # Extract optional priority addresses configuration
        priority_addresses_config = data.get('priority_addresses', None)
        
        # Extract optional start time configuration
        start_time_config = data.get('start_time', None)
        
        # Extract optional optimization objective configuration
        objective_config = data.get('objective', None)
        
        # Perform route optimization
        logger.info(f"API request received - optimizing route for {len(addresses)} addresses")
        logger.info(f"Addresses: {addresses[:3]}{'...' if len(addresses) > 3 else ''}")  # Log first 3 addresses
        
        if time_windows_config:
            logger.info(f"Time windows configuration provided: {len(time_windows_config)} entries")
        
        if priority_addresses_config:
            logger.info(f"Priority addresses configuration provided: {len(priority_addresses_config)} entries")
        
        if start_time_config:
            logger.info(f"Custom start time provided: {start_time_config}")
        
        if objective_config:
            logger.info(f"Optimization objective provided: {objective_config}")
        
        # Use Route Optimization API
        route_info = optimize_route_with_api(addresses, time_windows_config, priority_addresses_config, start_time_config, objective_config)
        
        if not route_info:
            return jsonify({
                'error': 'Could not find optimal route',
                'success': False
            }), 500
        
        # Prepare enhanced response with timing details
        response_data = route_info  # Use the complete response from optimize_route_with_api
        
        logger.info(f"API response - optimization successful with timing details")
        if 'timing_info' in route_info:
            logger.info(f"Vehicle starts at: {route_info['timing_info']['vehicle_start_time']}")
            logger.info(f"Vehicle ends at: {route_info['timing_info']['vehicle_end_time']}")
            logger.info(f"Total time: {route_info['timing_info']['total_duration_minutes']} minutes")
        
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


def _create_time_window(window_config):
    """
    Create a time window configuration for Google Route Optimization API.
    Supports both hard and soft time windows.
    
    Args:
        window_config: Dictionary containing time window configuration:
            - soft_start_time: ISO string for soft start time
            - soft_end_time: ISO string for soft end time  
            - hard_start_time: ISO string for hard start time
            - hard_end_time: ISO string for hard end time
            - cost_per_hour_before: Cost per hour for arriving before soft start
            - cost_per_hour_after: Cost per hour for arriving after soft end
    
    Returns:
        Dictionary containing time window configuration for API request
    """
    time_window = {}
    
    # Hard time windows (strict constraints)
    if window_config.get('hard_start_time'):
        time_window['startTime'] = window_config['hard_start_time']
    if window_config.get('hard_end_time'):
        time_window['endTime'] = window_config['hard_end_time']
    
    # Soft time windows (flexible constraints with costs)
    if window_config.get('soft_start_time'):
        time_window['softStartTime'] = window_config['soft_start_time']
        if window_config.get('cost_per_hour_before'):
            time_window['costPerHourBeforeSoftStartTime'] = window_config['cost_per_hour_before']
    
    if window_config.get('soft_end_time'):
        time_window['softEndTime'] = window_config['soft_end_time']
        if window_config.get('cost_per_hour_after'):
            time_window['costPerHourAfterSoftEndTime'] = window_config['cost_per_hour_after']
    
    return time_window


def create_priority_time_windows(addresses, priority_addresses_config, base_start_time):
    """
    Create time windows configuration for priority addresses.
    
    Args:
        addresses: List of all addresses
        priority_addresses_config: List of priority address configurations
        base_start_time: Base start time for route (datetime object)
    
    Returns:
        Dictionary containing time windows configuration for priority addresses
    """
    if not priority_addresses_config:
        return None
    
    time_windows = []
    
    for priority_config in priority_addresses_config:
        priority_address = priority_config.get('address')
        priority_level = priority_config.get('priority_level', 'medium')
        preferred_time_window = priority_config.get('preferred_time_window', 'early')
        
        # Find the index of the priority address in the addresses list
        address_index = None
        for i, addr in enumerate(addresses):
            if addr == priority_address:
                address_index = i
                break
        
        if address_index is None:
            logger.warning(f"Priority address not found in addresses list: {priority_address}")
            continue
        
        # Skip if it's start or end point (they are already fixed)
        if address_index == 0 or address_index == len(addresses) - 1:
            logger.warning(f"Cannot prioritize start or end point: {priority_address}")
            continue
        
        # Create time window based on priority level and preferred time
        if preferred_time_window == 'early':
            # Early delivery preference (23:00 - 01:00)
            soft_start_time = base_start_time
            soft_end_time = base_start_time + timedelta(hours=2)
        elif preferred_time_window == 'middle':
            # Middle delivery preference (01:00 - 03:00)
            soft_start_time = base_start_time + timedelta(hours=2)
            soft_end_time = base_start_time + timedelta(hours=4)
        else:  # late
            # Late delivery preference (03:00 - 05:00)
            soft_start_time = base_start_time + timedelta(hours=4)
            soft_end_time = base_start_time + timedelta(hours=6)
        
        # Set costs based on priority level
        if priority_level == 'high':
            cost_per_hour_before = 0.5   # Very low cost for early arrival
            cost_per_hour_after = 100.0  # Very high cost for late arrival
        elif priority_level == 'medium':
            cost_per_hour_before = 2.0   # Low cost for early arrival
            cost_per_hour_after = 50.0   # High cost for late arrival
        else:  # low
            cost_per_hour_before = 10.0  # Higher cost for early arrival
            cost_per_hour_after = 15.0   # Moderate cost for late arrival
        
        time_window_config = {
            'address_index': address_index,
            'soft_start_time': soft_start_time.isoformat().replace('+00:00', 'Z'),
            'soft_end_time': soft_end_time.isoformat().replace('+00:00', 'Z'),
            'cost_per_hour_before': cost_per_hour_before,
            'cost_per_hour_after': cost_per_hour_after
        }
        
        time_windows.append(time_window_config)
        logger.info(f"Created priority time window for {priority_address} (index {address_index}): {preferred_time_window} priority with level {priority_level}")
    
    return {
        'enabled': True,
        'windows': time_windows
    }


def optimize_route_with_api(addresses, time_windows_config=None, priority_addresses_config=None, start_time_config=None, objective_config=None):
    """
    Use Google Route Optimization API to find the optimal route.
    Enhanced with configurable timing and optimization objectives.
    
    Args:
        addresses: List of addresses to optimize
        time_windows_config: Optional configuration for time windows.
                           If provided, enables soft time windows support.
                           Format: {
                               'enabled': True,
                               'windows': [
                                   {
                                       'address_index': 1,
                                       'soft_start_time': '2024-01-01T10:00:00Z',
                                       'soft_end_time': '2024-01-01T14:00:00Z',
                                       'cost_per_hour_before': 10.0,
                                       'cost_per_hour_after': 5.0
                                   }
                               ]
                           }
        priority_addresses_config: Optional configuration for priority addresses.
                                 If provided, creates time windows to prioritize specific addresses.
                                 Format: [
                                     {
                                         'address': 'Exact address string',
                                         'priority_level': 'high|medium|low',
                                         'preferred_time_window': 'early|middle|late'
                                     }
                                 ]
        start_time_config: Optional custom start time in ISO format (e.g., '2024-12-21T08:00:00Z').
                          If not provided, defaults to 23:00 today.
        objective_config: Optional optimization objective ('minimize_time', 'minimize_distance', 'minimize_cost').
                         If not provided, defaults to 'minimize_time'.
    """
    if not GOOGLE_CLOUD_PROJECT_ID:
        raise Exception("Google Cloud Project ID is not configured")
    
    try:
        # Calculate start and end times
        if start_time_config:
            # Parse custom start time
            try:
                from dateutil.parser import parse
                start_time = parse(start_time_config)
                # Ensure timezone is UTC
                if start_time.tzinfo is None:
                    start_time = start_time.replace(tzinfo=pytz.UTC)
                else:
                    start_time = start_time.astimezone(pytz.UTC)
                logger.info(f"Using custom start time: {start_time}")
            except Exception as e:
                logger.error(f"Invalid start_time format '{start_time_config}': {e}")
                raise Exception(f"Invalid start_time format. Expected ISO format like '2024-12-21T08:00:00Z'")
        else:
            # Default behavior: start at 23:00 today
            today = datetime.now(pytz.UTC)
            start_time = today.replace(hour=23, minute=0, second=0, microsecond=0)
            
            # If current time is past 23:00, use tomorrow 23:00
            if today.hour >= 23:
                start_time = start_time + timedelta(days=1)
            
        # Set end time to 24 hours later
        end_time = start_time + timedelta(hours=24)
        
        # Configure optimization objective
        if objective_config:
            if objective_config not in ['minimize_time', 'minimize_distance', 'minimize_cost']:
                raise Exception(f"Invalid objective '{objective_config}'. Must be 'minimize_time', 'minimize_distance', or 'minimize_cost'")
            optimization_objective = objective_config
        else:
            optimization_objective = 'minimize_time'  # Default
        
        logger.info(f"Optimization objective: {optimization_objective}")
        
        # Set cost parameters based on objective
        if optimization_objective == 'minimize_distance':
            cost_per_kilometer = 10.0  # High cost for distance
            cost_per_hour = 0.1       # Low cost for time
        elif optimization_objective == 'minimize_cost':
            cost_per_kilometer = 5.0   # Medium cost for distance
            cost_per_hour = 2.0       # Medium cost for time
        else:  # minimize_time (default)
            cost_per_kilometer = 1.0   # Low cost for distance
            cost_per_hour = 10.0      # High cost for time
        
        start_time_str = start_time.isoformat().replace('+00:00', 'Z')
        end_time_str = end_time.isoformat().replace('+00:00', 'Z')
        
        logger.info(f"Route planning: Start at {start_time_str}, End by {end_time_str}")
        logger.info(f"Cost parameters: {cost_per_kilometer}/km, {cost_per_hour}/hour")
        
        # Handle priority addresses by creating time windows
        if priority_addresses_config:
            priority_time_windows = create_priority_time_windows(addresses, priority_addresses_config, start_time)
            if priority_time_windows:
                if time_windows_config:
                    # Merge with existing time windows
                    if 'windows' in time_windows_config:
                        time_windows_config['windows'].extend(priority_time_windows['windows'])
                    else:
                        time_windows_config['windows'] = priority_time_windows['windows']
                    time_windows_config['enabled'] = True
                else:
                    # Use priority time windows as the main time windows config
                    time_windows_config = priority_time_windows
                
                logger.info(f"Applied priority time windows for {len(priority_addresses_config)} addresses")
        
        # First, geocode all addresses to get coordinates
        logger.info("Geocoding addresses to coordinates...")
        coordinates = []
        coordinates_dict = {}  # Store coordinates for API response
        for address in addresses:
            lat, lng = geocode_address(address)
            if lat is None or lng is None:
                raise Exception(f"Failed to geocode address: {address}")
            coordinates.append((lat, lng))
            coordinates_dict[address] = {'latitude': lat, 'longitude': lng}
        
        # Get start and end coordinates
        start_lat, start_lng = coordinates[0]  # First address is start point
        end_lat, end_lng = coordinates[-1]     # Last address is end point
        
        # Create shipments for each address (except the first and last which are start/end points)
        # Each shipment represents a visit to the location (pickup only) with 3 minutes service time
        shipments = []
        customer_coordinates = coordinates[1:-1]  # Skip start and end points
        for i, (lat, lng) in enumerate(customer_coordinates, 1):  # Customer addresses only
            pickup_request = {
                "arrival_location": {
                    "latitude": lat,
                    "longitude": lng
                },
                "duration": "180s"  # 3 minutes service time per stop
            }
            
            # Add time windows if configured
            if time_windows_config and time_windows_config.get('enabled', False):
                time_windows = time_windows_config.get('windows', [])
                # Find time window for this address
                # i is 1-based customer index, original address index is i (since customers start from index 1)
                original_address_index = i  # Customer index in original addresses array
                for window in time_windows:
                    window_address_index = window.get('address_index')
                    if window_address_index == original_address_index:
                        pickup_request["time_windows"] = [_create_time_window(window)]
                        logger.info(f"Applied time window to customer address {original_address_index} (customer #{i}): {window}")
                        break
            
            shipment = {
                "pickups": [pickup_request]
                # No deliveries - just visit the location
            }
            shipments.append(shipment)
        
        # Create vehicle with separate start and end locations
        vehicle = {
            "start_location": {
                "latitude": start_lat,
                "longitude": start_lng
            },
            "end_location": {
                "latitude": end_lat,
                "longitude": end_lng
            },
            "cost_per_kilometer": cost_per_kilometer
        }
        
        # Create the optimization request with calculated times (Python API uses snake_case)
        request = ro.OptimizeToursRequest(
            parent=f"projects/{GOOGLE_CLOUD_PROJECT_ID}",
            model={
                "shipments": shipments,
                "vehicles": [vehicle],
                "global_start_time": start_time_str,
                "global_end_time": end_time_str
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
            
        # Parse the response with detailed timing information
        route = response.routes[0]
        visits = route.visits
        transitions = route.transitions if hasattr(route, 'transitions') else []
        
        # Build the optimized address list and timing details
        optimized_addresses = [addresses[0]]  # Start with start point
        route_indices = [0]  # Start with start point index
        visit_schedule = []  # Detailed schedule with times
        
        # Add start point time
        vehicle_start_time = route.vehicle_start_time if hasattr(route, 'vehicle_start_time') else start_time_str
        visit_schedule.append({
            'stop_number': 1,
            'address': addresses[0],
            'latitude': coordinates_dict[addresses[0]]['latitude'],
            'longitude': coordinates_dict[addresses[0]]['longitude'],
            'arrival_time': vehicle_start_time,
            'service_duration_minutes': 0,
            'wait_duration_minutes': 0,
            'is_depot': addresses[0] == addresses[-1],  # True if start == end
            'stop_type': 'Start'
        })
        
        logger.info(f"Processing {len(visits)} visits from Route Optimization API")
        
        # Process each visit
        for i, visit in enumerate(visits):
            shipment_index = visit.shipment_index
            address_index = shipment_index + 1  # +1 because customers start from index 1
            
            if address_index < len(addresses) - 1:  # Safety check (exclude end point)
                optimized_addresses.append(addresses[address_index])
                route_indices.append(address_index)
                
                # Extract timing information
                arrival_time = visit.start_time if hasattr(visit, 'start_time') else None
                visit_duration = 3  # 3 minutes service time
                
                # Get transition info if available
                wait_duration = 0
                if i < len(transitions):
                    transition = transitions[i]
                    if hasattr(transition, 'wait_duration'):
                        wait_duration = transition.wait_duration.seconds / 60 if transition.wait_duration.seconds else 0
                
                visit_schedule.append({
                    'stop_number': len(visit_schedule) + 1,
                    'address': addresses[address_index],
                    'latitude': coordinates_dict[addresses[address_index]]['latitude'],
                    'longitude': coordinates_dict[addresses[address_index]]['longitude'],
                    'arrival_time': arrival_time.isoformat().replace('+00:00', 'Z') if arrival_time else None,
                    'service_duration_minutes': visit_duration,
                    'wait_duration_minutes': round(wait_duration, 1),
                    'is_depot': False,
                    'stop_type': 'Customer Visit'
                })
        
        # Add end point
        end_point_index = len(addresses) - 1
        optimized_addresses.append(addresses[end_point_index])
        route_indices.append(end_point_index)
        
        # Add final end point arrival
        vehicle_end_time = route.vehicle_end_time if hasattr(route, 'vehicle_end_time') else end_time_str
        visit_schedule.append({
            'stop_number': len(visit_schedule) + 1,
            'address': addresses[end_point_index],
            'latitude': coordinates_dict[addresses[end_point_index]]['latitude'],
            'longitude': coordinates_dict[addresses[end_point_index]]['longitude'],
            'arrival_time': vehicle_end_time.isoformat().replace('+00:00', 'Z') if hasattr(vehicle_end_time, 'isoformat') else vehicle_end_time,
            'service_duration_minutes': 0,
            'wait_duration_minutes': 0,
            'is_depot': addresses[0] == addresses[end_point_index],  # True if start == end
            'stop_type': 'End Point'
        })
        
        # Calculate metrics
        total_duration = 0
        total_distance = 0
        if hasattr(route, 'metrics'):
            total_duration = route.metrics.total_duration.seconds if hasattr(route.metrics, 'total_duration') else 0
            total_distance = route.metrics.travel_distance_meters if hasattr(route.metrics, 'travel_distance_meters') else 0
        
        # Extract detailed transition information
        transition_details = []
        for i, transition in enumerate(transitions):
            if hasattr(transition, 'travel_duration'):
                transition_details.append({
                    'segment': i + 1,
                    'travel_duration_minutes': round(transition.travel_duration.seconds / 60, 1) if transition.travel_duration.seconds else 0,
                    'travel_distance_meters': transition.travel_distance_meters if hasattr(transition, 'travel_distance_meters') else 0,
                    'wait_duration_minutes': round(transition.wait_duration.seconds / 60, 1) if hasattr(transition, 'wait_duration') and transition.wait_duration.seconds else 0,
                    'start_time': transition.start_time.isoformat().replace('+00:00', 'Z') if hasattr(transition, 'start_time') and transition.start_time else None
                })
        
        logger.info(f"Route Optimization API completed successfully")
        logger.info(f"Optimized route indices: {route_indices}")
        logger.info(f"Total duration: {total_duration} seconds ({round(total_duration/60, 2)} minutes)")
        logger.info(f"Vehicle starts at: {vehicle_start_time}")
        logger.info(f"Vehicle ends at: {vehicle_end_time}")
        
        return {
            'success': True,
            'message': f'Route optimization completed successfully using Google Route Optimization API with objective: {optimization_objective}',
            'algorithm': 'Google Route Optimization API',
            'optimization_objective': optimization_objective,
            'original_addresses': addresses,
            'optimized_addresses': optimized_addresses,
            'route_indices': route_indices,
            'address_coordinates': coordinates_dict,
            'timing_info': {
                'vehicle_start_time': vehicle_start_time.isoformat().replace('+00:00', 'Z') if hasattr(vehicle_start_time, 'isoformat') else vehicle_start_time,
                'vehicle_end_time': vehicle_end_time.isoformat().replace('+00:00', 'Z') if hasattr(vehicle_end_time, 'isoformat') else vehicle_end_time,
                'total_duration_seconds': total_duration,
                'total_duration_minutes': round(total_duration / 60, 1),
                'total_duration_hours': round(total_duration / 3600, 2),
                'service_time_per_stop_minutes': 3,
                'custom_start_time_used': bool(start_time_config)
            },
            'visit_schedule': visit_schedule,
            'transition_details': transition_details,
            'optimization_info': {
                'addresses_count': len(addresses),
                'total_distance_meters': total_distance,
                'total_distance_km': round(total_distance / 1000, 2) if total_distance else 0,
                'total_time_seconds': total_duration,
                'total_time_minutes': round(total_duration / 60, 1),
                'total_time_hours': round(total_duration / 3600, 2),
                'cost_per_kilometer': cost_per_kilometer,
                'cost_per_hour': cost_per_hour
            }
        }
        
    except Exception as e:
        logger.error(f"Route Optimization API failed: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return None

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True) 