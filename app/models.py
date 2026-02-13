from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class AssessmentStatus(str, enum.Enum):
    draft = "draft"
    in_progress = "in_progress"
    completed = "completed"


class Classification(str, enum.Enum):
    low_risk = "Low risk"
    at_risk = "At risk"
    high_potential = "High potential"


class Child(Base):
    __tablename__ = "Children"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    age_months: Mapped[int] = mapped_column(Integer, nullable=False)

    guardian_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    guardian_phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    consent_obtained: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    assessments: Mapped[list[Assessment]] = relationship(back_populates="child", cascade="all, delete-orphan")


class Assessment(Base):
    __tablename__ = "assessments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    child_id: Mapped[int] = mapped_column(ForeignKey("children.id"), nullable=False)

    status: Mapped[AssessmentStatus] = mapped_column(Enum(AssessmentStatus), default=AssessmentStatus.draft, nullable=False)

    vision_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    hearing_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    speech_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    motor_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cognitive_score: Mapped[int | None] = mapped_column(Integer, nullable=True)

    composite_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    classification: Mapped[Classification | None] = mapped_column(Enum(Classification), nullable=True)

    total_duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    followup_months: Mapped[int | None] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    child: Mapped[Child] = relationship(back_populates="assessments")

    vision: Mapped[VisionScreening | None] = relationship(back_populates="assessment", uselist=False, cascade="all, delete-orphan")
    hearing: Mapped[HearingScreening | None] = relationship(back_populates="assessment", uselist=False, cascade="all, delete-orphan")
    speech: Mapped[SpeechLanguage | None] = relationship(back_populates="assessment", uselist=False, cascade="all, delete-orphan")
    motor: Mapped[MotorSkills | None] = relationship(back_populates="assessment", uselist=False, cascade="all, delete-orphan")
    cognitive: Mapped[CognitiveSkills | None] = relationship(back_populates="assessment", uselist=False, cascade="all, delete-orphan")
    caregiver: Mapped[CaregiverQuestionnaire | None] = relationship(back_populates="assessment", uselist=False, cascade="all, delete-orphan")

    recommendations: Mapped[list[Recommendation]] = relationship(back_populates="assessment", cascade="all, delete-orphan")


class VisionScreening(Base):
    __tablename__ = "vision_screening"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    assessment_id: Mapped[int] = mapped_column(ForeignKey("assessments.id"), unique=True, nullable=False)

    identifies_objects: Mapped[bool] = mapped_column(Boolean, default=False)
    matches_shapes: Mapped[bool] = mapped_column(Boolean, default=False)
    identifies_sizes: Mapped[bool] = mapped_column(Boolean, default=False)
    identifies_colors: Mapped[bool] = mapped_column(Boolean, default=False)

    squints_or_close: Mapped[bool] = mapped_column(Boolean, default=False)
    difficulty_shapes_colors: Mapped[bool] = mapped_column(Boolean, default=False)
    avoids_visual_tasks: Mapped[bool] = mapped_column(Boolean, default=False)

    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    assessment: Mapped[Assessment] = relationship(back_populates="Vision")


class HearingScreening(Base):
    __tablename__ = "hearing_screening"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    assessment_id: Mapped[int] = mapped_column(ForeignKey("assessments.id"), unique=True, nullable=False)

    responds_to_soft_name_call: Mapped[bool] = mapped_column(Boolean, default=False)
    identifies_animal_sounds: Mapped[bool] = mapped_column(Boolean, default=False)
    follows_one_step_command: Mapped[bool] = mapped_column(Boolean, default=False)
    follows_two_step_command: Mapped[bool] = mapped_column(Boolean, default=False)

    delayed_response: Mapped[bool] = mapped_column(Boolean, default=False)
    turns_one_ear: Mapped[bool] = mapped_column(Boolean, default=False)
    asks_repetition: Mapped[bool] = mapped_column(Boolean, default=False)

    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    assessment: Mapped[Assessment] = relationship(back_populates="Hearing")


class SpeechLanguage(Base):
    __tablename__ = "speech_language"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    assessment_id: Mapped[int] = mapped_column(ForeignKey("assessments.id"), unique=True, nullable=False)

    names_objects: Mapped[bool] = mapped_column(Boolean, default=False)
    repeats_words: Mapped[bool] = mapped_column(Boolean, default=False)
    answers_simple_questions: Mapped[bool] = mapped_column(Boolean, default=False)
    describes_picture: Mapped[bool] = mapped_column(Boolean, default=False)

    audio_path: Mapped[str | None] = mapped_column(Text, nullable=True)

    vocabulary_clarity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sentence_length: Mapped[int | None] = mapped_column(Integer, nullable=True)
    pronunciation: Mapped[int | None] = mapped_column(Integer, nullable=True)
    confidence: Mapped[int | None] = mapped_column(Integer, nullable=True)

    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    assessment: Mapped[Assessment] = relationship(back_populates="Speech")


class MotorSkills(Base):
    __tablename__ = "motor_skills"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    assessment_id: Mapped[int] = mapped_column(ForeignKey("assessments.id"), unique=True, nullable=False)

    fine_drag_drop: Mapped[bool] = mapped_column(Boolean, default=False)
    fine_trace_line: Mapped[bool] = mapped_column(Boolean, default=False)
    fine_pick_place: Mapped[bool] = mapped_column(Boolean, default=False)

    gross_walk_straight: Mapped[bool] = mapped_column(Boolean, default=False)
    gross_jump_two_feet: Mapped[bool] = mapped_column(Boolean, default=False)
    gross_stand_one_foot_5s: Mapped[bool] = mapped_column(Boolean, default=False)

    hand_dominance_unclear: Mapped[bool] = mapped_column(Boolean, default=False)
    poor_balance: Mapped[bool] = mapped_column(Boolean, default=False)
    weak_grip_coordination: Mapped[bool] = mapped_column(Boolean, default=False)

    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    assessment: Mapped[Assessment] = relationship(back_populates="Motor")


class CognitiveSkills(Base):
    __tablename__ = "cognitive_skills"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    assessment_id: Mapped[int] = mapped_column(ForeignKey("assessments.id"), unique=True, nullable=False)

    completes_puzzles: Mapped[bool] = mapped_column(Boolean, default=False)
    matches_patterns: Mapped[bool] = mapped_column(Boolean, default=False)
    counts_objects: Mapped[bool] = mapped_column(Boolean, default=False)
    identifies_sequences: Mapped[bool] = mapped_column(Boolean, default=False)
    memory_game_recall: Mapped[bool] = mapped_column(Boolean, default=False)

    solves_faster_than_norm: Mapped[bool] = mapped_column(Boolean, default=False)
    advanced_counting_reasoning: Mapped[bool] = mapped_column(Boolean, default=False)
    high_curiosity: Mapped[bool] = mapped_column(Boolean, default=False)
    strong_memory: Mapped[bool] = mapped_column(Boolean, default=False)
    creative_responses: Mapped[bool] = mapped_column(Boolean, default=False)

    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    assessment: Mapped[Assessment] = relationship(back_populates="Cognitive")


class YesSometimesNo(str, enum.Enum):
    yes = "yes"
    sometimes = "sometimes"
    no = "no"


class CaregiverQuestionnaire(Base):
    __tablename__ = "caregiver_questionnaire"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    assessment_id: Mapped[int] = mapped_column(ForeignKey("assessments.id"), unique=True, nullable=False)

    speaks_in_sentences: Mapped[YesSometimesNo | None] = mapped_column(Enum(YesSometimesNo), nullable=True)
    understands_simple_instructions: Mapped[YesSometimesNo | None] = mapped_column(Enum(YesSometimesNo), nullable=True)

    known_vision_issues: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    known_hearing_issues: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    delays_noticed_earlier: Mapped[bool | None] = mapped_column(Boolean, nullable=True)

    concentrates_5_10_min: Mapped[YesSometimesNo | None] = mapped_column(Enum(YesSometimesNo), nullable=True)
    enjoys_puzzles_songs_stories: Mapped[YesSometimesNo | None] = mapped_column(Enum(YesSometimesNo), nullable=True)
    interacts_well_with_children: Mapped[YesSometimesNo | None] = mapped_column(Enum(YesSometimesNo), nullable=True)

    learns_songs_poems_quickly: Mapped[YesSometimesNo | None] = mapped_column(Enum(YesSometimesNo), nullable=True)
    recognizes_numbers_letters_patterns_early: Mapped[YesSometimesNo | None] = mapped_column(Enum(YesSometimesNo), nullable=True)
    interest_in_drawing_music_story: Mapped[YesSometimesNo | None] = mapped_column(Enum(YesSometimesNo), nullable=True)

    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    assessment: Mapped[Assessment] = relationship(back_populates="Caregiver")


class RecommendationType(str, enum.Enum):
    intervention = "intervention"
    enrichment = "enrichment"
    referral = "referral"


class Recommendation(Base):
    __tablename__ = "recommendations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    assessment_id: Mapped[int] = mapped_column(ForeignKey("assessments.id"), nullable=False)

    recommendation_type: Mapped[RecommendationType] = mapped_column(Enum(RecommendationType), nullable=False)
    domain: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    follow_up_months: Mapped[int | None] = mapped_column(Integer, nullable=True)

    assessment: Mapped[Assessment] = relationship(back_populates="Recommendations")
