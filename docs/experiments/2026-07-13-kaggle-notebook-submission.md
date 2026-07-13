# Kaggle Notebook Submission

## Date And Commits

- Date: 2026-07-13
- Notebook packager commit: `9243782`
- T4 metadata fix commit: `6ab1381`
- Attack source commit: `553bf37`

## Goal

Submit the first probe through Kaggle's notebook-based code competition flow after direct file upload was unavailable.

## Public Notebook Pattern

Public notebooks for this competition use a Kaggle Notebook that:

- writes `attack.py` under `/kaggle/working`;
- writes a placeholder `submission.csv` with the four required IDs during the normal notebook commit;
- starts `kaggle_evaluation.jed_attack_134815.jed_attack_inference_server.JEDAttackInferenceServer().serve()` for the hidden competition rerun;
- submits via `kaggle competitions submit -f submission.csv -k <owner>/<notebook> -v <version>`.

Local examples pulled for inspection:

- `pilkwang/ai-agent-v3-1-2-single-post-exfiltration`
- `yusuketogashi/ai-agent-sec-another-approach`
- `tensorliu/jed-attack-improved-nb`
- `gdataranger/jed-attack-starter-v3-1-2-fixed`

## Authentication

Kaggle CLI OAuth login completed:

```bash
.venv/bin/kaggle auth login --force
```

Result: CLI reported logged in as `temperancehong`.

## Notebook Packaging

Generated a private Kaggle notebook folder:

```bash
PYTHONPATH=third_party/kaggle_ai_agent_security \
.venv/bin/python scripts/package_kaggle_notebook.py \
  --label first-probe-kernel \
  --kernel-slug ai-agent-security-first-probe \
  --title "AI Agent Security First Probe"
```

Final generated folder:

```text
/Users/fanhong-rippletide/personal/ai_agent_security_kaggle/submissions/first-probe-kernel-6ab1381-notebook/kernel
```

Final kernel metadata:

- `id`: `temperancehong/ai-agent-security-first-probe`
- `is_private`: `true`
- `enable_gpu`: `true`
- `machine_shape`: `NvidiaTeslaT4`
- `enable_internet`: `false`
- `competition_sources`: `["ai-agent-security-multi-step-tool-attacks"]`

The notebook base64-encodes the committed `attack.py` and verifies this hash after writing:

```text
5c6e5d63d47e30f1695d0149b649fef6708b34954e298e5c63009c692e9ca53c
```

## Push Attempts

Version 1:

```bash
.venv/bin/kaggle kernels push -p submissions/first-probe-kernel-9243782-notebook/kernel
```

Result: pushed and completed, but competition submission failed with:

```text
Submission not allowed:  Your Notebook cannot use P100 GPUs in this competition.
```

Fix: add `machine_shape: "NvidiaTeslaT4"` to generated `kernel-metadata.json`.

Version 2:

```bash
.venv/bin/kaggle kernels push -p submissions/first-probe-kernel-6ab1381-notebook/kernel
```

Result: version 2 pushed and completed.

Downloaded output from version 2:

- `attack.py` SHA-256: `5c6e5d63d47e30f1695d0149b649fef6708b34954e298e5c63009c692e9ca53c`
- `submission.csv` SHA-256: `fceee1bc45ad4a438838af8421e0fa38d32ab8b87fb890565b45acd1ac332fb2`
- notebook log confirms `attack.py bytes: 18854`.

Placeholder CSV:

```csv
Id,Score
gpt_oss_public,0.0
gpt_oss_private,0.0
gemma_public,0.0
gemma_private,0.0
```

## Competition Submission

Submitted notebook version 2:

```bash
.venv/bin/kaggle competitions submit \
  -c ai-agent-security-multi-step-tool-attacks \
  -f submission.csv \
  -k temperancehong/ai-agent-security-first-probe \
  -v 2 \
  -m "First probe sink-gap attack"
```

Submission registration:

- Submission ref: `54642077`
- Date: `2026-07-13T10:07:46.387000`
- Description: `First probe sink-gap attack`
- Latest observed status during this note: `SubmissionStatus.PENDING`
- Public score: not yet available
- Private score: not yet available

## Decision

Notebook-based submission path is now functional. Continue polling submission `54642077` for the first real leaderboard score, then decide whether to keep the current sink-gap first-probe baseline or immediately switch to a higher-throughput candidate strategy.
