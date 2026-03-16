"""tmux sender adapter."""

from __future__ import annotations

import time

from silicato.ports.sender import SenderPort

from .runtime import TmuxRuntime


class TmuxSender(SenderPort):
    """Send text to a tmux target pane and submit it."""

    # Some agent TUIs can miss submit when text + Enter are sent in one tmux call.
    # Keep a conservative split delay to improve reliability in tmux-driven CLIs.
    SUBMIT_DELAY_SECONDS = 0.25
    READY_WAIT_TIMEOUT_SECONDS = 5.0
    READY_WAIT_POLL_SECONDS = 0.20
    READY_STABILIZATION_SECONDS = 0.50

    def __init__(self, target: str, *, runtime: TmuxRuntime | None = None) -> None:
        self.target = target
        self._runtime = runtime or TmuxRuntime()

    def _capture_target_snapshot(self) -> str:
        pane_result = self._runtime.capture_pane(self.target)
        if pane_result.returncode != 0:
            message = (
                pane_result.stderr or pane_result.stdout or "tmux capture-pane failed"
            ).strip()
            raise RuntimeError(message)
        return pane_result.stdout or ""

    def _ensure_target_is_idle(self, pane_snapshot: str) -> None:
        pane_output = pane_snapshot.lower()
        if "ctrl+q enqueue" in pane_output and (
            "thinking" in pane_output or "processing" in pane_output
        ):
            raise RuntimeError(
                "tmux target is busy (agent still processing). Wait for completion before sending."
            )

    def _wait_until_ready(self, pane_snapshot: str) -> str:
        deadline = time.monotonic() + self.READY_WAIT_TIMEOUT_SECONDS
        current_snapshot = pane_snapshot
        waited_for_ready = False
        while True:
            pane_output = current_snapshot.lower()
            should_wait = "loading environment" in pane_output or not current_snapshot.strip()
            if not should_wait and not waited_for_ready:
                return current_snapshot
            if not should_wait and waited_for_ready:
                time.sleep(self.READY_STABILIZATION_SECONDS)
                current_snapshot = self._capture_target_snapshot()
                waited_for_ready = False
                continue
            if time.monotonic() >= deadline:
                raise RuntimeError(
                    "tmux target is still loading environment. Wait for it to finish and retry."
                )
            time.sleep(self.READY_WAIT_POLL_SECONDS)
            current_snapshot = self._capture_target_snapshot()
            waited_for_ready = True

    def send(self, text: str) -> None:
        pane_snapshot = self._capture_target_snapshot()
        ready_snapshot = self._wait_until_ready(pane_snapshot)
        self._ensure_target_is_idle(ready_snapshot)

        text_result = self._runtime.send_keys(self.target, text)
        if text_result.returncode != 0:
            message = (text_result.stderr or text_result.stdout or "tmux send-keys failed").strip()
            raise RuntimeError(message)

        time.sleep(self.SUBMIT_DELAY_SECONDS)

        submit_result = self._runtime.send_keys(self.target, "Enter")
        if submit_result.returncode != 0:
            message = (
                submit_result.stderr or submit_result.stdout or "tmux submit-key send failed"
            ).strip()
            raise RuntimeError(message)
