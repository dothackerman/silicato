from __future__ import annotations

from pathlib import Path

import pytest

from silicato.ui.cli.args import parse_args


def test_parse_args_supports_short_options() -> None:
    args = parse_args(
        [
            "-m",
            "small",
            "-d",
            "auto",
            "-c",
            "float16",
            "-l",
            "de",
            "-r",
            "44100",
            "--silence-stop-seconds",
            "2.5",
            "--silence-rms-threshold",
            "120",
            "-i",
            "hw:0,0",
            "-t",
            "codex:0.1",
            "-n",
            "-p",
            "-f",
            "/tmp/silicato.jsonl",
            "-o",
            "-D",
        ]
    )

    assert args.model == "small"
    assert args.device == "auto"
    assert args.compute_type == "float16"
    assert args.language == "de"
    assert args.sample_rate == 44100
    assert args.silence_stop_seconds == 2.5
    assert args.silence_rms_threshold == 120
    assert args.input_device == "hw:0,0"
    assert args.tmux_target == "codex:0.1"
    assert args.no_remember_target is True
    assert args.preview is True
    assert args.log_file == Path("/tmp/silicato.jsonl")
    assert args.once is True
    assert args.doctor is True
    assert args.profile is None
    assert args.spawn is False


def test_parse_args_picker_is_default_and_reuse_can_be_opted_in() -> None:
    default_args = parse_args([])
    assert default_args.pick_target is True
    assert default_args.silence_stop_seconds == 1.4
    assert default_args.silence_rms_threshold == 80

    reuse_args = parse_args(["--reuse-target"])
    assert reuse_args.pick_target is False


def test_parse_args_supports_spawn_profile_alias_and_explicit_profile() -> None:
    spawn_args = parse_args(["--spawn"])
    assert spawn_args.spawn is True
    assert spawn_args.profile == "spawn"

    profile_args = parse_args(["--profile", "spawn"])
    assert profile_args.spawn is False
    assert profile_args.profile == "spawn"


def test_parse_args_accepts_custom_profile_plugin_name() -> None:
    profile_args = parse_args(["--profile", "eco"])
    assert profile_args.profile == "eco"


def test_parse_args_supports_route_management_subcommands() -> None:
    add_args = parse_args(["route", "add", "gaia", "codex:0.1", "--force"])
    assert add_args.command == "route"
    assert add_args.route_command == "add"
    assert add_args.identifier == "gaia"
    assert add_args.tmux_target == "codex:0.1"
    assert add_args.force is True

    list_args = parse_args(["route", "list"])
    assert list_args.command == "route"
    assert list_args.route_command == "list"


def test_parse_args_supports_named_route_injection() -> None:
    text_args = parse_args(["inject", "--to", "gaia", "--text", "hello"])
    assert text_args.command == "inject"
    assert text_args.route_identifier == "gaia"
    assert text_args.inject_text == "hello"
    assert text_args.inject_from_file is None

    file_args = parse_args(["inject", "--to", "gaia", "--from-file", "/tmp/prompt.txt"])
    assert file_args.inject_from_file == Path("/tmp/prompt.txt")


def test_parse_args_help_text_mentions_target_modes_and_preview_actions(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit) as exc:
        parse_args(["--help"])

    assert exc.value.code == 0
    out = capsys.readouterr().out
    assert "--reuse-target" in out
    assert "SILICATO_TMUX_TARGET" in out
    assert "remembered config" in out
    assert "y=send" in out
    assert "e=edit" in out
    assert "r=retry" in out
    assert "s=skip" in out
    assert "q=quit" in out
    assert "--silence-stop-seconds" in out
    assert "--silence-rms-threshold" in out
    assert "--profile" in out
    assert "--spawn" in out
    assert "route add gaia" in out
    assert "inject --to gaia" in out


def test_parse_args_help_text_lists_discovered_runtime_plugins(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(
        "silicato.ui.cli.args.available_runtime_profiles",
        lambda: ["eco", "spawn"],
    )

    with pytest.raises(SystemExit) as exc:
        parse_args(["--help"])

    assert exc.value.code == 0
    out = capsys.readouterr().out
    assert "Available now:" in out
    assert "eco, spawn" in out
