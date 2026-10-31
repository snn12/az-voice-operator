"""End-to-end evaluation-run tests with synthetic WAV fixtures.

These validate scoring mechanics only. They are not benchmark results and do not
demonstrate Azerbaijani speech quality.
"""

import json
import wave
from pathlib import Path

import pytest

from voice_lab.evaluation.runner import EvaluationError, run_evaluation, write_report


def _write_wav(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(16000)
        handle.writeframes(b"\x00\x00" * 1600)


def _write_dataset(path: Path, records: list[dict[str, object]]) -> None:
    path.write_text(
        "\n".join(json.dumps(record, ensure_ascii=False) for record in records) + "\n",
        encoding="utf-8",
    )


def _record() -> dict[str, object]:
    return {
        "id": "utt-001",
        "audio": "audio/utt-001.wav",
        "reference": "Əli, saat 19:30-da 4 nəfər.",
        "hypothesis": "əli saat 19:30-da 4 nəfər",
        "entities": {
            "reference": {
                "name": "Əli",
                "date": "2026-11-05",
                "time": "19:30",
                "number": "4",
            },
            "hypothesis": {
                "name": "əli",
                "date": "2026-11-05",
                "time": "19:30",
                "number": "4",
            },
        },
    }


@pytest.fixture
def dataset(tmp_path: Path) -> Path:
    _write_wav(tmp_path / "audio" / "utt-001.wav")
    path = tmp_path / "dataset.jsonl"
    _write_dataset(path, [_record()])
    return path


def test_run_evaluation_produces_auditable_report(dataset: Path) -> None:
    report = run_evaluation(dataset, code_version="test-build")

    assert report["dataset"]["record_count"] == 1
    assert len(report["dataset"]["sha256"]) == 64
    assert len(report["config_sha256"]) == 64
    assert report["code_version"] == "test-build"
    assert report["audio_validation"].startswith("all audio files")
    assert "real audio" in report["notes"]

    transcript = report["transcripts"][0]
    assert transcript["id"] == "utt-001"
    assert transcript["reference_original"] == "Əli, saat 19:30-da 4 nəfər."
    assert transcript["hypothesis_original"] == "əli saat 19:30-da 4 nəfər"
    assert transcript["reference_normalized"] == "əli saat 19 30 da 4 nəfər"
    assert "ə" in transcript["reference_normalized"]
    assert len(transcript["audio_sha256"]) == 64
    assert report["aggregate"]["wer"]["rate"] == 0.0
    assert report["aggregate"]["cer"]["rate"] == 0.0

    categories = {category["category"]: category for category in report["entities"]["categories"]}
    assert set(categories) == {"name", "date", "time", "number"}
    assert categories["name"]["total"] == 1
    assert categories["name"]["accuracy"] == 1.0
    assert categories["date"]["accuracy"] == 1.0
    assert categories["time"]["accuracy"] == 1.0
    assert categories["number"]["accuracy"] == 1.0


def test_run_is_deterministic_except_for_timestamp(dataset: Path) -> None:
    first = run_evaluation(dataset)
    second = run_evaluation(dataset)

    first.pop("generated_at_utc")
    second.pop("generated_at_utc")

    assert first == second


def test_missing_audio_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "dataset.jsonl"
    _write_dataset(path, [_record()])

    with pytest.raises(EvaluationError, match="missing"):
        run_evaluation(path)


def test_empty_audio_is_rejected(tmp_path: Path) -> None:
    audio = tmp_path / "audio" / "utt-001.wav"
    audio.parent.mkdir(parents=True)
    audio.write_bytes(b"")
    path = tmp_path / "dataset.jsonl"
    _write_dataset(path, [_record()])

    with pytest.raises(EvaluationError, match="empty"):
        run_evaluation(path)


def test_duplicate_ids_are_rejected(tmp_path: Path) -> None:
    path = tmp_path / "dataset.jsonl"
    first = _record()
    second = dict(_record())
    _write_dataset(path, [first, second])

    with pytest.raises(EvaluationError, match="duplicate record id"):
        run_evaluation(path)


def test_entity_annotations_are_optional(tmp_path: Path) -> None:
    _write_wav(tmp_path / "audio" / "utt-001.wav")
    record = _record()
    del record["entities"]
    path = tmp_path / "dataset.jsonl"
    _write_dataset(path, [record])

    report = run_evaluation(path)

    assert "entities" not in report["transcripts"][0]
    categories = {category["category"]: category for category in report["entities"]["categories"]}
    assert all(category["total"] == 0 for category in categories.values())
    assert all(category["accuracy"] is None for category in categories.values())


def test_write_report_preserves_unicode(dataset: Path, tmp_path: Path) -> None:
    report = run_evaluation(dataset)
    destination = write_report(report, tmp_path / "reports" / "run.json")

    assert destination.is_file()
    loaded = json.loads(destination.read_text(encoding="utf-8"))
    assert loaded["transcripts"][0]["reference_original"].startswith("Əli")
    assert "Əli" in destination.read_text(encoding="utf-8")
