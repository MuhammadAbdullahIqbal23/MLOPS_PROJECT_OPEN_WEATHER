#!/bin/bash
# Quick Start Script for MLOps Pipeline
# Run this to set up and start the entire pipeline

echo "=========================================="
echo "MLOps Weather Prediction Pipeline Setup"
echo "=========================================="
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running. Please start Docker Desktop first."
    exit 1
fi

echo "✓ Docker is running"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  Creating .env file from template..."
    cp .env.example .env
    echo "❗ IMPORTANT: Edit .env file and add your OpenWeatherMap API key"
    echo "   Get your free API key from: https://openweathermap.org/api"
    echo ""
    echo "Press Enter after you've added your API key to .env file..."
    read
fi

echo "✓ Environment file exists"
echo ""

# Start Docker Compose
echo "🚀 Starting services (Airflow + MinIO)..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services to initialize (this may take 2-3 minutes)..."
sleep 30

# Check service status
echo ""
echo "📊 Service Status:"
docker-compose ps

echo ""
echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "Access the services:"
echo "  • Airflow UI:    http://localhost:8080"
echo "    Username: admin"
echo "    Password: admin"
echo ""
echo "  • MinIO Console: http://localhost:9001"
echo "    Username: minioadmin"
echo "    Password: minioadmin"
echo ""
echo "Next steps:"
echo "  1. Open Airflow UI at http://localhost:8080"
echo "  2. Find the 'weather_prediction_pipeline' DAG"
echo "  3. Toggle it ON (unpause)"
echo "  4. Click 'Trigger DAG' to run"
echo ""
echo "For detailed instructions, see SETUP_AND_RUN.md"
echo ""
