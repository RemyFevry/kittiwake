"""Export service for rendering analyses to various formats using Jinja2."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape


class ExportService:
    """Service for exporting analyses to Python/marimo/Jupyter formats."""

    def __init__(self):
        """Initialize export service with Jinja2 environment."""
        # Templates are in specs/001-tui-data-explorer/contracts/
        # Get project root (4 levels up from this file)
        self.project_root = Path(__file__).parent.parent.parent.parent
        self.templates_dir = self.project_root / "specs" / "001-tui-data-explorer" / "contracts"

        if not self.templates_dir.exists():
            raise FileNotFoundError(f"Templates directory not found: {self.templates_dir}")

        # Setup Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            autoescape=select_autoescape(),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def export_to_python(
        self,
        analysis_data: dict[str, Any],
        output_path: str | Path,
    ) -> Path:
        """Export analysis to Python script.

        Args:
            analysis_data: Analysis data with keys:
                - name: str
                - description: str (optional)
                - dataset_path: str
                - operations: list[dict] with 'display' and 'code' keys
            output_path: Output file path

        Returns:
            Path to written file
        """
        template = self.env.get_template("export-python.jinja2")
        
        context = self._prepare_context(analysis_data)
        rendered = template.render(**context)

        output = Path(output_path)
        output.write_text(rendered, encoding="utf-8")
        return output

    def export_to_marimo(
        self,
        analysis_data: dict[str, Any],
        output_path: str | Path,
    ) -> Path:
        """Export analysis to marimo notebook.

        Args:
            analysis_data: Analysis data (same format as export_to_python)
            output_path: Output file path

        Returns:
            Path to written file
        """
        template = self.env.get_template("export-marimo.jinja2")
        
        context = self._prepare_context(analysis_data)
        # Add backend dependencies for marimo if needed
        context["backend_dependencies"] = []
        
        rendered = template.render(**context)

        output = Path(output_path)
        output.write_text(rendered, encoding="utf-8")
        return output

    def export_to_jupyter(
        self,
        analysis_data: dict[str, Any],
        output_path: str | Path,
    ) -> Path:
        """Export analysis to Jupyter notebook.

        Args:
            analysis_data: Analysis data (same format as export_to_python)
            output_path: Output file path

        Returns:
            Path to written file
        """
        template = self.env.get_template("export-jupyter.jinja2")
        
        context = self._prepare_context(analysis_data)
        rendered = template.render(**context)

        # Parse as JSON to validate structure
        try:
            notebook = json.loads(rendered)
        except json.JSONDecodeError as e:
            raise ValueError(f"Generated invalid Jupyter notebook JSON: {e}")

        output = Path(output_path)
        output.write_text(json.dumps(notebook, indent=2), encoding="utf-8")
        return output

    def _prepare_context(self, analysis_data: dict[str, Any]) -> dict[str, Any]:
        """Prepare template context from analysis data.

        Args:
            analysis_data: Raw analysis data

        Returns:
            Context dict for Jinja2 template
        """
        # Get kittiwake version - default to "dev" if not available
        kittiwake_version = "dev"

        return {
            "analysis_name": analysis_data.get("name", "Untitled Analysis"),
            "analysis_description": analysis_data.get("description", ""),
            "dataset_path": analysis_data.get("dataset_path", ""),
            "operations": analysis_data.get("operations", []),
            "operation_count": len(analysis_data.get("operations", [])),
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "kittiwake_version": kittiwake_version,
        }
