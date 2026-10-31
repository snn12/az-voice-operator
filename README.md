# AZ VOICE OPERATOR

Azerbaijani-first voice AI operator for restaurants. It answers the phone,
takes reservations, handles approved FAQ, and hands the call to a human when it
should.

> **Status: Phase 0 — Product Discovery.**
> The voice engine is not implemented. This repository contains the project
> scaffold, architecture, and documentation only. No benchmark, latency, or
> pilot result has been produced yet.

## Goals

- Answer restaurant calls in natural Azerbaijani, 24/7.
- Create, change, and cancel reservations accurately.
- Answer approved questions about hours, address, menu, allergens, and parking.
- Escalate to staff on low confidence, complaints, or an explicit request.
- Keep latency low enough for natural conversation.
- Stay provider-agnostic so STT, LLM, and TTS can be compared and replaced.

## MVP scope

| In scope | Out of scope (for the MVP) |
| --- | --- |
| Inbound phone calls | Outbound marketing calls |
| Reservation create / change / cancel | Payments and deposits |
| FAQ from an approved knowledge base | Order-taking and delivery |
| Human handoff with context | Multi-venue analytics |
| Azerbaijani as primary language | Fully automated complaint handling |

## Current phase

**Phase 0 — Product Discovery.** In progress:

- Restaurant owner interviews in Baku (15-question guide, 10 target venues).
- Workflow, reservation, FAQ, and pricing discovery.
- Pilot success criteria definition.
- Voice Lab experiment plan and evaluation foundation (normalization, WER/CER,
  entity scoring). No benchmark has been run.

All of these are tracked in the project's Notion workspace. No interviews have
been completed and no results are reported in this repository.

Next: **Phase 1 — Azerbaijani Voice Lab**, comparing Google Chirp 3, Azure
Speech STT, Azure Banu/Babek TTS, and OpenAI Realtime.

## Architecture at a glance

```text
Caller
  │  PSTN / SIP trunk
  ▼
Telephony edge  ──►  Audio pipeline (streaming, VAD, barge-in)
                          │
                          ▼
                    Conversation core
                    ├── STT provider port   (Google Chirp 3 | Azure Speech)
                    ├── Dialog + LLM port   (low-latency LLM API)
                    ├── Restaurant tools    (reservations, FAQ)
                    └── TTS provider port   (Azure Banu | Babek)
                          │
                          ▼
                    Monitoring & call audit
```

Key principles:

- **Modular monolith** with ports and adapters.
- **Hybrid providers**: STT, LLM, and TTS are independently replaceable.
- **Azerbaijani-first**: prompts, confirmation phrases, and evaluation are built
  for Azerbaijani before any other language.
- **Human handoff** is a first-class outcome, not an error path.

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for detail.

## Technology stack

| Layer | Choice | Status |
| --- | --- | --- |
| Language | Python 3.11+ | Planned |
| API | FastAPI | Planned |
| Database | PostgreSQL | Planned |
| Web dashboard | Next.js | Planned |
| Telephony | SIP trunk | Planned |
| STT | Google Chirp 3 / Azure Speech | Under evaluation |
| LLM | Low-latency LLM API (provider TBD) | Under evaluation |
| TTS | Azure Speech (Banu / Babek) | Under evaluation |
| End-to-end alternative | OpenAI Realtime | Under evaluation |

No provider has been selected. Vendor Azerbaijani coverage must be verified
before benchmarking.

## Repository layout

```text
.
├── AGENTS.md              contributor and agent rules
├── README.md
├── .env.example           environment template (placeholders only)
├── pyproject.toml         minimal Python project + dev tooling
├── docs/                  PRD, architecture, roadmap, security, decisions
├── voice_lab/             offline STT/TTS/latency benchmarks and evaluation
├── src/az_voice_operator/ application package
├── tests/                 unit, integration, voice tests
├── scripts/               developer and operations scripts
└── infrastructure/docker/ container assets
```

## Setup

Requirements: Python 3.11 or newer, Git, and (later) Docker for local services.

```bash
git clone https://github.com/snn12/az-voice-operator.git
cd az-voice-operator

python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -e ".[dev]"
cp .env.example .env
```

Nothing is installed automatically. `pip install -e ".[dev]"` is a manual step
and currently installs only pytest and Ruff; runtime dependencies are added
when the corresponding modules are implemented.

Run the checks:

```bash
ruff check .
ruff format --check .
pytest
```

There is no runnable voice service yet, so there is no start command.

## Configuration

Configuration is read from environment variables. `.env.example` documents the
expected names with placeholders. Real credentials must never be committed.

## Documentation

- [Product requirements](docs/PRD.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Roadmap](docs/ROADMAP.md)
- [Security](docs/SECURITY.md)
- [Decisions](docs/DECISIONS.md)
- [Voice Lab](voice_lab/README.md)

## Contributing

Read [`AGENTS.md`](AGENTS.md) before making changes. All features that are not
implemented and tested must be labelled **planned** or **proposed**. Never
present targets as measured results.

## License

Proprietary. All rights reserved. No license is granted for redistribution.
