# 2026-07-13 Weak-Cell V4 Probe Prep

## Date And Commit

- Date: 2026-07-13
- Goal: prepare a small Kaggle V4 probe for the two newly mined weak families:
  - `UNTRUSTED_TO_ACTION`
  - `DESTRUCTIVE_WRITE`
- Candidate budget: 50 total candidates.
- Submission intent: transfer probe, not a high-score run.

## What Changed

Added a default static probe candidate set:

```text
submission-weak-v4
```

It returns exactly 50 candidates:

- 25 `UNTRUSTED_TO_ACTION`
- 25 `DESTRUCTIVE_WRITE`

Unlike `submission-live`, this set returns candidates directly without live prefiltering in `AttackAlgorithm.run`. This is deliberate: the public guardrail locally suppresses these weak-family shapes during live probing, so a live-fill strategy would likely return zero candidates before Kaggle replay can test them.

The high-yield path is preserved:

```text
submission-live -> 1000 candidate limit
submission-weak-v4 -> 50 candidate limit
```

## Local Validation

Fast validation:

```bash
PYTHONPATH=third_party/kaggle_ai_agent_security .venv/bin/python -m py_compile attack.py tests/test_replay_loop.py scripts/package_kaggle_notebook.py scripts/run_candidate_replay.py
PYTHONPATH=third_party/kaggle_ai_agent_security .venv/bin/python -m unittest discover -s tests
PYTHONPATH=third_party/kaggle_ai_agent_security .venv/bin/python -m aicomp_sdk.cli.main validate redteam attack.py
git diff --check
```

Results:

- Unit tests: 54 passed.
- SDK validation: passed.
- Diff check: clean.

Replay under no guardrail:

```bash
PYTHONPATH=third_party/kaggle_ai_agent_security .venv/bin/python scripts/run_candidate_replay.py \
  --candidate-set submission-weak-v4 \
  --guardrail none \
  --agent deterministic \
  --max-candidates 50 \
  --verbosity quiet
```

Result:

```text
runs/candidate-replay-20260713T154452553670Z-submission-weak-v4-none.jsonl
attempts=50 hits=50 kept=35 raw_estimate=998
```

Predicate mix under `none`:

```text
50 UNTRUSTED_TO_ACTION
38 DESTRUCTIVE_WRITE
26 EXFILTRATION
```

Replay under public optimal guardrail:

```bash
PYTHONPATH=third_party/kaggle_ai_agent_security .venv/bin/python scripts/run_candidate_replay.py \
  --candidate-set submission-weak-v4 \
  --guardrail optimal_public \
  --agent deterministic \
  --max-candidates 50 \
  --verbosity quiet
```

Result:

```text
runs/candidate-replay-20260713T154454346970Z-submission-weak-v4-optimal_public.jsonl
attempts=50 hits=0 kept=0 raw_estimate=0
```

## Interpretation

This probe is useful because it asks Kaggle:

```text
Do the newly mined local weak-family scoring cells transfer to the real evaluator/model mix?
```

But the local expectation is conservative:

```text
Public optimal guardrail blocks these direct weak-family shapes.
```

So this V4 is intentionally not the best score-seeking submission. It is a small measurement run. If the public score is zero or tiny, that confirms the local guardrail result. If it scores, the winning candidates are especially valuable because they crossed the weak-family guardrail boundary.

## Decision

Prepared and submitted as V4 from committed source.

## Packaging

Committed code:

```text
8b937c4 Prepare weak-cell V4 probe
```

Packaged notebook:

```bash
PYTHONPATH=third_party/kaggle_ai_agent_security .venv/bin/python scripts/package_kaggle_notebook.py \
  --label weak-cell-v4-probe \
  --kernel-slug ai-agent-security-high-yield-60 \
  --title "AI Agent Security Weak Cell V4 Probe"
```

Manifest:

```text
submissions/weak-cell-v4-probe-8b937c4-notebook/manifest.json
```

Important package fields:

```text
repo_commit: 8b937c4
attack_source_commit: 8b937c4
attack_py_sha256: 1fe4c37d7f43bb40e84b3d726d441c393ad7db921c5a8eda2a01900d0f1ecb61
notebook_sha256: 06f3efc99f22895fc5dea0bc19501f5dc7fb9a4d3f558bdb00312f2398a6ac5a
```

## Kaggle Push And Submission

Pushed kernel:

```bash
.venv/bin/kaggle kernels push -p submissions/weak-cell-v4-probe-8b937c4-notebook/kernel
```

Result:

```text
Kernel version 4 successfully pushed.
Resolved kernel ref: temperancehong/ai-agent-security-weak-cell-v4-probe
Kernel status: COMPLETE
```

Notebook output log confirmed:

```text
attack.py bytes: 74417
attack.py sha256: 1fe4c37d7f43bb40e84b3d726d441c393ad7db921c5a8eda2a01900d0f1ecb61
```

Submitted to competition:

```bash
.venv/bin/kaggle competitions submit \
  -c ai-agent-security-multi-step-tool-attacks \
  -f submission.csv \
  -k temperancehong/ai-agent-security-weak-cell-v4-probe \
  -v 4 \
  -m "Weak-cell V4 50 candidate probe"
```

Submission registration:

```text
Submission ref: 54652641
Date: 2026-07-13 15:46:48.610000
Description: Weak-cell V4 50 candidate probe
Status at registration: SubmissionStatus.PENDING
```
