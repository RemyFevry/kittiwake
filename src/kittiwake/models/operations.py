"""Operation entities for data transformations."""

from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple
from uuid import UUID
import narwhals as nw


@dataclass
class Operation:
    """Base operation class for data transformations."""

    code: str  # Narwhals expression code
    display: str  # Human-readable description
    operation_type: str  # Type of operation
    params: Dict[str, Any]  # Operation parameters
    id: UUID = None

    def __post_init__(self):
        if self.id is None:
            from uuid import uuid4

            self.id = uuid4()

    def to_dict(self) -> Dict[str, Any]:
        """Serialize operation to dict."""
        return {
            "code": self.code,
            "display": self.display,
            "operation_type": self.operation_type,
            "params": self.params,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Operation":
        """Deserialize operation from dict."""
        return cls(
            code=data["code"],
            display=data["display"],
            operation_type=data["operation_type"],
            params=data["params"],
        )

    def apply(self, df: nw.LazyFrame) -> nw.LazyFrame:
        """Apply operation to dataframe."""
        if df is None:
            raise OperationError("Cannot apply operation to None dataframe")

        try:
            namespace = {"df": df, "nw": nw}
            result = eval(self.code, {"__builtins__": {}}, namespace)
            return result
        except Exception as e:
            raise OperationError(f"Failed to apply operation '{self.display}': {e}")

    def validate(self, df: nw.LazyFrame) -> Tuple[bool, Optional[str]]:
        """Validate operation against schema."""
        if df is None:
            return False, "Dataframe is None"

        try:
            # Try on sample data
            sample = df.head(10).collect()
            lazy_sample = nw.from_native(sample)
            self.apply(lazy_sample)
            return True, None
        except Exception as e:
            return False, str(e)


class OperationError(Exception):
    """Operation execution error."""

    pass


# Operation type constants
OPERATION_TYPES = [
    "filter",
    "aggregate",
    "pivot",
    "join",
    "select",
    "drop",
    "rename",
    "with_columns",
    "sort",
    "unique",
    "fill_null",
    "drop_nulls",
    "head",
    "tail",
    "sample",
]
