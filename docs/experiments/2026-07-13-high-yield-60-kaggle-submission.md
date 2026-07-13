# 2026-07-13 High-Yield 60 Kaggle Submission

## Date And Commit

- Date: 2026-07-13
- Attack/source commit: `8bb876f`
- Notebook package: `submissions/high-yield-60-8bb876f-notebook/`
- Notebook artifact SHA-256: `1e1a00877a8c79159eb517013bf7ea49d12814c768ef01ed1e383193523af186`
- `attack.py` SHA-256: `43ade3dd0b2207698255f99a31b00fba5f201f87c112123da8442778f79f098b`

## Goal

Submit the high-yield live-fill attack that targets normalized score 60 by defaulting to 1,000 generated candidates:

- 500 `EXFILTRATION`
- 500 `CONFUSED_DEPUTY`

Expected raw score if all replay like local 50-candidate probes:

```text
500 * 18 + 500 * 6 = 12,000 raw
12,000 / 200,000 * 1,000 = 60 normalized
```

## Packaging

```bash
PYTHONPATH=third_party/kaggle_ai_agent_security \
.venv/bin/python scripts/package_kaggle_notebook.py \
  --label high-yield-60 \
  --kernel-slug ai-agent-security-first-probe \
  --title "AI Agent Security High Yield 60"
```

Resulting package:

```text
submissions/high-yield-60-8bb876f-notebook/kernel
```

## Kaggle Push

The Kaggle OAuth token had expired, so it was refreshed:

```bash
.venv/bin/kaggle auth login --force
```

Then the notebook was pushed:

```bash
.venv/bin/kaggle kernels push -p submissions/high-yield-60-8bb876f-notebook/kernel
```

Result:

- Kernel ref: `temperancehong/ai-agent-security-high-yield-60`
- Kernel version: 3
- Kernel status: `COMPLETE`

Kaggle warned that the requested metadata slug/title did not match and resolved the kernel to `ai-agent-security-high-yield-60`.

## Competition Submission

```bash
.venv/bin/kaggle competitions submit \
  -c ai-agent-security-multi-step-tool-attacks \
  -f submission.csv \
  -k temperancehong/ai-agent-security-high-yield-60 \
  -v 3 \
  -m "High yield live 1000 target for 60"
```

Submission registration:

- Submission ref: `54647183`
- Date: `2026-07-13 13:03:18.983000`
- Description: `High yield live 1000 target for 60`
- Status at submission time: `SubmissionStatus.PENDING`

## Baseline Context

Previous first-probe submission:

- Submission ref: `54642077`
- Description: `First probe sink-gap attack`
- Status: `COMPLETE`
- Public score: `0.360`

## Next Action

Poll submission `54647183` until Kaggle reports the public score, then compare against the 60-target hypothesis.
