FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY sender.py .
COPY config.yaml /config/config.yaml

# Create data directory
RUN mkdir -p /data

CMD ["python", "sender.py"]
