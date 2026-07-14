# 2026-07-14 V4 Blank Score / Failed Weak-Cell Probe

## Summary

V4 did not produce a usable public score.

Kaggle lists the submission as complete, but the public score field is blank:

```text
54652641  Weak-cell V4 50 candidate probe  SubmissionStatus.COMPLETE  publicScore=
```

This is different from V2, which completed with a visible score:

```text
54642077  First probe sink-gap attack  SubmissionStatus.COMPLETE  publicScore=0.360
```

## What V4 Was Trying To Measure

V4 was a small 50-candidate transfer probe for the two weak families that had not scored for us before:

```text
25 UNTRUSTED_TO_ACTION
25 DESTRUCTIVE_WRITE
```

The candidate set was static:

```text
DEFAULT_SUBMISSION_CANDIDATE_SET = "submission-weak-v4"
DEFAULT_SUBMISSION_CANDIDATE_LIMIT = 50
```

## Evidence

Local validation before submission:

```text
py_compile: passed
unit tests: 54 passed
SDK validate redteam attack.py: passed
git diff --check: clean
```

Local deterministic replay without guardrail:

```text
attempts=50 hits=50 kept=35 raw_estimate=998
```

Predicate mix under no guardrail:

```text
50 UNTRUSTED_TO_ACTION
38 DESTRUCTIVE_WRITE
26 EXFILTRATION
```

Local deterministic replay with `optimal_public` guardrail:

```text
attempts=50 hits=0 kept=0 raw_estimate=0
```

That means V4 was already expected to be weak against the public guardrail. A zero/tiny score would not have been surprising.

## Packaging Problem Found

The V4 package had a kernel title/id mismatch:

```json
{
  "id": "temperancehong/ai-agent-security-high-yield-60",
  "title": "AI Agent Security Weak Cell V4 Probe",
  "code_file": "ai-agent-security-high-yield-60.ipynb"
}
```

Kaggle resolved the visible kernel ref as:

```text
temperancehong/ai-agent-security-weak-cell-v4-probe
```

But the local manifest still recorded:

```text
temperancehong/ai-agent-security-high-yield-60
```

This mismatch made the final Kaggle rerun harder to reason about and may have contributed to the blank score behavior. The notebook commit itself did complete and wrote the expected `attack.py` hash.

## Decision

Treat V4 as a failed probe.

Do not use V4 as evidence that the mined weak-family templates transfer. The local public-guardrail result is still the stronger signal:

```text
submission-weak-v4 / optimal_public -> 0/50
```

## Fix Applied

The package script now refuses to package a notebook when the Kaggle-style slug implied by `--title` does not match `--kernel-slug`, unless `--allow-title-slug-mismatch` is explicitly passed.

## Recommended Next Action

For the next submission:

1. Use a clean matching slug/title pair.
2. First submit a small known-good high-yield sanity version to verify the Kaggle submission path still produces a visible score.
3. Then test weak-family probes only after they pass at least one stricter local replay gate or are mixed behind known-good scoring candidates.

