from fastapi.testclient import TestClient

from answerspot_sg_mcp.web import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "app": "KiasuScout"}


def test_index_loads_brand():
    response = client.get("/")
    assert response.status_code == 200
    assert "KiasuScout" in response.text
    assert "AI sends parents" in response.text


def test_prompt_endpoint():
    response = client.post(
        "/api/prompts",
        json={"category": "primary tuition", "location": "Tampines, Singapore", "limit": 3},
    )
    assert response.status_code == 200
    prompts = response.json()["prompts"]
    assert len(prompts) == 3
    assert "Tampines" in prompts[0]


def test_report_endpoint_with_sample():
    sample = client.get("/api/sample").json()
    response = client.post("/api/report", json=sample)
    assert response.status_code == 200
    report = response.json()
    assert report["business_name"] == "Little Explorers STEM Club"
    assert report["score"]["answer_share"] == 0.5
    assert report["recommendations"]
