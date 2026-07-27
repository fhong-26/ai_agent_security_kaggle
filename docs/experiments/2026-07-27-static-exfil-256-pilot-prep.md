# 2026-07-27 Static EXFIL 256 Pilot Prep

## Goal

Scale the Kaggle-proven static `EXFILTRATION` family from 128 to 256 one-message
`http.post` candidates.

Hypothesis: the 128-candidate pilot transferred linearly to public score
`11.520`, so 256 candidates using the identical prompt shape should score:

```text
256 * (16 severity + 2 unique-cell bonus) / 200 = 23.04
```

This is the safe intermediate gate before trying a 384/400 candidate run for a
30+ public score.

## Source

Implementation commit:

```text
0faf5d0 Add static exfil 256 pilot
```

Changed `attack.py` by adding:

```text
DEFAULT_STATIC_EXFIL_256_CANDIDATE_LIMIT = 256
STATIC_EXFIL_256_CANDIDATE_SETS = {
  "static-exfil-256",
  "static_exfil_256",
  "submission-static-exfil-256",
  "submission_static_exfil_256",
}
```

The committed repo default remains:

```text
DEFAULT_SUBMISSION_CANDIDATE_SET = "full"
```

Generated submission source:

```text
runs/submission-sources/static-exfil-256-pilot/attack.py
DEFAULT_SUBMISSION_CANDIDATE_SET: submission-static-exfil-256
attack.py bytes: 84107
attack.py sha256: 66ca7a18fc8bc74111580d662feb35168331aa2a0083735eee75c2b11a97cd98
resolved default candidate limit: 256
available static specs: 2000
```

## Validation

Commands run:

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
py_compile passed
61 tests passed
SDK validation passed
diff check passed
```

Mock-test result: the new `submission-static-exfil-256` path returns 256 static
`AttackCandidate` rows without calling the live environment, preserving the same
one-message `http.post` shape as the 128 pilot.

Real-model result: not run locally. This path relies on Kaggle hidden replay as
the real validation gate, matching the prior 128 pilot workflow.

## Packaging

Packaged with:

```bash
PYTHONPATH=third_party/kaggle_ai_agent_security \
.venv/bin/python scripts/package_kaggle_notebook.py \
  --label static-exfil-256-pilot \
  --kernel-slug ai-agent-security-static-exfil-256-pilot \
  --title "AI Agent Security Static Exfil 256 Pilot" \
  --attack-file runs/submission-sources/static-exfil-256-pilot/attack.py \
  --attack-source-ref "0faf5d0 default=submission-static-exfil-256 sha256=66ca7a18fc8bc74111580d662feb35168331aa2a0083735eee75c2b11a97cd98"
```

Generated kernel package:

```text
kernel_ref: temperancehong/ai-agent-security-static-exfil-256-pilot
kernel_dir: submissions/static-exfil-256-pilot-0faf5d0-notebook/kernel
notebook_sha256: 050847328170fd17c1196696046055dd910b7d02cd956abea8d848e09d009d52
metadata_sha256: b74142340eb745ad7051012ed796281728d57b917f20177ba8c1004288407e08
model_sources:
- llkh0a/gemma-4-26b-a4b-it-ud-q4-k-m-gguf/PyTorch/default/1
- llkh0a/gpt-oss-20b-gguf/PyTorch/default/1
```

## Kaggle Push Status

Attempted:

```bash
.venv/bin/kaggle kernels push \
  -p submissions/static-exfil-256-pilot-0faf5d0-notebook/kernel
```

Result:

```text
Authentication required to call the Kaggle API.
```

Kaggle auth is not configured on this machine, so the kernel has not been pushed
or submitted yet.

## Resume Commands

After authenticating:

```bash
.venv/bin/kaggle auth login --force

.venv/bin/kaggle kernels push \
  -p submissions/static-exfil-256-pilot-0faf5d0-notebook/kernel

.venv/bin/kaggle kernels status \
  temperancehong/ai-agent-security-static-exfil-256-pilot
```

After the kernel completes, download and verify output:

```bash
OUT_DIR="runs/kaggle-static-exfil-256-pilot-output-$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$OUT_DIR"
.venv/bin/kaggle kernels output \
  temperancehong/ai-agent-security-static-exfil-256-pilot \
  -p "$OUT_DIR"
```

Then submit the kernel output filename:

```bash
.venv/bin/kaggle competitions submit \
  -c ai-agent-security-multi-step-tool-attacks \
  -f submission.csv \
  -k temperancehong/ai-agent-security-static-exfil-256-pilot \
  -v 1 \
  -m "Static EXFIL 256 pilot"
```

## Decision

Keep. The code, tests, validation, generated source, and notebook package are
ready. The only blocker is missing local Kaggle authentication.

If public score returns `23.040` with nonzero `totalBytes`, the next score move
is a 384 or 400 static EXFIL pilot to clear 30+.
