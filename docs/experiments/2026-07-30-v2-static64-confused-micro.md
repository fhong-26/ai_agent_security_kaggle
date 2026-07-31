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

## Packaging

Generated source copies under ignored `runs/submission-sources/`:

```text
runs/submission-sources/v2-static64/attack.py
DEFAULT_SUBMISSION_CANDIDATE_SET: submission-score-priority-v2-static-64
resolved default candidate limit: 1064
is score-priority-v2-static: True
attack.py bytes: 102274
attack.py sha256: 068edd258c169272068bf640189b93c3aa67d16cb7b938dcbd4d8d96467d30c9

runs/submission-sources/confused-deputy-micro/attack.py
DEFAULT_SUBMISSION_CANDIDATE_SET: submission-confused-deputy-micro
resolved default candidate limit: 64
is live fill: True
attack.py bytes: 102268
attack.py sha256: 92ba2d68915d327e5ee163513616198da0e046fad0333133ea10667a96bced91
```

Packaged notebooks:

```text
kernel_ref: temperancehong/ai-agent-security-v2-static64
kernel_dir: submissions/v2-static64-ba82cab-notebook/kernel
notebook_sha256: a950236b129d96d8cff6bd69cc007e36a356a2915a5eba0b457955ce12988a40
metadata_sha256: c0555c2a817e2ffbc5f54a42852fc0af3aa9550c7d993aad4d9fe60e0851b44d

kernel_ref: temperancehong/ai-agent-security-confused-deputy-micro
kernel_dir: submissions/confused-deputy-micro-ba82cab-notebook/kernel
notebook_sha256: a33eb775dd6ed1ebbbb927e217d090ba1bca47fdfcfa97f63846f95cfcef6f11
metadata_sha256: 032563d66cd05059f151c1e053b77aa0618a9742888d35fea16ccefa886887e8
```

## Push And Submit

Pushed both kernels on 2026-07-30:

```text
temperancehong/ai-agent-security-v2-static64
Kernel version 1 successfully pushed.
KernelWorkerStatus.COMPLETE

temperancehong/ai-agent-security-confused-deputy-micro
Kernel version 1 successfully pushed.
KernelWorkerStatus.COMPLETE
```

Submitted both kernels to the competition:

```text
55108726  Score priority v2 plus static64       SubmissionStatus.PENDING
55108728  Confused deputy micro canary          SubmissionStatus.PENDING
```

## Final Public Results

Observed on 2026-07-31:

```text
55108726  Score priority v2 plus static64  SubmissionStatus.COMPLETE  publicScore=
55108728  Confused deputy micro canary     SubmissionStatus.COMPLETE  publicScore=1.920
```

The reduced static backstop rung failed with a blank public score, matching the
earlier mixed/static basket failure mode rather than a scored zero. Treat this
as evidence that adding even a small static tail to the live v2 path can make the
Kaggle submission output invalid or unreplayable under the hidden rerun.

The confused-deputy micro canary scored a small but real public signal. Keep it
as a weak-case probe and mutation seed, but do not mix it into the main
score-priority EXFIL path until the candidate volume and replay behavior are
measured in isolation.

Decision: discard `score-priority-v2-static-64` as a score ladder. Preserve the
last proven score rung, `score-priority-v2 adaptive template` at `65.565`, and
explore small isolated confused-deputy mutations separately.
