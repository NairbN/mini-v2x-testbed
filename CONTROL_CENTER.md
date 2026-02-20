# Control Center User Guide

**Complete guide to running V2X experiments from the web interface**

---

## Table of Contents

1. [Overview](#overview)
2. [Getting Started](#getting-started)
3. [Test Control Center](#test-control-center)
4. [Results Viewer](#results-viewer)
5. [Understanding Phases](#understanding-phases)
6. [Network Profiles](#network-profiles)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)
9. [Architecture](#architecture)

---

## Overview

The Control Center provides a complete web-based interface for managing V2X performance experiments without requiring command-line interaction.

### Key Features

✅ **No CLI Required** - Everything runs from your browser
✅ **Real-time Progress** - Live phase tracking and progress bars
✅ **Automatic Analytics** - KPI reports and charts generated automatically
✅ **Results Browser** - View and compare historical experiments
✅ **Download Support** - Export JSON, CSV, and PCAP files
✅ **Queue Management** - One test at a time to prevent conflicts
✅ **State Persistence** - Experiment history stored in database

### Quick Access

- **Main Dashboard**: http://localhost:8501
- **Test Control**: http://localhost:8501 → Click "Test Control Center"
- **Results Viewer**: http://localhost:8501 → Click "Results Viewer"

---

## Getting Started

### Prerequisites

1. **Docker Services Running**:
   ```bash
   docker-compose up -d
   ```

2. **Verify Dashboard Access**:
   - Open http://localhost:8501
   - You should see the main dashboard with navigation buttons

3. **First Time Setup**:
   - Database tables are created automatically
   - No manual migration needed

### Your First Experiment (5 minutes)

1. Navigate to http://localhost:8501
2. Click "Test Control Center" button
3. Use the default configuration:
   - **Name**: `exp_YYYYMMDD_HHMMSS` (auto-generated)
   - **Duration**: 30 seconds
   - **Network Profile**: moderate
   - **Protocols**: UDP, TCP, MQTT
4. Click "Start Experiment"
5. Watch the progress bar advance through phases
6. When complete (✅), click "View Results"
7. Explore metrics, charts, and download options

---

## Test Control Center

### Page Layout

```
┌─────────────────────────────────────────────┐
│  Test Control Center                        │
├─────────────────────────────────────────────┤
│  New Experiment Configuration               │
│  ┌─────────────────┬─────────────────┐      │
│  │ Name            │ Profile         │      │
│  │ Duration        │ Protocols       │      │
│  └─────────────────┴─────────────────┘      │
│  Advanced Options (collapsible)             │
│  [Start Experiment]                         │
├─────────────────────────────────────────────┤
│  Active Experiment                          │
│  ┌─────────────────────────────────────┐    │
│  │ test_1                              │    │
│  │ Progress: [████████░░] 80%          │    │
│  │ Phase: analyzing                    │    │
│  │ Elapsed: 45s | Remaining: 15s       │    │
│  │ [Cancel]                            │    │
│  └─────────────────────────────────────┘    │
├─────────────────────────────────────────────┤
│  Recent Experiments                         │
│  ✅ exp_20260219_143022 - Completed         │
│  🔄 baseline_test - Running                 │
│  ❌ severe_test - Failed                    │
└─────────────────────────────────────────────┘
```

### Configuration Options

#### Experiment Name
- **Format**: Alphanumeric and underscores only (`a-z`, `A-Z`, `0-9`, `_`)
- **Default**: Auto-generated with timestamp (`exp_YYYYMMDD_HHMMSS`)
- **Requirements**:
  - Must be unique (no duplicates)
  - Max 100 characters
  - No spaces or special characters
- **Examples**:
  - ✅ `baseline_test`
  - ✅ `severe_profile_v2`
  - ✅ `exp_20260219_120000`
  - ❌ `test-with-dashes` (dashes not allowed)
  - ❌ `my test` (spaces not allowed)

#### Duration
- **Range**: 10-300 seconds (slider)
- **Default**: 60 seconds
- **Recommendations**:
  - **Quick tests**: 10-30 seconds
  - **Standard**: 60 seconds
  - **Comprehensive**: 120-300 seconds
- **Note**: Longer tests provide more data but take more time

#### Network Profile
- **Options**: normal, moderate, severe, handoff
- **Default**: moderate
- **Details**: See [Network Profiles](#network-profiles) section

#### Protocols
- **Options**: UDP, TCP, MQTT (multi-select)
- **Default**: All three selected
- **Current Behavior**: All selected protocols are tested together
- **Future**: Individual protocol selection (coming soon)

#### Advanced Options
- **Enable Packet Capture**: Toggle PCAP recording (default: ON)
- **Custom Delay/Loss**: Coming soon
- **Data Points Limit**: Coming soon

### Starting an Experiment

1. **Fill Configuration Form**
2. **Click "Start Experiment"**
3. **System Validates**:
   - ✅ Name is unique and valid
   - ✅ No experiment currently running
   - ✅ Network profile exists
   - ✅ Sufficient disk space
4. **If Validation Passes**:
   - Experiment created with status "pending"
   - Background process launches
   - Status changes to "running"
   - Progress monitor appears
5. **If Validation Fails**:
   - ❌ Error message displayed
   - Fix issue and retry

### Monitoring Active Experiments

When an experiment is running, you'll see:

#### Progress Bar
- **Visual indicator**: 0-100%
- **Color coded**: Blue (running), Green (complete), Red (error)
- **Updates**: Every 2 seconds

#### Phase Indicator
Shows current stage:
- **Initializing** (0-5%)
- **Starting services** (5-10%)
- **Clearing data** (10-20%)
- **Applying network** (20-30%)
- **Capturing** (30%)
- **Running** (30-80%)
- **Stopping capture** (80-85%)
- **Analyzing** (85-95%)
- **Parsing PCAP** (95-100%)
- ✅ **Completed** (100%)

#### Time Tracking
- **Elapsed**: Time since experiment started
- **Remaining**: Estimated time to completion
- **Note**: Estimates include analytics time (~20-30 seconds)

#### Cancel Button
- **Location**: Top-right of active experiment card
- **Action**: Gracefully terminates experiment
- **Cleanup**:
  - Stops running processes
  - Clears network profiles
  - Updates status to "cancelled"
  - Preserves partial data

### Recent Experiments List

Shows last 15 experiments with:
- **Status Badge**: Running | ✅ Completed | ❌ Failed | Cancelled | Pending
- **Name**: Experiment identifier
- **Configuration**: Network profile, duration
- **Timestamp**: When experiment was created
- **Actions**:
  - **View Results** (if completed)
  - **Error Details** (if failed)

#### Status Filter
Dropdown to filter by:
- All
- Completed
- Running
- Failed
- Cancelled
- Pending

---

## Results Viewer

### Page Layout

```
┌─────────────────────────────────────────────┐
│  Experiment Results Viewer                  │
├─────────────────────────────────────────────┤
│  Select Experiment                          │
│  [exp_20260219_143022 - moderate (...)  ▼] │
├─────────────────────────────────────────────┤
│  Experiment Details                         │
│  Name | Profile | Duration | Status         │
├─────────────────────────────────────────────┤
│  Performance Metrics                        │
│  Latency Metrics                            │
│  Avg: 45.2ms | P95: 78.5ms | P99: 120.3ms  │
│                                             │
│  Reliability & Throughput                   │
│  Loss: 1.2% | Throughput: 15.3 msg/s       │
│                                             │
│  Protocol Comparison Table                  │
├─────────────────────────────────────────────┤
│  Performance Charts                         │
│  [Latency Over Time Chart]                 │
│  [Latency Distribution Chart]              │
│  [Protocol Comparison Chart]               │
├─────────────────────────────────────────────┤
│  Export & Download                          │
│  [JSON] [CSV] [PCAP]                       │
└─────────────────────────────────────────────┘
```

### Experiment Selector

**Dropdown showing**:
- Experiment name
- Network profile
- Timestamp (YYYY-MM-DD HH:MM)

**Example**: `exp_20260219_143022 - moderate (2026-02-19 14:30)`

### Metrics Dashboard

#### Latency Metrics

**Primary Metrics** (4 cards):
- **Average Latency**: Mean end-to-end latency
- **Median Latency**: 50th percentile (typical value)
- **P95 Latency**: 95th percentile (worst-case excluding outliers)
- **P99 Latency**: 99th percentile (extreme cases)

**Additional Statistics** (expandable):
- Min Latency
- Max Latency
- Standard Deviation
- Jitter (variance in latency)

**Interpretation**:
- **Low avg (<50ms)**: Good performance
- **Moderate avg (50-100ms)**: Acceptable for most V2X
- **High avg (>100ms)**: Degraded, may impact safety messages
- **P95 > 2x avg**: High variability, investigate jitter

#### Reliability & Throughput

**Packet Loss**:
- **Loss Rate %**: Percentage of lost packets
- **Total Lost**: Absolute count
- **Calculation**: Based on sequence gap detection

**Throughput**:
- **Messages/sec**: Message delivery rate
- **Bandwidth (Mbps)**: Network utilization

**Interpretation**:
- **Loss <1%**: Excellent
- **Loss 1-5%**: Acceptable for telemetry
- **Loss >5%**: Problematic for safety messages
- **Loss >10%**: Severe degradation

#### Protocol Comparison

**Table showing per-protocol**:
- Average Latency
- P95 Latency
- Packet Loss %
- Throughput
- Jitter

**Use Cases**:
- Compare UDP vs TCP reliability
- Identify best protocol for conditions
- Analyze MQTT overhead

### Visualization Charts

#### Latency Over Time
- **Type**: Scatter plot
- **X-axis**: Time (seconds since start)
- **Y-axis**: Latency (ms)
- **Color**: By protocol (UDP/TCP/MQTT)
- **Use**: Identify latency spikes, trends

#### Latency Distribution
- **Type**: Histogram/Box plot
- **Shows**: Distribution by protocol
- **Use**: Compare protocol variance

#### Protocol Comparison
- **Type**: Bar chart
- **Metrics**: Latency, loss, throughput
- **Use**: Quick visual comparison

#### Message Type Comparison
- **Type**: Pie chart
- **Shows**: Telemetry vs Safety breakdown
- **Use**: Verify message mix

#### Packet Loss Over Time
- **Type**: Line chart
- **Shows**: Loss rate progression
- **Use**: Identify loss patterns

### Download Options

#### JSON Report
- **File**: `<experiment_name>_kpi_report.json`
- **Contents**:
  - Metadata (timestamps, config)
  - Overall KPIs
  - Protocol comparison
  - Message type comparison
- **Use**: Programmatic analysis, archival

#### CSV Data
- **File**: `<experiment_name>_messages.csv`
- **Contents**: Raw message data
  - message_id, vehicle_id, message_type
  - send_timestamp, receive_timestamp, latency_ms
  - protocol, sequence_gap, payload_size
- **Use**: Custom analysis, Excel, Python/R

#### PCAP File
- **File**: `<experiment_name>_capture.pcap`
- **Contents**: Raw network packets
- **Use**: Wireshark analysis, deep inspection
- **Size**: Can be large for long experiments

---

## Understanding Phases

### Complete Phase Breakdown

| Phase | Duration | Progress % | What's Happening |
|-------|----------|-----------|------------------|
| **Initializing** | 1-2s | 0-5% | Creating output directory, validating config |
| **Starting Services** | 3-5s | 5-10% | Ensuring all Docker containers running |
| **Clearing Data** | 1-2s | 10-20% | Deleting previous messages from database |
| **Applying Network** | 2-3s | 20-30% | Applying tc rules for network profile |
| **Capturing** | 1s | 30% | Starting tcpdump packet capture |
| **Running** | Variable | 30-80% | Actual experiment duration (messages flowing) |
| **Stopping Capture** | 1-2s | 80-85% | Terminating tcpdump, saving PCAP |
| **Analyzing** | 15-20s | 85-95% | Running KPI calculator and visualizer |
| **Parsing PCAP** | 5-10s | 95-100% | Analyzing packet capture file |
| **Completed** | - | 100% | Experiment finished, results ready |

### Expected Timings

**For a 60-second experiment**:
- Setup phases: ~10 seconds
- Running phase: 60 seconds
- Cleanup/analysis: ~25 seconds
- **Total**: ~95 seconds

**Formula**: `Total Time ≈ Duration + 35 seconds`

### What Happens If...

#### Experiment Cancelled During "Running"
- Process terminated immediately
- Network profile cleared
- Partial data retained
- No analytics generated
- Status: "cancelled"

#### Failure During "Analyzing"
- Experiment data collected successfully
- Analytics generation failed
- Status: "failed"
- Error message available
- Can re-run analytics manually

#### Network Profile Fails to Apply
- Experiment stops
- Status: "failed"
- Error: Permission denied or interface not found
- **Fix**: Ensure NET_ADMIN capability in docker-compose.yml

---

## Network Profiles

### Profile Details

#### Normal (Baseline)
```yaml
Delay: 0ms
Packet Loss: 0%
Bandwidth: Unlimited
Reordering: 0%
Jitter: 0ms
```
**Use Case**: Baseline measurements, ideal conditions

**Expected Results**:
- Avg Latency: 5-15ms
- Packet Loss: 0-0.1%
- Throughput: Maximum

#### Moderate (Typical Congestion)
```yaml
Delay: 50ms ± 10ms
Packet Loss: 1%
Bandwidth: 10-15 Mbit/s
Reordering: 0%
Jitter: ~10ms
```
**Use Case**: Realistic LTE/5G edge network

**Expected Results**:
- Avg Latency: 50-70ms
- Packet Loss: 0.8-1.2%
- Throughput: Slightly reduced

#### Severe (Degraded Network)
```yaml
Delay: 200ms ± 50ms
Packet Loss: 10% (25% correlation)
Bandwidth: 2-5 Mbit/s
Reordering: 5% (25% correlation)
Jitter: ~50ms
```
**Use Case**: Poor coverage, edge of cell

**Expected Results**:
- Avg Latency: 200-300ms
- Packet Loss: 8-12%
- Throughput: Significantly reduced
- High jitter and variance

#### Handoff (Cell Tower Switching)
```yaml
Phase 1 (2s): Normal
  - 30ms delay, 0.5% loss
Phase 2 (3s): Disruption
  - 300ms delay, 30% loss
Phase 3 (2s): Recovery
  - 50ms delay, 2% loss
Phase 4 (ongoing): Stabilized
  - 25ms delay, 0.5% loss
```
**Use Case**: Vehicle moving between cells

**Expected Results**:
- Highly variable latency
- Burst packet loss during phase 2
- Recovery pattern visible in charts

### Choosing a Profile

**For Safety Message Testing**:
- Start with **Moderate** (realistic baseline)
- Test **Severe** (ensure delivery under stress)
- Test **Handoff** (mobility simulation)

**For Performance Benchmarking**:
- Start with **Normal** (max throughput)
- Compare against **Moderate** (typical conditions)

**For Protocol Comparison**:
- Use **Moderate** (balanced test)
- TCP should handle loss better than UDP
- MQTT adds overhead but guarantees delivery

---

## Best Practices

### Experiment Naming

**Good Naming Conventions**:
- `baseline_udp_60s`
- `moderate_all_protocols_120s`
- `severe_safety_messages_30s`
- `exp_YYYYMMDD_HHMMSS` (auto-generated)

**Bad Naming**:
- `test` (too generic)
- `my-experiment` (dashes not allowed)
- `final_FINAL_v2_ACTUALLY_FINAL` (version control in git instead)

### Test Duration Guidelines

**Quick Validation (10-30s)**:
- Verify configuration
- Test new network profile
- Debug issues

**Standard Testing (60-120s)**:
- Production-quality results
- Sufficient data for statistics
- Recommended default

**Long-term Testing (180-300s)**:
- Stability testing
- Jitter analysis
- Throughput saturation

**Very Long Tests (>300s)**:
- Not supported in UI (use CLI)
- Consider multiple shorter tests instead

### Interpreting Results

**Red Flags**:
- ⚠️ P95 > 3x Average latency (high variability)
- ⚠️ Packet loss > 10% on Normal profile (infrastructure issue)
- ⚠️ Throughput < 5 msg/s (sender/receiver problem)

**Investigation Steps**:
1. Check experiment error messages
2. Review Docker logs: `docker-compose logs`
3. Verify network profile applied: `tc qdisc show`
4. Check database: Count messages collected
5. Review PCAP in Wireshark for detailed analysis

### Workflow Recommendations

**Daily Development Testing**:
1. Run quick 30s test with Moderate profile
2. Verify metrics within expected range
3. Commit code if passing

**Pre-Release Validation**:
1. Run all 4 network profiles (60s each)
2. Compare results against baseline
3. Document any degradation
4. Test safety message delivery

**Performance Analysis**:
1. Baseline with Normal profile
2. Test each profile individually
3. Export results for comparison
4. Generate combined report

---

## Troubleshooting

### Common Issues

#### "Experiment already running" Error
**Problem**: Trying to start second experiment
**Solution**:
- Wait for current test to finish
- Or click "Cancel" on running experiment
- Only one test allowed at a time

#### Progress Stuck at Phase
**Problem**: Progress bar not updating
**Causes**:
1. Script error (check logs)
2. Network profile failed to apply
3. Docker service stopped

**Debugging**:
```bash
# Check dashboard logs
docker-compose logs -f dashboard

# Check running processes
docker-compose exec dashboard ps aux | grep run_experiment

# Manual network profile check
docker-compose exec dashboard tc qdisc show
```

#### Results Not Generated
**Problem**: Experiment completed but no results

**Check**:
1. Status is "completed" (✅) not "failed" (❌)
2. Output directory exists: `ls outputs/<experiment_name>/`
3. Analytics ran: `docker-compose logs analytics`
4. Files present:
   ```bash
   ls outputs/<experiment_name>/
   # Should see: kpi_report.json, *.png, messages.csv
   ```

**Fix**:
```bash
# Re-run analytics manually
docker-compose run --rm analytics python kpi_calculator.py /data/v2x_testbed.db /outputs/<experiment_name>
docker-compose run --rm analytics python visualize.py /data/v2x_testbed.db /outputs/<experiment_name>
```

#### Permission Denied Errors
**Problem**: Network profile can't be applied

**Root Cause**: Dashboard container lacks NET_ADMIN capability

**Fix**:
```yaml
# Verify docker-compose.yml has:
dashboard:
  cap_add:
    - NET_ADMIN
```

```bash
# Rebuild and restart
docker-compose build dashboard
docker-compose up -d dashboard
```

#### Database Locked
**Problem**: "database is locked" error

**Causes**:
- Multiple processes accessing database
- Container crashed mid-transaction

**Fix**:
```bash
# Stop all services
docker-compose down

# Optionally backup database
cp data/v2x_testbed.db data/v2x_testbed.db.backup

# Restart
docker-compose up -d

# If persists, check for file locks
lsof data/v2x_testbed.db
```

#### Charts Not Loading
**Problem**: "Image not found" in Results Viewer

**Check**:
1. Output directory has PNG files:
   ```bash
   ls outputs/<experiment_name>/*.png
   ```
2. Visualizer ran successfully:
   ```bash
   docker-compose logs analytics | grep visualize
   ```

**Fix**:
```bash
# Re-run visualizer
docker-compose run --rm analytics python visualize.py /data/v2x_testbed.db /outputs/<experiment_name>
```

### Getting Help

**Log Collection**:
```bash
# All services
docker-compose logs > debug_logs.txt

# Specific service
docker-compose logs dashboard > dashboard_logs.txt
docker-compose logs analytics > analytics_logs.txt
```

**System Info**:
```bash
# Docker version
docker --version
docker-compose --version

# Container status
docker-compose ps

# Database check
docker-compose exec edge_server sqlite3 /data/v2x_testbed.db "SELECT COUNT(*) FROM experiment_runs;"
```

**Reset to Clean State**:
```bash
# Nuclear option - deletes all data
docker-compose down
rm -rf data/ outputs/
docker-compose up -d
```

---

## Architecture

### System Components

```
┌─────────────────────────────────────────┐
│         Browser (Port 8501)             │
│  ┌────────────────────────────────┐     │
│  │  Streamlit Multi-Page App      │     │
│  │  - Main Dashboard (app.py)     │     │
│  │  - Test Control (page 1)       │     │
│  │  - Results Viewer (page 2)     │     │
│  └────────────────────────────────┘     │
└──────────────┬──────────────────────────┘
               │ HTTP/WebSocket
               ▼
┌─────────────────────────────────────────┐
│      Dashboard Container                │
│  ┌────────────────────────────────┐     │
│  │  TestOrchestrator              │     │
│  │  (test_runner.py)              │     │
│  │  - validate_inputs()           │     │
│  │  - start_experiment()          │     │
│  │  - _execute_experiment()       │     │
│  │  - cancel_experiment()         │     │
│  │  - get_experiment_results()    │     │
│  └────────────────────────────────┘     │
│               │                          │
│               ▼                          │
│  ┌────────────────────────────────┐     │
│  │  Subprocess (run_experiment.sh)│     │
│  │  - Network shaping (tc)        │     │
│  │  - Packet capture (tcpdump)    │     │
│  │  - Analytics orchestration     │     │
│  └────────────────────────────────┘     │
└──────────────┬──────────────────────────┘
               │
      ┌────────┴────────┐
      ▼                 ▼
┌──────────┐    ┌──────────────┐
│ SQLite   │    │  File System │
│ Database │    │  /outputs/   │
│          │    │  /data/      │
│ Tables:  │    │  *.pcap      │
│ - messages│    │  *.json     │
│ - experiment│  │  *.csv      │
│   _runs   │    │  *.png      │
└──────────┘    └──────────────┘
```

### Data Flow

**Experiment Creation**:
1. User fills form → Submit button
2. Streamlit → `orchestrator.start_experiment()`
3. Validation (name, duration, profile)
4. Create database entry (status: pending)
5. Launch background thread
6. Thread → `subprocess.Popen('run_experiment.sh')`
7. Update status to "running"

**Progress Tracking**:
1. Script outputs: `PHASE:running|45`
2. Orchestrator parses stdout
3. Updates database: `update_experiment_status(progress=45)`
4. Streamlit polls database every 2s
5. UI updates progress bar

**Completion**:
1. Script exits with code 0
2. Orchestrator detects completion
3. Updates status to "completed"
4. Analytics generated (KPI, charts)
5. Results available in viewer

### Database Schema

**experiment_runs table**:
```sql
CREATE TABLE experiment_runs (
    id INTEGER PRIMARY KEY,
    experiment_name TEXT UNIQUE NOT NULL,
    status TEXT NOT NULL,              -- pending|running|completed|failed|cancelled
    network_profile TEXT NOT NULL,     -- normal|moderate|severe|handoff
    duration_seconds INTEGER NOT NULL,
    protocol TEXT,                     -- UDP,TCP,MQTT or ALL
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    progress_percent INTEGER DEFAULT 0,
    current_phase TEXT,
    error_message TEXT,
    output_directory TEXT,
    process_id INTEGER,
    advanced_options TEXT,             -- JSON string
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Indexes**:
- `idx_experiment_status` on status (fast filtering)
- `idx_experiment_created` on created_at (chronological sorting)

### File Structure

**Per Experiment**:
```
outputs/<experiment_name>/
├── kpi_report.json           # Generated by kpi_calculator.py
├── messages.csv              # Generated by kpi_calculator.py
├── latency_by_protocol.csv   # Generated by kpi_calculator.py
├── latency_over_time.png     # Generated by visualize.py
├── latency_distribution.png  # Generated by visualize.py
├── protocol_comparison.png   # Generated by visualize.py
├── message_type_comparison.png
├── packet_loss_over_time.png
├── capture.pcap              # Generated by tcpdump
└── pcap_analysis.json        # Generated by parser.py
```

---

## Appendix

### Keyboard Shortcuts

**Streamlit Native**:
- `R` - Rerun app (refresh)
- `C` - Clear cache
- `?` - Show keyboard shortcuts

### API Reference (For Developers)

**TestOrchestrator Class**:
```python
from test_runner import get_orchestrator

orchestrator = get_orchestrator()

# Start experiment
result = orchestrator.start_experiment(
    name='my_test',
    duration=60,
    profile='moderate',
    protocol='ALL'
)

# Check status
status = orchestrator.get_experiment_status(run_id)

# Cancel
orchestrator.cancel_experiment(run_id)

# Get results
results = orchestrator.get_experiment_results(run_id)
```

### Environment Variables

```bash
# Database path (default: /data/v2x_testbed.db)
export V2X_DB_PATH=/custom/path/db.sqlite

# Output directory (default: /outputs)
export V2X_OUTPUT_DIR=/custom/outputs

# Network interface (default: eth0)
export V2X_INTERFACE=ens5
```

### Performance Tuning

**For Faster Tests**:
- Reduce duration to 10-30s
- Disable PCAP (saves disk I/O)
- Use Normal profile (no tc overhead)

**For Maximum Data**:
- Increase duration to 120-300s
- Enable all protocols
- Use Severe profile (stress test)

**For Disk Space**:
- Auto-cleanup old experiments (>30 days)
- Compress PCAP files: `gzip outputs/*/capture.pcap`
- Archive to external storage

---

## Changelog

### v1.0.0 (2026-02-19)
-Initial release of Control Center
-Test Control page
-Results Viewer page
-Real-time progress tracking
-Queue management (one test at a time)
-Multi-page Streamlit navigation

### Future Roadmap
-Multi-experiment comparison view
-Scheduled/automated experiments
-Custom network profile creation from UI
-WebSocket-based live updates
-REST API for CI/CD integration
-Export to PDF reports
-User authentication

---

**End of Control Center User Guide**

For more information, see:
- [README.md](README.md) - Complete project documentation
- [QUICK_START.md](QUICK_START.md) - Getting started guide
