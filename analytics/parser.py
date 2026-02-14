#!/usr/bin/env python3
"""
PCAP Parser - Extract metrics from packet captures
Uses scapy for packet analysis
"""

import logging
import sys
from pathlib import Path
from typing import Dict, List, Any
import json

try:
    from scapy.all import rdpcap, IP, TCP, UDP
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False
    print("Warning: scapy not installed. PCAP parsing will be limited.")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PCAPParser:
    """Parse PCAP files and extract network metrics"""

    def __init__(self, pcap_file: str):
        """Initialize parser with PCAP file"""
        self.pcap_file = Path(pcap_file)
        if not self.pcap_file.exists():
            raise FileNotFoundError(f"PCAP file not found: {pcap_file}")

        if not SCAPY_AVAILABLE:
            raise ImportError("scapy is required for PCAP parsing")

        logger.info(f"Loading PCAP file: {pcap_file}")
        self.packets = rdpcap(str(self.pcap_file))
        logger.info(f"Loaded {len(self.packets)} packets")

    def extract_basic_stats(self) -> Dict[str, Any]:
        """Extract basic packet statistics"""
        stats = {
            'total_packets': len(self.packets),
            'tcp_packets': 0,
            'udp_packets': 0,
            'total_bytes': 0,
            'start_time': None,
            'end_time': None,
            'duration_seconds': 0,
            'avg_packet_size': 0
        }

        for pkt in self.packets:
            if stats['start_time'] is None:
                stats['start_time'] = float(pkt.time)
            stats['end_time'] = float(pkt.time)

            if IP in pkt:
                stats['total_bytes'] += len(pkt[IP])

                if TCP in pkt:
                    stats['tcp_packets'] += 1
                elif UDP in pkt:
                    stats['udp_packets'] += 1

        if stats['start_time'] and stats['end_time']:
            stats['duration_seconds'] = stats['end_time'] - stats['start_time']

        if stats['total_packets'] > 0:
            stats['avg_packet_size'] = stats['total_bytes'] / stats['total_packets']

        return stats

    def extract_tcp_metrics(self) -> Dict[str, Any]:
        """Extract TCP-specific metrics (retransmissions, RTT estimates)"""
        tcp_flows = {}
        retransmissions = 0

        for pkt in self.packets:
            if TCP in pkt and IP in pkt:
                src = pkt[IP].src
                dst = pkt[IP].dst
                sport = pkt[TCP].sport
                dport = pkt[TCP].dport
                seq = pkt[TCP].seq

                flow_key = f"{src}:{sport}-{dst}:{dport}"

                if flow_key not in tcp_flows:
                    tcp_flows[flow_key] = {
                        'sequences': [],
                        'timestamps': [],
                        'retrans_count': 0
                    }

                # Detect retransmission (same sequence number seen before)
                if seq in tcp_flows[flow_key]['sequences']:
                    tcp_flows[flow_key]['retrans_count'] += 1
                    retransmissions += 1
                else:
                    tcp_flows[flow_key]['sequences'].append(seq)
                    tcp_flows[flow_key]['timestamps'].append(float(pkt.time))

        return {
            'tcp_flows': len(tcp_flows),
            'total_retransmissions': retransmissions,
            'retransmission_rate': retransmissions / max(len(self.packets), 1) * 100
        }

    def extract_udp_metrics(self) -> Dict[str, Any]:
        """Extract UDP-specific metrics"""
        udp_flows = {}

        for pkt in self.packets:
            if UDP in pkt and IP in pkt:
                src = pkt[IP].src
                dst = pkt[IP].dst
                sport = pkt[UDP].sport
                dport = pkt[UDP].dport

                flow_key = f"{src}:{sport}-{dst}:{dport}"

                if flow_key not in udp_flows:
                    udp_flows[flow_key] = {
                        'packet_count': 0,
                        'total_bytes': 0
                    }

                udp_flows[flow_key]['packet_count'] += 1
                udp_flows[flow_key]['total_bytes'] += len(pkt[UDP])

        return {
            'udp_flows': len(udp_flows),
            'flows': udp_flows
        }

    def extract_inter_arrival_times(self, protocol: str = 'UDP', port: int = 5000) -> List[float]:
        """Extract inter-arrival times for specific protocol/port"""
        timestamps = []

        for pkt in self.packets:
            match = False

            if protocol == 'UDP' and UDP in pkt:
                if pkt[UDP].dport == port or pkt[UDP].sport == port:
                    match = True
            elif protocol == 'TCP' and TCP in pkt:
                if pkt[TCP].dport == port or pkt[TCP].sport == port:
                    match = True

            if match:
                timestamps.append(float(pkt.time))

        # Calculate inter-arrival times
        if len(timestamps) < 2:
            return []

        inter_arrivals = [timestamps[i] - timestamps[i-1] for i in range(1, len(timestamps))]
        return inter_arrivals

    def generate_report(self, output_file: str = None) -> Dict[str, Any]:
        """Generate comprehensive analysis report"""
        report = {
            'pcap_file': str(self.pcap_file),
            'basic_stats': self.extract_basic_stats(),
            'tcp_metrics': self.extract_tcp_metrics(),
            'udp_metrics': self.extract_udp_metrics()
        }

        # Calculate inter-arrival statistics
        udp_inter_arrivals = self.extract_inter_arrival_times('UDP', 5000)
        if udp_inter_arrivals:
            import numpy as np
            report['inter_arrival_stats'] = {
                'mean_ms': float(np.mean(udp_inter_arrivals) * 1000),
                'median_ms': float(np.median(udp_inter_arrivals) * 1000),
                'stddev_ms': float(np.std(udp_inter_arrivals) * 1000)
            }

        if output_file:
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2)
            logger.info(f"Report saved to {output_file}")

        return report


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python parser.py <pcap_file> [output_json]")
        sys.exit(1)

    pcap_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    parser = PCAPParser(pcap_file)
    report = parser.generate_report(output_file)

    print("\n=== PCAP Analysis Report ===")
    print(json.dumps(report, indent=2))
