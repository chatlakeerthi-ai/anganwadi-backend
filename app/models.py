from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


# ================= ENUMS =================

class AssessmentStatus(str, enum.Enum):
    draft = "draft"
    in_progress = "in_progress"
    completed = "completed"


class Classification(str, enum.Enum):
    low_risk = "Low risk"
    at_risk = "At risk"
    high_potential = "High potential"


class YesSometimesNo(str, enum.Enum):
    yes = "yes"
    sometimes = "sometimes"
    no = "no"


class RecommendationType(str, enum.Enum):
    intervention = "intervention"
    enrichment = "enrichment"
    referral = "referral"


# ================= CHILD =================

class Child(Base):
    __tablename__ = "children"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    age_months: Mapped[int]

    guardian_name: Mapped[str | None]
    guardian_phone: Mapped[str | None]
    consent_obtained: Mapped[bool] = mapped_column(default=False)

    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    assessments: Mapped[list["Assessment"]] = relationship(
        back_populates="child",
        cascade="all, delete-orphan"
    )


# ================= ASSESSMENT =================

class Assessment(Base):
    __tablename__ = "assessments"

    id: Mapped[int] = mapped_column(primary_key=True)
    child_id: Mapped[int] = mapped_column(ForeignKey("children.id"))

    status: Mapped[AssessmentStatus] = mapped_column(
        Enum(AssessmentStatus),
        default=AssessmentStatus.draft
    )

    vision_score: Mapped[int | None]
    hearing_score: Mapped[int | None]
    speech_score: Mapped[int | None]
    motor_score: Mapped[int | None]
    cognitive_score: Mapped[int | None]

    composite_score: Mapped[float | None]
    classification: Mapped[Classification | None] = mapped_column(Enum(Classification))

    total_duration_minutes: Mapped[int | None]
    followup_months: Mapped[int | None]

    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at: Mapped[datetime | None]

    child: Mapped["Child"] = relationship(back_populates="assessments")

    vision: Mapped["VisionScreening | None"] = relationship(back_populates="assessment", uselist=False)
    hearing: Mapped["HearingScreening | None"] = relationship(back_populates="assessment", uselist=False)
    speech: Mapped["SpeechLanguage | None"] = relationship(back_populates="assessment", uselist=False)
    motor: Mapped["MotorSkills | None"] = relationship(back_populates="assessment", uselist=False)
    cognitive: Mapped["CognitiveSkills | None"] = relationship(back_populates="assessment", uselist=False)
    caregiver: Mapped["CaregiverQuestionnaire | None"] = relationship(back_populates="assessment", uselist=False)

    recommendations: Mapped[list["Recommendation"]] = relationship(
        back_populates="assessment",
        cascade="all, delete-orphan"
    )


# ================= SCREENING TABLES =================

class VisionScreening(Base):
    __tablename__ = "vision_screening"

    id: Mapped[int] = mapped_column(primary_key=True)
    assessment_id: Mapped[int] = mapped_column(ForeignKey("assessments.id"), unique=True)

    identifies_objects: Mapped[bool] = mapped_column(default=False)
    matches_shapes: Mapped[bool] = mapped_column(default=False)

    notes: Mapped[str | None]

    assessment: Mapped["Assessment"] = relationship(back_populates="vision")


class HearingScreening(Base):
    __tablename__ = "hearing_screening"

    id: Mapped[int] = mapped_column(primary_key=True)
    assessment_id: Mapped[int] = mapped_column(ForeignKey("assessments.id"), unique=True)

    responds_to_soft_name_call: Mapped[bool] = mapped_column(default=False)

    notes: Mapped[str | None]

    assessment: Mapped["Assessment"] = relationship(back_populates="hearing")


class SpeechLanguage(Base):
    __tablename__ = "speech_language"

    id: Mapped[int] = mapped_column(primary_key=True)
    assessment_id: Mapped[int] = mapped_column(ForeignKey("assessments.id"), unique=True)

    names_objects: Mapped[bool] = mapped_column(default=False)
    audio_path: Mapped[str | None]

    assessment: Mapped["Assessment"] = relationship(back_populates="speech")


class MotorSkills(Base):
    __tablename__ = "motor_skills"

    id: Mapped[int] = mapped_column(primary_key=True)
    assessment_id: Mapped[int] = mapped_column(ForeignKey("assessments.id"), unique=True)

    fine_drag_drop: Mapped[bool] = mapped_column(default=False)

    assessment: Mapped["Assessment"] = relationship(back_populates="motor")


class CognitiveSkills(Base):
    __tablename__ = "cognitive_skills"

    id: Mapped[int] = mapped_column(primary_key=True)
    assessment_id: Mapped[int] = mapped_column(ForeignKey("assessments.id"), unique=True)

    completes_puzzles: Mapped[bool] = mapped_column(default=False)

    assessment: Mapped["Assessment"] = relationship(back_populates="cognitive")


# ================= CAREGIVER =================

class CaregiverQuestionnaire(Base):
    __tablename__ = "caregiver_questionnaire"

    id: Mapped[int] = mapped_column(primary_key=True)
    assessment_id: Mapped[int] = mapped_column(ForeignKey("assessments.id"), unique=True)

    speaks_in_sentences: Mapped[YesSometimesNo | None] = mapped_column(Enum(YesSometimesNo))

    assessment: Mapped["Assessment"] = relationship(back_populates="caregiver")


# ================= RECOMMENDATIONS =================

class Recommendation(Base):
    __tablename__ = "recommendations"

    id: Mapped[int] = mapped_column(primary_key=True)
    assessment_id: Mapped[int] = mapped_column(ForeignKey("assessments.id"))

    recommendation_type: Mapped[RecommendationType] = mapped_column(Enum(RecommendationType))
    domain: Mapped[str]
    description: Mapped[str]
    follow_up_months: Mapped[int | None]

    assessment: Mapped["Assessment"] = relationship(back_populates="recommendations")
