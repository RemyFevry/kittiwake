"""Service for narwhals operations and pagination."""

import narwhals as nw


class NarwhalsOps:
    """Wrapper for narwhals operations."""

    @staticmethod
    def get_page(lazy_frame: nw.LazyFrame, page_num: int, page_size: int = 500):
        """Get a page of data from lazy frame.

        Uses row indexing and filtering for pagination since narwhals LazyFrame
        doesn't have a slice method. This creates a row_index column temporarily.
        """
        if lazy_frame is None:
            return None

        offset = page_num * page_size

        # Get first column name for ordering (stable pagination)
        try:
            order_col = lazy_frame.columns[0] if lazy_frame.columns else None
        except Exception:
            order_col = None

        if order_col is None:
            # Fallback: just use head if we can't determine column
            return lazy_frame.head(page_size).collect()

        # Use with_row_index + filter for pagination
        # This is more efficient than head().tail() for large offsets
        try:
            result = (
                lazy_frame.with_row_index(name="__row_idx__", order_by=order_col)
                .filter(
                    (nw.col("__row_idx__") >= offset)
                    & (nw.col("__row_idx__") < offset + page_size)
                )
                .drop("__row_idx__")
                .collect()
            )
            return result
        except Exception:
            # Fallback: use head if with_row_index fails
            return lazy_frame.head(page_size).collect()

    @staticmethod
    def get_schema(frame: nw.LazyFrame) -> dict[str, str]:
        """Get schema from frame."""
        if frame is None:
            return {}

        try:
            # Use collect_schema() to avoid collecting the entire frame
            if hasattr(frame, 'collect_schema'):
                schema = frame.collect_schema()
            else:
                # Fallback for backends that don't support collect_schema
                schema = frame.schema
            return {col: str(dtype) for col, dtype in schema.items()}
        except Exception:
            return {}

    @staticmethod
    def get_row_count(frame: nw.LazyFrame) -> int:
        """Get row count from lazy frame.

        Note: This collects the frame which may be expensive for large datasets.
        Consider using a count() aggregation if possible.
        """
        if frame is None:
            return 0

        try:
            # Collect and count rows using len()
            collected = frame.collect()
            return len(collected)
        except Exception:
            return 0
