#!/usr/bin/env python3
"""Run deterministic auto-stop evaluation over prerecorded WAV fixtures."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate Silicato auto-stop settings against prerecorded WAV fixtures."
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("tests/fixtures/auto_stop/local/manifest.toml"),
        help="Path to the auto-stop fixture manifest.",
    )
    parser.add_argument(
        "--silence-stop-seconds",
        type=float,
        default=1.8,
        help="Silence duration before auto-stop triggers.",
    )
    parser.add_argument(
        "--speech-rms-threshold",
        type=int,
        default=500,
        help="RMS threshold required to count a frame as speech.",
    )
    parser.add_argument(
        "--frame-bytes",
        type=int,
        default=4096,
        help="Frame size used during deterministic replay.",
    )
    return parser.parse_args()


def main() -> int:
    from silicato.application.auto_stop_evaluation import (
        evaluate_auto_stop_fixtures,
        load_auto_stop_fixtures,
        summarize_auto_stop_results,
    )
    from silicato.domain.auto_stop import AutoStopConfig

    args = parse_args()
    fixtures = load_auto_stop_fixtures(args.manifest)
    if not fixtures:
        print(
            f"No fixtures found in {args.manifest}. Add WAV recordings before running evaluation."
        )
        return 0

    config = AutoStopConfig(
        silence_stop_seconds=args.silence_stop_seconds,
        speech_rms_threshold=args.speech_rms_threshold,
        frame_bytes=args.frame_bytes,
    )
    results = evaluate_auto_stop_fixtures(fixtures, config=config)
    summary = summarize_auto_stop_results(results)

    print("fixture\toutcome\tstop_s\twindow_s\tpenalty_s\treason\tpath")
    for result in results:
        stop_s = (
            "-" if result.detected_stop_seconds is None else f"{result.detected_stop_seconds:.2f}"
        )
        window_s = f"{result.min_stop_seconds:.2f}-{result.max_stop_seconds:.2f}"
        print(
            f"{result.fixture_id}\t{result.outcome}\t{stop_s}\t{window_s}\t"
            f"{result.penalty_seconds:.2f}\t{result.decision.reason}\t{result.wav_path}"
        )

    print()
    print(
        "summary",
        f"fixtures={summary.fixture_count}",
        f"in_window={summary.in_window_count}",
        f"early={summary.early_count}",
        f"late={summary.late_count}",
        f"no_stop={summary.no_stop_count}",
        f"total_penalty_s={summary.total_penalty_seconds:.2f}",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
