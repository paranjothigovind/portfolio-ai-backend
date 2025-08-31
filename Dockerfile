# Use official lightweight Python image
FROM python:3.9-slim AS base

# Set working directory
WORKDIR /app

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/root/.local/bin:$PATH"

# Install system dependencies only once
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies separately for caching
COPY rag-backend/requirements.txt /app/requirements.txt
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r /app/requirements.txt

# Copy application source code
COPY rag-backend/ /app

# Expose the application port
EXPOSE 8000

# Use uvicorn as production server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
