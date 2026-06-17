# AnswerSpot SG MCP

AnswerSpot SG MCP is a first-pass Model Context Protocol server for **AI local answer visibility** in Singapore and Southeast Asia, focused on businesses serving middle-class parents looking for:

- tuition and academic support
- enrichment classes
- children's activities
- educational toys and learning products
- camps, workshops, STEM/arts/sports programmes

The server helps agencies and operators answer: **"When parents ask ChatGPT/Gemini/Perplexity/Google AI for recommendations, do we appear, which competitors appear, and what signals are missing?"**

This MVP is intentionally measurement-first. It does not scrape consumer AI platforms yet. Instead, it provides prompt packs and analysis tools for answers captured manually, via approved APIs, or by later browser automation.

## MCP tools

- `generate_prompt_pack` — create Singapore/SEA parent-oriented prompt sets for a category/location.
- `analyze_answer_visibility` — parse captured LLM answers and score business visibility against competitors.
- `recommend_visibility_fixes` — produce practical local SEO/GEO fixes for the education/children sector.
- `create_visibility_report` — generate a complete client-ready JSON report.
- `list_supported_segments` — list supported locations, categories, parent personas, and platforms.

## Install

```bash
git clone https://github.com/sixirixis/answerspot-sg-mcp.git
cd answerspot-sg-mcp
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
```

## Run tests

```bash
pytest -q
```

## Run as an MCP server

```bash
python -m answerspot_sg_mcp.server
```

Example Hermes config:

```yaml
mcp_servers:
  answerspot_sg:
    command: "python"
    args: ["-m", "answerspot_sg_mcp.server"]
    timeout: 120
```

## Example analysis payload

```json
{
  "business_name": "BrightMinds Learning Hub",
  "category": "primary tuition",
  "location": "Tampines, Singapore",
  "competitors": ["The Learning Lab", "Mind Stretcher", "Kumon"],
  "answers": [
    {
      "platform": "ChatGPT",
      "prompt": "What are the best primary math tuition centres near Tampines for a P4 student?",
      "answer_text": "Parents often consider The Learning Lab, Mind Stretcher and Kumon...",
      "captured_at": "2026-06-18T10:00:00Z"
    }
  ]
}
```

## Product direction

The initial ICP is **local SEO agencies and education/enrichment operators in Singapore**. The first commercial deliverable should be a white-label monthly AI visibility report showing:

- answer share across platforms
- competitor recommendations
- prompt/category gaps
- cited sources and reputation signals
- recommended fixes: Google Business Profile, local directories, parent forums, review targets, schema, service pages, FAQs, and marketplace listings

## Safety and terms

This repo does not include scraping logic. Any future connector should prefer official APIs or user-authorized collection and clearly disclose methodology.
