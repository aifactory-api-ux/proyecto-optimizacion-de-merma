#!/bin/bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Project root directory
PROJECT_ROOT=$(cd "$(dirname "$0")" && pwd)
cd "$PROJECT_ROOT"

echo "=========================================="
echo "  Merma Optimization - Starting Services"
echo "=========================================="

# Step 1: Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed.${NC}"
    echo "Please install Docker from: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}Error: Docker Compose is not installed.${NC}"
    echo "Please install Docker Compose from: https://docs.docker.com/compose/install/"
    exit 1
fi

# Step 2: Create .env from .env.example if missing
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${GREEN}✓ .env created from .env.example${NC}"
    else
        echo -e "${RED}Error: .env.example not found. Cannot create .env${NC}"
        exit 1
    fi
fi

# Step 3: Validate required environment variables
MISSING_VARS=()

# Check critical backend variables
if ! grep -q "POSTGRES_HOST" .env 2>/dev/null || ! grep -q "POSTGRES_USER" .env 2>/dev/null || ! grep -q "POSTGRES_PASSWORD" .env 2>/dev/null; then
    echo -e "${YELLOW}Warning: Some PostgreSQL variables may not be set in .env${NC}"
fi

if ! grep -q "JWT_SECRET_KEY" .env 2>/dev/null || grep -q "your-secret-key-change-in-production" .env 2>/dev/null; then
    echo -e "${YELLOW}Warning: JWT_SECRET_KEY may not be properly configured${NC}"
fi

# Step 4: Build and start services
echo ""
echo "Building and starting services..."

# Use docker compose (v2) if available, otherwise docker-compose (v1)
if docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
else
    COMPOSE_CMD="docker-compose"
fi

# Build without using cache first to ensure fresh builds
$COMPOSE_CMD build --no-cache

# Start services in detached mode
$COMPOSE_CMD up -d

echo ""
echo "Waiting for services to become healthy..."

# Step 5: Wait for services to be healthy
MAX_WAIT=120
INTERVAL=5
ELAPSED=0

while [ $ELAPSED -lt $MAX_WAIT ]; do
    # Check backend health
    BACKEND_HEALTH=$(docker inspect --format='{{.State.Health.Status}}' merma-backend 2>/dev/null || echo "not-found")
    
    # Check frontend health
    FRONTEND_HEALTH=$(docker inspect --format='{{.State.Health.Status}}' merma-frontend 2>/dev/null || echo "not-found")
    
    if [ "$BACKEND_HEALTH" = "healthy" ] && [ "$FRONTEND_HEALTH" = "healthy" ]; then
        echo -e "${GREEN}✓ All services are healthy!${NC}"
        break
    fi
    
    echo "  Backend: $BACKEND_HEALTH | Frontend: $FRONTEND_HEALTH"
    sleep $INTERVAL
    ELAPSED=$((ELAPSED + INTERVAL))
done

if [ $ELAPSED -ge $MAX_WAIT ]; then
    echo -e "${YELLOW}Warning: Timeout waiting for services to be healthy${NC}"
    echo "Services may still be starting up. Check status with: docker-compose ps"
fi

# Step 6: Display access information
echo ""
echo "=========================================="
echo -e "  ${GREEN}Services Started Successfully!${NC}"
echo "=========================================="
echo ""
echo "  Frontend:     http://localhost:3000"
echo "  Backend API:  http://localhost:8080"
echo "  API Docs:     http://localhost:8080/docs"
echo ""
echo "  PostgreSQL:    localhost:5432"
echo "  Redis:         localhost:6379"
echo ""
echo "  Default credentials:"
echo "    Username: admin"
echo "    Password: admin123"
echo ""
echo "=========================================="
echo "To stop:     ./run.sh stop"
echo "To view logs: docker-compose logs -f"
echo "=========================================="

# Check for stop command
if [ "$1" = "stop" ]; then
    echo "Stopping services..."
    $COMPOSE_CMD down
    echo -e "${GREEN}✓ Services stopped${NC}"
    exit 0
fi

# Keep container running, allow Ctrl+C to stop
trap 'echo ""; echo "Stopping services..."; $COMPOSE_CMD down; echo "✓ Services stopped"; exit 0' INT TERM

# Wait indefinitely (or until Ctrl+C)
wait
