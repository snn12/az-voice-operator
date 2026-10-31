# STT Benchmark

Planned harness for comparing Google Chirp 3 and Azure Speech on Azerbaijani
restaurant audio.

Expected workflow:

1. Load the frozen corpus manifest and ground-truth transcripts.
2. Run each provider with identical audio and streaming settings.
3. Capture hypotheses, confidence, and per-stage latency.
4. Score WER, entity accuracy, and critical entity errors.
5. Write a versioned report with build, date, and sample size.

Planned files:

- `run_benchmark.py` — provider runner and result writer.
- `score.py` — WER and entity-level scoring.
- `providers/` — thin adapters for the benchmark only.
- `reports/` — generated results (ignored by Git).

No implementation exists yet. No results have been produced.
