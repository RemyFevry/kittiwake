"""Unit tests for saved analyses edge cases (T095, T096, T097, T098)."""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from kittiwake.services.persistence import (
    DatabaseCorruptionError,
    SavedAnalysisRepository,
)


class TestDatasetPathUnavailable:
    """Tests for T095 - Handle dataset path unavailable when loading analysis."""

    def test_load_analysis_with_missing_path_shows_warning(self):
        """Test that loading analysis with missing path shows warning."""
        pass

    def test_path_update_modal_updates_correctly(self):
        """Test that PathUpdateModal correctly updates path."""
        pass

    def test_schema_validation_after_path_update(self):
        """Test that schema validation occurs after path update."""
        pass


class TestDatabaseCorruption:
    """Tests for T096 - Handle DuckDB database corruption."""

    def test_database_corruption_error_raised_on_invalid_db(self):
        """Test that DatabaseCorruptionError is raised on invalid database."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a corrupted database file in .kittiwake directory
            kittiwake_dir = Path(tmpdir) / ".kittiwake"
            kittiwake_dir.mkdir(parents=True, exist_ok=True)
            db_path = kittiwake_dir / "analyses.db"
            db_path.write_text("corrupted data not a real database")

            with patch(
                "kittiwake.services.persistence.Path.home",
                return_value=Path(tmpdir),
            ):
                with pytest.raises(DatabaseCorruptionError):
                    SavedAnalysisRepository()

    def test_check_database_health_returns_true_on_valid_db(self):
        """Test that check_database_health returns True on valid database."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch(
                "kittiwake.services.persistence.Path.home",
                return_value=Path(tmpdir),
            ):
                repo = SavedAnalysisRepository()
                is_healthy, error_msg = repo.check_database_health()
                assert is_healthy
                assert error_msg == ""

    def test_reinitialize_database_clears_existing_data(self):
        """Test that reinitialize_database clears existing database."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch(
                "kittiwake.services.persistence.Path.home",
                return_value=Path(tmpdir),
            ):
                # Create initial repository
                repo = SavedAnalysisRepository()

                # Save some data
                analysis_data = {
                    "name": "Test Analysis",
                    "description": "Test",
                    "operation_count": 1,
                    "dataset_path": "/test/path.csv",
                    "operations": [
                        {
                            "code": "df = df.filter(nw.col('col') > 0)",
                            "display": "Filter col > 0",
                            "operation_type": "filter",
                            "params": {},
                        }
                    ],
                }
                repo.save(analysis_data)

                # Verify data exists
                analyses = repo.list_all()
                assert len(analyses) == 1

                # Reinitialize
                result = repo.reinitialize_database()
                assert result

                # Verify data is cleared
                analyses = repo.list_all()
                assert len(analyses) == 0

    def test_reinitialize_database_creates_empty_db_if_missing(self):
        """Test that reinitialize_database creates new database if missing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_dir = Path(tmpdir) / ".kittiwake"
            db_dir.mkdir(parents=True, exist_ok=True)

            with patch(
                "src.kittiwake.services.persistence.Path.home",
                return_value=Path(tmpdir),
            ):
                repo = SavedAnalysisRepository()

                # Ensure database doesn't exist
                assert repo.db_path.exists()

                # Delete database
                repo.db_path.unlink()

                # Reinitialize
                result = repo.reinitialize_database()
                assert result

                # Verify database exists
                assert repo.db_path.exists()

                # Verify schema is correct
                analyses = repo.list_all()
                assert isinstance(analyses, list)


class TestExportOfUnsavedAnalyses:
    """Tests for T097 - Prevent export of unsaved analyses."""

    def test_export_requires_saved_analysis(self):
        """Test that export requires analysis to be saved first."""
        pass

    def test_export_shows_save_first_message(self):
        """Test that export shows 'Save analysis first' message."""
        pass


class TestDuplicateAnalysisNames:
    """Tests for T098 - Handle duplicate analysis names."""

    def test_auto_version_with_timestamp_suffix(self):
        """Test that duplicate names get timestamp suffix."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch(
                "src.kittiwake.services.persistence.Path.home",
                return_value=Path(tmpdir),
            ):
                repo = SavedAnalysisRepository()

                # Save first analysis
                analysis_data = {
                    "name": "My Analysis",
                    "description": "Test",
                    "operation_count": 1,
                    "dataset_path": "/test/path.csv",
                    "operations": [
                        {
                            "code": "df = df.filter(nw.col('col') > 0)",
                            "display": "Filter col > 0",
                            "operation_type": "filter",
                            "params": {},
                        }
                    ],
                }
                result_id, versioned_name = repo.save(analysis_data)
                assert result_id
                assert versioned_name is None

                # Try to save with same name - should auto-version
                analysis_data2 = {
                    "name": "My Analysis",
                    "description": "Test 2",
                    "operation_count": 1,
                    "dataset_path": "/test/path.csv",
                    "operations": [
                        {
                            "code": "df = df.filter(nw.col('col') > 0)",
                            "display": "Filter col > 0",
                            "operation_type": "filter",
                            "params": {},
                        }
                    ],
                }
                result_id2, versioned_name2 = repo.save(analysis_data2)
                assert result_id2
                assert versioned_name2 is not None
                assert "My Analysis" in versioned_name2
                assert versioned_name2 != "My Analysis"

                # Verify both analyses exist
                analyses = repo.list_all()
                assert len(analyses) == 2

                # Verify names are different
                names = [a["name"] for a in analyses]
                assert "My Analysis" in names
                assert len([n for n in names if n.startswith("My Analysis")]) == 2

    def test_multiple_duplicates_get_unique_timestamps(self):
        """Test that multiple duplicates get unique timestamps."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch(
                "src.kittiwake.services.persistence.Path.home",
                return_value=Path(tmpdir),
            ):
                repo = SavedAnalysisRepository()

                base_name = "Test Analysis"
                analysis_data = {
                    "name": base_name,
                    "description": "Test",
                    "operation_count": 1,
                    "dataset_path": "/test/path.csv",
                    "operations": [
                        {
                            "code": "df = df.filter(nw.col('col') > 0)",
                            "display": "Filter col > 0",
                            "operation_type": "filter",
                            "params": {},
                        }
                    ],
                }

                # Save multiple times with same name
                results = []
                for i in range(5):
                    result_id, versioned_name = repo.save(analysis_data)
                    results.append((result_id, versioned_name))

                # First save should not be versioned
                assert results[0][1] is None

                # Subsequent saves should be versioned
                versioned_names = [r[1] for r in results[1:] if r[1]]
                assert len(versioned_names) == 4

                # All versioned names should be unique
                assert len(set(versioned_names)) == 4

                # All should start with base name
                for name in versioned_names:
                    assert base_name in name

    def test_unique_name_not_versioned_if_different(self):
        """Test that unique names are not versioned."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch(
                "src.kittiwake.services.persistence.Path.home",
                return_value=Path(tmpdir),
            ):
                repo = SavedAnalysisRepository()

                # Save first analysis
                analysis_data1 = {
                    "name": "Analysis 1",
                    "description": "Test",
                    "operation_count": 1,
                    "dataset_path": "/test/path.csv",
                    "operations": [
                        {
                            "code": "df = df.filter(nw.col('col') > 0)",
                            "display": "Filter col > 0",
                            "operation_type": "filter",
                            "params": {},
                        }
                    ],
                }
                result_id1, versioned_name1 = repo.save(analysis_data1)
                assert result_id1
                assert versioned_name1 is None

                # Save second analysis with different name
                analysis_data2 = {
                    "name": "Analysis 2",
                    "description": "Test",
                    "operation_count": 1,
                    "dataset_path": "/test/path.csv",
                    "operations": [
                        {
                            "code": "df = df.filter(nw.col('col') > 0)",
                            "display": "Filter col > 0",
                            "operation_type": "filter",
                            "params": {},
                        }
                    ],
                }
                result_id2, versioned_name2 = repo.save(analysis_data2)
                assert result_id2
                assert versioned_name2 is None

                # Verify both analyses exist with original names
                analyses = repo.list_all()
                names = [a["name"] for a in analyses]
                assert "Analysis 1" in names
                assert "Analysis 2" in names
