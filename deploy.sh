#!/bin/bash

# 🚀 Quick deployment script for Route Optimization API
# This script automates the deployment process to Google Cloud App Engine

set -e  # Exit on any error

echo "🚀 Route Optimization API Deployment Script"
echo "=============================================="

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ Error: gcloud CLI is not installed"
    echo "Please install Google Cloud SDK first"
    exit 1
fi

# Check if user is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "❌ Error: Not authenticated with Google Cloud"
    echo "Please run: gcloud auth login"
    exit 1
fi

# Get current project
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
if [ -z "$PROJECT_ID" ]; then
    echo "❌ Error: No project set"
    echo "Please run: gcloud config set project YOUR_PROJECT_ID"
    exit 1
fi

echo "📋 Current project: $PROJECT_ID"

# Confirm deployment
echo ""
read -p "🤔 Deploy to Google Cloud App Engine? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Deployment cancelled"
    exit 1
fi

# Enable required APIs
echo "🔧 Enabling required APIs..."
gcloud services enable appengine.googleapis.com --quiet
gcloud services enable compute.googleapis.com --quiet

# Deploy the application
echo "🚀 Deploying application..."
gcloud app deploy --quiet

# Get the deployed URL
echo "🌐 Getting deployment URL..."
URL=$(gcloud app describe --format="value(defaultHostname)" 2>/dev/null)
if [ -n "$URL" ]; then
    FULL_URL="https://$URL"
    echo ""
    echo "✅ Deployment successful!"
    echo "🌐 Your API is now available at:"
    echo "   $FULL_URL"
    echo ""
    echo "📋 Available endpoints:"
    echo "   GET  $FULL_URL/           - Web interface"
    echo "   GET  $FULL_URL/health     - Health check"
    echo "   POST $FULL_URL/api/optimize - Route optimization API"
    echo "   GET  $FULL_URL/example    - Download example JSON"
    echo ""
    echo "🧪 Test your API:"
    echo "   curl $FULL_URL/health"
else
    echo "⚠️  Deployment completed but couldn't get URL"
    echo "   Check Google Cloud Console for details"
fi

# Show logs command
echo "📊 To view logs, run:"
echo "   gcloud app logs tail -s default"

echo ""
echo "🎉 Deployment complete!" 