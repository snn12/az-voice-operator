"""Azerbaijani-aware text normalization for reproducible evaluation.

The normalizer is deliberately conservative:

- Azerbaijani letters ``ə ı ö ü ğ ş ç`` are never transliterated to ASCII.
- Diacritics are never stripped.
- Compatibility normalization (NFKC/NFKD) is not allowed, because it can alter
  characters that matter to Azerbaijani orthography.
- Every transformation is configurable, and the configuration is recorded in
  evaluation reports.
"""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass
from typing import Literal

AZERBAIJANI_LOWER = "əıöüğşç"
AZERBAIJANI_UPPER = "ƏIÖÜĞŞÇ"

# Only Azerbaijani-specific case pairs are translated. No letter is mapped to an
# English equivalent: this table changes case, never the underlying phoneme.
_AZERBAIJANI_CASE_MAP = str.maketrans(
    {
        "I": "ı",
        "İ": "i",
        "Ə": "ə",
        "Ö": "ö",
        "Ü": "ü",
        "Ğ": "ğ",
        "Ş": "ş",
        "Ç": "ç",
    }
)

UnicodeForm = Literal["NFC", "NFD", "NONE"]
_ALLOWED_UNICODE_FORMS = frozenset({"NFC", "NFD", "NONE"})


def lower_az(text: str) -> str:
    """Lowercase Azerbaijani text without ASCII folding.

    Python's ``str.lower()`` maps ``I`` to ``i``. Azerbaijani requires ``I`` to
    become ``ı`` and ``İ`` to become ``i``, so the mapping is applied first.
    Azerbaijani letters remain Azerbaijani letters.
    """
    # NFD represents İ as I + COMBINING DOT ABOVE. Replace that sequence before
    # the I -> ı mapping; otherwise the result would be ı + a stray dot instead
    # of the Azerbaijani i.
    text = text.replace("I\u0307", "i")
    return text.translate(_AZERBAIJANI_CASE_MAP).lower()


@dataclass(frozen=True)
class NormalizationConfig:
    """Configurable, reportable text normalization.

    Attributes:
        unicode_form: NFC (default), NFD, or NONE. Compatibility forms are not
            supported because they can rewrite characters.
        lowercase: Apply Azerbaijani-aware lowercasing.
        remove_punctuation: Replace Unicode punctuation with spaces.
        collapse_whitespace: Collapse all whitespace runs to one space.
        strip: Strip leading and trailing whitespace.
    """

    unicode_form: UnicodeForm = "NFC"
    lowercase: bool = True
    remove_punctuation: bool = True
    collapse_whitespace: bool = True
    strip: bool = True

    def __post_init__(self) -> None:
        if self.unicode_form not in _ALLOWED_UNICODE_FORMS:
            raise ValueError(
                f"unicode_form must be one of {sorted(_ALLOWED_UNICODE_FORMS)}, "
                f"got {self.unicode_form!r}"
            )


DEFAULT_NORMALIZATION = NormalizationConfig()

# Entity values (names, dates, times, numbers) keep their punctuation so that
# "19:30" does not silently become "1930".
DEFAULT_ENTITY_NORMALIZATION = NormalizationConfig(remove_punctuation=False)


def normalize_text(
    text: str,
    config: NormalizationConfig = DEFAULT_NORMALIZATION,
) -> str:
    """Normalize text while preserving Azerbaijani orthography.

    The returned string is safe for WER/CER scoring. Callers must retain the
    original text separately; this function never mutates its input.
    """
    if not isinstance(text, str):
        raise TypeError(f"text must be str, got {type(text).__name__}")

    result = text
    if config.unicode_form != "NONE":
        result = unicodedata.normalize(config.unicode_form, result)

    if config.lowercase:
        result = lower_az(result)

    if config.remove_punctuation:
        result = "".join(
            " " if unicodedata.category(char).startswith("P") else char for char in result
        )

    if config.collapse_whitespace:
        result = " ".join(result.split())
    elif config.strip:
        result = result.strip()

    return result
