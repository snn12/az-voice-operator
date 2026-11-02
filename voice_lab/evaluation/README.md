# Evaluation

Scoring foundation for Azerbaijani Voice Lab experiments.

> **Status: tooling implemented; no experiment has been run.** No benchmark
> result is reported here. Vendor Azerbaijani support and quality remain
> unverified. Audio fixtures used by unit tests are synthetic and validate code
> behaviour only.

## Implemented

| Module | Purpose |
| --- | --- |
| `normalization.py` | Azerbaijani-aware, configurable text normalization |
| `metrics.py` | WER and CER with edit counts and corpus aggregation |
| `entities.py` | Independent name, date, time, and number scoring |
| `runner.py` | JSONL dataset validation, audio hashing, report generation |
| `__main__.py` | Command-line runner |

Not implemented yet:

- Dataset collection or annotation.
- Automatic entity extraction; entity values must be supplied as annotations.
- Semantic date/time canonicalization or relative-date resolution.
- Confidence intervals and significance testing.
- TTS and latency scoring (those live in their own Voice Lab directories).
- Any benchmark run or provider comparison.

## Azerbaijani text rules

1. Preserve `ə`, `ı`, `ö`, `ü`, `ğ`, `ş`, `ç` and their uppercase forms.
2. Never map them to `e`, `i`, `o`, `u`, `g`, `s`, `c`.
3. Never strip diacritics.
4. Do not use NFKC or NFKD; only NFC (default), NFD, or no Unicode normalization.
5. Normalization is configurable:
   - Unicode form
   - Azerbaijani-aware lowercasing
   - punctuation replacement
   - whitespace collapsing and stripping
6. The exact configuration is written into every report and hashed.
7. The original transcript is always retained next to the normalized transcript.

Azerbaijani casing is handled explicitly: `I` lowercases to `ı`, and `İ`
lowercases to `i`. Python's default lowercasing is not used for these pairs.
This also holds for decomposed input: under NFD, `İ` is `I` plus a combining dot
and still lowercases to `i`.

## Dataset format

One JSON object per line (JSONL), UTF-8:

```json
{
  "id": "utt-001",
  "audio": "audio/utt-001.wav",
  "reference": "Əli, saat 19:30-da 4 nəfər.",
  "hypothesis": "əli saat 19:30-da 4 nəfər",
  "entities": {
    "reference": {
      "name": "Əli",
      "date": "2026-11-05",
      "time": "19:30",
      "number": "4"
    },
    "hypothesis": {
      "name": "əli",
      "date": "2026-11-05",
      "time": "19:30",
      "number": "4"
    }
  }
}
```

Rules:

- `id` is unique and non-empty.
- `audio` is resolved relative to the dataset file. It must exist and be
  non-empty, or the run aborts.
- `reference` and `hypothesis` are required strings.
- `entities` is optional. Missing categories are not scored; a prediction for an
  unannotated category is reported as `unexpected`.
- Entity categories default to `name`, `date`, `time`, and `number`.
- Entity normalization preserves punctuation, so `19:30` and `1930` are not
  treated as equal.
- Audio and private transcripts stay out of Git.

## Scoring

**WER** — whitespace-delimited words after normalization. The report includes
substitutions, deletions, insertions, error count, reference units, and rate.
Corpus WER is computed by summing errors and reference units, not by averaging
per-utterance percentages.

**CER** — character-level edit distance after normalization. Spaces are excluded
by default and can be included with `--cer-include-spaces`. The choice is
recorded.

**Entity accuracy** — each configured category is scored independently. The
denominator contains only examples where the reference annotates that category.
Missing predictions count as errors. Unexpected predictions are reported
separately and do not inflate accuracy. Accuracy is `null` when a category has
no annotated examples.

An empty reference has an undefined rate (`null`); the raw error counts are
still reported. Corpus rates sum every edit operation, so an empty reference
contributes its insertions to the numerator and zero reference units to the
denominator. `mean_utterance_*` averages only utterances with a defined rate.

## Reproducibility

Every report records:

- Dataset path and SHA-256.
- Per-record audio path and SHA-256.
- Normalization and entity-normalization configuration.
- CER space setting and entity categories.
- Config SHA-256.
- Schema and tool version.
- Optional code version (commit or build ID).
- UTC generation timestamp.
- Original and normalized transcripts.
- Per-record and aggregate counts.

Runs are deterministic except for `generated_at_utc`. Re-running the same
dataset, audio, config, and code version produces identical scores.

## Usage

```bash
python -m voice_lab.evaluation \
  --dataset voice_lab/datasets/manifest.jsonl \
  --output voice_lab/evaluation/reports/run.json \
  --code-version <commit-or-build-id>
```

Options:

```text
--cer-include-spaces        count spaces in CER
--keep-punctuation          preserve punctuation in transcript normalization
--no-lowercase              disable Azerbaijani-aware lowercasing for transcripts
--unicode-form {NFC,NFD,NONE}
--entity-categories name,date,time,number
--code-version <value>
```

The command exits with status 2 if the dataset is invalid, audio is missing,
empty, or unreadable, ids are duplicated, a required field is absent, the report
cannot be written, or `--output` would overwrite the dataset. Stdout and
`--output` reports are UTF-8.

## Validity rules

- A benchmark result is valid only when it was produced from real, listed audio.
- The runner rejects missing, empty, or unreadable audio, but it cannot prove
  where a hypothesis came from. The operator must confirm the hypothesis was
  produced from the same audio by the system under test.
- Never hand-edit scores or drop failed utterances.
- Never tune on the hold-out set.
- Never claim a vendor comparison before E0 confirms Azerbaijani support.
- Unit tests use synthetic silence; they validate code only and are not evidence
  of speech quality.

## Reports and decision memos

Generated reports belong in `reports/` and stay out of Git unless they contain no
private data. The final decision memo must include:

- Experiment ID, code version, and configuration hash.
- Dataset and audio hashes.
- Sample size and composition.
- WER, CER, and per-category entity accuracy.
- Median and P95 latency where applicable.
- Failures and exclusions with reasons.
- A link to the raw report.

No report exists yet.

## Related

- [Voice Lab overview](../README.md)
- [Architecture](../../docs/ARCHITECTURE.md)
- [Decisions](../../docs/DECISIONS.md)
- [Pilot Success Metrics (Notion)](https://app.notion.com/p/40a541b17b3f81418385d6c6b6ae7848)
