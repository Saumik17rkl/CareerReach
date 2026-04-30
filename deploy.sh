#!/bin/bash

# ReachBridge Deployment Script
# This script deploys the ReachBridge application using Docker Compose

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p uploads
mkdir -p logs
mkdir -p ssl

# Copy environment file if it doesn't exist
if [ ! -f .env ]; then
    print_warning ".env file not found. Creating from .env.example..."
    cp .env.example .env
    print_warning "Please edit .env file with your configuration before running in production."
fi

# Build and start services
print_status "Building and starting services..."
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Wait for services to be ready
print_status "Waiting for services to be ready..."
sleep 10

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    print_status "Services are running successfully!"
    
    # Show service status
    echo ""
    print_status "Service Status:"
    docker-compose ps
    
    # Show logs
    echo ""
    print_status "Recent logs:"
    docker-compose logs --tail=20 app
    
    echo ""
    print_status "Deployment completed successfully!"
    print_status "API is available at: http://localhost:8000"
    print_status "API Documentation: http://localhost:8000/docs"
    print_status "Database: PostgreSQL on port 5432"
    
else
    print_error "Some services failed to start. Check logs:"
    docker-compose logs
    exit 1
fi

# Optional: Run database migrations if needed
print_status "Running database setup..."
docker-compose exec app python -c "
from app.database import Base, engine
Base.metadata.create_all(bind=engine)
print('Database tables created successfully')
"

print_status "Deployment setup complete!"
