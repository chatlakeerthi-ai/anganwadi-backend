from __future__ import annotations

from dataclasses import dataclass

from .models import Classification, RecommendationType


def _clamp_0_100(x: float) -> int:
    return max(0, min(100, int(round(x))))


@dataclass
class DomainScoreResult:
    score: int
    risk_flags: int = 0
    high_potential_flags: int = 0


def score_vision(
    *,
    identifies_objects: bool,
    matches_shapes: bool,
    identifies_sizes: bool,
    identifies_colors: bool,
    squints_or_close: bool,
    difficulty_shapes_colors: bool,
    avoids_visual_tasks: bool,
) -> DomainScoreResult:
    tasks = [identifies_objects, matches_shapes, identifies_sizes, identifies_colors]
    observations = [squints_or_close, difficulty_shapes_colors, avoids_visual_tasks]

    task_score = (sum(tasks) / len(tasks)) * 100
    penalty = sum(observations) * 10
    score = _clamp_0_100(task_score - penalty)

    risk_flags = 1 if score < 60 else 0
    return DomainScoreResult(score=score, risk_flags=risk_flags)


def score_hearing(
    *,
    responds_to_soft_name_call: bool,
    identifies_animal_sounds: bool,
    follows_one_step_command: bool,
    follows_two_step_command: bool,
    delayed_response: bool,
    turns_one_ear: bool,
    asks_repetition: bool,
) -> DomainScoreResult:
    tasks = [
        responds_to_soft_name_call,
        identifies_animal_sounds,
        follows_one_step_command,
        follows_two_step_command,
    ]
    observations = [delayed_response, turns_one_ear, asks_repetition]

    task_score = (sum(tasks) / len(tasks)) * 100
    penalty = sum(observations) * 10
    score = _clamp_0_100(task_score - penalty)

    risk_flags = 1 if score < 60 else 0
    return DomainScoreResult(score=score, risk_flags=risk_flags)


def score_speech(
    *,
    names_objects: bool,
    repeats_words: bool,
    answers_simple_questions: bool,
    describes_picture: bool,
    vocabulary_clarity: int | None,
    sentence_length: int | None,
    pronunciation: int | None,
    confidence: int | None,
) -> DomainScoreResult:
    tasks = [names_objects, repeats_words, answers_simple_questions, describes_picture]
    task_score = (sum(tasks) / len(tasks)) * 100

    # If worker provided manual/AI sub-scores, average them in.
    subs = [v for v in [vocabulary_clarity, sentence_length, pronunciation, confidence] if v is not None]
    sub_score = sum(subs) / len(subs) if subs else None

    combined = task_score if sub_score is None else (task_score * 0.5 + sub_score * 0.5)
    score = _clamp_0_100(combined)

    risk_flags = 1 if score < 60 else 0
    high_flags = 1 if score >= 85 else 0
    return DomainScoreResult(score=score, risk_flags=risk_flags, high_potential_flags=high_flags)


def score_motor(
    *,
    fine_drag_drop: bool,
    fine_trace_line: bool,
    fine_pick_place: bool,
    gross_walk_straight: bool,
    gross_jump_two_feet: bool,
    gross_stand_one_foot_5s: bool,
    hand_dominance_unclear: bool,
    poor_balance: bool,
    weak_grip_coordination: bool,
) -> DomainScoreResult:
    fine = [fine_drag_drop, fine_trace_line, fine_pick_place]
    gross = [gross_walk_straight, gross_jump_two_feet, gross_stand_one_foot_5s]
    tasks = fine + gross
    observations = [hand_dominance_unclear, poor_balance, weak_grip_coordination]

    task_score = (sum(tasks) / len(tasks)) * 100
    penalty = sum(observations) * 10
    score = _clamp_0_100(task_score - penalty)

    risk_flags = 1 if score < 60 else 0
    high_flags = 1 if score >= 85 else 0
    return DomainScoreResult(score=score, risk_flags=risk_flags, high_potential_flags=high_flags)


def score_cognitive(
    *,
    completes_puzzles: bool,
    matches_patterns: bool,
    counts_objects: bool,
    identifies_sequences: bool,
    memory_game_recall: bool,
    solves_faster_than_norm: bool,
    advanced_counting_reasoning: bool,
    high_curiosity: bool,
    strong_memory: bool,
    creative_responses: bool,
) -> DomainScoreResult:
    tasks = [
        completes_puzzles,
        matches_patterns,
        counts_objects,
        identifies_sequences,
        memory_game_recall,
    ]
    indicators = [
        solves_faster_than_norm,
        advanced_counting_reasoning,
        high_curiosity,
        strong_memory,
        creative_responses,
    ]

    task_score = (sum(tasks) / len(tasks)) * 100
    bonus = sum(indicators) * 3
    score = _clamp_0_100(task_score + bonus)

    risk_flags = 1 if score < 60 else 0
    high_flags = 1 if score >= 85 else 0
    return DomainScoreResult(score=score, risk_flags=risk_flags, high_potential_flags=high_flags)


def composite_score(*, vision: int | None, hearing: int | None, speech: int | None, motor: int | None, cognitive: int | None) -> float | None:
    parts = {"vision": vision, "hearing": hearing, "speech": speech, "motor": motor, "cognitive": cognitive}
    if any(v is None for v in parts.values()):
        return None

    v = float(vision)
    h = float(hearing)
    s = float(speech)
    m = float(motor)
    c = float(cognitive)

    return round(v * 0.15 + h * 0.15 + s * 0.25 + m * 0.20 + c * 0.25, 2)


def classify(*, domain_scores: dict[str, int | None], risk_flags_total: int, high_flags_total: int) -> Classification | None:
    if any(domain_scores.get(k) is None for k in ["vision", "hearing", "speech", "motor", "cognitive"]):
        return None

    scores = [domain_scores["vision"], domain_scores["hearing"], domain_scores["speech"], domain_scores["motor"], domain_scores["cognitive"]]

    if risk_flags_total >= 1 or any((s or 0) < 60 for s in scores):
        return Classification.at_risk

    if high_flags_total >= 2 and sum(1 for s in scores if (s or 0) >= 85) >= 2:
        return Classification.high_potential

    return Classification.low_risk


def recommendations_for(
    *,
    classification: Classification | None,
    domain_scores: dict[str, int | None],
) -> list[dict]:
    recs: list[dict] = []

    if classification is None:
        return recs

    if classification == Classification.at_risk:
        # Basic interventions per domain below threshold
        for domain, score in domain_scores.items():
            if score is not None and score < 60:
                recs.append(
                    {
                        "recommendation_type": RecommendationType.intervention,
                        "domain": domain,
                        "description": f"Provide targeted activities for {domain} for 10 minutes daily; repeat assessment in 3 months.",
                        "follow_up_months": 3,
                    }
                )
        if not recs:
            recs.append(
                {
                    "recommendation_type": RecommendationType.intervention,
                    "domain": "general",
                    "description": "Monitor development and repeat screening in 3 months.",
                    "follow_up_months": 3,
                }
            )

    if classification == Classification.high_potential:
        recs.append(
            {
                "recommendation_type": RecommendationType.enrichment,
                "domain": "cognitive",
                "description": "Introduce enrichment activities: puzzles, pattern games, early numeracy, storytelling, and creative play; reassess in 6 months.",
                "follow_up_months": 6,
            }
        )

    if classification == Classification.low_risk:
        recs.append(
            {
                "recommendation_type": RecommendationType.intervention,
                "domain": "general",
                "description": "Continue age-appropriate play-based learning and monitor routinely; reassess in 6 months.",
                "follow_up_months": 6,
            }
        )

    return recs
