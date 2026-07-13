# OpenRouter Candidate Factory

Date: 2026-07-13

## Goal

Add an offline LLM-guided prompt factory that can use OpenRouter to generate Kaggle sandbox candidate prompts without putting external API calls inside the submitted Kaggle notebook.

## Secret Setup

Copy or edit `.env` locally:

```bash
OPENROUTER_API_KEY=sk-or-...
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_FACTORY_MODEL=qwen/qwen3-coder
OPENROUTER_REVIEW_MODEL=z-ai/glm-5.2
OPENROUTER_SITE_URL=
OPENROUTER_APP_NAME=ai-agent-security-kaggle
```

`.env` is ignored by git. `.env.example` is committed only as a safe variable-name contract.

## Usage

Dry-run without spending API tokens:

```bash
PYTHONPATH=third_party/kaggle_ai_agent_security .venv/bin/python scripts/generate_openrouter_candidates.py \
  --dry-run \
  --family all \
  --count-per-family 5 \
  --print-requests
```

Generate candidates with the cascade:

```bash
PYTHONPATH=third_party/kaggle_ai_agent_security .venv/bin/python scripts/generate_openrouter_candidates.py \
  --family all \
  --count-per-family 50 \
  --mode cascade
```

Cheaper bulk-only generation:

```bash
PYTHONPATH=third_party/kaggle_ai_agent_security .venv/bin/python scripts/generate_openrouter_candidates.py \
  --family confused_deputy \
  --count-per-family 100 \
  --mode factory
```

Strategy-only generation:

```bash
PYTHONPATH=third_party/kaggle_ai_agent_security .venv/bin/python scripts/generate_openrouter_candidates.py \
  --family untrusted_to_action \
  --mode architect
```

Outputs go to:

```text
runs/llm_candidates/openrouter-candidates-<timestamp>.jsonl
runs/llm_candidates/openrouter-candidates-<timestamp>.manifest.json
```

## Intended Loop

```text
OpenRouter generates candidate bank
        ↓
inspect JSONL manually
        ↓
run local/mock replay or targeted live-fill probes
        ↓
promote only successful compact templates into attack.py
```

## Decision

Keep this outside `attack.py`. The submitted Kaggle notebook should remain fast and deterministic; OpenRouter is for offline invention and critique.
