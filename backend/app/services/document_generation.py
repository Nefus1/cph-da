from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from app.models.models import Clause, InterviewDraft, TemplateVersion
from app.template_engine.expression import SafeBooleanEvaluator


@dataclass(slots=True)
class DocumentArtifacts:
    template_version_label: str
    storage_path: Path
    docx_path: Path
    pdf_path: Path | None
    docx_sha256: str
    pdf_sha256: str | None


class DocumentGenerationService:
    def __init__(
        self,
        templates_root: str | Path = "templates",
        storage_root: str | Path = "storage",
        converter_binary: str = "soffice",
    ):
        self.templates_root = Path(templates_root)
        self.storage_root = Path(storage_root)
        self.converter_binary = converter_binary
        self.evaluator = SafeBooleanEvaluator()

    def generate(self, draft: InterviewDraft, template_version: TemplateVersion, clauses: list[Clause]) -> DocumentArtifacts:
        answers = self._load_answers(draft.answers_json)
        resolved_clauses = self._resolve_clauses(clauses, answers)

        template_docx, template_version_label = self._resolve_template_file(template_version)

        target_dir = self.storage_root / str(draft.user_id) / str(draft.id)
        target_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now(tz=timezone.utc).strftime("%Y%m%d%H%M%S")
        docx_path = target_dir / f"generated-{timestamp}.docx"
        pdf_path = target_dir / f"generated-{timestamp}.pdf"

        rendered_context = {
            "interview": answers,
            "resolved_clauses": [{"label": clause.label, "content": clause.content} for clause in resolved_clauses],
            "resolved_clause_text": "\n\n".join(clause.content for clause in resolved_clauses),
            "draft_id": draft.id,
            "generated_at": datetime.now(tz=timezone.utc).isoformat(),
        }

        from docxtpl import DocxTemplate

        template = DocxTemplate(str(template_docx))
        template.render(rendered_context)
        template.save(str(docx_path))

        docx_sha256 = self._compute_sha256(docx_path)

        generated_pdf_path, pdf_sha256 = self._convert_to_pdf(docx_path, pdf_path)

        return DocumentArtifacts(
            template_version_label=template_version_label,
            storage_path=target_dir,
            docx_path=docx_path,
            pdf_path=generated_pdf_path,
            docx_sha256=docx_sha256,
            pdf_sha256=pdf_sha256,
        )

    def _resolve_template_file(self, template_version: TemplateVersion) -> tuple[Path, str]:
        # Style-aware insertion points are handled in the DOCX via Jinja placeholders (docxtpl),
        # e.g. {{ interview.tenant_name }} and {{ resolved_clause_text }} in pre-styled blocks.
        doc_type = "three_day_notice"
        version = "v1"

        if template_version.body and ":" in template_version.body:
            maybe_doc_type, maybe_version = template_version.body.split(":", maxsplit=1)
            if maybe_doc_type and maybe_version:
                doc_type, version = maybe_doc_type, maybe_version

        template_docx = self.templates_root / doc_type / version / "template.docx"
        if not template_docx.exists():
            raise FileNotFoundError(f"Template not found: {template_docx}")

        return template_docx, f"{doc_type}:{version}"

    def _resolve_clauses(self, clauses: list[Clause], answers: dict) -> list[Clause]:
        resolved: list[Clause] = []
        for clause in clauses:
            expr = (clause.condition_expression or "").strip()
            include = True if not expr else self.evaluator.evaluate(expr, answers)
            if include:
                resolved.append(clause)
        return resolved

    @staticmethod
    def _load_answers(raw_answers: str) -> dict:
        if not raw_answers:
            return {}
        try:
            loaded = json.loads(raw_answers)
        except json.JSONDecodeError:
            return {}
        return loaded if isinstance(loaded, dict) else {}

    @staticmethod
    def _compute_sha256(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as file_obj:
            for chunk in iter(lambda: file_obj.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    def _convert_to_pdf(self, docx_path: Path, target_pdf_path: Path) -> tuple[Path | None, str | None]:
        if shutil.which(self.converter_binary) is None:
            return None, None

        try:
            subprocess.run(
                [
                    self.converter_binary,
                    "--headless",
                    "--convert-to",
                    "pdf",
                    "--outdir",
                    str(target_pdf_path.parent),
                    str(docx_path),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
        except subprocess.CalledProcessError:
            return None, None

        converted_pdf = target_pdf_path.parent / f"{docx_path.stem}.pdf"
        if converted_pdf.exists() and converted_pdf != target_pdf_path:
            converted_pdf.replace(target_pdf_path)

        if not target_pdf_path.exists():
            return None, None

        return target_pdf_path, self._compute_sha256(target_pdf_path)
