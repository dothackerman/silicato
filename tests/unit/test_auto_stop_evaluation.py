from __future__ import annotations

import array
import wave
from pathlib import Path

import pytest

from silicato.application.auto_stop_evaluation import (
    evaluate_auto_stop_fixture,
    load_auto_stop_fixtures,
    summarize_auto_stop_results,
)
from silicato.domain.auto_stop import AutoStopConfig


def test_load_auto_stop_fixtures_resolves_root_relative_to_manifest(tmp_path: Path) -> None:
    fixtures_dir = tmp_path / "fixtures"
    fixtures_dir.mkdir()
    manifest_path = tmp_path / "manifest.toml"
    manifest_path.write_text(
        """
version = 1
root = "fixtures"

[[fixture]]
id = "slow-thought"
wav = "slow-thought.wav"
script = "I want to think slowly and finish clearly."
target_stop_seconds = 2.4
min_stop_seconds = 2.2
max_stop_seconds = 2.8
tags = ["slow", "quiet-ending"]
expected_transcript = "I want to think slowly and finish clearly."
""".strip(),
        encoding="utf-8",
    )

    fixtures = load_auto_stop_fixtures(manifest_path)

    assert len(fixtures) == 1
    assert fixtures[0].fixture_id == "slow-thought"
    assert fixtures[0].wav_path == (fixtures_dir / "slow-thought.wav").resolve()
    assert fixtures[0].tags == ("slow", "quiet-ending")


def test_evaluate_auto_stop_fixture_classifies_early_in_window_and_late(tmp_path: Path) -> None:
    wav_path = tmp_path / "slow_pause.wav"
    _write_test_wav(
        wav_path,
        sample_rate_hz=1000,
        frame_samples=200,
        frame_amplitudes=[1200, 1200, 1200, 1200, 1200, 0, 0, 0, 0, 0, 0, 0, 0],
    )
    fixture_manifest = tmp_path / "manifest.toml"
    fixture_manifest.write_text(
        f"""
version = 1

[[fixture]]
id = "slow-pause"
wav = "{wav_path.name}"
script = "This sentence ends slowly."
target_stop_seconds = 2.0
min_stop_seconds = 1.8
max_stop_seconds = 2.1
tags = ["slow", "pause-mid-sentence"]
""".strip(),
        encoding="utf-8",
    )
    fixture = load_auto_stop_fixtures(fixture_manifest)[0]

    early = evaluate_auto_stop_fixture(
        fixture,
        config=AutoStopConfig(
            silence_stop_seconds=0.6,
            speech_rms_threshold=500,
            frame_bytes=400,
        ),
    )
    in_window = evaluate_auto_stop_fixture(
        fixture,
        config=AutoStopConfig(
            silence_stop_seconds=0.8,
            speech_rms_threshold=500,
            frame_bytes=400,
        ),
    )
    late = evaluate_auto_stop_fixture(
        fixture,
        config=AutoStopConfig(
            silence_stop_seconds=1.2,
            speech_rms_threshold=500,
            frame_bytes=400,
        ),
    )

    assert early.outcome == "early"
    assert early.detected_stop_seconds == pytest.approx(1.6)
    assert in_window.outcome == "in_window"
    assert in_window.detected_stop_seconds == pytest.approx(1.8)
    assert late.outcome == "late"
    assert late.detected_stop_seconds == pytest.approx(2.2)

    summary = summarize_auto_stop_results((early, in_window, late))
    assert summary.fixture_count == 3
    assert summary.early_count == 1
    assert summary.in_window_count == 1
    assert summary.late_count == 1


def _write_test_wav(
    wav_path: Path,
    *,
    sample_rate_hz: int,
    frame_samples: int,
    frame_amplitudes: list[int],
) -> None:
    samples = array.array("h")
    for amplitude in frame_amplitudes:
        samples.extend([amplitude] * frame_samples)

    with wave.open(str(wav_path), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(sample_rate_hz)
        handle.writeframes(samples.tobytes())
