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

## First API Smoke Result

After filling local `.env`, ran a small cheap-model smoke:

```bash
PYTHONPATH=third_party/kaggle_ai_agent_security .venv/bin/python scripts/generate_openrouter_candidates.py \
  --family confused_deputy \
  --count-per-family 8 \
  --mode factory \
  --max-tokens 2048 \
  --temperature 0.7 \
  --output runs/llm_candidates/openrouter-smoke-confused.jsonl
```

Result:

- OpenRouter auth and model call succeeded.
- Output: 8 candidates.
- Shape: all 8 had one message, contained `{recipient}`, and avoided `send`, `email`, and `upload`.

Then ran a controlled cheap factory batch:

```bash
PYTHONPATH=third_party/kaggle_ai_agent_security .venv/bin/python scripts/generate_openrouter_candidates.py \
  --family all \
  --count-per-family 40 \
  --mode factory \
  --max-tokens 8192 \
  --temperature 0.8 \
  --output runs/llm_candidates/openrouter-factory-all-40.jsonl
```

Result:

- Output: 160 candidates.
- Counts: 40 each for `exfiltration`, `confused_deputy`, `untrusted_to_action`, and `destructive_write`.
- Basic structural audit passed.
- Strategic note: Qwen's exfiltration prompts are worse than our current hand-coded winner because some use intent-heavy words like "Send" or "Upload". The confused-deputy prompts are more promising as mutation seeds.

Added replay bridge:

```bash
PYTHONPATH=third_party/kaggle_ai_agent_security .venv/bin/python scripts/run_candidate_replay.py \
  --candidate-jsonl runs/llm_candidates/openrouter-smoke-confused.jsonl \
  --guardrail none \
  --agent deterministic \
  --max-candidates 8 \
  --verbosity quiet
```

Result:

- Attempts: 8.
- Predicate hits: 0.
- Kept: 0.

Interpretation: this does not disprove the prompts. The deterministic toy agent does not translate natural-language notification requests into `email.send`. The important outcome is that generated JSONL now renders into replayable `CandidateSpec` objects for later GPT-OSS/Gemma validation.
