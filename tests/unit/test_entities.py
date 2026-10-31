"""Entity scores are independent for names, dates, times, and numbers."""

import pytest

from voice_lab.evaluation.entities import (
    ENTITY_CATEGORIES,
    EntityExample,
    evaluate_entities,
)


def test_categories_are_scored_separately() -> None:
    examples = [
        EntityExample(
            example_id="ex1",
            reference={
                "name": "Əli Məmmədov",
                "date": "2026-11-05",
                "time": "19:30",
                "number": "4",
            },
            hypothesis={
                "name": "əli məmmədov",
                "date": "2026-11-06",
                "time": "19:30",
                "number": "5",
            },
        ),
        EntityExample(
            example_id="ex2",
            reference={
                "name": "Aysel",
                "date": "2026-11-06",
                "time": "20:00",
                "number": "2",
            },
            hypothesis={
                "name": "Aysel",
                "date": "2026-11-06",
                "time": "20:00",
                "number": "2",
            },
        ),
    ]

    report = evaluate_entities(examples)
    scores = report.by_category()

    assert tuple(scores) == ENTITY_CATEGORIES
    assert scores["name"].correct == 2
    assert scores["name"].accuracy == 1.0
    assert scores["date"].correct == 1
    assert scores["date"].accuracy == 0.5
    assert scores["time"].accuracy == 1.0
    assert scores["number"].correct == 1
    assert scores["number"].accuracy == 0.5
    assert len(report.comparisons) == 8


def test_missing_prediction_is_incorrect() -> None:
    report = evaluate_entities(
        [EntityExample("ex1", {"date": "2026-11-05"}, {})],
        categories=("date",),
    )
    score = report.by_category()["date"]
    assert score.total == 1
    assert score.correct == 0
    assert score.accuracy == 0.0
    assert report.comparisons[0].hypothesis is None
    assert report.comparisons[0].correct is False


def test_unexpected_prediction_is_counted_but_not_in_accuracy() -> None:
    report = evaluate_entities(
        [EntityExample("ex1", {}, {"name": "Əli"})],
        categories=("name",),
    )
    score = report.by_category()["name"]
    assert score.total == 0
    assert score.correct == 0
    assert score.unexpected == 1
    assert score.accuracy is None
    assert report.comparisons[0].unexpected is True


def test_no_transliteration_in_entity_matching() -> None:
    report = evaluate_entities(
        [EntityExample("ex1", {"name": "Əli"}, {"name": "Eli"})],
        categories=("name",),
    )
    score = report.by_category()["name"]
    assert score.total == 1
    assert score.correct == 0
    assert score.accuracy == 0.0


def test_time_punctuation_is_not_removed() -> None:
    report = evaluate_entities(
        [EntityExample("ex1", {"time": "19:30"}, {"time": "1930"})],
        categories=("time",),
    )
    score = report.by_category()["time"]
    assert score.correct == 0
    assert report.comparisons[0].normalized_reference == "19:30"
    assert report.comparisons[0].normalized_hypothesis == "1930"


def test_duplicate_example_ids_are_rejected() -> None:
    examples = [
        EntityExample("dup", {"name": "A"}, {}),
        EntityExample("dup", {"name": "B"}, {}),
    ]
    with pytest.raises(ValueError, match="duplicate entity example_id"):
        evaluate_entities(examples)


def test_empty_categories_are_rejected() -> None:
    with pytest.raises(ValueError, match="at least one"):
        evaluate_entities([], categories=())


def test_category_string_is_rejected() -> None:
    with pytest.raises(ValueError, match="sequence of names"):
        evaluate_entities([], categories="name")


def test_non_string_entity_value_is_rejected() -> None:
    with pytest.raises(TypeError, match="must be str or None"):
        evaluate_entities(
            [EntityExample("ex1", {"number": 4}, {})],  # type: ignore[dict-item]
            categories=("number",),
        )
