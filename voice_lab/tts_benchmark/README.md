# TTS Benchmark

Planned blind listening test for Azure Banu and Babek voices on Azerbaijani
restaurant phrases.

Expected workflow:

1. Select a balanced phrase set: greetings, confirmations, numbers, dates,
   names, menu items, and apologies.
2. Synthesize each phrase with every voice at identical settings.
3. Randomize and anonymize samples.
4. Collect naturalness, pronunciation, and preference ratings from listeners.
5. Report mean scores with confidence intervals and verbatim comments.

Planned files:

- `generate_samples.py` — synthesis runner.
- `listening_sheet.md` — blind rating template.
- `score.py` — aggregate scores.
- `samples/` — generated audio, never committed.

No samples exist yet. No listener study has been run.
