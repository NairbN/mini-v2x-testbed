#!/usr/bin/env python3
"""
Edge Server - Receives and processes messages from vehicle nodes
Supports UDP, TCP, and MQTT protocols
"""

import socket
import json
import time
import logging
import sys
import threading
from typing import Dict, Any
import paho.mqtt.client as mqtt
from database import Database
from metrics import MetricsCalculator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/data/edge_server.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class EdgeServer:
    """Edge server for receiving V2X messages"""

    def __init__(self, protocol: str = 'UDP', port: int = 5000):
        """Initialize edge server"""
        self.protocol = protocol
        self.port = port
        self.db = Database('/data/v2x_testbed.db')
        self.metrics = MetricsCalculator(self.db)

        # Message tracking for detecting losses
        self.last_message_ids = {}

        logger.info(f"Edge Server initialized with {protocol} on port {port}")

    def process_message(self, message_data: bytes, protocol: str):
        """Process received message and calculate metrics"""
        try:
            receive_timestamp = time.time()
            message = json.loads(message_data.decode('utf-8'))

            # Calculate end-to-end latency
            send_timestamp = message.get('send_timestamp', receive_timestamp)
            latency_ms = (receive_timestamp - send_timestamp) * 1000

            # Extract message details
            message_id = message.get('message_id', 'unknown')
            vehicle_id = message.get('vehicle_id', 'unknown')
            message_type = message.get('message_type', 'unknown')

            # Detect packet loss (out of sequence)
            sequence_gap = self._detect_sequence_gap(vehicle_id, message_id, message_type)

            # Store in database
            self.db.insert_message(
                message_id=message_id,
                vehicle_id=vehicle_id,
                message_type=message_type,
                send_timestamp=send_timestamp,
                receive_timestamp=receive_timestamp,
                latency_ms=latency_ms,
                protocol=protocol,
                sequence_gap=sequence_gap,
                payload_size=len(message_data)
            )

            logger.debug(
                f"Processed {message_type} from {vehicle_id}: "
                f"latency={latency_ms:.2f}ms, gap={sequence_gap}"
            )

        except Exception as e:
            logger.error(f"Error processing message: {e}")

    def _detect_sequence_gap(self, vehicle_id: str, message_id: str, message_type: str) -> int:
        """Detect gaps in message sequence (packet loss indicator)"""
        try:
            # Extract sequence number from message_id (format: TYPE_VEH_XXX_SEQNUM)
            parts = message_id.split('_')
            if len(parts) >= 4:
                current_seq = int(parts[-1])
                key = f"{vehicle_id}_{message_type}"

                if key in self.last_message_ids:
                    expected_seq = self.last_message_ids[key] + 1
                    gap = current_seq - expected_seq
                    self.last_message_ids[key] = current_seq
                    return max(0, gap)
                else:
                    self.last_message_ids[key] = current_seq
                    return 0
        except Exception as e:
            logger.debug(f"Could not parse sequence from {message_id}: {e}")

        return 0

    def run_udp_server(self):
        """Run UDP server"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('0.0.0.0', self.port))

        logger.info(f"UDP server listening on port {self.port}")

        try:
            while True:
                data, addr = sock.recvfrom(4096)
                self.process_message(data, 'UDP')
        except KeyboardInterrupt:
            logger.info("Shutting down UDP server")
        finally:
            sock.close()

    def run_tcp_server(self):
        """Run TCP server"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('0.0.0.0', self.port))
        sock.listen(5)

        logger.info(f"TCP server listening on port {self.port}")

        try:
            while True:
                client_sock, addr = sock.accept()
                logger.info(f"TCP client connected from {addr}")
                threading.Thread(
                    target=self._handle_tcp_client,
                    args=(client_sock,),
                    daemon=True
                ).start()
        except KeyboardInterrupt:
            logger.info("Shutting down TCP server")
        finally:
            sock.close()

    def _handle_tcp_client(self, client_sock):
        """Handle individual TCP client connection"""
        try:
            while True:
                # Read 4-byte length prefix
                length_bytes = client_sock.recv(4)
                if not length_bytes:
                    break

                message_length = int.from_bytes(length_bytes, 'big')

                # Read message payload
                data = b''
                while len(data) < message_length:
                    chunk = client_sock.recv(min(4096, message_length - len(data)))
                    if not chunk:
                        break
                    data += chunk

                if len(data) == message_length:
                    self.process_message(data, 'TCP')
        except Exception as e:
            logger.error(f"TCP client error: {e}")
        finally:
            client_sock.close()

    def run_mqtt_server(self):
        """Run MQTT subscriber"""
        client = mqtt.Client(client_id="edge_server")

        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                logger.info("MQTT connected, subscribing to v2x/#")
                client.subscribe("v2x/#", qos=1)
            else:
                logger.error(f"MQTT connection failed: {rc}")

        def on_message(client, userdata, msg):
            self.process_message(msg.payload, 'MQTT')

        client.on_connect = on_connect
        client.on_message = on_message

        try:
            client.connect("mqtt_broker", 1883, 60)
            logger.info("MQTT client connected")
            client.loop_forever()
        except KeyboardInterrupt:
            logger.info("Shutting down MQTT client")
        finally:
            client.disconnect()

    def run(self):
        """Start server based on protocol"""
        if self.protocol == 'UDP':
            self.run_udp_server()
        elif self.protocol == 'TCP':
            self.run_tcp_server()
        elif self.protocol == 'MQTT':
            self.run_mqtt_server()
        else:
            logger.error(f"Unknown protocol: {self.protocol}")
            sys.exit(1)


if __name__ == '__main__':
    import os
    protocol = os.getenv('PROTOCOL', 'UDP')
    port = int(os.getenv('PORT', 5000))

    server = EdgeServer(protocol=protocol, port=port)
    server.run()
