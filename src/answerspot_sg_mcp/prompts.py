from __future__ import annotations

SUPPORTED_LOCATIONS = [
    "Singapore",
    "Tampines",
    "Woodlands",
    "Jurong East",
    "Bukit Timah",
    "Punggol",
    "Serangoon",
    "Ang Mo Kio",
    "Queenstown",
    "Kuala Lumpur",
    "Petaling Jaya",
    "Johor Bahru",
    "Bangkok",
    "Jakarta",
]

SUPPORTED_SEGMENTS = {
    "tuition": ["primary tuition", "secondary tuition", "PSLE prep", "O-Level prep", "IB tuition"],
    "enrichment": ["coding class", "robotics class", "art class", "music class", "speech and drama", "chinese enrichment"],
    "activities": ["holiday camp", "weekend activity", "indoor playground", "STEM workshop", "sports class"],
    "toys": ["educational toys", "STEM toys", "montessori toys", "learning games", "kids books"],
}

PARENT_PERSONAS = [
    "middle-class parent comparing value and outcomes",
    "busy working parent seeking convenient locations and schedules",
    "parent of a preschool child looking for play-based learning",
    "parent of a primary school child preparing for PSLE",
    "parent seeking bilingual English/Chinese development",
    "expat parent new to Singapore",
]

PLATFORMS = ["ChatGPT", "Gemini", "Perplexity", "Google AI Overviews", "Claude", "Copilot"]


def flatten_categories() -> list[str]:
    return [category for values in SUPPORTED_SEGMENTS.values() for category in values]


def generate_prompt_pack(
    category: str,
    location: str = "Singapore",
    persona: str | None = None,
    child_age: str | None = None,
    budget: str | None = "middle-class",
    limit: int = 12,
) -> list[str]:
    """Generate parent-oriented prompts for local AI visibility checks."""
    persona_text = persona or "middle-class parent"
    child_text = f" for a {child_age}" if child_age else ""
    budget_text = f" with a {budget} budget" if budget else ""
    base = category.strip()
    loc = location.strip()

    prompts = [
        f"What are the best {base} options in {loc}{child_text}{budget_text}?",
        f"Recommend 3 trusted {base} providers near {loc}{child_text}.",
        f"As a {persona_text}, which {base} businesses in {loc} should I compare?",
        f"Which {base} centres in {loc} have strong reviews from parents?",
        f"What are affordable but high-quality {base} choices in {loc}{child_text}?",
        f"Which {base} provider in {loc} is best for convenience, outcomes and parent reviews?",
        f"Compare the top {base} businesses around {loc} for a Singapore parent.",
        f"Where can I find reputable {base} in {loc} that parents recommend?",
        f"What should I choose for {base} in {loc} if I care about safety, learning quality and value?",
        f"List {base} businesses in {loc} that are suitable for children and explain why.",
        f"Which {base} options in {loc} are mentioned most often online by Singapore parents?",
        f"What are the best-rated {base} options near MRT-accessible areas in {loc}?",
        f"Which {base} businesses in {loc} are good for first-time parents to try?",
        f"Give me a shortlist of {base} providers in {loc}, including pros, cons and who each suits.",
    ]
    return prompts[: max(1, min(limit, len(prompts)))]
