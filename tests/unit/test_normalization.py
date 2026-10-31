"""Azerbaijani normalization preserves orthography and is configurable."""

import unicodedata

import pytest

from voice_lab.evaluation.normalization import (
    AZERBAIJANI_LOWER,
    AZERBAIJANI_UPPER,
    NormalizationConfig,
    lower_az,
    normalize_text,
)


def test_alphabet_constants() -> None:
    assert AZERBAIJANI_LOWER == "əıöüğşç"
    assert AZERBAIJANI_UPPER == "ƏIÖÜĞŞÇ"


def test_lower_az_uses_azerbaijani_case_pairs() -> None:
    assert lower_az("IİƏÖÜĞŞÇ") == "ıiəöüğşç"


def test_normalization_preserves_every_azerbaijani_letter() -> None:
    result = normalize_text("Əı öü ğşç")
    assert result == "əı öü ğşç"


def test_no_ascii_transliteration() -> None:
    pairs = {
        "ə": "e",
        "ı": "i",
        "ö": "o",
        "ü": "u",
        "ğ": "g",
        "ş": "s",
        "ç": "c",
    }
    for azerbaijani, english in pairs.items():
        normalized = normalize_text(azerbaijani)
        assert normalized == azerbaijani
        assert normalized != english


def test_punctuation_removal_is_configurable() -> None:
    text = "Əli, Bakı!"
    assert normalize_text(text) == "əli bakı"
    assert normalize_text(text, NormalizationConfig(remove_punctuation=False)) == "əli, bakı!"


def test_lowercasing_is_configurable() -> None:
    text = "ƏLİ"
    assert normalize_text(text) == "əli"
    assert normalize_text(text, NormalizationConfig(lowercase=False)) == "ƏLİ"


def test_whitespace_is_collapsed_and_stripped() -> None:
    assert normalize_text("  Əli \t Bakı \n") == "əli bakı"


def test_default_nfc_keeps_composed_characters() -> None:
    normalized = normalize_text("ö")
    assert normalized == "ö"
    assert len(normalized) == 1


def test_nfd_is_explicit_and_does_not_drop_marks() -> None:
    normalized = normalize_text(
        "ö",
        NormalizationConfig(unicode_form="NFD", lowercase=False),
    )
    assert normalized == unicodedata.normalize("NFD", "ö")
    assert normalized != "o"


def test_invalid_unicode_form_is_rejected() -> None:
    with pytest.raises(ValueError, match="unicode_form"):
        NormalizationConfig(unicode_form="NFKC")  # type: ignore[arg-type]


def test_non_string_is_rejected() -> None:
    with pytest.raises(TypeError):
        normalize_text(123)  # type: ignore[arg-type]
