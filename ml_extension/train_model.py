#!/usr/bin/env python3
"""
ML Model Training - Predict network performance degradation
Uses Random Forest to predict packet loss and latency spikes
"""

import pandas as pd
import numpy as np
import sqlite3
import pickle
import logging
from pathlib import Path
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, accuracy_score, classification_report
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class V2XMLModel:
    """Machine learning model for V2X performance prediction"""

    def __init__(self, db_path: str = '/data/v2x_testbed.db'):
        """Initialize ML model trainer"""
        self.db_path = db_path
        self.latency_model = None
        self.loss_model = None

    def load_and_prepare_data(self):
        """Load data and engineer features"""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query("SELECT * FROM messages ORDER BY receive_timestamp", conn)
        conn.close()

        if df.empty:
            raise ValueError("No data available for training")

        logger.info(f"Loaded {len(df)} messages")

        # Feature engineering
        df = df.sort_values('receive_timestamp')

        # Time-based features
        df['hour'] = pd.to_datetime(df['receive_timestamp'], unit='s').dt.hour
        df['minute'] = pd.to_datetime(df['receive_timestamp'], unit='s').dt.minute

        # Rolling window features (last 10 messages)
        df['latency_rolling_mean'] = df['latency_ms'].rolling(window=10, min_periods=1).mean()
        df['latency_rolling_std'] = df['latency_ms'].rolling(window=10, min_periods=1).std()

        # Protocol encoding
        df['protocol_encoded'] = df['protocol'].map({'UDP': 0, 'TCP': 1, 'MQTT': 2})

        # Message type encoding
        df['message_type_encoded'] = df['message_type'].map({'telemetry': 0, 'safety': 1})

        # Target: packet loss indicator (binary)
        df['has_loss'] = (df['sequence_gap'] > 0).astype(int)

        # Target: high latency indicator (> 95th percentile)
        latency_threshold = df['latency_ms'].quantile(0.95)
        df['high_latency'] = (df['latency_ms'] > latency_threshold).astype(int)

        return df

    def train_latency_predictor(self, df: pd.DataFrame):
        """Train regression model to predict latency"""
        features = [
            'protocol_encoded',
            'message_type_encoded',
            'latency_rolling_mean',
            'latency_rolling_std',
            'hour',
            'minute'
        ]

        # Remove NaN values
        df_clean = df[features + ['latency_ms']].dropna()

        X = df_clean[features]
        y = df_clean['latency_ms']

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        logger.info("Training latency prediction model...")
        self.latency_model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        self.latency_model.fit(X_train, y_train)

        # Evaluate
        y_pred = self.latency_model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)

        logger.info(f"Latency Model RMSE: {rmse:.2f} ms")

        # Feature importance
        feature_importance = dict(zip(features, self.latency_model.feature_importances_))
        logger.info(f"Feature Importance: {feature_importance}")

        return {
            'rmse': rmse,
            'feature_importance': feature_importance
        }

    def train_loss_classifier(self, df: pd.DataFrame):
        """Train classifier to predict packet loss probability"""
        features = [
            'protocol_encoded',
            'message_type_encoded',
            'latency_rolling_mean',
            'latency_rolling_std',
            'hour',
            'minute'
        ]

        df_clean = df[features + ['has_loss']].dropna()

        X = df_clean[features]
        y = df_clean['has_loss']

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        logger.info("Training packet loss classification model...")
        self.loss_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        self.loss_model.fit(X_train, y_train)

        # Evaluate
        y_pred = self.loss_model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)

        logger.info(f"Loss Classification Accuracy: {accuracy:.2%}")
        logger.info("\n" + classification_report(y_test, y_pred))

        return {
            'accuracy': accuracy,
            'classification_report': classification_report(y_test, y_pred, output_dict=True)
        }

    def save_models(self, output_dir: str = '/outputs'):
        """Save trained models to disk"""
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        if self.latency_model:
            latency_path = f"{output_dir}/latency_model.pkl"
            with open(latency_path, 'wb') as f:
                pickle.dump(self.latency_model, f)
            logger.info(f"Saved latency model to {latency_path}")

        if self.loss_model:
            loss_path = f"{output_dir}/loss_model.pkl"
            with open(loss_path, 'wb') as f:
                pickle.dump(self.loss_model, f)
            logger.info(f"Saved loss model to {loss_path}")

    def train_all(self):
        """Train all models"""
        df = self.load_and_prepare_data()

        results = {
            'latency_model': self.train_latency_predictor(df),
            'loss_model': self.train_loss_classifier(df)
        }

        self.save_models()

        return results


if __name__ == '__main__':
    import sys

    db_path = sys.argv[1] if len(sys.argv) > 1 else '/data/v2x_testbed.db'

    trainer = V2XMLModel(db_path)
    results = trainer.train_all()

    print("\n=== ML Model Training Results ===")
    print(json.dumps(results, indent=2, default=str))
