"""
Real-time metrics calculator
Computes KPIs from received messages
"""

import logging
import numpy as np
from typing import Dict, Any, List
from database import Database

logger = logging.getLogger(__name__)


class MetricsCalculator:
    """Calculate V2X performance metrics"""

    def __init__(self, db: Database):
        """Initialize metrics calculator"""
        self.db = db

    def calculate_latency_stats(
        self,
        message_type: str = None,
        protocol: str = None,
        time_window_seconds: int = None
    ) -> Dict[str, float]:
        """Calculate latency statistics"""
        messages = self.db.get_messages(message_type=message_type)

        if not messages:
            return {
                'avg_latency_ms': 0.0,
                'median_latency_ms': 0.0,
                'p95_latency_ms': 0.0,
                'p99_latency_ms': 0.0,
                'min_latency_ms': 0.0,
                'max_latency_ms': 0.0,
                'stddev_latency_ms': 0.0
            }

        latencies = [msg['latency_ms'] for msg in messages]

        return {
            'avg_latency_ms': float(np.mean(latencies)),
            'median_latency_ms': float(np.median(latencies)),
            'p95_latency_ms': float(np.percentile(latencies, 95)),
            'p99_latency_ms': float(np.percentile(latencies, 99)),
            'min_latency_ms': float(np.min(latencies)),
            'max_latency_ms': float(np.max(latencies)),
            'stddev_latency_ms': float(np.std(latencies))
        }

    def calculate_jitter(self, message_type: str = None) -> float:
        """Calculate jitter (variance in latency)"""
        messages = self.db.get_messages(message_type=message_type, limit=1000)

        if len(messages) < 2:
            return 0.0

        latencies = [msg['latency_ms'] for msg in messages]

        # Jitter is the average absolute difference between consecutive latencies
        diffs = [abs(latencies[i] - latencies[i-1]) for i in range(1, len(latencies))]

        return float(np.mean(diffs)) if diffs else 0.0

    def calculate_packet_loss_rate(self, message_type: str = None) -> float:
        """Calculate packet loss rate based on sequence gaps"""
        messages = self.db.get_messages(message_type=message_type)

        if not messages:
            return 0.0

        total_expected = len(messages) + sum(msg['sequence_gap'] for msg in messages)
        total_received = len(messages)

        if total_expected == 0:
            return 0.0

        loss_rate = (total_expected - total_received) / total_expected * 100
        return max(0.0, min(100.0, loss_rate))

    def calculate_throughput(self, time_window_seconds: int = 60) -> Dict[str, float]:
        """Calculate throughput metrics"""
        messages = self.db.get_messages(limit=10000)

        if not messages:
            return {
                'messages_per_second': 0.0,
                'bytes_per_second': 0.0,
                'kbps': 0.0
            }

        # Calculate time span
        timestamps = [msg['receive_timestamp'] for msg in messages]
        time_span = max(timestamps) - min(timestamps)

        if time_span == 0:
            return {
                'messages_per_second': 0.0,
                'bytes_per_second': 0.0,
                'kbps': 0.0
            }

        # Calculate rates
        total_messages = len(messages)
        total_bytes = sum(msg.get('payload_size', 0) for msg in messages)

        messages_per_second = total_messages / time_span
        bytes_per_second = total_bytes / time_span
        kbps = (bytes_per_second * 8) / 1000  # Convert to kilobits per second

        return {
            'messages_per_second': round(messages_per_second, 2),
            'bytes_per_second': round(bytes_per_second, 2),
            'kbps': round(kbps, 2)
        }

    def get_protocol_comparison(self) -> Dict[str, Dict[str, Any]]:
        """Compare performance across protocols"""
        protocols = ['UDP', 'TCP', 'MQTT']
        comparison = {}

        for protocol in protocols:
            stats = self.db.get_statistics(protocol=protocol)

            if stats.get('total_messages', 0) > 0:
                comparison[protocol] = {
                    'total_messages': stats.get('total_messages', 0),
                    'avg_latency_ms': round(stats.get('avg_latency', 0), 2),
                    'min_latency_ms': round(stats.get('min_latency', 0), 2),
                    'max_latency_ms': round(stats.get('max_latency', 0), 2),
                    'total_packet_loss': stats.get('total_gaps', 0)
                }

        return comparison

    def get_realtime_metrics(self) -> Dict[str, Any]:
        """Get current real-time metrics for dashboard"""
        return {
            'latency_stats': self.calculate_latency_stats(),
            'jitter_ms': round(self.calculate_jitter(), 2),
            'packet_loss_rate': round(self.calculate_packet_loss_rate(), 2),
            'throughput': self.calculate_throughput(),
            'protocol_comparison': self.get_protocol_comparison()
        }
