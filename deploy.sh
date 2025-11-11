#!/bin/bash

# Production deployment script for Climbing Tracker

set -e

echo "🧗 Starting Climbing Tracker deployment..."

# Check if .env.production exists
if [ ! -f ".env.production" ]; then
    echo "❌ .env.production file not found!"
    echo "Please create .env.production with your production environment variables."
    exit 1
fi

# Pull latest changes (if using git)
echo "📥 Pulling latest changes..."
git pull origin main || echo "⚠️  Git pull failed or not a git repository"

# Build and deploy with docker-compose
echo "🐳 Building Docker image..."
docker-compose -f docker-compose.prod.yml build --no-cache

echo "🚀 Deploying application..."
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d

# Wait for health check
echo "🔍 Waiting for application to be healthy..."
sleep 30

# Check if the application is working
if docker-compose -f docker-compose.prod.yml ps | grep -q "Up (healthy)"; then
    echo "✅ Deployment successful! Application is running and healthy."
    echo "🌐 Application should be available at your configured domain."
else
    echo "❌ Deployment failed! Check logs with: docker-compose -f docker-compose.prod.yml logs"
    exit 1
fi

# Clean up old images
echo "🧹 Cleaning up old Docker images..."
docker image prune -f

echo "🎉 Deployment complete!"