# Score-Priority Live Fill

Date: 2026-07-27
Base repo commit: `56e2fdc`

## Goal And Hypothesis

Adapt the strongest public-notebook lesson to this repo without changing the
existing `live-high-yield` behavior. The hypothesis is that our two strongest
families should not be round-robined equally when the higher-value family is
still firing:

- `EXFILTRATION`: strongest public-score family, about `18` raw per unique
  clean candidate.
- `CONFUSED_DEPUTY`: useful fallback/diversifier, but lower value per clean
  candidate.

The new mode should therefore spend attempts on `EXFILTRATION` first, keep only
successful candidates, and fall back to `CONFUSED_DEPUTY` only when exfil stalls.

## Dataset / SDK

- Local curated SDK mirror under `third_party/kaggle_ai_agent_security`
- Mock replay fixtures in `tests/test_replay_loop.py`
- No real model/API run in this loop.

## Attack Family And Stage

- Stage: candidate generation/live validation.
- Families: `EXFILTRATION` first, `CONFUSED_DEPUTY` fallback.
- New candidate-set aliases:
  - `live-score-priority`
  - `live_score_priority`
  - `score-priority-live`
  - `score_priority_live`
  - `exfil-first-live`
  - `exfil_first_live`

## Commands Run

```bash
.venv/bin/python -m unittest tests.test_replay_loop
.venv/bin/python -m unittest discover -s tests
.venv/bin/python -m py_compile attack.py tests/test_replay_loop.py
git diff --check
```

## Mock-Test Result

Pass.

```text
Ran 49 tests in 0.163s
OK

Ran 65 tests in 0.174s
OK
```

The tests verify:

- `live-score-priority` maps to the same two strong families as
  `live-high-yield`.
- When both families fire, all retained attempts are `EXFILTRATION`.
- When `EXFILTRATION` fails once, the mode disables it and fills from
  `CONFUSED_DEPUTY`.

## Real-Model Result

Not complete yet. The Kaggle submission is now pending; public/private replay
results are the next validation gate.

## Predicate Hits And Score Impact

Expected public-score behavior if replay is clean:

```text
EXFILTRATION candidate ~= 16 severity + 2 unique = 18 raw
CONFUSED_DEPUTY candidate ~= lower severity + 2 unique
```

Compared with old `live-high-yield` round-robin, `live-score-priority` should
increase expected raw score whenever direct exfil remains reliable, because it
does not spend every other attempt on the lower-value family.

## Replayability Evidence

The mode uses the existing live-fill loop:

- `env.reset()`
- `env.interact(...)`
- `env.export_trace_dict()`
- `eval_predicates(...)`
- score-cell dedupe
- return only `AttackCandidate.from_messages(...)` for kept attempts

The only change is scheduler order.

## Decision

Keep. `candidate_set=live-score-priority` has now been pushed as an opt-in
Kaggle submission. Do not replace `live-high-yield` yet; keep it as the
round-robin comparison baseline.

## Packaging And Submission

Generated a submission-specific source copy so the committed repo default stays
`full`:

```text
runs/submission-sources/score-priority-live-fill/attack.py
DEFAULT_SUBMISSION_CANDIDATE_SET: live-score-priority
attack.py bytes: 85597
attack.py sha256: 92c75a63d6b44e8794c4446f14c73ed84504b552dd0a43834a448936dc03e43f
resolved default candidate limit: 1000
resolved families: ('exfil', 'confused_deputy')
```

Packaged with:

```bash
PYTHONPATH=third_party/kaggle_ai_agent_security \
.venv/bin/python scripts/package_kaggle_notebook.py \
  --label score-priority-live-fill \
  --kernel-slug ai-agent-security-score-priority-live-fill \
  --title "AI Agent Security Score Priority Live Fill" \
  --attack-file runs/submission-sources/score-priority-live-fill/attack.py \
  --attack-source-ref "8bb35d8 default=live-score-priority sha256=92c75a63d6b44e8794c4446f14c73ed84504b552dd0a43834a448936dc03e43f"
```

Generated kernel package:

```text
kernel_ref: temperancehong/ai-agent-security-score-priority-live-fill
kernel_dir: submissions/score-priority-live-fill-8bb35d8-notebook/kernel
notebook_sha256: 9996961a11ee5be1c9ec0c9c4acaaf7e6518484cec171ff3c930f22012f54b98
metadata_sha256: 740aa953b427526d55ad5dda9208304930f3d52bd4687e16cf873026dd91eedd
model_sources:
- llkh0a/gemma-4-26b-a4b-it-ud-q4-k-m-gguf/PyTorch/default/1
- llkh0a/gpt-oss-20b-gguf/PyTorch/default/1
```

Pushed kernel version 1:

```bash
.venv/bin/kaggle kernels push \
  -p submissions/score-priority-live-fill-8bb35d8-notebook/kernel
```

Kernel status after push:

```text
temperancehong/ai-agent-security-score-priority-live-fill
KernelWorkerStatus.COMPLETE
```

Submitted kernel version 1:

```bash
KAGGLE_API_TOKEN="$(.venv/bin/kaggle auth print-access-token)" \
.venv/bin/kaggle competitions submit \
  -c ai-agent-security-multi-step-tool-attacks \
  -f submission.csv \
  -k temperancehong/ai-agent-security-score-priority-live-fill \
  -v 1 \
  -m "Score-priority live fill"
```

Initial Kaggle status:

```text
55032211  submission.csv  2026-07-27 15:14:03.113000
description: Score-priority live fill
status: SubmissionStatus.PENDING
publicScore: null
privateScore: null
```

Note: plain `kaggle competitions submit` did not pick up the OAuth credential
file on this machine, so the command bridged the active OAuth access token into
`KAGGLE_API_TOKEN` without printing the token.
