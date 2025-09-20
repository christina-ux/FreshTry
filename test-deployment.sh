#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=======================================================${NC}"
echo -e "${GREEN}   PolicyEdgeAI - Local Deployment Test Script        ${NC}"
echo -e "${BLUE}=======================================================${NC}"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed. Please install it first.${NC}"
    exit 1
fi

# Create a local network for the containers
echo -e "${GREEN}Creating Docker network...${NC}"
docker network create policyedgeai-network 2>/dev/null || true

# Build API image
echo -e "${GREEN}Building API Docker image...${NC}"
docker build -t policyedgeai-api:local -f api.Dockerfile .

# Build Dashboard image
echo -e "${GREEN}Building Dashboard Docker image...${NC}"
docker build -t policyedgeai-dashboard:local -f dashboard.Dockerfile .

# Stop and remove existing containers
echo -e "${GREEN}Cleaning up existing containers...${NC}"
docker rm -f policyedgeai-api policyedgeai-dashboard 2>/dev/null || true

# Start API container
echo -e "${GREEN}Starting API container...${NC}"
docker run -d \
  --name policyedgeai-api \
  --network policyedgeai-network \
  -p 8000:8000 \
  -e OPENAI_API_KEY="${OPENAI_API_KEY}" \
  -e ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY}" \
  -e JWT_SECRET_KEY="local-testing-jwt-secret-key" \
  -e LOG_LEVEL="INFO" \
  -e PORT=8000 \
  policyedgeai-api:local

# Start Dashboard container
echo -e "${GREEN}Starting Dashboard container...${NC}"
docker run -d \
  --name policyedgeai-dashboard \
  --network policyedgeai-network \
  -p 8501:8501 \
  -e API_URL="http://policyedgeai-api:8000" \
  -e STREAMLIT_SERVER_PORT=8501 \
  policyedgeai-dashboard:local

# Wait for containers to be ready
echo -e "${GREEN}Waiting for containers to start...${NC}"
sleep 5

# Check if containers are running
echo -e "${GREEN}Checking container status...${NC}"
API_RUNNING=$(docker ps --filter "name=policyedgeai-api" --format "{{.Status}}" | grep -q "Up" && echo "true" || echo "false")
DASHBOARD_RUNNING=$(docker ps --filter "name=policyedgeai-dashboard" --format "{{.Status}}" | grep -q "Up" && echo "true" || echo "false")

if [ "$API_RUNNING" = "true" ] && [ "$DASHBOARD_RUNNING" = "true" ]; then
    echo -e "${GREEN}Both containers are running successfully!${NC}"
    
    # Check API health
    echo -e "${GREEN}Checking API health...${NC}"
    if curl -s http://localhost:8000/health | grep -q "healthy"; then
        echo -e "${GREEN}API is healthy!${NC}"
    else
        echo -e "${YELLOW}API health check failed. Check logs.${NC}"
        docker logs policyedgeai-api
    fi
    
    echo -e "${BLUE}=======================================================${NC}"
    echo -e "${GREEN}Local deployment test completed successfully!${NC}"
    echo -e "${BLUE}=======================================================${NC}"
    echo -e "${YELLOW}Access the services at:${NC}"
    echo -e "  - API: http://localhost:8000"
    echo -e "  - Dashboard: http://localhost:8501"
    echo -e "${YELLOW}To view logs:${NC}"
    echo -e "  - API Logs: docker logs policyedgeai-api"
    echo -e "  - Dashboard Logs: docker logs policyedgeai-dashboard"
    echo -e "${YELLOW}To stop the containers:${NC}"
    echo -e "  - docker stop policyedgeai-api policyedgeai-dashboard"
    echo -e "${BLUE}=======================================================${NC}"
else
    echo -e "${RED}Container startup failed!${NC}"
    
    echo -e "${YELLOW}API Container Status:${NC}"
    docker ps --filter "name=policyedgeai-api" --format "{{.Status}}"
    
    echo -e "${YELLOW}Dashboard Container Status:${NC}"
    docker ps --filter "name=policyedgeai-dashboard" --format "{{.Status}}"
    
    echo -e "${YELLOW}API Container Logs:${NC}"
    docker logs policyedgeai-api
    
    echo -e "${YELLOW}Dashboard Container Logs:${NC}"
    docker logs policyedgeai-dashboard
    
    echo -e "${RED}Local deployment test failed!${NC}"
    exit 1
fi