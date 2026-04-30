FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system CA certificates (needed for TLS to MongoDB Atlas)
RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 10000

# Create a simple script to handle port binding
RUN echo '#!/bin/sh\nuvicorn main:app --host 0.0.0.0 --port ${PORT:-10000}' > /start.sh && chmod +x /start.sh

# Run the application
CMD ["/start.sh"]
