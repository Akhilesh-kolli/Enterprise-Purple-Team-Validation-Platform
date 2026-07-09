#!/bin/bash
# Development startup script for local setup

set -e

echo "🚀 Enterprise Purple Team Platform - Development Setup"
echo "=============================================="

# Check Python version
echo "📦 Checking Python version..."
python3 --version || { echo "Python 3 is required"; exit 1; }

# Create venv if it doesn't exist
if [ ! -d "backend/venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv backend/venv
fi

# Activate venv
echo "📦 Activating virtual environment..."
source backend/venv/bin/activate

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r backend/requirements.txt

# Check PostgreSQL
echo "🗄️ Checking PostgreSQL..."
psql -U admin -d postgres -c "SELECT 1;" 2>/dev/null || {
    echo "⚠️  PostgreSQL not running. Start it manually or use:"
    echo "   docker run -d --name postgres -e POSTGRES_PASSWORD=password -e POSTGRES_USER=admin -e POSTGRES_DB=purple_team -p 5432:5432 postgres:15-alpine"
}

# Check Redis
echo "📡 Checking Redis..."
redis-cli ping 2>/dev/null || {
    echo "⚠️  Redis not running. Start it manually or use:"
    echo "   docker run -d --name redis -p 6379:6379 redis:7-alpine"
}

# Seed data
echo "🌱 Seeding initial data..."
python backend/scripts/seed_data.py

echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 To start the server, run:"
echo "   cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "📖 API Documentation:"
echo "   http://localhost:8000/docs"
echo ""
echo "🔑 Test Credentials:"
echo "   Username: admin"
echo "   Password: AdminPassword123"
