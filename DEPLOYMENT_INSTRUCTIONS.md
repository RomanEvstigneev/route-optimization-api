# 🚀 Deployment Instructions for Route Optimization API

## Prerequisites
- Google Cloud SDK installed and authenticated
- Google Cloud Project with App Engine enabled
- Google Maps API key with required permissions

## 📋 Step-by-Step Deployment

### 1. Google Cloud Setup
```bash
# Login to Google Cloud
gcloud auth login

# Set your project (replace with your actual project ID)
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable appengine.googleapis.com
gcloud services enable maps-backend.googleapis.com
```

### 2. Configure Environment Variables
```bash
# Set Google Maps API Key
gcloud app deploy --set-env-vars GOOGLE_MAPS_API_KEY=YOUR_API_KEY_HERE

# Set Flask Secret Key
gcloud app deploy --set-env-vars SECRET_KEY=your-secret-key-here
```

**Or create `.env` file for local testing:**
```
GOOGLE_MAPS_API_KEY=your_api_key_here
SECRET_KEY=your_secret_key_here
```

### 3. Google Maps API Permissions
Ensure your API key has these APIs enabled:
- Distance Matrix API
- Directions API
- Routes API (optional)

### 4. Local Testing (Optional)
```bash
# Install dependencies
pip install -r requirements.txt

# Test locally with gunicorn
gunicorn -b :8080 --workers 2 --threads 4 --timeout 60 main:app

# Test endpoints
curl http://localhost:8080/health
```

### 5. Deploy to App Engine
```bash
# Deploy the application
gcloud app deploy

# View logs
gcloud app logs tail -s default
```

## 🌐 API Endpoints

After deployment, your API will be available at:
```
https://items-routes-route-optimisation-dot-[PROJECT-ID].appspot.com
```

### Available Endpoints:
- `GET /` - Web interface
- `GET /health` - Health check
- `POST /api/optimize` - Route optimization API
- `GET /example` - Download example JSON

### API Usage Example:
```bash
curl -X POST \
  https://items-routes-route-optimisation-dot-[PROJECT-ID].appspot.com/api/optimize \
  -H "Content-Type: application/json" \
  -d '{
    "addresses": [
      "Berlin, Germany",
      "Munich, Germany",
      "Hamburg, Germany"
    ]
  }'
```

## 🔧 Configuration Details

### app.yaml Configuration:
- **Service**: `items-routes-route-optimisation`
- **Runtime**: `python39`
- **Scaling**: Basic scaling with max 5 instances
- **Timeout**: 60 seconds for API calls
- **Workers**: 2 workers with 4 threads each

### Security Features:
- All endpoints secured with HTTPS (`secure: always`)
- Static files with proper caching headers
- Environment variables for sensitive data

## 📊 Monitoring

- **Health Check**: `/health` endpoint for monitoring
- **Logs**: `gcloud app logs tail -s default`
- **Metrics**: Available in Google Cloud Console

## 🐛 Troubleshooting

### Common Issues:
1. **API Key Error**: Ensure Google Maps API key is set correctly
2. **Timeout**: Large route optimization may take time
3. **Memory**: OR-Tools may need more memory for large datasets

### Debug Commands:
```bash
# View app logs
gcloud app logs tail -s default

# Check app status
gcloud app services describe default

# Update environment variables
gcloud app deploy --set-env-vars KEY=VALUE
```

## 📝 Notes

- Service automatically scales based on demand
- Maximum 5 instances to control costs
- 20-minute idle timeout for cost optimization
- Static files cached for 1 hour for performance 