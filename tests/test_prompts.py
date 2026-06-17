from answerspot_sg_mcp.prompts import SUPPORTED_SEGMENTS, generate_prompt_pack


def test_prompt_pack_has_singapore_parent_focus():
    prompts = generate_prompt_pack("primary math tuition", "Tampines, Singapore", child_age="P4 child", limit=5)
    assert len(prompts) == 5
    joined = " ".join(prompts).lower()
    assert "tampines" in joined
    assert "parent" in joined or "parents" in joined
    assert "primary math tuition" in joined


def test_supported_segments_include_toys_and_enrichment():
    assert "toys" in SUPPORTED_SEGMENTS
    assert "enrichment" in SUPPORTED_SEGMENTS
    assert "educational toys" in SUPPORTED_SEGMENTS["toys"]
