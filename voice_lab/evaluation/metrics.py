"""Word- and character-level error rates with Azerbaijani-aware normalization.

WER and CER are computed with the same configurable normalization. The original
reference and hypothesis strings are always retained by ``score_transcript``.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass

from .normalization import DEFAULT_NORMALIZATION, NormalizationConfig, normalize_text


@dataclass(frozen=True)
class EditCounts:
    """Substitution, deletion, and insertion counts from an edit alignment."""

    substitutions: int
    deletions: int
    insertions: int

    def __post_init__(self) -> None:
        if min(self.substitutions, self.deletions, self.insertions) < 0:
            raise ValueError("edit counts cannot be negative")

    @property
    def errors(self) -> int:
        return self.substitutions + self.deletions + self.insertions


@dataclass(frozen=True)
class ErrorRate:
    """An error rate and the counts it was derived from."""

    errors: int
    reference_units: int
    substitutions: int
    deletions: int
    insertions: int

    def __post_init__(self) -> None:
        if self.errors < 0 or self.reference_units < 0:
            raise ValueError("error counts and reference units cannot be negative")
        if min(self.substitutions, self.deletions, self.insertions) < 0:
            raise ValueError("edit counts cannot be negative")
        if self.substitutions + self.deletions + self.insertions != self.errors:
            raise ValueError("errors must equal substitutions + deletions + insertions")

    @property
    def rate(self) -> float | None:
        """Errors per reference unit, or ``None`` when the reference is empty."""
        if self.reference_units == 0:
            return None
        return self.errors / self.reference_units

    def to_dict(self) -> dict[str, int | float | None]:
        return {
            "errors": self.errors,
            "reference_units": self.reference_units,
            "substitutions": self.substitutions,
            "deletions": self.deletions,
            "insertions": self.insertions,
            "rate": self.rate,
        }


def _edit_counts(reference: Sequence[str], hypothesis: Sequence[str]) -> EditCounts:
    """Return deterministic edit counts for two sequences.

    The backtrace prefers matches, then substitutions, deletions, and insertions.
    The total error count is independent of that tie-breaking order; the split
    between categories is deterministic.
    """
    reference_length = len(reference)
    hypothesis_length = len(hypothesis)

    distances = [[0] * (hypothesis_length + 1) for _ in range(reference_length + 1)]
    for index in range(1, reference_length + 1):
        distances[index][0] = index
    for index in range(1, hypothesis_length + 1):
        distances[0][index] = index

    for ref_index in range(1, reference_length + 1):
        for hyp_index in range(1, hypothesis_length + 1):
            substitution_cost = 0 if reference[ref_index - 1] == hypothesis[hyp_index - 1] else 1
            distances[ref_index][hyp_index] = min(
                distances[ref_index - 1][hyp_index] + 1,
                distances[ref_index][hyp_index - 1] + 1,
                distances[ref_index - 1][hyp_index - 1] + substitution_cost,
            )

    substitutions = 0
    deletions = 0
    insertions = 0
    ref_index = reference_length
    hyp_index = hypothesis_length

    while ref_index > 0 or hyp_index > 0:
        if (
            ref_index > 0
            and hyp_index > 0
            and reference[ref_index - 1] == hypothesis[hyp_index - 1]
            and distances[ref_index][hyp_index] == distances[ref_index - 1][hyp_index - 1]
        ):
            ref_index -= 1
            hyp_index -= 1
        elif (
            ref_index > 0
            and hyp_index > 0
            and distances[ref_index][hyp_index] == distances[ref_index - 1][hyp_index - 1] + 1
        ):
            substitutions += 1
            ref_index -= 1
            hyp_index -= 1
        elif (
            ref_index > 0
            and distances[ref_index][hyp_index] == distances[ref_index - 1][hyp_index] + 1
        ):
            deletions += 1
            ref_index -= 1
        elif (
            hyp_index > 0
            and distances[ref_index][hyp_index] == distances[ref_index][hyp_index - 1] + 1
        ):
            insertions += 1
            hyp_index -= 1
        else:  # pragma: no cover - defensive guard; the recurrence always resolves
            raise RuntimeError("edit-distance backtrace failed")

    return EditCounts(
        substitutions=substitutions,
        deletions=deletions,
        insertions=insertions,
    )


def _error_rate(counts: EditCounts, reference_units: int) -> ErrorRate:
    return ErrorRate(
        errors=counts.errors,
        reference_units=reference_units,
        substitutions=counts.substitutions,
        deletions=counts.deletions,
        insertions=counts.insertions,
    )


def wer(
    reference: str,
    hypothesis: str,
    config: NormalizationConfig = DEFAULT_NORMALIZATION,
) -> ErrorRate:
    """Word error rate after configurable normalization.

    Words are whitespace-delimited units of the normalized strings. The rate is
    ``errors / reference_words``; an empty reference has an undefined rate
    (``None``) but still reports any insertion errors.
    """
    normalized_reference = normalize_text(reference, config)
    normalized_hypothesis = normalize_text(hypothesis, config)
    reference_words = normalized_reference.split()
    hypothesis_words = normalized_hypothesis.split()
    return _error_rate(
        _edit_counts(reference_words, hypothesis_words),
        len(reference_words),
    )


def cer(
    reference: str,
    hypothesis: str,
    config: NormalizationConfig = DEFAULT_NORMALIZATION,
    *,
    include_spaces: bool = False,
) -> ErrorRate:
    """Character error rate after configurable normalization.

    Spaces are excluded by default. Set ``include_spaces=True`` to score them as
    characters; the choice is recorded in evaluation reports.
    """
    normalized_reference = normalize_text(reference, config)
    normalized_hypothesis = normalize_text(hypothesis, config)

    if not include_spaces:
        normalized_reference = "".join(normalized_reference.split())
        normalized_hypothesis = "".join(normalized_hypothesis.split())

    return _error_rate(
        _edit_counts(normalized_reference, normalized_hypothesis),
        len(normalized_reference),
    )


@dataclass(frozen=True)
class TranscriptScore:
    """Transcript-level WER/CER with original and normalized text retained."""

    reference_original: str
    hypothesis_original: str
    reference_normalized: str
    hypothesis_normalized: str
    wer: ErrorRate
    cer: ErrorRate

    def to_dict(self) -> dict[str, object]:
        return {
            "reference_original": self.reference_original,
            "hypothesis_original": self.hypothesis_original,
            "reference_normalized": self.reference_normalized,
            "hypothesis_normalized": self.hypothesis_normalized,
            "wer": self.wer.to_dict(),
            "cer": self.cer.to_dict(),
        }


def score_transcript(
    reference: str,
    hypothesis: str,
    config: NormalizationConfig = DEFAULT_NORMALIZATION,
    *,
    cer_include_spaces: bool = False,
) -> TranscriptScore:
    """Score one transcript pair without discarding the original text."""
    normalized_reference = normalize_text(reference, config)
    normalized_hypothesis = normalize_text(hypothesis, config)

    reference_words = normalized_reference.split()
    hypothesis_words = normalized_hypothesis.split()
    word_counts = _edit_counts(reference_words, hypothesis_words)

    cer_reference = normalized_reference
    cer_hypothesis = normalized_hypothesis
    if not cer_include_spaces:
        cer_reference = "".join(cer_reference.split())
        cer_hypothesis = "".join(cer_hypothesis.split())
    character_counts = _edit_counts(cer_reference, cer_hypothesis)

    return TranscriptScore(
        reference_original=reference,
        hypothesis_original=hypothesis,
        reference_normalized=normalized_reference,
        hypothesis_normalized=normalized_hypothesis,
        wer=_error_rate(word_counts, len(reference_words)),
        cer=_error_rate(character_counts, len(cer_reference)),
    )


def aggregate_error_rates(rates: Iterable[ErrorRate]) -> ErrorRate:
    """Aggregate rates at corpus level by summing errors and reference units."""
    errors = 0
    reference_units = 0
    substitutions = 0
    deletions = 0
    insertions = 0

    for rate in rates:
        errors += rate.errors
        reference_units += rate.reference_units
        substitutions += rate.substitutions
        deletions += rate.deletions
        insertions += rate.insertions

    return ErrorRate(
        errors=errors,
        reference_units=reference_units,
        substitutions=substitutions,
        deletions=deletions,
        insertions=insertions,
    )
