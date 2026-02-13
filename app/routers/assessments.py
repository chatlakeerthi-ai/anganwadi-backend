from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from ..db import get_db
from ..init_db import init_db
from ..models import (
    Assessment,
    AssessmentStatus,
    CaregiverQuestionnaire,
    Child,
    CognitiveSkills,
    HearingScreening,
    MotorSkills,
    Recommendation,
    SpeechLanguage,
    VisionScreening,
)
from ..schemas import (
    AssessmentCreate,
    AssessmentOut,
    AssessmentReportOut,
    CaregiverIn,
    CognitiveIn,
    HearingIn,
    MotorIn,
    RecommendationOut,
    SpeechIn,
    VisionIn,
)
from ..scoring import (
    classify,
    composite_score,
    recommendations_for,
    score_cognitive,
    score_hearing,
    score_motor,
    score_speech,
    score_vision,
)

router = APIRouter(tags=["assessments"])

UPLOAD_DIR = Path(__file__).resolve().parents[2] / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Initialize DB tables on first import (MVP).
init_db()


def _assessment_out(a: Assessment) -> AssessmentOut:
    return AssessmentOut(
        id=a.id,
        child_id=a.child_id,
        status=a.status.value,
        vision_score=a.vision_score,
        hearing_score=a.hearing_score,
        speech_score=a.speech_score,
        motor_score=a.motor_score,
        cognitive_score=a.cognitive_score,
        composite_score=a.composite_score,
        classification=a.classification.value if a.classification else None,
        followup_months=a.followup_months,
        created_at=a.created_at,
        completed_at=a.completed_at,
    )


@router.post("/assessments", response_model=AssessmentOut)
def create_assessment(payload: AssessmentCreate, db: Session = Depends(get_db)):
    child = db.get(Child, payload.child_id)
    if not child:
        raise HTTPException(status_code=404, detail="Child not found")
    if not child.consent_obtained:
        raise HTTPException(status_code=400, detail="Consent is required before assessment")

    a = Assessment(child_id=payload.child_id, status=AssessmentStatus.in_progress)
    db.add(a)
    db.commit()
    db.refresh(a)
    return _assessment_out(a)


@router.get("/assessments/{assessment_id}", response_model=AssessmentOut)
def get_assessment(assessment_id: int, db: Session = Depends(get_db)):
    a = db.get(Assessment, assessment_id)
    if not a:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return _assessment_out(a)


@router.post("/assessments/{assessment_id}/vision", response_model=AssessmentOut)
def submit_vision(assessment_id: int, payload: VisionIn, db: Session = Depends(get_db)):
    a = db.get(Assessment, assessment_id)
    if not a:
        raise HTTPException(status_code=404, detail="Assessment not found")

    v = a.vision or VisionScreening(assessment_id=a.id)
    for k, val in payload.model_dump().items():
        setattr(v, k, val)

    a.vision = v
    db.add(a)
    db.commit()
    db.refresh(a)
    return _assessment_out(a)


@router.post("/assessments/{assessment_id}/hearing", response_model=AssessmentOut)
def submit_hearing(assessment_id: int, payload: HearingIn, db: Session = Depends(get_db)):
    a = db.get(Assessment, assessment_id)
    if not a:
        raise HTTPException(status_code=404, detail="Assessment not found")

    h = a.hearing or HearingScreening(assessment_id=a.id)
    for k, val in payload.model_dump().items():
        setattr(h, k, val)

    a.hearing = h
    db.add(a)
    db.commit()
    db.refresh(a)
    return _assessment_out(a)


@router.post("/assessments/{assessment_id}/speech", response_model=AssessmentOut)
def submit_speech(assessment_id: int, payload: SpeechIn, db: Session = Depends(get_db)):
    a = db.get(Assessment, assessment_id)
    if not a:
        raise HTTPException(status_code=404, detail="Assessment not found")

    s = a.speech or SpeechLanguage(assessment_id=a.id)
    for k, val in payload.model_dump().items():
        setattr(s, k, val)

    a.speech = s
    db.add(a)
    db.commit()
    db.refresh(a)
    return _assessment_out(a)


@router.post("/assessments/{assessment_id}/speech/audio", response_model=AssessmentOut)
def upload_speech_audio(
    assessment_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    a = db.get(Assessment, assessment_id)
    if not a:
        raise HTTPException(status_code=404, detail="Assessment not found")

    ext = os.path.splitext(file.filename or "audio")[1].lower() or ".wav"
    safe_ext = ext if ext in {".wav", ".m4a", ".aac", ".mp3", ".ogg"} else ".wav"

    out_path = UPLOAD_DIR / f"speech_{assessment_id}_{int(datetime.utcnow().timestamp())}{safe_ext}"
    with out_path.open("wb") as f:
        f.write(file.file.read())

    s = a.speech or SpeechLanguage(assessment_id=a.id)
    s.audio_path = str(out_path)
    a.speech = s

    db.add(a)
    db.commit()
    db.refresh(a)
    return _assessment_out(a)


@router.post("/assessments/{assessment_id}/motor", response_model=AssessmentOut)
def submit_motor(assessment_id: int, payload: MotorIn, db: Session = Depends(get_db)):
    a = db.get(Assessment, assessment_id)
    if not a:
        raise HTTPException(status_code=404, detail="Assessment not found")

    m = a.motor or MotorSkills(assessment_id=a.id)
    for k, val in payload.model_dump().items():
        setattr(m, k, val)

    a.motor = m
    db.add(a)
    db.commit()
    db.refresh(a)
    return _assessment_out(a)


@router.post("/assessments/{assessment_id}/cognitive", response_model=AssessmentOut)
def submit_cognitive(assessment_id: int, payload: CognitiveIn, db: Session = Depends(get_db)):
    a = db.get(Assessment, assessment_id)
    if not a:
        raise HTTPException(status_code=404, detail="Assessment not found")

    c = a.cognitive or CognitiveSkills(assessment_id=a.id)
    for k, val in payload.model_dump().items():
        setattr(c, k, val)

    a.cognitive = c
    db.add(a)
    db.commit()
    db.refresh(a)
    return _assessment_out(a)


@router.post("/assessments/{assessment_id}/caregiver", response_model=AssessmentOut)
def submit_caregiver(assessment_id: int, payload: CaregiverIn, db: Session = Depends(get_db)):
    a = db.get(Assessment, assessment_id)
    if not a:
        raise HTTPException(status_code=404, detail="Assessment not found")

    cg = a.caregiver or CaregiverQuestionnaire(assessment_id=a.id)
    for k, val in payload.model_dump().items():
        setattr(cg, k, val)

    a.caregiver = cg
    db.add(a)
    db.commit()
    db.refresh(a)
    return _assessment_out(a)


@router.post("/assessments/{assessment_id}/complete", response_model=AssessmentOut)
def complete_assessment(assessment_id: int, db: Session = Depends(get_db)):
    a = db.get(Assessment, assessment_id)
    if not a:
        raise HTTPException(status_code=404, detail="Assessment not found")

    if a.status == AssessmentStatus.completed:
        return _assessment_out(a)

    if not (a.vision and a.hearing and a.speech and a.motor and a.cognitive):
        raise HTTPException(status_code=400, detail="All 5 domains must be submitted before completion")

    # Domain scoring
    vision_res = score_vision(
        identifies_objects=a.vision.identifies_objects,
        matches_shapes=a.vision.matches_shapes,
        identifies_sizes=a.vision.identifies_sizes,
        identifies_colors=a.vision.identifies_colors,
        squints_or_close=a.vision.squints_or_close,
        difficulty_shapes_colors=a.vision.difficulty_shapes_colors,
        avoids_visual_tasks=a.vision.avoids_visual_tasks,
    )
    hearing_res = score_hearing(
        responds_to_soft_name_call=a.hearing.responds_to_soft_name_call,
        identifies_animal_sounds=a.hearing.identifies_animal_sounds,
        follows_one_step_command=a.hearing.follows_one_step_command,
        follows_two_step_command=a.hearing.follows_two_step_command,
        delayed_response=a.hearing.delayed_response,
        turns_one_ear=a.hearing.turns_one_ear,
        asks_repetition=a.hearing.asks_repetition,
    )
    speech_res = score_speech(
        names_objects=a.speech.names_objects,
        repeats_words=a.speech.repeats_words,
        answers_simple_questions=a.speech.answers_simple_questions,
        describes_picture=a.speech.describes_picture,
        vocabulary_clarity=a.speech.vocabulary_clarity,
        sentence_length=a.speech.sentence_length,
        pronunciation=a.speech.pronunciation,
        confidence=a.speech.confidence,
    )
    motor_res = score_motor(
        fine_drag_drop=a.motor.fine_drag_drop,
        fine_trace_line=a.motor.fine_trace_line,
        fine_pick_place=a.motor.fine_pick_place,
        gross_walk_straight=a.motor.gross_walk_straight,
        gross_jump_two_feet=a.motor.gross_jump_two_feet,
        gross_stand_one_foot_5s=a.motor.gross_stand_one_foot_5s,
        hand_dominance_unclear=a.motor.hand_dominance_unclear,
        poor_balance=a.motor.poor_balance,
        weak_grip_coordination=a.motor.weak_grip_coordination,
    )
    cognitive_res = score_cognitive(
        completes_puzzles=a.cognitive.completes_puzzles,
        matches_patterns=a.cognitive.matches_patterns,
        counts_objects=a.cognitive.counts_objects,
        identifies_sequences=a.cognitive.identifies_sequences,
        memory_game_recall=a.cognitive.memory_game_recall,
        solves_faster_than_norm=a.cognitive.solves_faster_than_norm,
        advanced_counting_reasoning=a.cognitive.advanced_counting_reasoning,
        high_curiosity=a.cognitive.high_curiosity,
        strong_memory=a.cognitive.strong_memory,
        creative_responses=a.cognitive.creative_responses,
    )

    a.vision_score = vision_res.score
    a.hearing_score = hearing_res.score
    a.speech_score = speech_res.score
    a.motor_score = motor_res.score
    a.cognitive_score = cognitive_res.score

    domain_scores = {
        "vision": a.vision_score,
        "hearing": a.hearing_score,
        "speech": a.speech_score,
        "motor": a.motor_score,
        "cognitive": a.cognitive_score,
    }

    a.composite_score = composite_score(
        vision=a.vision_score,
        hearing=a.hearing_score,
        speech=a.speech_score,
        motor=a.motor_score,
        cognitive=a.cognitive_score,
    )

    risk_total = vision_res.risk_flags + hearing_res.risk_flags + speech_res.risk_flags + motor_res.risk_flags + cognitive_res.risk_flags
    high_total = speech_res.high_potential_flags + motor_res.high_potential_flags + cognitive_res.high_potential_flags

    a.classification = classify(domain_scores=domain_scores, risk_flags_total=risk_total, high_flags_total=high_total)

    # Recommendations
    a.recommendations.clear()
    recs = recommendations_for(classification=a.classification, domain_scores=domain_scores)
    for r in recs:
        a.recommendations.append(
            Recommendation(
                recommendation_type=r["recommendation_type"],
                domain=r["domain"],
                description=r["description"],
                follow_up_months=r.get("follow_up_months"),
            )
        )

    a.followup_months = max((r.get("follow_up_months") or 0) for r in recs) if recs else None

    a.status = AssessmentStatus.completed
    a.completed_at = datetime.utcnow()

    db.add(a)
    db.commit()
    db.refresh(a)

    return _assessment_out(a)


@router.get("/assessments/{assessment_id}/report", response_model=AssessmentReportOut)
def get_report(assessment_id: int, db: Session = Depends(get_db)):
    a = db.get(Assessment, assessment_id)
    if not a:
        raise HTTPException(status_code=404, detail="Assessment not found")

    child = db.get(Child, a.child_id)
    if not child:
        raise HTTPException(status_code=404, detail="Child not found")

    assessment_out = _assessment_out(a)

    recs = [
        RecommendationOut(
            recommendation_type=r.recommendation_type.value,
            domain=r.domain,
            description=r.description,
            follow_up_months=r.follow_up_months,
        )
        for r in a.recommendations
    ]

    return AssessmentReportOut(
        assessment=assessment_out,
        child={
            "id": child.id,
            "name": child.name,
            "age_months": child.age_months,
            "guardian_name": child.guardian_name,
            "guardian_phone": child.guardian_phone,
            "consent_obtained": child.consent_obtained,
            "created_at": child.created_at,
        },
        domain_scores={
            "vision": a.vision_score,
            "hearing": a.hearing_score,
            "speech": a.speech_score,
            "motor": a.motor_score,
            "cognitive": a.cognitive_score,
        },
        composite_score=a.composite_score,
        classification=a.classification.value if a.classification else None,
        recommendations=recs,
    )
