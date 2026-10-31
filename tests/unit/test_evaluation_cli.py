"""CLI behaviour for reproducible evaluation runs."""

import json
import os
import subprocess
import sys
import wave
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


def _write_wav(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(16000)
        handle.writeframes(b"\x00\x00" * 160)


def _write_dataset(path: Path) -> None:
    record = {
        "id": "utt-001",
        "audio": "audio/utt-001.wav",
        "reference": "Əli, saat 19:30-da 4 nəfər.",
        "hypothesis": "əli saat 19:30-da 4 nəfər",
    }
    path.write_text(
        json.dumps(record, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


@pytest.fixture
def dataset(tmp_path: Path) -> Path:
    _write_wav(tmp_path / "audio" / "utt-001.wav")
    path = tmp_path / "dataset.jsonl"
    _write_dataset(path)
    return path


def _run_cli(
    *args: str,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[bytes]:
    process_env = os.environ.copy()
    if env is not None:
        process_env.update(env)
    return subprocess.run(
        [sys.executable, "-m", "voice_lab.evaluation", *args],
        cwd=REPO_ROOT,
        env=process_env,
        capture_output=True,
        check=False,
    )


def test_cli_writes_utf8_stdout_on_non_utf8_console(dataset: Path) -> None:
    result = _run_cli(
        "--dataset",
        str(dataset),
        env={"PYTHONIOENCODING": "cp1251", "PYTHONUTF8": "0"},
    )

    assert result.returncode == 0, result.stderr.decode("utf-8", errors="replace")
    report = json.loads(result.stdout.decode("utf-8"))
    assert report["transcripts"][0]["reference_original"].startswith("Əli")


def test_cli_reports_unwritable_output(dataset: Path, tmp_path: Path) -> None:
    result = _run_cli("--dataset", str(dataset), "--output", str(tmp_path))

    assert result.returncode == 2
    stderr = result.stderr.decode("utf-8", errors="replace")
    assert "error: cannot write report" in stderr


def test_cli_refuses_to_overwrite_dataset(dataset: Path) -> None:
    original = dataset.read_bytes()
    result = _run_cli("--dataset", str(dataset), "--output", str(dataset))

    assert result.returncode == 2
    stderr = result.stderr.decode("utf-8", errors="replace")
    assert "must not overwrite" in stderr
    assert dataset.read_bytes() == original


def test_cli_reports_missing_audio(dataset: Path) -> None:
    (dataset.parent / "audio" / "utt-001.wav").unlink()
    result = _run_cli("--dataset", str(dataset))

    assert result.returncode == 2
    stderr = result.stderr.decode("utf-8", errors="replace")
    assert "missing" in stderr
