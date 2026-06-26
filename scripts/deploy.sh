#!/bin/bash
# Production Deployment Script

set -e

echo "🚀 Deploying AKAVIN OS to Production"

# Load environment
source .env.production

# Pull latest code
echo "📥 Pulling latest code..."
git pull origin main

# Install dependencies
echo "📦 Installing dependencies..."
cd backend && pip install -r requirements.txt
cd ../frontend && npm ci && cd ..

# Build frontend
echo "🔨 Building frontend..."
cd frontend && npm run build && cd ..

# Migrate database
echo "🗄️ Running database migrations..."
python3 -m backend.migrate

# Restart services
echo "🔄 Restarting services..."
docker-compose -f docker/docker-compose.prod.yml down
docker-compose -f docker/docker-compose.prod.yml up -d

# Health check
echo "🔍 Running health check..."
sleep 10
curl -f https://www.visit.akavin.online/health || echo "⚠️ Health check failed!"

echo "✅ Deployment complete!"
