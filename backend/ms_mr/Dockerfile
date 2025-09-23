FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared modules
COPY ../shared ./shared

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONPATH=/app
ENV PORT=8002

# Expose port
EXPOSE 8002

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8002/mr/health || exit 1

# Run the application
CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8002"]