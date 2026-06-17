from __future__ import annotations

from collections import Counter
from typing import Any

from pydantic import BaseModel, Field


class ParentSearchRequest(BaseModel):
    query: str
    child_age: str = "primary school"
    location: str = "Singapore"
    category: str = "enrichment"
    budget: str = "middle-class"
    goal: str = "confidence and curiosity"


class BusinessProfile(BaseModel):
    id: str
    name: str
    category: str
    location: str
    description: str
    strengths: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)
    price_band: str = "$$"
    age_range: str = "Primary"
    evidence: list[str] = Field(default_factory=list)


class ParentFeedbackEvent(BaseModel):
    business_name: str
    action: str
    reason: str | None = None
    query: str | None = None
    category: str | None = None
    location: str | None = None


SEED_BUSINESSES = [
    BusinessProfile(
        id="little-explorers-stem",
        name="Little Explorers STEM Club",
        category="STEM enrichment class",
        location="Tampines, Singapore",
        description="Hands-on science, coding and robotics workshops for curious primary school children.",
        strengths=["Tampines-based", "hands-on STEM", "trial classes", "small class sizes"],
        gaps=["needs more parent reviews mentioning age range", "publish clearer holiday camp schedule"],
        price_band="$$",
        age_range="7–12",
        evidence=["Parent testimonials", "Trial class offer", "Neighbourhood location"],
    ),
    BusinessProfile(
        id="brightminds-learning-hub",
        name="BrightMinds Learning Hub",
        category="primary tuition",
        location="Tampines, Singapore",
        description="Primary math and science tuition with exam confidence coaching and parent updates.",
        strengths=["PSLE focus", "parent progress updates", "near MRT"],
        gaps=["add teacher credentials", "add FAQ schema for stressed learners"],
        price_band="$$",
        age_range="P3–P6",
        evidence=["Progress updates", "Exam prep pages", "Google reviews"],
    ),
    BusinessProfile(
        id="playwise-toys",
        name="PlayWise Learning Toys",
        category="educational toys",
        location="Singapore",
        description="Curated Montessori, STEM and bilingual learning toys for preschool and lower primary children.",
        strengths=["age-filtered toys", "gift guides", "bilingual products"],
        gaps=["add product schema", "collect post-purchase learning outcome feedback"],
        price_band="$–$$",
        age_range="3–8",
        evidence=["Product guides", "Parent reviews", "Age filters"],
    ),
    BusinessProfile(
        id="saturday-kids",
        name="Saturday Kids",
        category="coding class",
        location="Singapore",
        description="Established coding and digital creativity programmes for children across Singapore.",
        strengths=["strong brand awareness", "coding curriculum", "holiday camps"],
        gaps=["premium pricing perception"],
        price_band="$$$",
        age_range="7–16",
        evidence=["Publisher mentions", "Course pages", "Camp pages"],
    ),
]


def recommend_for_parent(request: ParentSearchRequest) -> dict[str, Any]:
    query_text = " ".join(
        [request.query, request.category, request.location, request.child_age, request.budget, request.goal]
    ).casefold()
    scored: list[tuple[int, BusinessProfile, list[str]]] = []
    for business in SEED_BUSINESSES:
        haystack = " ".join(
            [business.name, business.category, business.location, business.description]
            + business.strengths
            + business.evidence
        ).casefold()
        score = 0
        reasons: list[str] = []
        for token in set(query_text.replace(",", " ").split()):
            if len(token) > 2 and token in haystack:
                score += 1
        if request.location.split(",")[0].casefold() in business.location.casefold():
            score += 4
            reasons.append(f"matches {request.location}")
        if request.category.casefold() in business.category.casefold() or business.category.casefold() in request.category.casefold():
            score += 4
            reasons.append(f"fits {request.category}")
        if any(word in haystack for word in ["trial", "reviews", "parent", "small", "mrt"]):
            score += 2
            reasons.append("has parent-friendly trust signals")
        if not reasons:
            reasons.append("broadly relevant to the parent query")
        scored.append((score, business, reasons))
    scored.sort(key=lambda item: item[0], reverse=True)
    return {
        "query": request.model_dump(),
        "recommendations": [
            {"business": business.model_dump(), "fit_score": score, "reasons": reasons}
            for score, business, reasons in scored[:3]
        ],
        "feedback_options": [
            "saved",
            "contacted",
            "too expensive",
            "too far",
            "not enough info",
            "not suitable for age",
            "looks promising",
        ],
    }


def summarize_parent_signals(events: list[ParentFeedbackEvent], business_name: str) -> dict[str, Any]:
    relevant = [event for event in events if event.business_name.casefold() == business_name.casefold()]
    actions = Counter(event.action for event in relevant)
    reasons = Counter(event.reason for event in relevant if event.reason)
    queries = Counter(event.query for event in relevant if event.query)
    positive = sum(actions.get(action, 0) for action in ["saved", "contacted", "looks promising"])
    negative = sum(actions.get(action, 0) for action in ["too expensive", "too far", "not enough info", "not suitable for age"])
    total = len(relevant)
    return {
        "total_parent_events": total,
        "positive_intent_events": positive,
        "objection_events": negative,
        "shortlist_rate": round(positive / total, 3) if total else 0.0,
        "top_actions": dict(actions.most_common()),
        "top_objections": dict(reasons.most_common(5)),
        "top_parent_queries": dict(queries.most_common(5)),
    }


def parent_signal_recommendations(summary: dict[str, Any]) -> list[dict[str, str]]:
    recs: list[dict[str, str]] = []
    objections = " ".join(summary.get("top_objections", {}).keys()).casefold()
    if "price" in objections or "expensive" in objections:
        recs.append(
            {
                "priority": "high",
                "area": "Price transparency",
                "action": "Publish trial pricing, monthly fee ranges and what is included so AI answers can address affordability concerns.",
                "rationale": "Parents are rejecting or hesitating because cost/value is unclear.",
            }
        )
    if "info" in objections:
        recs.append(
            {
                "priority": "high",
                "area": "Profile completeness",
                "action": "Add age range, class size, schedule, teacher credentials, trial availability and FAQs to the website and profile.",
                "rationale": "Parent feedback says the business lacks enough information to shortlist confidently.",
            }
        )
    if "far" in objections:
        recs.append(
            {
                "priority": "medium",
                "area": "Location clarity",
                "action": "Add MRT/bus directions, neighbourhood pages and service-area wording for nearby estates.",
                "rationale": "Convenience is a ranking and conversion factor for Singapore parents.",
            }
        )
    if not recs and summary.get("total_parent_events", 0):
        recs.append(
            {
                "priority": "medium",
                "area": "Parent proof",
                "action": "Turn positive parent interactions into review requests and testimonials that mention child age, goal and outcome.",
                "rationale": "Positive shortlist signals should become public evidence that AI systems can retrieve.",
            }
        )
    return recs
