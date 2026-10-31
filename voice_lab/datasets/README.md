# Datasets

Reserved for consented, licensed audio and transcripts.

**No audio, transcripts, or manifests here are committed to Git.** The parent
`.gitignore` ignores everything in this directory except this README and
`.gitkeep`.

Planned contents:

- `manifest.csv` — clip ID, speaker ID, condition, duration, transcript hash.
- `audio/` — WAV clips, 16 kHz mono, loudness-normalized.
- `transcripts/` — human-verified Azerbaijani transcripts.
- `scenarios/` — conversation scripts for end-to-end tests.
- `holdout/` — final evaluation set, never used for tuning.

Requirements:

- Written consent or a licence for every recording.
- No real caller data from production.
- Speaker diversity across gender, age, and accent.
- Clean and noisy restaurant conditions.
- Double transcription and adjudication for ground truth.

Do not commit audio, personal data, or vendor credentials.
