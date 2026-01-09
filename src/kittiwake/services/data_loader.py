"""Service for loading datasets from files and URLs."""

from pathlib import Path
from uuid import uuid4

import httpx
import narwhals as nw

from ..models.dataset import Dataset
from .narwhals_ops import NarwhalsOps


class DataLoader:
    """Handles loading of datasets from various sources."""

    def __init__(self):
        self.cache_dir = Path.home() / ".kittiwake" / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    async def load_from_source(self, source: str) -> Dataset:
        """Load dataset from file path or URL and return Dataset object.

        Args:
            source: File path or URL to load

        Returns:
            Dataset object with loaded data
        """
        # Load LazyFrame
        if source.startswith(("http://", "https://")):
            lazy_frame = await self._load_remote(source)
            name = source.split("/")[-1]
        else:
            lazy_frame = self._load_local(source)
            name = Path(source).name

        # Detect backend
        backend = self.detect_backend()

        # Get schema and row count
        schema = NarwhalsOps.get_schema(lazy_frame)
        row_count = NarwhalsOps.get_row_count(lazy_frame)

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

        return dataset

    async def load(self, source: str) -> nw.LazyFrame:
        """Load dataset from file path or URL (returns LazyFrame).

        Deprecated: Use load_from_source() instead to get Dataset object.
        """
        if source.startswith(("http://", "https://")):
            return await self._load_remote(source)
        else:
            return self._load_local(source)

    async def _load_remote(self, url: str) -> nw.LazyFrame:
        """Load dataset from remote URL."""
        # Download file to cache
        temp_path = await self._download_file(url)

        # Load from cached file
        return self._load_local(str(temp_path))

    async def _download_file(self, url: str, timeout: float = 30.0) -> Path:
        """Download file from URL to cache.

        Args:
            url: URL to download
            timeout: Request timeout in seconds (default: 30)

        Returns:
            Path to downloaded file

        Raises:
            httpx.TimeoutException: If request times out
            httpx.HTTPStatusError: If HTTP error occurs
            ValueError: If URL is invalid or file cannot be written
        """
        filename = url.split("/")[-1] or "downloaded_data"
        dest_path = self.cache_dir / filename

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                async with client.stream("GET", url) as response:
                    response.raise_for_status()

                    with dest_path.open("wb") as f:
                        async for chunk in response.aiter_bytes(chunk_size=8192):
                            f.write(chunk)

        except httpx.TimeoutException as e:
            raise TimeoutError(f"Request timed out after {timeout}s: {url}") from e
        except httpx.HTTPStatusError as e:
            raise ValueError(f"HTTP error {e.response.status_code}: {url}") from e
        except Exception as e:
            raise ValueError(f"Failed to download file from {url}: {e}") from e

        return dest_path

    def _load_local(self, path: str) -> nw.LazyFrame:
        """Load dataset from local file path."""
        file_path = Path(path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        # Determine file type and load accordingly
        suffix = file_path.suffix.lower()

        # Get backend module for narwhals
        backend = self._get_backend_module()

        if suffix == ".csv":
            return nw.scan_csv(str(file_path), backend=backend)
        elif suffix == ".parquet":
            return nw.scan_parquet(str(file_path), backend=backend)
        elif suffix == ".json":
            # JSON loading varies by backend - use eager loading then convert to lazy
            try:
                import polars as pl
                df = pl.read_json(str(file_path))
                return nw.from_native(df, eager_only=False).lazy()
            except ImportError:
                import pandas as pd
                df = pd.read_json(str(file_path))
                return nw.from_native(df, eager_only=False).lazy()
        elif suffix in [".xlsx", ".xls"]:
            # Excel files need to be read eagerly then converted
            import pandas as pd
            df = pd.read_excel(str(file_path))
            return nw.from_native(df, eager_only=False).lazy()
        elif suffix == ".db":
            # DuckDB files - load using DuckDB connection
            try:
                import duckdb
                # Connect to DuckDB file and scan all tables
                # For now, we'll scan the first table found
                conn = duckdb.connect(str(file_path), read_only=True)
                tables = conn.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='main'").fetchall()
                
                if not tables:
                    raise ValueError(f"No tables found in DuckDB file: {path}")
                
                table_name = tables[0][0]
                # Use DuckDB to read and convert to backend format
                df = conn.execute(f"SELECT * FROM {table_name}").df()
                conn.close()
                
                # Convert to lazy frame
                return nw.from_native(df, eager_only=False).lazy()
            except ImportError:
                raise ValueError("DuckDB is required to read .db files. Install with: pip install duckdb")
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
