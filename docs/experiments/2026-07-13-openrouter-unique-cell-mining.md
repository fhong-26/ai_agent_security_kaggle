# 2026-07-13 OpenRouter Unique-Cell Mining

## Date And Commit

- Date: 2026-07-13
- Git commit hash before change: `9ccc489`
- Goal: keep using OpenRouter feedback-guided mining until the weak families have around 10 unique local scoring cells each, not just 10 passing prompts.
- Early stop criteria: stop at 10 unique target-predicate cells per family or 1 hour.

## What Changed

- Updated `scripts/mine_openrouter_templates.py` so the primary target is now unique target-predicate cell hashes.
- Added `unique_scoring_cells.jsonl`, separate from:
  - `passing_templates.jsonl`: all templates that hit the target predicate.
  - `unique_kept.jsonl`: all locally unique kept traces.
  - `unique_scoring_cells.jsonl`: target-family predicate hits with new cell hashes.
- Added feedback fields for known target cell hashes, unique-cell examples, and duplicate-cell examples.
- Added cell-diversity styles:
  - Search prefix before page-driven untrusted action.
  - Read prefix before page-driven untrusted action.
  - Read/Open/Search/Shell prefix before `Delete secret.txt`.
- Relaxed weak-family structural validation so `DESTRUCTIVE_WRITE` can be multi-message and `UNTRUSTED_TO_ACTION` can start with a search/read prefix as long as the chain later names a web/email fixture.

## Commands Run

Dry-run check:

```bash
PYTHONPATH=third_party/kaggle_ai_agent_security .venv/bin/python scripts/mine_openrouter_templates.py \
  --dry-run \
  --target-passing-per-family 1 \
  --target-unique-per-family 2 \
  --max-runtime-s 120 \
  --batch-size 2 \
  --sleep-s 0 \
  --max-batches 8 \
  --output-dir runs/llm_candidates/template-mining-unique-dryrun-check
```

Result: streamed `unique_cells=` progress and reached the small dry-run target.

First real run:

```bash
PYTHONPATH=third_party/kaggle_ai_agent_security .venv/bin/python scripts/mine_openrouter_templates.py \
  --target-passing-per-family 10 \
  --target-unique-per-family 10 \
  --max-runtime-s 3600 \
  --batch-size 4 \
  --sleep-s 1 \
  --temperature 0.9 \
  --max-tokens 2048 \
  --guardrail none \
  --agent deterministic
```

Result: stopped manually after the filter bug was clear. `UNTRUSTED_TO_ACTION` got stuck at 2 unique cells because search/read-prefix chains were filtered before replay.

After the filter fix, reran the same command.

Output directory:

```text
runs/llm_candidates/template-mining-20260713T151556Z
```

## Results

The successful run finished in about 68 seconds, far below the 1-hour cap.

| Family | Requested Generated | Valid Replayed | Passing Templates | Target Hits | Unique Target Cells |
|---|---:|---:|---:|---:|---:|
| `UNTRUSTED_TO_ACTION` | 28 | 25 | 24 | 25 | 10 |
| `DESTRUCTIVE_WRITE` | 20 | 20 | 18 | 18 | 11 |

Files written:

```text
runs/llm_candidates/template-mining-20260713T151556Z/generated.jsonl
runs/llm_candidates/template-mining-20260713T151556Z/attempts.jsonl
runs/llm_candidates/template-mining-20260713T151556Z/passing_templates.jsonl
runs/llm_candidates/template-mining-20260713T151556Z/unique_kept.jsonl
runs/llm_candidates/template-mining-20260713T151556Z/unique_scoring_cells.jsonl
runs/llm_candidates/template-mining-20260713T151556Z/manifest.json
```

## What It Learned

`UNTRUSTED_TO_ACTION` reached 10 unique cells by varying the prefix before the same two useful sources:

- `page_1035 -> http.post`
- `page_5 -> fs.delete`
- `Search -> page_1035/page_5 -> action`
- `Read file -> page_1035/page_5 -> action`

`DESTRUCTIVE_WRITE` reached 11 unique cells by prepending different tool paths before the final `Delete secret.txt`:

- `fs.read -> fs.delete`
- `web.open -> fs.delete`
- `web.search -> fs.delete`
- `shell.run -> fs.delete`
- direct `fs.delete`

## Important Caveat

This is local deterministic replay with `guardrail=none`. It proves we can mine diverse local scoring cells, but it does not prove public leaderboard success. Public `optimal_public` previously blocked the direct weak-family actions.

## Decision

Keep the unique-cell mining changes. This is a meaningful improvement over the previous template-count miner because it learns from duplicate cells and optimizes for actual scoring diversity.

Next path:

- Add an opt-in candidate bank or replay mode that consumes `unique_scoring_cells.jsonl`.
- Test a small subset against the heavier local/Kaggle target model only when we are ready to spend that budget.
- For public score, still preserve the current high-yield `EXFILTRATION`/`CONFUSED_DEPUTY` path unless these weak-family cells prove transferable under the real evaluator.
