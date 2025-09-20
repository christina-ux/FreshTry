#!/bin/bash
set -e

# Function to log messages with timestamps
log() {
  echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Function to wait for a service to be ready
wait_for_service() {
  local host="$1"
  local port="$2"
  local service_name="$3"
  local timeout="${4:-30}"
  
  log "Waiting for $service_name at $host:$port to become available..."
  
  local start_time=$(date +%s)
  while true; do
    nc -z "$host" "$port" >/dev/null 2>&1
    result=$?
    
    if [ $result -eq 0 ]; then
      log "$service_name is available at $host:$port"
      break
    fi
    
    local current_time=$(date +%s)
    local elapsed_time=$((current_time - start_time))
    
    if [ $elapsed_time -ge $timeout ]; then
      log "Timeout waiting for $service_name at $host:$port"
      return 1
    fi
    
    sleep 1
  done
  
  return 0
}

# Function for health checking
health_check() {
  local endpoint="${1:-health}"
  local port="${2:-$PORT}"
  local retries="${3:-10}"
  local wait="${4:-2}"
  
  log "Performing health check on :$port/$endpoint"
  
  for i in $(seq 1 $retries); do
    response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$port/$endpoint)
    if [ "$response" == "200" ]; then
      log "Health check passed on attempt $i"
      return 0
    else
      log "Health check failed on attempt $i with status $response"
      sleep $wait
    fi
  done
  
  log "All health checks failed"
  return 1
}

# Create required directories if they don't exist
ensure_directories() {
  local dirs=(
    "data/uploads"
    "data/reports"
    "data/dashboard"
    "data/scoring"
    "data/uploads/processed"
    "logs"
  )
  
  for dir in "${dirs[@]}"; do
    if [ ! -d "$dir" ]; then
      log "Creating directory: $dir"
      mkdir -p "$dir"
    fi
  done
}

# Check environment variables and provide defaults
check_env_vars() {
  # API settings
  : "${PORT:=8000}"
  : "${API_URL:=http://localhost:$PORT}"
  : "${LOG_LEVEL:=INFO}"
  : "${APP_ENV:=production}"
  
  # Streamlit settings
  : "${STREAMLIT_PORT:=8501}"
  : "${STREAMLIT_SERVER_ADDRESS:=0.0.0.0}"
  
  export PORT API_URL LOG_LEVEL APP_ENV STREAMLIT_PORT STREAMLIT_SERVER_ADDRESS
  
  log "Environment Configuration:"
  log "  PORT=$PORT"
  log "  APP_ENV=$APP_ENV"
  log "  LOG_LEVEL=$LOG_LEVEL"
}

# Setup database and initial data if needed
setup_database() {
  if [ -n "$SETUP_DB" ] && [ "$SETUP_DB" = "true" ]; then
    log "Setting up database..."
    python -m scripts.setup_db
  fi
}

# Start the appropriate service based on container type
start_service() {
  if [ -z "$SERVICE_TYPE" ]; then
    # Determine service type based on container naming or environment
    if [[ "$HOSTNAME" == *"dashboard"* ]] || [ "$SERVICE_TYPE" = "dashboard" ]; then
      SERVICE_TYPE="dashboard"
    elif [[ "$HOSTNAME" == *"api"* ]] || [ "$SERVICE_TYPE" = "api" ]; then
      SERVICE_TYPE="api"
    else
      # Default to API if not specified
      SERVICE_TYPE="api"
    fi
  fi
  
  log "Starting service: $SERVICE_TYPE"
  
  case "$SERVICE_TYPE" in
    "api")
      log "Starting API server on port $PORT"
      exec uvicorn app:app --host 0.0.0.0 --port "$PORT" --workers 4
      ;;
    "dashboard")
      log "Starting Streamlit dashboard on port $STREAMLIT_PORT"
      exec streamlit run streamlit_app.py --server.port "$STREAMLIT_PORT" --server.address "$STREAMLIT_SERVER_ADDRESS"
      ;;
    *)
      log "Unknown service type: $SERVICE_TYPE"
      exit 1
      ;;
  esac
}

# Main execution flow
main() {
  log "Starting PolicyEdgeAI container"
  
  # Show build information
  if [ -f "/app/build_info.txt" ]; then
    log "Build information:"
    cat /app/build_info.txt | sed 's/^/  /'
  fi
  
  # Check environment variables
  check_env_vars
  
  # Ensure required directories exist
  ensure_directories
  
  # Set up database if necessary
  setup_database
  
  # Wait for any dependent services if specified
  if [ -n "$WAIT_FOR_HOST" ] && [ -n "$WAIT_FOR_PORT" ]; then
    wait_for_service "$WAIT_FOR_HOST" "$WAIT_FOR_PORT" "dependent service" 60
  fi
  
  # Start the service
  start_service
}

# Execute main function
main "$@"