from __future__ import annotations

import pytest

from silicato.ui.cli.profiles import RuntimeSettings, apply_profile, resolve_spawn_profile_settings


def test_apply_profile_returns_manual_settings_when_profile_absent() -> None:
    settings = apply_profile(profile=None, model="medium", device="cuda", compute_type="float16")
    assert settings == RuntimeSettings(
        model="medium",
        device="cuda",
        compute_type="float16",
        reason="manual settings",
    )


def test_resolve_spawn_profile_cpu_fallback_when_no_gpu(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("silicato.ui.cli.profiles.detect_gpu_total_vram_mb", lambda: None)

    settings = resolve_spawn_profile_settings()

    assert settings.model == "small"
    assert settings.device == "cpu"
    assert settings.compute_type == "int8"
    assert "no NVIDIA GPU" in settings.reason


def test_resolve_spawn_profile_6gb_gpu_prefers_small_int8_float16(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("silicato.ui.cli.profiles.detect_gpu_total_vram_mb", lambda: 6144)

    settings = resolve_spawn_profile_settings()

    assert settings.model == "small"
    assert settings.device == "cuda"
    assert settings.compute_type == "int8_float16"
    assert "6144" in settings.reason
