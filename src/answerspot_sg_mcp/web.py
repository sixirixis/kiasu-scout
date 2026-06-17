from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .analyzer import create_report
from .prompts import (
    PARENT_PERSONAS,
    PLATFORMS,
    SUPPORTED_LOCATIONS,
    SUPPORTED_SEGMENTS,
    flatten_categories,
    generate_prompt_pack,
)
from .schemas import VisibilityInput
from .signals import (
    ParentFeedbackEvent,
    ParentSearchRequest,
    SEED_BUSINESSES,
    parent_signal_recommendations,
    recommend_for_parent,
    summarize_parent_signals,
)

STATIC_DIR = Path(__file__).parent / "static"
PARENT_EVENTS: list[ParentFeedbackEvent] = []

app = FastAPI(
    title="KiasuScout",
    description=(
        "AI answer visibility MVP for Singapore/SEA children activities, tuition, "
        "enrichment, and educational toy businesses."
    ),
    version="0.2.0",
)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class PromptRequest(BaseModel):
    category: str
    location: str = "Singapore"
    persona: str | None = None
    child_age: str | None = None
    budget: str | None = "middle-class"
    limit: int = 12


class CombinedReportRequest(BaseModel):
    visibility: dict[str, Any]
    parent_events: list[ParentFeedbackEvent] = Field(default_factory=list)


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "app": "KiasuScout"}


@app.get("/api/segments")
def segments() -> dict[str, Any]:
    return {
        "brand": "KiasuScout",
        "tagline": "Know where parents' AI assistants send them.",
        "locations": SUPPORTED_LOCATIONS,
        "segments": SUPPORTED_SEGMENTS,
        "categories": flatten_categories(),
        "parent_personas": PARENT_PERSONAS,
        "platforms": PLATFORMS,
        "seed_businesses": [business.model_dump() for business in SEED_BUSINESSES],
    }


@app.post("/api/prompts")
def prompts(request: PromptRequest) -> dict[str, Any]:
    generated = generate_prompt_pack(
        request.category,
        request.location,
        request.persona,
        request.child_age,
        request.budget,
        request.limit,
    )
    return {"prompts": generated}


@app.post("/api/parent-search")
def parent_search(request: ParentSearchRequest) -> dict[str, Any]:
    return recommend_for_parent(request)


@app.post("/api/feedback")
def feedback(event: ParentFeedbackEvent) -> dict[str, Any]:
    PARENT_EVENTS.append(event)
    return {"saved": True, "event_count": len(PARENT_EVENTS), "event": event.model_dump()}


@app.get("/api/feedback")
def feedback_events() -> dict[str, Any]:
    return {"events": [event.model_dump() for event in PARENT_EVENTS]}


@app.post("/api/report")
def report(payload: dict[str, Any]) -> dict[str, Any]:
    parsed = VisibilityInput.model_validate(payload)
    return create_report(parsed).model_dump()


@app.post("/api/combined-report")
def combined_report(payload: CombinedReportRequest) -> dict[str, Any]:
    parsed = VisibilityInput.model_validate(payload.visibility)
    base_report = create_report(parsed).model_dump()
    events = payload.parent_events or PARENT_EVENTS
    parent_summary = summarize_parent_signals(events, parsed.business_name)
    extra_recs = parent_signal_recommendations(parent_summary)
    base_report["parent_signals"] = parent_summary
    base_report["recommendations"] = extra_recs + base_report["recommendations"]
    base_report["executive_summary"] = (
        base_report["executive_summary"]
        + " Parent interaction signals are included to connect AEO visibility with what families "
        "actually ask, shortlist and reject."
    )
    return base_report


@app.get("/api/sample")
def sample_payload() -> dict[str, Any]:
    return {
        "business_name": "Little Explorers STEM Club",
        "category": "STEM enrichment class",
        "location": "Tampines, Singapore",
        "competitors": ["The Learning Lab", "Saturday Kids", "Nullspace Robotics"],
        "answers": [
            {
                "platform": "ChatGPT",
                "prompt": "What are the best STEM enrichment classes in Tampines for a primary school child?",
                "answer_text": (
                    "Parents often compare 1. Saturday Kids for coding workshops, "
                    "2. Nullspace Robotics for robotics pathways, and 3. Little Explorers "
                    "STEM Club for convenient Tampines-based hands-on science classes."
                ),
            },
            {
                "platform": "Perplexity",
                "prompt": "Recommend robotics or coding classes for kids near Tampines Singapore.",
                "answer_text": (
                    "Saturday Kids and Nullspace Robotics are commonly mentioned options. "
                    "Check recent parent reviews, age suitability and class locations before booking."
                ),
            },
        ],
    }


@app.get("/api/sample-parent-events")
def sample_parent_events() -> dict[str, Any]:
    events = [
        ParentFeedbackEvent(
            business_name="Little Explorers STEM Club",
            action="saved",
            reason="looks convenient and hands-on",
            query="STEM classes for an 8-year-old near Tampines",
            category="STEM enrichment class",
            location="Tampines, Singapore",
        ),
        ParentFeedbackEvent(
            business_name="Little Explorers STEM Club",
            action="not enough info",
            reason="not enough info about trial price and class schedule",
            query="coding class with trial lesson near Tampines",
            category="STEM enrichment class",
            location="Tampines, Singapore",
        ),
        ParentFeedbackEvent(
            business_name="Little Explorers STEM Club",
            action="contacted",
            reason="small class size and nearby",
            query="robotics class for primary school child",
            category="STEM enrichment class",
            location="Tampines, Singapore",
        ),
    ]
    return {"events": [event.model_dump() for event in events]}


def main() -> None:
    import uvicorn

    uvicorn.run("answerspot_sg_mcp.web:app", host="127.0.0.1", port=8000, reload=False)


if __name__ == "__main__":
    main()
