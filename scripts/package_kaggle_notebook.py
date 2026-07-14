from __future__ import annotations

import argparse
import base64
import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Final

REPO_ROOT: Final[Path] = Path(__file__).resolve().parents[1]
ATTACK_FILE: Final[Path] = REPO_ROOT / "attack.py"
SUBMISSIONS_DIR: Final[Path] = REPO_ROOT / "submissions"
COMPETITION_SLUG: Final[str] = "ai-agent-security-multi-step-tool-attacks"
DEFAULT_KERNEL_SLUG: Final[str] = "ai-agent-security-first-probe"
DEFAULT_KERNEL_TITLE: Final[str] = "AI Agent Security First Probe"
KAGGLE_USER: Final[str] = "temperancehong"
EXPECTED_IDS: Final[tuple[str, ...]] = (
    "gpt_oss_public",
    "gpt_oss_private",
    "gemma_public",
    "gemma_private",
)
OFFICIAL_GGUF_MODEL_SOURCES: Final[tuple[str, ...]] = (
    "llkh0a/gemma-4-26b-a4b-it-ud-q4-k-m-gguf/PyTorch/default/1",
    "llkh0a/gpt-oss-20b-gguf/PyTorch/default/1",
)


def sha256_bytes(data: bytes) -> str:
    """Return a SHA-256 digest for generated notebook provenance."""
    return hashlib.sha256(data).hexdigest()


def current_git_commit(*pathspec: str) -> str:
    """Return the short git commit for naming and provenance."""
    command = ["git", "rev-parse", "--short", "HEAD"]
    if pathspec:
        command = ["git", "log", "-1", "--format=%h", "--", *pathspec]

    try:
        return subprocess.check_output(
            command,
            cwd=REPO_ROOT,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def code_cell(source: str) -> dict[str, object]:
    """Return a minimal executable notebook code cell."""
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": source.splitlines(keepends=True),
    }


def markdown_cell(source: str) -> dict[str, object]:
    """Return a minimal notebook markdown cell."""
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": source.splitlines(keepends=True),
    }


def chunk_text(value: str, size: int = 76) -> list[str]:
    """Split encoded attack content into notebook-friendly chunks."""
    return [value[index : index + size] for index in range(0, len(value), size)]


def slugify_title(title: str) -> str:
    """Return the Kaggle-style slug implied by a notebook title."""
    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")


def build_notebook(attack_source: bytes, attack_sha256: str) -> dict[str, object]:
    """Return the Kaggle notebook JSON that writes attack.py and serves reruns."""
    encoded_chunks = chunk_text(base64.b64encode(attack_source).decode("ascii"))
    encoded_literal = "\n".join(f"    {chunk!r}," for chunk in encoded_chunks)
    expected_ids_literal = ",\n    ".join(repr(item) for item in EXPECTED_IDS)

    setup_source = """\
from pathlib import Path
import os
import sys

NOTEBOOK_MODE = "first_probe_submit"
COMPETITION_SLUG = "ai-agent-security-multi-step-tool-attacks"
IS_COMPETITION_RERUN = bool(os.getenv("KAGGLE_IS_COMPETITION_RERUN"))
WORKING_DIR = Path("/kaggle/working") if Path("/kaggle/working").exists() else Path.cwd()
WORKING_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(WORKING_DIR)
if str(WORKING_DIR) not in sys.path:
    sys.path.insert(0, str(WORKING_DIR))

print("NOTEBOOK_MODE:", NOTEBOOK_MODE)
print("IS_COMPETITION_RERUN:", IS_COMPETITION_RERUN)
print("WORKING_DIR:", WORKING_DIR)
"""

    attack_write_source = f"""\
import base64
import hashlib
import py_compile

ATTACK_PY_B64_CHUNKS = [
{encoded_literal}
]
ATTACK_SHA256 = {attack_sha256!r}
ATTACK_PATH = WORKING_DIR / "attack.py"

attack_bytes = base64.b64decode("".join(ATTACK_PY_B64_CHUNKS))
actual_sha256 = hashlib.sha256(attack_bytes).hexdigest()
assert actual_sha256 == ATTACK_SHA256, (actual_sha256, ATTACK_SHA256)
ATTACK_PATH.write_bytes(attack_bytes)
py_compile.compile(str(ATTACK_PATH), doraise=True)

source = ATTACK_PATH.read_text(encoding="utf-8")
assert "class AttackAlgorithm(AttackAlgorithmBase)" in source
assert "def run(" in source

print("attack.py written:", ATTACK_PATH)
print("attack.py bytes:", ATTACK_PATH.stat().st_size)
print("attack.py sha256:", actual_sha256)
"""

    submission_source = f"""\
import csv

SUBMISSION_PATH = WORKING_DIR / "submission.csv"
EXPECTED_IDS = [
    {expected_ids_literal}
]


def write_placeholder_submission() -> None:
    with SUBMISSION_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["Id", "Score"])
        for item_id in EXPECTED_IDS:
            writer.writerow([item_id, 0.0])


if IS_COMPETITION_RERUN:
    assert ATTACK_PATH.exists() and ATTACK_PATH.stat().st_size > 0
    print("Starting official JED attack inference server")
    from kaggle_evaluation.jed_attack_134815.jed_attack_inference_server import (
        JEDAttackInferenceServer,
    )

    JEDAttackInferenceServer().serve()
else:
    write_placeholder_submission()
    with SUBMISSION_PATH.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        assert reader.fieldnames == ["Id", "Score"]
    assert [row["Id"] for row in rows] == EXPECTED_IDS
    assert len(rows) == 4
    for row in rows:
        float(row["Score"])
    print("submission.csv placeholder written:", SUBMISSION_PATH)
    print(SUBMISSION_PATH.read_text(encoding="utf-8"))
"""

    notebook: dict[str, object] = {
        "cells": [
            markdown_cell(
                "# AI Agent Security First Probe\n\n"
                "This notebook writes the committed `attack.py` into `/kaggle/working`, "
                "emits a placeholder `submission.csv` for normal notebook commits, and "
                "starts the official JED attack inference server during competition reruns.\n"
            ),
            code_cell(setup_source),
            code_cell(attack_write_source),
            code_cell(submission_source),
        ],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {
                "codemirror_mode": {"name": "ipython", "version": 3},
                "file_extension": ".py",
                "mimetype": "text/x-python",
                "name": "python",
                "nbconvert_exporter": "python",
                "pygments_lexer": "ipython3",
                "version": "3.11.0",
            },
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    return notebook


def build_kernel_metadata(
    *,
    kernel_slug: str,
    title: str,
    code_file: str,
    is_private: bool,
    model_sources: list[str],
) -> dict[str, object]:
    """Return Kaggle kernel metadata for a competition notebook."""
    return {
        "id": f"{KAGGLE_USER}/{kernel_slug}",
        "title": title,
        "code_file": code_file,
        "language": "python",
        "kernel_type": "notebook",
        "is_private": is_private,
        "enable_gpu": True,
        "enable_tpu": False,
        "enable_internet": False,
        "keywords": [],
        "dataset_sources": [],
        "kernel_sources": [],
        "competition_sources": [COMPETITION_SLUG],
        "model_sources": model_sources,
        "machine_shape": "NvidiaTeslaT4",
    }


def build_submission_notebook(
    label: str,
    kernel_slug: str,
    title: str,
    *,
    model_sources: list[str],
) -> dict[str, str | int | list[str]]:
    """Create a Kaggle kernel folder that can be pushed as a notebook version."""
    attack_source = ATTACK_FILE.read_bytes()
    compile(attack_source.decode("utf-8"), str(ATTACK_FILE), "exec")

    repo_commit = current_git_commit()
    attack_source_commit = current_git_commit("attack.py")
    attack_sha256 = sha256_bytes(attack_source)

    output_dir = SUBMISSIONS_DIR / f"{label}-{repo_commit}-notebook"
    kernel_dir = output_dir / "kernel"
    kernel_dir.mkdir(parents=True, exist_ok=True)

    notebook_name = f"{kernel_slug}.ipynb"
    notebook_path = kernel_dir / notebook_name
    metadata_path = kernel_dir / "kernel-metadata.json"
    manifest_path = output_dir / "manifest.json"

    notebook = build_notebook(attack_source, attack_sha256)
    metadata = build_kernel_metadata(
        kernel_slug=kernel_slug,
        title=title,
        code_file=notebook_name,
        is_private=True,
        model_sources=model_sources,
    )

    notebook_bytes = (json.dumps(notebook, indent=1) + "\n").encode("utf-8")
    metadata_bytes = (json.dumps(metadata, indent=2) + "\n").encode("utf-8")
    notebook_path.write_bytes(notebook_bytes)
    metadata_path.write_bytes(metadata_bytes)

    manifest: dict[str, str | int] = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "repo_commit": repo_commit,
        "attack_source_commit": attack_source_commit,
        "attack_py_bytes": len(attack_source),
        "attack_py_sha256": attack_sha256,
        "kernel_ref": f"{KAGGLE_USER}/{kernel_slug}",
        "kernel_title": title,
        "kernel_dir": str(kernel_dir),
        "notebook": str(notebook_path),
        "notebook_bytes": len(notebook_bytes),
        "notebook_sha256": sha256_bytes(notebook_bytes),
        "metadata": str(metadata_path),
        "metadata_sha256": sha256_bytes(metadata_bytes),
        "model_sources": model_sources,
        "manifest": str(manifest_path),
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Package a Kaggle notebook submission.")
    parser.add_argument(
        "--label",
        default=datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S"),
        help="Submission directory label prefix.",
    )
    parser.add_argument("--kernel-slug", default=DEFAULT_KERNEL_SLUG)
    parser.add_argument("--title", default=DEFAULT_KERNEL_TITLE)
    parser.add_argument(
        "--allow-title-slug-mismatch",
        action="store_true",
        help=(
            "Permit a title whose Kaggle-style slug does not match --kernel-slug. "
            "Use only when intentionally relying on Kaggle title/id resolution."
        ),
    )
    parser.add_argument(
        "--include-official-model-sources",
        dest="include_official_model_sources",
        action="store_true",
        help=(
            "Attach the public GPT-OSS and Gemma GGUF Kaggle model sources used "
            "by the starter/public notebooks. This is the default; internet remains disabled."
        ),
    )
    parser.add_argument(
        "--no-official-model-sources",
        dest="include_official_model_sources",
        action="store_false",
        help=(
            "Do not attach the public GPT-OSS and Gemma GGUF model sources. "
            "Use only for reproducing older submissions or mount diagnostics."
        ),
    )
    parser.add_argument(
        "--model-source",
        action="append",
        default=[],
        help="Additional Kaggle model source ref to attach to kernel metadata.",
    )
    parser.set_defaults(include_official_model_sources=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    expected_slug = slugify_title(str(args.title))
    actual_slug = str(args.kernel_slug)
    if expected_slug != actual_slug and not args.allow_title_slug_mismatch:
        raise SystemExit(
            "Refusing to package notebook because --title implies slug "
            f"{expected_slug!r}, but --kernel-slug is {actual_slug!r}. "
            "Use a matching slug/title pair or pass --allow-title-slug-mismatch."
        )

    model_sources = list(args.model_source)
    if args.include_official_model_sources:
        model_sources = [*OFFICIAL_GGUF_MODEL_SOURCES, *model_sources]
    model_sources = list(dict.fromkeys(model_sources))
    manifest = build_submission_notebook(
        str(args.label),
        str(args.kernel_slug),
        str(args.title),
        model_sources=model_sources,
    )
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
