"""Evaluation entry points for the Azerbaijani Voice Lab."""

__version__ = "0.1.0"

from .entities import (
    ENTITY_CATEGORIES,
    EntityCategoryScore,
    EntityComparison,
    EntityExample,
    EntityReport,
    evaluate_entities,
)
from .metrics import (
    EditCounts,
    ErrorRate,
    TranscriptScore,
    aggregate_error_rates,
    cer,
    score_transcript,
    wer,
)
from .normalization import (
    AZERBAIJANI_LOWER,
    AZERBAIJANI_UPPER,
    DEFAULT_ENTITY_NORMALIZATION,
    DEFAULT_NORMALIZATION,
    NormalizationConfig,
    lower_az,
    normalize_text,
)
from .runner import EvaluationError, run_evaluation, write_report

__version__ = "0.1.0"

__all__ = [
    "AZERBAIJANI_LOWER",
    "AZERBAIJANI_UPPER",
    "DEFAULT_ENTITY_NORMALIZATION",
    "DEFAULT_NORMALIZATION",
    "ENTITY_CATEGORIES",
    "EditCounts",
    "EntityCategoryScore",
    "EntityComparison",
    "EntityExample",
    "EntityReport",
    "ErrorRate",
    "EvaluationError",
    "NormalizationConfig",
    "TranscriptScore",
    "aggregate_error_rates",
    "cer",
    "evaluate_entities",
    "lower_az",
    "normalize_text",
    "run_evaluation",
    "score_transcript",
    "wer",
    "write_report",
]
