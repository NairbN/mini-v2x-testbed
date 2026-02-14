#!/usr/bin/env python3
"""
KPI Calculator - Compute performance metrics from database
"""

import sqlite3
import numpy as np
import pandas as pd
import logging
import sys
from pathlib import Path
from typing import Dict, Any, Optional
import json

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class KPICalculator:
    """Calculate Key Performance Indicators for V2X testbed"""

    def __init__(self, db_path: str = '/data/v2x_testbed.db'):
        """Initialize KPI calculator"""
        self.db_path = db_path
        if not Path(db_path).exists():
            raise FileNotFoundError(f"Database not found: {db_path}")

        self.conn = sqlite3.connect(db_path)
        logger.info(f"Connected to database: {db_path}")

    def load_messages_df(self, message_type: Optional[str] = None) -> pd.DataFrame:
        """Load messages into pandas DataFrame"""
        query = "SELECT * FROM messages"
        params = []

        if message_type:
            query += " WHERE message_type = ?"
            params.append(message_type)

        query += " ORDER BY receive_timestamp"

        df = pd.read_sql_query(query, self.conn, params=params)
        logger.info(f"Loaded {len(df)} messages")
        return df

    def calculate_latency_kpis(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calculate latency-based KPIs"""
        if df.empty:
            return {}

        return {
            'avg_latency_ms': float(df['latency_ms'].mean()),
            'median_latency_ms': float(df['latency_ms'].median()),
            'p50_latency_ms': float(df['latency_ms'].quantile(0.50)),
            'p95_latency_ms': float(df['latency_ms'].quantile(0.95)),
            'p99_latency_ms': float(df['latency_ms'].quantile(0.99)),
            'min_latency_ms': float(df['latency_ms'].min()),
            'max_latency_ms': float(df['latency_ms'].max()),
            'stddev_latency_ms': float(df['latency_ms'].std())
        }

    def calculate_jitter(self, df: pd.DataFrame) -> float:
        """Calculate jitter (inter-arrival time variance)"""
        if len(df) < 2:
            return 0.0

        # Sort by timestamp
        df_sorted = df.sort_values('receive_timestamp')

        # Calculate inter-arrival times
        inter_arrivals = df_sorted['receive_timestamp'].diff().dropna()

        # Jitter is standard deviation of inter-arrival times (in ms)
        jitter_ms = float(inter_arrivals.std() * 1000)
        return jitter_ms

    def calculate_packet_loss(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate packet loss metrics"""
        if df.empty:
            return {
                'total_expected': 0,
                'total_received': 0,
                'total_lost': 0,
                'loss_rate_percent': 0.0
            }

        total_received = len(df)
        total_gaps = int(df['sequence_gap'].sum())
        total_expected = total_received + total_gaps

        loss_rate = (total_gaps / total_expected * 100) if total_expected > 0 else 0.0

        return {
            'total_expected': total_expected,
            'total_received': total_received,
            'total_lost': total_gaps,
            'loss_rate_percent': float(loss_rate)
        }

    def calculate_throughput(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calculate throughput metrics"""
        if df.empty:
            return {
                'messages_per_second': 0.0,
                'bytes_per_second': 0.0,
                'kbps': 0.0,
                'mbps': 0.0
            }

        # Calculate time span
        time_span = df['receive_timestamp'].max() - df['receive_timestamp'].min()

        if time_span == 0:
            return {
                'messages_per_second': 0.0,
                'bytes_per_second': 0.0,
                'kbps': 0.0,
                'mbps': 0.0
            }

        total_messages = len(df)
        total_bytes = df['payload_size'].sum()

        messages_per_second = total_messages / time_span
        bytes_per_second = total_bytes / time_span
        kbps = (bytes_per_second * 8) / 1000
        mbps = kbps / 1000

        return {
            'messages_per_second': float(messages_per_second),
            'bytes_per_second': float(bytes_per_second),
            'kbps': float(kbps),
            'mbps': float(mbps),
            'duration_seconds': float(time_span)
        }

    def compare_protocols(self) -> Dict[str, Dict[str, Any]]:
        """Compare performance across protocols"""
        protocols = ['UDP', 'TCP', 'MQTT']
        comparison = {}

        for protocol in protocols:
            df = self.load_messages_df()
            df_protocol = df[df['protocol'] == protocol]

            if df_protocol.empty:
                continue

            comparison[protocol] = {
                'latency': self.calculate_latency_kpis(df_protocol),
                'jitter_ms': self.calculate_jitter(df_protocol),
                'packet_loss': self.calculate_packet_loss(df_protocol),
                'throughput': self.calculate_throughput(df_protocol)
            }

        return comparison

    def compare_message_types(self) -> Dict[str, Dict[str, Any]]:
        """Compare performance for telemetry vs safety messages"""
        message_types = ['telemetry', 'safety']
        comparison = {}

        for msg_type in message_types:
            df = self.load_messages_df(message_type=msg_type)

            if df.empty:
                continue

            comparison[msg_type] = {
                'latency': self.calculate_latency_kpis(df),
                'jitter_ms': self.calculate_jitter(df),
                'packet_loss': self.calculate_packet_loss(df),
                'throughput': self.calculate_throughput(df)
            }

        return comparison

    def generate_full_report(self) -> Dict[str, Any]:
        """Generate comprehensive KPI report"""
        df = self.load_messages_df()

        report = {
            'metadata': {
                'total_messages': len(df),
                'unique_vehicles': int(df['vehicle_id'].nunique()) if not df.empty else 0,
                'protocols_used': df['protocol'].unique().tolist() if not df.empty else [],
                'time_range': {
                    'start': float(df['receive_timestamp'].min()) if not df.empty else 0,
                    'end': float(df['receive_timestamp'].max()) if not df.empty else 0
                }
            },
            'overall_kpis': {
                'latency': self.calculate_latency_kpis(df),
                'jitter_ms': self.calculate_jitter(df),
                'packet_loss': self.calculate_packet_loss(df),
                'throughput': self.calculate_throughput(df)
            },
            'protocol_comparison': self.compare_protocols(),
            'message_type_comparison': self.compare_message_types()
        }

        return report

    def export_to_csv(self, output_dir: str = '/outputs'):
        """Export KPI data to CSV files"""
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        # Export all messages
        df = self.load_messages_df()
        csv_path = f"{output_dir}/messages.csv"
        df.to_csv(csv_path, index=False)
        logger.info(f"Exported messages to {csv_path}")

        # Export summary statistics
        report = self.generate_full_report()

        # Latency summary by protocol
        latency_data = []
        for protocol, metrics in report['protocol_comparison'].items():
            row = {'protocol': protocol}
            row.update(metrics['latency'])
            latency_data.append(row)

        if latency_data:
            latency_df = pd.DataFrame(latency_data)
            latency_csv = f"{output_dir}/latency_by_protocol.csv"
            latency_df.to_csv(latency_csv, index=False)
            logger.info(f"Exported latency summary to {latency_csv}")

        return report

    def close(self):
        """Close database connection"""
        self.conn.close()


if __name__ == '__main__':
    db_path = sys.argv[1] if len(sys.argv) > 1 else '/data/v2x_testbed.db'
    output_dir = sys.argv[2] if len(sys.argv) > 2 else '/outputs'

    calculator = KPICalculator(db_path)

    # Generate and export report
    report = calculator.export_to_csv(output_dir)

    # Print report
    report_json = f"{output_dir}/kpi_report.json"
    with open(report_json, 'w') as f:
        json.dump(report, f, indent=2)

    print("\n=== V2X KPI Report ===")
    print(json.dumps(report, indent=2))

    calculator.close()
