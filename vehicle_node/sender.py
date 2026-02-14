#!/usr/bin/env python3
"""
Vehicle Node (OBU Simulator)
Sends telemetry and safety messages to edge server
Supports UDP, TCP, and MQTT protocols
"""

import socket
import time
import json
import logging
import yaml
import random
import sys
from datetime import datetime
from typing import Dict, Any
import paho.mqtt.client as mqtt

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/data/vehicle_node.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class VehicleNode:
    """Simulated vehicle onboard unit"""

    def __init__(self, config_path: str = 'config.yaml'):
        """Initialize vehicle node with configuration"""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        self.vehicle_id = self.config['vehicle']['vehicle_id']
        self.protocol = self.config['vehicle']['protocol']
        self.edge_host = self.config['edge_server']['host']
        self.edge_port = self.config['edge_server']['port']

        # Message counters
        self.telemetry_count = 0
        self.safety_count = 0

        # Simulated GPS state
        self.latitude = 37.7749  # San Francisco starting point
        self.longitude = -122.4194
        self.speed = 0.0

        # Initialize connection based on protocol
        self.socket = None
        self.mqtt_client = None
        self._init_connection()

        logger.info(f"Vehicle Node {self.vehicle_id} initialized with {self.protocol} protocol")

    def _init_connection(self):
        """Initialize network connection based on protocol"""
        if self.protocol == 'UDP':
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            logger.info(f"UDP socket created for {self.edge_host}:{self.edge_port}")

        elif self.protocol == 'TCP':
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                self.socket.connect((self.edge_host, self.edge_port))
                logger.info(f"TCP connection established to {self.edge_host}:{self.edge_port}")
            except Exception as e:
                logger.error(f"Failed to connect TCP: {e}")
                sys.exit(1)

        elif self.protocol == 'MQTT':
            self.mqtt_client = mqtt.Client(client_id=f"vehicle_{self.vehicle_id}")
            self.mqtt_client.on_connect = self._on_mqtt_connect
            self.mqtt_client.on_disconnect = self._on_mqtt_disconnect
            try:
                mqtt_host = self.config['mqtt']['broker_host']
                mqtt_port = self.config['mqtt']['broker_port']
                self.mqtt_client.connect(mqtt_host, mqtt_port, 60)
                self.mqtt_client.loop_start()
                logger.info(f"MQTT client connecting to {mqtt_host}:{mqtt_port}")
            except Exception as e:
                logger.error(f"Failed to connect MQTT: {e}")
                sys.exit(1)
        else:
            logger.error(f"Unknown protocol: {self.protocol}")
            sys.exit(1)

    def _on_mqtt_connect(self, client, userdata, flags, rc):
        """MQTT connection callback"""
        if rc == 0:
            logger.info("MQTT connected successfully")
        else:
            logger.error(f"MQTT connection failed with code {rc}")

    def _on_mqtt_disconnect(self, client, userdata, rc):
        """MQTT disconnection callback"""
        logger.warning(f"MQTT disconnected with code {rc}")

    def _update_simulated_position(self):
        """Update simulated GPS coordinates and speed"""
        # Simulate vehicle movement with random walk
        self.latitude += random.uniform(-0.0001, 0.0001)
        self.longitude += random.uniform(-0.0001, 0.0001)
        self.speed = max(0, min(120, self.speed + random.uniform(-5, 5)))

    def create_telemetry_message(self) -> Dict[str, Any]:
        """Create telemetry message"""
        self.telemetry_count += 1
        self._update_simulated_position()

        message = {
            'message_id': f"TEL_{self.vehicle_id}_{self.telemetry_count}",
            'send_timestamp': time.time(),
            'vehicle_id': self.vehicle_id,
            'message_type': 'telemetry',
            'latitude': self.latitude,
            'longitude': self.longitude,
            'speed': round(self.speed, 2),
            'heading': random.randint(0, 359),
            'battery_level': random.randint(20, 100)
        }
        return message

    def create_safety_message(self) -> Dict[str, Any]:
        """Create high-priority safety message"""
        self.safety_count += 1

        message = {
            'message_id': f"SAF_{self.vehicle_id}_{self.safety_count}",
            'send_timestamp': time.time(),
            'vehicle_id': self.vehicle_id,
            'message_type': 'safety',
            'latitude': self.latitude,
            'longitude': self.longitude,
            'speed': round(self.speed, 2),
            'alert_type': random.choice(['hard_brake', 'collision_warning', 'lane_change', 'emergency_stop']),
            'severity': random.choice(['low', 'medium', 'high'])
        }
        return message

    def send_message(self, message: Dict[str, Any]):
        """Send message using configured protocol"""
        payload = json.dumps(message).encode('utf-8')

        try:
            if self.protocol == 'UDP':
                self.socket.sendto(payload, (self.edge_host, self.edge_port))

            elif self.protocol == 'TCP':
                # Add length prefix for TCP to handle message boundaries
                length = len(payload)
                self.socket.sendall(length.to_bytes(4, 'big') + payload)

            elif self.protocol == 'MQTT':
                topic = f"v2x/{self.vehicle_id}/{message['message_type']}"
                self.mqtt_client.publish(topic, payload, qos=1)

            logger.debug(f"Sent {message['message_type']} message: {message['message_id']}")

        except Exception as e:
            logger.error(f"Failed to send message: {e}")

    def run(self):
        """Main loop - send telemetry and safety messages"""
        logger.info("Starting vehicle node transmission loop")

        telemetry_interval = self.config['vehicle']['telemetry_interval_ms'] / 1000.0
        safety_interval = self.config['vehicle']['safety_interval_ms'] / 1000.0

        last_telemetry_time = 0
        last_safety_time = 0

        try:
            while True:
                current_time = time.time()

                # Send telemetry every 100ms
                if current_time - last_telemetry_time >= telemetry_interval:
                    telemetry_msg = self.create_telemetry_message()
                    self.send_message(telemetry_msg)
                    last_telemetry_time = current_time

                # Send safety message every 1 second
                if current_time - last_safety_time >= safety_interval:
                    safety_msg = self.create_safety_message()
                    self.send_message(safety_msg)
                    last_safety_time = current_time

                # Sleep to prevent busy loop
                time.sleep(0.01)

        except KeyboardInterrupt:
            logger.info("Shutting down vehicle node")
        finally:
            self.cleanup()

    def cleanup(self):
        """Clean up resources"""
        if self.socket:
            self.socket.close()
        if self.mqtt_client:
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()
        logger.info("Vehicle node shutdown complete")


if __name__ == '__main__':
    node = VehicleNode('/config/config.yaml')
    node.run()
