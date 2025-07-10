# Route Optimization API Service

🚀 **Production-ready Flask API service for route optimization using Google Route Optimization API**

## ✨ Features

- ✅ **Professional Route Optimization** - Google Route Optimization API
- ✅ **Auto-Geocoding** - Converts addresses to GPS coordinates
- ✅ **International Support** - Tested with German addresses, Unicode support
- ✅ **Production Ready** - Deployed on Google Cloud App Engine
- ✅ **Single API Call** - Efficient optimization vs traditional multi-request approaches
- ✅ **Real-world Constraints** - Traffic, road conditions, vehicle limitations
- ✅ **High Capacity** - Supports 100+ addresses (vs 10 with Distance Matrix API)
- ✅ **Web Interface** - User-friendly UI for manual optimization
- ✅ **REST API** - Full programmatic access

## 🌐 Live Production API

**Production URL:** `https://items-routes-route-optimisation-dot-maibach-items-routes.ew.r.appspot.com`

### Quick Test

```bash
# Health check
curl https://items-routes-route-optimisation-dot-maibach-items-routes.ew.r.appspot.com/health

# Route optimization
curl -X POST https://items-routes-route-optimisation-dot-maibach-items-routes.ew.r.appspot.com/api/optimize \
  -H "Content-Type: application/json" \
  -d '{"addresses": ["Berlin, Germany", "Munich, Germany", "Hamburg, Germany"]}'
```

## 🏗️ Architecture

- **Backend:** Flask (Python 3.9)
- **WSGI Server:** Gunicorn (production)
- **Optimization:** Google Route Optimization API
- **Geocoding:** Google Geocoding API
- **Deployment:** Google Cloud App Engine
- **Scaling:** Auto-scaling (max 5 instances)

## 📁 Project Structure

```
Route_API_service/
├── main.py                    # Main Flask application
├── main_route_optimization.py # Alternative implementation
├── requirements.txt           # Python dependencies
├── app.yaml                   # Google App Engine config
├── deploy.sh                  # Deployment script
├── API_DOCUMENTATION.md       # Complete API documentation
├── templates/                 # HTML templates
│   ├── index.html
│   └── result.html
├── static/                    # Static files
│   ├── style.css
│   └── example.json
├── test_api.py               # API tests
├── test_deployment.py        # Deployment tests
└── README.md                 # This file
```

## 🛠️ Local Development

### Prerequisites

- Python 3.9+
- Google Cloud SDK
- Google Maps API key
- Google Cloud Project with Route Optimization API enabled

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/route-optimization-api.git
cd route-optimization-api
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
export GOOGLE_MAPS_API_KEY="your_google_maps_api_key"
export GOOGLE_CLOUD_PROJECT_ID="your_google_cloud_project_id"
export SECRET_KEY="your_secret_key"
```

4. Run locally:
```bash
python main.py
```

## 🚀 Deployment

### Google Cloud App Engine

1. Configure Google Cloud:
```bash
gcloud config set project YOUR_PROJECT_ID
gcloud app create --region=europe-west1
```

2. Set environment variables:
```bash
gcloud app deploy --set-env-vars GOOGLE_MAPS_API_KEY=your_key,SECRET_KEY=your_secret
```

3. Deploy:
```bash
./deploy.sh
```

## 📚 API Documentation

Complete API documentation is available in [API_DOCUMENTATION.md](API_DOCUMENTATION.md).

### Key Endpoints

- **GET /health** - Health check
- **GET /** - Web interface
- **POST /api/optimize** - Route optimization
- **GET /example** - Download example JSON

### Example Usage

```python
import requests

response = requests.post(
    "https://items-routes-route-optimisation-dot-maibach-items-routes.ew.r.appspot.com/api/optimize",
    json={"addresses": ["New York, NY", "Boston, MA", "Philadelphia, PA"]},
    headers={"Content-Type": "application/json"}
)

result = response.json()
print(f"Optimized route: {result['optimized_addresses']}")
```

## 🧪 Testing

### Run Tests

```bash
# API tests
python test_api.py

# Deployment tests
python test_deployment.py
```

### Test with Real Data

The API has been tested with real-world German addresses:
- ✅ Unicode support (ü, ß, ä, ö)
- ✅ International geocoding
- ✅ Complex address formats
- ✅ Route optimization accuracy

## 🔧 Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GOOGLE_MAPS_API_KEY` | Yes | Google Maps API key |
| `GOOGLE_CLOUD_PROJECT_ID` | Yes | Google Cloud Project ID |
| `SECRET_KEY` | Yes | Flask secret key |

### Google Cloud APIs

Enable these APIs in your Google Cloud project:
- Route Optimization API
- Geocoding API
- Maps Backend API

## 📊 Performance

- **Optimization Speed:** Single API call vs traditional multi-request
- **Capacity:** 100+ addresses (vs 10 with Distance Matrix)
- **Accuracy:** Real-world traffic and road conditions
- **Availability:** 99.9% uptime on Google Cloud App Engine

## 🔒 Security

- ✅ HTTPS encryption
- ✅ Environment variable configuration
- ✅ API key protection
- ✅ Input validation
- ✅ Error handling

## 📈 Monitoring

- **Health Check:** `/health` endpoint
- **Logs:** `gcloud app logs tail`
- **Metrics:** Google Cloud Console
- **Alerts:** Google Cloud Monitoring

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
- Check the [API Documentation](API_DOCUMENTATION.md)
- Review the logs: `gcloud app logs tail`
- Test the health endpoint: `/health`

## 🎯 Version History

- **v2.0.0** - Google Route Optimization API integration
- **v1.0.0** - Initial release with OR-Tools

---

**Production API:** https://items-routes-route-optimisation-dot-maibach-items-routes.ew.r.appspot.com

Made with ❤️ for efficient route optimization 