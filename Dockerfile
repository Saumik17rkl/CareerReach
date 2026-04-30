FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE $PORT

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "$PORT"]
