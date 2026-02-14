#!/usr/bin/env python3
"""
Streamlit Dashboard for V2X Performance Monitoring
Real-time visualization of network metrics
"""

import streamlit as st
import pandas as pd
import sqlite3
import time
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import sys
sys.path.append('/app')

# Page configuration
st.set_page_config(
    page_title="V2X Performance Dashboard",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Database connection
@st.cache_resource
def get_db_connection():
    """Get database connection"""
    return sqlite3.connect('/data/v2x_testbed.db', check_same_thread=False)

def load_data(limit=1000):
    """Load recent messages from database"""
    conn = get_db_connection()
    query = f"""
        SELECT * FROM messages
        ORDER BY receive_timestamp DESC
        LIMIT {limit}
    """
    df = pd.read_sql_query(query, conn)
    return df

def calculate_metrics(df):
    """Calculate real-time metrics"""
    if df.empty:
        return {
            'total_messages': 0,
            'avg_latency': 0,
            'p95_latency': 0,
            'packet_loss_rate': 0,
            'throughput': 0
        }

    total_expected = len(df) + df['sequence_gap'].sum()
    loss_rate = (df['sequence_gap'].sum() / total_expected * 100) if total_expected > 0 else 0

    time_span = df['receive_timestamp'].max() - df['receive_timestamp'].min()
    throughput = len(df) / time_span if time_span > 0 else 0

    return {
        'total_messages': len(df),
        'avg_latency': df['latency_ms'].mean(),
        'p95_latency': df['latency_ms'].quantile(0.95),
        'packet_loss_rate': loss_rate,
        'throughput': throughput
    }

# Dashboard Title
st.title("🚗 V2X Performance & Edge Connectivity Dashboard")
st.markdown("Real-time monitoring of Vehicle-to-Network communication metrics")

# Sidebar controls
st.sidebar.header("⚙️ Controls")
auto_refresh = st.sidebar.checkbox("Auto-refresh", value=True)
refresh_interval = st.sidebar.slider("Refresh interval (seconds)", 1, 10, 3)
data_limit = st.sidebar.slider("Data points to display", 100, 5000, 1000)

# Protocol filter
protocol_filter = st.sidebar.multiselect(
    "Filter by Protocol",
    options=['UDP', 'TCP', 'MQTT'],
    default=['UDP', 'TCP', 'MQTT']
)

# Load data
df = load_data(limit=data_limit)

# Apply protocol filter
if protocol_filter:
    df = df[df['protocol'].isin(protocol_filter)]

# Calculate metrics
metrics = calculate_metrics(df)

# Metrics row
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="📊 Total Messages",
        value=f"{metrics['total_messages']:,}",
        delta=None
    )

with col2:
    st.metric(
        label="⏱️ Avg Latency",
        value=f"{metrics['avg_latency']:.2f} ms",
        delta=None
    )

with col3:
    st.metric(
        label="📉 P95 Latency",
        value=f"{metrics['p95_latency']:.2f} ms",
        delta=None
    )

with col4:
    st.metric(
        label="📦 Packet Loss",
        value=f"{metrics['packet_loss_rate']:.2f}%",
        delta=None
    )

# Throughput
st.metric(
    label="🚀 Throughput",
    value=f"{metrics['throughput']:.2f} msg/s"
)

st.divider()

# Charts
if not df.empty:
    # Latency over time
    st.subheader("📈 Latency Over Time")

    df_sorted = df.sort_values('receive_timestamp')
    df_sorted['time_offset'] = df_sorted['receive_timestamp'] - df_sorted['receive_timestamp'].min()

    fig_latency = px.scatter(
        df_sorted,
        x='time_offset',
        y='latency_ms',
        color='protocol',
        title='End-to-End Latency',
        labels={'time_offset': 'Time (seconds)', 'latency_ms': 'Latency (ms)'},
        opacity=0.6
    )
    fig_latency.update_layout(height=400)
    st.plotly_chart(fig_latency, use_container_width=True)

    # Protocol comparison
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📊 Latency Distribution by Protocol")
        fig_box = px.box(
            df,
            x='protocol',
            y='latency_ms',
            color='protocol',
            title='Latency Distribution'
        )
        fig_box.update_layout(height=400)
        st.plotly_chart(fig_box, use_container_width=True)

    with col2:
        st.subheader("🔄 Message Type Distribution")
        message_counts = df['message_type'].value_counts()
        fig_pie = px.pie(
            values=message_counts.values,
            names=message_counts.index,
            title='Messages by Type'
        )
        fig_pie.update_layout(height=400)
        st.plotly_chart(fig_pie, use_container_width=True)

    # Protocol comparison table
    st.subheader("📋 Protocol Performance Comparison")

    protocol_stats = []
    for protocol in df['protocol'].unique():
        df_p = df[df['protocol'] == protocol]
        total_expected_p = len(df_p) + df_p['sequence_gap'].sum()
        loss_p = (df_p['sequence_gap'].sum() / total_expected_p * 100) if total_expected_p > 0 else 0

        protocol_stats.append({
            'Protocol': protocol,
            'Messages': len(df_p),
            'Avg Latency (ms)': round(df_p['latency_ms'].mean(), 2),
            'P95 Latency (ms)': round(df_p['latency_ms'].quantile(0.95), 2),
            'Packet Loss (%)': round(loss_p, 2)
        })

    st.dataframe(pd.DataFrame(protocol_stats), use_container_width=True)

    # Recent messages
    st.subheader("📜 Recent Messages")
    st.dataframe(
        df[['message_id', 'vehicle_id', 'message_type', 'latency_ms', 'protocol', 'sequence_gap']].head(20),
        use_container_width=True
    )

else:
    st.warning("⚠️ No data available. Ensure the vehicle node and edge server are running.")

# Footer
st.divider()
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Auto-refresh
if auto_refresh:
    time.sleep(refresh_interval)
    st.rerun()
