# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libjpeg-dev \
    zlib1g-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create storage and logs directories
RUN mkdir -p storage logs

# Listen port (overridden per env in compose: 9013 dev, 9003 main)
ENV PORT=9003
EXPOSE 9003

# Run the application using gunicorn with threads and keep-alive for stability
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT} --workers 2 --worker-class gthread --threads 4 --timeout 120 --keep-alive 5 --access-logfile - run:app"]

# Healthcheck to ensure the app is responding
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD sh -c 'curl -f http://localhost:${PORT}/ || exit 1'
