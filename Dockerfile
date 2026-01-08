FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libffi-dev \
    shared-mime-info \
    curl \
    ca-certificates \
    git \
    postgresql-client \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Copy application code
COPY backend /app/backend
COPY frontend /app/frontend
COPY entrypoint.sh /app/entrypoint.sh

# Capture git commit hash at build time (optional)
ARG GIT_COMMIT=unknown
RUN echo "$GIT_COMMIT" > /app/.git_commit

# Create directories
RUN mkdir -p /app/logs

# Make entrypoint executable
RUN chmod +x /app/entrypoint.sh

# Set PYTHONPATH
ENV PYTHONPATH=/app/backend

# Expose port
EXPOSE 8030

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8030}/health || exit 1

# Run entrypoint script
CMD ["/app/entrypoint.sh"]
