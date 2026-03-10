from __future__ import annotations

from pathlib import Path

from silicato.application.auto_stop_recording_session import (
    RecordedFixtureDraft,
    append_or_update_manifest_entry,
    fixture_id_for_take,
    infer_stop_window,
    load_recording_plan,
    similarity_ratio,
)


def test_load_recording_plan_parses_prompts_and_metadata(tmp_path: Path) -> None:
    plan_path = tmp_path / "plan.toml"
    plan_path.write_text(
        """
version = 1
plan_id = "de-en-core"
description = "Balanced DE/EN starter prompts."

[[prompt]]
id = "en-slow-01"
language = "en"
script = "I want to speak slowly and still finish naturally."
instructions = "Speak slowly with one short pause in the middle."
tags = ["english", "slow"]
setup = "quiet room"
""".strip(),
        encoding="utf-8",
    )

    plan = load_recording_plan(plan_path)

    assert plan.plan_id == "de-en-core"
    assert plan.prompts[0].prompt_id == "en-slow-01"
    assert plan.prompts[0].setup == "quiet room"


def test_fixture_id_for_take_adds_suffix_only_for_repeated_takes() -> None:
    assert fixture_id_for_take("en-slow-01", 1, 1) == "en-slow-01"
    assert fixture_id_for_take("en-slow-01", 2, 2) == "en-slow-01-take02"


def test_infer_stop_window_biases_toward_slightly_patient_defaults() -> None:
    target, minimum, maximum = infer_stop_window(
        speech_end_seconds=2.35,
        target_post_speech_seconds=0.9,
        early_tolerance_seconds=0.2,
        late_tolerance_seconds=0.5,
    )

    assert target == 3.25
    assert minimum == 3.05
    assert maximum == 3.75


def test_append_or_update_manifest_entry_rewrites_fixture_manifest_canonically(
    tmp_path: Path,
) -> None:
    manifest_path = tmp_path / "manifest.toml"
    append_or_update_manifest_entry(
        manifest_path,
        RecordedFixtureDraft(
            fixture_id="en-slow-01",
            wav_relpath="wav/en-slow-01.wav",
            script="I want to speak slowly and still finish naturally.",
            target_stop_seconds=3.2,
            min_stop_seconds=3.0,
            max_stop_seconds=3.6,
            tags=("english", "slow"),
            expected_transcript="I want to speak slowly and still finish naturally.",
        ),
    )

    text = manifest_path.read_text(encoding="utf-8")
    assert 'id = "en-slow-01"' in text
    assert 'wav = "wav/en-slow-01.wav"' in text
    assert 'tags = ["english", "slow"]' in text


def test_similarity_ratio_flags_major_script_transcript_divergence() -> None:
    assert similarity_ratio("please open the terminal", "please open terminal") > 0.7
    assert similarity_ratio("please open the terminal", "goodbye and thanks") < 0.3
