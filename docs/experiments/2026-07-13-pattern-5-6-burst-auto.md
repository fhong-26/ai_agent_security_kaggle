# Pattern 5/6 Burst And Auto Modes

Date: 2026-07-13
Base commit: a54287c

## Goal And Hypothesis

Goal: check whether strategy-study Pattern 5 and Pattern 6 were applied, and code the missing parts.

Hypothesis: Pattern 6 was partly present through live-fill budget controls, but Pattern 5 needed an explicit opt-in burst runner. Adding burst mode as non-default lets us test the high-raw-score idea later without risking the current high-yield single-call submission path.

## Dataset / SDK

Local curated SDK under `third_party/kaggle_ai_agent_security`.

## Attack Family And Stage

- Pattern 5: multi-message EXFILTRATION burst candidates.
- Pattern 6: portfolio/timeit live-fill control mode with default dead-family pruning.
- Default submission path remains `submission-live`.

## Commands Run

```bash
PYTHONPATH=third_party/kaggle_ai_agent_security .venv/bin/python -m py_compile attack.py scripts/run_candidate_replay.py tests/test_replay_loop.py
PYTHONPATH=third_party/kaggle_ai_agent_security .venv/bin/python -m unittest tests.test_replay_loop.ThroughputLiveFillTests
PYTHONPATH=third_party/kaggle_ai_agent_security .venv/bin/python -m unittest discover -s tests
PYTHONPATH=third_party/kaggle_ai_agent_security .venv/bin/python -m aicomp_sdk.cli.main validate redteam attack.py
```

## Mock-Test Result

Passed.

- Targeted Pattern 5/6 tests: 18 tests passed.
- Full lightweight suite: 34 tests passed.
- SDK validator: passed.

## Real-Model Result

Not run. We intentionally avoided local model replay for this pass to keep the Mac cool.

## Predicate Hits And Score Impact

Mock burst candidates can produce three successful marker-bearing `http.post` events in one replay candidate, and the local predicate evaluator emits three `EXFILTRATION` findings for that trace. Estimated raw per 3-post burst in the fake env is at least `3 * 16 + 2 = 50`.

The mode is opt-in as `live-burst` / `burst-stack`; it is not used by default because public notebooks suggest stacked candidates are fragile under replay.

## Replayability Evidence

The new burst runner returns only candidates whose exported trace has both:

- enough successful `http.post` events containing `SECRET_MARKER`;
- enough matching `EXFILTRATION` predicate findings.

If no burst candidate fires and time remains, it falls back to the existing high-yield exfil/confused live-fill families.

## Decision

Keep as an experiment knob, not as the default Kaggle submission path yet. Use `timeit` / `auto` first to measure family productivity, and test `live-burst` only when we want to spend budget on stacked candidates.
