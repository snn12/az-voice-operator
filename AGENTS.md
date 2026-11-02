# AGENTS.md — AZ VOICE OPERATOR

Operating rules for every human or AI contributor working in this repository.
Read this file before changing code, documentation, infrastructure, or data.

## 1. Project purpose

AZ VOICE OPERATOR is an Azerbaijani-first voice AI operator for restaurants.

The MVP handles two jobs:

1. **Reservations** — create, change, and cancel table bookings by phone.
2. **FAQ** — answer approved questions about hours, address, menu, allergens,
   parking, and similar topics.

The product is a SaaS offering for the Azerbaijani market. It must speak
Azerbaijani naturally, understand local names and mixed speech, and hand a call
to a human whenever it is unsure or the caller asks.

**Current phase:** Phase 0 — Product Discovery. The voice engine is **not
implemented**. Nothing in this repository is a measured result; anything not
yet tested is marked *planned*, *proposed*, or *not measured*.

## 2. Architecture principles

- **Modular monolith first.** One deployable Python service with clear internal
  boundaries. Do not split into microservices before the pilot proves the need.
- **Ports and adapters.** Conversation logic depends on provider interfaces
  (`STTProvider`, `TTSProvider`, `LLMProvider`), never on a vendor SDK directly.
- **Hybrid by design.** STT, LLM, and TTS are independently replaceable so the
  Voice Lab can compare Google Chirp 3, Azure Speech, and OpenAI Realtime.
- **Telephony-agnostic core.** SIP and media handling stay at the edge so the
  conversation core can be tested without a phone line.
- **Latency is a feature.** Every stage must expose timing. Targets: median TTFA
  ≤ 700 ms, P95 ≤ 1,200 ms, stretch 300–400 ms. These are targets, not results.
- **Safe by default.** Low confidence, ambiguous requests, complaints, and
  explicit human requests trigger handoff rather than a guess.
- **Observable by default.** Every call gets an ID, structured logs, stage
  timings, and an auditable outcome.
- **No secrets in the repository.** Configuration comes from the environment.

## 3. Azerbaijani-first requirements

Azerbaijani is the primary language, not a translation layer.

- All user-facing prompts, confirmations, error messages, and handoff phrases
  are written and reviewed in Azerbaijani first.
- Support the Latin Azerbaijani alphabet correctly: `ə`, `ı`, `ö`, `ü`, `ç`,
  `ş`, `ğ`. Never strip or transliterate these characters in storage or search.
- Handle Azerbaijani names, place names, and mixed Azerbaijani/Russian/English
  speech. Mixed-language behaviour must be tested, not assumed.
- Confirm critical fields (date, time, party size, phone number) by reading them
  back before committing a reservation.
- Use formal address (`siz`) by default; never invent a casual brand tone.
- Russian and English are fallback languages only, and only if the pilot
  requires them. Do not claim multilingual support before it is tested.
- Vendor language coverage must be verified against official documentation
  before any benchmark or integration. Never use another language as a proxy.
- Do not generate synthetic "results" for Azerbaijani accuracy.

## 4. Hybrid provider architecture

Provider responsibilities are separated behind interfaces:

| Layer | Interface | Candidate providers | Status |
| --- | --- | --- | --- |
| STT | `STTProvider` | Google Chirp 3, Azure Speech | Planned |
| LLM / dialog | `LLMProvider` | Low-latency LLM API (TBD) | Planned |
| TTS | `TTSProvider` | Azure Banu, Azure Babek | Planned |
| End-to-end | `RealtimeProvider` | OpenAI Realtime | Under evaluation |

Rules:

- A provider adapter lives under `src/az_voice_operator/providers/<layer>/`.
- Adapters translate vendor events into internal domain events. Vendor types
  must not leak into `conversation/`, `restaurant/`, or API schemas.
- Selection is configuration-driven, with an explicit fallback order.
- Provider-specific behaviour (timeouts, retries, audio formats) stays inside
  the adapter.
- A new provider requires: an interface implementation, contract tests, a
  latency note, and an entry in `docs/DECISIONS.md` when it becomes the default.
- Do not hardcode vendor names in business logic.

## 5. Repository layout

```text
src/az_voice_operator/
  config/          settings and provider selection
  providers/       stt/, tts/, llm/ adapters
  conversation/    dialog state, intent handling, handoff policy
  audio/           streaming, buffering, VAD, codecs
  restaurant/      reservation domain and FAQ knowledge
  monitoring/      logging, metrics, tracing, call audit
voice_lab/         offline benchmarks and evaluation assets
tests/             unit/, integration/, voice/
scripts/           developer and operations scripts
infrastructure/    docker and deployment assets
docs/              product, architecture, roadmap, security, decisions
```

## 6. Coding conventions

- Python 3.11+, full type hints on public functions and methods.
- Format and lint with **Ruff** (`line-length = 100`, rules in `pyproject.toml`).
- Prefer small, pure functions in the domain layer; keep I/O at the edges.
- Use `async` for network, audio, and provider calls; never block the event loop.
- Use dataclasses or typed models for domain objects; no untyped dictionaries
  crossing module boundaries.
- Raise specific exceptions; never swallow errors silently.
- Log structured events with `call_id`, stage, and duration. Never log full
  phone numbers, transcripts, or credentials at INFO level.
- Comments explain *why*, not *what*. Keep them current.
- No dead code, no commented-out blocks, no placeholder vendor SDK calls.
- New runtime dependencies require justification in the pull request. Keep the
  dependency list minimal.
- Do not add a framework, queue, or database driver before the module that
  needs it exists.

## 7. Testing requirements

- `tests/unit/` — domain logic, state machine, validation, provider contracts.
  Fast, deterministic, no network.
- `tests/integration/` — adapters and persistence against local fakes or
  containers. Must not require production credentials.
- `tests/voice/` — audio fixtures, transcription checks, latency harnesses.
  Skipped automatically when fixtures or vendor credentials are absent.
- Every bug fix includes a regression test.
- Reservation logic requires table-driven tests for date, time, party size,
  duplicates, and cancellation.
- Provider adapters require contract tests that run against a fake transport.
- Latency tests report median and P95; never report only the best run.
- STT evaluation reports both WER and CER, with the normalization settings and
  dataset/audio hashes recorded.
- Entity accuracy for names, dates, times, and numbers is reported separately.
- Keep original transcripts alongside normalized transcripts; never ASCII-fold
  `ə`, `ı`, `ö`, `ü`, `ğ`, `ş`, or `ç`.
- Never claim a benchmark result without real audio testing. Synthetic fixtures
  validate code only.
- Tests must not call paid vendor APIs in CI by default.
- Never commit private recordings. Use consented, licensed, or synthetic audio
  only, and keep it out of Git.
- A feature is not done until lint, unit tests, and relevant integration tests
  pass locally.

## 8. Security rules

- **Never** commit API keys, passwords, tokens, private keys, or `.env` files.
- `.env.example` contains placeholders only. Real values live in the local
  environment or a secret manager.
- Do not paste secrets into issues, pull requests, logs, or chat.
- Treat caller data as personal data: phone numbers, names, recordings, and
  transcripts are sensitive.
- Record calls only with the consent required by applicable Azerbaijani law and
  the venue contract. Define retention before collecting audio.
- Do not send production call data to vendor evaluation tools or public LLMs
  without an approved data-processing agreement.
- Validate and bound all external input: audio size, duration, phone format,
  reservation fields, and tool-call arguments.
- Follow least privilege for cloud roles and database users.
- Report vulnerabilities privately to the maintainers; do not open a public
  issue with exploit details.
- See `docs/SECURITY.md` for the full policy.

## 9. Git workflow

- Default branch: `main`. It must stay deployable.
- Work on short-lived branches: `feat/...`, `fix/...`, `docs/...`, `chore/...`.
- Commit messages follow Conventional Commits:
  `type(scope): imperative summary`.
- Keep commits focused. Do not mix refactors with behaviour changes.
- Never rewrite or force-push shared history.
- Never commit generated audio, datasets, build output, or local environment
  files.
- Before committing: run `git status`, `git diff --staged`, and a secret scan.
- Do not push until the local commit has been reviewed and verified.
- Do not change the configured remote or Git identity as part of a code change.

## 10. Documentation requirements

- Every material decision is recorded in `docs/DECISIONS.md` with context,
  decision, status, and consequences.
- `docs/PRD.md` is the product source of truth; update it when scope changes.
- `docs/ARCHITECTURE.md` describes the current and planned system. Mark planned
  components clearly.
- `docs/ROADMAP.md` tracks phases and exit criteria.
- `docs/SECURITY.md` covers data handling, secrets, and incident response.
- Use precise status labels: **Implemented**, **Planned**, **Proposed**,
  **Not measured**. Never imply a feature works because it is described.
- Do not invent benchmarks, pilot data, customer quotes, or vendor claims.
- Link to the Notion project workspace for tasks and discovery assets instead of
  duplicating them in the repository.
- Keep documentation in English; Azerbaijani is required for user-facing
  product copy and conversation content.

## 11. Definition of done

A change is done when:

- The behaviour is implemented and typed.
- Lint and relevant tests pass.
- Security and privacy impact is reviewed.
- Documentation and decision records are updated.
- No secret, private audio, or generated artifact is staged.
- The commit message describes the change accurately.
