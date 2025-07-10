from flask import Flask, render_template, request, redirect, url_for, send_file, flash
import json
import os
from datetime import datetime
from google.maps import routeoptimization_v1 as ro
from google.auth import default
from google.oauth2 import service_account

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev')

# Option 1: Use service account key file
SERVICE_ACCOUNT_FILE = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
if SERVICE_ACCOUNT_FILE:
    credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE)
else:
    # Option 2: Use default credentials (for Google Cloud environments)
    credentials, project = default()

# Initialize the Route Optimization client
client = ro.RouteOptimizationClient(credentials=credentials)

# Your Google Cloud project ID
PROJECT_ID = os.environ.get('GOOGLE_CLOUD_PROJECT_ID')

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/example', methods=['GET'])
def download_example():
    return send_file('static/example.json', as_attachment=True)

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
    except Exception as e:
        flash(f'Error reading JSON: {e}')
        return redirect(url_for('index'))

    if not PROJECT_ID:
        flash('Google Cloud Project ID is not set.')
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

def optimize_route_with_api(addresses):
    """
    Use Google Route Optimization API to find the optimal route
    This is more efficient than the old approach with multiple API calls
    """
    try:
        # Create shipments for each address (except the first one which is the depot)
        shipments = []
        for i, address in enumerate(addresses[1:], 1):  # Skip depot
            shipment = {
                "deliveries": [{
                    "arrival_location": {"address": address},
                    "duration": "5m"  # 5 minutes service time at each location
                }]
            }
            shipments.append(shipment)
        
        # Create vehicle starting and ending at the depot
        vehicle = {
            "start_location": {"address": addresses[0]},  # First address is depot
            "end_location": {"address": addresses[0]},    # Return to depot
            "cost_per_kilometer": 1.0,
            "travel_duration_multiple": 1.0
        }
        
        # Create the optimization request
        request = ro.OptimizeToursRequest(
            parent=f"projects/{PROJECT_ID}",
            model={
                "shipments": shipments,
                "vehicles": [vehicle],
                "global_start_time": datetime.now().isoformat() + "Z",
                "global_end_time": (datetime.now().replace(hour=23, minute=59)).isoformat() + "Z"
            }
        )
        
        print("DEBUG: Sending request to Route Optimization API")
        response = client.optimize_tours(request=request)
        
        if not response.routes:
            print("ERROR: No routes found in optimization response")
            return None
            
        # Parse the response
        route = response.routes[0]
        visits = route.visits
        
        # Build the optimized address list
        optimized_addresses = [addresses[0]]  # Start with depot
        
        for visit in visits:
            # Get the shipment index and map it to address
            shipment_index = visit.shipment_index
            if shipment_index < len(addresses) - 1:
                optimized_addresses.append(addresses[shipment_index + 1])
        
        # Add depot at the end for return trip
        optimized_addresses.append(addresses[0])
        
        # Calculate route details
        steps = []
        total_time = 0
        total_distance = 0
        
        for i, addr in enumerate(optimized_addresses):
            if i == 0:
                steps.append({
                    'address': addr,
                    'eta': 'Start',
                    'cumulative_time': 0,
                    'cumulative_distance': 0
                })
            else:
                # For simplicity, we'll use the route metrics from the optimization
                # In a real implementation, you might want to get more detailed route info
                eta_minutes = i * 15  # Rough estimate
                steps.append({
                    'address': addr,
                    'eta': f"{eta_minutes} min",
                    'cumulative_time': eta_minutes * 60,
                    'cumulative_distance': i * 5000  # Rough estimate in meters
                })
        
        # Extract metrics from the optimization response
        if route.metrics:
            total_time = int(route.metrics.total_time.total_seconds())
            total_distance = int(route.metrics.total_distance_meters)
        
        return {
            'total_time': f"{total_time//60} min",
            'total_distance': f"{total_distance/1000:.1f} km",
            'steps': steps,
            'route_summary': {
                'total_time_seconds': total_time,
                'total_distance_meters': total_distance,
                'num_stops': len(optimized_addresses),
                'optimization_method': 'Route Optimization API'
            }
        }
        
    except Exception as e:
        print(f"ERROR: Route optimization failed: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True) 