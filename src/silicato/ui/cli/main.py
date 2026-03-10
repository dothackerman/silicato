"""Silicato CLI runtime composition and control flow."""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

from silicato.adapters.audio.alsa_capture import AlsaCaptureAdapter
from silicato.adapters.storage.config_store import TomlConfigStore
from silicato.adapters.storage.jsonl_turn_logger import JsonlTurnLogger
from silicato.adapters.stt.whisper import WhisperSttAdapter, build_model, is_cuda_runtime_missing
from silicato.adapters.tmux.sender import TmuxSender
from silicato.adapters.tmux.target_resolver import TmuxTargetResolver
from silicato.application.use_cases.confirm_turn import ConfirmTurnUseCase
from silicato.application.use_cases.log_turn import LogTurnUseCase
from silicato.application.use_cases.resolve_target import ResolveTargetUseCase
from silicato.application.use_cases.run_capture_transcribe import (
    RunCaptureTranscribeUseCase,
    TurnConfig,
)
from silicato.application.use_cases.send_turn import SendTurnUseCase
from silicato.ports.storage import SilicatoConfig
from silicato.ports.stt import TranscriptResult
from silicato.ports.targeting import InvalidTmuxTargetError, NoTmuxSessionError, PickerAbortedError
from silicato.ui.cli.args import parse_args
from silicato.ui.cli.prompts import prompt_confirm, prompt_edit_text, prompt_turn_start
from silicato.ui.cli.runtime_checks import require_binary, run_doctor
from silicato.ui.cli.runtime_plugins import RuntimeProfilePluginError, resolve_runtime_settings


def _maybe_log(
    use_case: LogTurnUseCase,
    *,
    action: str,
    transcript: str,
    language: str,
    tmux_target: str,
    preview: bool,
    sent: bool,
) -> None:
    try:
        use_case.execute(
            action=action,
            transcript=transcript,
            language=language,
            tmux_target=tmux_target,
            preview=preview,
            sent=sent,
        )
    except OSError as exc:
        print(f"Warning: could not write log file: {exc}", file=sys.stderr)


def main() -> int:
    args = parse_args()
    if args.doctor:
        return run_doctor()

    require_binary("arecord", apt_package="alsa-utils")
    require_binary("tmux", apt_package="tmux")

    config_store = TomlConfigStore()
    config = config_store.load()

    target_resolver = TmuxTargetResolver()
    resolve_target = ResolveTargetUseCase(target_resolver)

    try:
        env_target = os.environ.get("SILICATO_TMUX_TARGET")
        target_result = resolve_target.execute(
            explicit_target=args.tmux_target,
            pick_target=args.pick_target,
            env_target=env_target,
            remembered_target=config.tmux_target,
        )
        target = target_result.target
        if target_result.remembered_target_error:
            print(
                f"Remembered tmux target is invalid: {target_result.remembered_target_error}",
                file=sys.stderr,
            )
            print("Falling back to interactive picker.", file=sys.stderr)
    except NoTmuxSessionError:
        target_resolver.print_no_tmux_guidance()
        return 1
    except InvalidTmuxTargetError as exc:
        print(f"Invalid tmux target: {exc}", file=sys.stderr)
        return 1
    except PickerAbortedError:
        print("tmux target selection aborted.", file=sys.stderr)
        return 1

    if not args.no_remember_target and config.tmux_target != target:
        config_store.save(SilicatoConfig(tmux_target=target))

    sender = TmuxSender(target)
    send_turn = SendTurnUseCase(sender)

    try:
        runtime = resolve_runtime_settings(
            profile=args.profile,
            model=args.model,
            device=args.device,
            compute_type=args.compute_type,
        )
    except RuntimeProfilePluginError as exc:
        print(f"Runtime profile error: {exc}", file=sys.stderr)
        return 1

    if runtime.reason != "manual settings":
        print(runtime.reason)

    model, active_device, _active_compute_type = build_model(
        runtime.model,
        runtime.device,
        runtime.compute_type,
    )
    silence_stop_seconds = getattr(args, "silence_stop_seconds", 1.4)
    silence_rms_threshold = getattr(args, "silence_rms_threshold", 80)
    capture_adapter = AlsaCaptureAdapter(
        silence_stop_seconds=silence_stop_seconds,
        silence_rms_threshold=silence_rms_threshold,
    )
    stt_adapter = WhisperSttAdapter(model)
    run_capture_transcribe = RunCaptureTranscribeUseCase(capture_adapter, stt_adapter)

    log_turn = LogTurnUseCase(JsonlTurnLogger(path=args.log_file))
    confirm_turn = ConfirmTurnUseCase()

    turn_config = TurnConfig(
        sample_rate=args.sample_rate,
        input_device=args.input_device,
        language=args.language,
    )

    while True:
        if not prompt_turn_start():
            return 0

        retry_turn = True
        while retry_turn:
            retry_turn = False
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                wav_path = Path(tmp.name)

            transcript_result: TranscriptResult | None = None
            current_text = ""
            try:
                print("Recording to temporary WAV...")
                transcript_result = run_capture_transcribe.execute(wav_path, turn_config)
                current_text = transcript_result.text
            except RuntimeError as exc:
                if active_device in {"auto", "cuda"} and is_cuda_runtime_missing(exc):
                    print("CUDA inference failed during transcription. Retrying on CPU.")
                    model, active_device, _active_compute_type = build_model(
                        runtime.model,
                        "cpu",
                        "int8",
                    )
                    run_capture_transcribe = RunCaptureTranscribeUseCase(
                        capture_adapter,
                        WhisperSttAdapter(model),
                    )
                    retry_turn = True
                    continue
                print(f"Error: {exc}", file=sys.stderr)
                break
            except Exception as exc:  # noqa: BLE001
                print(f"Error: {exc}", file=sys.stderr)
                break
            finally:
                wav_path.unlink(missing_ok=True)

            if transcript_result is None:
                break
            if not current_text:
                if args.preview:
                    print("Transcript: [no speech detected]")
                else:
                    print("No speech detected; skipping turn.")
                _maybe_log(
                    log_turn,
                    action="skip",
                    transcript="",
                    language=transcript_result.language,
                    tmux_target=target,
                    preview=args.preview,
                    sent=False,
                )
                break

            if args.preview:
                print(f"Transcript: {current_text}")

            if not args.preview:
                try:
                    send_turn.execute(current_text)
                except Exception as exc:  # noqa: BLE001
                    print(f"Error: {exc}", file=sys.stderr)
                    _maybe_log(
                        log_turn,
                        action="send_failed",
                        transcript=current_text,
                        language=transcript_result.language,
                        tmux_target=target,
                        preview=False,
                        sent=False,
                    )
                else:
                    _maybe_log(
                        log_turn,
                        action="send",
                        transcript=current_text,
                        language=transcript_result.language,
                        tmux_target=target,
                        preview=False,
                        sent=True,
                    )
                    print(f"Sent transcript to tmux target '{target}'.")

                if args.once:
                    return 0
                break

            while True:
                action = confirm_turn.execute(
                    prompt_confirm(),
                    preview_mode=True,
                )
                if action is None:
                    print("Invalid choice. In preview mode, send must be explicit (type 'y').")
                    continue

                if action == "edit":
                    current_text = prompt_edit_text(current_text).strip()
                    if not current_text:
                        print("Transcript is empty. Edit again, retry, skip, or quit.")
                    else:
                        print(f"Edited transcript: {current_text}")
                    continue

                if action == "retry":
                    _maybe_log(
                        log_turn,
                        action="retry",
                        transcript=current_text,
                        language=transcript_result.language,
                        tmux_target=target,
                        preview=True,
                        sent=False,
                    )
                    retry_turn = True
                    break

                if action == "skip":
                    _maybe_log(
                        log_turn,
                        action="skip",
                        transcript=current_text,
                        language=transcript_result.language,
                        tmux_target=target,
                        preview=True,
                        sent=False,
                    )
                    break

                if action == "quit":
                    _maybe_log(
                        log_turn,
                        action="quit",
                        transcript=current_text,
                        language=transcript_result.language,
                        tmux_target=target,
                        preview=True,
                        sent=False,
                    )
                    return 0

                if not current_text:
                    print("Cannot send an empty transcript. Edit, retry, or skip.")
                    continue

                send_turn.execute(current_text)
                _maybe_log(
                    log_turn,
                    action="send",
                    transcript=current_text,
                    language=transcript_result.language,
                    tmux_target=target,
                    preview=True,
                    sent=True,
                )
                print(f"Sent transcript to tmux target '{target}'.")
                break

            if args.once and not retry_turn:
                return 0


if __name__ == "__main__":
    raise SystemExit(main())
