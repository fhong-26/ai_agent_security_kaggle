from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Final

REPO_ROOT: Final[Path] = Path(__file__).resolve().parents[1]
ATTACK_FILE: Final[Path] = REPO_ROOT / "attack.py"
SUBMISSIONS_DIR: Final[Path] = REPO_ROOT / "submissions"
ZIP_TIMESTAMP: Final[tuple[int, int, int, int, int, int]] = (1980, 1, 1, 0, 0, 0)


def sha256_file(path: Path) -> str:
    """Return a SHA-256 digest for a local submission artifact."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


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


def build_submission(label: str) -> dict[str, str | int]:
    """Create a ready-to-upload attack.py copy and zip artifact."""
    if not ATTACK_FILE.is_file():
        raise FileNotFoundError(f"missing {ATTACK_FILE}")

    compile(ATTACK_FILE.read_text(encoding="utf-8"), str(ATTACK_FILE), "exec")

    repo_commit = current_git_commit()
    attack_source_commit = current_git_commit("attack.py")
    output_dir = SUBMISSIONS_DIR / f"{label}-{repo_commit}"
    output_dir.mkdir(parents=True, exist_ok=True)

    attack_copy = output_dir / "attack.py"
    zip_path = output_dir / "submission.zip"
    manifest_path = output_dir / "manifest.json"

    shutil.copy2(ATTACK_FILE, attack_copy)

    zip_info = zipfile.ZipInfo("attack.py", date_time=ZIP_TIMESTAMP)
    zip_info.compress_type = zipfile.ZIP_DEFLATED
    with zipfile.ZipFile(zip_path, "w") as archive:
        archive.writestr(zip_info, ATTACK_FILE.read_bytes())

    manifest: dict[str, str | int] = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_commit": repo_commit,
        "repo_commit": repo_commit,
        "attack_source_commit": attack_source_commit,
        "attack_py": str(attack_copy),
        "attack_py_bytes": attack_copy.stat().st_size,
        "attack_py_sha256": sha256_file(attack_copy),
        "zip": str(zip_path),
        "zip_bytes": zip_path.stat().st_size,
        "zip_sha256": sha256_file(zip_path),
        "zip_root_member": "attack.py",
        "manifest": str(manifest_path),
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Package the red-team Kaggle submission.")
    parser.add_argument(
        "--label",
        default=datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S"),
        help="Submission directory label prefix.",
    )
    return parser.parse_args()


def main() -> int:
    manifest = build_submission(str(parse_args().label))
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
