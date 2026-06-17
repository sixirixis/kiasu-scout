from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

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

STATIC_DIR = Path(__file__).parent / "static"

app = FastAPI(
    title="KiasuScout",
    description=(
        "AI answer visibility MVP for Singapore/SEA children activities, tuition, "
        "enrichment, and educational toy businesses."
    ),
    version="0.1.0",
)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class PromptRequest(BaseModel):
    category: str
    location: str = "Singapore"
    persona: str | None = None
    child_age: str | None = None
    budget: str | None = "middle-class"
    limit: int = 12


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


@app.post("/api/report")
def report(payload: dict[str, Any]) -> dict[str, Any]:
    parsed = VisibilityInput.model_validate(payload)
    return create_report(parsed).model_dump()


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


def main() -> None:
    import uvicorn

    uvicorn.run("answerspot_sg_mcp.web:app", host="127.0.0.1", port=8000, reload=False)


if __name__ == "__main__":
    main()
