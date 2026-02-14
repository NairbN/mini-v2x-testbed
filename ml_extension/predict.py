#!/usr/bin/env python3
"""
ML Prediction - Use trained models to predict network performance
"""

import pickle
import numpy as np
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class V2XPredictor:
    """Predict V2X performance using trained models"""

    def __init__(self, model_dir: str = '/outputs'):
        """Load trained models"""
        self.latency_model = None
        self.loss_model = None

        try:
            with open(f"{model_dir}/latency_model.pkl", 'rb') as f:
                self.latency_model = pickle.load(f)
            logger.info("Loaded latency prediction model")
        except FileNotFoundError:
            logger.warning("Latency model not found")

        try:
            with open(f"{model_dir}/loss_model.pkl", 'rb') as f:
                self.loss_model = pickle.load(f)
            logger.info("Loaded loss prediction model")
        except FileNotFoundError:
            logger.warning("Loss model not found")

    def predict_latency(
        self,
        protocol: str,
        message_type: str,
        latency_rolling_mean: float,
        latency_rolling_std: float,
        hour: int,
        minute: int
    ) -> float:
        """Predict expected latency"""
        if not self.latency_model:
            raise ValueError("Latency model not loaded")

        protocol_map = {'UDP': 0, 'TCP': 1, 'MQTT': 2}
        message_type_map = {'telemetry': 0, 'safety': 1}

        features = np.array([[
            protocol_map.get(protocol, 0),
            message_type_map.get(message_type, 0),
            latency_rolling_mean,
            latency_rolling_std,
            hour,
            minute
        ]])

        prediction = self.latency_model.predict(features)[0]
        return float(prediction)

    def predict_packet_loss_probability(
        self,
        protocol: str,
        message_type: str,
        latency_rolling_mean: float,
        latency_rolling_std: float,
        hour: int,
        minute: int
    ) -> float:
        """Predict probability of packet loss"""
        if not self.loss_model:
            raise ValueError("Loss model not loaded")

        protocol_map = {'UDP': 0, 'TCP': 1, 'MQTT': 2}
        message_type_map = {'telemetry': 0, 'safety': 1}

        features = np.array([[
            protocol_map.get(protocol, 0),
            message_type_map.get(message_type, 0),
            latency_rolling_mean,
            latency_rolling_std,
            hour,
            minute
        ]])

        # Predict probability of class 1 (packet loss)
        probability = self.loss_model.predict_proba(features)[0][1]
        return float(probability)


if __name__ == '__main__':
    predictor = V2XPredictor()

    # Example prediction
    predicted_latency = predictor.predict_latency(
        protocol='UDP',
        message_type='telemetry',
        latency_rolling_mean=25.5,
        latency_rolling_std=5.2,
        hour=14,
        minute=30
    )

    loss_probability = predictor.predict_packet_loss_probability(
        protocol='UDP',
        message_type='telemetry',
        latency_rolling_mean=25.5,
        latency_rolling_std=5.2,
        hour=14,
        minute=30
    )

    print(f"\nPredicted Latency: {predicted_latency:.2f} ms")
    print(f"Packet Loss Probability: {loss_probability:.2%}")
