# Architecture

**Status:** Proposed design for the MVP. No voice component is implemented.
**Last updated:** 2026-11-01

> This document describes the intended system. Anything labelled *planned* does
> not exist in code yet. There are no measured latency or quality results.

## 1. Goals and constraints

- Natural, low-latency Azerbaijani phone conversations.
- Independent substitution of STT, LLM, and TTS providers.
- A modular monolith that one team can build, deploy, and operate.
- Clear human-handoff behaviour.
- Auditable reservations and calls.
- No vendor SDK leakage into domain logic.

Constraints:

- Python 3.11+, FastAPI, PostgreSQL.
- SIP trunk telephony; the provider is not yet selected.
- Vendor Azerbaijani coverage must be verified first.
- MVP targets 10 concurrent calls per venue, with a path to more.

## 2. System context

```text
        Caller
          │  PSTN
          ▼
   ┌──────────────┐        ┌─────────────────────┐
   │ SIP trunk /  │◄──────►│  AZ VOICE OPERATOR  │
   │ media gateway│  RTP   │  (FastAPI service)  │
   └──────────────┘        └──────┬──────────────┘
                                  │
              ┌───────────────────┼────────────────────┐
              ▼                   ▼                    ▼
      Speech providers      LLM provider        PostgreSQL
      (STT / TTS)           (dialog + tools)    (calls, bookings, config)
              │
              ▼
      Human handoff destination
```

Planned supporting systems: object storage for consented recordings, a metrics
and tracing backend, and a Next.js dashboard for venue configuration.

## 3. Internal modules

```text
src/az_voice_operator/
├── config/          settings, provider selection, validation
├── providers/
│   ├── stt/         STT port + Google Chirp 3 / Azure Speech adapters
│   ├── tts/         TTS port + Azure Banu / Babek adapters
│   └── llm/         LLM port + low-latency API adapter, tool schemas
├── conversation/    dialog state machine, intents, policies, handoff
├── audio/           streaming, buffering, VAD, resampling, barge-in
├── restaurant/      reservation domain, availability, FAQ knowledge base
└── monitoring/      structured logging, metrics, tracing, call audit
```

### Dependency rule

`conversation` and `restaurant` define the domain. They may depend on
`config`, shared types, and provider *interfaces* — never on concrete adapters.
`providers` depend on the domain interfaces. `audio` and `monitoring` are
cross-cutting and must not contain business rules.

## 4. Provider ports

```python
class STTProvider(Protocol):
    async def open_stream(self, config: STTConfig) -> STTStream: ...
    async def close(self) -> None: ...


class TTSProvider(Protocol):
    async def synthesize(self, text: str, voice: VoiceConfig) -> AsyncIterator[bytes]: ...
    async def close(self) -> None: ...


class LLMProvider(Protocol):
    async def respond(self, messages: list[Message], tools: list[ToolSpec]) -> LLMResult: ...
```

Actual interfaces are planned and will be defined with tests before adapters.

Rules:

- One adapter per vendor and layer.
- Adapters normalise audio formats, errors, and timing into internal types.
- Provider selection comes from configuration with an explicit fallback chain.
- Contract tests run against fakes; live vendor tests are opt-in.
- An OpenAI Realtime adapter, if evaluated, implements a separate
  `RealtimeProvider` port because it replaces the whole pipeline.

## 5. Call flow (planned)

1. SIP INVITE arrives; the telephony edge accepts and opens a media stream.
2. A `CallSession` is created with a call ID, venue ID, and language profile.
3. Audio is resampled to the STT format and streamed to the STT adapter.
4. VAD detects speech end; partial and final transcripts are emitted.
5. The dialog manager updates state and asks the LLM for the next action.
6. Tool calls are validated against the reservation domain before execution.
7. The response is synthesized by TTS and streamed back.
8. Barge-in detection cancels playback and returns to listening.
9. On handoff, the call is transferred with a structured context payload.
10. On hangup, the call record, transcript, and outcome are persisted.

## 6. Dialog state machine (planned)

```text
GREETING → INTENT_DETECTION
              ├── RESERVATION → COLLECT_FIELDS → CONFIRM → BOOK → CLOSE
              ├── FAQ → ANSWER → (FOLLOW_UP | CLOSE)
              ├── HANDOFF → TRANSFER → CLOSE
              └── UNCLEAR → CLARIFY → (retry | HANDOFF)
```

Policies:

- Maximum two clarification attempts before handoff.
- Confirmation is mandatory before any write.
- Tool errors never produce a fabricated success message.
- Silence and no-input timeouts have explicit prompts and a final handoff.
- Every transition is logged with the call ID and reason.

## 7. Latency budget (proposed)

The 700 ms median TTFA target is a product target, not a measurement. A proposed
allocation for the component pipeline:

| Stage | Budget (median) |
| --- | --- |
| VAD / endpointing | 100–150 ms |
| STT finalization | 100–150 ms |
| LLM first token | 150–250 ms |
| TTS first audio | 100–150 ms |
| Network / jitter buffer | 50–100 ms |
| **Total** | **≤ 700 ms** |

Rules:

- Stream partials to the dialog layer where possible.
- Start TTS on the first complete phrase.
- Measure at the caller's audio boundary, not inside a vendor SDK.
- Report median and P95; keep failed and slow turns in the sample.
- The 300–400 ms stretch target applies only under ideal conditions and is
  reported separately.

## 8. Data model (planned)

Core entities:

| Entity | Purpose |
| --- | --- |
| `Venue` | Restaurant profile, timezone, hours, handoff number |
| `FaqEntry` | Approved question/answer pairs with versioning |
| `Reservation` | Date, time, party size, guest, phone, status, source |
| `Call` | Call ID, venue, timestamps, outcome, latency summary |
| `TranscriptTurn` | Redacted transcript segments with timing |
| `Handoff` | Reason, destination, context payload, result |
| `ProviderConfig` | Selected providers and fallback order per environment |

PostgreSQL is the system of record. Recordings, if enabled, live in object
storage with a retention policy; they are not stored in the repository.

## 9. Human handoff

- Transfer is a first-class state, not an exception.
- The context payload includes call ID, caller number, intent, collected fields,
  summary, and reason.
- If transfer fails, the assistant tells the caller and offers a callback.
- Handoff success and connect time are measured separately from conversation
  quality.

## 10. Observability

- Structured JSON logs with `call_id`, `venue_id`, `stage`, `duration_ms`, and
  outcome. No credentials or full phone numbers at INFO level.
- Metrics: calls started/completed, handoff rate, booking success, STT
  confidence, per-stage latency, provider errors.
- Traces span the call, each turn, and each provider request.
- Audit trail for every reservation write and configuration change.

## 11. Deployment (planned)

- Containerised FastAPI service.
- PostgreSQL managed instance.
- SIP/media gateway close to the target region.
- Secrets from a managed secret store, never from the image.
- Separate development, staging, and production environments.
- Health endpoints and graceful shutdown for in-flight calls.

Docker assets will live in `infrastructure/docker/`. Nothing is deployable yet.

## 12. Security and privacy

- TLS for all service-to-service traffic; SRTP for media where the trunk allows.
- Least-privilege database and cloud roles.
- Consent and retention rules defined before recording is enabled.
- PII minimisation in logs and transcripts.
- Vendor data-processing terms reviewed before sending call audio.

See [SECURITY.md](SECURITY.md).

## 13. Testing strategy

| Layer | Approach |
| --- | --- |
| Domain | Pure unit tests for reservations, dates, and state transitions |
| Providers | Contract tests against fakes; opt-in live smoke tests |
| Audio | Fixture-based tests with consented or synthetic audio |
| Conversation | Scripted scenario tests with deterministic LLM stubs |
| Latency | Harness measuring TTFA and barge-in on the real path |
| Integration | SIP and database tests in local containers |

Voice Lab experiments are defined in [`../voice_lab/README.md`](../voice_lab/README.md).

## 14. Key decisions

See [DECISIONS.md](DECISIONS.md). Notable:

- Hybrid provider architecture over a single end-to-end model.
- Modular monolith over microservices for the MVP.
- Azerbaijani-first rather than translation-based.
- Latency measured at the caller boundary.

## 15. Open architecture questions

1. Which SIP trunk provider supports Azerbaijan numbers and media quality?
2. Does the reservation system need a direct integration or an internal store?
3. Is streaming STT available in the required region for each vendor?
4. Where must call audio be processed and stored for compliance?
5. Is an end-to-end realtime model viable for Azerbaijani, and at what cost?
