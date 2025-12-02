#!/bin/bash
# NovaCore Database Setup Script
# This script helps you start PostgreSQL for NovaCore

set -e

echo "🔷 NovaCore Database Setup"
echo ""

# Check if Docker is running
if command -v docker &> /dev/null; then
    if docker info &> /dev/null; then
        echo "✓ Docker is running"
        echo ""
        echo "Starting PostgreSQL with Docker Compose..."
        docker-compose up -d postgres
        echo ""
        echo "Waiting for PostgreSQL to be ready..."
        sleep 5
        
        # Check if postgres is healthy
        if docker-compose ps postgres | grep -q "healthy"; then
            echo "✓ PostgreSQL is ready!"
            echo ""
            echo "You can now run migrations:"
            echo "  source .venv/bin/activate"
            echo "  alembic upgrade head"
            exit 0
        else
            echo "⚠ PostgreSQL is starting, please wait a bit more..."
            echo "Check status with: docker-compose ps"
        fi
    else
        echo "⚠ Docker is installed but daemon is not running"
        echo "Please start Docker Desktop or Docker daemon"
    fi
else
    echo "⚠ Docker not found"
fi

echo ""
echo "Alternative: Install PostgreSQL locally"
echo "  brew install postgresql@16"
echo "  brew services start postgresql@16"
echo ""
echo "Or use any PostgreSQL instance and update DATABASE_URL in .env"

