# Product Requirements Document (PRD)

**Product:** AZ VOICE OPERATOR
**Market:** Azerbaijan
**Model:** SaaS
**Document status:** Living draft — Phase 0 (Product Discovery)
**Last updated:** 2026-11-01

> Nothing in this document is a measured result. Features are marked
> **Planned**, **Proposed**, or **Implemented**. Only items explicitly marked
> *Implemented* exist, and currently none of the voice features do.

## 1. Problem

Restaurant staff in Baku answer the phone while serving guests. Calls arrive
during peak service, often in Azerbaijani with mixed Russian or English, and
cover both reservations and repetitive questions. Missed or misunderstood calls
cost bookings and interrupt service.

The hypothesis to validate in Phase 0:

- Owners lose reservations when calls are missed during busy periods.
- Staff time is consumed by repetitive FAQ calls.
- Existing IVR and reservation tools do not handle natural Azerbaijani speech.
- Owners will pay for a service that reliably reduces missed bookings.

These are hypotheses, not findings. Phase 0 interviews must confirm or reject
them.

## 2. Target users

| User | Need |
| --- | --- |
| Restaurant owner / manager | Fewer missed bookings, less phone disruption, clear ROI |
| Host / front-of-house staff | Accurate reservation records, less repetitive work |
| Caller (guest) | Fast answer in Azerbaijani, correct booking, easy human escalation |
| Operations (internal) | Visibility into call quality, failures, and cost |

## 3. Product goals

1. Answer inbound calls in natural Azerbaijani at any hour.
2. Create, modify, and cancel reservations accurately.
3. Answer approved FAQ using venue-supplied content.
4. Escalate to a human when confidence is low or the caller asks.
5. Keep conversational latency low enough to feel natural.
6. Give the venue an auditable record of every call and booking.

## 4. MVP scope

### In scope

- Inbound calls to a venue's dedicated number.
- Reservation create, change, and cancel.
- FAQ: hours, address, location/parking, menu categories, allergens, price
  range, large groups, and venue-specific policies supplied by the owner.
- Azerbaijani as the primary language.
- Human handoff to a configured number.
- Call summary and reservation record for the venue.
- Basic operational dashboard and call audit (planned).

### Out of scope for the MVP

- Outbound campaigns or confirmations.
- Payments, deposits, and refunds.
- Food ordering and delivery.
- Loyalty programs and marketing.
- Multi-location analytics and franchise management.
- Fully automated complaint resolution.
- Languages other than Azerbaijani, unless pilot evidence requires them.

## 5. Core user stories

| ID | As a… | I want… | Priority |
| --- | --- | --- | --- |
| US-01 | Caller | to book a table by phone in Azerbaijani | P0 |
| US-02 | Caller | to change or cancel my booking | P0 |
| US-03 | Caller | to ask about hours, address, and menu | P0 |
| US-04 | Caller | to reach a person when I ask | P0 |
| US-05 | Owner | to see every reservation the assistant made | P0 |
| US-06 | Owner | to control which answers are approved | P0 |
| US-07 | Owner | to be alerted when the assistant fails | P1 |
| US-08 | Staff | to receive context when a call is transferred | P0 |

## 6. Conversation requirements

### 6.1 Reservation flow (planned)

1. Greet the caller in Azerbaijani and identify the venue.
2. Detect intent: reservation, FAQ, handoff, or unclear.
3. Collect date, time, party size, name, and phone number.
4. Read back critical fields and confirm.
5. Check availability through the reservation tool.
6. Create the booking and give a confirmation reference.
7. If any step is ambiguous or fails, offer handoff.

Rules:

- Never invent availability or confirm a booking that was not persisted.
- Always read back date, time, party size, and phone number.
- Treat relative dates ("sabah", "cümə axşamı") carefully and resolve them
  against the venue's local timezone (`Asia/Baku`).
- Support correction loops ("yox, saat yeddidə").
- Keep turns short and avoid repeating the full script.

### 6.2 FAQ flow (planned)

- Answers come only from venue-approved content.
- If the answer is missing or uncertain, say so and offer a human.
- Never guess prices, allergens, or availability.
- Allergen answers must include a clear disclaimer and a handoff option.

### 6.3 Human handoff (planned)

Triggers:

- Caller explicitly asks for a person.
- Low STT or intent confidence after one clarification attempt.
- Complaint, refund, or legal topic.
- Large group or event beyond configured limits.
- Tool failure or booking system unavailable.
- Caller distress or repeated misunderstanding.

Handoff must pass: call ID, caller number, intent, collected fields, transcript
summary, and reason for transfer.

## 7. Functional requirements

| ID | Requirement | Status |
| --- | --- | --- |
| FR-01 | Accept inbound SIP calls and stream audio bidirectionally | Planned |
| FR-02 | Transcribe Azerbaijani speech with domain vocabulary | Planned |
| FR-03 | Detect end of speech and support barge-in | Planned |
| FR-04 | Maintain dialog state across turns | Planned |
| FR-05 | Execute reservation tool calls with validation | Planned |
| FR-06 | Answer from an approved FAQ knowledge base | Planned |
| FR-07 | Transfer calls with structured context | Planned |
| FR-08 | Persist call records, transcripts, and reservations | Planned |
| FR-09 | Expose venue configuration and FAQ management | Planned |
| FR-10 | Emit per-stage latency and quality metrics | Planned |

## 8. Non-functional requirements

### Latency targets (proposed, not measured)

| Metric | Target |
| --- | --- |
| Median time to first audio (TTFA) | ≤ 700 ms |
| P95 TTFA | ≤ 1,200 ms |
| Stretch median TTFA | 300–400 ms under ideal conditions |
| Barge-in stop time | ≤ 300 ms |
| Handoff connect time | ≤ 10 s |

These are product targets. They must be validated on the real SIP path during
the Voice Lab and pilot.

### Other requirements

- **Availability:** 99.5% monthly target for the pilot (proposed).
- **Concurrency:** design for 10 concurrent calls per venue initially; validate
  before scale-up.
- **Language:** Azerbaijani first, Latin alphabet preserved end to end.
- **Privacy:** recordings and transcripts handled per `docs/SECURITY.md`.
- **Auditability:** every booking traceable to a call ID and tool invocation.
- **Cost:** target cost per call minute set after vendor quotes; not yet defined.

## 9. Pricing hypothesis (to validate)

Proposed models to test in interviews:

1. Fixed monthly subscription per venue.
2. Per-minute usage.
3. Per-successful-reservation fee.
4. Setup fee plus monthly subscription.
5. Tiered subscription by call volume.

No price has been approved. Pricing must come from discovery evidence, not
assumption.

## 10. Success criteria

Pilot gates are defined in the Notion *Pilot Success Metrics* page and summarized
in `docs/ROADMAP.md`. All thresholds are **proposed** and require sign-off before
the pilot. No results exist yet.

Headline gates:

- Azerbaijani domain WER ≤ 15%.
- Reservation exact-match accuracy ≥ 95%, zero lost or duplicate bookings.
- FAQ answer accuracy ≥ 95%, zero critical factual errors in the sample.
- Median TTFA ≤ 700 ms, P95 ≤ 1,200 ms.
- Explicit human requests honored 100%; correct escalation ≥ 95%.
- Caller CSAT ≥ 4.0 / 5.

STT evaluation must report CER alongside WER, and entity accuracy must be broken
out for names, dates, times, and numbers. No CER threshold has been approved yet;
CER results must be reported, not used to replace WER.

## 11. Assumptions

- Restaurants use phone reservations as a meaningful booking channel.
- Owners can supply approved FAQ content and availability rules.
- A SIP trunk can be provisioned with a number acceptable to pilot venues.
- At least one vendor supports Azerbaijani well enough for production use; this
  is unverified.
- Venues can provide a human handoff destination during operating hours.

## 12. Open questions

1. Which reservation systems do target venues already use, and can they expose
   an API?
2. What is the acceptable price range and buying process?
3. Is call recording permitted under the venue contract and Azerbaijani law?
4. How do venues handle no-shows and deposits today?
5. Which languages do callers actually mix, and how often?
6. What is the minimum viable dashboard for an owner?
7. Which vendor supports Azerbaijani STT/TTS at production quality and in which
   region?
8. What happens outside opening hours — answer, take a message, or transfer?

## 13. Dependencies and risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Vendor Azerbaijani quality is insufficient | Product cannot launch | Voice Lab gate before build commitment |
| Telephony integration is harder than expected | Delays | Validate SIP path early in Phase 1–2 |
| Restaurant data is incomplete | Wrong FAQ answers | Owner-approved content workflow |
| Latency targets are missed | Poor conversation quality | Per-stage budgets and provider comparison |
| Privacy or recording rules are unclear | Legal exposure | Legal review before recording |
| Low willingness to pay | No viable business | Discovery pricing validation |

## 14. Release criteria for the MVP

- All P0 user stories implemented and tested.
- Pilot success gates met or explicitly waived with a recorded decision.
- Security review completed; no open critical findings.
- Handoff verified with real staff at pilot venues.
- Rollback and support runbook documented.

## 15. Related documents

- [Architecture](ARCHITECTURE.md)
- [Roadmap](ROADMAP.md)
- [Security](SECURITY.md)
- [Decisions](DECISIONS.md)
- Notion project workspace: AZ VOICE OPERATOR
