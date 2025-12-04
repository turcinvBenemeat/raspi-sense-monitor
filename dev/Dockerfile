FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies (skip sense-hat for fake data mode)
COPY requirements.txt .
# Install dependencies, but skip sense-hat (not needed for fake data)
RUN pip install --no-cache-dir psutil psycopg2-binary

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1
# FAKE_DATA will be set via docker-compose or .env file

# Run the logger
CMD ["python", "main.py"]

