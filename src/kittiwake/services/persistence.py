"""Persistence service using DuckDB for saved analyses and workflows."""

import json
from pathlib import Path
from threading import Lock
from typing import Any

try:
    import duckdb
except ImportError:
    duckdb = None


class DatabaseCorruptionError(Exception):
    """Exception raised when the DuckDB database is corrupted or inaccessible."""

    pass


class SavedAnalysisRepository:
    """Repository for saved analyses using DuckDB."""

    _write_lock = Lock()

    def __init__(self):
        if duckdb is None:
            raise ImportError("duckdb is required for persistence")

        self.db_path = Path.home() / ".kittiwake" / "analyses.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize database with error handling
        try:
            self._init_database()
        except Exception as e:
            raise DatabaseCorruptionError(f"Failed to initialize database: {e}") from e

    def _init_database(self):
        """Initialize database schema."""
        conn = self._get_connection()

        # Check if table exists and needs migration
        result = conn.execute("""
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_name = 'saved_analyses'
        """).fetchone()

        table_exists = result[0] > 0 if result else False

        if table_exists:
            # Check if id column has auto-increment (check column_default)
            try:
                col_info = conn.execute("""
                    SELECT column_default
                    FROM information_schema.columns
                    WHERE table_name = 'saved_analyses' AND column_name = 'id'
                """).fetchone()

                # If column_default is None, we need to migrate
                if col_info and col_info[0] is None:
                    # Backup existing data
                    backup = conn.execute("SELECT * FROM saved_analyses").fetchall()

                    # Drop and recreate table
                    conn.execute("DROP TABLE saved_analyses")
                    table_exists = False

                    # We'll restore data after creating new table
                    needs_restore = True
                    restore_data = backup
                else:
                    needs_restore = False
                    restore_data = []
            except Exception:
                # If we can't check, assume it's fine
                needs_restore = False
                restore_data = []
        else:
            needs_restore = False
            restore_data = []

        # Create saved_analyses table with auto-increment (DuckDB 0.10+)
        if not table_exists:
            conn.execute("""
                CREATE TABLE saved_analyses (
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

            # Create sequence for auto-increment
            conn.execute("CREATE SEQUENCE saved_analyses_seq START 1")

            # Restore backed up data if any
            if needs_restore and restore_data:
                for row in restore_data:
                    conn.execute(
                        """
                        INSERT INTO saved_analyses
                        (name, description, created_at, modified_at, operation_count, dataset_path, operations)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                        list(row[1:]),
                    )  # Skip the old id

        # Create indices
        conn.execute("CREATE INDEX IF NOT EXISTS idx_name ON saved_analyses(name)")
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_created_at ON saved_analyses(created_at DESC)"
        )

        conn.close()

    def _get_connection(self):
        """Get database connection."""
        conn = duckdb.connect(str(self.db_path))
        return conn

    def save(self, analysis_data: dict[str, Any]) -> tuple[int | None, str | None]:
        """Save analysis to database.

        Handles duplicate names by auto-versioning with timestamp suffix.

        Args:
            analysis_data: Analysis data with name, description, operations, etc.

        Returns:
            Tuple of (analysis_id, versioned_name_if_changed)
            - analysis_id: The ID of the saved analysis
            - versioned_name_if_changed: The auto-versioned name if original was duplicate, None otherwise
        """
        with self._write_lock:
            conn = self._get_connection()

            original_name = analysis_data["name"]
            versioned_name = None

            try:
                result = conn.execute(
                    """
                    INSERT INTO saved_analyses (id, name, description, operation_count, dataset_path, operations)
                    VALUES (nextval('saved_analyses_seq'), ?, ?, ?, ?, ?)
                    RETURNING id
                """,
                    [
                        original_name,
                        analysis_data.get("description"),
                        analysis_data["operation_count"],
                        analysis_data["dataset_path"],
                        json.dumps(analysis_data["operations"]),
                    ],
                ).fetchone()

                conn.close()
                return (result[0] if result else None, None)

            except Exception as e:
                # Check if it's a UNIQUE constraint violation
                error_msg = str(e).lower()
                if "unique" in error_msg or "constraint" in error_msg:
                    # Auto-version with timestamp suffix and counter if needed
                    from datetime import datetime

                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    versioned_name = f"{original_name}_{timestamp}"
                    counter = 1

                    # Retry with versioned name (keep adding counter if still duplicate)
                    while True:
                        try:
                            result = conn.execute(
                                """
                                INSERT INTO saved_analyses (id, name, description, operation_count, dataset_path, operations)
                                VALUES (nextval('saved_analyses_seq'), ?, ?, ?, ?, ?)
                                RETURNING id
                                """,
                                [
                                    versioned_name,
                                    analysis_data.get("description"),
                                    analysis_data["operation_count"],
                                    analysis_data["dataset_path"],
                                    json.dumps(analysis_data["operations"]),
                                ],
                            ).fetchone()

                            conn.close()
                            return (result[0] if result else None, versioned_name)
                        except Exception as retry_error:
                            # Check if still a UNIQUE constraint violation
                            retry_msg = str(retry_error).lower()
                            if "unique" in retry_msg or "constraint" in retry_msg:
                                # Try with counter
                                counter += 1
                                versioned_name = (
                                    f"{original_name}_{timestamp}_{counter}"
                                )
                                continue
                            else:
                                conn.close()
                                raise retry_error
                else:
                    conn.close()
                    raise

    def list_all(self) -> list[dict[str, Any]]:
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

    def load_by_id(self, analysis_id: int) -> dict[str, Any] | None:
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

    def update(self, analysis_id: int, analysis_data: dict[str, Any]) -> bool:
        """Update analysis."""
        with self._write_lock:
            conn = self._get_connection()

            result = conn.execute(
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

            updated = result.fetchone()[0] > 0
            conn.close()
            return updated

    def delete(self, analysis_id: int) -> bool:
        """Delete analysis."""
        with self._write_lock:
            conn = self._get_connection()

            result = conn.execute(
                "DELETE FROM saved_analyses WHERE id = ?", [analysis_id]
            )

            deleted = result.fetchone()[0] > 0
            conn.close()
            return deleted

    def reinitialize_database(self) -> bool:
        """Reinitialize the database by deleting and recreating it.

        This is used to recover from database corruption.
        WARNING: This will delete all saved analyses.

        Returns:
            True if reinitialized successfully, False otherwise

        """
        try:
            # Close any existing connections
            conn = self._get_connection()
            conn.close()

            # Delete the database file
            if self.db_path.exists():
                self.db_path.unlink()

            # Recreate database
            self._init_database()
            return True

        except Exception as e:
            raise DatabaseCorruptionError(
                f"Failed to reinitialize database: {e}"
            ) from e

    def check_database_health(self) -> tuple[bool, str]:
        """Check if the database is accessible and not corrupted.

        Returns:
            Tuple of (is_healthy, error_message)

        """
        try:
            conn = self._get_connection()

            # Try to execute a simple query
            conn.execute("SELECT COUNT(*) FROM saved_analyses").fetchone()

            conn.close()
            return (True, "")

        except Exception as e:
            return (False, str(e))


class WorkflowRepository:
    """Repository for saved workflows using DuckDB."""

    _write_lock = Lock()

    def __init__(self):
        """Initialize workflow repository."""
        if duckdb is None:
            raise ImportError("duckdb is required for persistence")

        self.db_path = Path.home() / ".kittiwake" / "analyses.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize database
        self._init_database()

    def _init_database(self):
        """Initialize database schema for workflows table."""
        conn = self._get_connection()

        # Check if workflows table exists
        result = conn.execute("""
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_name = 'workflows'
        """).fetchone()

        table_exists = result[0] > 0 if result else False

        # Create workflows table
        if not table_exists:
            conn.execute("""
                CREATE TABLE workflows (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    modified_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    operation_count INTEGER NOT NULL CHECK (operation_count >= 0),
                    operations JSON NOT NULL,
                    required_schema JSON
                )
            """)

            # Create sequence for auto-increment
            conn.execute("CREATE SEQUENCE workflows_seq START 1")

        # Create indices
        conn.execute("CREATE INDEX IF NOT EXISTS idx_workflow_name ON workflows(name)")
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_workflow_created_at ON workflows(created_at DESC)"
        )

        conn.close()

    def _get_connection(self):
        """Get database connection."""
        conn = duckdb.connect(str(self.db_path))
        return conn

    def save(self, workflow_data: dict[str, Any]) -> tuple[int | None, str | None]:
        """Save workflow to database.

        Handles duplicate names by auto-versioning with timestamp suffix.

        Args:
            workflow_data: Workflow data with name, description, operations, required_schema

        Returns:
            Tuple of (workflow_id, versioned_name_if_changed)
            - workflow_id: The ID of the saved workflow
            - versioned_name_if_changed: The auto-versioned name if original was duplicate, None otherwise

        """
        with self._write_lock:
            conn = self._get_connection()

            original_name = workflow_data["name"]
            versioned_name = None

            try:
                result = conn.execute(
                    """
                    INSERT INTO workflows (id, name, description, operation_count, operations, required_schema)
                    VALUES (nextval('workflows_seq'), ?, ?, ?, ?, ?)
                    RETURNING id
                    """,
                    [
                        original_name,
                        workflow_data.get("description"),
                        workflow_data["operation_count"],
                        json.dumps(workflow_data["operations"]),
                        json.dumps(workflow_data.get("required_schema"))
                        if workflow_data.get("required_schema")
                        else None,
                    ],
                ).fetchone()

                conn.close()
                return (result[0] if result else None, None)

            except Exception as e:
                # Check if it's a UNIQUE constraint violation
                error_msg = str(e).lower()
                if "unique" in error_msg or "constraint" in error_msg:
                    # Auto-version with timestamp suffix and counter if needed
                    from datetime import datetime

                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    versioned_name = f"{original_name}_{timestamp}"
                    counter = 1

                    # Retry with versioned name (keep adding counter if still duplicate)
                    while True:
                        try:
                            result = conn.execute(
                                """
                                INSERT INTO workflows (id, name, description, operation_count, operations, required_schema)
                                VALUES (nextval('workflows_seq'), ?, ?, ?, ?, ?)
                                RETURNING id
                                """,
                                [
                                    versioned_name,
                                    workflow_data.get("description"),
                                    workflow_data["operation_count"],
                                    json.dumps(workflow_data["operations"]),
                                    json.dumps(workflow_data.get("required_schema"))
                                    if workflow_data.get("required_schema")
                                    else None,
                                ],
                            ).fetchone()

                            conn.close()
                            return (result[0] if result else None, versioned_name)
                        except Exception as retry_error:
                            # Check if still a UNIQUE constraint violation
                            retry_msg = str(retry_error).lower()
                            if "unique" in retry_msg or "constraint" in retry_msg:
                                # Try with counter
                                counter += 1
                                versioned_name = (
                                    f"{original_name}_{timestamp}_{counter}"
                                )
                                continue
                            else:
                                conn.close()
                                raise retry_error
                else:
                    conn.close()
                    raise

    def list_all(self) -> list[dict[str, Any]]:
        """List all saved workflows."""
        conn = self._get_connection()

        result = conn.execute("""
            SELECT id, name, description, created_at, modified_at, operation_count
            FROM workflows
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
            }
            for row in result
        ]

    def load_by_id(self, workflow_id: int) -> dict[str, Any] | None:
        """Load workflow by ID.

        Args:
            workflow_id: ID of the workflow to load

        Returns:
            Workflow data dict or None if not found

        """
        conn = self._get_connection()

        result = conn.execute(
            """
            SELECT id, name, description, created_at, modified_at, operation_count, operations, required_schema
            FROM workflows
            WHERE id = ?
        """,
            [workflow_id],
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
            "operations": json.loads(result[6]),
            "required_schema": json.loads(result[7]) if result[7] else None,
        }

    def update(self, workflow_id: int, workflow_data: dict[str, Any]) -> bool:
        """Update workflow.

        Args:
            workflow_id: ID of workflow to update
            workflow_data: Updated workflow data

        Returns:
            True if updated successfully, False otherwise

        """
        with self._write_lock:
            conn = self._get_connection()

            result = conn.execute(
                """
                UPDATE workflows
                SET name = ?, description = ?, modified_at = CURRENT_TIMESTAMP,
                    operation_count = ?, operations = ?, required_schema = ?
                WHERE id = ?
            """,
                [
                    workflow_data["name"],
                    workflow_data.get("description"),
                    workflow_data["operation_count"],
                    json.dumps(workflow_data["operations"]),
                    json.dumps(workflow_data.get("required_schema"))
                    if workflow_data.get("required_schema")
                    else None,
                    workflow_id,
                ],
            )

            updated = result.fetchone()[0] > 0
            conn.close()
            return updated

    def delete(self, workflow_id: int) -> bool:
        """Delete workflow.

        Args:
            workflow_id: ID of workflow to delete

        Returns:
            True if deleted successfully, False otherwise

        """
        with self._write_lock:
            conn = self._get_connection()

            result = conn.execute("DELETE FROM workflows WHERE id = ?", [workflow_id])

            deleted = result.fetchone()[0] > 0
            conn.close()
            return deleted
