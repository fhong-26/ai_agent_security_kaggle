# First Probe Submission Prep

## Date And Commits

- Date: 2026-07-13
- Packaging commit: `9de58b9`
- Last attack-code commit: `553bf37`
- Prior score evidence commit: `84ae294`

## Goal

Prepare the first Kaggle red-team probe artifact without uploading it.

## Artifact

- Upload candidate: `/Users/fanhong-rippletide/personal/ai_agent_security_kaggle/submissions/first-probe-9de58b9/submission.zip`
- Raw file copy: `/Users/fanhong-rippletide/personal/ai_agent_security_kaggle/submissions/first-probe-9de58b9/attack.py`
- Manifest: `/Users/fanhong-rippletide/personal/ai_agent_security_kaggle/submissions/first-probe-9de58b9/manifest.json`
- Zip root member: `attack.py`
- `attack.py` bytes: `18854`
- `attack.py` SHA-256: `5c6e5d63d47e30f1695d0149b649fef6708b34954e298e5c63009c692e9ca53c`
- `submission.zip` bytes: `4879`
- `submission.zip` SHA-256: `d77f6ba76604bf3547e31a4adc3bbf6d2b1e5fdd78711389f890c20d444a15d3`

The zip contains exactly one root-level file:

```text
attack.py
```

## Packaging Command

```bash
PYTHONPATH=third_party/kaggle_ai_agent_security .venv/bin/python scripts/package_submission.py --label first-probe
```

## Validation

```bash
PYTHONPATH=third_party/kaggle_ai_agent_security .venv/bin/python -m py_compile attack.py scripts/run_candidate_replay.py scripts/package_submission.py tests/test_replay_loop.py
```

Result: passed.

```bash
PYTHONPATH=third_party/kaggle_ai_agent_security .venv/bin/python -m unittest discover -s tests
```

Result: 16 tests passed.

```bash
PYTHONPATH=third_party/kaggle_ai_agent_security .venv/bin/python -m aicomp_sdk.cli.main validate redteam submissions/first-probe-9de58b9/attack.py
```

Result: valid Python syntax, imports, and red-team `AttackAlgorithm` structure.

```bash
PYTHONPATH=third_party/kaggle_ai_agent_security .venv/bin/python -m aicomp_sdk.cli.main evaluate redteam submissions/first-probe-9de58b9/attack.py --agent deterministic --env sandbox --budget-s 30 --verbosity progress --artifacts-dir evaluation_artifacts/submission-prep-deterministic-9de58b9
```

Result: evaluator completed against the packaged copy. Deterministic score was `0.00`, which is expected for this attack family and is not the score evidence used for submission readiness.

The SDK zip loader was also checked against `submissions/first-probe-9de58b9/submission.zip`; it loaded `AttackAlgorithm` successfully from root member `attack.py`.

## Score Evidence

The submission artifact contains the same `attack.py` hash as the previously scored local GPT-OSS GGUF run:

- Local agent: `gpt_oss_gguf`
- Guardrail: `optimal_public`
- Env: `sandbox`
- Default attack config: no override
- Gentle timebox: `AttackRunConfig(time_budget_s=600, max_steps=50, max_tool_hops=8)`, `budget_s=720`
- Result: 6 findings, raw score `72.0`, normalized local score `0.36000000000000004`

The score evidence is documented in `docs/experiments/2026-07-13-default-sink-gap-priority.md`.

## Upload Status

No upload was performed. The local `kaggle` CLI was not found, and no `~/.kaggle/kaggle.json` file was present during this prep check. Use the Kaggle web UI to upload the zip, or install/configure the Kaggle CLI before command-line submission.

## Decision

Ready for first probe submission. This is an okay sanity-check submission, not a competitive final score. Submit the zip to get a real leaderboard/private-evaluator signal, then use that score to decide whether to keep mutating sink-gap families or pivot to higher-diversity trace families.
