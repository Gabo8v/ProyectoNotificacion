from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.template import Template
from app.schemas.template import TemplateCreate, TemplateOut

router = APIRouter(prefix="/templates", tags=["templates"])


@router.get("/", response_model=list[TemplateOut])
def list_templates(db: Session = Depends(get_db)):
    return db.query(Template).order_by(Template.created_at.desc()).all()


@router.post("/", response_model=TemplateOut)
def create_template(data: TemplateCreate, db: Session = Depends(get_db)):
    template = Template(
        name=data.name,
        keywords=data.keywords,
        subject=data.subject,
        body=data.body,
    )
    db.add(template)
    db.commit()
    db.refresh(template)
    return template


@router.delete("/{template_id}")
def delete_template(template_id: str, db: Session = Depends(get_db)):
    template = db.query(Template).filter(Template.id == template_id).first()
    if template:
        db.delete(template)
        db.commit()
    return {"ok": True}
