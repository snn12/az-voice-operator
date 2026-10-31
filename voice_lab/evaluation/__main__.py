"""Command-line entry point for reproducible Voice Lab evaluation runs."""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence

from .entities import ENTITY_CATEGORIES
from .normalization import NormalizationConfig
from .runner import EvaluationError, run_evaluation, write_report


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m voice_lab.evaluation",
        description=(
            "Score Azerbaijani STT transcripts with WER, CER, and entity-level "
            "accuracy. Every record must reference a real, non-empty audio file."
        ),
    )
    parser.add_argument("--dataset", required=True, type=str, help="JSONL dataset path")
    parser.add_argument("--output", type=str, default=None, help="Optional report path")
    parser.add_argument(
        "--cer-include-spaces",
        action="store_true",
        help="Count spaces as characters in CER (default: exclude).",
    )
    parser.add_argument(
        "--keep-punctuation",
        action="store_true",
        help="Do not replace punctuation with spaces in transcript normalization.",
    )
    parser.add_argument(
        "--no-lowercase",
        action="store_true",
        help="Disable Azerbaijani-aware lowercasing.",
    )
    parser.add_argument(
        "--unicode-form",
        choices=("NFC", "NFD", "NONE"),
        default="NFC",
        help="Unicode normalization form (default: NFC).",
    )
    parser.add_argument(
        "--entity-categories",
        default=",".join(ENTITY_CATEGORIES),
        help="Comma-separated entity categories (default: name,date,time,number).",
    )
    parser.add_argument(
        "--code-version",
        default=None,
        help="Git commit or build identifier to record in the report.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    categories = tuple(
        category.strip() for category in args.entity_categories.split(",") if category.strip()
    )
    normalization = NormalizationConfig(
        unicode_form=args.unicode_form,
        lowercase=not args.no_lowercase,
        remove_punctuation=not args.keep_punctuation,
    )

    try:
        report = run_evaluation(
            args.dataset,
            normalization=normalization,
            cer_include_spaces=args.cer_include_spaces,
            entity_categories=categories,
            code_version=args.code_version,
        )
    except (EvaluationError, ValueError) as error:
        parser.exit(status=2, message=f"error: {error}\n")

    if args.output:
        destination = write_report(report, args.output)
        print(f"Wrote report: {destination}")
    else:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
