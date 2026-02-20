"""
Database module for storing V2X messages and metrics
Uses SQLite for simplicity
"""

import sqlite3
import logging
from typing import Optional, List, Dict, Any
from contextlib import contextmanager
import threading

logger = logging.getLogger(__name__)


class Database:
    """SQLite database manager for V2X testbed"""

    def __init__(self, db_path: str = '/data/v2x_testbed.db'):
        """Initialize database connection"""
        self.db_path = db_path
        self.local = threading.local()
        self._init_database()
        logger.info(f"Database initialized at {db_path}")

    @contextmanager
    def get_connection(self):
        """Thread-safe database connection context manager"""
        if not hasattr(self.local, 'conn'):
            self.local.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.local.conn.row_factory = sqlite3.Row

        try:
            yield self.local.conn
        except Exception as e:
            self.local.conn.rollback()
            raise e

    def _init_database(self):
        """Create database schema"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Messages table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message_id TEXT NOT NULL,
                    vehicle_id TEXT NOT NULL,
                    message_type TEXT NOT NULL,
                    send_timestamp REAL NOT NULL,
                    receive_timestamp REAL NOT NULL,
                    latency_ms REAL NOT NULL,
                    protocol TEXT NOT NULL,
                    sequence_gap INTEGER DEFAULT 0,
                    payload_size INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Network conditions table (for experiment tracking)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS network_conditions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    condition_name TEXT NOT NULL,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    delay_ms INTEGER,
                    loss_percent REAL,
                    bandwidth_limit TEXT,
                    description TEXT
                )
            ''')

            # Packet capture metadata
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS pcap_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_name TEXT NOT NULL,
                    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    end_time TIMESTAMP,
                    pcap_file_path TEXT,
                    packet_count INTEGER
                )
            ''')

            # Experiment runs (for UI test control)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS experiment_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    experiment_name TEXT UNIQUE NOT NULL,
                    status TEXT NOT NULL,
                    network_profile TEXT NOT NULL,
                    duration_seconds INTEGER NOT NULL,
                    protocol TEXT,
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    progress_percent INTEGER DEFAULT 0,
                    current_phase TEXT,
                    error_message TEXT,
                    output_directory TEXT,
                    process_id INTEGER,
                    advanced_options TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Create indexes
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_message_id ON messages(message_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_vehicle_id ON messages(vehicle_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_message_type ON messages(message_type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamps ON messages(send_timestamp, receive_timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_experiment_status ON experiment_runs(status)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_experiment_created ON experiment_runs(created_at)')

            conn.commit()

    def insert_message(
        self,
        message_id: str,
        vehicle_id: str,
        message_type: str,
        send_timestamp: float,
        receive_timestamp: float,
        latency_ms: float,
        protocol: str,
        sequence_gap: int = 0,
        payload_size: Optional[int] = None
    ):
        """Insert received message into database"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO messages (
                    message_id, vehicle_id, message_type,
                    send_timestamp, receive_timestamp, latency_ms,
                    protocol, sequence_gap, payload_size
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                message_id, vehicle_id, message_type,
                send_timestamp, receive_timestamp, latency_ms,
                protocol, sequence_gap, payload_size
            ))
            conn.commit()

    def insert_network_condition(
        self,
        condition_name: str,
        delay_ms: Optional[int] = None,
        loss_percent: Optional[float] = None,
        bandwidth_limit: Optional[str] = None,
        description: Optional[str] = None
    ):
        """Record network condition change"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO network_conditions (
                    condition_name, delay_ms, loss_percent, bandwidth_limit, description
                ) VALUES (?, ?, ?, ?, ?)
            ''', (condition_name, delay_ms, loss_percent, bandwidth_limit, description))
            conn.commit()

    def get_messages(
        self,
        limit: Optional[int] = None,
        message_type: Optional[str] = None,
        vehicle_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve messages with optional filters"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            query = 'SELECT * FROM messages WHERE 1=1'
            params = []

            if message_type:
                query += ' AND message_type = ?'
                params.append(message_type)

            if vehicle_id:
                query += ' AND vehicle_id = ?'
                params.append(vehicle_id)

            query += ' ORDER BY receive_timestamp DESC'

            if limit:
                query += ' LIMIT ?'
                params.append(limit)

            cursor.execute(query, params)
            rows = cursor.fetchall()

            return [dict(row) for row in rows]

    def get_statistics(self, protocol: Optional[str] = None) -> Dict[str, Any]:
        """Get overall statistics"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            where_clause = ''
            params = []
            if protocol:
                where_clause = 'WHERE protocol = ?'
                params.append(protocol)

            cursor.execute(f'''
                SELECT
                    COUNT(*) as total_messages,
                    AVG(latency_ms) as avg_latency,
                    MIN(latency_ms) as min_latency,
                    MAX(latency_ms) as max_latency,
                    SUM(sequence_gap) as total_gaps
                FROM messages
                {where_clause}
            ''', params)

            row = cursor.fetchone()
            return dict(row) if row else {}

    def clear_data(self):
        """Clear all message data (for new experiments)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM messages')
            cursor.execute('DELETE FROM network_conditions')
            conn.commit()
        logger.info("Database cleared")

    # Experiment management methods
    def create_experiment_run(
        self,
        name: str,
        profile: str,
        duration: int,
        protocol: str = 'ALL',
        advanced_options: Optional[str] = None
    ) -> int:
        """Create new experiment run entry"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO experiment_runs (
                    experiment_name, status, network_profile,
                    duration_seconds, protocol, advanced_options,
                    output_directory
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (name, 'pending', profile, duration, protocol, advanced_options, f'/outputs/{name}'))
            conn.commit()
            return cursor.lastrowid

    def update_experiment_status(
        self,
        run_id: int,
        status: Optional[str] = None,
        progress: Optional[int] = None,
        phase: Optional[str] = None,
        error_msg: Optional[str] = None,
        process_id: Optional[int] = None
    ):
        """Update experiment status and progress"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            updates = []
            params = []

            if status:
                updates.append('status = ?')
                params.append(status)
                if status == 'running' and not self.get_experiment_run(run_id).get('started_at'):
                    updates.append('started_at = CURRENT_TIMESTAMP')
                elif status in ('completed', 'failed', 'cancelled'):
                    updates.append('completed_at = CURRENT_TIMESTAMP')

            if progress is not None:
                updates.append('progress_percent = ?')
                params.append(progress)

            if phase:
                updates.append('current_phase = ?')
                params.append(phase)

            if error_msg:
                updates.append('error_message = ?')
                params.append(error_msg)

            if process_id is not None:
                updates.append('process_id = ?')
                params.append(process_id)

            if updates:
                params.append(run_id)
                query = f"UPDATE experiment_runs SET {', '.join(updates)} WHERE id = ?"
                cursor.execute(query, params)
                conn.commit()

    def get_experiment_run(self, run_id: int) -> Dict[str, Any]:
        """Get experiment run by ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM experiment_runs WHERE id = ?', (run_id,))
            row = cursor.fetchone()
            return dict(row) if row else {}

    def get_experiment_by_name(self, name: str) -> Dict[str, Any]:
        """Get experiment run by name"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM experiment_runs WHERE experiment_name = ?', (name,))
            row = cursor.fetchone()
            return dict(row) if row else {}

    def list_experiment_runs(
        self,
        limit: Optional[int] = 20,
        status_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List experiment runs with optional status filter"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            query = 'SELECT * FROM experiment_runs WHERE 1=1'
            params = []

            if status_filter:
                query += ' AND status = ?'
                params.append(status_filter)

            query += ' ORDER BY created_at DESC'

            if limit:
                query += ' LIMIT ?'
                params.append(limit)

            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def get_running_experiment(self) -> Optional[Dict[str, Any]]:
        """Get currently running experiment (only one allowed at a time)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM experiment_runs
                WHERE status IN ('running', 'pending')
                ORDER BY created_at DESC
                LIMIT 1
            ''')
            row = cursor.fetchone()
            return dict(row) if row else None

    def delete_experiment_run(self, run_id: int) -> bool:
        """Delete experiment run"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM experiment_runs WHERE id = ?', (run_id,))
            conn.commit()
            return cursor.rowcount > 0
