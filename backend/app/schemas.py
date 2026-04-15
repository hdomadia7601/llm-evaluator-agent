from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from .prompts import PROMPT_VERSION

class EvaluateRequest(BaseModel):
    query: str = Field(min_length=3, max_length=4000)


class MetricScores(BaseModel):
    a: int = Field(ge=1, le=10)
    b: int = Field(ge=1, le=10)


class EvaluationResult(BaseModel):
    clarity_scores: MetricScores
    completeness_scores: MetricScores
    correctness_scores: MetricScores
    winner: Literal["A", "B"]
    reasoning: str = Field(min_length=5, max_length=800)


class EvaluateResponse(BaseModel):
    query: str
    response_a: str
    response_b: str
    evaluation: EvaluationResult
    model_a: str
    model_b: str
    prompt_version: str = PROMPT_VERSION
    user_feedback: Literal["up", "down"] | None = None
    timestamp: datetime


class FeedbackRequest(BaseModel):
    query: str
    response_a: str
    response_b: str
    evaluation: EvaluationResult
    feedback: Literal["up", "down"] = "up"
    prompt_version: str = PROMPT_VERSION


class FeedbackRecord(FeedbackRequest):
    user_feedback: Literal["up", "down"]
    timestamp: datetime


class AnalyticsResponse(BaseModel):
    total_queries: int
    most_common_queries: list[dict[str, int | str]]
    average_evaluation_scores: dict[str, dict[str, float]]
    winner_distribution: dict[str, int]
    win_rate_percentage: dict[str, float]
