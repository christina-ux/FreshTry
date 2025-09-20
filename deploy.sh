#\!/bin/bash

# Stop and remove existing containers if they exist
docker stop policyedgeai-api policyedgeai-dashboard || true
docker rm policyedgeai-api policyedgeai-dashboard || true

# Pull the latest code (if using git)
# git pull origin main

# Build and start the containers
docker-compose up -d

# Show container status
docker ps
