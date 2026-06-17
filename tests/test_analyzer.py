from answerspot_sg_mcp.analyzer import analyze_visibility, create_report
from answerspot_sg_mcp.schemas import VisibilityInput


def sample_payload():
    return VisibilityInput.model_validate(
        {
            "business_name": "BrightMinds Learning Hub",
            "category": "primary tuition",
            "location": "Tampines, Singapore",
            "competitors": ["The Learning Lab", "Mind Stretcher", "Kumon"],
            "answers": [
                {
                    "platform": "ChatGPT",
                    "prompt": "Best primary math tuition in Tampines?",
                    "answer_text": (
                        "1. The Learning Lab is well known. 2. BrightMinds Learning Hub "
                        "is convenient for Tampines families. 3. Kumon has broad coverage."
                    ),
                },
                {
                    "platform": "Perplexity",
                    "prompt": "Recommend primary tuition near Tampines",
                    "answer_text": (
                        "Parents often compare Mind Stretcher, The Learning Lab and Kumon "
                        "for structured programmes."
                    ),
                },
            ],
        }
    )


def test_analyze_visibility_scores_mentions_and_competitors():
    score = analyze_visibility(sample_payload())
    assert score.total_answers == 2
    assert score.answers_with_business == 1
    assert score.answer_share == 0.5
    assert score.competitor_mentions["The Learning Lab"] == 2
    assert score.platform_breakdown["ChatGPT"]["mentions"] == 1


def test_create_report_contains_sector_recommendations():
    report = create_report(sample_payload())
    assert report.business_name == "BrightMinds Learning Hub"
    areas = [r.area for r in report.recommendations]
    assert "Parent reviews" in areas
    assert any("Singapore" in r.action or "SEA" in r.action for r in report.recommendations)
