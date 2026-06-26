#!/bin/bash

# Development script

case "$1" in
    "backend")
        echo "🚀 Starting backend..."
        source venv/bin/activate
        cd backend
        uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
        ;;
    "frontend")
        echo "🚀 Starting frontend..."
        cd frontend
        npm run dev
        ;;
    "docker")
        echo "🚀 Starting Docker services..."
        docker-compose up -d
        echo "Services running at:"
        echo "  - Frontend: http://localhost:3000"
        echo "  - Backend: http://localhost:8000"
        echo "  - API Docs: http://localhost:8000/api/docs"
        echo "  - PostgreSQL: localhost:5432"
        echo "  - Redis: localhost:6379"
        echo "  - Elasticsearch: localhost:9200"
        echo "  - Ollama: http://localhost:11434"
        ;;
    "stop")
        echo "🛑 Stopping Docker services..."
        docker-compose down
        ;;
    "logs")
        echo "📋 Showing logs..."
        docker-compose logs -f
        ;;
    *)
        echo "Usage: ./dev.sh [backend|frontend|docker|stop|logs]"
        ;;
esac
