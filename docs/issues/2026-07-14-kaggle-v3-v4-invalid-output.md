# 2026-07-14 Kaggle V3/V4 Invalid Output Failures

## Summary

The high-yield V3 submission and both V4 submissions did not merely score zero.
Kaggle marked them `COMPLETE`, but the API reports `publicScore = null`,
`totalBytes = 0`, and a hidden-rerun output-format error.

Current repo commit during investigation:

```text
92892ed Record V4 retry submission
```

Failed submissions:

```text
54647183  High yield live 1000 target for 60   COMPLETE  publicScore=null  totalBytes=0
54652641  Weak-cell V4 50 candidate probe      COMPLETE  publicScore=null  totalBytes=0
54665813  Retry weak-cell V4 kernel version 4  COMPLETE  publicScore=null  totalBytes=0
```

Known-good comparison:

```text
54642077  First probe sink-gap attack  COMPLETE  publicScore=0.360  totalBytes=152
```

## Kaggle API Evidence

Command:

```bash
.venv/bin/python - <<'PY'
from kaggle.api.kaggle_api_extended import KaggleApi
api = KaggleApi()
api.authenticate()
for sub in api.competition_submissions("ai-agent-security-multi-step-tool-attacks"):
    print(sub)
PY
```

All three failed submissions include:

```text
errorDescription: Your notebook generated a submission file with incorrect format.
Some examples causing this are: wrong number of rows or columns, empty values,
an incorrect data type for a value, or invalid submission values from what is expected.
```

This means the hidden competition rerun raised before producing a valid scorer
CSV. It is not evidence that the attack families transferred but scored zero.

## Notebook Lineage Problem

The same Kaggle notebook lineage was repeatedly renamed through mismatched
metadata `id`, `title`, and `code_file` values:

```text
V3 package:
  metadata id:    temperancehong/ai-agent-security-first-probe
  title:          AI Agent Security High Yield 60
  visible ref:    temperancehong/ai-agent-security-high-yield-60

V4 package:
  metadata id:    temperancehong/ai-agent-security-high-yield-60
  title:          AI Agent Security Weak Cell V4 Probe
  visible ref:    temperancehong/ai-agent-security-weak-cell-v4-probe
```

The Kaggle API now reports all submission URLs under the renamed
`ai-agent-security-weak-cell-v4-probe` slug. Pulling output by older refs or
script version ids returned the latest visible V4 output, so those endpoints are
not reliable for historical source forensics after the rename chain.

The packager has since been hardened to reject slug/title mismatch by default.

## Local Gateway Checks

I copied the exact V3 and current/V4 attack sources into ignored run folders and
ran the official `JEDAttackInferenceServer().run_local_gateway()` path with
`AICOMP_MODEL_NAMES=deterministic`.

Current/V4:

```text
Received 50 candidates
Replay summary: 0 findings, score 0.0
submission.csv written
```

V3:

```text
Total ops: 9004
Op breakdown: {'reset': 3002, 'interact': 3001, 'export_trace_dict': 3001}
Elapsed: 33.0s
Received 0 candidates
submission.csv written
```

These deterministic gateway checks show that the attack classes can serialize
candidates and the gateway can write a CSV locally. They do not reproduce the
Kaggle invalid-output error.

## Real-Model Risk Signal

A narrow GPT-OSS GGUF replay of 10 V4 candidates was interrupted after about
four minutes without completing:

```bash
GPT_OSS_MODEL_PATH=data/models/gpt-oss-20b/gpt-oss-20b-Q4_K_M.gguf \
PYTHONPATH=third_party/kaggle_ai_agent_security \
.venv/bin/python scripts/run_candidate_replay.py \
  --candidate-set submission-weak-v4 \
  --guardrail optimal_public \
  --agent gpt_oss_gguf \
  --max-candidates 10 \
  --verbosity quiet
```

The interruption occurred inside `llama_cpp` generation. This is not a replay
failure proof, but it is strong evidence that the later submissions were much
more expensive under the real model path than the deterministic checks implied.

## Likely Causes

Most likely V3 cause:

- The default V3 strategy attempted a 1,000-candidate live-fill run.
- In deterministic gateway mode it consumed 9,004 env operations and returned
  zero candidates.
- Under real GPT-OSS/Gemma, that strategy is likely to time out, exhaust the
  model server, or otherwise raise during generation/replay before CSV writing.

Most likely V4 cause:

- V4 returned 50 static weak-family candidates without live prefiltering.
- Local public-guardrail replay already predicted `0/50` under
  `optimal_public`.
- The hidden gateway invalidates the whole submission if any replay candidate
  raises, not just if it misses predicates. These weak candidates had not been
  batch-replayed with the real GPT-OSS/Gemma path before submission.

Cross-cutting packaging risk:

- Reusing one Kaggle notebook lineage while changing slug/title made result
  attribution confusing and may have contributed to Kaggle selecting or
  recording unexpected script versions.

## Decision

Treat V3 and both V4 attempts as invalid hidden-rerun failures, not as score
measurements.

Do not use V3 to conclude high-yield live-fill cannot score. Do not use V4 to
conclude the weak-family candidates cannot transfer. The submissions failed
before producing a valid scored output.

## Next Submission Rules

1. Use a fresh, matching Kaggle slug/title pair and never rename the kernel
   lineage between submissions.
2. Package with `--include-official-model-sources` to remove model-mount
   ambiguity, even though the first probe happened to score without it.
3. Submit a tiny known-good sink-gap sanity version first to verify the fresh
   Kaggle path produces a non-null `publicScore` and nonzero `totalBytes`.
4. Keep real-model replay budgets small. Avoid 1,000 live probes until a
   smaller real-model gateway run completes.
5. For static candidate probes, replay small real-model batches first and drop
   any candidate shape that throws, hangs, or requires excessive tool/model
   turns.
6. When polling Kaggle, inspect `errorDescription`, `totalBytes`, and
   `publicScore`; a blank score alone is not enough.

## Follow-Up Applied

The no-config default has been restored to the V2-style `full` path, whose
first 8 candidates are the sink-gap candidates that produced the successful
`0.360` public score. Notebook packaging now includes the official GGUF model
sources by default, with `--no-official-model-sources` reserved for
reproducing older artifacts.
