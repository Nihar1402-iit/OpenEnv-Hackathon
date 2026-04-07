FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies with network resilience
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir --default-timeout 100 -r requirements.txt

# Copy app code
COPY app/ ./app/
COPY openenv.yaml .
COPY app.py .
COPY hf_spaces_run.py .

# Expose port 7860 for Hugging Face Spaces
EXPOSE 7860

# Health check with curl
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:7860/health || exit 1

# Run FastAPI app on port 7860 for HF Spaces compatibility
CMD ["python", "hf_spaces_run.py"]
