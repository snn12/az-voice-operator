"""WER and CER tests, including Azerbaijani originals and normalization."""

import pytest

from voice_lab.evaluation.metrics import (
    ErrorRate,
    aggregate_error_rates,
    cer,
    score_transcript,
    wer,
)


def test_wer_perfect_match() -> None:
    rate = wer("Əli Bakıya gəldi", "əli bakıya gəldi")
    assert rate.errors == 0
    assert rate.substitutions == 0
    assert rate.deletions == 0
    assert rate.insertions == 0
    assert rate.rate == 0.0


def test_wer_substitution() -> None:
    rate = wer("bir iki üç", "bir iki dörd")
    assert (rate.substitutions, rate.deletions, rate.insertions) == (1, 0, 0)
    assert rate.rate == pytest.approx(1 / 3)


def test_wer_deletion() -> None:
    rate = wer("bir iki üç", "bir iki")
    assert (rate.substitutions, rate.deletions, rate.insertions) == (0, 1, 0)
    assert rate.rate == pytest.approx(1 / 3)


def test_wer_insertion() -> None:
    rate = wer("bir iki", "bir iki üç")
    assert (rate.substitutions, rate.deletions, rate.insertions) == (0, 0, 1)
    assert rate.rate == pytest.approx(0.5)


def test_wer_mixed_edits() -> None:
    rate = wer("a b c", "a x c d")
    assert (rate.substitutions, rate.deletions, rate.insertions) == (1, 0, 1)
    assert rate.errors == 2
    assert rate.reference_units == 3


def test_empty_reference_has_undefined_rate_but_reports_insertions() -> None:
    empty = wer("", "")
    assert empty.errors == 0
    assert empty.rate is None

    inserted = wer("", "əlavə")
    assert inserted.errors == 1
    assert inserted.reference_units == 0
    assert inserted.rate is None


def test_cer_substitution() -> None:
    rate = cer("abc", "adc")
    assert (rate.substitutions, rate.deletions, rate.insertions) == (1, 0, 0)
    assert rate.rate == pytest.approx(1 / 3)


def test_cer_space_handling_is_configurable() -> None:
    without_spaces = cer("ab cd", "abcd", include_spaces=False)
    assert without_spaces.errors == 0
    assert without_spaces.rate == 0.0

    with_spaces = cer("ab cd", "abcd", include_spaces=True)
    assert with_spaces.errors == 1
    assert with_spaces.reference_units == 5
    assert with_spaces.rate == pytest.approx(1 / 5)


def test_score_transcript_retains_original_and_normalized_text() -> None:
    score = score_transcript("Əli, BAKI!", "əli bakı")
    assert score.reference_original == "Əli, BAKI!"
    assert score.hypothesis_original == "əli bakı"
    assert score.reference_normalized == "əli bakı"
    assert score.hypothesis_normalized == "əli bakı"
    assert score.wer.rate == 0.0
    assert score.cer.rate == 0.0


def test_score_transcript_preserves_azerbaijani_characters() -> None:
    score = score_transcript("şəhər", "şəhər")
    assert score.reference_normalized == "şəhər"


def test_aggregate_error_rates_sums_counts() -> None:
    aggregate = aggregate_error_rates(
        [
            wer("a b", "a"),
            wer("c d e", "c d e"),
        ]
    )
    assert aggregate.errors == 1
    assert aggregate.reference_units == 5
    assert aggregate.rate == pytest.approx(0.2)


def test_error_rate_rejects_inconsistent_counts() -> None:
    with pytest.raises(ValueError, match="errors must equal"):
        ErrorRate(
            errors=2,
            reference_units=3,
            substitutions=1,
            deletions=0,
            insertions=0,
        )
