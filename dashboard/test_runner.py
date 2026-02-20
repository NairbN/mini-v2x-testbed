"""
Test Orchestrator for V2X Dashboard Control Center
Manages experiment execution, progress tracking, and cleanup
"""

import subprocess
import threading
import logging
import re
import time
import json
import os
import signal
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import sys

# Add edge_server to path to import Database
sys.path.append('/app')
sys.path.append('/edge_server')
from database import Database

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class TestOrchestrator:
    """Manages test execution, progress tracking, and cleanup"""

    def __init__(self, db_path: str = '/data/v2x_testbed.db'):
        """Initialize orchestrator with database connection"""
        self.db = Database(db_path)
        self.processes = {}  # {run_id: subprocess.Popen}
        self.threads = {}    # {run_id: threading.Thread}
        self.network_profiles = ['normal', 'moderate', 'severe', 'handoff']
        self.valid_protocols = ['UDP', 'TCP', 'MQTT', 'ALL']
        logger.info("TestOrchestrator initialized")

    def validate_experiment_name(self, name: str) -> tuple[bool, str]:
        """Validate experiment name (alphanumeric + underscore only)"""
        if not name:
            return False, "Experiment name cannot be empty"

        if not re.match(r'^[a-zA-Z0-9_]+$', name):
            return False, "Experiment name must contain only letters, numbers, and underscores"

        if len(name) > 100:
            return False, "Experiment name must be less than 100 characters"

        # Check for duplicate names
        existing = self.db.get_experiment_by_name(name)
        if existing:
            return False, f"Experiment '{name}' already exists"

        return True, ""

    def validate_inputs(
        self,
        name: str,
        duration: int,
        profile: str,
        protocol: str
    ) -> tuple[bool, str]:
        """Validate all experiment inputs"""

        # Validate name
        valid, msg = self.validate_experiment_name(name)
        if not valid:
            return False, msg

        # Validate duration
        if not (10 <= duration <= 300):
            return False, "Duration must be between 10 and 300 seconds"

        # Validate network profile
        if profile not in self.network_profiles:
            return False, f"Invalid network profile. Must be one of: {', '.join(self.network_profiles)}"

        # Validate protocol
        if protocol not in self.valid_protocols:
            return False, f"Invalid protocol. Must be one of: {', '.join(self.valid_protocols)}"

        # Check available disk space (basic check)
        try:
            stat = os.statvfs('/outputs')
            free_space_gb = (stat.f_bavail * stat.f_frsize) / (1024**3)
            if free_space_gb < 0.5:  # Less than 500MB
                return False, f"Insufficient disk space: {free_space_gb:.2f}GB available"
        except Exception as e:
            logger.warning(f"Could not check disk space: {e}")

        return True, ""

    def start_experiment(
        self,
        name: str,
        duration: int,
        profile: str,
        protocol: str = 'ALL',
        advanced_options: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Start new experiment (queued if one already running)
        Returns: {'success': bool, 'run_id': int, 'status': str, 'message': str}
        """

        # Validate inputs
        valid, error_msg = self.validate_inputs(name, duration, profile, protocol)
        if not valid:
            return {'success': False, 'run_id': None, 'status': 'error', 'message': error_msg}

        # Check for running experiments (queue enforcement)
        running = self.db.get_running_experiment()
        if running:
            return {
                'success': False,
                'run_id': None,
                'status': 'blocked',
                'message': f"Experiment '{running['experiment_name']}' is already running. Please wait for it to complete."
            }

        # Create database entry
        try:
            advanced_json = json.dumps(advanced_options) if advanced_options else None
            run_id = self.db.create_experiment_run(
                name=name,
                profile=profile,
                duration=duration,
                protocol=protocol,
                advanced_options=advanced_json
            )

            logger.info(f"Created experiment run {run_id}: {name}")

            # Launch experiment in background thread
            thread = threading.Thread(
                target=self._execute_experiment,
                args=(run_id,),
                daemon=True
            )
            thread.start()
            self.threads[run_id] = thread

            return {
                'success': True,
                'run_id': run_id,
                'status': 'started',
                'message': f"Experiment '{name}' started successfully"
            }

        except Exception as e:
            logger.error(f"Failed to start experiment: {e}")
            return {
                'success': False,
                'run_id': None,
                'status': 'error',
                'message': f"Failed to start experiment: {str(e)}"
            }

    def _execute_experiment(self, run_id: int):
        """
        Background executor - runs in separate thread
        Launches run_experiment.sh via subprocess
        Monitors stdout/stderr for progress markers
        Updates database with progress
        """

        exp = self.db.get_experiment_run(run_id)
        if not exp:
            logger.error(f"Experiment {run_id} not found")
            return

        name = exp['experiment_name']
        duration = exp['duration_seconds']
        profile = exp['network_profile']

        logger.info(f"Executing experiment {run_id}: {name}")

        try:
            # Update status to running
            self.db.update_experiment_status(run_id, status='running', phase='initializing', progress=0)

            # Build command
            cmd = [
                'bash',
                '/app/run_experiment.sh',
                name,
                str(duration),
                profile
            ]

            logger.info(f"Running command: {' '.join(cmd)}")

            # Start subprocess
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )

            self.processes[run_id] = process
            self.db.update_experiment_status(run_id, process_id=process.pid)

            # Monitor output for progress markers
            phase_pattern = re.compile(r'PHASE:(\w+)\|(\d+)')

            for line in process.stdout:
                logger.info(f"[{name}] {line.strip()}")

                # Check for progress markers
                match = phase_pattern.search(line)
                if match:
                    phase = match.group(1)
                    progress = int(match.group(2))
                    self.db.update_experiment_status(
                        run_id,
                        phase=phase,
                        progress=progress
                    )
                    logger.info(f"Progress: {phase} - {progress}%")

            # Wait for process to complete
            return_code = process.wait()

            # Update final status
            if return_code == 0:
                self.db.update_experiment_status(
                    run_id,
                    status='completed',
                    phase='completed',
                    progress=100
                )
                logger.info(f"Experiment {name} completed successfully")
            else:
                self.db.update_experiment_status(
                    run_id,
                    status='failed',
                    error_msg=f"Process exited with code {return_code}"
                )
                logger.error(f"Experiment {name} failed with code {return_code}")

        except Exception as e:
            logger.error(f"Error executing experiment {name}: {e}")
            self.db.update_experiment_status(
                run_id,
                status='failed',
                error_msg=str(e)
            )

        finally:
            # Cleanup
            if run_id in self.processes:
                del self.processes[run_id]

            # Always clear network profile
            self._clear_network_profile()

    def _clear_network_profile(self):
        """Clear network traffic shaping rules"""
        try:
            subprocess.run(
                ['bash', '/network_profiles/clear.sh'],
                capture_output=True,
                text=True,
                timeout=10
            )
            logger.info("Network profile cleared")
        except Exception as e:
            logger.error(f"Failed to clear network profile: {e}")

    def get_experiment_status(self, run_id: int) -> Dict[str, Any]:
        """Fetch current experiment state from database"""
        exp = self.db.get_experiment_run(run_id)

        if not exp:
            return {'error': 'Experiment not found'}

        # Calculate elapsed time if running
        if exp.get('started_at') and exp['status'] == 'running':
            started = datetime.fromisoformat(exp['started_at'])
            elapsed = (datetime.now() - started).total_seconds()
            exp['elapsed_seconds'] = int(elapsed)
            exp['remaining_seconds'] = max(0, exp['duration_seconds'] - int(elapsed))

        return exp

    def cancel_experiment(self, run_id: int) -> Dict[str, Any]:
        """
        Terminate running experiment, cleanup resources
        Returns: {'success': bool, 'message': str}
        """

        exp = self.db.get_experiment_run(run_id)
        if not exp:
            return {'success': False, 'message': 'Experiment not found'}

        if exp['status'] not in ('running', 'pending'):
            return {'success': False, 'message': f"Cannot cancel experiment with status '{exp['status']}'"}

        try:
            # Kill subprocess if exists
            if run_id in self.processes:
                process = self.processes[run_id]
                if process.poll() is None:  # Still running
                    logger.info(f"Terminating process {process.pid}")
                    process.terminate()

                    # Wait up to 5 seconds for graceful shutdown
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        logger.warning("Process did not terminate gracefully, killing...")
                        process.kill()
                        process.wait()

                del self.processes[run_id]

            # Update database
            self.db.update_experiment_status(
                run_id,
                status='cancelled',
                error_msg='Cancelled by user'
            )

            # Clear network profile
            self._clear_network_profile()

            logger.info(f"Experiment {run_id} cancelled successfully")
            return {'success': True, 'message': 'Experiment cancelled successfully'}

        except Exception as e:
            logger.error(f"Error cancelling experiment {run_id}: {e}")
            return {'success': False, 'message': f'Error: {str(e)}'}

    def get_experiment_results(self, run_id: int) -> Dict[str, Any]:
        """
        Load results from output directory (JSON, CSVs)
        Returns parsed KPI data
        """

        exp = self.db.get_experiment_run(run_id)
        if not exp:
            return {'error': 'Experiment not found'}

        if exp['status'] != 'completed':
            return {'error': f"Experiment has status '{exp['status']}', no results available"}

        output_dir = exp['output_directory']
        kpi_file = os.path.join(output_dir, 'kpi_report.json')

        if not os.path.exists(kpi_file):
            return {'error': 'Results file not found'}

        try:
            with open(kpi_file, 'r') as f:
                results = json.load(f)

            # Add experiment metadata
            results['experiment_name'] = exp['experiment_name']
            results['network_profile'] = exp['network_profile']
            results['duration_seconds'] = exp['duration_seconds']
            results['started_at'] = exp['started_at']
            results['completed_at'] = exp['completed_at']

            return results

        except Exception as e:
            logger.error(f"Error loading results for experiment {run_id}: {e}")
            return {'error': f'Failed to load results: {str(e)}'}

    def list_experiments(
        self,
        limit: int = 20,
        status_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List experiment runs with optional status filter"""
        return self.db.list_experiment_runs(limit=limit, status_filter=status_filter)

    def get_running_experiment(self) -> Optional[Dict[str, Any]]:
        """Get currently running experiment"""
        return self.db.get_running_experiment()

    def cleanup_old_experiments(self, days: int = 30) -> Dict[str, Any]:
        """
        Delete experiments older than N days
        Returns: {'deleted': int, 'errors': list}
        """

        cutoff_date = datetime.now() - timedelta(days=days)
        deleted_count = 0
        errors = []

        try:
            all_experiments = self.db.list_experiment_runs(limit=None)

            for exp in all_experiments:
                created_at = datetime.fromisoformat(exp['created_at'])

                if created_at < cutoff_date:
                    # Delete output directory if exists
                    output_dir = exp['output_directory']
                    if os.path.exists(output_dir):
                        try:
                            import shutil
                            shutil.rmtree(output_dir)
                            logger.info(f"Deleted output directory: {output_dir}")
                        except Exception as e:
                            errors.append(f"Failed to delete {output_dir}: {e}")

                    # Delete database entry
                    if self.db.delete_experiment_run(exp['id']):
                        deleted_count += 1

            logger.info(f"Cleaned up {deleted_count} old experiments")
            return {'deleted': deleted_count, 'errors': errors}

        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
            return {'deleted': deleted_count, 'errors': [str(e)]}


# Singleton instance for use in Streamlit pages
_orchestrator_instance = None

def get_orchestrator() -> TestOrchestrator:
    """Get singleton TestOrchestrator instance"""
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = TestOrchestrator()
    return _orchestrator_instance
