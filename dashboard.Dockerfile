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
      app.kubernetes.io/name="policyedgeai-dashboard" \
      app.kubernetes.io/version="1.0.0" \
      app.kubernetes.io/component="dashboard" \
      app.kubernetes.io/part-of="policyedgeai"

WORKDIR /app

# Install system dependencies - combine RUN commands to reduce layers
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    wget \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create dedicated non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser -d /app appuser \
    && chown -R appuser:appuser /app

# Create necessary directories with correct permissions
RUN mkdir -p /app/data/dashboard /app/logs /app/cache \
    && chown -R appuser:appuser /app/data /app/logs /app/cache

# Copy requirements first for better layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_ENABLE_CORS=false \
    STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=true \
    BUILD_VERSION=${GITHUB_SHA} \
    APP_ENV=production \
    CACHE_DIR=/app/cache

# Set Streamlit configuration
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false \
    STREAMLIT_THEME_PRIMARY_COLOR="#0066CC" \
    STREAMLIT_THEME_BACKGROUND_COLOR="#FFFFFF" \
    STREAMLIT_THEME_TEXTCOLOR="#262730" \
    STREAMLIT_THEME_FONT="sans serif"

# Save build info for diagnostics
RUN echo "Build: ${GITHUB_SHA}" > /app/build_info.txt && \
    echo "Branch/Tag: ${GITHUB_REF}" >> /app/build_info.txt && \
    echo "Build Date: ${BUILD_DATE}" >> /app/build_info.txt && \
    chown appuser:appuser /app/build_info.txt

# Copy application code - do this as late as possible to maximize caching
COPY --chown=appuser:appuser . .

# Switch to non-root user for security
USER appuser

# Expose Streamlit port
EXPOSE 8501

# Set the default health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:8501/ || exit 1

# Start the Streamlit server with optimized parameters for production
CMD ["streamlit", "run", "streamlit_app.py", "--server.enableCORS=false", "--server.enableXsrfProtection=true", "--server.maxUploadSize=10"]