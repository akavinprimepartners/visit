#!/bin/bash

# AKAVIN OS Setup Script

echo "🚀 Setting up AKAVIN OS..."

# Create directories
mkdir -p data/db
mkdir -p data/storage
mkdir -p data/uploads
mkdir -p logs

# Set permissions
chmod 755 data
chmod 755 logs

# Check for Docker
if ! command -v docker &> /dev/null; then
    echo "⚠️  Docker not found. Please install Docker first."
    exit 1
fi

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "⚠️  Python 3 not found. Please install Python 3.11+"
    exit 1
fi

# Setup Python virtual environment
echo "🐍 Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r backend/requirements.txt

# Setup Node.js
if ! command -v node &> /dev/null; then
    echo "⚠️  Node.js not found. Please install Node.js 18+"
    exit 1
fi

echo "📦 Installing Node.js dependencies..."
cd frontend
npm install
cd ..

# Create .env files
cp docker/.env.example .env

# Initialize database
echo "🗄️ Initializing database..."
python3 -c "from backend.app.core.database import Database; import asyncio; asyncio.run(Database().connect())" 2>/dev/null || echo "⚠️  Database initialization skipped"

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Start services: docker-compose up -d"
echo "2. Access web: http://localhost:3000"
echo "3. Access API: http://localhost:8000"
echo "4. API Docs: http://localhost:8000/api/docs"
echo ""
echo "Or run development servers:"
echo "Backend: ./scripts/dev.sh backend"
echo "Frontend: ./scripts/dev.sh frontend"
