# 2026-07-13 Live-Fill Budget Enhancement

## Date And Commit

- Date: 2026-07-13
- Base commit: `de2f9e3`
- Dataset/SDK source: local `third_party/kaggle_ai_agent_security`

## Goal

Avoid spending notebook attack-generation budget on live-fill families that do not produce early saved candidates.

## Motivation

The 50-candidate family eval showed:

- `EXFILTRATION`: 50 findings from 50 attempts.
- `CONFUSED_DEPUTY`: 50 findings from 50 attempts.
- `UNTRUSTED_TO_ACTION`: 0 findings from 50 attempts.
- `DESTRUCTIVE_WRITE`: 0 findings from 50 attempts.

So equal `live-all` round-robin budget is not score-optimal locally. It wastes time on two families that currently do not save candidates.

## Implementation

Added a high-yield live-fill candidate set:

- `live-high-yield`
- `live_high_yield`
- `high-yield-live`
- `score-live`
- `submission-live`
- `live-exfil-confused`
- `live_exfil_confused`

This mode rotates only:

1. `EXFILTRATION`
2. `CONFUSED_DEPUTY`

Added adaptive skipping with:

```python
live_fill_family_fail_cap = N
```

When set to a positive number, a family is disabled after `N` unproductive attempts. Unproductive means:

- invalid candidate
- replay error
- no target predicate

Duplicate scored cells do not count as a family failure, because they still prove the family can fire.

## Example Configs

High-yield submission-oriented run:

```python
{
    "candidate_set": "live-high-yield",
    "max_candidates": 100,
    "live_fill_max_attempts": 100,
    "live_fill_warmup": False,
}
```

Adaptive all-family exploratory run:

```python
{
    "candidate_set": "live-all",
    "max_candidates": 100,
    "live_fill_max_attempts": 120,
    "live_fill_family_fail_cap": 2,
    "live_fill_warmup": False,
}
```

## Validation

```bash
PYTHONPATH=third_party/kaggle_ai_agent_security .venv/bin/python -m py_compile attack.py scripts/run_candidate_replay.py tests/test_replay_loop.py
PYTHONPATH=third_party/kaggle_ai_agent_security .venv/bin/python -m unittest discover -s tests
git diff --check
PYTHONPATH=third_party/kaggle_ai_agent_security .venv/bin/python -m aicomp_sdk.cli.main validate redteam attack.py
```

Results:

- Unit tests: passed, 30 tests.
- SDK validation: passed; `attack.py` remains Kaggle-compatible.
- Real-model result: not run in this checkpoint.

## Decision

Keep. This gives us a direct configuration answer to the budget problem:

- For scoring: use `live-high-yield`.
- For exploration: use `live-all` with `live_fill_family_fail_cap`.

## Next Action

Run one combined local GGUF eval with `candidate_set=live-high-yield`, `max_candidates=100`, and `live_fill_max_attempts=100` before packaging the next Kaggle notebook.
