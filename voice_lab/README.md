# Voice Lab

Offline experiments for selecting the Azerbaijani speech stack. The Voice Lab is
separate from the product runtime: it produces evidence, not production code.

> **Status: preparation and evaluation tooling.** No experiment has been run and
> no result is reported here. Vendor Azerbaijani coverage is unverified.

## Purpose

Answer four questions with repeatable measurements:

1. Which STT system transcribes Azerbaijani restaurant calls most accurately?
2. Which TTS voice sounds natural and pronounces domain terms correctly?
3. Does a component pipeline meet the latency target, and how does OpenAI
   Realtime compare?
4. What does each option cost and how hard is it to operate?

## Systems under test

| ID | System | Layer |
| --- | --- | --- |
| V1 | Google Chirp 3 | STT |
| V2 | Azure Speech STT | STT |
| V3 | Azure TTS — Banu | TTS |
| V4 | Azure TTS — Babek | TTS |
| V5 | OpenAI Realtime | End-to-end speech-to-speech |

V1–V4 are component options. V5 replaces STT → LLM → TTS and must be compared at
the conversation level, not only by word error rate.

## Experiment sequence

| ID | Experiment | Gate |
| --- | --- | --- |
| E0 | Availability and compliance | Must pass before any benchmark |
| E1 | STT benchmark | WER, entity accuracy, latency |
| E2 | TTS listening test | Naturalness, pronunciation |
| E3 | End-to-end conversation | Task success, TTFA, barge-in, handoff |
| E4 | Operability and cost | Concurrency, reliability, price |

E0 checks official documentation, regional availability, streaming support,
pricing, rate limits, data retention, and training-use terms. A system without
confirmed Azerbaijani support is excluded from that layer. Never substitute
another language as a proxy.

## Datasets

`datasets/` is reserved for a consented, licensed test corpus:

- 200+ restaurant-domain utterances.
- 20+ speakers with varied gender and age.
- Clean and noisy restaurant conditions.
- 20 conversation scenarios covering reservations, FAQ, complaints, and handoff.
- Double-transcribed, adjudicated ground truth.
- A hold-out set reserved for final evaluation.

**No audio is committed to Git.** The directory is ignored except for its
placeholder files. Do not place private recordings here.

## Azerbaijani evaluation requirements

These rules apply to every STT and end-to-end evaluation:

- **Preserve the Azerbaijani alphabet:** `ə`, `ı`, `ö`, `ü`, `ğ`, `ş`, `ç`, and
  their uppercase forms. Never ASCII-fold them to `e`, `i`, `o`, `u`, `g`, `s`,
  `c`.
- **Never strip diacritics** or use compatibility normalization (NFKC/NFKD).
- **Normalization is configurable and recorded:** case, punctuation, whitespace,
  and Unicode form are explicit settings, not hidden defaults.
- **Report WER and CER** for every transcript set. CER space handling is an
  explicit setting.
- **Score entity categories separately:** names, dates, times, and numbers.
- **Keep original transcripts alongside normalized transcripts** in every
  report. Normalization never replaces the source text.
- **Make runs reproducible:** record the dataset SHA-256, every audio file hash,
  the normalization/scoring config, the tool version, and an optional code
  version.
- **No benchmark result without real audio testing.** A report is invalid if any
  referenced audio file is missing, empty, or not the audio the hypotheses were
  produced from.

The scoring foundation is in [`evaluation/`](evaluation/README.md). Dataset
collection and all benchmark runs remain **not started**.

## Metrics

| Metric | Proposed threshold |
| --- | --- |
| STT WER (hold-out) | ≤ 15% |
| STT CER (hold-out) | Reported alongside WER; threshold not yet approved |
| Entity accuracy (name, date, time, number) | ≥ 95% |
| TTS naturalness (blind MOS-style) | ≥ 4.0 / 5 |
| TTS domain pronunciation | ≥ 90% |
| End-to-end task success | ≥ 90% |
| Median TTFA | ≤ 700 ms |
| P95 TTFA | ≤ 1,200 ms |
| Barge-in stop time | ≤ 300 ms |
| Handoff correctness | ≥ 95% |

Thresholds are proposals aligned with the Notion *Pilot Success Metrics* page and
require sign-off. They are not results. The CER threshold is intentionally
unset until real audio evidence exists.

## Directory guide

```text
voice_lab/
├── datasets/          consented corpus and manifests (not committed)
├── stt_benchmark/     transcription scoring and provider runners
├── tts_benchmark/     synthesis samples and blind listening sheets
├── latency_benchmark/ TTFA and barge-in harnesses
└── evaluation/        normalization, WER/CER, entity scoring, run reports
```

Each directory contains a README describing its expected inputs and outputs.

## Procedure

1. Complete E0 and freeze the eligible vendor list.
2. Freeze corpus, scripts, rubric, normalization config, and scoring config with
   version IDs.
3. Run E1 on identical audio; report WER, CER, entity accuracy for names, dates,
   times, and numbers, plus per-stage latency.
4. Run E2 blind and randomized; hide vendor names from listeners.
5. Build both the component pipeline and the realtime path with the same
   prompts and restaurant content.
6. Run E3 scenarios; record success, TTFA, barge-in, and handoff.
7. Score independently; keep failed runs; report median and P95.
8. Write a decision memo and update `docs/DECISIONS.md`.

## Rules

- Never report a result without the build, date, sample size, and environment.
- Never exclude failed calls from the sample.
- Never tune on the hold-out set.
- Never commit vendor credentials or private audio.
- Never transliterate Azerbaijani text for scoring; retain original and
  normalized transcripts together.
- Never report a benchmark number without real audio testing and the recorded
  audio hashes.
- Lab results do not authorize production; the pilot remains the validation
  gate.

## Related

- [Architecture](../docs/ARCHITECTURE.md)
- [Pilot Success Metrics (Notion)](https://app.notion.com/p/40a541b17b3f81418385d6c6b6ae7848)
- [Voice Lab Preparation (Notion)](https://app.notion.com/p/40a541b17b3f81929c43cd6db2234847)
