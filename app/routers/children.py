from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Child
from ..schemas import ChildCreate, ChildOut

router = APIRouter(tags=["children"])


@router.post("/children", response_model=ChildOut)
def create_child(payload: ChildCreate, db: Session = Depends(get_db)):
    child = Child(
        name=payload.name,
        age_months=payload.age_months,
        guardian_name=payload.guardian_name,
        guardian_phone=payload.guardian_phone,
        consent_obtained=payload.consent_obtained,
    )
    db.add(child)
    db.commit()
    db.refresh(child)
    return ChildOut(
        id=child.id,
        name=child.name,
        age_months=child.age_months,
        guardian_name=child.guardian_name,
        guardian_phone=child.guardian_phone,
        consent_obtained=child.consent_obtained,
        created_at=child.created_at,
    )


@router.get("/children", response_model=list[ChildOut])
def list_children(db: Session = Depends(get_db)):
    children = db.query(Child).order_by(Child.created_at.desc()).all()
    return [
        ChildOut(
            id=c.id,
            name=c.name,
            age_months=c.age_months,
            guardian_name=c.guardian_name,
            guardian_phone=c.guardian_phone,
            consent_obtained=c.consent_obtained,
            created_at=c.created_at,
        )
        for c in children
    ]


@router.get("/children/{child_id}", response_model=ChildOut)
def get_child(child_id: int, db: Session = Depends(get_db)):
    c = db.get(Child, child_id)
    if not c:
        raise HTTPException(status_code=404, detail="Child not found")

    return ChildOut(
        id=c.id,
        name=c.name,
        age_months=c.age_months,
        guardian_name=c.guardian_name,
        guardian_phone=c.guardian_phone,
        consent_obtained=c.consent_obtained,
        created_at=c.created_at,
    )
