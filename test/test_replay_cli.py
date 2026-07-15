import json
from pathlib import Path

import pytest

from openinputhub.tools.replay import main

FIXTURE = "test/fixtures/spacecontroller/session_v1.jsonl"


def test_cli_prints_one_json_event_per_line(
    capsys: pytest.CaptureFixture[str],
) -> None:
    result = main([FIXTURE, "--speed", "0", "--session-id", "replay:test"])
    output = [json.loads(line) for line in capsys.readouterr().out.splitlines()]
    assert result == 0
    assert output[0]["event_type"] == "identity"
    assert output[0]["source_session_id"] == "replay:test"
    assert {item["event_type"] for item in output} >= {
        "identity",
        "capabilities",
        "motion",
        "buttons",
        "wheel",
        "health",
    }


def test_cli_timestamps_use_frame_completion_offset_and_origin(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert main([FIXTURE, "--timestamp-origin-ns", "100"]) == 0
    output = [json.loads(line) for line in capsys.readouterr().out.splitlines()]
    assert output[0]["event_type"] == "identity"
    assert output[0]["timestamp_ns"] == 20_000_100


def test_cli_raw_frames_include_selector_sequence_and_payload(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert main([FIXTURE, "--raw-frames"]) == 0
    output = [json.loads(line) for line in capsys.readouterr().out.splitlines()]
    assert output[0]["selector"] == "f1"
    assert output[0]["sequence"] == 0
    assert isinstance(output[0]["payload_hex"], str)
    assert output[0]["offset_ns"] == 20_000_000


def test_cli_reports_bad_capture_without_traceback(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = tmp_path / "bad.jsonl"
    path.write_text("not-json\n", encoding="utf-8")
    assert main([str(path)]) == 2
    captured = capsys.readouterr()
    assert "bad.jsonl:1" in captured.err
    assert "Traceback" not in captured.err


def test_cli_reports_missing_capture_without_traceback(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = tmp_path / "missing.jsonl"
    assert main([str(path)]) == 2
    assert "missing.jsonl" in capsys.readouterr().err


def test_cli_returns_one_when_parser_rejects_bytes(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    source = Path(FIXTURE).read_text(encoding="utf-8").splitlines()
    source.insert(1, '{"offset_ns":0,"data_hex":"00 01"}')
    path = tmp_path / "noise.jsonl"
    path.write_text("\n".join(source) + "\n", encoding="utf-8")
    assert main([str(path)]) == 1
    assert "discarded" in capsys.readouterr().err
