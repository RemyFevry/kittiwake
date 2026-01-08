"""Persistence service using DuckDB for saved analyses."""

import json
from pathlib import Path
from threading import Lock
from typing import List, Optional, Dict, Any

try:
    import duckdb
except ImportError:
    duckdb = None


class SavedAnalysisRepository:
    """Repository for saved analyses using DuckDB."""

    _write_lock = Lock()

    def __init__(self):
        if duckdb is None:
            raise ImportError("duckdb is required for persistence")

        self.db_path = Path.home() / ".kittiwake" / "analyses.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize database
        self._init_database()

    def _init_database(self):
        """Initialize database schema."""
        conn = self._get_connection()

        # Create saved_analyses table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS saved_analyses (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                modified_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                operation_count INTEGER NOT NULL CHECK (operation_count >= 0),
                dataset_path TEXT NOT NULL,
                operations JSON NOT NULL
            )
        """)

        # Create indices
        conn.execute("CREATE INDEX IF NOT EXISTS idx_name ON saved_analyses(name)")
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_created_at ON saved_analyses(created_at DESC)"
        )

        conn.close()

    def _get_connection(self):
        """Get database connection with WAL mode."""
        conn = duckdb.connect(str(self.db_path))
        conn.execute("PRAGMA journal_mode=WAL")
        return conn

    def save(self, analysis_data: Dict[str, Any]) -> int:
        """Save analysis to database."""
        with self._write_lock:
            conn = self._get_connection()

            result = conn.execute(
                """
                INSERT INTO saved_analyses (name, description, operation_count, dataset_path, operations)
                VALUES (?, ?, ?, ?, ?)
                RETURNING id
            """,
                [
                    analysis_data["name"],
                    analysis_data.get("description"),
                    analysis_data["operation_count"],
                    analysis_data["dataset_path"],
                    json.dumps(analysis_data["operations"]),
                ],
            ).fetchone()

            conn.close()
            return result[0] if result else None

    def list_all(self) -> List[Dict[str, Any]]:
        """List all saved analyses."""
        conn = self._get_connection()

        result = conn.execute("""
            SELECT id, name, description, created_at, modified_at, operation_count, dataset_path
            FROM saved_analyses
            ORDER BY modified_at DESC
        """).fetchall()

        conn.close()

        return [
            {
                "id": row[0],
                "name": row[1],
                "description": row[2],
                "created_at": row[3],
                "modified_at": row[4],
                "operation_count": row[5],
                "dataset_path": row[6],
            }
            for row in result
        ]

    def load_by_id(self, analysis_id: int) -> Optional[Dict[str, Any]]:
        """Load analysis by ID."""
        conn = self._get_connection()

        result = conn.execute(
            """
            SELECT id, name, description, created_at, modified_at, operation_count, dataset_path, operations
            FROM saved_analyses
            WHERE id = ?
        """,
            [analysis_id],
        ).fetchone()

        conn.close()

        if result is None:
            return None

        return {
            "id": result[0],
            "name": result[1],
            "description": result[2],
            "created_at": result[3],
            "modified_at": result[4],
            "operation_count": result[5],
            "dataset_path": result[6],
            "operations": json.loads(result[7]),
        }

    def update(self, analysis_id: int, analysis_data: Dict[str, Any]) -> bool:
        """Update analysis."""
        with self._write_lock:
            conn = self._get_connection()

            conn.execute(
                """
                UPDATE saved_analyses
                SET name = ?, description = ?, modified_at = CURRENT_TIMESTAMP, operation_count = ?, operations = ?
                WHERE id = ?
            """,
                [
                    analysis_data["name"],
                    analysis_data.get("description"),
                    analysis_data["operation_count"],
                    json.dumps(analysis_data["operations"]),
                    analysis_id,
                ],
            )

            updated = conn.total_changes > 0
            conn.close()
            return updated

    def delete(self, analysis_id: int) -> bool:
        """Delete analysis."""
        with self._write_lock:
            conn = self._get_connection()

            conn.execute("DELETE FROM saved_analyses WHERE id = ?", [analysis_id])

            deleted = conn.total_changes > 0
            conn.close()
            return deleted
