FROM python:3.12-slim

# Install ffmpeg for audio extraction and format merging
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first (better Docker cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Render sets PORT env var; default to 5050 for local dev
EXPOSE ${PORT:-5050}

# Run the FastAPI app
CMD ["python", "-m", "app.app"]
