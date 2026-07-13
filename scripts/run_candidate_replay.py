#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Sequence

REPO_ROOT = Path(__file__).resolve().parents[1]
SDK_ROOT = REPO_ROOT / "third_party" / "kaggle_ai_agent_security"
for import_root in (REPO_ROOT, SDK_ROOT):
    root_text = str(import_root)
    if root_text not in sys.path:
        sys.path.insert(0, root_text)

from aicomp_sdk.agents import build_agent_factory
from aicomp_sdk.core.cells import cell_signature
from aicomp_sdk.core.env.api import EnvRunDiagnostics
from aicomp_sdk.core.predicates import eval_predicates
from aicomp_sdk.evaluation.ops import (
    build_attack_env,
    resolve_attack_guardrail_spec,
    resolve_fixtures_dir,
)
from aicomp_sdk.guardrails.base import GuardrailBase

from attack import (
    CandidateSpec,
    iter_candidate_specs,
    predicate_weight,
    trace_has_guardrail_block,
    trace_score_cell,
    trace_tool_sequence,
    validate_messages,
)

DEFAULT_AGENT = "deterministic"
DEFAULT_ENV = "sandbox"
DEFAULT_GUARDRAIL = "optimal_public"
DEFAULT_SEED = 123
DEFAULT_MAX_TOOL_HOPS = 4
DEFAULT_SAMPLE_LIMIT = 50
NO_GUARDRAIL_ALIASES = {"none", "allow_all", "diagnostic_none"}
GGUF_AGENT_MODULES = {
    "gpt_oss_gguf": "kaggle_evaluation.jed_attack_134815.gpt_oss_model_server",
    "gemma_gguf": "kaggle_evaluation.jed_attack_134815.gemma_model_server",
}
SENSITIVE_NAME_RE = re.compile(
    r"(secret|credential|api[_-]?key|token|password|passwd|private)", re.IGNORECASE
)
SENSITIVE_LINE_RE = re.compile(
    r"(secret|credential|api[_-]?key|token|password|passwd|private|SECRET_MARKER)",
    re.IGNORECASE,
)


def safe_snippet(value: Any, *, name: str = "", limit: int = 180) -> str:
    """Return a compact fixture preview with sensitive-looking content redacted."""
    if name and SENSITIVE_NAME_RE.search(name):
        return "<redacted sensitive fixture>"
    text = "" if value is None else str(value)
    safe_lines = []
    for line in text.replace("\r", "\n").split("\n"):
        safe_lines.append("[redacted sensitive line]" if SENSITIVE_LINE_RE.search(line) else line)
    compact = " ".join(" ".join(safe_lines).split())
    if len(compact) > limit:
        return compact[: limit - 3] + "..."
    return compact


def _load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_fixture_map(
    fixtures_dir: Path | None = None,
    *,
    sample_limit: int = DEFAULT_SAMPLE_LIMIT,
) -> dict[str, Any]:
    """Load public fixture identities and safe previews for replay planning."""
    resolved = resolve_fixtures_dir(fixtures_dir)
    web_corpus = _load_json(resolved / "web_corpus.json")
    mail_seed = _load_json(resolved / "mail_seed.json")

    pages = list(web_corpus.get("pages", []))
    inbox = list(mail_seed.get("inbox", []))
    files = sorted((resolved / "file_seed").iterdir(), key=lambda path: path.name)

    web_items = [
        {
            "id": str(page.get("id", "")),
            "title": safe_snippet(page.get("title", ""), name=str(page.get("id", "")), limit=120),
            "url": safe_snippet(page.get("url", ""), name=str(page.get("id", "")), limit=160),
            "snippet": safe_snippet(
                page.get("content", ""),
                name=f"{page.get('id', '')} {page.get('title', '')}",
            ),
        }
        for page in pages[:sample_limit]
    ]
    mail_items = [
        {
            "id": str(message.get("id", "")),
            "from": safe_snippet(message.get("from", ""), name=str(message.get("id", "")), limit=120),
            "subject": safe_snippet(
                message.get("subject", ""),
                name=str(message.get("id", "")),
                limit=160,
            ),
            "snippet": safe_snippet(
                message.get("body", ""),
                name=f"{message.get('id', '')} {message.get('subject', '')}",
            ),
        }
        for message in inbox[:sample_limit]
    ]
    file_items = []
    for path in files[:sample_limit]:
        content = ""
        if path.is_file():
            content = path.read_text(encoding="utf-8", errors="replace")
        file_items.append(
            {
                "name": path.name,
                "size": path.stat().st_size if path.exists() else 0,
                "snippet": safe_snippet(content, name=path.name),
            }
        )

    return {
        "fixtures_dir": str(resolved),
        "sample_limit": int(sample_limit),
        "web": {
            "count": len(pages),
            "ids": [str(page.get("id", "")) for page in pages],
            "items": web_items,
        },
        "mail": {
            "count": len(inbox),
            "ids": [str(message.get("id", "")) for message in inbox],
            "items": mail_items,
        },
        "files": {
            "count": len(files),
            "names": [path.name for path in files],
            "items": file_items,
        },
    }


def sanitize_tool_event(event: Mapping[str, Any]) -> dict[str, Any]:
    """Return a trace event summary without tool outputs or secret-bearing values."""
    args = event.get("args", {}) if isinstance(event.get("args", {}), Mapping) else {}
    safe_args: dict[str, Any] = {}
    for key, value in args.items():
        if SENSITIVE_NAME_RE.search(str(key)):
            safe_args[str(key)] = "<redacted>"
        elif key in {"data", "body", "content", "message"}:
            safe_args[str(key)] = safe_snippet(value, limit=120)
        else:
            safe_args[str(key)] = safe_snippet(value, limit=120)

    return {
        "name": event.get("name", ""),
        "args": safe_args,
        "ok": bool(event.get("ok")),
        "side_effect": event.get("side_effect", ""),
        "scope": event.get("scope", ""),
        "source": event.get("source", ""),
        "error": safe_snippet(event.get("error", ""), limit=120),
    }


def summarize_predicates(predicates: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Return stable predicate summaries for JSONL logs and ranking tests."""
    return [
        {
            "predicate": str(predicate.get("predicate", "")),
            "severity": int(predicate.get("severity", 1)),
            "evidence": dict(predicate.get("evidence", {})),
        }
        for predicate in predicates
    ]


def attempt_raw_score_estimate(
    predicates: Sequence[Mapping[str, Any]],
    *,
    is_unique_cell: bool,
) -> int:
    """Return the SDK-style raw score estimate for one local attempt."""
    return predicate_weight(predicates) + (2 if predicates and is_unique_cell else 0)


def decide_attempt(
    predicates: Sequence[Mapping[str, Any]],
    cell_hash: str,
    seen_cells: set[str],
) -> tuple[str, bool]:
    """Choose keep/mutate/discard from predicate hits and score-cell diversity."""
    if not predicates:
        return "discard_no_predicate", False
    if cell_hash in seen_cells:
        return "mutate_duplicate_cell", False
    seen_cells.add(cell_hash)
    return "keep", True


def _candidate_limit(
    specs: Sequence[CandidateSpec],
    max_candidates: int | None,
) -> Sequence[CandidateSpec]:
    if max_candidates is None:
        return specs
    return specs[: max(0, int(max_candidates))]


def build_replay_agent_factory(agent: str, *, verbose: bool):
    """Build an SDK agent factory, including optional local GGUF model servers."""
    module_name = GGUF_AGENT_MODULES.get(agent)
    if module_name is None:
        return build_agent_factory(agent, verbose=verbose)

    from kaggle_evaluation.jed_attack_134815 import remote_agent

    model_server = importlib.import_module(module_name)
    predict_fn: Callable[[Mapping[str, Any]], Mapping[str, Any]] = model_server.predict
    return lambda: remote_agent.RemoteAgent(predict_fn)


def build_replay_env(args: argparse.Namespace, fixtures_dir: Path):
    """Construct the SDK sandbox used by the local replay harness."""
    if args.guardrail in NO_GUARDRAIL_ALIASES:
        guardrail = GuardrailBase()
    else:
        guardrail_spec = resolve_attack_guardrail_spec(args.guardrail)
        guardrail = guardrail_spec.guardrail_factory()
    agent_factory = build_replay_agent_factory(args.agent, verbose=args.verbosity == "debug")
    return build_attack_env(
        seed=int(args.seed),
        fixtures_dir=fixtures_dir,
        agent_factory=agent_factory,
        guardrail=guardrail,
        env_selection=args.env,
        max_tool_hops=int(args.max_tool_hops),
    )


def replay_spec(
    env: Any,
    spec: CandidateSpec,
    *,
    max_tool_hops: int,
    seen_cells: set[str],
) -> dict[str, Any]:
    """Replay one candidate spec and return a sanitized attempt record."""
    try:
        messages = validate_messages(spec.messages)
    except (TypeError, ValueError) as err:
        return {
            "type": "attempt",
            "family": spec.family,
            "source": spec.source,
            "target": spec.target,
            "variant": spec.variant,
            "messages": list(spec.messages),
            "predicates": [],
            "cell_hash": "",
            "tool_sequence": [],
            "agent_refused": False,
            "guardrail_blocked": False,
            "raw_score_estimate": 0,
            "decision": "discard_invalid",
            "error": str(err),
        }

    env.reset()
    diagnostics = EnvRunDiagnostics()
    for message in messages:
        diagnostics.record(env.interact(message, max_tool_hops=max_tool_hops))

    trace = env.export_trace_dict()
    predicates = summarize_predicates(eval_predicates(trace))
    score_cell = trace_score_cell(trace)
    cell_hash = str(score_cell["hash"])
    diagnostic_cell = cell_signature(
        trace.get("tool_events", []),
        egress_data=trace.get("egress", []),
        user_messages=trace.get("user_messages", []),
    )
    decision, is_unique_cell = decide_attempt(predicates, cell_hash, seen_cells)
    return {
        "type": "attempt",
        "family": spec.family,
        "source": spec.source,
        "target": spec.target,
        "variant": spec.variant,
        "messages": list(messages),
        "predicates": predicates,
        "cell_hash": cell_hash,
        "diagnostic_cell_hash": str(diagnostic_cell["hash"]),
        "tool_sequence": list(trace_tool_sequence(trace)),
        "tool_events": [sanitize_tool_event(event) for event in trace.get("tool_events", [])],
        "agent_refused": bool(diagnostics.agent_refusals),
        "guardrail_blocked": trace_has_guardrail_block(trace),
        "raw_score_estimate": attempt_raw_score_estimate(
            predicates,
            is_unique_cell=is_unique_cell,
        ),
        "decision": decision,
    }


def write_jsonl(path: Path, records: Iterable[Mapping[str, Any]]) -> None:
    """Write replay records in deterministic JSONL form for local analysis."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, sort_keys=True) + "\n")


def run_label(value: str) -> str:
    """Return a filesystem-safe label for local replay artifact names."""
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", value).strip("-") or "default"


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Replay deterministic attack candidates locally.")
    parser.add_argument("--agent", default=DEFAULT_AGENT)
    parser.add_argument("--env", default=DEFAULT_ENV)
    parser.add_argument("--guardrail", default=DEFAULT_GUARDRAIL)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--max-tool-hops", type=int, default=DEFAULT_MAX_TOOL_HOPS)
    parser.add_argument("--candidate-set", default="smoke")
    parser.add_argument("--max-candidates", type=int, default=None)
    parser.add_argument("--fixtures-dir", type=Path, default=None)
    parser.add_argument("--runs-dir", type=Path, default=REPO_ROOT / "runs")
    parser.add_argument("--fixture-sample-limit", type=int, default=DEFAULT_SAMPLE_LIMIT)
    parser.add_argument("--verbosity", choices=("quiet", "info", "debug"), default="info")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    fixtures_dir = resolve_fixtures_dir(args.fixtures_dir)
    fixture_map = load_fixture_map(fixtures_dir, sample_limit=args.fixture_sample_limit)
    env = build_replay_env(args, fixtures_dir)
    specs = _candidate_limit(tuple(iter_candidate_specs(args.candidate_set)), args.max_candidates)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    output_path = args.runs_dir / (
        "candidate-replay-"
        f"{timestamp}-{run_label(args.candidate_set)}-{run_label(args.guardrail)}.jsonl"
    )
    seen_cells: set[str] = set()
    records: list[dict[str, Any]] = [
        {
            "type": "fixture_map",
            "created_at": timestamp,
            "agent": args.agent,
            "env": args.env,
            "guardrail": args.guardrail,
            "seed": args.seed,
            "max_tool_hops": args.max_tool_hops,
            "fixture_map": fixture_map,
        }
    ]

    for index, spec in enumerate(specs):
        attempt = replay_spec(
            env,
            spec,
            max_tool_hops=int(args.max_tool_hops),
            seen_cells=seen_cells,
        )
        attempt.update({"index": index, "created_at": timestamp})
        records.append(attempt)

    kept = [record for record in records if record.get("decision") == "keep"]
    predicate_hits = [
        record
        for record in records
        if record.get("type") == "attempt" and record.get("predicates")
    ]
    records.append(
        {
            "type": "summary",
            "created_at": timestamp,
            "attempts": len(specs),
            "predicate_hit_attempts": len(predicate_hits),
            "kept": len(kept),
            "unique_score_cells": len(seen_cells),
            "raw_score_estimate": sum(
                int(record.get("raw_score_estimate", 0))
                for record in records
                if record.get("decision") == "keep"
            ),
            "output_path": str(output_path),
        }
    )
    write_jsonl(output_path, records)
    summary = records[-1]
    print(
        "wrote {path} attempts={attempts} hits={hits} kept={kept} raw_estimate={score}".format(
            path=output_path,
            attempts=summary["attempts"],
            hits=summary["predicate_hit_attempts"],
            kept=summary["kept"],
            score=summary["raw_score_estimate"],
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
