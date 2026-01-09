"""Operation entities for data transformations."""

from dataclasses import dataclass, field
from typing import Any
from uuid import UUID, uuid4

import narwhals as nw


@dataclass
class Operation:
    """Base operation class for data transformations."""

    code: str  # Narwhals expression code
    display: str  # Human-readable description
    operation_type: str  # Type of operation
    params: dict[str, Any]  # Operation parameters
    id: UUID = field(default_factory=uuid4)
    state: str = "queued"  # Operation state: "queued" | "executed" | "failed"
    error_message: str | None = None  # Error message if state is "failed"

    def to_dict(self) -> dict[str, Any]:
        """Serialize operation to dict."""
        return {
            "code": self.code,
            "display": self.display,
            "operation_type": self.operation_type,
            "params": self.params,
            "state": self.state,
        }

    def to_code(self) -> str:
        """Generate Python code for this operation.
        
        Returns the code attribute directly, which is the narwhals expression
        to be executed. This is used for exporting operations to notebooks.
        """
        return self.code

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Operation":
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
            exec(self.code, {"__builtins__": {}}, namespace)
            return namespace["df"]
        except Exception as e:
            raise OperationError(f"Failed to apply operation '{self.display}': {e}")

    def validate(self, df: nw.LazyFrame) -> tuple[bool, str | None]:
        """Validate operation against schema."""
        if df is None:
            return False, "Dataframe is None"

        try:
            # Try on sample data
            sample = df.head(10).collect()
            lazy_sample = nw.from_native(sample).lazy()
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
