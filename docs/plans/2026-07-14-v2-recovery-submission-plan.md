# 2026-07-14 V2 Recovery Submission Plan

## Goal

Recover to the last known-good Kaggle submission behavior before trying another
score-seeking expansion.

The next submission should first prove that the Kaggle hidden-rerun path can
again produce a valid non-null score. Only after that should we spend a
submission on larger live-fill or weak-family probes.

## What V2 Got Right

V2 succeeded because it was boring in the right places:

- The notebook slug, title, and submitted kernel ref matched.
- The generated notebook wrote the expected `attack.py` and placeholder
  `submission.csv` during normal commit.
- The hidden rerun used the no-config `AttackAlgorithm(config={})` path.
- That no-config path was the bounded `full` candidate set:
  - default cap: 8 candidates;
  - first 8 candidates: known sink-gap family;
  - local GPT-OSS GGUF evidence: 6 findings, raw score 72, normalized score
    0.360.
- The attack did not attempt large live probing or unvetted static weak-family
  replay during the hidden run.

## What V3/V4 Taught Us

V3 failed because the no-config path became too ambitious:

- Default set changed to `submission-live`.
- Default target grew to 1,000 live-filled candidates.
- Local deterministic gateway smoke required 9,004 env ops and still returned
  zero candidates.
- Real GPT-OSS/Gemma hidden rerun likely timed out or raised before writing the
  scorer CSV.

V4 failed because the no-config path became too speculative:

- Default set changed to `submission-weak-v4`.
- It returned 50 static weak-family candidates with no live prefiltering.
- Local public-guardrail replay had already shown 0/50.
- A single replay exception can invalidate the whole hidden submission, and the
  candidates were not real-model batch vetted.

Both attempts also inherited notebook-lineage confusion from mismatched
slug/title metadata.

## Fixes Applied

- `DEFAULT_SUBMISSION_CANDIDATE_SET` is back to `full`, restoring the V2-style
  bounded no-config path.
- Regression tests now assert that the no-config candidate set is `full` and
  that `full` starts with the 8 sink-gap candidates.
- Notebook packaging now attaches the official GPT-OSS/Gemma GGUF model sources
  by default. Use `--no-official-model-sources` only to reproduce older
  submissions or perform diagnostics.
- The packager already refuses slug/title mismatch unless explicitly overridden.

## Next Submission Gate

Before pushing another competitive package:

```bash
PYTHONPATH=third_party/kaggle_ai_agent_security \
.venv/bin/python -m py_compile attack.py scripts/package_kaggle_notebook.py tests/test_replay_loop.py

PYTHONPATH=third_party/kaggle_ai_agent_security \
.venv/bin/python -m unittest discover -s tests

PYTHONPATH=third_party/kaggle_ai_agent_security \
.venv/bin/python -m aicomp_sdk.cli.main validate redteam attack.py
```

Then package a fresh sanity notebook with a new matching slug/title:

```bash
PYTHONPATH=third_party/kaggle_ai_agent_security \
.venv/bin/python scripts/package_kaggle_notebook.py \
  --label v2-sanity-recovery \
  --kernel-slug ai-agent-security-v2-sanity-recovery \
  --title "AI Agent Security V2 Sanity Recovery"
```

The manifest should include the official model sources automatically.

Submit only after the Kaggle normal notebook run confirms:

- `attack.py` hash matches the manifest;
- placeholder `submission.csv` has the four expected rows;
- kernel slug/title/ref are the fresh matching values.

Poll with the Python API, not just the table output, and require:

- `errorDescription is None`;
- `totalBytes > 0`;
- `publicScore` is non-null.

## Four-Type Sanity Variant

It is possible to test a few candidates from all four predicate families while
preserving the V2 submission style. The opt-in candidate set is:

```text
submission-four-type-sanity
```

Shape:

- 12 total bounded attempts.
- The first 8 are the known V2 sink-gap candidates.
- The tail adds 4 destructive-write probes.
- The attempted families are `EXFILTRATION`, `CONFUSED_DEPUTY`,
  `UNTRUSTED_TO_ACTION`, and `DESTRUCTIVE_WRITE`.
- The mode uses the V2 live-prefilter loop, not V4 static return: weak
  candidates that do not trigger predicates during attack generation are not
  returned for replay.

Use this only after the fresh V2 sanity recovery submission proves the Kaggle
path is valid again. To submit it, make a one-commit packaging branch that sets
`DEFAULT_SUBMISSION_CANDIDATE_SET` to `submission-four-type-sanity`, package with
a fresh matching slug/title, then restore the default afterward.

## Stop Conditions

Do not submit another high-yield or weak-family variant until the fresh sanity
submission proves the scorer path is valid.

Do not switch the default away from `full` unless the replacement has:

- a bounded no-config candidate count;
- real-model replay evidence;
- deterministic gateway completion;
- a written rollback plan.
