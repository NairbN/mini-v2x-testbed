#!/usr/bin/env python3
"""
Results Viewer - V2X Dashboard
Browse and analyze completed experiment results
"""

import streamlit as st
import sys
import os
from datetime import datetime
import json

# Add paths to import test_runner
sys.path.append('/app')
from test_runner import get_orchestrator

# Page configuration
st.set_page_config(
    page_title="Results Viewer",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize orchestrator
orchestrator = get_orchestrator()

# Page Title
st.title("📈 Experiment Results Viewer")
st.markdown("Browse and analyze completed V2X performance experiments")

st.divider()

# Section 1: Experiment Selector
st.subheader("🔍 Select Experiment")

# Get completed experiments
completed_exps = orchestrator.list_experiments(status_filter='completed')

if not completed_exps:
    st.warning("⚠️ No completed experiments found. Run an experiment from the Test Control page first.")
    st.page_link("pages/1_🎮_Test_Control.py", label="🎮 Go to Test Control", icon="🚀")
    st.stop()

# Check if experiment was selected from Test Control page
selected_exp_id = st.session_state.get('selected_experiment_id', None)

# Create selection options
exp_options = {
    exp['id']: f"{exp['experiment_name']} - {exp['network_profile']} ({datetime.fromisoformat(exp['created_at']).strftime('%Y-%m-%d %H:%M')})"
    for exp in completed_exps
}

# Find default index
default_index = 0
if selected_exp_id and selected_exp_id in exp_options:
    default_index = list(exp_options.keys()).index(selected_exp_id)

selected_exp_id = st.selectbox(
    "Choose an experiment to view",
    options=list(exp_options.keys()),
    format_func=lambda x: exp_options[x],
    index=default_index,
    help="Select a completed experiment to view its results"
)

# Get experiment details
selected_exp = orchestrator.get_experiment_status(selected_exp_id)

if not selected_exp or 'error' in selected_exp:
    st.error("❌ Could not load experiment details")
    st.stop()

st.divider()

# Section 2: Experiment Metadata
st.subheader("📋 Experiment Details")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Experiment Name", selected_exp['experiment_name'])
    st.caption(f"🆔 ID: {selected_exp['id']}")

with col2:
    st.metric("Network Profile", selected_exp['network_profile'])
    protocol = selected_exp.get('protocol', 'ALL')
    st.caption(f"🔌 Protocol: {protocol}")

with col3:
    st.metric("Duration", f"{selected_exp['duration_seconds']}s")
    created = datetime.fromisoformat(selected_exp['created_at']).strftime('%Y-%m-%d %H:%M:%S')
    st.caption(f"📅 Started: {created}")

with col4:
    st.metric("Status", selected_exp['status'].upper())
    if selected_exp.get('completed_at'):
        completed = datetime.fromisoformat(selected_exp['completed_at']).strftime('%Y-%m-%d %H:%M:%S')
        st.caption(f"✅ Completed: {completed}")

st.divider()

# Section 3: Load Results
st.subheader("📊 Performance Metrics")

results = orchestrator.get_experiment_results(selected_exp_id)

if 'error' in results:
    st.error(f"❌ {results['error']}")
    st.info("💡 Results may not be available yet. Check the output directory or run the analytics manually.")
    st.stop()

# Display KPIs
if 'overall_kpis' in results:
    kpis = results['overall_kpis']

    # Overall latency metrics
    st.markdown("### ⏱️ Latency Metrics")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        avg_latency = kpis['latency'].get('avg_latency_ms', 0)
        st.metric("Average Latency", f"{avg_latency:.2f} ms")

    with col2:
        median_latency = kpis['latency'].get('median_latency_ms', 0)
        st.metric("Median Latency", f"{median_latency:.2f} ms")

    with col3:
        p95_latency = kpis['latency'].get('p95_latency_ms', 0)
        st.metric("P95 Latency", f"{p95_latency:.2f} ms")

    with col4:
        p99_latency = kpis['latency'].get('p99_latency_ms', 0)
        st.metric("P99 Latency", f"{p99_latency:.2f} ms")

    # Additional latency stats
    with st.expander("📉 Additional Latency Statistics"):
        col_a, col_b, col_c, col_d = st.columns(4)
        with col_a:
            st.metric("Min Latency", f"{kpis['latency'].get('min_latency_ms', 0):.2f} ms")
        with col_b:
            st.metric("Max Latency", f"{kpis['latency'].get('max_latency_ms', 0):.2f} ms")
        with col_c:
            st.metric("Std Dev", f"{kpis['latency'].get('stddev_latency_ms', 0):.2f} ms")
        with col_d:
            jitter = kpis.get('jitter_ms', 0)
            st.metric("Jitter", f"{jitter:.2f} ms")

    st.divider()

    # Packet loss and throughput
    st.markdown("### 📦 Reliability & Throughput")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        loss_rate = kpis['packet_loss'].get('loss_rate_percent', 0)
        st.metric("Packet Loss Rate", f"{loss_rate:.2f}%")

    with col2:
        total_lost = kpis['packet_loss'].get('total_lost', 0)
        st.metric("Total Lost Packets", f"{total_lost:,}")

    with col3:
        msg_per_sec = kpis['throughput'].get('messages_per_second', 0)
        st.metric("Throughput", f"{msg_per_sec:.2f} msg/s")

    with col4:
        mbps = kpis['throughput'].get('mbps', 0)
        st.metric("Bandwidth", f"{mbps:.2f} Mbps")

    # Additional throughput stats
    with st.expander("🚀 Additional Throughput Statistics"):
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            bytes_per_sec = kpis['throughput'].get('bytes_per_second', 0)
            st.metric("Bytes/sec", f"{bytes_per_sec:,.0f}")
        with col_b:
            kbps = kpis['throughput'].get('kbps', 0)
            st.metric("Kbps", f"{kbps:.2f}")
        with col_c:
            duration = kpis['throughput'].get('duration_seconds', 0)
            st.metric("Measurement Duration", f"{duration:.1f}s")

    st.divider()

# Section 4: Protocol Comparison (if available)
if 'protocol_comparison' in results and results['protocol_comparison']:
    st.markdown("### 🔌 Protocol Performance Comparison")

    protocol_data = results['protocol_comparison']

    # Create comparison table
    comparison_rows = []
    for proto, stats in protocol_data.items():
        comparison_rows.append({
            'Protocol': proto,
            'Avg Latency (ms)': f"{stats['latency']['avg_latency_ms']:.2f}",
            'P95 Latency (ms)': f"{stats['latency']['p95_latency_ms']:.2f}",
            'Packet Loss (%)': f"{stats['packet_loss']['loss_rate_percent']:.2f}",
            'Throughput (msg/s)': f"{stats['throughput']['messages_per_second']:.2f}",
            'Jitter (ms)': f"{stats.get('jitter_ms', 0):.2f}"
        })

    st.dataframe(comparison_rows, use_container_width=True, hide_index=True)

    st.divider()

# Section 5: Charts & Visualizations
st.subheader("📊 Performance Charts")

output_dir = selected_exp['output_directory']

# List of expected chart files
chart_files = [
    ('latency_over_time.png', 'Latency Over Time'),
    ('latency_distribution.png', 'Latency Distribution'),
    ('protocol_comparison.png', 'Protocol Comparison'),
    ('message_type_comparison.png', 'Message Type Comparison'),
    ('packet_loss_over_time.png', 'Packet Loss Over Time')
]

# Display charts
charts_found = False
for chart_file, chart_title in chart_files:
    chart_path = os.path.join(output_dir, chart_file)

    if os.path.exists(chart_path):
        charts_found = True
        st.markdown(f"#### {chart_title}")
        st.image(chart_path, use_column_width=True)
        st.divider()

if not charts_found:
    st.info("📊 No visualization charts found. Charts are generated during experiment analysis.")

# Section 6: Raw Data & Downloads
st.subheader("📥 Export & Download")

col1, col2, col3 = st.columns(3)

# JSON Report
kpi_file = os.path.join(output_dir, 'kpi_report.json')
if os.path.exists(kpi_file):
    with col1:
        with open(kpi_file, 'r') as f:
            json_data = f.read()
        st.download_button(
            label="📄 Download JSON Report",
            data=json_data,
            file_name=f"{selected_exp['experiment_name']}_kpi_report.json",
            mime="application/json",
            use_container_width=True
        )
else:
    with col1:
        st.button("📄 JSON Report (Not Available)", disabled=True, use_container_width=True)

# CSV Data
csv_file = os.path.join(output_dir, 'messages.csv')
if os.path.exists(csv_file):
    with col2:
        with open(csv_file, 'r') as f:
            csv_data = f.read()
        st.download_button(
            label="📊 Download CSV Data",
            data=csv_data,
            file_name=f"{selected_exp['experiment_name']}_messages.csv",
            mime="text/csv",
            use_container_width=True
        )
else:
    with col2:
        st.button("📊 CSV Data (Not Available)", disabled=True, use_container_width=True)

# PCAP File
pcap_file = os.path.join(output_dir, 'capture.pcap')
if os.path.exists(pcap_file):
    with col3:
        with open(pcap_file, 'rb') as f:
            pcap_data = f.read()
        st.download_button(
            label="📦 Download PCAP File",
            data=pcap_data,
            file_name=f"{selected_exp['experiment_name']}_capture.pcap",
            mime="application/octet-stream",
            use_container_width=True
        )
else:
    with col3:
        st.button("📦 PCAP File (Not Available)", disabled=True, use_container_width=True)

st.divider()

# Section 7: Raw JSON View (for debugging)
with st.expander("🔍 View Raw Results JSON"):
    st.json(results, expanded=False)

# Section 8: Future - Comparison Mode
st.divider()
with st.expander("🔀 Compare with Another Experiment (Coming Soon)"):
    st.info("📊 Multi-experiment comparison feature will be available in a future update. "
            "This will allow you to select multiple experiments and compare their metrics side-by-side.")

    st.markdown("""
    **Planned comparison features:**
    - Side-by-side metrics table
    - Overlay latency curves
    - Protocol performance delta
    - Network profile impact analysis
    - Statistical significance testing
    """)

# Footer
st.caption(f"Last refreshed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
