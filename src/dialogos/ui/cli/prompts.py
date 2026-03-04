"""CLI prompt and input helpers."""

from __future__ import annotations


def prompt_turn_start() -> bool:
    try:
        choice = input("Press Enter to talk, or type 'q' then Enter to quit: ").strip().lower()
    except EOFError:
        print()
        return False
    return choice not in {"q", "quit", "exit"}


def prompt_confirm() -> str:
    return input("Confirm [y=send, e=edit, r=retry, s=skip, q=quit]: ")


def prompt_edit_text(current_text: str) -> str:
    print(f"Current transcript: {current_text}")
    edited = input("Edited transcript (empty keeps current): ").strip()
    if edited:
        return edited
    return current_text
