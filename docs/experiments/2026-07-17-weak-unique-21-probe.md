# 2026-07-17 Weak Unique 21-Cell Probe

## Goal

Probe the exact mined `10 + 11 = 21` unique scoring-cell bank from:

```text
runs/llm_candidates/template-mining-20260713T151556Z/unique_scoring_cells.jsonl
```

This submission intentionally keeps the V2-style static return path: no live
prefiltering, just replayable `AttackCandidate.from_messages(...)` candidates.

## Source

Added an opt-in static set in commit `6aa69a5`:

```text
candidate_set: submission-weak-unique-21
candidate count: 21
family mix: 10 UNTRUSTED_TO_ACTION, 11 DESTRUCTIVE_WRITE
repo default remains: full
```

Generated submission source:

```text
runs/submission-sources/weak-unique-21-probe/attack.py
DEFAULT_SUBMISSION_CANDIDATE_SET: submission-weak-unique-21
attack.py bytes: 82573
attack.py sha256: 15281d8fe48c34f2bec516667abad5794b513f27306edb3833bb1831cf7179a6
```

## Validation

Local checks:

```bash
PYTHONPATH=third_party/kaggle_ai_agent_security \
.venv/bin/python -m py_compile attack.py scripts/package_kaggle_notebook.py tests/test_replay_loop.py

PYTHONPATH=third_party/kaggle_ai_agent_security \
.venv/bin/python -m unittest discover -s tests

PYTHONPATH=third_party/kaggle_ai_agent_security \
.venv/bin/python -m aicomp_sdk.cli.main validate redteam attack.py

git diff --check
```

Results:

```text
57 tests passed
SDK validation passed
diff check passed
```

Downloaded Kaggle output verified:

```text
runs/kaggle-weak-unique-21-probe-output-20260717T095932Z/attack.py
sha256: 15281d8fe48c34f2bec516667abad5794b513f27306edb3833bb1831cf7179a6
DEFAULT_SUBMISSION_CANDIDATE_SET: submission-weak-unique-21
resolved candidate count: 21
submission.csv rows: gpt_oss_public, gpt_oss_private, gemma_public, gemma_private
```

## Packaging

```bash
PYTHONPATH=third_party/kaggle_ai_agent_security \
.venv/bin/python scripts/package_kaggle_notebook.py \
  --label weak-unique-21-probe \
  --kernel-slug ai-agent-security-weak-unique-21-probe \
  --title "AI Agent Security Weak Unique 21 Probe" \
  --attack-file runs/submission-sources/weak-unique-21-probe/attack.py \
  --attack-source-ref "6aa69a5 default=submission-weak-unique-21 sha256=15281d8fe48c34f2bec516667abad5794b513f27306edb3833bb1831cf7179a6"
```

Generated kernel:

```text
temperancehong/ai-agent-security-weak-unique-21-probe version 1
notebook sha256: 417177320610a7277c1edef93d85de954f339bda58bd4a86a6682d56e6dce98d
model_sources:
- llkh0a/gemma-4-26b-a4b-it-ud-q4-k-m-gguf/PyTorch/default/1
- llkh0a/gpt-oss-20b-gguf/PyTorch/default/1
```

## Submission

Initial CLI attempt used a local output path for `-f` and failed:

```text
400 Client Error: Bad Request ... CreateCodeSubmission
```

Root cause: code competition submissions expect the kernel output filename,
not the local path to the downloaded file.

Successful API-equivalent call used:

```text
file_name: submission.csv
kernel: temperancehong/ai-agent-security-weak-unique-21-probe
kernel_version: 1
message: Weak unique 21-cell bank probe
```

Initial Kaggle status:

```text
54780348  Weak unique 21-cell bank probe
status: PENDING
publicScore: null
```

## Decision

Wait for hidden replay. If this succeeds, the exact 21-cell bank is safe to
compare against the broader V4 weak-cell submissions. If it fails while the V2
canary remains healthy, suspect either weak-family transfer brittleness or
private guardrail blocking rather than notebook packaging.
