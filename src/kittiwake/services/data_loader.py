"""Service for loading datasets from files and URLs."""

import asyncio
import os
from pathlib import Path
from typing import Callable
from uuid import uuid4

import httpx
import narwhals as nw

from ..models.dataset import Dataset
from ..utils.security import InputValidator, SecurityError
from .narwhals_ops import NarwhalsOps


class DataLoader:
    """Handles loading of datasets from various sources."""

    # Thresholds for large file detection
    LARGE_FILE_SIZE_MB = 50  # 50MB
    ESTIMATED_ROWS_THRESHOLD = 500_000  # 500K rows

    # Rough estimates for row count calculation (bytes per row)
    BYTES_PER_ROW_CSV = 50  # Conservative estimate for CSV
    BYTES_PER_ROW_PARQUET = 30  # Parquet is more compressed
    BYTES_PER_ROW_JSON = 100  # JSON is verbose

    def __init__(self):
        self.cache_dir = Path.home() / ".kittiwake" / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def get_file_info(self, source: str) -> tuple[int, int, bool]:
        """Get file size, estimated row count, and whether file is large.

        Args:
            source: File path or URL to check

        Returns:
            Tuple of (file_size_bytes, estimated_rows, is_large)
        """
        # For URLs, we can't easily get size without downloading
        if source.startswith(("http://", "https://")):
            return (0, 0, False)

        try:
            validated_path = InputValidator.validate_file_path(source)
            if not validated_path.exists():
                return (0, 0, False)

            file_size = validated_path.stat().st_size
            suffix = validated_path.suffix.lower()

            # Estimate row count based on file type
            if suffix == ".csv":
                bytes_per_row = self.BYTES_PER_ROW_CSV
            elif suffix == ".parquet":
                bytes_per_row = self.BYTES_PER_ROW_PARQUET
            elif suffix == ".json":
                bytes_per_row = self.BYTES_PER_ROW_JSON
            else:
                # Default conservative estimate
                bytes_per_row = 100

            estimated_rows = file_size // bytes_per_row

            # Check if file is large
            file_size_mb = file_size / (1024 * 1024)
            is_large = (
                file_size_mb > self.LARGE_FILE_SIZE_MB
                or estimated_rows > self.ESTIMATED_ROWS_THRESHOLD
            )

            return (file_size, estimated_rows, is_large)

        except Exception:
            return (0, 0, False)

    async def load_from_source(
        self,
        source: str,
        progress_callback: Callable[[float, str], None] | None = None,
        is_cancelled: Callable[[], bool] | None = None,
    ) -> Dataset:
        """Load dataset from file path or URL and return Dataset object.

        Args:
            source: File path or URL to load
            progress_callback: Optional callback for progress updates (value 0-1, message)
            is_cancelled: Optional callback to check if operation should be cancelled

        Returns:
            Dataset object with loaded data

        Raises:
            asyncio.CancelledError: If loading was cancelled by user

        """
        # Check for cancellation
        if is_cancelled and is_cancelled():
            import asyncio

            raise asyncio.CancelledError("Loading cancelled by user")

        # Report progress: starting
        if progress_callback:
            progress_callback(0.0, "Initializing...")

        # Load LazyFrame
        if source.startswith(("http://", "https://")):
            if is_cancelled and is_cancelled():
                import asyncio

                raise asyncio.CancelledError("Loading cancelled by user")

            if progress_callback:
                progress_callback(0.1, "Downloading file...")
            lazy_frame = await self._load_remote(source, is_cancelled=is_cancelled)
            name = source.split("/")[-1]
        else:
            if is_cancelled and is_cancelled():
                import asyncio

                raise asyncio.CancelledError("Loading cancelled by user")

            if progress_callback:
                progress_callback(0.1, "Reading file...")
            lazy_frame = await self._load_local(source, is_cancelled=is_cancelled)
            name = Path(source).name

        # Check for cancellation
        if is_cancelled and is_cancelled():
            import asyncio

            raise asyncio.CancelledError("Loading cancelled by user")

        # Report progress: file loaded
        if progress_callback:
            progress_callback(0.5, "Analyzing schema...")

        # Detect backend
        backend = self.detect_backend()

        # Get schema and row count
        schema = NarwhalsOps.get_schema(lazy_frame)

        if is_cancelled and is_cancelled():
            import asyncio

            raise asyncio.CancelledError("Loading cancelled by user")

        if progress_callback:
            progress_callback(0.8, "Counting rows...")
        row_count = NarwhalsOps.get_row_count(lazy_frame)

        # Check for cancellation
        if is_cancelled and is_cancelled():
            import asyncio

            raise asyncio.CancelledError("Loading cancelled by user")

        # Report progress: almost done
        if progress_callback:
            progress_callback(0.95, "Finalizing...")

        # Create Dataset object
        dataset = Dataset(
            id=uuid4(),
            name=name,
            source=source,
            backend=backend,
            frame=lazy_frame,
            original_frame=lazy_frame,
            schema=schema,
            row_count=row_count,
            is_active=True,
            is_lazy=True,
        )

        # Report progress: complete
        if progress_callback:
            progress_callback(1.0, "Complete")

        return dataset

    async def load(self, source: str) -> nw.LazyFrame:
        """Load dataset from file path or URL (returns LazyFrame).

        Deprecated: Use load_from_source() instead to get Dataset object.
        """
        if source.startswith(("http://", "https://")):
            return await self._load_remote(source)
        else:
            return self._load_local(source)

    async def _load_remote(
        self, url: str, is_cancelled: Callable[[], bool] | None = None
    ) -> nw.LazyFrame:
        """Load dataset from remote URL.

        Args:
            url: URL to load from
            is_cancelled: Optional callback to check if operation should be cancelled

        Returns:
            LazyFrame with loaded data

        Raises:
            asyncio.CancelledError: If loading was cancelled by user

        """
        # Download file to cache
        temp_path = await self._download_file(url, is_cancelled=is_cancelled)

        # Load from cached file
        return await self._load_local(str(temp_path), is_cancelled=is_cancelled)

    async def _download_file(
        self,
        url: str,
        timeout: float = 30.0,
        is_cancelled: Callable[[], bool] | None = None,
    ) -> Path:
        """Download file from URL to cache.

        Args:
            url: URL to download
            timeout: Request timeout in seconds (default: 30)
            is_cancelled: Optional callback to check if operation should be cancelled

        Returns:
            Path to downloaded file

        Raises:
            httpx.TimeoutException: If request times out
            httpx.HTTPStatusError: If HTTP error occurs
            ValueError: If URL is invalid or file cannot be written
            asyncio.CancelledError: If download was cancelled by user

        """
        filename = url.split("/")[-1] or "downloaded_data"
        dest_path = self.cache_dir / filename

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                async with client.stream("GET", url) as response:
                    response.raise_for_status()

                    with dest_path.open("wb") as f:
                        chunk_count = 0
                        async for chunk in response.aiter_bytes(chunk_size=8192):
                            # Check for cancellation every 10 chunks
                            chunk_count += 1
                            if (
                                chunk_count % 10 == 0
                                and is_cancelled
                                and is_cancelled()
                            ):
                                import asyncio

                                # Clean up partial download
                                if dest_path.exists():
                                    dest_path.unlink()
                                raise asyncio.CancelledError(
                                    "Download cancelled by user"
                                )

                            f.write(chunk)

        except httpx.TimeoutException as e:
            raise TimeoutError(f"Request timed out after {timeout}s: {url}") from e
        except httpx.HTTPStatusError as e:
            raise ValueError(f"HTTP error {e.response.status_code}: {url}") from e
        except Exception as e:
            raise ValueError(f"Failed to download file from {url}: {e}") from e

        return dest_path

    async def _load_local(
        self, path: str, is_cancelled: Callable[[], bool] | None = None
    ) -> nw.LazyFrame:
        """Load dataset from local file path asynchronously.

        Args:
            path: Path to local file
            is_cancelled: Optional callback to check if operation should be cancelled

        Returns:
            LazyFrame with loaded data

        Raises:
            FileNotFoundError: If file not found
            ValueError: If file format is unsupported or invalid path
            asyncio.CancelledError: If loading was cancelled by user

        """
        # Check for cancellation
        if is_cancelled and is_cancelled():
            raise asyncio.CancelledError("Loading cancelled by user")

        # Validate path for security
        try:
            validated_path = InputValidator.validate_file_path(path)
        except SecurityError as e:
            raise ValueError(f"Invalid file path: {e}")

        file_path = validated_path

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        # Determine file type and load accordingly
        suffix = file_path.suffix.lower()

        # Get backend module for narwhals
        backend = self._get_backend_module()

        # Run blocking file operations in executor to keep UI responsive
        loop = asyncio.get_event_loop()

        if suffix == ".csv":
            return await loop.run_in_executor(
                None, lambda: nw.scan_csv(str(file_path), backend=backend)
            )
        elif suffix == ".parquet":
            return await loop.run_in_executor(
                None, lambda: nw.scan_parquet(str(file_path), backend=backend)
            )
        elif suffix == ".json":
            # JSON loading varies by backend - use eager loading then convert to lazy
            def load_json():
                try:
                    import polars as pl

                    df = pl.read_json(str(file_path))
                    return nw.from_native(df, eager_only=False).lazy()
                except ImportError:
                    import pandas as pd

                    df = pd.read_json(str(file_path))
                    return nw.from_native(df, eager_only=False).lazy()

            return await loop.run_in_executor(None, load_json)
        elif suffix in [".xlsx", ".xls"]:
            # Excel files need to be read eagerly then converted
            def load_excel():
                import pandas as pd

                df = pd.read_excel(str(file_path))
                return nw.from_native(df, eager_only=False).lazy()

            return await loop.run_in_executor(None, load_excel)
        elif suffix == ".db":
            # DuckDB files - load using DuckDB connection
            def load_duckdb():
                try:
                    import duckdb

                    # Connect to DuckDB file and scan all tables
                    # For now, we'll scan the first table found
                    conn = duckdb.connect(str(file_path), read_only=True)
                    tables = conn.execute(
                        "SELECT table_name FROM information_schema.tables WHERE table_schema='main'"
                    ).fetchall()

                    if not tables:
                        raise ValueError(f"No tables found in DuckDB file: {path}")

                    table_name = tables[0][0]

                    # Validate table name to prevent SQL injection
                    try:
                        validated_table = InputValidator.validate_sql_identifier(
                            table_name
                        )
                    except SecurityError as e:
                        raise ValueError(f"Invalid table name in database: {e}")

                    # Use parameterized query - DuckDB supports ? placeholders
                    # However, table names cannot be parameterized in SQL, so we use validated identifier
                    # The table name comes from the database itself (not user input), but we validate it
                    df = conn.execute(f'SELECT * FROM "{validated_table}"').df()
                    conn.close()

                    # Convert to lazy frame
                    return nw.from_native(df, eager_only=False).lazy()
                except ImportError:
                    raise ValueError(
                        "DuckDB is required to read .db files. Install with: pip install duckdb"
                    )

            return await loop.run_in_executor(None, load_duckdb)
        else:
            raise ValueError(f"Unsupported file format: {suffix}")

    def detect_backend(self) -> str:
        """Detect available backend library.

        Returns:
            String name of available backend ('polars', 'pandas', 'pyarrow', or 'unknown')

        """
        try:
            import polars

            return "polars"
        except ImportError:
            try:
                import pandas

                return "pandas"
            except ImportError:
                try:
                    import pyarrow

                    return "pyarrow"
                except ImportError:
                    return "unknown"

    def _get_backend_module(self):
        """Get the actual backend module for narwhals.

        Returns:
            The backend module (polars, pandas, or pyarrow)

        Raises:
            ImportError: If no backend is available

        """
        try:
            import polars

            return polars
        except ImportError:
            try:
                import pandas

                return pandas
            except ImportError:
                try:
                    import pyarrow

                    return pyarrow
                except ImportError:
                    raise ImportError(
                        "No backend available. Please install polars, pandas, or pyarrow."
                    )
