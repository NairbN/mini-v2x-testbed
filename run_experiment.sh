#!/bin/bash
# Automated experiment runner

set -e

EXPERIMENT_NAME="${1:-experiment_$(date +%s)}"
DURATION="${2:-60}"
NETWORK_PROFILE="${3:-moderate}"

echo "========================================="
echo "V2X Testbed Experiment Runner"
echo "========================================="
echo "Experiment: $EXPERIMENT_NAME"
echo "Duration: $DURATION seconds"
echo "Network Profile: $NETWORK_PROFILE"
echo "========================================="

# Create experiment directory
EXPERIMENT_DIR="outputs/$EXPERIMENT_NAME"
mkdir -p "$EXPERIMENT_DIR"

# Start services
echo "Starting services..."
docker-compose up -d
sleep 5

# Clear existing data
echo "Clearing previous data..."
docker-compose exec -T edge_server sqlite3 /data/v2x_testbed.db "DELETE FROM messages; DELETE FROM network_conditions;"

# Apply network profile
echo "Applying network profile: $NETWORK_PROFILE..."
sudo bash "network_profiles/${NETWORK_PROFILE}.sh"

# Start packet capture
PCAP_FILE="$EXPERIMENT_DIR/capture.pcap"
echo "Starting packet capture: $PCAP_FILE"
sudo tcpdump -i eth0 port 5000 -w "$PCAP_FILE" &
TCPDUMP_PID=$!

# Run experiment
echo "Running experiment for $DURATION seconds..."
sleep "$DURATION"

# Stop packet capture
echo "Stopping packet capture..."
sudo kill $TCPDUMP_PID 2>/dev/null || true

# Clear network profile
echo "Clearing network profile..."
sudo bash network_profiles/clear.sh

# Generate analytics
echo "Generating analytics..."
docker-compose run --rm analytics python kpi_calculator.py /data/v2x_testbed.db "/outputs/$EXPERIMENT_NAME"
docker-compose run --rm analytics python visualize.py /data/v2x_testbed.db "/outputs/$EXPERIMENT_NAME"

# Parse PCAP
if [ -f "$PCAP_FILE" ]; then
    echo "Parsing PCAP file..."
    docker-compose run --rm analytics python parser.py "/outputs/$EXPERIMENT_NAME/capture.pcap" "/outputs/$EXPERIMENT_NAME/pcap_analysis.json"
fi

echo "========================================="
echo "Experiment complete!"
echo "Results saved to: $EXPERIMENT_DIR"
echo "========================================="

# Display summary
cat "$EXPERIMENT_DIR/kpi_report.json" | jq '.overall_kpis.latency'
