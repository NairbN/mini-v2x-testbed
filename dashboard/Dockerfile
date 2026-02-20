FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for network shaping and packet capture
RUN apt-get update && apt-get install -y \
    iproute2 \
    tcpdump \
    sqlite3 \
    jq \
    bash \
    docker.io \
    sudo \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy dashboard application files
COPY app.py .
COPY test_runner.py .
COPY pages/ ./pages/

# Create necessary directories
RUN mkdir -p /data /outputs /network_profiles

# Expose Streamlit port
EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
