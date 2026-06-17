from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from .analyzer import analyze_visibility, create_report, recommend_fixes
from .prompts import (
    PARENT_PERSONAS,
    PLATFORMS,
    SUPPORTED_LOCATIONS,
    SUPPORTED_SEGMENTS,
    flatten_categories,
    generate_prompt_pack as _generate_prompt_pack,
)
from .schemas import VisibilityInput, VisibilityScore

mcp = FastMCP("answerspot-sg-mcp")


@mcp.tool()
def list_supported_segments() -> dict[str, Any]:
    """List supported SEA/Singapore locations, categories, personas and AI platforms."""
    return {
        "locations": SUPPORTED_LOCATIONS,
        "segments": SUPPORTED_SEGMENTS,
        "categories": flatten_categories(),
        "parent_personas": PARENT_PERSONAS,
        "platforms": PLATFORMS,
    }


@mcp.tool()
def generate_prompt_pack(
    category: str,
    location: str = "Singapore",
    persona: str | None = None,
    child_age: str | None = None,
    budget: str | None = "middle-class",
    limit: int = 12,
) -> list[str]:
    """Generate parent-oriented AI visibility prompts for children/education businesses."""
    return _generate_prompt_pack(category, location, persona, child_age, budget, limit)


@mcp.tool()
def analyze_answer_visibility(payload: dict[str, Any]) -> dict[str, Any]:
    """Score whether a business appears in captured LLM answers and which competitors appear."""
    parsed = VisibilityInput.model_validate(payload)
    return analyze_visibility(parsed).model_dump()


@mcp.tool()
def recommend_visibility_fixes(
    score_payload: dict[str, Any], category: str, location: str = "Singapore"
) -> list[dict[str, Any]]:
    """Recommend practical fixes for SG/SEA children education/activity/toy AI visibility gaps."""
    score = VisibilityScore.model_validate(score_payload)
    return [rec.model_dump() for rec in recommend_fixes(score, category, location)]


@mcp.tool()
def create_visibility_report(payload: dict[str, Any]) -> dict[str, Any]:
    """Create a client-ready AI answer visibility report from captured LLM answers."""
    parsed = VisibilityInput.model_validate(payload)
    return create_report(parsed).model_dump()


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
