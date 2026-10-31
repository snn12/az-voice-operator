# Roadmap

**Status:** Phase 0 in progress. All later phases are planned.
**Last updated:** 2026-11-01

> Dates are intentionally omitted until discovery and vendor evaluation produce
> evidence. No milestone below is complete unless explicitly marked.
> Execution detail lives in the Notion project workspace; this file records the
> repository-level plan and exit criteria.

## Phase overview

| Phase | Name | Status | Primary outcome |
| --- | --- | --- | --- |
| 0 | Product Discovery | **In progress** | Validated problem, pricing signal, pilot venues |
| 1 | Azerbaijani Voice Lab | Planned | Evidence-based STT/TTS/LLM selection |
| 2 | MVP Build | Planned | Working reservation + FAQ voice agent |
| 3 | Restaurant Pilot | Planned | Real calls, measured success gates |
| 4 | Launch and Scale | Planned | Commercial availability in Baku |

## Phase 0 — Product Discovery

**Objective:** Confirm the problem, workflow, and willingness to pay before
building.

Deliverables:

- 15-question restaurant interview guide.
- Interview tracker for 10 Baku venues.
- Completed interviews and synthesized findings.
- Pilot success metrics with signed-off targets.
- Voice Lab experiment plan.
- Legal and data-protection review for call recording.
- Updated PRD assumptions and open questions.

Exit criteria:

- At least 10 target venues identified and contacted.
- Enough interviews completed to identify recurring workflow and pricing
  patterns. The exact sample will be recorded when known.
- At least 2 venues willing to discuss a pilot.
- Success metrics approved.
- Recording and retention approach reviewed.

Current status: guide, tracker, metrics, and experiment plan exist; interviews
have **not** been completed and no findings are reported.

## Phase 1 — Azerbaijani Voice Lab

**Objective:** Select providers using measured evidence.

Deliverables:

- Availability and compliance matrix for each vendor.
- Consented Azerbaijani test corpus with transcripts.
- STT benchmark: WER, entity accuracy, latency.
- TTS listening test: naturalness and domain pronunciation.
- End-to-end comparison including OpenAI Realtime.
- Cost and operability review.
- Architecture decision memo.

Exit criteria:

- Azerbaijani support confirmed for every selected layer.
- STT entity accuracy meets the agreed threshold on the hold-out set.
- TTS quality meets the agreed naturalness threshold.
- End-to-end median TTFA and P95 measured on a realistic path.
- Chosen stack recorded in `docs/DECISIONS.md`.

Current status: **not started**. No vendor has been tested.

## Phase 2 — MVP Build

**Objective:** Build the reservation and FAQ voice agent.

Deliverables:

- SIP inbound call handling.
- Streaming STT → dialog → TTS pipeline.
- Reservation create/change/cancel with validation.
- Approved FAQ knowledge base.
- Human handoff with context.
- Call records, transcripts, and audit.
- Venue configuration and basic dashboard.
- Deployment to a staging environment.

Exit criteria:

- All P0 user stories implemented and tested.
- Internal call tests pass on the real telephony path.
- Security review complete; no open critical findings.
- Operational runbook and rollback plan exist.

Current status: **not started**. Only the repository scaffold exists.

## Phase 3 — Restaurant Pilot

**Objective:** Validate quality and value with real venues and real callers.

Deliverables:

- Pilot agreement and consent flow.
- Live calls during and outside service hours.
- Weekly quality review against pilot metrics.
- Incident and handoff review.
- Owner feedback and pricing validation.

Exit criteria (proposed, pending sign-off):

- Median TTFA ≤ 700 ms; P95 ≤ 1,200 ms.
- Reservation exact match ≥ 95%; zero lost or duplicate bookings.
- FAQ accuracy ≥ 95%; zero critical factual errors in the sample.
- Explicit human requests honored 100%; correct escalation ≥ 95%.
- Caller CSAT ≥ 4.0 / 5.
- No unresolved critical defect or compliance issue.

Current status: **not started**.

## Phase 4 — Launch and Scale

**Objective:** Turn a successful pilot into a repeatable SaaS product.

Deliverables:

- Self-service or assisted onboarding.
- Billing and subscription management.
- Multi-venue support and analytics.
- Reliability targets and on-call process.
- Sales materials grounded in pilot evidence.

Exit criteria:

- Documented onboarding playbook.
- Support and incident processes operating.
- Unit economics validated.
- At least one paying customer beyond the pilot.

Current status: **not started**.

## Cross-cutting workstreams

| Workstream | Phase | Status |
| --- | --- | --- |
| Security and privacy | 0 → 4 | Policy drafted; implementation planned |
| Observability | 2 → 4 | Planned |
| Documentation | 0 → 4 | Repository docs started |
| Legal and compliance | 0 → 3 | Review not started |
| Pricing | 0 → 3 | Hypothesis only |

## Explicit non-goals for the near term

- Outbound calling.
- Payments and deposits.
- Order-taking and delivery.
- Multi-country expansion.
- Microservice split.
- Custom model training before vendor evaluation.

## Related documents

- [PRD](PRD.md)
- [Architecture](ARCHITECTURE.md)
- [Decisions](DECISIONS.md)
- [Pilot Success Metrics (Notion)](https://app.notion.com/p/40a541b17b3f81418385d6c6b6ae7848)
- [Voice Lab Preparation (Notion)](https://app.notion.com/p/40a541b17b3f81929c43cd6db2234847)
