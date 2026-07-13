# 2026-07-13 High-Yield 60 Submission Prep

## Date And Commit

- Date: 2026-07-13
- Base commit: `a528fd3`
- Dataset/SDK source: local `third_party/kaggle_ai_agent_security`

## Goal

Prepare a Kaggle notebook submission that targets a normalized score of 60+ by scaling the two locally proven live-fill families:

- `EXFILTRATION`
- `CONFUSED_DEPUTY`

## Score Math

Prior local 50-candidate evals showed:

- `EXFILTRATION`: 50/50 findings, 50 unique cells, raw score 900.
- `CONFUSED_DEPUTY`: 50/50 findings, 50 unique cells, raw score 300.

That implies:

- Each unique exfil candidate contributes about 18 raw points.
- Each unique confused-deputy candidate contributes about 6 raw points.

The new default uses `submission-live`, which rotates:

1. `EXFILTRATION`
2. `CONFUSED_DEPUTY`

Default cap:

```python
DEFAULT_SUBMISSION_CANDIDATE_LIMIT = 1000
```

If all 1,000 candidates replay like the local 50+50 probes:

- 500 exfil candidates * 18 raw = 9,000 raw
- 500 confused-deputy candidates * 6 raw = 3,000 raw
- Total = 12,000 raw
- Normalized = `12000 / 200000 * 1000 = 60`

## Change

`AttackAlgorithm()` with no config now defaults to:

```python
candidate_set = "submission-live"
max_candidates = 1000
```

This matters because Kaggle's hidden rerun instantiates the submitted attack without our local `attack_config`.

## Validation

Local heavy GGUF replay was intentionally skipped for this checkpoint to avoid overheating the Mac.

Fast validations run:

```bash
PYTHONPATH=third_party/kaggle_ai_agent_security .venv/bin/python -m py_compile attack.py scripts/run_candidate_replay.py tests/test_replay_loop.py
PYTHONPATH=third_party/kaggle_ai_agent_security .venv/bin/python -m unittest discover -s tests
git diff --check
PYTHONPATH=third_party/kaggle_ai_agent_security .venv/bin/python -m aicomp_sdk.cli.main validate redteam attack.py
```

Results:

- Unit tests: passed, 30 tests.
- SDK validation: passed; `attack.py` remains Kaggle-compatible.

## Risk

This is a cross-fingers submission attempt, not a proven public score:

- Kaggle hidden replay may be stricter than local GPT-OSS GGUF.
- 1,000 candidates may run close to the notebook attack/replay time budget.
- The public score will be the source of truth.

## Decision

Package and submit this as the next Kaggle notebook version.
