from __future__ import annotations

import re
from collections import Counter, defaultdict
from statistics import mean
from typing import Any

from .schemas import (
    Mention,
    Recommendation,
    VisibilityInput,
    VisibilityReport,
    VisibilityScore,
)

SECTOR_FIXES = [
    Recommendation(
        priority="high",
        area="Google Business Profile and Maps",
        action=(
            "Ensure the business has the most specific categories, complete services, "
            "opening hours, photos of child-safe facilities, and recent posts for "
            "classes/camps/products."
        ),
        rationale=(
            "AI systems often rely on local business data and review-rich profiles when "
            "recommending parent-facing local options."
        ),
    ),
    Recommendation(
        priority="high",
        area="Parent reviews",
        action=(
            "Set a monthly review target and ask parents to mention child age, programme type, "
            "neighbourhood, learning outcome, teacher quality, and safety."
        ),
        rationale=(
            "For tuition, enrichment and toys, parent trust signals are often more persuasive "
            "than generic star ratings."
        ),
    ),
    Recommendation(
        priority="high",
        area="Local citations and marketplaces",
        action=(
            "Claim and standardise listings on relevant Singapore/SEA sources such as Google "
            "Maps, Facebook, Instagram, Yelp where relevant, Sassy Mama, HoneyKids Asia, "
            "Little Day Out, KiasuParents, Skoolopedia, parent directories, shopping "
            "marketplaces, and category-specific portals."
        ),
        rationale=(
            "LLM answers frequently cite or infer from third-party lists, directories, forums "
            "and publisher roundups."
        ),
    ),
    Recommendation(
        priority="medium",
        area="Structured data",
        action=(
            "Add LocalBusiness, Course, Product, Review, FAQPage and Event schema where "
            "applicable, including age range, location, price range, schedule and curriculum details."
        ),
        rationale="Structured data helps AI/search systems understand what the business offers and who it serves.",
    ),
    Recommendation(
        priority="medium",
        area="Service/location pages",
        action=(
            "Create pages matching parent prompts, e.g. 'Primary Math Tuition in Tampines', "
            "'STEM holiday camp Singapore', or 'Montessori toys for preschoolers in Singapore'."
        ),
        rationale="Prompt-matched pages improve retrievability for high-intent AI answers.",
    ),
    Recommendation(
        priority="medium",
        area="Evidence of outcomes and safety",
        action=(
            "Publish teacher credentials, curriculum samples, child safety policies, class size, "
            "trial class details, refund policy, and parent testimonials."
        ),
        rationale="Middle-class parents compare trust, convenience, safety and outcomes before price alone.",
    ),
]


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.casefold()).strip()


def _find_sentence(text: str, name: str) -> str:
    sentences = re.split(r"(?<=[.!?])\s+|\n+", text)
    n_name = normalize(name)
    for sentence in sentences:
        if n_name in normalize(sentence):
            return sentence.strip()[:500]
    idx = normalize(text).find(n_name)
    if idx == -1:
        return ""
    start = max(0, idx - 160)
    end = min(len(text), idx + len(name) + 240)
    return text[start:end].strip()


def _estimate_position(answer_text: str, name: str) -> int | None:
    """Estimate list position from answer text using nearby numbering or mention order."""
    n_text = normalize(answer_text)
    n_name = normalize(name)
    idx = n_text.find(n_name)
    if idx < 0:
        return None

    before = n_text[max(0, idx - 80) : idx]
    numbered = re.search(r"(?:^|[\n\s])([1-9])\s*[\).:-]\s*$", before)
    if numbered:
        return int(numbered.group(1))

    prior_lines = answer_text[:idx].splitlines()
    bullet_count = sum(
        1 for line in prior_lines if re.match(r"\s*(?:[-*•]|[1-9][\).:-])\s+", line)
    )
    if bullet_count:
        return bullet_count + 1
    return None


def analyze_visibility(payload: VisibilityInput) -> VisibilityScore:
    business = payload.business_name
    competitors = payload.competitors
    total = len(payload.answers)
    business_mentions: list[Mention] = []
    positions: list[int] = []
    comp_counts: Counter[str] = Counter()
    platform_stats: dict[str, dict[str, int]] = defaultdict(lambda: {"answers": 0, "mentions": 0})

    for answer in payload.answers:
        platform_stats[answer.platform]["answers"] += 1
        answer_norm = normalize(answer.answer_text)

        if normalize(business) in answer_norm:
            platform_stats[answer.platform]["mentions"] += 1
            pos = _estimate_position(answer.answer_text, business)
            if pos is not None:
                positions.append(pos)
            business_mentions.append(
                Mention(
                    name=business,
                    platform=answer.platform,
                    prompt=answer.prompt,
                    position=pos,
                    evidence=_find_sentence(answer.answer_text, business),
                )
            )

        for competitor in competitors:
            if normalize(competitor) in answer_norm:
                comp_counts[competitor] += 1

    breakdown: dict[str, dict[str, Any]] = {
        platform: {
            "answers": stats["answers"],
            "mentions": stats["mentions"],
            "answer_share": round(stats["mentions"] / stats["answers"], 3)
            if stats["answers"]
            else 0.0,
        }
        for platform, stats in sorted(platform_stats.items())
    }

    return VisibilityScore(
        business_name=business,
        total_answers=total,
        answers_with_business=len(business_mentions),
        answer_share=round(len(business_mentions) / total, 3) if total else 0.0,
        average_position=round(mean(positions), 2) if positions else None,
        competitor_mentions=dict(comp_counts.most_common()),
        platform_breakdown=breakdown,
        mentions=business_mentions,
    )


def recommend_fixes(score: VisibilityScore, category: str, location: str) -> list[Recommendation]:
    fixes = list(SECTOR_FIXES)
    if score.answer_share == 0:
        fixes.insert(
            0,
            Recommendation(
                priority="urgent",
                area="AI answer invisibility",
                action=(
                    f"Run a source-gap audit for {score.business_name} against the top-mentioned "
                    f"competitors, then create or update the pages/listings most likely to be "
                    f"retrieved for '{category}' in {location}."
                ),
                rationale=(
                    "The business was not mentioned in any captured answer, so the first goal is "
                    "entity recognition and retrievable third-party evidence."
                ),
            ),
        )
    elif score.answer_share < 0.34:
        fixes.insert(
            0,
            Recommendation(
                priority="high",
                area="Low answer share",
                action=(
                    "Prioritise prompts and platforms where the business is missing; compare "
                    "cited sources against competitors and close the most repeated gaps."
                ),
                rationale="The business appears occasionally but does not yet have reliable answer-share.",
            ),
        )
    if score.competitor_mentions:
        top_competitor = next(iter(score.competitor_mentions))
        fixes.append(
            Recommendation(
                priority="medium",
                area="Competitor citation gap",
                action=(
                    f"Review why {top_competitor} is mentioned more often: sources, review "
                    "language, category pages, parent forums, and PR/listicle presence."
                ),
                rationale="Competitor co-mentions reveal where AI systems are likely finding trusted local evidence.",
            )
        )
    return fixes[:8]


def create_report(payload: VisibilityInput) -> VisibilityReport:
    score = analyze_visibility(payload)
    fixes = recommend_fixes(score, payload.category, payload.location)
    if score.answer_share == 0:
        summary = (
            f"{payload.business_name} was not recommended in the captured AI answers for "
            f"{payload.category} in {payload.location}. Competitor/source gap work should be "
            "prioritised before rank optimisation."
        )
    elif score.answer_share < 0.5:
        summary = (
            f"{payload.business_name} has partial AI answer visibility ({score.answer_share:.0%} "
            f"answer share) for {payload.category} in {payload.location}, with room to improve "
            "consistency across prompts and platforms."
        )
    else:
        summary = (
            f"{payload.business_name} has meaningful AI answer visibility ({score.answer_share:.0%} "
            f"answer share) for {payload.category} in {payload.location}; next steps should focus "
            "on holding position and expanding prompt coverage."
        )

    methodology = [
        "This MVP analyses captured AI answer text supplied by the user or an approved collector; it does not scrape platforms.",
        "Answer share is the fraction of captured answers that mention the target business by name.",
        "Position is estimated from explicit list numbering or bullet order when present; unstructured mentions may not have a position.",
        "Recommendations are prioritised for Singapore/SEA parent-facing education, enrichment, activity and educational toy businesses.",
    ]
    return VisibilityReport(
        business_name=payload.business_name,
        category=payload.category,
        location=payload.location,
        executive_summary=summary,
        score=score,
        recommendations=fixes,
        methodology=methodology,
    )
