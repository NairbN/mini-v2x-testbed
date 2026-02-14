FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy analytics scripts
COPY parser.py .
COPY kpi_calculator.py .
COPY visualize.py .

# Create directories
RUN mkdir -p /data /outputs /pcaps

CMD ["python", "kpi_calculator.py"]
