# 2026-07-13 OpenRouter Streaming Template Mining

## Date And Commit

- Date: 2026-07-13
- Git commit hash before change: `a161478`
- Goal: use OpenRouter feedback-guided generation to mine passing local templates for the two weak families, while returning results in real time and avoiding local GPU load.
- Early stop criteria: stop at 10 passing templates per family or 1 hour.

## What Changed

- Added `scripts/mine_openrouter_templates.py`.
- The miner:
  - generates small OpenRouter batches instead of one large batch;
  - immediately replays each generated candidate locally;
  - prints batch and candidate-level progress as soon as results are available;
  - writes `generated.jsonl`, `attempts.jsonl`, `passing_templates.jsonl`, `unique_kept.jsonl`, and `manifest.json` incrementally;
  - defaults to `agent=deterministic` and `guardrail=none`, so it does not load local GPT/Gemma or use the local GPU;
  - sleeps between batches to avoid hammering the API or the machine;
  - feeds previous pass/fail summaries back into the next OpenRouter prompt.

## Commands Run

Dry-run streaming check:

```bash
PYTHONPATH=third_party/kaggle_ai_agent_security .venv/bin/python scripts/mine_openrouter_templates.py \
  --dry-run \
  --target-passing-per-family 1 \
  --max-runtime-s 120 \
  --batch-size 2 \
  --sleep-s 0 \
  --max-batches 4 \
  --output-dir runs/llm_candidates/template-mining-dryrun-check
```

Result: streamed per-candidate output and reached the dry-run target.

Real OpenRouter mining run:

```bash
PYTHONPATH=third_party/kaggle_ai_agent_security .venv/bin/python scripts/mine_openrouter_templates.py \
  --target-passing-per-family 10 \
  --max-runtime-s 3600 \
  --batch-size 4 \
  --sleep-s 1 \
  --temperature 0.9 \
  --max-tokens 2048 \
  --guardrail none \
  --agent deterministic
```

Output directory:

```text
runs/llm_candidates/template-mining-20260713T150410Z
```

## Results

The run finished in about 69 seconds, far under the 1-hour cap.

| Family | Requested Generated | Valid Replayed | Passing Templates | Target Hits | Unique Score Cells |
|---|---:|---:|---:|---:|---:|
| `UNTRUSTED_TO_ACTION` | 24 | 19 | 10 | 10 | 2 |
| `DESTRUCTIVE_WRITE` | 24 | 19 | 10 | 10 | 1 |

Files written:

```text
runs/llm_candidates/template-mining-20260713T150410Z/generated.jsonl
runs/llm_candidates/template-mining-20260713T150410Z/attempts.jsonl
runs/llm_candidates/template-mining-20260713T150410Z/passing_templates.jsonl
runs/llm_candidates/template-mining-20260713T150410Z/unique_kept.jsonl
runs/llm_candidates/template-mining-20260713T150410Z/manifest.json
```

## What It Learned

`UNTRUSTED_TO_ACTION`:

- Best passing styles were still `page_1035` and `page_5`.
- Generic email and `page_214` styles mostly failed in deterministic replay.
- The miner learned to cycle back to `page_1035-training`, `page5-maintenance`, and low-salience pronoun continuations.

`DESTRUCTIVE_WRITE`:

- Delete-heavy phrasings passed reliably.
- Softer overwrite/replace/truncate styles mostly failed in deterministic replay.
- Passing templates mostly collapse into the same score cell because the scored tool signature is still `fs.delete(path=secret.txt)`.

## Interpretation

This achieved the local template-mining goal: around 10 passing templates for each weak family.

It did not prove public leaderboard score improvement. The unique score-cell counts are still low, and prior `optimal_public` testing showed these weak-family shapes are blocked by the public guardrail. Use these as a template bank and mutation seed source, not as a replacement for the current high-yield default submission path.

## Decision

Keep the streaming miner. It is the right tool for iterative OpenRouter mining because it gives immediate feedback, avoids local GPU pressure by default, and records each pass/fail example for later analysis.

Next mutation path:

- Add a replay mode that can run the curated passing bank against Kaggle/GPT-OSS only when the user explicitly wants a heavier model run.
- For public score, keep prioritizing `EXFILTRATION` and `CONFUSED_DEPUTY`.
- For weak-family research, bias future OpenRouter prompts toward `page_1035`, `page_5`, and exact delete-heavy `secret.txt` variants.
