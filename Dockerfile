FROM python:3.9-slim

WORKDIR /app

# Set environment variables for better Python behavior in containers
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies and security updates
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install pandas-ta (with potential workaround for squeeze_pro issue)
COPY patch_ta.py .
RUN pip install --no-cache-dir pandas-ta
RUN python patch_ta.py

# Copy import test script and verify all dependencies are installed correctly
COPY import_test.py .
RUN python import_test.py

# Create a non-root user and switch to it
RUN adduser --disabled-password --gecos "" appuser
RUN chown -R appuser:appuser /app
USER appuser

# Copy the rest of the application
COPY . .

# Accept Azure credentials as build args and set environment variables
ARG AZURE_API_KEY
ARG AZURE_OPENAI_ENDPOINT
ARG AZURE_DEPLOYMENT_NAME
ENV AZURE_API_KEY=${AZURE_API_KEY} \
    AZURE_OPENAI_ENDPOINT=${AZURE_OPENAI_ENDPOINT} \
    AZURE_DEPLOYMENT_NAME=${AZURE_DEPLOYMENT_NAME} \
    AZURE_API_VERSION="2025-01-01-preview"

# Expose the Streamlit port
EXPOSE 8501

# Set health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Run the application with reduced privileges
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.enableCORS=false", "--server.enableXsrfProtection=true"] 