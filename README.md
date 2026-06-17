# KiasuScout

**KiasuScout** is an MVP for Singapore and Southeast Asian businesses that want to know where parents' AI assistants send them.

It combines:

1. a **Model Context Protocol server** for agent workflows, and
2. a lightweight **web frontend** for running first-pass AI answer visibility reports.

The initial focus is middle-class parents looking for:

- tuition and academic support
- enrichment classes
- children's activities
- educational toys and learning products
- camps, workshops, STEM/arts/sports programmes

KiasuScout helps agencies and operators answer:

> "When parents ask ChatGPT, Gemini, Perplexity or Google AI for recommendations, do we appear — or do our competitors?"

This MVP is intentionally measurement-first. It does not scrape consumer AI platforms yet. Instead, it provides prompt packs and analysis tools for answers captured manually, via approved APIs, or by later browser automation.

## What's in the MVP

### Web app

- Singapore/SEA landing page and dashboard
- prompt-pack generator for parent discovery queries
- form for business/category/location/competitors
- captured-answer JSON input
- answer-share report
- competitor mentions
- recommended visibility fixes
- raw report JSON for export/debugging

### MCP tools

- `generate_prompt_pack` — create Singapore/SEA parent-oriented prompt sets for a category/location.
- `analyze_answer_visibility` — parse captured LLM answers and score business visibility against competitors.
- `recommend_visibility_fixes` — produce practical local SEO/GEO fixes for the education/children sector.
- `create_visibility_report` — generate a complete client-ready JSON report.
- `list_supported_segments` — list supported locations, categories, parent personas, and platforms.

## Install

```bash
git clone https://github.com/sixirixis/kiasu-scout.git
cd kiasu-scout
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
```

## Run the web MVP

```bash
python -m answerspot_sg_mcp.web
```

Open:

```text
http://127.0.0.1:8000
```

## Run as an MCP server

```bash
python -m answerspot_sg_mcp.server
```

Example Hermes config:

```yaml
mcp_servers:
  kiasu_scout:
    command: "python"
    args: ["-m", "answerspot_sg_mcp.server"]
    timeout: 120
```

## Run tests

```bash
pytest -q
ruff check .
```

## Example analysis payload

```json
{
  "business_name": "Little Explorers STEM Club",
  "category": "STEM enrichment class",
  "location": "Tampines, Singapore",
  "competitors": ["The Learning Lab", "Saturday Kids", "Nullspace Robotics"],
  "answers": [
    {
      "platform": "ChatGPT",
      "prompt": "What are the best STEM enrichment classes in Tampines for a primary school child?",
      "answer_text": "Parents often compare Saturday Kids, Nullspace Robotics and Little Explorers STEM Club..."
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
