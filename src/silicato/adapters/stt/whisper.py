"""faster-whisper speech-to-text adapter."""

from __future__ import annotations

import sys
import time
from pathlib import Path
from typing import Any

from silicato.ports.stt import SpeechToTextPort, TranscriptResult


class WhisperSttAdapter(SpeechToTextPort):
    """Speech-to-text adapter backed by a loaded faster-whisper model."""

    def __init__(self, model: Any) -> None:
        self._model = model

    def transcribe(self, wav_path: Path, language: str) -> TranscriptResult:
        kwargs: dict[str, object] = {
            "beam_size": 5,
            "vad_filter": True,
            "condition_on_previous_text": False,
        }
        if language.lower() != "auto":
            kwargs["language"] = language

        segments, _info = self._model.transcribe(str(wav_path), **kwargs)
        text = "".join(segment.text for segment in segments).strip()
        return TranscriptResult(text=text, language=language)


def is_cuda_runtime_missing(exc: Exception) -> bool:
    msg = str(exc).lower()
    return any(
        token in msg
        for token in (
            "libcublas",
            "cublas_status_alloc_failed",
            "cublas",
            "libcudnn",
            "cuda",
            "cannot be loaded",
            "not found",
        )
    )


def build_model(model_name: str, device: str, compute_type: str) -> tuple[Any, str, str]:
    try:
        from faster_whisper import WhisperModel
    except ImportError as exc:
        print("Python package 'faster-whisper' is not installed.", file=sys.stderr)
        print("Run: python3 -m pip install -e .", file=sys.stderr)
        raise SystemExit(1) from exc

    print(
        f"Loading model '{model_name}' (device={device}, compute_type={compute_type}). "
        "First run can take a while due to model download."
    )
    start = time.time()
    try:
        model = WhisperModel(model_name, device=device, compute_type=compute_type)
        elapsed = time.time() - start
        print(f"Model ready in {elapsed:.1f}s.")
        return model, device, compute_type
    except RuntimeError as exc:
        if device in {"auto", "cuda"} and is_cuda_runtime_missing(exc):
            print("CUDA runtime not available. Falling back to CPU (compute_type=int8).")
            model = WhisperModel(model_name, device="cpu", compute_type="int8")
            elapsed = time.time() - start
            print(f"Model ready on CPU in {elapsed:.1f}s.")
            return model, "cpu", "int8"
        raise
