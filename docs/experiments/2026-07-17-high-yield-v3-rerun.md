# 2026-07-17 High-Yield V3 Rerun

## Goal

After the exact V2 canary submission succeeded, resubmit the V3 high-yield
attempt that targeted a 60+ public score.

## Health Gate

The exact V2 canary confirmed the hidden evaluator was scoring again:

```text
54779273  Exact V2 canary rerun after grader pause
status: COMPLETE
totalBytes: 122
publicScore: 0.370
errorDescription: null
```

## Source

Used the historical V3 high-yield source from commit `8bb876f`:

```text
attack.py bytes: 42621
attack.py sha256: 43ade3dd0b2207698255f99a31b00fba5f201f87c112123da8442778f79f098b
DEFAULT_SUBMISSION_CANDIDATE_SET: submission-live
DEFAULT_SUBMISSION_CANDIDATE_LIMIT: 1000
```

This is the same source hash embedded in the original V3 artifact:

```text
submissions/high-yield-60-8bb876f-notebook
```

## Packaging

Added `--attack-file` support to `scripts/package_kaggle_notebook.py` so a
historical attack source can be embedded without modifying the repo's current
safe `attack.py` default.

Packaged under a fresh matching slug/title to avoid the prior lineage confusion:

```bash
PYTHONPATH=third_party/kaggle_ai_agent_security \
.venv/bin/python scripts/package_kaggle_notebook.py \
  --label high-yield-60-rerun-v3 \
  --kernel-slug ai-agent-security-high-yield-60-rerun \
  --title "AI Agent Security High Yield 60 Rerun" \
  --attack-file runs/submission-sources/v3-high-yield-60-8bb876f/attack.py \
  --attack-source-ref 8bb876f
```

Generated kernel:

```text
temperancehong/ai-agent-security-high-yield-60-rerun
```

Normal notebook output verified:

```text
attack.py bytes: 42621
attack.py sha256: 43ade3dd0b2207698255f99a31b00fba5f201f87c112123da8442778f79f098b
submission.csv rows: gpt_oss_public, gpt_oss_private, gemma_public, gemma_private
```

## Submission

Submitted kernel version 1:

```bash
.venv/bin/kaggle competitions submit \
  -c ai-agent-security-multi-step-tool-attacks \
  -f submission.csv \
  -k temperancehong/ai-agent-security-high-yield-60-rerun \
  -v 1 \
  -m "High yield V3 60-score rerun after canary success"
```

Initial Kaggle status:

```text
54780086  High yield V3 60-score rerun after canary success
status: PENDING
totalBytes: 0
publicScore: null
errorDescription: null
url: /code/temperancehong/ai-agent-security-high-yield-60-rerun?scriptVersionId=335907732
```

## Decision

Hidden replay completed with the same format-error signature as the original
larger V3/V4 failures:

```text
54780086  High yield V3 60-score rerun after canary success
status: COMPLETE
totalBytes: 0
publicScore: null
errorDescription: Your notebook generated a submission file with incorrect format.
```

Because the exact V2 canary succeeded on the same day and the 21-candidate
static weak-family probe produced a valid `0.000` scorer output, treat this as
evidence that the 1,000-candidate live-fill V3 path is too expensive or brittle
under hidden replay.

Next action: use smaller static pilots from the proven `EXFILTRATION` path
before attempting any 650-800 candidate bank.
