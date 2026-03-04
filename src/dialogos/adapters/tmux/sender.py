"""tmux sender adapter."""

from __future__ import annotations

import subprocess
import time

from dialogos.ports.sender import SenderPort


class TmuxSender(SenderPort):
    """Send text to a tmux target pane and submit it."""

    # Codex TUI can miss submit when text + Enter are sent in one tmux call.
    # A short split delay makes submission reliable in practice.
    SUBMIT_DELAY_SECONDS = 0.05

    def __init__(self, target: str) -> None:
        self.target = target

    def send(self, text: str) -> None:
        text_result = subprocess.run(
            ["tmux", "send-keys", "-t", self.target, text],
            capture_output=True,
            text=True,
            check=False,
        )
        if text_result.returncode != 0:
            message = (text_result.stderr or text_result.stdout or "tmux send-keys failed").strip()
            raise RuntimeError(message)

        time.sleep(self.SUBMIT_DELAY_SECONDS)

        submit_result = subprocess.run(
            ["tmux", "send-keys", "-t", self.target, "Enter"],
            capture_output=True,
            text=True,
            check=False,
        )
        if submit_result.returncode != 0:
            message = (
                submit_result.stderr or submit_result.stdout or "tmux submit-key send failed"
            ).strip()
            raise RuntimeError(message)
