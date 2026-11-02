"""Category-level evaluation for names, dates, times, and numbers.

Entity values are supplied as annotations rather than guessed from raw text. This
keeps the evaluation reproducible and avoids pretending that a heuristic parser
is ground truth.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from .normalization import (
    DEFAULT_ENTITY_NORMALIZATION,
    NormalizationConfig,
    normalize_text,
)

ENTITY_CATEGORIES: tuple[str, ...] = ("name", "date", "time", "number")


@dataclass(frozen=True)
class EntityExample:
    """One transcript's reference and predicted entity annotations.

    A missing key or ``None`` means the category is absent. An empty string is a
    present but empty value.
    """

    example_id: str
    reference: Mapping[str, str | None]
    hypothesis: Mapping[str, str | None]

    def __post_init__(self) -> None:
        if not self.example_id:
            raise ValueError("example_id must not be empty")


@dataclass(frozen=True)
class EntityComparison:
    """Auditable comparison for one category of one example."""

    example_id: str
    category: str
    reference: str | None
    hypothesis: str | None
    normalized_reference: str | None
    normalized_hypothesis: str | None
    correct: bool
    unexpected: bool

    def to_dict(self) -> dict[str, object]:
        return {
            "example_id": self.example_id,
            "category": self.category,
            "reference": self.reference,
            "hypothesis": self.hypothesis,
            "normalized_reference": self.normalized_reference,
            "normalized_hypothesis": self.normalized_hypothesis,
            "correct": self.correct,
            "unexpected": self.unexpected,
        }


@dataclass(frozen=True)
class EntityCategoryScore:
    """Aggregate score for one entity category."""

    category: str
    correct: int
    total: int
    unexpected: int

    def __post_init__(self) -> None:
        if self.correct < 0 or self.total < 0 or self.unexpected < 0:
            raise ValueError("entity counts cannot be negative")
        if self.correct > self.total:
            raise ValueError("correct cannot exceed total")

    @property
    def accuracy(self) -> float | None:
        """Correct / annotated total, or ``None`` when nothing was annotated."""
        if self.total == 0:
            return None
        return self.correct / self.total

    def to_dict(self) -> dict[str, object]:
        return {
            "category": self.category,
            "correct": self.correct,
            "total": self.total,
            "unexpected": self.unexpected,
            "accuracy": self.accuracy,
        }


@dataclass(frozen=True)
class EntityReport:
    """Per-category scores plus every individual comparison for audit."""

    categories: tuple[EntityCategoryScore, ...]
    comparisons: tuple[EntityComparison, ...]

    def by_category(self) -> dict[str, EntityCategoryScore]:
        return {score.category: score for score in self.categories}

    def to_dict(self) -> dict[str, object]:
        return {
            "categories": [score.to_dict() for score in self.categories],
            "comparisons": [comparison.to_dict() for comparison in self.comparisons],
        }


def _entity_value(entities: Mapping[str, str | None], category: str) -> str | None:
    value = entities.get(category)
    if value is None:
        return None
    if not isinstance(value, str):
        raise TypeError(f"entity {category!r} must be str or None, got {type(value).__name__}")
    return value


def evaluate_entities(
    examples: Sequence[EntityExample],
    categories: Sequence[str] = ENTITY_CATEGORIES,
    config: NormalizationConfig = DEFAULT_ENTITY_NORMALIZATION,
) -> EntityReport:
    """Score entity categories independently.

    Only categories annotated in the reference are counted in the denominator.
    A prediction for an unannotated category is recorded as ``unexpected`` and
    does not inflate accuracy. Values are compared after configurable
    normalization (case and whitespace by default), with punctuation preserved
    so that ``19:30`` and ``1930`` are not treated as equal.
    """
    if not categories:
        raise ValueError("at least one entity category is required")
    if isinstance(categories, str):
        raise ValueError("categories must be a sequence of names, not a string")
    if any(not isinstance(category, str) or not category for category in categories):
        raise ValueError("entity categories must be non-empty strings")
    if len(set(categories)) != len(categories):
        raise ValueError("entity categories must be unique")

    totals = {category: 0 for category in categories}
    correct = {category: 0 for category in categories}
    unexpected = {category: 0 for category in categories}
    comparisons: list[EntityComparison] = []
    seen_ids: set[str] = set()

    for example in examples:
        if example.example_id in seen_ids:
            raise ValueError(f"duplicate entity example_id: {example.example_id!r}")
        seen_ids.add(example.example_id)

        for category in categories:
            reference_value = _entity_value(example.reference, category)
            hypothesis_value = _entity_value(example.hypothesis, category)

            if reference_value is None:
                if hypothesis_value is None:
                    continue
                unexpected[category] += 1
                comparisons.append(
                    EntityComparison(
                        example_id=example.example_id,
                        category=category,
                        reference=None,
                        hypothesis=hypothesis_value,
                        normalized_reference=None,
                        normalized_hypothesis=normalize_text(hypothesis_value, config),
                        correct=False,
                        unexpected=True,
                    )
                )
                continue

            normalized_reference = normalize_text(reference_value, config)
            normalized_hypothesis = (
                normalize_text(hypothesis_value, config) if hypothesis_value is not None else None
            )
            is_correct = (
                normalized_hypothesis is not None and normalized_reference == normalized_hypothesis
            )

            totals[category] += 1
            if is_correct:
                correct[category] += 1

            comparisons.append(
                EntityComparison(
                    example_id=example.example_id,
                    category=category,
                    reference=reference_value,
                    hypothesis=hypothesis_value,
                    normalized_reference=normalized_reference,
                    normalized_hypothesis=normalized_hypothesis,
                    correct=is_correct,
                    unexpected=False,
                )
            )

    scores = tuple(
        EntityCategoryScore(
            category=category,
            correct=correct[category],
            total=totals[category],
            unexpected=unexpected[category],
        )
        for category in categories
    )
    return EntityReport(categories=scores, comparisons=tuple(comparisons))
