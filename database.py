"""
database.py - SQLite database operations for Grinding Polisher

Handles saving, loading, and managing experimental data and results.
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple
from pathlib import Path


class Database:
    """SQLite database handler for the grinding polisher application"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            # Use data directory in the same location as this file
            base_dir = Path(__file__).parent
            data_dir = base_dir / 'data'
            data_dir.mkdir(exist_ok=True)
            db_path = data_dir / 'grinding_polisher.db'
        
        self.db_path = str(db_path)
        self._init_database()
    
    def _get_connection(self):
        """Create and return a database connection"""
        return sqlite3.connect(self.db_path)
    
    def _init_database(self):
        """Initialize the database with required tables"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Experiments table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS experiments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    material_type TEXT,
                    specimen_id TEXT,
                    date TEXT NOT NULL,
                    duration_minutes REAL,
                    operator TEXT,
                    notes TEXT,
                    created_at TEXT NOT NULL
                )
            ''')
            
            # Speed trials table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS speed_trials (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    experiment_id INTEGER,
                    trial_number INTEGER,
                    motor_speed_rpm REAL,
                    output_speed_rpm REAL,
                    pulley_ratio REAL,
                    timestamp TEXT,
                    FOREIGN KEY (experiment_id) REFERENCES experiments (id)
                )
            ''')
            
            # Abrasive sequences table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS abrasive_sequences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    experiment_id INTEGER,
                    step_number INTEGER,
                    step_type TEXT,  -- 'grinding' or 'polishing'
                    abrasive_type TEXT,
                    grit_size TEXT,
                    duration_seconds INTEGER,
                    pressure_mpa REAL,
                    notes TEXT,
                    FOREIGN KEY (experiment_id) REFERENCES experiments (id)
                )
            ''')
            
            # Results table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    experiment_id INTEGER,
                    surface_quality TEXT,
                    magnification TEXT,
                    grain_structure TEXT,
                    vibration_level TEXT,
                    chatter_marks BOOLEAN,
                    uniform_polishing BOOLEAN,
                    overall_assessment TEXT,
                    timestamp TEXT,
                    FOREIGN KEY (experiment_id) REFERENCES experiments (id)
                )
            ''')
            
            # Settings table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated_at TEXT
                )
            ''')
            
            conn.commit()
    
    # ===================== EXPERIMENT OPERATIONS =====================
    
    def create_experiment(self, name: str, material_type: str = None,
                         specimen_id: str = None, operator: str = None,
                         notes: str = None) -> int:
        """Create a new experiment and return its ID"""
        now = datetime.now().isoformat()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO experiments (name, material_type, specimen_id, date, operator, notes, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (name, material_type, specimen_id, now, operator, notes, now))
            conn.commit()
            return cursor.lastrowid
    
    def get_experiment(self, experiment_id: int) -> Optional[Dict[str, Any]]:
        """Get an experiment by ID"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM experiments WHERE id = ?', (experiment_id,))
            row = cursor.fetchone()
            if row:
                columns = [description[0] for description in cursor.description]
                return dict(zip(columns, row))
            return None
    
    def get_all_experiments(self) -> List[Dict[str, Any]]:
        """Get all experiments"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM experiments ORDER BY created_at DESC')
            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
    
    def update_experiment(self, experiment_id: int, **kwargs):
        """Update an experiment's fields"""
        allowed_fields = ['name', 'material_type', 'specimen_id', 'duration_minutes', 
                         'operator', 'notes']
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not updates:
            return
            
        set_clause = ', '.join([f"{k} = ?" for k in updates.keys()])
        values = list(updates.values()) + [experiment_id]
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f'UPDATE experiments SET {set_clause} WHERE id = ?', values)
            conn.commit()
    
    def delete_experiment(self, experiment_id: int):
        """Delete an experiment and all related data"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Delete related data first
            cursor.execute('DELETE FROM speed_trials WHERE experiment_id = ?', (experiment_id,))
            cursor.execute('DELETE FROM abrasive_sequences WHERE experiment_id = ?', (experiment_id,))
            cursor.execute('DELETE FROM results WHERE experiment_id = ?', (experiment_id,))
            cursor.execute('DELETE FROM experiments WHERE id = ?', (experiment_id,))
            conn.commit()
    
    # ===================== SPEED TRIALS =====================
    
    def add_speed_trial(self, experiment_id: int, trial_number: int,
                       motor_speed_rpm: float, output_speed_rpm: float,
                       pulley_ratio: float) -> int:
        """Add a speed trial record"""
        now = datetime.now().isoformat()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO speed_trials 
                (experiment_id, trial_number, motor_speed_rpm, output_speed_rpm, 
                 pulley_ratio, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (experiment_id, trial_number, motor_speed_rpm, output_speed_rpm,
                  pulley_ratio, now))
            conn.commit()
            return cursor.lastrowid
    
    def get_speed_trials(self, experiment_id: int) -> List[Dict[str, Any]]:
        """Get all speed trials for an experiment"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM speed_trials 
                WHERE experiment_id = ? 
                ORDER BY trial_number
            ''', (experiment_id,))
            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
    
    # ===================== ABRASIVE SEQUENCES =====================
    
    def add_abrasive_step(self, experiment_id: int, step_number: int,
                         step_type: str, abrasive_type: str, grit_size: str,
                         duration_seconds: int, pressure_mpa: float = None,
                         notes: str = None) -> int:
        """Add an abrasive sequence step"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO abrasive_sequences 
                (experiment_id, step_number, step_type, abrasive_type, grit_size,
                 duration_seconds, pressure_mpa, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (experiment_id, step_number, step_type, abrasive_type, grit_size,
                  duration_seconds, pressure_mpa, notes))
            conn.commit()
            return cursor.lastrowid
    
    def get_abrasive_sequence(self, experiment_id: int) -> List[Dict[str, Any]]:
        """Get the abrasive sequence for an experiment"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM abrasive_sequences 
                WHERE experiment_id = ? 
                ORDER BY step_number
            ''', (experiment_id,))
            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
    
    # ===================== RESULTS =====================
    
    def save_results(self, experiment_id: int, surface_quality: str,
                    magnification: str, grain_structure: str,
                    vibration_level: str, chatter_marks: bool,
                    uniform_polishing: bool, overall_assessment: str) -> int:
        """Save results for an experiment"""
        now = datetime.now().isoformat()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO results 
                (experiment_id, surface_quality, magnification, grain_structure,
                 vibration_level, chatter_marks, uniform_polishing,
                 overall_assessment, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (experiment_id, surface_quality, magnification, grain_structure,
                  vibration_level, 1 if chatter_marks else 0,
                  1 if uniform_polishing else 0, overall_assessment, now))
            conn.commit()
            return cursor.lastrowid
    
    def get_results(self, experiment_id: int) -> Optional[Dict[str, Any]]:
        """Get results for an experiment"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM results WHERE experiment_id = ?', (experiment_id,))
            row = cursor.fetchone()
            if row:
                columns = [description[0] for description in cursor.description]
                result = dict(zip(columns, row))
                # Convert boolean flags
                result['chatter_marks'] = bool(result['chatter_marks'])
                result['uniform_polishing'] = bool(result['uniform_polishing'])
                return result
            return None
    
    # ===================== SETTINGS =====================
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a setting value"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
            row = cursor.fetchone()
            if row:
                try:
                    return json.loads(row[0])
                except:
                    return row[0]
            return default
    
    def set_setting(self, key: str, value: Any):
        """Set a setting value"""
        now = datetime.now().isoformat()
        value_str = json.dumps(value) if not isinstance(value, str) else value
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO settings (key, value, updated_at)
                VALUES (?, ?, ?)
            ''', (key, value_str, now))
            conn.commit()
    
    # ===================== EXPORT / IMPORT =====================
    
    def export_experiment_data(self, experiment_id: int) -> Dict[str, Any]:
        """Export all data for an experiment as a dictionary"""
        exp = self.get_experiment(experiment_id)
        if not exp:
            return {}
        
        return {
            'experiment': exp,
            'speed_trials': self.get_speed_trials(experiment_id),
            'abrasive_sequence': self.get_abrasive_sequence(experiment_id),
            'results': self.get_results(experiment_id)
        }
    
    def get_summary_statistics(self) -> Dict[str, Any]:
        """Get summary statistics from all experiments"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Count experiments
            cursor.execute('SELECT COUNT(*) FROM experiments')
            total_experiments = cursor.fetchone()[0]
            
            # Count by material type
            cursor.execute('''
                SELECT material_type, COUNT(*) 
                FROM experiments 
                WHERE material_type IS NOT NULL 
                GROUP BY material_type
            ''')
            material_counts = dict(cursor.fetchall())
            
            # Average speed
            cursor.execute('SELECT AVG(motor_speed_rpm) FROM speed_trials')
            avg_motor_speed = cursor.fetchone()[0] or 0
            
            cursor.execute('SELECT AVG(output_speed_rpm) FROM speed_trials')
            avg_output_speed = cursor.fetchone()[0] or 0
            
            # Success rate (based on uniform polishing)
            cursor.execute('''
                SELECT COUNT(*) FROM results WHERE uniform_polishing = 1
            ''')
            successful = cursor.fetchone()[0] or 0
            
            cursor.execute('SELECT COUNT(*) FROM results')
            total_results = cursor.fetchone()[0] or 1
            
            return {
                'total_experiments': total_experiments,
                'material_counts': material_counts,
                'avg_motor_speed_rpm': avg_motor_speed,
                'avg_output_speed_rpm': avg_output_speed,
                'successful_preparations': successful,
                'success_rate': (successful / total_results) * 100
            }