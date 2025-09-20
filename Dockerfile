FROM python:3.9-slim

# Build arguments
ARG GITHUB_SHA=unknown
ARG GITHUB_REF=unknown
ARG BUILD_DATE=unknown

# Labels for container metadata
LABEL org.opencontainers.image.created=${BUILD_DATE} \
      org.opencontainers.image.revision=${GITHUB_SHA} \
      org.opencontainers.image.source="https://github.com/your-github-username/policyedgeai" \
      maintainer="DevOps <devops@example.com>" \
      app.kubernetes.io/name="policyedgeai" \
      app.kubernetes.io/version="1.0.0"

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libmagic1 \
    curl \
    gnupg \
    lsb-release \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set up health check utilities
RUN apt-get update && apt-get install -y --no-install-recommends \
    iputils-ping \
    dnsutils \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create necessary directories
RUN mkdir -p data/uploads data/reports data/dashboard data/scoring data/uploads/processed logs

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PORT=8000 \
    STREAMLIT_PORT=8501 \
    AWS_REGION=us-east-1 \
    API_URL=http://localhost:8000 \
    LOG_LEVEL=INFO \
    BUILD_VERSION=${GITHUB_SHA} \
    APP_ENV=production

# Save build info for diagnostics
RUN echo "Build: ${GITHUB_SHA}" > /app/build_info.txt && \
    echo "Branch/Tag: ${GITHUB_REF}" >> /app/build_info.txt && \
    echo "Build Date: $(date)" >> /app/build_info.txt

# Copy application code
COPY . .

# Ensure the entrypoint script is executable
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Expose ports for FastAPI and Streamlit
EXPOSE 8000 8501

# Set the default health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
  CMD curl --fail http://localhost:$PORT/health || exit 1

# Set the entrypoint script
ENTRYPOINT ["/docker-entrypoint.sh"]