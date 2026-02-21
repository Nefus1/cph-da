from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


_ALLOWED_QUESTION_TYPES = {"boolean", "string", "number", "select"}


def _expect_type(value: Any, expected_type: type, field_name: str) -> Any:
    if not isinstance(value, expected_type):
        raise ValueError(f"Field '{field_name}' must be of type {expected_type.__name__}")
    return value


def _expect_dict(value: Any, field_name: str) -> dict:
    return _expect_type(value, dict, field_name)


@dataclass(slots=True)
class InterviewQuestion:
    id: str
    prompt: str
    type: str = "string"
    options: list[str] = field(default_factory=list)
    visible_when: str | None = None
    required: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "InterviewQuestion":
        question_type = data.get("type", "string")
        if question_type not in _ALLOWED_QUESTION_TYPES:
            raise ValueError(f"Unsupported question type '{question_type}'")
        options = data.get("options", [])
        if not isinstance(options, list) or not all(isinstance(option, str) for option in options):
            raise ValueError("Question options must be a list of strings")
        return cls(
            id=str(data["id"]),
            prompt=str(data["prompt"]),
            type=question_type,
            options=options,
            visible_when=data.get("visible_when"),
            required=bool(data.get("required", False)),
        )


@dataclass(slots=True)
class InterviewConfig:
    questions: list[InterviewQuestion] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "InterviewConfig":
        questions = [_expect_dict(item, "questions[]") for item in data.get("questions", [])]
        return cls(questions=[InterviewQuestion.from_dict(item) for item in questions])


@dataclass(slots=True)
class ClauseDefinition:
    id: str
    title: str
    text: str
    default_included: bool = False
    include_when: str | None = None
    depends_on: list[str] = field(default_factory=list)
    exclusive_group: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ClauseDefinition":
        depends_on = data.get("depends_on", [])
        if not isinstance(depends_on, list) or not all(isinstance(dep, str) for dep in depends_on):
            raise ValueError("Clause depends_on must be a list of strings")
        return cls(
            id=str(data["id"]),
            title=str(data["title"]),
            text=str(data["text"]),
            default_included=bool(data.get("default_included", False)),
            include_when=data.get("include_when"),
            depends_on=depends_on,
            exclusive_group=data.get("exclusive_group"),
        )


@dataclass(slots=True)
class ClauseConfig:
    clauses: list[ClauseDefinition] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ClauseConfig":
        clauses = [_expect_dict(item, "clauses[]") for item in data.get("clauses", [])]
        return cls(clauses=[ClauseDefinition.from_dict(item) for item in clauses])


@dataclass(slots=True)
class ValidationRule:
    id: str
    expression: str
    message: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ValidationRule":
        return cls(id=str(data["id"]), expression=str(data["expression"]), message=str(data["message"]))


@dataclass(slots=True)
class PackDefinition:
    id: str
    include_when: str | None = None
    questions: list[InterviewQuestion] = field(default_factory=list)
    validations: list[ValidationRule] = field(default_factory=list)
    clauses: list[ClauseDefinition] = field(default_factory=list)
    disclosures: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PackDefinition":
        return cls(
            id=str(data["id"]),
            include_when=data.get("include_when"),
            questions=[InterviewQuestion.from_dict(_expect_dict(item, "pack.questions[]")) for item in data.get("questions", [])],
            validations=[ValidationRule.from_dict(_expect_dict(item, "pack.validations[]")) for item in data.get("validations", [])],
            clauses=[ClauseDefinition.from_dict(_expect_dict(item, "pack.clauses[]")) for item in data.get("clauses", [])],
            disclosures=[str(item) for item in data.get("disclosures", [])],
        )


@dataclass(slots=True)
class JurisdictionConfig:
    base_pack: str
    packs: list[PackDefinition] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "JurisdictionConfig":
        packs = [PackDefinition.from_dict(_expect_dict(item, "jurisdiction.packs[]")) for item in data.get("packs", [])]
        base_pack = str(data["base_pack"])
        if base_pack not in {pack.id for pack in packs}:
            raise ValueError(f"base_pack '{base_pack}' must exist in packs")
        return cls(base_pack=base_pack, packs=packs)


@dataclass(slots=True)
class TemplateMetadata:
    doc_type: str
    version: str
    template_file: str
    jurisdiction: JurisdictionConfig

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TemplateMetadata":
        return cls(
            doc_type=str(data["doc_type"]),
            version=str(data["version"]),
            template_file=str(data.get("template_file", "template.docx")),
            jurisdiction=JurisdictionConfig.from_dict(_expect_dict(data["jurisdiction"], "jurisdiction")),
        )


@dataclass(slots=True)
class TemplateContent:
    interview: InterviewConfig
    clauses: ClauseConfig
    metadata: TemplateMetadata


@dataclass(slots=True)
class ComposedJurisdictionPack:
    selected_pack_ids: list[str]
    questions: list[InterviewQuestion]
    validations: list[ValidationRule]
    clauses: list[ClauseDefinition]
    disclosures: list[str]
