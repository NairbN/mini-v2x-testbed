#!/usr/bin/env python3
"""
Visualization - Generate plots for V2X performance metrics
"""

import sqlite3
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
import logging
import sys
from pathlib import Path
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MetricsVisualizer:
    """Generate visualizations for V2X metrics"""

    def __init__(self, db_path: str = '/data/v2x_testbed.db'):
        """Initialize visualizer"""
        self.db_path = db_path
        if not Path(db_path).exists():
            raise FileNotFoundError(f"Database not found: {db_path}")

        self.conn = sqlite3.connect(db_path)
        logger.info(f"Connected to database: {db_path}")

    def load_data(self, message_type: Optional[str] = None) -> pd.DataFrame:
        """Load data from database"""
        query = "SELECT * FROM messages ORDER BY receive_timestamp"
        params = []

        if message_type:
            query = "SELECT * FROM messages WHERE message_type = ? ORDER BY receive_timestamp"
            params.append(message_type)

        df = pd.read_sql_query(query, self.conn, params=params)
        logger.info(f"Loaded {len(df)} messages")
        return df

    def plot_latency_over_time(self, output_path: str = '/outputs/latency_over_time.png'):
        """Plot latency over time"""
        df = self.load_data()

        if df.empty:
            logger.warning("No data to plot")
            return

        fig, ax = plt.subplots(figsize=(12, 6))

        # Plot by protocol
        for protocol in df['protocol'].unique():
            df_protocol = df[df['protocol'] == protocol]
            ax.scatter(
                df_protocol['receive_timestamp'] - df['receive_timestamp'].min(),
                df_protocol['latency_ms'],
                label=protocol,
                alpha=0.6,
                s=10
            )

        ax.set_xlabel('Time (seconds)')
        ax.set_ylabel('Latency (ms)')
        ax.set_title('End-to-End Latency Over Time')
        ax.legend()
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(output_path, dpi=150)
        logger.info(f"Saved latency plot to {output_path}")
        plt.close()

    def plot_latency_distribution(self, output_path: str = '/outputs/latency_distribution.png'):
        """Plot latency distribution by protocol"""
        df = self.load_data()

        if df.empty:
            logger.warning("No data to plot")
            return

        protocols = df['protocol'].unique()
        fig, axes = plt.subplots(1, len(protocols), figsize=(15, 5), sharey=True)

        if len(protocols) == 1:
            axes = [axes]

        for idx, protocol in enumerate(protocols):
            df_protocol = df[df['protocol'] == protocol]
            axes[idx].hist(df_protocol['latency_ms'], bins=50, edgecolor='black', alpha=0.7)
            axes[idx].set_xlabel('Latency (ms)')
            axes[idx].set_title(f'{protocol} Latency Distribution')
            axes[idx].grid(True, alpha=0.3)

        axes[0].set_ylabel('Frequency')

        plt.tight_layout()
        plt.savefig(output_path, dpi=150)
        logger.info(f"Saved distribution plot to {output_path}")
        plt.close()

    def plot_protocol_comparison(self, output_path: str = '/outputs/protocol_comparison.png'):
        """Compare protocols across metrics"""
        df = self.load_data()

        if df.empty:
            logger.warning("No data to plot")
            return

        protocols = df['protocol'].unique()

        metrics = {
            'Avg Latency (ms)': [],
            'P95 Latency (ms)': [],
            'Packet Loss (%)': []
        }

        for protocol in protocols:
            df_p = df[df['protocol'] == protocol]
            metrics['Avg Latency (ms)'].append(df_p['latency_ms'].mean())
            metrics['P95 Latency (ms)'].append(df_p['latency_ms'].quantile(0.95))

            total_expected = len(df_p) + df_p['sequence_gap'].sum()
            loss_rate = (df_p['sequence_gap'].sum() / total_expected * 100) if total_expected > 0 else 0
            metrics['Packet Loss (%)'].append(loss_rate)

        fig, axes = plt.subplots(1, 3, figsize=(15, 5))

        for idx, (metric_name, values) in enumerate(metrics.items()):
            axes[idx].bar(protocols, values, edgecolor='black', alpha=0.7)
            axes[idx].set_ylabel(metric_name)
            axes[idx].set_title(metric_name)
            axes[idx].grid(True, alpha=0.3, axis='y')

        plt.tight_layout()
        plt.savefig(output_path, dpi=150)
        logger.info(f"Saved protocol comparison to {output_path}")
        plt.close()

    def plot_message_type_comparison(self, output_path: str = '/outputs/message_type_comparison.png'):
        """Compare telemetry vs safety message performance"""
        df = self.load_data()

        if df.empty:
            logger.warning("No data to plot")
            return

        message_types = df['message_type'].unique()

        fig, axes = plt.subplots(1, 2, figsize=(12, 5))

        # Latency comparison
        latencies = [df[df['message_type'] == mt]['latency_ms'].values for mt in message_types]
        axes[0].boxplot(latencies, labels=message_types)
        axes[0].set_ylabel('Latency (ms)')
        axes[0].set_title('Latency by Message Type')
        axes[0].grid(True, alpha=0.3, axis='y')

        # Throughput comparison
        throughputs = []
        for mt in message_types:
            df_mt = df[df['message_type'] == mt]
            time_span = df_mt['receive_timestamp'].max() - df_mt['receive_timestamp'].min()
            msg_per_sec = len(df_mt) / time_span if time_span > 0 else 0
            throughputs.append(msg_per_sec)

        axes[1].bar(message_types, throughputs, edgecolor='black', alpha=0.7)
        axes[1].set_ylabel('Messages/second')
        axes[1].set_title('Throughput by Message Type')
        axes[1].grid(True, alpha=0.3, axis='y')

        plt.tight_layout()
        plt.savefig(output_path, dpi=150)
        logger.info(f"Saved message type comparison to {output_path}")
        plt.close()

    def plot_packet_loss_over_time(self, output_path: str = '/outputs/packet_loss_over_time.png'):
        """Plot cumulative packet loss over time"""
        df = self.load_data()

        if df.empty:
            logger.warning("No data to plot")
            return

        fig, ax = plt.subplots(figsize=(12, 6))

        for protocol in df['protocol'].unique():
            df_p = df[df['protocol'] == protocol].copy()
            df_p['cumulative_loss'] = df_p['sequence_gap'].cumsum()

            time_normalized = df_p['receive_timestamp'] - df['receive_timestamp'].min()
            ax.plot(time_normalized, df_p['cumulative_loss'], label=protocol, linewidth=2)

        ax.set_xlabel('Time (seconds)')
        ax.set_ylabel('Cumulative Packet Loss')
        ax.set_title('Cumulative Packet Loss Over Time')
        ax.legend()
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(output_path, dpi=150)
        logger.info(f"Saved packet loss plot to {output_path}")
        plt.close()

    def generate_all_plots(self, output_dir: str = '/outputs'):
        """Generate all visualization plots"""
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        logger.info("Generating all plots...")

        self.plot_latency_over_time(f"{output_dir}/latency_over_time.png")
        self.plot_latency_distribution(f"{output_dir}/latency_distribution.png")
        self.plot_protocol_comparison(f"{output_dir}/protocol_comparison.png")
        self.plot_message_type_comparison(f"{output_dir}/message_type_comparison.png")
        self.plot_packet_loss_over_time(f"{output_dir}/packet_loss_over_time.png")

        logger.info(f"All plots saved to {output_dir}")

    def close(self):
        """Close database connection"""
        self.conn.close()


if __name__ == '__main__':
    db_path = sys.argv[1] if len(sys.argv) > 1 else '/data/v2x_testbed.db'
    output_dir = sys.argv[2] if len(sys.argv) > 2 else '/outputs'

    visualizer = MetricsVisualizer(db_path)
    visualizer.generate_all_plots(output_dir)
    visualizer.close()

    print(f"\n✓ Visualizations generated in {output_dir}")
