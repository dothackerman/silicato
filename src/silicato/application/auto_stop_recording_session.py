"""Helpers for guided auto-stop fixture recording sessions."""

from __future__ import annotations

import json
import re
import tomllib
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RecordingPrompt:
    """One guided utterance for fixture recording."""

    prompt_id: str
    language: str
    script: str
    instructions: str
    tags: tuple[str, ...] = ()
    setup: str | None = None


@dataclass(frozen=True)
class RecordingPlan:
    """Plan describing a full recording session."""

    plan_id: str
    description: str
    prompts: tuple[RecordingPrompt, ...]


@dataclass(frozen=True)
class RecordedFixtureDraft:
    """Fixture metadata inferred from one accepted recording."""

    fixture_id: str
    wav_relpath: str
    script: str
    target_stop_seconds: float
    min_stop_seconds: float
    max_stop_seconds: float
    tags: tuple[str, ...]
    expected_transcript: str


def load_recording_plan(plan_path: Path) -> RecordingPlan:
    """Load the guided recording plan."""

    data = tomllib.loads(plan_path.read_text(encoding="utf-8"))
    if data.get("version") != 1:
        raise ValueError("Recording plan version must be 1")
    prompts = tuple(
        RecordingPrompt(
            prompt_id=str(entry["id"]),
            language=str(entry["language"]),
            script=str(entry["script"]),
            instructions=str(entry["instructions"]),
            tags=tuple(str(tag) for tag in entry.get("tags", [])),
            setup=str(entry["setup"]) if entry.get("setup") is not None else None,
        )
        for entry in data.get("prompt", [])
    )
    if not prompts:
        raise ValueError("Recording plan must contain at least one prompt")
    return RecordingPlan(
        plan_id=str(data["plan_id"]),
        description=str(data.get("description", "")),
        prompts=prompts,
    )


def fixture_id_for_take(prompt_id: str, take_index: int, total_takes: int) -> str:
    """Return deterministic fixture IDs for repeated takes."""

    if take_index < 1:
        raise ValueError("take_index must be >= 1")
    if total_takes <= 1:
        return prompt_id
    return f"{prompt_id}-take{take_index:02d}"


def infer_stop_window(
    *,
    speech_end_seconds: float,
    target_post_speech_seconds: float,
    early_tolerance_seconds: float,
    late_tolerance_seconds: float,
) -> tuple[float, float, float]:
    """Infer target/min/max stop windows from the final speech timestamp."""

    target = speech_end_seconds + target_post_speech_seconds
    minimum = max(0.0, target - early_tolerance_seconds)
    maximum = target + late_tolerance_seconds
    return (round(target, 3), round(minimum, 3), round(maximum, 3))


def similarity_ratio(expected_text: str, actual_text: str) -> float:
    """Return a lightweight normalized text similarity ratio."""

    expected_tokens = _normalize_tokens(expected_text)
    actual_tokens = _normalize_tokens(actual_text)
    if not expected_tokens and not actual_tokens:
        return 1.0
    if not expected_tokens or not actual_tokens:
        return 0.0
    overlap = sum(1 for token in actual_tokens if token in expected_tokens)
    return overlap / max(len(expected_tokens), len(actual_tokens))


def append_or_update_manifest_entry(manifest_path: Path, draft: RecordedFixtureDraft) -> None:
    """Append or replace one fixture entry in the auto-stop manifest."""

    existing = _load_manifest_entries(manifest_path)
    existing[draft.fixture_id] = draft
    _write_manifest(manifest_path, tuple(existing[key] for key in sorted(existing)))


def write_diagnostics_json(path: Path, payload: dict[str, object]) -> None:
    """Persist sidecar diagnostics for a recording."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def _load_manifest_entries(manifest_path: Path) -> dict[str, RecordedFixtureDraft]:
    if not manifest_path.exists():
        return {}
    data = tomllib.loads(manifest_path.read_text(encoding="utf-8"))
    if data.get("version") != 1:
        raise ValueError("Auto-stop manifest version must be 1")
    entries: dict[str, RecordedFixtureDraft] = {}
    for entry in data.get("fixture", []):
        fixture_id = str(entry["id"])
        entries[fixture_id] = RecordedFixtureDraft(
            fixture_id=fixture_id,
            wav_relpath=str(entry["wav"]),
            script=str(entry["script"]),
            target_stop_seconds=float(entry["target_stop_seconds"]),
            min_stop_seconds=float(entry["min_stop_seconds"]),
            max_stop_seconds=float(entry["max_stop_seconds"]),
            tags=tuple(str(tag) for tag in entry.get("tags", [])),
            expected_transcript=(
                str(entry["expected_transcript"])
                if entry.get("expected_transcript") is not None
                else str(entry["script"])
            ),
        )
    return entries


def _write_manifest(manifest_path: Path, drafts: tuple[RecordedFixtureDraft, ...]) -> None:
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["version = 1", 'root = "."', ""]
    for draft in drafts:
        lines.extend(
            [
                "[[fixture]]",
                f"id = {json.dumps(draft.fixture_id)}",
                f"wav = {json.dumps(draft.wav_relpath)}",
                f"script = {json.dumps(draft.script)}",
                f"target_stop_seconds = {_format_float(draft.target_stop_seconds)}",
                f"min_stop_seconds = {_format_float(draft.min_stop_seconds)}",
                f"max_stop_seconds = {_format_float(draft.max_stop_seconds)}",
                f"tags = {_format_string_array(draft.tags)}",
                f"expected_transcript = {json.dumps(draft.expected_transcript)}",
                "",
            ]
        )
    manifest_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _format_string_array(values: tuple[str, ...]) -> str:
    return "[" + ", ".join(json.dumps(value) for value in values) + "]"


def _format_float(value: float) -> str:
    return f"{value:.3f}".rstrip("0").rstrip(".")


def _normalize_tokens(text: str) -> tuple[str, ...]:
    normalized = re.sub(r"[^a-z0-9äöüß]+", " ", text.casefold())
    return tuple(token for token in normalized.split() if token)
