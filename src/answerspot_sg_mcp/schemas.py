from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class CapturedAnswer(BaseModel):
    platform: str = Field(..., description="AI platform, e.g. ChatGPT, Gemini, Perplexity")
    prompt: str
    answer_text: str
    captured_at: str | None = None
    location_context: str | None = None
    raw_citations: list[str] = Field(default_factory=list)


class VisibilityInput(BaseModel):
    business_name: str
    category: str
    location: str = "Singapore"
    competitors: list[str] = Field(default_factory=list)
    answers: list[CapturedAnswer]


class Mention(BaseModel):
    name: str
    platform: str
    prompt: str
    position: int | None = None
    evidence: str


class VisibilityScore(BaseModel):
    business_name: str
    total_answers: int
    answers_with_business: int
    answer_share: float
    average_position: float | None
    competitor_mentions: dict[str, int]
    platform_breakdown: dict[str, dict[str, Any]]
    mentions: list[Mention]
    generated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")


class Recommendation(BaseModel):
    priority: str
    area: str
    action: str
    rationale: str


class VisibilityReport(BaseModel):
    business_name: str
    category: str
    location: str
    executive_summary: str
    score: VisibilityScore
    recommendations: list[Recommendation]
    methodology: list[str]
