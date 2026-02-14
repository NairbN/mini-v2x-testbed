FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY receiver.py .
COPY database.py .
COPY metrics.py .

# Create data directory
RUN mkdir -p /data

# Expose port
EXPOSE 5000

CMD ["python", "receiver.py"]
