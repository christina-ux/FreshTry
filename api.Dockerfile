FROM python:3.9-slim

# Build arguments for better container metadata
ARG GITHUB_SHA=unknown
ARG GITHUB_REF=unknown
ARG BUILD_DATE=unknown
ARG GITHUB_REPOSITORY_OWNER=unknown

# Labels for container metadata
LABEL org.opencontainers.image.created=${BUILD_DATE} \
      org.opencontainers.image.revision=${GITHUB_SHA} \
      org.opencontainers.image.source="https://github.com/${GITHUB_REPOSITORY_OWNER}/policyedgeai" \
      maintainer="DevOps <devops@example.com>" \
      app.kubernetes.io/name="policyedgeai-api" \
      app.kubernetes.io/version="1.0.0" \
      app.kubernetes.io/component="api" \
      app.kubernetes.io/part-of="policyedgeai"

WORKDIR /app

# Install system dependencies - combine RUN commands to reduce layers
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libmagic1 \
    curl \
    gnupg \
    lsb-release \
    iputils-ping \
    dnsutils \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create dedicated non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser -d /app appuser \
    && chown -R appuser:appuser /app

# Create necessary directories with correct permissions
RUN mkdir -p /app/data/uploads /app/data/reports /app/data/scoring /app/data/uploads/processed /app/logs /app/cache \
    && chown -R appuser:appuser /app/data /app/logs /app/cache

# Copy requirements first for better layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PORT=8000 \
    AWS_REGION=us-east-1 \
    LOG_LEVEL=INFO \
    BUILD_VERSION=${GITHUB_SHA} \
    APP_ENV=production \
    CACHE_DIR=/app/cache

# Save build info for diagnostics
RUN echo "Build: ${GITHUB_SHA}" > /app/build_info.txt && \
    echo "Branch/Tag: ${GITHUB_REF}" >> /app/build_info.txt && \
    echo "Build Date: ${BUILD_DATE}" >> /app/build_info.txt && \
    chown appuser:appuser /app/build_info.txt

# Copy application code - do this as late as possible to maximize caching
COPY --chown=appuser:appuser . .

# Switch to non-root user for security
USER appuser

# Expose API port
EXPOSE 8000

# Set the default health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
  CMD curl --fail http://localhost:${PORT}/health || exit 1

# Start the API server
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]