from fastapi.testclient import TestClient

from answerspot_sg_mcp.web import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "app": "KiasuScout"}


def test_index_loads_parent_and_business_positioning():
    response = client.get("/")
    assert response.status_code == 200
    assert "KiasuScout" in response.text
    assert "Parent discovery" in response.text
    assert "Business AEO" in response.text


def test_prompt_endpoint():
    response = client.post(
        "/api/prompts",
        json={"category": "primary tuition", "location": "Tampines, Singapore", "limit": 3},
    )
    assert response.status_code == 200
    prompts = response.json()["prompts"]
    assert len(prompts) == 3
    assert "Tampines" in prompts[0]


def test_parent_search_endpoint_returns_recommendations():
    response = client.post(
        "/api/parent-search",
        json={
            "query": "robotics class near Tampines for my 8-year-old",
            "child_age": "8-year-old",
            "location": "Tampines, Singapore",
            "category": "STEM enrichment class",
            "budget": "middle-class",
            "goal": "hands-on learning",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["recommendations"]
    assert data["recommendations"][0]["business"]["name"] == "Little Explorers STEM Club"


def test_feedback_endpoint_captures_parent_signal():
    response = client.post(
        "/api/feedback",
        json={
            "business_name": "Little Explorers STEM Club",
            "action": "saved",
            "reason": "nearby and hands-on",
            "query": "STEM near Tampines",
            "category": "STEM enrichment class",
            "location": "Tampines, Singapore",
        },
    )
    assert response.status_code == 200
    assert response.json()["saved"] is True


def test_report_endpoint_with_sample():
    sample = client.get("/api/sample").json()
    response = client.post("/api/report", json=sample)
    assert response.status_code == 200
    report = response.json()
    assert report["business_name"] == "Little Explorers STEM Club"
    assert report["score"]["answer_share"] == 0.5
    assert report["recommendations"]


def test_combined_report_includes_parent_signals():
    sample = client.get("/api/sample").json()
    parent_events = client.get("/api/sample-parent-events").json()["events"]
    response = client.post(
        "/api/combined-report",
        json={"visibility": sample, "parent_events": parent_events},
    )
    assert response.status_code == 200
    report = response.json()
    assert report["parent_signals"]["total_parent_events"] == 3
    assert report["parent_signals"]["positive_intent_events"] == 2
    areas = [rec["area"] for rec in report["recommendations"]]
    assert "Profile completeness" in areas
