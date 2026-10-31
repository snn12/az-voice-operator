# Latency Benchmark

Planned harness for measuring conversational latency at the caller boundary.

Metrics:

- Time to first audio (TTFA), median and P95.
- Per-stage timing: VAD, STT finalization, LLM first token, TTS first audio.
- Barge-in stop time.
- Handoff connect time.

Rules:

- Measure on the real SIP/media path, not inside a vendor SDK.
- Include slow and failed turns in the sample.
- Record build, environment, date, and sample size with every run.
- Report distributions, not a single best run.

Planned files:

- `harness.py` — scripted call driver.
- `stage_timer.py` — timestamp collection.
- `report.py` — median, P95, and histogram output.
- `results/` — generated results (ignored by Git).

Proposed targets: median TTFA ≤ 700 ms, P95 ≤ 1,200 ms, barge-in ≤ 300 ms.
These are targets, not measurements.
