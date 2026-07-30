# V2 Static64 And Confused Deputy Micro

Date: 2026-07-30
Base repo commit before implementation: `a07b2b8`

## Goal And Hypothesis

Prepare two separate sandboxed Kaggle submissions:

- a score-seeking rung: `score-priority-v2` plus only 64 static EXFIL backstop
  candidates;
- a learning canary: a confused-deputy-only live micro submission.

The reason for splitting them is the 2026-07-30 result from the previous
portfolio attempt:

```text
55076352  Score-priority v2 adaptive template      COMPLETE  publicScore=65.565
55076852  Score-max v3 live plus static backstop   COMPLETE  format error, totalBytes=0
55076854  Category explore v1 anchored basket      COMPLETE  format error, totalBytes=0
```

The new score rung keeps the proven v2 live path and reduces the appended static
EXFIL backstop from 400 to 64. If all 64 static candidates replay and score, the
expected public-score lift is:

```text
64 * (16 EXFILTRATION severity + 2 unique-cell bonus) / 200 = 5.760
65.565 + 5.760 ~= 71.325
```

The confused-deputy micro canary is intentionally separate so it can measure one
non-EXFIL family without the failed mixed-basket replay risk.

## Implementation

Added opt-in score rung aliases:

- `score-priority-v2-static-64`
- `score_priority_v2_static_64`
- `live-score-priority-v2-static-64`
- `live_score_priority_v2_static_64`
- `submission-score-priority-v2-static-64`
- `submission_score_priority_v2_static_64`

Defaults:

- live cap: `1000`
- static EXFIL backstop cap: `64`
- total candidate cap: `1064`
- static URL start index: `1000`
- adaptive fast EXFIL: enabled by default

Added opt-in confused-deputy micro aliases:

- `confused-deputy-micro`
- `confused_deputy_micro`
- `live-confused-deputy-micro`
- `live_confused_deputy_micro`
- `submission-confused-deputy-micro`
- `submission_confused_deputy_micro`

Defaults:

- family: `confused_deputy`
- live candidate cap: `64`

## Validation

Commands run:

```bash
PYTHONPATH=third_party/kaggle_ai_agent_security \
.venv/bin/python -m py_compile attack.py tests/test_replay_loop.py scripts/package_kaggle_notebook.py

PYTHONPATH=third_party/kaggle_ai_agent_security \
.venv/bin/python -m unittest tests.test_replay_loop

PYTHONPATH=third_party/kaggle_ai_agent_security \
.venv/bin/python -m unittest discover -s tests

git diff --check
```

Results:

```text
Ran 56 tests in 0.169s
OK

Ran 72 tests in 0.181s
OK

diff check passed
```

## Decision

Proceed to package, push, and submit both as separate notebooks:

1. `submission-score-priority-v2-static-64` for the score ladder.
2. `submission-confused-deputy-micro` as the isolated non-EXFIL canary.
