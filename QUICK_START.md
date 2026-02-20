# Quick Start Guide

## Repository Location
```
C:\Users\Brian\Workspace\Mini V2X Performance & Edge Connectivity Testbed
```

## ✅ What Was Created

### Complete V2X Testbed Implementation
- ✅ Vehicle Node (OBU Simulator) - UDP/TCP/MQTT support
- ✅ Edge Server (Message Receiver) - Real-time metrics
- ✅ Network Profiles (5 traffic shaping scripts)
- ✅ Analytics Engine (KPI calculator, visualizer, PCAP parser)
- ✅ Dashboard (Streamlit real-time monitoring)
- ✅ **🎮 Control Center UI** - Run tests from browser (NEW!)
- ✅ **📈 Results Viewer** - Browse experiment history (NEW!)
- ✅ **Test Orchestrator** - Background process management (NEW!)
- ✅ ML Extension (Predictive models)
- ✅ Docker Infrastructure (Complete docker-compose setup)

### Total Files Created: 35+ (7 new files for Control Center)

## Instant Commands

### 1. Start Everything (Windows with Docker Desktop + WSL2)

**Note**: This system requires Linux for network shaping. You have two options:

#### Option A: Run in WSL2 (Recommended)
```bash
# Open WSL2 terminal
cd "/mnt/c/Users/Brian/Workspace/Mini V2X Performance & Edge Connectivity Testbed"

# Start services
docker-compose up --build -d

# View dashboard
# Open browser to: http://localhost:8501
```

#### Option B: Use Linux VM or Cloud Instance
- Transfer repository to Linux machine
- Run commands there

### 2. UI-Based Workflow (Recommended - No CLI!)

**NEW: Run tests from the browser!**

```bash
# 1. Start services
docker-compose up -d

# 2. Open browser to http://localhost:8501

# 3. Click "🎮 Test Control Center"

# 4. Configure and run experiment:
#    - Name: test_1
#    - Duration: 30 seconds
#    - Profile: moderate
#    - Click "🚀 Start Experiment"

# 5. Watch real-time progress bar

# 6. View results when complete
```

**Features:**
- ✅ No command line needed
- ✅ Real-time progress tracking
- ✅ Automatic analytics generation
- ✅ One-click result viewing
- ✅ Download reports (JSON/CSV/PCAP)

### 3. CLI Workflow (Alternative)

For automation or scripting:

```bash
# Automated experiment runner
sudo ./run_experiment.sh my_test 60 moderate

# Results saved to: outputs/my_test/
```

### 4. Manual Workflow (Advanced)

For maximum control:

```bash
# Start services
docker-compose up -d

# Wait 10 seconds for data collection
sleep 10

# View real-time data
docker-compose logs -f vehicle_node

# Generate analytics manually
docker-compose run --rm analytics python kpi_calculator.py /data/v2x_testbed.db /outputs
docker-compose run --rm analytics python visualize.py /data/v2x_testbed.db /outputs

# View results
ls -lh outputs/
```

### 5. Stop Services
```bash
docker-compose down
```

## Access Points

### Web UI (Main Interface)
- **Main Dashboard**: http://localhost:8501
  - Real-time metrics and visualizations
  - Live data monitoring
- **🎮 Test Control Center**: http://localhost:8501 → Click "Test Control" or use sidebar
  - Configure and launch experiments
  - Monitor running tests
  - View experiment history
- **📈 Results Viewer**: http://localhost:8501 → Click "Results Viewer" or use sidebar
  - Browse completed experiments
  - View detailed KPIs
  - Download reports

### Backend Services
- **MQTT Broker**: localhost:1883
- **Edge Server UDP**: localhost:5000/udp
- **Edge Server TCP**: localhost:5000/tcp
- **Database**: `data/v2x_testbed.db` (SQLite)

## Control Center Quick Guide

### Running Your First Test

1. **Open Dashboard**: http://localhost:8501
2. **Navigate to Test Control**: Click "🎮 Test Control Center" button
3. **Configure Experiment**:
   ```
   Experiment Name: test_run_1 (or auto-generated)
   Duration: 30 seconds (start small)
   Network Profile: moderate
   Protocols: UDP, TCP, MQTT (all selected)
   ```
4. **Launch**: Click "🚀 Start Experiment"
5. **Monitor**: Watch real-time progress (initializing → running → analyzing → completed)
6. **View Results**: Click "📈 View Results" button when complete

### What You'll See

**During Experiment:**
- Progress bar (0-100%)
- Current phase indicator:
  - 🔄 Initializing
  - 🌐 Applying network profile
  - ⚡ Running (with elapsed/remaining time)
  - 📊 Analyzing
  - ✅ Completed
- Cancel button (graceful shutdown)

**After Completion:**
- Experiment appears in "Recent Experiments" list
- Status: ✅ Completed
- "View Results" button becomes active

### Viewing Results

1. **Click "📈 Results Viewer"** (or click "View Results" on completed experiment)
2. **Select experiment** from dropdown
3. **Review metrics**:
   - Latency: Avg, P95, P99
   - Packet Loss: Rate and total
   - Throughput: msg/s, Mbps
   - Protocol comparison table
4. **View charts**: Latency over time, distributions, comparisons
5. **Download**: JSON report, CSV data, PCAP file

### Queue Management

⚠️ **Important**: Only one experiment runs at a time

If you try to start a second test while one is running:
- ❌ Blocked with message: "Experiment 'xxx' is already running"
- 💡 Wait for completion or cancel the current test

## Generated Outputs

After running experiments (automatically generated by Control Center):
```
outputs/
├── kpi_report.json              # Full KPI metrics
├── messages.csv                 # Raw message data
├── latency_by_protocol.csv      # Protocol comparison
├── latency_over_time.png        # Latency graph
├── latency_distribution.png     # Distribution plot
├── protocol_comparison.png      # Protocol metrics
├── message_type_comparison.png  # Telemetry vs Safety
└── packet_loss_over_time.png    # Loss graph
```

## Testing Without Linux (Limited)

You can still test the Docker services on Windows:

```bash
# Start services (no network shaping)
docker-compose up --build

# View dashboard
# Browser: http://localhost:8501

# Check if data is flowing
docker-compose exec edge_server sqlite3 /data/v2x_testbed.db "SELECT COUNT(*) FROM messages;"
```

**Note**: Network shaping (`tc` commands) requires Linux kernel, so:
- ❌ Won't work on Windows
- ✅ Works on WSL2 with proper setup
- ✅ Works on native Linux
- ✅ Works on Linux VM

## Full Experiment

### Option 1: Via UI (Recommended)

**No Linux restrictions - works anywhere Docker runs!**

1. Open http://localhost:8501
2. Click "🎮 Test Control Center"
3. Configure experiment (60 seconds, moderate profile)
4. Click "🚀 Start Experiment"
5. Wait for completion
6. View results automatically

### Option 2: Via CLI (Linux Required for Network Shaping)

```bash
# Make script executable
chmod +x run_experiment.sh

# Run automated experiment
sudo ./run_experiment.sh my_test 60 moderate

# Results appear in: outputs/my_test/
```

**Note**: The UI method uses the same underlying script but handles all the complexity for you!

## Quick Verification

Check if everything is working:

```bash
# 1. Check Docker services
docker-compose ps

# 2. Check database
docker-compose exec edge_server sqlite3 /data/v2x_testbed.db "SELECT COUNT(*) FROM messages;"

# 3. View recent messages
docker-compose exec edge_server sqlite3 /data/v2x_testbed.db "SELECT message_id, latency_ms FROM messages LIMIT 5;"

# 4. Check logs
docker-compose logs vehicle_node | tail -20
```

## Next Steps

### Quick Wins (Start Here!)

1. **🎮 Run Your First Test** - Use Test Control Center (http://localhost:8501)
   - Configure 30-second experiment
   - Watch real-time progress
   - View results automatically

2. **📈 Explore Results** - Browse completed experiments
   - View detailed metrics
   - Compare protocol performance
   - Download reports

3. **🔄 Try Different Profiles** - Test all network conditions
   - Normal (baseline)
   - Moderate (typical congestion)
   - Severe (degraded network)
   - Handoff (cell tower switching)

### Advanced Exploration

4. **Read README.md** - Complete documentation and architecture
5. **Explore vehicle_node/config.yaml** - Change protocol (UDP/TCP/MQTT)
6. **Try CLI workflow** - Use `run_experiment.sh` for automation
7. **View live dashboard** - Monitor real-time metrics on main page
8. **Train ML models** - Predict performance degradation

## Troubleshooting

### Control Center Issues

#### Can't start experiment - "another test is running"
```
Only one experiment runs at a time
Solution: Wait for current test to finish or click "🛑 Cancel"
```

#### Progress bar stuck or not updating
```bash
# Refresh browser (F5)
# Or check dashboard logs
docker-compose logs -f dashboard
```

#### Results not showing after completion
```bash
# Wait 30 seconds for analytics to finish
# Check if analytics ran successfully
docker-compose logs analytics

# Verify output directory exists
ls outputs/<experiment_name>/
```

#### "View Results" button not working
```
Make sure experiment status is "completed" (✅)
Try navigating directly to Results Viewer page
```

#### Pages not appearing (404)
```bash
# Rebuild dashboard with new pages
docker-compose build dashboard
docker-compose up -d dashboard
```

### General Issues

#### Services won't start
```bash
docker-compose down
docker-compose up --build
```

#### No data in dashboard
```bash
# Check if services are running
docker-compose ps

# Check vehicle node logs
docker-compose logs vehicle_node

# Restart vehicle node
docker-compose restart vehicle_node
```

#### Database locked
```bash
# Stop all services
docker-compose down

# Remove database (WARNING: Deletes all data)
rm data/v2x_testbed.db

# Restart
docker-compose up -d
```

#### Network shaping not working (CLI method)
```
Network shaping requires Linux kernel
- ✅ Works on: WSL2, Linux VM, native Linux
- ❌ Won't work on: Windows, macOS (without VM)
- Control Center handles this automatically when available
```

## Architecture

```
Vehicle Node (Sender)
        ↓ UDP/TCP/MQTT
Edge Server (Receiver) → SQLite Database
        ↓
   Dashboard (Streamlit)
        ↓
  Analytics Engine → Visualizations
```

## Success Criteria

### Core Functionality
✅ Dashboard shows live data
✅ Messages counter increases
✅ Latency metrics display
✅ Database contains messages

### Control Center (NEW!)
✅ Test Control page loads (http://localhost:8501)
✅ Can configure and start experiments
✅ Progress bar updates during test run
✅ Experiments complete successfully
✅ Results viewer shows completed tests
✅ Can download reports (JSON/CSV/PCAP)
✅ Multiple experiments can be run sequentially

### Analytics
✅ KPI reports generate automatically
✅ Visualizations appear in Results Viewer
✅ Charts load correctly (PNG files)

---

**Repository**: Fully implemented with UI Control Center!
**Platform**: Linux required for network shaping (works with WSL2)
**Docker**: All services containerized
**UI**: Complete web-based test control - no CLI needed!
**Documentation**: Complete README.md + QUICK_START.md

## Ready to Go!

**Recommended First Steps:**
1. Start services: `docker-compose up -d`
2. Open browser: http://localhost:8501
3. Click: "🎮 Test Control Center"
4. Run your first 30-second experiment
5. Explore the results!
