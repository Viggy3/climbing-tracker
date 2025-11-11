# Production deployment script for Climbing Tracker (PowerShell)

$ErrorActionPreference = "Stop"

Write-Host "🧗 Starting Climbing Tracker deployment..." -ForegroundColor Green

# Check if .env.production exists
if (-not (Test-Path ".env.production")) {
    Write-Host "❌ .env.production file not found!" -ForegroundColor Red
    Write-Host "Please create .env.production with your production environment variables." -ForegroundColor Yellow
    exit 1
}

# Pull latest changes (if using git)
Write-Host "📥 Pulling latest changes..." -ForegroundColor Blue
try {
    git pull origin main
} catch {
    Write-Host "⚠️  Git pull failed or not a git repository" -ForegroundColor Yellow
}

# Build and deploy with docker-compose
Write-Host "🐳 Building Docker image..." -ForegroundColor Blue
docker-compose -f docker-compose.prod.yml build --no-cache

Write-Host "🚀 Deploying application..." -ForegroundColor Blue
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d

# Wait for health check
Write-Host "🔍 Waiting for application to be healthy..." -ForegroundColor Blue
Start-Sleep -Seconds 30

# Check if the application is working
$status = docker-compose -f docker-compose.prod.yml ps
if ($status -match "Up.*healthy") {
    Write-Host "✅ Deployment successful! Application is running and healthy." -ForegroundColor Green
    Write-Host "🌐 Application should be available at your configured domain." -ForegroundColor Green
} else {
    Write-Host "❌ Deployment failed! Check logs with: docker-compose -f docker-compose.prod.yml logs" -ForegroundColor Red
    exit 1
}

# Clean up old images
Write-Host "🧹 Cleaning up old Docker images..." -ForegroundColor Blue
docker image prune -f

Write-Host "🎉 Deployment complete!" -ForegroundColor Green