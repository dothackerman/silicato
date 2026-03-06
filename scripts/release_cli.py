#!/usr/bin/env python3
"""Dispatch and watch manual GitHub release workflow runs."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
import tomllib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

WORKFLOW_FILE = "release.yml"


class ReleaseError(RuntimeError):
    """Raised when release orchestration preflight fails."""


def run(cmd: list[str], *, capture: bool = False) -> str:
    if capture:
        completed = subprocess.run(
            cmd,
            check=True,
            text=True,
            capture_output=True,
        )
        return completed.stdout
    subprocess.run(cmd, check=True)
    return ""


def run_json(cmd: list[str]) -> Any:
    output = run(cmd, capture=True)
    return json.loads(output or "null")


def require_clean_worktree() -> None:
    status = run(["git", "status", "--porcelain"], capture=True).strip()
    if status:
        raise ReleaseError("Working tree is not clean. Commit or stash changes before release.")


def require_pyproject_version(expected_version: str) -> None:
    pyproject = Path("pyproject.toml")
    data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    actual_version = data["project"]["version"]
    if actual_version != expected_version:
        raise ReleaseError(
            "Version mismatch: pyproject.toml has "
            f"{actual_version!r}, expected {expected_version!r}."
        )


def require_gh_auth() -> None:
    run(["gh", "auth", "status"])


def run_gate() -> None:
    run(["make", "gate"])


def dispatch_workflow(channel: str, version: str, ref: str) -> None:
    run(
        [
            "gh",
            "workflow",
            "run",
            WORKFLOW_FILE,
            "--ref",
            ref,
            "-f",
            f"channel={channel}",
            "-f",
            f"version={version}",
            "-f",
            "create_github_release=true",
        ]
    )


def parse_created_at(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def resolve_run_id(started_at: datetime, timeout_seconds: int = 90) -> int:
    deadline = time.monotonic() + timeout_seconds
    oldest_allowed = started_at - timedelta(minutes=1)
    while time.monotonic() < deadline:
        runs = run_json(
            [
                "gh",
                "run",
                "list",
                "--workflow",
                WORKFLOW_FILE,
                "--event",
                "workflow_dispatch",
                "--json",
                "databaseId,createdAt,status",
                "--limit",
                "10",
            ]
        )
        if isinstance(runs, list):
            for item in runs:
                created_at = parse_created_at(item["createdAt"])
                if created_at >= oldest_allowed:
                    return int(item["databaseId"])
        time.sleep(2)
    raise ReleaseError("Failed to find dispatched workflow run id.")


def watch_run(run_id: int) -> dict[str, Any]:
    run(["gh", "run", "watch", str(run_id), "--exit-status"])
    details = run_json(["gh", "run", "view", str(run_id), "--json", "url,status,conclusion"])
    if not isinstance(details, dict):
        raise ReleaseError("Unexpected run view output.")
    return details


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run local preflight checks and dispatch manual GitHub release workflow."
    )
    parser.add_argument("--channel", required=True, choices=["test", "prod"])
    parser.add_argument("--version", required=True, help="Version in pyproject.toml, e.g. 0.1.0rc3")
    parser.add_argument("--ref", default="main", help="Git ref to release from (default: main)")
    parser.add_argument(
        "--skip-gate",
        action="store_true",
        help="Skip local gate execution (not recommended).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        print("== Release preflight ==")
        require_clean_worktree()
        require_pyproject_version(args.version)
        require_gh_auth()

        if not args.skip_gate:
            print("== Running local gate ==")
            run_gate()
        else:
            print("== Skipping local gate by request ==")

        print("== Dispatching release workflow ==")
        started_at = datetime.now(datetime.UTC)
        dispatch_workflow(args.channel, args.version, args.ref)

        print("== Waiting for workflow run ==")
        run_id = resolve_run_id(started_at)
        details = watch_run(run_id)
        print(f"Run completed: {details.get('conclusion')} ({details.get('url')})")
        return 0
    except subprocess.CalledProcessError as exc:
        print(f"Command failed: {' '.join(exc.cmd)}", file=sys.stderr)
        return exc.returncode
    except ReleaseError as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
