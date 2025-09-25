"""
Deployment history management system.

This module provides functionality for storing, retrieving, and managing
deployment history records with search and filtering capabilities.
"""

import json
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import sqlite3
from contextlib import contextmanager

from .models import DeploymentRecord, DeploymentSummary, DeploymentStatus

logger = logging.getLogger(__name__)


class DeploymentHistoryManager:
    """Manages deployment history storage and retrieval."""
    
    def __init__(self, storage_path: str = "deployment_history.db"):
        """
        Initialize history manager.
        
        Args:
            storage_path: Path to SQLite database file
        """
        self.storage_path = storage_path
        self.db_path = Path(storage_path)
        self._ensure_database()
    
    def _ensure_database(self):
        """Ensure database exists and has correct schema."""
        try:
            with self._get_connection() as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS deployments (
                        deployment_id TEXT PRIMARY KEY,
                        environment TEXT NOT NULL,
                        commit_sha TEXT NOT NULL,
                        image_tag TEXT NOT NULL,
                        revision_name TEXT,
                        status TEXT NOT NULL,
                        start_time TEXT NOT NULL,
                        end_time TEXT,
                        duration_seconds REAL,
                        overall_progress REAL DEFAULT 0.0,
                        error_count INTEGER DEFAULT 0,
                        warning_count INTEGER DEFAULT 0,
                        success BOOLEAN DEFAULT FALSE,
                        rollback_revision TEXT,
                        rollback_reason TEXT,
                        rollback_time TEXT,
                        deployment_config TEXT,
                        environment_config TEXT,
                        metadata TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS deployment_phases (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        deployment_id TEXT NOT NULL,
                        phase TEXT NOT NULL,
                        status TEXT NOT NULL,
                        start_time TEXT,
                        end_time TEXT,
                        duration_seconds REAL,
                        progress_percentage REAL DEFAULT 0.0,
                        current_step TEXT,
                        total_steps INTEGER DEFAULT 0,
                        completed_steps INTEGER DEFAULT 0,
                        error_message TEXT,
                        warnings TEXT,
                        metadata TEXT,
                        FOREIGN KEY (deployment_id) REFERENCES deployments (deployment_id)
                    )
                """)
                
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS deployment_metrics (
                        deployment_id TEXT PRIMARY KEY,
                        total_duration_seconds REAL DEFAULT 0.0,
                        validation_duration_seconds REAL DEFAULT 0.0,
                        build_duration_seconds REAL DEFAULT 0.0,
                        deployment_duration_seconds REAL DEFAULT 0.0,
                        health_check_duration_seconds REAL DEFAULT 0.0,
                        cpu_usage_percent REAL DEFAULT 0.0,
                        memory_usage_mb REAL DEFAULT 0.0,
                        network_io_mb REAL DEFAULT 0.0,
                        success_rate REAL DEFAULT 0.0,
                        error_count INTEGER DEFAULT 0,
                        warning_count INTEGER DEFAULT 0,
                        FOREIGN KEY (deployment_id) REFERENCES deployments (deployment_id)
                    )
                """)
                
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS deployment_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        deployment_id TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        level TEXT NOT NULL,
                        message TEXT NOT NULL,
                        source TEXT,
                        metadata TEXT,
                        FOREIGN KEY (deployment_id) REFERENCES deployments (deployment_id)
                    )
                """)
                
                # Create indexes for better query performance
                conn.execute("CREATE INDEX IF NOT EXISTS idx_deployments_environment ON deployments (environment)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_deployments_status ON deployments (status)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_deployments_start_time ON deployments (start_time)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_deployment_phases_deployment_id ON deployment_phases (deployment_id)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_deployment_logs_deployment_id ON deployment_logs (deployment_id)")
                
                conn.commit()
                logger.info(f"Database initialized at {self.storage_path}")
                
        except Exception as e:
            logger.error(f"Failed to initialize database: {str(e)}")
            raise
    
    @contextmanager
    def _get_connection(self):
        """Get database connection with proper error handling."""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {str(e)}")
            raise
        finally:
            if conn:
                conn.close()
    
    def save_deployment_record(self, record: DeploymentRecord) -> bool:
        """
        Save deployment record to history.
        
        Args:
            record: Deployment record to save
            
        Returns:
            True if saved successfully
        """
        try:
            with self._get_connection() as conn:
                # Save main deployment record
                conn.execute("""
                    INSERT OR REPLACE INTO deployments (
                        deployment_id, environment, commit_sha, image_tag, revision_name,
                        status, start_time, end_time, duration_seconds, overall_progress,
                        error_count, warning_count, success, rollback_revision,
                        rollback_reason, rollback_time, deployment_config,
                        environment_config, metadata
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    record.deployment_id,
                    record.environment,
                    record.commit_sha,
                    record.image_tag,
                    record.revision_name,
                    record.status.value,
                    record.start_time.isoformat(),
                    record.end_time.isoformat() if record.end_time else None,
                    record.get_duration_seconds(),
                    record.overall_progress_percentage,
                    len(record.errors),
                    len(record.warnings),
                    record.is_successful(),
                    record.rollback_revision,
                    record.rollback_reason,
                    record.rollback_time.isoformat() if record.rollback_time else None,
                    json.dumps(record.deployment_config),
                    json.dumps(record.environment_config),
                    json.dumps(record.metadata)
                ))
                
                # Save phase information
                conn.execute("DELETE FROM deployment_phases WHERE deployment_id = ?", (record.deployment_id,))
                for phase, progress in record.phases.items():
                    conn.execute("""
                        INSERT INTO deployment_phases (
                            deployment_id, phase, status, start_time, end_time,
                            duration_seconds, progress_percentage, current_step,
                            total_steps, completed_steps, error_message, warnings, metadata
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        record.deployment_id,
                        phase.value,
                        progress.status.value,
                        progress.start_time.isoformat() if progress.start_time else None,
                        progress.end_time.isoformat() if progress.end_time else None,
                        progress.duration_seconds,
                        progress.progress_percentage,
                        progress.current_step,
                        progress.total_steps,
                        progress.completed_steps,
                        progress.error_message,
                        json.dumps(progress.warnings),
                        json.dumps(progress.metadata)
                    ))
                
                # Save metrics
                conn.execute("""
                    INSERT OR REPLACE INTO deployment_metrics (
                        deployment_id, total_duration_seconds, validation_duration_seconds,
                        build_duration_seconds, deployment_duration_seconds,
                        health_check_duration_seconds, cpu_usage_percent,
                        memory_usage_mb, network_io_mb, success_rate,
                        error_count, warning_count
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    record.deployment_id,
                    record.metrics.total_duration_seconds,
                    record.metrics.validation_duration_seconds,
                    record.metrics.build_duration_seconds,
                    record.metrics.deployment_duration_seconds,
                    record.metrics.health_check_duration_seconds,
                    record.metrics.cpu_usage_percent,
                    record.metrics.memory_usage_mb,
                    record.metrics.network_io_mb,
                    record.metrics.success_rate,
                    record.metrics.error_count,
                    record.metrics.warning_count
                ))
                
                conn.commit()
                logger.info(f"Saved deployment record: {record.deployment_id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to save deployment record {record.deployment_id}: {str(e)}")
            return False
    
    def get_deployment_record(self, deployment_id: str) -> Optional[DeploymentRecord]:
        """
        Get deployment record by ID.
        
        Args:
            deployment_id: Deployment ID to retrieve
            
        Returns:
            Deployment record if found
        """
        try:
            with self._get_connection() as conn:
                # Get main deployment record
                row = conn.execute("""
                    SELECT * FROM deployments WHERE deployment_id = ?
                """, (deployment_id,)).fetchone()
                
                if not row:
                    return None
                
                # Convert row to deployment record
                record = self._row_to_deployment_record(row)
                
                # Get phase information
                phase_rows = conn.execute("""
                    SELECT * FROM deployment_phases WHERE deployment_id = ?
                """, (deployment_id,)).fetchall()
                
                for phase_row in phase_rows:
                    phase_progress = self._row_to_phase_progress(phase_row)
                    record.phases[phase_progress.phase] = phase_progress
                
                # Get metrics
                metrics_row = conn.execute("""
                    SELECT * FROM deployment_metrics WHERE deployment_id = ?
                """, (deployment_id,)).fetchone()
                
                if metrics_row:
                    record.metrics = self._row_to_metrics(metrics_row)
                
                return record
                
        except Exception as e:
            logger.error(f"Failed to get deployment record {deployment_id}: {str(e)}")
            return None
    
    def get_deployment_history(
        self,
        environment: Optional[str] = None,
        status: Optional[DeploymentStatus] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[DeploymentSummary]:
        """
        Get deployment history with filtering.
        
        Args:
            environment: Filter by environment
            status: Filter by status
            start_date: Filter by start date (inclusive)
            end_date: Filter by end date (inclusive)
            limit: Maximum number of records to return
            offset: Number of records to skip
            
        Returns:
            List of deployment summaries
        """
        try:
            with self._get_connection() as conn:
                query = "SELECT * FROM deployments WHERE 1=1"
                params = []
                
                if environment:
                    query += " AND environment = ?"
                    params.append(environment)
                
                if status:
                    query += " AND status = ?"
                    params.append(status.value)
                
                if start_date:
                    query += " AND start_time >= ?"
                    params.append(start_date.isoformat())
                
                if end_date:
                    query += " AND start_time <= ?"
                    params.append(end_date.isoformat())
                
                query += " ORDER BY start_time DESC LIMIT ? OFFSET ?"
                params.extend([limit, offset])
                
                rows = conn.execute(query, params).fetchall()
                
                summaries = []
                for row in rows:
                    summary = DeploymentSummary(
                        deployment_id=row['deployment_id'],
                        environment=row['environment'],
                        status=DeploymentStatus(row['status']),
                        start_time=datetime.fromisoformat(row['start_time']),
                        end_time=datetime.fromisoformat(row['end_time']) if row['end_time'] else None,
                        duration_seconds=row['duration_seconds'],
                        commit_sha=row['commit_sha'],
                        image_tag=row['image_tag'],
                        success=bool(row['success']),
                        error_count=row['error_count'],
                        warning_count=row['warning_count']
                    )
                    summaries.append(summary)
                
                return summaries
                
        except Exception as e:
            logger.error(f"Failed to get deployment history: {str(e)}")
            return []
    
    def get_deployment_statistics(
        self,
        environment: Optional[str] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get deployment statistics for the specified period.
        
        Args:
            environment: Filter by environment
            days: Number of days to include in statistics
            
        Returns:
            Dictionary with deployment statistics
        """
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            with self._get_connection() as conn:
                query = """
                    SELECT 
                        COUNT(*) as total_deployments,
                        SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful_deployments,
                        AVG(duration_seconds) as avg_duration_seconds,
                        MIN(duration_seconds) as min_duration_seconds,
                        MAX(duration_seconds) as max_duration_seconds,
                        SUM(error_count) as total_errors,
                        SUM(warning_count) as total_warnings
                    FROM deployments 
                    WHERE start_time >= ?
                """
                params = [start_date.isoformat()]
                
                if environment:
                    query += " AND environment = ?"
                    params.append(environment)
                
                row = conn.execute(query, params).fetchone()
                
                # Get deployment counts by status
                status_query = """
                    SELECT status, COUNT(*) as count
                    FROM deployments 
                    WHERE start_time >= ?
                """
                status_params = [start_date.isoformat()]
                
                if environment:
                    status_query += " AND environment = ?"
                    status_params.append(environment)
                
                status_query += " GROUP BY status"
                status_rows = conn.execute(status_query, status_params).fetchall()
                
                # Get deployment counts by environment
                env_query = """
                    SELECT environment, COUNT(*) as count
                    FROM deployments 
                    WHERE start_time >= ?
                    GROUP BY environment
                """
                env_rows = conn.execute(env_query, [start_date.isoformat()]).fetchall()
                
                statistics = {
                    'period_days': days,
                    'start_date': start_date.isoformat(),
                    'end_date': datetime.utcnow().isoformat(),
                    'total_deployments': row['total_deployments'] or 0,
                    'successful_deployments': row['successful_deployments'] or 0,
                    'failed_deployments': (row['total_deployments'] or 0) - (row['successful_deployments'] or 0),
                    'success_rate': (row['successful_deployments'] or 0) / max(row['total_deployments'] or 1, 1) * 100,
                    'avg_duration_seconds': row['avg_duration_seconds'] or 0,
                    'min_duration_seconds': row['min_duration_seconds'] or 0,
                    'max_duration_seconds': row['max_duration_seconds'] or 0,
                    'total_errors': row['total_errors'] or 0,
                    'total_warnings': row['total_warnings'] or 0,
                    'deployments_by_status': {row['status']: row['count'] for row in status_rows},
                    'deployments_by_environment': {row['environment']: row['count'] for row in env_rows}
                }
                
                return statistics
                
        except Exception as e:
            logger.error(f"Failed to get deployment statistics: {str(e)}")
            return {}
    
    def cleanup_old_records(self, days_to_keep: int = 90) -> int:
        """
        Clean up old deployment records.
        
        Args:
            days_to_keep: Number of days of records to keep
            
        Returns:
            Number of records deleted
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
            
            with self._get_connection() as conn:
                # Get deployment IDs to delete
                deployment_ids = conn.execute("""
                    SELECT deployment_id FROM deployments 
                    WHERE start_time < ?
                """, (cutoff_date.isoformat(),)).fetchall()
                
                if not deployment_ids:
                    return 0
                
                ids_to_delete = [row['deployment_id'] for row in deployment_ids]
                
                # Delete related records
                for deployment_id in ids_to_delete:
                    conn.execute("DELETE FROM deployment_phases WHERE deployment_id = ?", (deployment_id,))
                    conn.execute("DELETE FROM deployment_metrics WHERE deployment_id = ?", (deployment_id,))
                    conn.execute("DELETE FROM deployment_logs WHERE deployment_id = ?", (deployment_id,))
                
                # Delete main records
                deleted_count = conn.execute("""
                    DELETE FROM deployments WHERE start_time < ?
                """, (cutoff_date.isoformat(),)).rowcount
                
                conn.commit()
                logger.info(f"Cleaned up {deleted_count} old deployment records")
                return deleted_count
                
        except Exception as e:
            logger.error(f"Failed to cleanup old records: {str(e)}")
            return 0
    
    def _row_to_deployment_record(self, row) -> DeploymentRecord:
        """Convert database row to DeploymentRecord."""
        from .models import DeploymentRecord, DeploymentStatus, DeploymentMetrics
        
        record = DeploymentRecord(
            deployment_id=row['deployment_id'],
            environment=row['environment'],
            commit_sha=row['commit_sha'],
            image_tag=row['image_tag'],
            revision_name=row['revision_name'] or "",
            status=DeploymentStatus(row['status']),
            start_time=datetime.fromisoformat(row['start_time']),
            end_time=datetime.fromisoformat(row['end_time']) if row['end_time'] else None,
            overall_progress_percentage=row['overall_progress'],
            rollback_revision=row['rollback_revision'],
            rollback_reason=row['rollback_reason'],
            rollback_time=datetime.fromisoformat(row['rollback_time']) if row['rollback_time'] else None,
            deployment_config=json.loads(row['deployment_config']) if row['deployment_config'] else {},
            environment_config=json.loads(row['environment_config']) if row['environment_config'] else {},
            metadata=json.loads(row['metadata']) if row['metadata'] else {}
        )
        
        return record
    
    def _row_to_phase_progress(self, row):
        """Convert database row to PhaseProgress."""
        from .models import DeploymentPhase, ProgressStatus, PhaseProgress
        
        return PhaseProgress(
            phase=DeploymentPhase(row['phase']),
            status=ProgressStatus(row['status']),
            start_time=datetime.fromisoformat(row['start_time']) if row['start_time'] else None,
            end_time=datetime.fromisoformat(row['end_time']) if row['end_time'] else None,
            duration_seconds=row['duration_seconds'],
            progress_percentage=row['progress_percentage'],
            current_step=row['current_step'] or "",
            total_steps=row['total_steps'],
            completed_steps=row['completed_steps'],
            error_message=row['error_message'],
            warnings=json.loads(row['warnings']) if row['warnings'] else [],
            metadata=json.loads(row['metadata']) if row['metadata'] else {}
        )
    
    def _row_to_metrics(self, row):
        """Convert database row to DeploymentMetrics."""
        from .models import DeploymentMetrics
        
        return DeploymentMetrics(
            total_duration_seconds=row['total_duration_seconds'],
            validation_duration_seconds=row['validation_duration_seconds'],
            build_duration_seconds=row['build_duration_seconds'],
            deployment_duration_seconds=row['deployment_duration_seconds'],
            health_check_duration_seconds=row['health_check_duration_seconds'],
            cpu_usage_percent=row['cpu_usage_percent'],
            memory_usage_mb=row['memory_usage_mb'],
            network_io_mb=row['network_io_mb'],
            success_rate=row['success_rate'],
            error_count=row['error_count'],
            warning_count=row['warning_count']
        )