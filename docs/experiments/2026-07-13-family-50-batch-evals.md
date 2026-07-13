# 2026-07-13 Family 50 Batch Evals

## Date And Commit

- Date: 2026-07-13
- Commit under test: `03436dd`
- Dataset/SDK source: local `third_party/kaggle_ai_agent_security`
- Model: local GPT-OSS GGUF at `data/models/gpt-oss-20b/gpt-oss-20b-Q4_K_M.gguf`
- Weak-family artifacts: `runs/weak-family-50-eval-20260713T122738Z/`
- High-yield artifacts: `runs/high-yield-50-eval-20260713T124401Z/`

## Goal

Generate and locally test 50 live-fill attempts each for the two families that did not succeed in the prior `live-all` run:

- `UNTRUSTED_TO_ACTION`
- `DESTRUCTIVE_WRITE`

Also verify whether the two families that did work can be batched with the same prompt templates:

- `EXFILTRATION`
- `CONFUSED_DEPUTY`

## Shared Config

Each family used the same attempt shape:

```python
{
    "max_candidates": 50,
    "live_fill_max_attempts": 50,
    "live_fill_warmup": False,
    "live_fill_margin_s": 30.0,
    "live_fill_slowest0_s": 10.0,
    "live_fill_slowest_mult": 1.25,
}
```

Runtime config:

```python
AttackRunConfig(time_budget_s=900, max_steps=50, max_tool_hops=4)
```

## Results

| Family | Candidate Set | Attempts | Findings | Unique Cells | Raw Score |
|---|---:|---:|---:|---:|---:|
| `UNTRUSTED_TO_ACTION` | `live-untrusted-to-action` | 50 | 0 | 0 | 0.0 |
| `DESTRUCTIVE_WRITE` | `live-destructive-write` | 50 | 0 | 0 | 0.0 |
| `EXFILTRATION` | `throughput-single` | 50 | 50 | 50 | 900.0 |
| `CONFUSED_DEPUTY` | `live-confused-deputy` | 50 | 50 | 50 | 300.0 |

Predicate/tool details:

```json
{
  "throughput-single": {
    "predicate_counts": {"EXFILTRATION": 50},
    "tool_counts": {"http.post": 50}
  },
  "live-confused-deputy": {
    "predicate_counts": {"CONFUSED_DEPUTY": 50},
    "tool_counts": {"email.send": 50}
  },
  "live-untrusted-to-action": {
    "predicate_counts": {},
    "tool_counts": {}
  },
  "live-destructive-write": {
    "predicate_counts": {},
    "tool_counts": {}
  }
}
```

## Interpretation

The two weak families were generated and tested locally, but neither produced saved candidates:

- Created/attempted: yes, 50 each.
- Saved/replayed as successful candidates: no.
- Score contribution: zero.

The two high-yield families scaled exactly as expected in local replay:

- `throughput-single`: 50 out of 50 saved candidates scored.
- `live-confused-deputy`: 50 out of 50 saved candidates scored.

So the answer to "can we batch generate using the same prompt template?" is locally yes for the two high-yield families. The caveat is that this was tested as two separate 50-candidate evals; the next submission-oriented step is to combine those families in one high-yield mode and test the combined runtime.

## Decision

Do not spend equal notebook budget on `UNTRUSTED_TO_ACTION` or `DESTRUCTIVE_WRITE` in the next submission attempt. They are currently too slow/low-yield locally.

Focus the next score-seeking variant on `EXFILTRATION` plus `CONFUSED_DEPUTY`, because those produced 100 successful unique local findings across 100 generated candidates.

## Next Action

Add a high-yield live-fill candidate set that rotates only:

1. `EXFILTRATION`
2. `CONFUSED_DEPUTY`

Then run it as one combined local eval before packaging a new Kaggle notebook submission.
