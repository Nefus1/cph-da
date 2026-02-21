import json
import types
from pathlib import Path

from app.models.models import Clause, InterviewDraft, TemplateVersion
from app.services.document_generation import DocumentGenerationService


class _FakeDocxTemplate:
    def __init__(self, template_path: str):
        self.template_path = template_path
        self.context = None

    def render(self, context: dict):
        self.context = context

    def save(self, output_path: str):
        Path(output_path).write_text(json.dumps(self.context), encoding="utf-8")


def test_generate_renders_docx_and_resolves_clauses(monkeypatch, tmp_path):
    templates_root = tmp_path / "templates" / "three_day_notice" / "v1"
    templates_root.mkdir(parents=True)
    (templates_root / "template.docx").write_text("template", encoding="utf-8")

    monkeypatch.setitem(__import__("sys").modules, "docxtpl", types.SimpleNamespace(DocxTemplate=_FakeDocxTemplate))

    service = DocumentGenerationService(templates_root=tmp_path / "templates", storage_root=tmp_path / "storage")

    draft = InterviewDraft(id=5, user_id=9, template_version_id=3, answers_json=json.dumps({"include_late_fee": True}))
    template_version = TemplateVersion(id=3, template_id=1, version_number=1, title="v1", body="")
    clauses = [
        Clause(id=1, template_version_id=3, label="Late Fee", content="Late fee applies", condition_expression="include_late_fee == True"),
        Clause(id=2, template_version_id=3, label="Optional", content="Never shown", condition_expression="include_late_fee == False"),
    ]

    artifacts = service.generate(draft=draft, template_version=template_version, clauses=clauses)

    assert artifacts.docx_path.exists()
    assert artifacts.storage_path == tmp_path / "storage" / "9" / "5"
    assert artifacts.pdf_path is None
    rendered = json.loads(artifacts.docx_path.read_text(encoding="utf-8"))
    assert rendered["interview"]["include_late_fee"] is True
    assert rendered["resolved_clauses"] == [{"label": "Late Fee", "content": "Late fee applies"}]
    assert len(artifacts.docx_sha256) == 64


def test_generate_uses_template_version_hint(monkeypatch, tmp_path):
    template_dir = tmp_path / "templates" / "notice" / "v2"
    template_dir.mkdir(parents=True)
    (template_dir / "template.docx").write_text("template", encoding="utf-8")

    monkeypatch.setitem(__import__("sys").modules, "docxtpl", types.SimpleNamespace(DocxTemplate=_FakeDocxTemplate))

    service = DocumentGenerationService(templates_root=tmp_path / "templates", storage_root=tmp_path / "storage")

    draft = InterviewDraft(id=7, user_id=11, template_version_id=1, answers_json="{}")
    template_version = TemplateVersion(id=1, template_id=1, version_number=1, title="", body="notice:v2")

    artifacts = service.generate(draft=draft, template_version=template_version, clauses=[])

    assert artifacts.template_version_label == "notice:v2"
