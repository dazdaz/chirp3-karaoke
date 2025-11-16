# Multi-stage build for optimized image size
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies for building Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt

# Final stage
FROM python:3.11-slim

# Create non-root user for security
RUN useradd -m -u 1000 chirpuser && \
    mkdir -p /app && \
    chown -R chirpuser:chirpuser /app

# Set working directory
WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /home/chirpuser/.local

# Copy application files
COPY --chown=chirpuser:chirpuser . .

# Ensure Python can find the installed packages
ENV PATH=/home/chirpuser/.local/bin:$PATH
ENV PYTHONPATH=/home/chirpuser/.local/lib/python3.11/site-packages:$PYTHONPATH

# Switch to non-root user
USER chirpuser

# Create necessary directories and set permissions
RUN mkdir -p /app/songs && \
    touch /app/leaderboard.json && \
    touch /app/songs.json

# Run setup script to initialize data
RUN python setup_data.py || true

# Expose the application port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/').read()" || exit 1

# Set environment variables for production
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["python", "main.py"]
