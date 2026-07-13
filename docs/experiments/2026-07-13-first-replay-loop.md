# 2026-07-13 First Replay Loop

## Date And Commit

- Date: 2026-07-13
- Git commit hash: `bfe68fa`
- Goal: build the first mock-to-submission loop from public fixtures to replayable attack output.
- Hypothesis: deterministic public-fixture replay should give us a measurable local loop even when the default public guardrail blocks early candidate families.

## Source And Scope

- Dataset/SDK source: `third_party/kaggle_ai_agent_security/aicomp_sdk/fixtures`
- Fixture counts observed by the replay harness:
  - Web pages: 19679
  - Inbox emails: 8746
  - File fixtures: 24
- Fixture handling: fixture IDs, filenames, counts, and safe sampled snippets only. Sensitive-looking file names and sensitive-looking lines are redacted in run logs.
- Stage targeted: first full coding loop, deterministic replay, score-cell dedupe, and official evaluator compatibility.
- Mock-test definition: deterministic/local validation using the real SDK and public fixtures, not the private Kaggle evaluation set.

## Attack Families

- Replay-first exfil probes from public web pages.
- Web/email-to-action probes for `UNTRUSTED_TO_ACTION`.
- Confused-deputy email send probes.
- Guarded low-count protected-file write/delete probes.
- Deterministic variants include source ID, role frame, topic bridge, action target, and sink/action framing.

## Commands Run

```bash
PYTHONPATH=third_party/kaggle_ai_agent_security python3 -m py_compile attack.py scripts/run_candidate_replay.py tests/test_replay_loop.py
```

Result: passed on syntax, but subsequent SDK imports under Homebrew `python3` failed because that interpreter did not have `pydantic`.

```bash
PYTHONPATH=third_party/kaggle_ai_agent_security .venv/bin/python -m py_compile attack.py scripts/run_candidate_replay.py tests/test_replay_loop.py
PYTHONPATH=third_party/kaggle_ai_agent_security .venv/bin/python -m unittest discover -s tests
```

Result: 7 unit tests passed.

```bash
PYTHONPATH=third_party/kaggle_ai_agent_security .venv/bin/python scripts/run_candidate_replay.py --candidate-set smoke --max-candidates 10
```

Result: wrote `runs/candidate-replay-20260713T072619Z.jsonl`; attempts 10, predicate hits 0, kept 0, raw score estimate 0.

```bash
PYTHONPATH=third_party/kaggle_ai_agent_security .venv/bin/python -m aicomp_sdk.cli.main validate redteam attack.py
PYTHONPATH=third_party/kaggle_ai_agent_security .venv/bin/python -m aicomp_sdk.cli.main test redteam attack.py --agent deterministic --budget-s 30 --verbosity debug
```

Result: SDK validation passed. Deterministic red-team evaluation completed in 0.5s with 0 findings, 0 unique cells, raw score 0.00, normalized attack score 0.00. Local SDK history artifact: `.aicomp/history/attack_20260713_092624.json`.

## Predicate And Score Evidence

- Replay harness predicate hits: 0 of 10 smoke candidates.
- Official deterministic evaluator findings: 0.
- Score impact: 0 raw, 0 normalized.
- Replayability evidence: `attack.py` imports and validates under the official CLI, and official deterministic replay finishes without invalid candidate errors.
- Failure analysis: the default `OptimalGuardrail` blocks or suppresses the current public deterministic families before score predicates fire. This is acceptable for the first loop because the objective was a measurable harness and Kaggle-compatible return path, not a scored attack yet.

## Real-Model Result

- GPT-OSS/Gemma checks: skipped in this pass; no local model configuration was exercised.
- OpenAI check: skipped in this pass; no paid/API run was needed for the deterministic loop.

## Decision

- Keep the harness, `attack.py` scaffold, candidate validation, and score-cell dedupe.
- Mutate next: add guardrail-aware multi-turn variants that first create benign context, then trigger source-to-sink action without direct sensitive words. Prioritize variants that diversify `http.post`, `email.send`, and protected-file action signatures.
- Backlog: improve smoke set so at least one deterministic/no-guardrail or diagnostic mode can demonstrate a positive predicate path, while keeping `optimal_public` as the default scorer-like gate.
