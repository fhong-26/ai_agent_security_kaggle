# LLM-Guided Options For Kaggle AI Agent Security

Date: 2026-07-13
Repo head when researched: 45842fb

## Question

Can we use LLMs, either on Kaggle or elsewhere, to guide candidate generation for the AI Agent Security competition?

## Rule Readback

I re-read the official Kaggle competition pages through the Kaggle CLI:

```bash
.venv/bin/kaggle competitions pages ai-agent-security-multi-step-tool-attacks --content --page-name rules
.venv/bin/kaggle competitions pages ai-agent-security-multi-step-tool-attacks --content --page-name "Code Requirements"
.venv/bin/kaggle competitions pages ai-agent-security-multi-step-tool-attacks --content --page-name Evaluation
```

Important rule facts:

- Submissions must be made through Kaggle Notebooks.
- Notebook internet access must be disabled.
- GPU Notebook runtime must be no more than 15 hours.
- Freely and publicly available external data is allowed, including pre-trained models.
- External data and models are acceptable unless specifically prohibited, but they must be reasonably accessible to all competitors and minimal cost.
- Small LLM subscription costs are given as an example that can be acceptable under the reasonableness standard.
- Open-source code used in the submitted model/code path must use an OSI-approved license that does not limit commercial use.
- Private code/data sharing outside the team is not allowed; public sharing must be on Kaggle competition forums/notebooks.
- Winners must be able to deliver code and documentation that reproduces the winning submission.

Baby-language version:

**We can use LLMs, but the submitted Kaggle notebook cannot call the internet.**

So:

- External hosted APIs during the Kaggle rerun: no, because internet is disabled.
- External hosted APIs before submission, for research/prompt generation: likely yes, if reasonably accessible/minimal cost and documented.
- Public Kaggle model assets attached to the notebook: yes.
- Private model weights or private prompt corpora: risky unless made reasonably/publicly accessible under the rules.

## What Public Notebooks Do

I checked local copies of public notebooks under `data/public_kaggle_kernels_20260713`.

Observed metadata pattern:

- All relevant competition notebooks have `enable_internet: false`.
- Most high-score notebooks use no extra model sources.
- Several public notebooks attach the same public Kaggle model sources:
  - `llkh0a/gemma-4-26b-a4b-it-ud-q4-k-m-gguf/PyTorch/default/1`
  - `llkh0a/gpt-oss-20b-gguf/PyTorch/default/1`
- Those model sources are also attached by the fixed starter notebook we downloaded.

Kaggle model listing showed:

- `llkh0a/gpt-oss-20b-gguf`, version 1, about 11.6 GB.
- `llkh0a/gemma-4-26b-a4b-it-ud-q4-k-m-gguf`, version 1, about 16.9 GB.

This means Kaggle-side offline LLM use is not forbidden by notebook metadata. The practical question is whether loading/inferencing those models inside our attack generation budget is worth the time.

## What Our Research Already Found

From `docs/research/multistep-agent-security-research-2026-07-10.md` and `docs/research/public-notebook-strategy-study-2026-07-13.md`:

- AgentDojo, InjecAgent, ToolEmu, ToolSword, PurpleLlama, garak, GPTFuzz, PromptBench, and prompt-injection writeups are useful as idea sources.
- The winning public pattern is not fancy LLM reasoning. It is cheap replayable candidate generation with trace validation.
- We did not find public notebooks calling OpenAI, Anthropic, Gemini API, or local `transformers` at notebook runtime to generate attacks.
- Public notebooks use the competition target model itself as the live calibration model through `env.interact(...)`.
- The most score-relevant LLM-guided idea from research is mutation plus feedback: generate prompt variants, run them, keep only variants that fire predicates, then scale the successful family.

## Allowed LLM-Guided Routes

### Route A: Offline LLM Candidate Factory

Use an external LLM locally before submission to generate candidate templates. Commit only deterministic prompt templates or a seed list into `attack.py`.

Pros:

- No Kaggle runtime cost.
- No notebook internet issue.
- Easy to document and reproduce if prompts and model/source are listed.

Cons:

- The generated prompts still need real replay validation.
- Private paid LLM use must remain reasonably accessible/minimal cost if it materially creates the submission.

Best use:

- Generate more variants for `UNTRUSTED_TO_ACTION` and `DESTRUCTIVE_WRITE`.
- Generate low-salience synonyms for `http.post` and `email.send` prompts.
- Generate paraphrase clusters, then local/Kaggle live-fill selects winners.

### Route B: Kaggle-Attached Offline LLM In The Notebook

Attach a public Kaggle model source and load it inside the notebook or `attack.py`.

Pros:

- Rule-compatible shape: internet stays disabled, model is public.
- Could adapt prompts inside the same environment.
- Uses models already seen in starter/public notebooks.

Cons:

- Very expensive in time and memory.
- GPT-OSS/Gemma are already the target models; loading another copy during `AttackAlgorithm.run` can steal budget from candidate replay.
- Inference generation may produce non-deterministic or overly verbose prompts unless tightly constrained.

Best use:

- A tiny first-stage generator that creates 20 to 50 candidate prompt variants, not hundreds.
- Only use if attached model loading is confirmed in a Kaggle dry run.
- Cache generated prompt families in memory and immediately validate with `env.interact`.

### Route C: Target-Model Self-Calibration

This is what strong notebooks already do: use `env.interact(...)` as the live model probe and keep successful candidates.

Pros:

- Directly measures the actual hidden replay model path.
- No extra model load.
- Already coded in our `submission-live`, `timeit`, and `live-burst` modes.

Cons:

- It can only test prompts we already know how to produce.
- It is not creative by itself.

Best use:

- Pair with Route A: offline LLM generates candidate families; target-model self-calibration chooses winners.

### Route D: External LLM API During Notebook Rerun

Do not plan on this.

The submitted notebook must have internet disabled, so external API calls to OpenAI, Anthropic, Gemini API, hosted Hugging Face, etc. should fail or make the notebook ineligible.

## What I Changed

I added an opt-in packager switch:

```bash
PYTHONPATH=third_party/kaggle_ai_agent_security .venv/bin/python scripts/package_kaggle_notebook.py \
  --label llm-guided-dryrun \
  --kernel-slug ai-agent-security-llm-guided-dryrun \
  --title "AI Agent Security LLM Guided Dryrun" \
  --include-official-model-sources
```

This keeps:

```json
"enable_internet": false
```

and adds:

```json
"model_sources": [
  "llkh0a/gemma-4-26b-a4b-it-ud-q4-k-m-gguf/PyTorch/default/1",
  "llkh0a/gpt-oss-20b-gguf/PyTorch/default/1"
]
```

Dry-run artifact created successfully at:

```text
submissions/llm-guided-dryrun-45842fb-notebook/kernel/kernel-metadata.json
```

## Recommended Experiments

### Experiment 1: Offline LLM Prompt Factory

Use an LLM outside Kaggle to produce 200 candidate templates:

- 80 exfil paraphrases
- 60 confused-deputy paraphrases
- 30 untrusted-to-action chains
- 30 destructive-write chains

Then run only our deterministic validator and small live-fill probes. Store only successful deterministic templates in `attack.py`.

This is the best score-per-hour path.

### Experiment 2: Kaggle Attached Model Smoke Test

Package a notebook with `--include-official-model-sources` and add a very small non-submission diagnostic cell that:

- lists `/kaggle/input`;
- checks whether the GGUF files are visible;
- imports `llama_cpp`;
- optionally loads only one model if the file path is found.

Do not submit this as the scoring variant until the notebook commit proves the model source mounts correctly.

### Experiment 3: Tiny In-Run LLM Mutator

Only after Experiment 2 works, test:

- load one small/public model;
- ask it for 10 paraphrases of one seed prompt;
- validate each with `env.interact`;
- keep winners.

Stop immediately if model load plus 10 generations costs more than the number of direct live-fill candidates it displaces.

### Experiment 4: Private-Guardrail Transfer Generator

Use offline LLM generation to make prompts less like the public leaderboard pattern:

- avoid direct `Call http.post once`;
- use operational language;
- vary `SECRET_MARKER` placement;
- test confused-deputy prompts without words like `send`, `email`, `upload`;
- keep `submission-live` as the fallback path.

## Decision

Do not put a big LLM into the default scoring path yet.

The best near-term architecture is:

```text
offline LLM generates candidate families
        ↓
local/mock validation removes broken candidates
        ↓
Kaggle env.interact live-fill keeps only firing candidates
        ↓
scale the cheap winners
```

In other words: use LLMs as a creative assistant before the run, not as a slow passenger inside every submitted replay.
