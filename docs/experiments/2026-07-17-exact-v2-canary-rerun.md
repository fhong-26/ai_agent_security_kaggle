# 2026-07-17 Exact V2 Canary Rerun

## Goal

Resubmit the exact notebook/source combination that previously scored, to test
whether the Kaggle hidden evaluator is working again after the 2026-07-14
format-error wave.

## Artifact

Used the existing completed Kaggle kernel:

```text
temperancehong/ai-agent-security-first-probe version 1
```

This kernel was created from the archived V2 notebook folder:

```text
submissions/first-probe-kernel-6ab1381-notebook/kernel
```

Verification before submission:

```text
kernel ref: temperancehong/ai-agent-security-first-probe
title: AI Agent Security First Probe
model_sources: []
attack.py bytes: 18854
attack.py sha256: 5c6e5d63d47e30f1695d0149b649fef6708b34954e298e5c63009c692e9ca53c
```

This is the same archived V2 source hash that produced historical submission
`54642077` with public score `0.360`.

## Command

```bash
.venv/bin/kaggle competitions submit \
  -c ai-agent-security-multi-step-tool-attacks \
  -f submission.csv \
  -k temperancehong/ai-agent-security-first-probe \
  -v 1 \
  -m "Exact V2 canary rerun after grader pause"
```

## Initial Kaggle Status

```text
54779273  Exact V2 canary rerun after grader pause  PENDING
url: /code/temperancehong/ai-agent-security-first-probe?scriptVersionId=335057591
errorDescription: null
totalBytes: 0
publicScore: null
```

## Decision Gate

If this canary returns `errorDescription is None`, `totalBytes > 0`, and a
non-null `publicScore`, treat the hidden evaluator as likely healthy again and
resume the small-probe-to-static-bank ladder.

If it fails with the same format error, keep the 650-800 static bank blocked as
a platform-health risk rather than an attack-code issue.
