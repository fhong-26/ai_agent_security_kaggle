# 2026-07-14 V2 Exact Rerun Submission

## Goal

Submit a second small probe that is identical to the previously successful V2
first-probe artifact, while leaving the already-submitted V2 sanity recovery
probe running.

## Source Artifact

Used the archived generated notebook folder:

```text
submissions/first-probe-kernel-6ab1381-notebook/kernel
```

This is the old successful V2 notebook pattern:

- kernel ref: `temperancehong/ai-agent-security-first-probe`
- title: `AI Agent Security First Probe`
- GPU shape: `NvidiaTeslaT4`
- internet: disabled
- model sources: none
- embedded `attack.py` bytes: `18854`
- embedded `attack.py` SHA-256:
  `5c6e5d63d47e30f1695d0149b649fef6708b34954e298e5c63009c692e9ca53c`

The current repo `attack.py` was not used for this rerun.

## Commands

Pushed the archived notebook folder:

```bash
.venv/bin/kaggle kernels push \
  -p submissions/first-probe-kernel-6ab1381-notebook/kernel
```

Kaggle created a fresh recreated lineage version:

```text
temperancehong/ai-agent-security-first-probe version 1
```

Pulled the normal notebook output and verified:

```text
attack.py bytes: 18854
attack.py sha256: 5c6e5d63d47e30f1695d0149b649fef6708b34954e298e5c63009c692e9ca53c
submission.csv rows: gpt_oss_public, gpt_oss_private, gemma_public, gemma_private
```

Submitted the completed kernel version:

```bash
.venv/bin/kaggle competitions submit \
  -c ai-agent-security-multi-step-tool-attacks \
  -f submission.csv \
  -k temperancehong/ai-agent-security-first-probe \
  -v 1 \
  -m "Exact V2 first-probe rerun"
```

## Kaggle Result

Registered submission:

```text
54686411  Exact V2 first-probe rerun  PENDING  totalBytes=0  publicScore=null  errorDescription=null
```

Already-running comparison probe:

```text
54685964  V2 sanity recovery small probe  PENDING  totalBytes=0  publicScore=null  errorDescription=null
```

Known-good historical comparison:

```text
54642077  First probe sink-gap attack  COMPLETE  totalBytes=152  publicScore=0.360  errorDescription=null
```

## Decision

Wait for either small probe to complete with `errorDescription is None`,
`totalBytes > 0`, and non-null `publicScore` before attempting the 650-800
static bank.
