from __future__ import annotations

import json
from pathlib import Path

from app.template_engine.models import ClauseConfig, InterviewConfig, TemplateContent, TemplateMetadata


class TemplateLoader:
    def __init__(self, templates_root: str | Path):
        self.templates_root = Path(templates_root)

    def load(self, doc_type: str, version: str) -> TemplateContent:
        version_path = self.templates_root / doc_type / version
        interview = InterviewConfig.from_dict(self._read_yaml(version_path / "interview.yaml"))
        clauses = ClauseConfig.from_dict(self._read_yaml(version_path / "clauses.yaml"))
        metadata = TemplateMetadata.from_dict(self._read_yaml(version_path / "metadata.yaml"))

        template_file = version_path / metadata.template_file
        if not template_file.exists():
            raise FileNotFoundError(f"Template file does not exist: {template_file}")

        return TemplateContent(interview=interview, clauses=clauses, metadata=metadata)

    @staticmethod
    def _read_yaml(path: Path) -> dict:
        content = path.read_text(encoding="utf-8")
        try:
            loaded = json.loads(content)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Unable to parse {path}. This loader expects YAML files to use JSON-compatible syntax."
            ) from exc

        if not isinstance(loaded, dict):
            raise ValueError(f"Expected mapping in {path}, got {type(loaded).__name__}")
        return loaded
