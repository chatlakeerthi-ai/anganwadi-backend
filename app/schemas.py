from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class ChildCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    age_months: int = Field(ge=0, le=72)
    guardian_name: str | None = None
    guardian_phone: str | None = None
    consent_obtained: bool = False


class ChildOut(BaseModel):
    id: int
    name: str
    age_months: int
    guardian_name: str | None
    guardian_phone: str | None
    consent_obtained: bool
    created_at: datetime


class AssessmentCreate(BaseModel):
    child_id: int


class AssessmentOut(BaseModel):
    id: int
    child_id: int
    status: str
    vision_score: int | None
    hearing_score: int | None
    speech_score: int | None
    motor_score: int | None
    cognitive_score: int | None
    composite_score: float | None
    classification: str | None
    followup_months: int | None
    created_at: datetime
    completed_at: datetime | None


class VisionIn(BaseModel):
    identifies_objects: bool = False
    matches_shapes: bool = False
    identifies_sizes: bool = False
    identifies_colors: bool = False
    squints_or_close: bool = False
    difficulty_shapes_colors: bool = False
    avoids_visual_tasks: bool = False
    notes: str | None = None


class HearingIn(BaseModel):
    responds_to_soft_name_call: bool = False
    identifies_animal_sounds: bool = False
    follows_one_step_command: bool = False
    follows_two_step_command: bool = False
    delayed_response: bool = False
    turns_one_ear: bool = False
    asks_repetition: bool = False
    notes: str | None = None


class SpeechIn(BaseModel):
    names_objects: bool = False
    repeats_words: bool = False
    answers_simple_questions: bool = False
    describes_picture: bool = False
    vocabulary_clarity: int | None = Field(default=None, ge=0, le=100)
    sentence_length: int | None = Field(default=None, ge=0, le=100)
    pronunciation: int | None = Field(default=None, ge=0, le=100)
    confidence: int | None = Field(default=None, ge=0, le=100)
    notes: str | None = None


class MotorIn(BaseModel):
    fine_drag_drop: bool = False
    fine_trace_line: bool = False
    fine_pick_place: bool = False
    gross_walk_straight: bool = False
    gross_jump_two_feet: bool = False
    gross_stand_one_foot_5s: bool = False
    hand_dominance_unclear: bool = False
    poor_balance: bool = False
    weak_grip_coordination: bool = False
    notes: str | None = None


class CognitiveIn(BaseModel):
    completes_puzzles: bool = False
    matches_patterns: bool = False
    counts_objects: bool = False
    identifies_sequences: bool = False
    memory_game_recall: bool = False
    solves_faster_than_norm: bool = False
    advanced_counting_reasoning: bool = False
    high_curiosity: bool = False
    strong_memory: bool = False
    creative_responses: bool = False
    notes: str | None = None


YesSometimesNo = Literal["yes", "sometimes", "no"]


class CaregiverIn(BaseModel):
    speaks_in_sentences: YesSometimesNo | None = None
    understands_simple_instructions: YesSometimesNo | None = None
    known_vision_issues: bool | None = None
    known_hearing_issues: bool | None = None
    delays_noticed_earlier: bool | None = None
    concentrates_5_10_min: YesSometimesNo | None = None
    enjoys_puzzles_songs_stories: YesSometimesNo | None = None
    interacts_well_with_children: YesSometimesNo | None = None
    learns_songs_poems_quickly: YesSometimesNo | None = None
    recognizes_numbers_letters_patterns_early: YesSometimesNo | None = None
    interest_in_drawing_music_story: YesSometimesNo | None = None
    notes: str | None = None


class RecommendationOut(BaseModel):
    recommendation_type: str
    domain: str
    description: str
    follow_up_months: int | None


class AssessmentReportOut(BaseModel):
    assessment: AssessmentOut
    child: ChildOut
    domain_scores: dict[str, int | None]
    composite_score: float | None
    classification: str | None
    recommendations: list[RecommendationOut]
