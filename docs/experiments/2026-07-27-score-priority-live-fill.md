# Score-Priority Live Fill

Date: 2026-07-27
Base repo commit: `56e2fdc`

## Goal And Hypothesis

Adapt the strongest public-notebook lesson to this repo without changing the
existing `live-high-yield` behavior. The hypothesis is that our two strongest
families should not be round-robined equally when the higher-value family is
still firing:

- `EXFILTRATION`: strongest public-score family, about `18` raw per unique
  clean candidate.
- `CONFUSED_DEPUTY`: useful fallback/diversifier, but lower value per clean
  candidate.

The new mode should therefore spend attempts on `EXFILTRATION` first, keep only
successful candidates, and fall back to `CONFUSED_DEPUTY` only when exfil stalls.

## Dataset / SDK

- Local curated SDK mirror under `third_party/kaggle_ai_agent_security`
- Mock replay fixtures in `tests/test_replay_loop.py`
- No real model/API run in this loop.

## Attack Family And Stage

- Stage: candidate generation/live validation.
- Families: `EXFILTRATION` first, `CONFUSED_DEPUTY` fallback.
- New candidate-set aliases:
  - `live-score-priority`
  - `live_score_priority`
  - `score-priority-live`
  - `score_priority_live`
  - `exfil-first-live`
  - `exfil_first_live`

## Commands Run

```bash
.venv/bin/python -m unittest tests.test_replay_loop
.venv/bin/python -m unittest discover -s tests
.venv/bin/python -m py_compile attack.py tests/test_replay_loop.py
git diff --check
```

## Mock-Test Result

Pass.

```text
Ran 49 tests in 0.163s
OK

Ran 65 tests in 0.174s
OK
```

The tests verify:

- `live-score-priority` maps to the same two strong families as
  `live-high-yield`.
- When both families fire, all retained attempts are `EXFILTRATION`.
- When `EXFILTRATION` fails once, the mode disables it and fills from
  `CONFUSED_DEPUTY`.

## Real-Model Result

Not run in this loop. This change is intentionally mock-first and should be
submitted only after a small real/Kaggle canary confirms timeout behavior.

## Predicate Hits And Score Impact

Expected public-score behavior if replay is clean:

```text
EXFILTRATION candidate ~= 16 severity + 2 unique = 18 raw
CONFUSED_DEPUTY candidate ~= lower severity + 2 unique
```

Compared with old `live-high-yield` round-robin, `live-score-priority` should
increase expected raw score whenever direct exfil remains reliable, because it
does not spend every other attempt on the lower-value family.

## Replayability Evidence

The mode uses the existing live-fill loop:

- `env.reset()`
- `env.interact(...)`
- `env.export_trace_dict()`
- `eval_predicates(...)`
- score-cell dedupe
- return only `AttackCandidate.from_messages(...)` for kept attempts

The only change is scheduler order.

## Decision

Keep. Use `candidate_set=live-score-priority` as the next opt-in live-fill
experiment after static rungs confirm headroom. Do not replace `live-high-yield`
yet; keep it as the round-robin comparison baseline.
