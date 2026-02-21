from datetime import datetime

from pydantic import BaseModel


class ClauseCreate(BaseModel):
    label: str
    group_type: str = "rules"
    is_optional: bool = False
    condition_expression: str | None = None
    content: str


class TemplateCreate(BaseModel):
    name: str
    description: str | None = None


class TemplateVersionCreate(BaseModel):
    template_id: int
    title: str
    body: str


class InterviewDraftCreate(BaseModel):
    template_version_id: int


class InterviewDraftUpdate(BaseModel):
    answers_json: str
    current_step: int
    status: str = "in_progress"


class ClauseEvaluationRequest(BaseModel):
    clause_id: int
    answers: dict[str, str | int | bool]


class DocumentGenerateRequest(BaseModel):
    draft_id: int


class DocumentGenerateResponse(BaseModel):
    document_id: int
    docx_file_name: str
    pdf_file_name: str | None
    template_version: str
    created_at: datetime


class TemplateResponse(BaseModel):
    id: int
    name: str
    description: str | None

    class Config:
        from_attributes = True


class TemplateVersionResponse(BaseModel):
    id: int
    template_id: int
    version_number: int
    title: str
    body: str

    class Config:
        from_attributes = True
