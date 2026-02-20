# Mini V2X Performance & Edge Connectivity Testbed

**A containerized, web-controlled simulation environment for testing Vehicle-to-Infrastructure (V2I) communication performance without expensive real-world deployments.**

## Purpose & Impact

### What It Does
This testbed **simulates and measures** the performance of connected vehicle communication between:
- **Vehicle Node** (On-Board Unit simulator) → Sends telemetry & safety messages
- **Edge Server** (Roadside Unit/Infrastructure) → Receives and analyzes messages

### Why It Matters
**Traditional V2X testing requires:**
- Expensive roadside infrastructure ($10K-$100K per RSU)
- Real vehicles with OBUs
- Physical test tracks or roads
- Significant setup and logistics time

**This testbed provides:**
- ✅ **$0 infrastructure cost** - Runs on any Linux machine with Docker
- ✅ **Instant setup** - Deploy in 5 minutes
- ✅ **Repeatable tests** - Exact network conditions, no environmental variance
- ✅ **Safe experimentation** - Test extreme conditions (severe packet loss, high latency)
- ✅ **Educational tool** - Learn V2X concepts without real equipment

### Who It's For
- **Researchers** - Protocol comparison, network optimization studies
- **Educators** - Teaching V2X communication concepts
- **V2X Developers** - Testing applications before field deployment
- **Network Planners** - Modeling edge infrastructure requirements

### Real-World Applications
- **5G V2X Research**: Test MEC (Multi-access Edge Computing) latency requirements
- **Safety Message Delivery**: Validate critical alert transmission under poor network conditions
- **Protocol Selection**: Compare UDP, TCP, and MQTT for different V2X use cases
- **Network Capacity Planning**: Determine infrastructure needs before deployment
- **ML/AI Training**: Generate labeled datasets for predictive models

## How It Works

```
┌─────────────────────────────────────────────────────────┐
│                  Your Linux Machine                      │
│                                                           │
│  ┌──────────────┐         ┌──────────────┐              │
│  │ Vehicle Node │ ──────→ │ Edge Server  │              │
│  │  (Sender)    │  UDP/   │ (Receiver)   │              │
│  │              │  TCP/   │              │              │
│  │ Simulates:   │  MQTT   │ Simulates:   │              │
│  │ • OBU        │         │ • RSU        │              │
│  │ • Telemetry  │         │ • MEC Node   │              │
│  │ • Safety     │         │ • 5G Edge    │              │
│  └──────────────┘         └──────┬───────┘              │
│                                   │                       │
│  ┌──────────────────────────────┴───────────────────┐  │
│  │         Network Simulation (tc)                   │  │
│  │  • Delay (0-300ms)                                │  │
│  │  • Packet Loss (0-30%)                            │  │
│  │  • Bandwidth Limits (2-15 Mbps)                   │  │
│  │  • Jitter, Reordering                             │  │
│  └───────────────────────────────────────────────────┘  │
│                                                           │
│  ┌──────────────────────────────────────────────────┐  │
│  │    Web Dashboard (http://localhost:8501)          │  │
│  │  • Run experiments from browser                   │  │
│  │  • Real-time metrics & charts                     │  │
│  │  • Historical results viewer                      │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### What Gets Tested
✅ **End-to-End Latency** - Time from vehicle send → infrastructure receive
✅ **Packet Loss** - Message delivery reliability under degradation
✅ **Throughput** - Message rate and bandwidth utilization
✅ **Protocol Performance** - UDP vs TCP vs MQTT comparison
✅ **Network Resilience** - Behavior during cell handoffs
✅ **Jitter** - Variance in latency (critical for safety messages)

### What It Does NOT Test
❌ **Vehicle-to-Vehicle (V2V)** - Only tests Vehicle-to-Infrastructure (V2I)
❌ **Real RF propagation** - Network simulation via software (tc), not radio
❌ **GPS accuracy** - Simulated vehicle position
❌ **Real-time OS** - Uses standard Linux, not automotive RTOS

## Features

- **UI-Based Test Control**: Run experiments directly from the dashboard - no CLI required
- **Multi-Protocol Support**: UDP, TCP, and MQTT
- **Network Simulation**: Linux `tc` traffic shaping (delay, jitter, packet loss, bandwidth limits)
- **Real-Time Metrics**: Latency, jitter, packet loss, throughput
- **Real-Time Progress Tracking**: Monitor running experiments with live phase indicators
- **Packet Capture**: tcpdump integration with PCAP analysis
- **Analytics Pipeline**: KPI calculation and visualization
- **Live Dashboard**: Streamlit-based real-time monitoring with multi-page navigation
- **Results Viewer**: Browse historical experiments and download reports
- **ML Extension**: Predictive models for performance degradation

## Prerequisites

- Linux system (Ubuntu 20.04+ recommended)
- Docker and Docker Compose
- Root access (for network shaping with `tc`)
- 4GB+ RAM recommended

## Quick Start

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

You'll see:
- **Main Dashboard**: Real-time metrics and visualizations
- **🎮 Test Control Center**: Run experiments from the UI
- **📈 Results Viewer**: Browse completed experiments

## Running Experiments

### Method 1: UI-Based Control (Recommended - No CLI Required!)

The easiest way to run experiments is through the **Test Control Center**:

1. **Open Dashboard**: Navigate to http://localhost:8501
2. **Click "🎮 Test Control Center"** (top navigation or sidebar)
3. **Configure Experiment**:
   - Enter experiment name (or use auto-generated)
   - Set duration (10-300 seconds)
   - Select network profile (normal/moderate/severe/handoff)
   - Choose protocols to test
4. **Click "🚀 Start Experiment"**
5. **Monitor Progress**: Watch real-time progress bar and phase indicators
6. **View Results**: Automatically displayed when complete, or browse via "📈 Results Viewer"

**Features:**
- ✅ No command-line interaction needed
- ✅ Real-time progress tracking with phase indicators
- ✅ Automatic analytics generation
- ✅ Browse historical experiments
- ✅ Download reports (JSON, CSV, PCAP)
- ✅ One-click result viewing
- ✅ Queue management (one test at a time)

### Method 2: Automated Script (CLI)

For automation or CI/CD integration, use the experiment runner script:

```bash
# Make script executable (first time only)
chmod +x run_experiment.sh

# Run experiment: ./run_experiment.sh <name> <duration> <profile>
sudo ./run_experiment.sh my_test 60 moderate
```

This will:
1. Start all services
2. Clear existing data
3. Apply network profile
4. Start packet capture
5. Run for specified duration
6. Generate analytics and visualizations
7. Clean up and save results to `outputs/my_test/`

**Output includes:**
- `kpi_report.json` - Complete metrics
- `messages.csv` - Raw data
- `*.png` - Visualization charts
- `capture.pcap` - Packet capture
- `pcap_analysis.json` - Network analysis

### Method 3: Manual Step-by-Step (Advanced)

For maximum control, run each step manually:

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
   docker-compose run --rm analytics python kpi_calculator.py /data/v2x_testbed.db /outputs
   docker-compose run --rm analytics python visualize.py /data/v2x_testbed.db /outputs
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

## Control Center UI Guide

### Overview

The Control Center provides a complete web-based interface for managing experiments without touching the command line.

### Test Control Page

**Access:** http://localhost:8501 → Click "🎮 Test Control Center"

**Features:**

1. **Experiment Configuration**
   - **Name**: Auto-generated or custom (alphanumeric + underscores only)
   - **Duration**: 10-300 seconds slider
   - **Network Profile**: Dropdown selection
     - Normal: Baseline (no degradation)
     - Moderate: 50ms delay, 1% loss
     - Severe: 200ms delay, 10% loss
     - Handoff: Multi-phase cell tower handoff simulation
   - **Protocols**: Multi-select (UDP/TCP/MQTT)
   - **Advanced Options**: Coming soon (custom delay/loss, PCAP control)

2. **Active Experiment Monitor**
   - Real-time progress bar (0-100%)
   - Current phase indicator:
     - 🔄 Initializing
     - 🚀 Starting services
     - 🧹 Clearing data
     - 🌐 Applying network profile
     - 📦 Capturing packets
     - ⚡ Running experiment
     - 🛑 Stopping capture
     - 📊 Analyzing results
     - 📈 Parsing PCAP
     - ✅ Completed
   - Elapsed and remaining time
   - Cancel button (graceful shutdown)

3. **Recent Experiments List**
   - Status badges (Running, Completed, Failed, Cancelled)
   - Filter by status
   - Quick "View Results" button
   - Error details for failed experiments

### Results Viewer Page

**Access:** http://localhost:8501 → Click "📈 Results Viewer"

**Features:**

1. **Experiment Selector**
   - Dropdown of all completed experiments
   - Shows name, profile, and timestamp

2. **Performance Metrics Dashboard**
   - **Latency**: Avg, Median, P95, P99, Min, Max, StdDev, Jitter
   - **Reliability**: Packet loss rate, total lost packets
   - **Throughput**: Messages/sec, Bytes/sec, Kbps, Mbps
   - **Protocol Comparison**: Side-by-side table

3. **Visualizations**
   - Latency over time
   - Latency distribution
   - Protocol comparison charts
   - Message type comparison
   - Packet loss over time

4. **Download Options**
   - 📄 JSON Report - Full KPI metrics
   - 📊 CSV Data - Raw message data
   - 📦 PCAP File - Network packet capture

5. **Coming Soon**
   - Multi-experiment comparison
   - Statistical significance testing
   - Export to PDF reports

### Queue Management

**Important:** Only one experiment can run at a time to prevent:
- Network profile conflicts (multiple tc rules)
- PCAP file collisions
- Resource contention

If you try to start a second experiment while one is running:
- ❌ Request blocked with clear message
- ℹ️ Shows which experiment is currently running
- 💡 Suggests waiting for completion

### Architecture

```
┌─────────────────────────────────────┐
│   Streamlit Dashboard (Port 8501)   │
│  ┌──────────┐  ┌──────────────┐    │
│  │ Metrics  │  │Test Control  │    │
│  │Dashboard │  │   Center     │    │
│  └──────────┘  └──────────────┘    │
│  ┌──────────────────────────────┐  │
│  │   Results Viewer             │  │
│  └──────────────────────────────┘  │
└──────────────┬──────────────────────┘
               │
               ▼
    ┌──────────────────────┐
    │  TestOrchestrator    │
    │  (test_runner.py)    │
    │  - Subprocess mgmt   │
    │  - Progress tracking │
    │  - State management  │
    └──────────────────────┘
               │
    ┌──────────┴──────────┐
    ▼                     ▼
┌────────────┐    ┌──────────────┐
│run_experiment│    │experiment_runs│
│.sh script   │    │table (SQLite)│
└────────────┘    └──────────────┘
```

### Database Tables

**New table:** `experiment_runs`
- Tracks all experiments (pending, running, completed, failed, cancelled)
- Stores configuration, progress, timestamps, error messages
- Enables historical browsing and state recovery

**Existing tables:**
- `messages` - Message data with latency metrics
- `network_conditions` - Applied network profiles
- `pcap_sessions` - Packet capture metadata

## Analytics

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

## ML Extension (Optional)

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

## Key Performance Indicators (KPIs)

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

## Repository Structure

```
mini-v2x-testbed/
├── vehicle_node/          # OBU simulator
│   ├── sender.py
│   ├── config.yaml
│   └── Dockerfile
├── edge_server/           # Message receiver
│   ├── receiver.py
│   ├── database.py        # UPDATED: Added experiment_runs table
│   ├── metrics.py
│   └── Dockerfile
├── network_profiles/      # Traffic shaping scripts
│   ├── normal.sh
│   ├── moderate.sh
│   ├── severe.sh
│   ├── handoff.sh
│   └── clear.sh
├── analytics/             # KPI calculation & visualization
│   ├── kpi_calculator.py
│   ├── visualize.py
│   ├── parser.py
│   └── Dockerfile
├── dashboard/             # Streamlit dashboard (ENHANCED)
│   ├── app.py             # UPDATED: Added navigation
│   ├── test_runner.py     # NEW: Test orchestration
│   ├── pages/             # NEW: Multi-page app
│   │   ├── 1_🎮_Test_Control.py   # NEW: Control center UI
│   │   └── 2_📈_Results_Viewer.py # NEW: Results browser
│   ├── requirements.txt
│   └── Dockerfile         # UPDATED: System dependencies
├── ml_extension/          # ML prediction models
│   ├── train_model.py
│   └── predict.py
├── data/                  # Database storage
│   └── v2x_testbed.db     # UPDATED: New experiment_runs table
├── outputs/               # Analysis results (per experiment)
│   └── <experiment_name>/
│       ├── kpi_report.json
│       ├── messages.csv
│       ├── *.png
│       └── capture.pcap
├── run_experiment.sh      # UPDATED: Progress markers added
├── docker-compose.yml     # UPDATED: Dashboard with NET_ADMIN
└── README.md              # UPDATED: Control center docs
```

**Key Changes:**
- ✨ `dashboard/test_runner.py` - New test orchestration engine
- ✨ `dashboard/pages/` - Multi-page Streamlit app structure
- 🔧 `edge_server/database.py` - Extended with experiment tracking
- 🔧 `run_experiment.sh` - Instrumented with progress markers
- 🔧 `docker-compose.yml` - Dashboard with NET_ADMIN capability

## Network Shaping Details

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

## Troubleshooting

### Control Center Issues

#### "Experiment blocked - another test is running"
- Only one experiment can run at a time
- Wait for current test to complete (check progress bar)
- Or cancel the running experiment (use 🛑 Cancel button)

#### Experiment stuck at a phase
1. Check dashboard container logs:
   ```bash
   docker-compose logs -f dashboard
   ```
2. Look for error messages in the experiment list (Failed status)
3. Cancel and retry
4. Verify network profiles cleared: `sudo bash network_profiles/clear.sh`

#### Progress bar not updating
- Refresh browser (F5)
- Check if experiment process is still running:
  ```bash
  docker-compose exec dashboard ps aux | grep run_experiment
  ```
- Dashboard auto-refreshes every 2 seconds during tests

#### Results not appearing
- Wait 30 seconds after completion for analytics generation
- Check outputs directory exists:
  ```bash
  ls -la outputs/<experiment_name>/
  ```
- Verify analytics container ran:
  ```bash
  docker-compose logs analytics
  ```

#### "Permission denied" for network profiles
- Dashboard container needs NET_ADMIN capability
- Check docker-compose.yml has `cap_add: [NET_ADMIN]`
- Rebuild dashboard:
  ```bash
  docker-compose build dashboard
  docker-compose up -d dashboard
  ```

### General Issues

#### Permission denied when running tc scripts (CLI method)
```bash
# Run with sudo
sudo bash network_profiles/moderate.sh
```

#### No data in dashboard
- Ensure vehicle_node and edge_server are running
- Check logs: `docker-compose logs -f edge_server`
- Verify database: `sqlite3 data/v2x_testbed.db "SELECT COUNT(*) FROM messages;"`
- Restart vehicle node: `docker-compose restart vehicle_node`

#### High packet loss with normal profile
- Clear existing tc rules: `sudo bash network_profiles/clear.sh`
- Check network interface: Ensure scripts use correct interface (default: eth0)

#### Container networking issues
- Verify network: `docker network inspect mini-v2x-testbed_v2x_network`
- Restart services: `docker-compose restart`

#### Dashboard pages not showing (404)
- Ensure pages directory exists: `dashboard/pages/`
- Rebuild dashboard: `docker-compose build dashboard`
- Check that both page files exist:
  - `1_🎮_Test_Control.py`
  - `2_📈_Results_Viewer.py`

## References

- **V2X Communication**: 3GPP TS 23.285
- **Linux Traffic Control**: `man tc-netem`
- **PCAP Analysis**: Wireshark documentation

## Contributing

Contributions welcome! Focus areas:
- Additional network profiles
- Enhanced ML models
- Real vehicle data integration
- 5G NR simulation

## License

MIT License - See LICENSE file

## Acknowledgments

Built for V2X research and education. Not intended for production deployment.
