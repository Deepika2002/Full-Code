FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    gcc \
    g++ \
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
ENV PORT=8001

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8001/index/health || exit 1

# Run the application
CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8001"]