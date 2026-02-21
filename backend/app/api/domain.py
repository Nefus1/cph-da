import json
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.models import (
    Clause,
    GeneratedDocument,
    InterviewDraft,
    Template,
    TemplateVersion,
    User,
)
from app.schemas.domain import (
    ClauseCreate,
    ClauseEvaluationRequest,
    DocumentGenerateRequest,
    InterviewDraftCreate,
    InterviewDraftUpdate,
    TemplateCreate,
    TemplateResponse,
    TemplateVersionCreate,
    TemplateVersionResponse,
)

router = APIRouter(tags=["domain"])
OUTPUT_DIR = Path("generated")
OUTPUT_DIR.mkdir(exist_ok=True)


@router.post("/templates", response_model=TemplateResponse)
def create_template(payload: TemplateCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    template = Template(name=payload.name, description=payload.description, owner_id=user.id)
    db.add(template)
    db.commit()
    db.refresh(template)
    return template


@router.get("/templates", response_model=list[TemplateResponse])
def list_templates(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Template).filter(Template.owner_id == user.id).all()


@router.post("/template-versions", response_model=TemplateVersionResponse)
def create_template_version(payload: TemplateVersionCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    template = db.query(Template).filter(Template.id == payload.template_id, Template.owner_id == user.id).first()
    if not template:
        raise HTTPException(404, "Template not found")
    max_version = db.query(func.max(TemplateVersion.version_number)).filter(TemplateVersion.template_id == template.id).scalar()
    version = TemplateVersion(
        template_id=template.id,
        version_number=(max_version or 0) + 1,
        title=payload.title,
        body=payload.body,
    )
    db.add(version)
    db.commit()
    db.refresh(version)
    return version


@router.get("/templates/{template_id}/versions", response_model=list[TemplateVersionResponse])
def list_template_versions(template_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    template = db.query(Template).filter(Template.id == template_id, Template.owner_id == user.id).first()
    if not template:
        raise HTTPException(404, "Template not found")
    return db.query(TemplateVersion).filter(TemplateVersion.template_id == template_id).all()


@router.post("/template-versions/{version_id}/clauses")
def create_clause(version_id: int, payload: ClauseCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    version = (
        db.query(TemplateVersion)
        .join(Template, Template.id == TemplateVersion.template_id)
        .filter(TemplateVersion.id == version_id, Template.owner_id == user.id)
        .first()
    )
    if not version:
        raise HTTPException(404, "Template version not found")
    clause = Clause(template_version_id=version_id, **payload.model_dump())
    db.add(clause)
    db.commit()
    db.refresh(clause)
    return {"id": clause.id}


@router.post("/drafts")
def create_draft(payload: InterviewDraftCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    draft = InterviewDraft(user_id=user.id, template_version_id=payload.template_version_id)
    db.add(draft)
    db.commit()
    db.refresh(draft)
    return {"id": draft.id, "status": draft.status}


@router.get("/drafts/{draft_id}")
def get_draft(draft_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    draft = db.query(InterviewDraft).filter(InterviewDraft.id == draft_id, InterviewDraft.user_id == user.id).first()
    if not draft:
        raise HTTPException(404, "Draft not found")
    return {
        "id": draft.id,
        "answers_json": draft.answers_json,
        "status": draft.status,
        "current_step": draft.current_step,
    }


@router.put("/drafts/{draft_id}")
def update_draft(draft_id: int, payload: InterviewDraftUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    draft = db.query(InterviewDraft).filter(InterviewDraft.id == draft_id, InterviewDraft.user_id == user.id).first()
    if not draft:
        raise HTTPException(404, "Draft not found")
    draft.answers_json = payload.answers_json
    draft.current_step = payload.current_step
    draft.status = payload.status
    db.commit()
    return {"ok": True}


@router.get("/drafts/resume/latest")
def resume_latest(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    draft = (
        db.query(InterviewDraft)
        .filter(InterviewDraft.user_id == user.id)
        .order_by(InterviewDraft.updated_at.desc())
        .first()
    )
    if not draft:
        raise HTTPException(404, "No drafts")
    return {"draft_id": draft.id, "current_step": draft.current_step}


@router.post("/clauses/evaluate")
def evaluate_clause(payload: ClauseEvaluationRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    clause = (
        db.query(Clause)
        .join(TemplateVersion, TemplateVersion.id == Clause.template_version_id)
        .join(Template, Template.id == TemplateVersion.template_id)
        .filter(Clause.id == payload.clause_id, Template.owner_id == user.id)
        .first()
    )
    if not clause:
        raise HTTPException(404, "Clause not found")
    expr = clause.condition_expression or ""
    triggered = bool(expr) and any(str(v).lower() in expr.lower() for v in payload.answers.values())
    return {"clause_id": clause.id, "triggered": triggered, "preview": clause.content if triggered else ""}


@router.post("/documents/generate")
def generate_document(payload: DocumentGenerateRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    draft = db.query(InterviewDraft).filter(InterviewDraft.id == payload.draft_id, InterviewDraft.user_id == user.id).first()
    if not draft:
        raise HTTPException(404, "Draft not found")

    file_name = f"draft-{draft.id}.txt"
    file_path = OUTPUT_DIR / file_name
    rendered = f"Draft {draft.id}\nAnswers: {json.loads(draft.answers_json or '{}')}\nStatus: {draft.status}\n"
    file_path.write_text(rendered)

    document = GeneratedDocument(draft_id=draft.id, file_name=file_name, storage_path=str(file_path))
    db.add(document)
    db.commit()
    db.refresh(document)
    return {"document_id": document.id, "file_name": file_name}


@router.get("/documents/{document_id}/file")
def get_document(document_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    document = (
        db.query(GeneratedDocument)
        .join(InterviewDraft, InterviewDraft.id == GeneratedDocument.draft_id)
        .filter(GeneratedDocument.id == document_id, InterviewDraft.user_id == user.id)
        .first()
    )
    if not document:
        raise HTTPException(404, "Document not found")
    return FileResponse(document.storage_path, filename=document.file_name)
