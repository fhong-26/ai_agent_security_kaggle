# Kaggle AI Agent Security Official SDK Snapshot

This directory contains the reusable code from the Kaggle `ai-agent-security-multi-step-tool-attacks` download.

Tracked here:

- `aicomp_sdk/`: official competition SDK code, CLI, scoring, guardrails, environments, attacks, and packaged benchmark fixtures.
- `kaggle_evaluation/`: official Kaggle inference/evaluation bridge code used by competition notebooks.
- `aicomp_sdk-3.1.2.dist-info/`: package metadata and license for the SDK snapshot.

Not tracked here:

- `build/`: duplicate generated package build output from the extracted archive.
- Raw `.zip` downloads and throwaway full archive extractions. Keep those under ignored `data/`.

The `aicomp_sdk/fixtures/` files are data, but they are packaged test fixtures that the SDK resolves at runtime. Keep them with the vendored SDK unless we later replace this snapshot with an installed dependency or a reproducible download/bootstrap script.

For local imports from the repository root, add this directory to `PYTHONPATH`:

```bash
export PYTHONPATH="$PWD/third_party/kaggle_ai_agent_security:$PYTHONPATH"
```
