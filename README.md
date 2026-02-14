# Mini V2X Performance & Edge Connectivity Testbed

A simulated Vehicle-to-Network (V2N) performance testbed that models connected vehicle communication over LTE/5G-like infrastructure.

## 🎯 Features

- **Multi-Protocol Support**: UDP, TCP, and MQTT
- **Network Simulation**: Linux `tc` traffic shaping (delay, jitter, packet loss, bandwidth limits)
- **Real-Time Metrics**: Latency, jitter, packet loss, throughput
- **Packet Capture**: tcpdump integration with PCAP analysis
- **Analytics Pipeline**: KPI calculation and visualization
- **Live Dashboard**: Streamlit-based real-time monitoring
- **ML Extension**: Predictive models for performance degradation

## 📋 Prerequisites

- Linux system (Ubuntu 20.04+ recommended)
- Docker and Docker Compose
- Root access (for network shaping with `tc`)
- 4GB+ RAM recommended

## 🚀 Quick Start

### 1. Clone Repository

```bash
cd mini-v2x-testbed
```

### 2. Build and Start Services

```bash
docker-compose up --build
```

This starts:
- MQTT Broker (port 1883)
- Edge Server (port 5000)
- Vehicle Node (sending messages)
- Dashboard (http://localhost:8501)

### 3. Access Dashboard

Open your browser to:
```
http://localhost:8501
```

## 🧪 Running Experiments

### Basic Experiment Workflow

1. **Start the testbed**:
   ```bash
   docker-compose up -d
   ```

2. **Apply network degradation** (requires root):
   ```bash
   sudo bash network_profiles/moderate.sh
   ```

3. **Capture packets**:
   ```bash
   sudo tcpdump -i eth0 port 5000 -w pcaps/experiment_$(date +%s).pcap
   ```

4. **Run for desired duration** (e.g., 60 seconds):
   ```bash
   sleep 60
   ```

5. **Stop packet capture**: `Ctrl+C`

6. **Clear network shaping**:
   ```bash
   sudo bash network_profiles/clear.sh
   ```

7. **Generate analytics**:
   ```bash
   docker-compose run --rm analytics python kpi_calculator.py
   docker-compose run --rm analytics python visualize.py
   ```

8. **View results**: Check `./outputs/` directory

### Network Profiles

Apply different network conditions:

```bash
# Normal (no degradation)
sudo bash network_profiles/normal.sh

# Moderate congestion (50ms delay, 1% loss)
sudo bash network_profiles/moderate.sh

# Severe degradation (200ms delay, 10% loss)
sudo bash network_profiles/severe.sh

# Handoff scenario (simulates cell tower handoff)
sudo bash network_profiles/handoff.sh

# Clear all rules
sudo bash network_profiles/clear.sh
```

### Changing Protocol

Edit `vehicle_node/config.yaml`:

```yaml
vehicle:
  protocol: "TCP"  # Options: UDP, TCP, MQTT
```

Then restart:
```bash
docker-compose restart vehicle_node
```

## 📊 Analytics

### Generate KPI Report

```bash
docker-compose run --rm analytics python kpi_calculator.py /data/v2x_testbed.db /outputs
```

Outputs:
- `outputs/kpi_report.json` - Full KPI report
- `outputs/messages.csv` - Raw message data
- `outputs/latency_by_protocol.csv` - Latency summary

### Generate Visualizations

```bash
docker-compose run --rm analytics python visualize.py /data/v2x_testbed.db /outputs
```

Generates:
- `latency_over_time.png`
- `latency_distribution.png`
- `protocol_comparison.png`
- `message_type_comparison.png`
- `packet_loss_over_time.png`

### Parse PCAP Files

```bash
docker-compose run --rm analytics python parser.py /pcaps/experiment_*.pcap /outputs/pcap_analysis.json
```

## 🤖 ML Extension (Optional)

### Train Prediction Models

```bash
docker-compose run --rm analytics python /app/ml_extension/train_model.py /data/v2x_testbed.db
```

Outputs:
- `outputs/latency_model.pkl` - Latency prediction model
- `outputs/loss_model.pkl` - Packet loss classifier

### Make Predictions

```python
from ml_extension.predict import V2XPredictor

predictor = V2XPredictor('/outputs')
predicted_latency = predictor.predict_latency(
    protocol='UDP',
    message_type='telemetry',
    latency_rolling_mean=25.0,
    latency_rolling_std=5.0,
    hour=14,
    minute=30
)
```

## 🔍 Key Performance Indicators (KPIs)

### Latency
- **Average Latency**: Mean end-to-end latency
- **P95 Latency**: 95th percentile (excludes outliers)
- **P99 Latency**: 99th percentile (worst-case scenarios)

**Calculation**: `receive_timestamp - send_timestamp`

### Jitter
- **Definition**: Variance in latency
- **Calculation**: Standard deviation of inter-arrival times

### Packet Loss
- **Detection**: Sequence gap tracking
- **Calculation**: `(total_gaps / total_expected) * 100`

### Throughput
- **Messages/sec**: `total_messages / time_span`
- **Bytes/sec**: `total_bytes / time_span`
- **Kbps**: `(bytes_per_sec * 8) / 1000`

## 🗂️ Repository Structure

```
mini-v2x-testbed/
├── vehicle_node/          # OBU simulator
├── edge_server/           # Message receiver
├── network_profiles/      # Traffic shaping scripts
├── analytics/             # KPI calculation & visualization
├── dashboard/             # Streamlit dashboard
├── ml_extension/          # ML prediction models
├── data/                  # Database storage
├── pcaps/                 # Packet captures
├── outputs/               # Analysis results
└── docker-compose.yml
```

## 📡 Network Shaping Details

### Moderate Profile
- Delay: 50ms ± 10ms
- Packet Loss: 1%
- Bandwidth: 10-15 Mbit/s

### Severe Profile
- Delay: 200ms ± 50ms
- Packet Loss: 10% (25% correlation)
- Bandwidth: 2-5 Mbit/s
- Reordering: 5%

### Handoff Scenario
- **Phase 1** (2s): Normal (30ms, 0.5% loss)
- **Phase 2** (3s): Disruption (300ms, 30% loss)
- **Phase 3** (2s): Recovery (50ms, 2% loss)
- **Phase 4**: Stabilized (25ms, 0.5% loss)

## 🛠️ Troubleshooting

### Permission denied when running tc scripts
```bash
# Run with sudo
sudo bash network_profiles/moderate.sh
```

### No data in dashboard
- Ensure vehicle_node and edge_server are running
- Check logs: `docker-compose logs -f edge_server`
- Verify database: `sqlite3 data/v2x_testbed.db "SELECT COUNT(*) FROM messages;"`

### High packet loss with normal profile
- Clear existing tc rules: `sudo bash network_profiles/clear.sh`
- Check network interface: Ensure scripts use correct interface (default: eth0)

### Container networking issues
- Verify network: `docker network inspect mini-v2x-testbed_v2x_network`
- Restart services: `docker-compose restart`

## 📚 References

- **V2X Communication**: 3GPP TS 23.285
- **Linux Traffic Control**: `man tc-netem`
- **PCAP Analysis**: Wireshark documentation

## 🤝 Contributing

Contributions welcome! Focus areas:
- Additional network profiles
- Enhanced ML models
- Real vehicle data integration
- 5G NR simulation

## 📄 License

MIT License - See LICENSE file

## ✨ Acknowledgments

Built for V2X research and education. Not intended for production deployment.
