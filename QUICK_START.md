# Quick Start Guide

## 📁 Repository Location
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
- ✅ ML Extension (Predictive models)
- ✅ Docker Infrastructure (Complete docker-compose setup)

### Total Files Created: 28+

## 🚀 Instant Commands

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

### 2. Basic Workflow (Linux only)

```bash
# Start services
docker-compose up -d

# Wait 10 seconds for data collection
sleep 10

# View real-time data
docker-compose logs -f vehicle_node

# Generate analytics
docker-compose run --rm analytics python kpi_calculator.py
docker-compose run --rm analytics python visualize.py

# View results
ls -lh outputs/
```

### 3. Stop Services
```bash
docker-compose down
```

## 🌐 Access Points

- **Dashboard**: http://localhost:8501
- **MQTT Broker**: localhost:1883
- **Edge Server UDP**: localhost:5000/udp
- **Edge Server TCP**: localhost:5000/tcp

## 📊 Generated Outputs

After running analytics:
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

## 🔧 Testing Without Linux (Limited)

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

## 🎯 Full Experiment (Linux Required)

```bash
# Make script executable
chmod +x run_experiment.sh

# Run automated experiment
sudo ./run_experiment.sh my_test 60 moderate

# Results appear in: outputs/my_test/
```

## 🔍 Quick Verification

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

## 🎓 Next Steps

1. **Read README.md** - Complete documentation
2. **Explore vehicle_node/config.yaml** - Change protocol (UDP/TCP/MQTT)
3. **Try network profiles** - Apply degradation (Linux only)
4. **View dashboard** - Monitor real-time metrics
5. **Generate analytics** - Create KPI reports
6. **Train ML models** - Predict performance

## 🐛 Troubleshooting

### Services won't start
```bash
docker-compose down
docker-compose up --build
```

### No data in dashboard
```bash
# Check if services are running
docker-compose ps

# Check vehicle node logs
docker-compose logs vehicle_node

# Restart vehicle node
docker-compose restart vehicle_node
```

### Database locked
```bash
# Stop all services
docker-compose down

# Remove database
rm data/v2x_testbed.db

# Restart
docker-compose up -d
```

## 📚 Architecture

```
Vehicle Node (Sender)
        ↓ UDP/TCP/MQTT
Edge Server (Receiver) → SQLite Database
        ↓
   Dashboard (Streamlit)
        ↓
  Analytics Engine → Visualizations
```

## 🎉 Success Criteria

✅ Dashboard shows live data
✅ Messages counter increases
✅ Latency metrics display
✅ Analytics generate plots
✅ Database contains messages

---

**Repository**: Fully implemented and ready to use!
**Platform**: Linux required for full features
**Docker**: All services containerized
**Documentation**: Complete README.md provided
