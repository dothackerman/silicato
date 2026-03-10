#!/usr/bin/env python3
"""Guided recorder for Silicato auto-stop fixtures."""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Guide the operator through a structured auto-stop fixture recording session."
    )
    parser.add_argument(
        "--plan",
        type=Path,
        default=Path("tests/fixtures/auto_stop/plans/de-en-core.toml"),
        help="Recording plan describing the guided prompts.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("tests/fixtures/auto_stop/local"),
        help="Directory where fixture WAVs and diagnostics are written.",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("tests/fixtures/auto_stop/local/manifest.toml"),
        help="Auto-stop manifest to append/update.",
    )
    parser.add_argument(
        "--takes",
        type=int,
        default=1,
        help="How many takes to record for each prompt.",
    )
    parser.add_argument("--sample-rate", type=int, default=16000)
    parser.add_argument("--input-device", default=None)
    parser.add_argument("--model", default="base")
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--compute-type", default="int8")
    parser.add_argument(
        "--target-post-speech-seconds",
        type=float,
        default=0.9,
        help="Default target stop lag after the final spoken word.",
    )
    parser.add_argument(
        "--early-tolerance-seconds",
        type=float,
        default=0.2,
        help="Allowed early-stop tolerance before the target point.",
    )
    parser.add_argument(
        "--late-tolerance-seconds",
        type=float,
        default=0.5,
        help="Allowed late-stop tolerance after the target point.",
    )
    return parser.parse_args()


def main() -> int:
    from silicato.adapters.audio.alsa_capture import AlsaCaptureAdapter
    from silicato.adapters.stt.whisper import build_model
    from silicato.application.auto_stop_recording_session import (
        RecordedFixtureDraft,
        append_or_update_manifest_entry,
        fixture_id_for_take,
        infer_stop_window,
        load_recording_plan,
        similarity_ratio,
        write_diagnostics_json,
    )

    args = parse_args()
    if args.takes < 1:
        raise SystemExit("--takes must be >= 1")

    plan = load_recording_plan(args.plan)
    print(f"Loaded plan '{plan.plan_id}' with {len(plan.prompts)} prompt(s).")
    if plan.description:
        print(plan.description)
    print(
        "Recording guidance: speak naturally, leave about two seconds of silence at the end, "
        "then press Enter to stop."
    )
    print(
        "Collection mode uses manual stop on purpose so recording itself "
        "does not inherit auto-stop errors."
    )
    print("Controls: Enter=start/accept, r=retry current prompt, s=skip current prompt, q=quit.")

    model, _device, _compute_type = build_model(args.model, args.device, args.compute_type)
    capture = AlsaCaptureAdapter(silence_stop_seconds=0.0)
    wav_root = args.output_dir / "wav"
    diagnostics_root = args.output_dir / "diagnostics"
    wav_root.mkdir(parents=True, exist_ok=True)
    diagnostics_root.mkdir(parents=True, exist_ok=True)

    total_steps = len(plan.prompts) * args.takes
    step_index = 0

    for take_index in range(1, args.takes + 1):
        for prompt in plan.prompts:
            step_index += 1
            fixture_id = fixture_id_for_take(prompt.prompt_id, take_index, args.takes)
            wav_relpath = Path("wav") / f"{fixture_id}.wav"
            diagnostics_relpath = Path("diagnostics") / f"{fixture_id}.json"
            wav_path = args.output_dir / wav_relpath
            diagnostics_path = args.output_dir / diagnostics_relpath

            while True:
                print()
                print(f"[{step_index}/{total_steps}] {fixture_id} ({prompt.language})")
                if prompt.setup:
                    print(f"Setup: {prompt.setup}")
                print(f"Instruction: {prompt.instructions}")
                print(f"Script: {prompt.script}")
                action = (
                    input("Press Enter to record, 's' to skip, or 'q' to quit: ").strip().lower()
                )
                if action == "q":
                    print("Recording session aborted by operator.")
                    return 0
                if action == "s":
                    print(f"Skipped {fixture_id}.")
                    break

                wav_path.parent.mkdir(parents=True, exist_ok=True)
                if not _record_prompt(
                    capture,
                    wav_path=wav_path,
                    sample_rate=args.sample_rate,
                    input_device=args.input_device,
                ):
                    print("Recording did not succeed; retrying prompt.")
                    continue

                report = _transcribe_recording(
                    model,
                    wav_path=wav_path,
                    language=prompt.language,
                )
                target, minimum, maximum = infer_stop_window(
                    speech_end_seconds=report["speech_end_seconds"],
                    target_post_speech_seconds=args.target_post_speech_seconds,
                    early_tolerance_seconds=args.early_tolerance_seconds,
                    late_tolerance_seconds=args.late_tolerance_seconds,
                )
                ratio = similarity_ratio(prompt.script, str(report["transcript"]))
                report["script"] = prompt.script
                report["fixture_id"] = fixture_id
                report["wav_relpath"] = str(wav_relpath)
                report["similarity_ratio"] = round(ratio, 3)
                report["target_stop_seconds"] = target
                report["min_stop_seconds"] = minimum
                report["max_stop_seconds"] = maximum
                write_diagnostics_json(diagnostics_path, report)

                print(f"Transcript: {report['transcript']}")
                print(
                    "Confidence:",
                    f"avg_word_prob={report['avg_word_probability']:.3f}",
                    f"avg_segment_logprob={report['avg_segment_logprob']:.3f}",
                    f"speech_end={report['speech_end_seconds']:.2f}s",
                    f"ratio={ratio:.2f}",
                )
                print(
                    "Inferred stop window:",
                    f"target={target:.2f}s",
                    f"min={minimum:.2f}s",
                    f"max={maximum:.2f}s",
                )
                review = (
                    input("Accept recording? [Enter=yes, r=retry, s=skip, q=quit]: ")
                    .strip()
                    .lower()
                )
                if review == "q":
                    return 0
                if review == "s":
                    wav_path.unlink(missing_ok=True)
                    diagnostics_path.unlink(missing_ok=True)
                    print(f"Skipped {fixture_id}.")
                    break
                if review == "r":
                    wav_path.unlink(missing_ok=True)
                    diagnostics_path.unlink(missing_ok=True)
                    continue

                draft = RecordedFixtureDraft(
                    fixture_id=fixture_id,
                    wav_relpath=str(wav_relpath).replace("\\", "/"),
                    script=prompt.script,
                    target_stop_seconds=target,
                    min_stop_seconds=minimum,
                    max_stop_seconds=maximum,
                    tags=prompt.tags,
                    expected_transcript=prompt.script,
                )
                append_or_update_manifest_entry(args.manifest, draft)
                print(f"Saved {fixture_id} and updated {args.manifest}.")
                break

    print("Recording session complete.")
    return 0


def _record_prompt(
    capture: object,
    *,
    wav_path: Path,
    sample_rate: int,
    input_device: str | None,
) -> bool:
    try:
        capture.record_once(wav_path, sample_rate, input_device)
        return True
    except RuntimeError as exc:
        print(f"Recording error: {exc}")
        return False


def _transcribe_recording(model: object, *, wav_path: Path, language: str) -> dict[str, object]:
    kwargs: dict[str, object] = {
        "beam_size": 5,
        "vad_filter": True,
        "condition_on_previous_text": False,
        "word_timestamps": True,
    }
    if language.lower() != "auto":
        kwargs["language"] = language

    segments_iter, info = model.transcribe(str(wav_path), **kwargs)
    segments = list(segments_iter)
    transcript = "".join(segment.text for segment in segments).strip()
    words = [word for segment in segments for word in (segment.words or [])]
    speech_end_seconds = words[-1].end if words else (segments[-1].end if segments else 0.0)
    avg_word_probability = sum(word.probability for word in words) / len(words) if words else 0.0
    avg_segment_logprob = (
        sum(segment.avg_logprob for segment in segments) / len(segments)
        if segments
        else float("-inf")
    )
    return {
        "transcript": transcript,
        "detected_language": info.language,
        "language_probability": info.language_probability,
        "duration_seconds": info.duration,
        "duration_after_vad_seconds": info.duration_after_vad,
        "speech_end_seconds": round(speech_end_seconds, 3),
        "avg_word_probability": round(avg_word_probability, 3),
        "avg_segment_logprob": round(_finite_or_zero(avg_segment_logprob), 3),
        "segments": [
            {
                "id": segment.id,
                "start": round(segment.start, 3),
                "end": round(segment.end, 3),
                "text": segment.text,
                "avg_logprob": round(segment.avg_logprob, 3),
                "no_speech_prob": round(segment.no_speech_prob, 3),
                "words": [
                    {
                        "start": round(word.start, 3),
                        "end": round(word.end, 3),
                        "word": word.word,
                        "probability": round(word.probability, 3),
                    }
                    for word in (segment.words or [])
                ],
            }
            for segment in segments
        ],
    }


def _finite_or_zero(value: float) -> float:
    return value if math.isfinite(value) else 0.0


if __name__ == "__main__":
    raise SystemExit(main())
