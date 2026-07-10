# 2026-07-10 Research Kickoff Action Log

## Context

- Goal: start the research phase for the Kaggle AI Agent Security - Multi-Step Tool Attacks competition.
- Starting commit: `c9064e8eae849357ea3a70d5712a7a2789e19e3c`.
- Ending commit for the research checkpoint: `ee458a3 Add multi-step agent security research`.
- Safety scope: offline benchmark research only; no live-system attack adaptation.

## Actions Taken

### Repository Inspection

- Checked `git status --short`; the tree was clean before research work began.
- Read the local SDK and competition-relevant files, including:
  - `third_party/kaggle_ai_agent_security/aicomp_sdk/attacks/contracts.py`
  - `third_party/kaggle_ai_agent_security/aicomp_sdk/core/predicates.py`
  - `third_party/kaggle_ai_agent_security/aicomp_sdk/core/tools/*`
  - `third_party/kaggle_ai_agent_security/aicomp_sdk/scoring.py`
  - `third_party/kaggle_ai_agent_security/aicomp_sdk/attacks/baselines/attacker_goexplore.py`
- Confirmed the local scoring and predicate mechanics for `EXFILTRATION`, `UNTRUSTED_TO_ACTION`, `DESTRUCTIVE_WRITE`, and `CONFUSED_DEPUTY`.

### Subagent Work

- Spawned Agent 1 for broad source discovery and synthesis.
  - Output file: `docs/research/agent1_multistep_agent_security_source_catalog_2026-07-10.md`.
  - Coverage: 30 arXiv papers, 35 repositories, 52 articles/posts/reports/discussions.
  - Identified top repositories for cloning: AgentDojo, InjecAgent, ToolEmu, AdaptiveAttackAgent, and GPTFuzz.
- Spawned Agent 2 for actionable problem decomposition.
  - Produced workstream plan covering fixture reconnaissance, attack families, mutation/coverage, trace replay, predicate scoring, guardrail probing, candidate selection, time budgeting, local evaluation, submission packaging, and experiment documentation.
- Spawned focused repo-reader agents for cloned research repos.
  - AgentDojo reader summarized task-suite architecture, injection tasks, `ToolKnowledgeAttack`, and evaluation mechanics.
  - BIPIA reader summarized dataset construction, payload families, insertion positions, and ASR-style evaluation.
  - garak reader summarized probe/detector architecture, latent injection, web injection, encoding, adaptive probes, and logging.
  - PyRIT reader summarized scenario/attack/executor/scorer/memory structure, XPIA workflow, and converter stacks.
  - HouYi reader summarized chromosome structure, framework/separator/disruptor optimization, harnesses, intentions, mutation, and fitness flow.

### Web And Source Research

- Used web search, arXiv search/API, GitHub search/metadata, and current security blog/report searches.
- Covered academic sources including AgentDojo, InjecAgent, BIPIA, ToolEmu, Agent Security Bench, WASP, AdaptiveAttackAgent, TopicAttack, ShadowCode, and related defense/design papers.
- Covered practical sources from Simon Willison, Trail of Bits, Embrace The Red, OWASP, PortSwigger, Anthropic, Microsoft, Invariant Labs, Docker, Unit 42, HiddenLayer, Lakera, GitHub Security, Orca, Oasis, Noma, WorkOS, Obsidian, and Promptfoo.
- Treated X/Twitter as a discovery layer only; durable articles, papers, and repos were preferred for documentation.

### Submodules Added

Added nine pinned research submodules under `third_party/research/`:

- `third_party/research/agentdojo` -> `https://github.com/ethz-spylab/agentdojo.git`
- `third_party/research/InjecAgent` -> `https://github.com/uiuc-kang-lab/InjecAgent.git`
- `third_party/research/ToolEmu` -> `https://github.com/ryoungj/ToolEmu.git`
- `third_party/research/AdaptiveAttackAgent` -> `https://github.com/uiuc-kang-lab/AdaptiveAttackAgent.git`
- `third_party/research/GPTFuzz` -> `https://github.com/sherdencooper/GPTFuzz.git`
- `third_party/research/BIPIA` -> `https://github.com/microsoft/BIPIA.git`
- `third_party/research/garak` -> `https://github.com/NVIDIA/garak.git`
- `third_party/research/PyRIT` -> `https://github.com/microsoft/PyRIT.git`
- `third_party/research/HouYi` -> `https://github.com/LLMSecurity/HouYi.git`

Pinned submodule commits at validation time:

- `AdaptiveAttackAgent`: `7ea08cf4424e689079c6bc6348e28fbb84a090eb`
- `BIPIA`: `a004b69ec0dd446e0afd461d98cb5e96e120a5d0`
- `GPTFuzz`: `0c26cccc3b19cd5eed91d6cb6912431cf2501762`
- `HouYi`: `cd2e06c8cecc2934b9e64f0cd0d38e9acc6898c8`
- `InjecAgent`: `f19c9f2c79a41046eb13c03c51a24c567a8ffa07`
- `PyRIT`: `a6d52abba093d720dcf375ef4702200137fcb2d8`
- `ToolEmu`: `ac4a7ab7ed8c7985d96231e214bd6b54304b7ddb`
- `agentdojo`: `089ed468cf3ed0322acc66b0211f26d9d90dbf60`
- `garak`: `adeac617f47f2f2c6818dbf4c821c2912e166aa7`

### Documentation Written

- Created canonical report:
  - `docs/research/multistep-agent-security-research-2026-07-10.md`
  - Includes executive synthesis, local SDK grounding, submodule summaries, 20 paper sections, 28 repository sections, 48 article/report sections, predicate mapping, actionable workstreams, next 2-3 day plan, backlog, implementation hypotheses, repo-reader addendum, and Agent 1 full catalog appendix.
- Created supporting source catalog:
  - `docs/research/agent1_multistep_agent_security_source_catalog_2026-07-10.md`
  - Includes 30 arXiv papers, 35 repositories, 52 articles/posts/reports/discussions, best-repo recommendations, and predicate-by-predicate synthesis.

## Validation

- Confirmed source-section counts:
  - Main report: 20 paper sections, 28 repo sections, 48 article sections.
  - Agent 1 catalog: 30 paper sections, 35 repo sections, 52 article sections.
- Ran secret-like string scan against docs and `.gitmodules`; no committed secret values found.
- Reviewed staged diff summary before commit.
- Confirmed final `git status --short` was clean after commit.
- Did not run executable tests because the checkpoint changed documentation and submodule pointers only.

## Commit

- Commit: `ee458a3 Add multi-step agent security research`
- Files added:
  - `.gitmodules`
  - `docs/research/agent1_multistep_agent_security_source_catalog_2026-07-10.md`
  - `docs/research/multistep-agent-security-research-2026-07-10.md`
  - Nine `third_party/research/*` submodule gitlinks.

## Decisions

- Kept both a canonical synthesized report and Agent 1's raw catalog.
- Appended Agent 1's catalog into the canonical report as an appendix so the user-requested "same markdown" report has all source sections in one place.
- Added more than the requested five submodules after Agent 1 identified repos more directly aligned with the competition.
- Preserved all work as benchmark/offline research and avoided live-target exploitation guidance.

## Next Best Actions

1. Build fixture reconnaissance over `web_corpus.json`, `mail_seed.json`, and `file_seed/`.
2. Implement a replay-gated local candidate scorer around `env.interact`, `env.export_trace_dict`, `eval_predicates`, and cell signatures.
3. Create first deterministic `AttackAlgorithm` prompt bank using AgentDojo-style tool-sequence families and BIPIA-style source/payload matrices.
4. Log each experiment under `docs/experiments/` with commit hash, commands, predicate hits, score estimate, replay evidence, and keep/mutate/discard decision.

