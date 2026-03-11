"""Deterministic evaluation helpers for auto-stop fixtures."""

from __future__ import annotations

import tomllib
import wave
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from silicato.domain.auto_stop import (
    AutoStopConfig,
    AutoStopDecision,
    evaluate_rms_frames,
    iter_rms_frames_s16le,
)

AutoStopOutcome = Literal["early", "in_window", "late", "no_stop"]
_FLOAT_EPSILON = 1e-9


@dataclass(frozen=True)
class AutoStopFixture:
    """One prerecorded utterance with expected auto-stop behavior."""

    fixture_id: str
    wav_path: Path
    script: str
    target_stop_seconds: float
    min_stop_seconds: float
    max_stop_seconds: float
    tags: tuple[str, ...] = ()
    expected_transcript: str | None = None


@dataclass(frozen=True)
class AutoStopFixtureResult:
    """Evaluation result for one fixture/config pair."""

    fixture_id: str
    wav_path: Path
    outcome: AutoStopOutcome
    detected_stop_seconds: float | None
    expected_target_seconds: float
    min_stop_seconds: float
    max_stop_seconds: float
    penalty_seconds: float
    decision: AutoStopDecision


@dataclass(frozen=True)
class AutoStopEvaluationSummary:
    """Aggregate scores for one config over a fixture set."""

    fixture_count: int
    in_window_count: int
    early_count: int
    late_count: int
    no_stop_count: int
    total_penalty_seconds: float


def load_auto_stop_fixtures(manifest_path: Path) -> tuple[AutoStopFixture, ...]:
    """Load fixture metadata from a TOML manifest."""

    if not manifest_path.exists():
        return ()
    data = tomllib.loads(manifest_path.read_text(encoding="utf-8"))
    if data.get("version") != 1:
        raise ValueError("Auto-stop manifest version must be 1")

    root = manifest_path.parent / data.get("root", ".")
    fixtures: list[AutoStopFixture] = []
    seen_ids: set[str] = set()

    for entry in data.get("fixture", []):
        fixture_id = str(entry["id"])
        if fixture_id in seen_ids:
            raise ValueError(f"Duplicate auto-stop fixture id: {fixture_id}")
        seen_ids.add(fixture_id)
        fixtures.append(
            AutoStopFixture(
                fixture_id=fixture_id,
                wav_path=(root / str(entry["wav"])).resolve(),
                script=str(entry["script"]),
                target_stop_seconds=float(entry["target_stop_seconds"]),
                min_stop_seconds=float(entry["min_stop_seconds"]),
                max_stop_seconds=float(entry["max_stop_seconds"]),
                tags=tuple(str(tag) for tag in entry.get("tags", [])),
                expected_transcript=(
                    str(entry["expected_transcript"])
                    if entry.get("expected_transcript") is not None
                    else None
                ),
            )
        )

    return tuple(fixtures)


def evaluate_auto_stop_fixture(
    fixture: AutoStopFixture,
    *,
    config: AutoStopConfig,
) -> AutoStopFixtureResult:
    """Evaluate one fixture against the provided endpointing settings."""

    sample_rate_hz, pcm_bytes = _read_mono_s16le_wav(fixture.wav_path)
    decision = evaluate_rms_frames(
        iter_rms_frames_s16le(
            pcm_bytes,
            sample_rate_hz=sample_rate_hz,
            config=config,
        ),
        config=config,
    )
    outcome, penalty_seconds = _score_decision(decision, fixture)
    return AutoStopFixtureResult(
        fixture_id=fixture.fixture_id,
        wav_path=fixture.wav_path,
        outcome=outcome,
        detected_stop_seconds=decision.stop_time_seconds,
        expected_target_seconds=fixture.target_stop_seconds,
        min_stop_seconds=fixture.min_stop_seconds,
        max_stop_seconds=fixture.max_stop_seconds,
        penalty_seconds=penalty_seconds,
        decision=decision,
    )


def evaluate_auto_stop_fixtures(
    fixtures: Sequence[AutoStopFixture],
    *,
    config: AutoStopConfig,
) -> tuple[AutoStopFixtureResult, ...]:
    """Evaluate a config across a full fixture set."""

    return tuple(evaluate_auto_stop_fixture(fixture, config=config) for fixture in fixtures)


def summarize_auto_stop_results(
    results: Iterable[AutoStopFixtureResult],
) -> AutoStopEvaluationSummary:
    """Aggregate fixture-level outcomes into one summary."""

    result_list = list(results)
    return AutoStopEvaluationSummary(
        fixture_count=len(result_list),
        in_window_count=sum(result.outcome == "in_window" for result in result_list),
        early_count=sum(result.outcome == "early" for result in result_list),
        late_count=sum(result.outcome == "late" for result in result_list),
        no_stop_count=sum(result.outcome == "no_stop" for result in result_list),
        total_penalty_seconds=sum(result.penalty_seconds for result in result_list),
    )


def _read_mono_s16le_wav(wav_path: Path) -> tuple[int, bytes]:
    try:
        with wave.open(str(wav_path), "rb") as handle:
            channels = handle.getnchannels()
            sample_width = handle.getsampwidth()
            sample_rate_hz = handle.getframerate()
            pcm_bytes = handle.readframes(handle.getnframes())
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"Auto-stop fixture WAV not found: {wav_path}") from exc

    if channels != 1:
        raise ValueError(f"Auto-stop fixture must be mono WAV: {wav_path}")
    if sample_width != 2:
        raise ValueError(f"Auto-stop fixture must be 16-bit WAV: {wav_path}")
    return sample_rate_hz, pcm_bytes


def _score_decision(
    decision: AutoStopDecision,
    fixture: AutoStopFixture,
) -> tuple[AutoStopOutcome, float]:
    stop_time = decision.stop_time_seconds
    if stop_time is None:
        overflow = max(0.0, decision.clip_duration_seconds - fixture.max_stop_seconds)
        return "no_stop", 5.0 + overflow
    if stop_time + _FLOAT_EPSILON < fixture.min_stop_seconds:
        return "early", fixture.min_stop_seconds - stop_time
    if stop_time - _FLOAT_EPSILON > fixture.max_stop_seconds:
        return "late", (stop_time - fixture.max_stop_seconds) * 0.5
    return "in_window", 0.0
