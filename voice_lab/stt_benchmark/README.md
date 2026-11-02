# STT Benchmark

Planned harness for comparing Google Chirp 3 and Azure Speech on Azerbaijani
restaurant audio.

Expected workflow:

1. Load the frozen corpus manifest and ground-truth transcripts.
2. Run each provider with identical audio and streaming settings.
3. Capture hypotheses, confidence, and per-stage latency.
4. Score WER and CER, plus name, date, time, and number accuracy separately.
5. Write a versioned report with build, date, audio hashes, and sample size.

Planned files:

- `run_benchmark.py` — provider runner and result writer.
- `score.py` — adapter around the implemented `voice_lab.evaluation` scorer.
- `providers/` — thin adapters for the benchmark only.
- `reports/` — generated results (ignored by Git).

The scoring foundation exists in [`../evaluation/`](../evaluation/README.md).
The provider runner does not exist yet, and no benchmark has been produced.
