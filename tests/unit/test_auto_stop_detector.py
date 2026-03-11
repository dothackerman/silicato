from __future__ import annotations

from silicato.domain.auto_stop import (
    AutoStopConfig,
    IncrementalAutoStopDetector,
    RmsFrame,
    evaluate_rms_frames,
)


def test_evaluate_rms_frames_stops_after_expected_silence_window() -> None:
    frames = [
        RmsFrame(rms=900, end_time_seconds=0.2),
        RmsFrame(rms=900, end_time_seconds=0.4),
        RmsFrame(rms=900, end_time_seconds=0.6),
        RmsFrame(rms=0, end_time_seconds=0.8),
        RmsFrame(rms=0, end_time_seconds=1.0),
        RmsFrame(rms=0, end_time_seconds=1.2),
    ]

    decision = evaluate_rms_frames(
        frames,
        config=AutoStopConfig(silence_stop_seconds=0.6, speech_rms_threshold=500),
    )

    assert decision.reason == "silence"
    assert decision.speech_detected is True
    assert decision.stop_time_seconds == 1.2


def test_evaluate_rms_frames_reports_no_speech_when_threshold_is_never_crossed() -> None:
    frames = [
        RmsFrame(rms=100, end_time_seconds=0.2),
        RmsFrame(rms=120, end_time_seconds=0.4),
        RmsFrame(rms=80, end_time_seconds=0.6),
    ]

    decision = evaluate_rms_frames(
        frames,
        config=AutoStopConfig(silence_stop_seconds=0.6, speech_rms_threshold=500),
    )

    assert decision.reason == "no_speech"
    assert decision.speech_detected is False
    assert decision.stop_time_seconds is None


def test_evaluate_rms_frames_keeps_auto_stop_disabled_when_requested() -> None:
    frames = [
        RmsFrame(rms=900, end_time_seconds=0.2),
        RmsFrame(rms=0, end_time_seconds=0.4),
        RmsFrame(rms=0, end_time_seconds=0.6),
    ]

    decision = evaluate_rms_frames(
        frames,
        config=AutoStopConfig(silence_stop_seconds=0.0, speech_rms_threshold=500),
    )

    assert decision.reason == "disabled"
    assert decision.stop_time_seconds is None
    assert decision.clip_duration_seconds == 0.6


def test_incremental_detector_matches_batch_evaluation() -> None:
    frames = [
        RmsFrame(rms=900, end_time_seconds=0.2),
        RmsFrame(rms=900, end_time_seconds=0.4),
        RmsFrame(rms=0, end_time_seconds=0.6),
        RmsFrame(rms=0, end_time_seconds=0.8),
        RmsFrame(rms=0, end_time_seconds=1.0),
    ]
    config = AutoStopConfig(silence_stop_seconds=0.6, speech_rms_threshold=500)

    batch = evaluate_rms_frames(frames, config=config)
    detector = IncrementalAutoStopDetector(config)
    observed = None
    for frame in frames:
        observed = detector.observe(frame)
        if observed is not None:
            break
    if observed is None:
        observed = detector.finish()

    assert observed == batch


def test_incremental_detector_stops_at_max_duration() -> None:
    frames = [
        RmsFrame(rms=900, end_time_seconds=0.2),
        RmsFrame(rms=900, end_time_seconds=0.4),
        RmsFrame(rms=900, end_time_seconds=0.6),
    ]

    decision = evaluate_rms_frames(
        frames,
        config=AutoStopConfig(
            silence_stop_seconds=1.4,
            speech_rms_threshold=500,
            max_recording_seconds=0.5,
        ),
    )

    assert decision.reason == "max_duration"
    assert decision.speech_detected is True
    assert decision.stop_time_seconds == 0.5
    assert decision.clip_duration_seconds == 0.6
