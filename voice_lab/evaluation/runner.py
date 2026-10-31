"""Reproducible evaluation runs for Azerbaijani STT output.

A run is only produced when every dataset record points to an existing,
non-empty audio file. The report records the dataset hash, every audio hash, the
normalization configuration, and the scoring configuration so the same inputs
can be re-scored exactly.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from . import __version__
from .entities import ENTITY_CATEGORIES, EntityExample, evaluate_entities
from .metrics import (
    ErrorRate,
    TranscriptScore,
    aggregate_error_rates,
    score_transcript,
)
from .normalization import (
    DEFAULT_ENTITY_NORMALIZATION,
    DEFAULT_NORMALIZATION,
    NormalizationConfig,
)

SCHEMA_VERSION = "1.0"
_CHUNK_SIZE = 1024 * 1024


class EvaluationError(ValueError):
    """Raised when an evaluation cannot be run safely or reproducibly."""


@dataclass(frozen=True)
class DatasetRecord:
    example_id: str
    audio: str
    audio_path: Path
    reference: str
    hypothesis: str
    reference_entities: dict[str, str | None]
    hypothesis_entities: dict[str, str | None]


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(_CHUNK_SIZE), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _sha256_json(payload: object) -> str:
    canonical = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return _sha256_bytes(canonical.encode("utf-8"))


def _entity_mapping(
    value: object,
    *,
    field: str,
    example_id: str,
) -> dict[str, str | None]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise EvaluationError(f"record {example_id!r}: entities.{field} must be an object")

    result: dict[str, str | None] = {}
    for key, item in value.items():
        if not isinstance(key, str):
            raise EvaluationError(f"record {example_id!r}: entities.{field} keys must be strings")
        if item is not None and not isinstance(item, str):
            raise EvaluationError(
                f"record {example_id!r}: entities.{field}.{key} must be a string or null"
            )
        result[key] = item
    return result


def _load_dataset(dataset_path: Path) -> tuple[list[DatasetRecord], str]:
    try:
        raw = dataset_path.read_bytes()
    except OSError as error:
        raise EvaluationError(f"cannot read dataset {dataset_path}: {error}") from error

    dataset_hash = _sha256_bytes(raw)
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError as error:
        raise EvaluationError(f"dataset must be UTF-8: {error}") from error

    records: list[DatasetRecord] = []
    seen_ids: set[str] = set()
    missing_audio: list[str] = []
    empty_audio: list[str] = []

    for line_number, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError as error:
            raise EvaluationError(f"dataset line {line_number}: invalid JSON: {error}") from error
        if not isinstance(item, dict):
            raise EvaluationError(f"dataset line {line_number}: record must be an object")

        example_id = item.get("id")
        if not isinstance(example_id, str) or not example_id:
            raise EvaluationError(f"dataset line {line_number}: id must be a non-empty string")
        if example_id in seen_ids:
            raise EvaluationError(f"duplicate record id: {example_id!r}")
        seen_ids.add(example_id)

        audio = item.get("audio")
        if not isinstance(audio, str) or not audio:
            raise EvaluationError(f"record {example_id!r}: audio must be a non-empty string")

        reference = item.get("reference")
        hypothesis = item.get("hypothesis")
        if not isinstance(reference, str):
            raise EvaluationError(f"record {example_id!r}: reference must be a string")
        if not isinstance(hypothesis, str):
            raise EvaluationError(f"record {example_id!r}: hypothesis must be a string")

        audio_path = Path(audio)
        if not audio_path.is_absolute():
            audio_path = dataset_path.parent / audio_path
        audio_path = audio_path.resolve()
        if not audio_path.is_file():
            missing_audio.append(f"{example_id}: {audio}")
        elif audio_path.stat().st_size == 0:
            empty_audio.append(f"{example_id}: {audio}")

        entities = item.get("entities", {})
        if entities is None:
            entities = {}
        if not isinstance(entities, Mapping):
            raise EvaluationError(f"record {example_id!r}: entities must be an object")
        reference_entities = _entity_mapping(
            entities.get("reference", {}),
            field="reference",
            example_id=example_id,
        )
        hypothesis_entities = _entity_mapping(
            entities.get("hypothesis", {}),
            field="hypothesis",
            example_id=example_id,
        )

        records.append(
            DatasetRecord(
                example_id=example_id,
                audio=audio,
                audio_path=audio_path,
                reference=reference,
                hypothesis=hypothesis,
                reference_entities=reference_entities,
                hypothesis_entities=hypothesis_entities,
            )
        )

    if not records:
        raise EvaluationError(f"dataset {dataset_path} contains no records")
    if missing_audio:
        raise EvaluationError(
            "evaluation requires a real audio file for every record; missing: "
            + ", ".join(missing_audio)
        )
    if empty_audio:
        raise EvaluationError(
            "evaluation requires non-empty audio files; empty: " + ", ".join(empty_audio)
        )

    return records, dataset_hash


def _mean_defined_rate(rates: Sequence[ErrorRate]) -> float | None:
    values = [rate.rate for rate in rates if rate.rate is not None]
    if not values:
        return None
    return sum(values) / len(values)


def run_evaluation(
    dataset_path: str | Path,
    *,
    normalization: NormalizationConfig = DEFAULT_NORMALIZATION,
    entity_normalization: NormalizationConfig = DEFAULT_ENTITY_NORMALIZATION,
    cer_include_spaces: bool = False,
    entity_categories: Sequence[str] = ENTITY_CATEGORIES,
    code_version: str | None = None,
) -> dict[str, Any]:
    """Score a JSONL dataset and return a reproducible report.

    Every record must include ``id``, ``audio``, ``reference``, and ``hypothesis``.
    ``audio`` is resolved relative to the dataset file. The run aborts if any
    audio file is missing or empty, so a report cannot be produced without real
    audio inputs.
    """
    categories = tuple(entity_categories)
    if not categories:
        raise EvaluationError("at least one entity category is required")
    if len(set(categories)) != len(categories):
        raise EvaluationError("entity categories must be unique")

    source = Path(dataset_path).resolve()
    if not source.is_file():
        raise EvaluationError(f"dataset not found: {source}")

    records, dataset_hash = _load_dataset(source)

    config_payload: dict[str, Any] = {
        "normalization": asdict(normalization),
        "entity_normalization": asdict(entity_normalization),
        "cer_include_spaces": cer_include_spaces,
        "entity_categories": list(categories),
    }
    config_hash = _sha256_json(config_payload)

    transcript_scores: list[TranscriptScore] = []
    transcripts: list[dict[str, Any]] = []
    entity_examples: list[EntityExample] = []

    for record in records:
        score = score_transcript(
            record.reference,
            record.hypothesis,
            normalization,
            cer_include_spaces=cer_include_spaces,
        )
        transcript_scores.append(score)

        payload: dict[str, Any] = {
            "id": record.example_id,
            "audio": record.audio,
            "audio_sha256": _sha256_file(record.audio_path),
            **score.to_dict(),
        }
        if record.reference_entities or record.hypothesis_entities:
            payload["entities"] = {
                "reference": record.reference_entities,
                "hypothesis": record.hypothesis_entities,
            }
            entity_examples.append(
                EntityExample(
                    example_id=record.example_id,
                    reference=record.reference_entities,
                    hypothesis=record.hypothesis_entities,
                )
            )
        transcripts.append(payload)

    word_rates = [score.wer for score in transcript_scores]
    character_rates = [score.cer for score in transcript_scores]
    aggregate_wer = aggregate_error_rates(word_rates)
    aggregate_cer = aggregate_error_rates(character_rates)
    entity_report = evaluate_entities(entity_examples, categories, entity_normalization)

    return {
        "schema_version": SCHEMA_VERSION,
        "tool_version": __version__,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "code_version": code_version,
        "dataset": {
            "path": str(source),
            "sha256": dataset_hash,
            "record_count": len(records),
        },
        "config": config_payload,
        "config_sha256": config_hash,
        "audio_validation": "all audio files exist, are non-empty, and are hashed",
        "aggregate": {
            "wer": aggregate_wer.to_dict(),
            "cer": aggregate_cer.to_dict(),
            "mean_utterance_wer": _mean_defined_rate(word_rates),
            "mean_utterance_cer": _mean_defined_rate(character_rates),
        },
        "entities": entity_report.to_dict(),
        "transcripts": transcripts,
        "notes": (
            "Scores apply only to the listed audio files and hypotheses. "
            "No benchmark result is valid without real audio testing, and the "
            "hypotheses must be produced from those audio files by the system "
            "under test."
        ),
    }


def write_report(report: Mapping[str, object], output_path: str | Path) -> Path:
    """Write a report as UTF-8 JSON, creating parent directories if needed."""
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return destination
