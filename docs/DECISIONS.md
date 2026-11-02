# Decision Log

Architecture and product decisions for AZ VOICE OPERATOR.
Format: context → decision → status → consequences.

**Status values:** Proposed · Accepted · Superseded · Rejected

| ID | Title | Status | Date |
| --- | --- | --- | --- |
| D-001 | Target market and product focus | Accepted | 2026-11-01 |
| D-002 | Hybrid voice AI architecture | Accepted | 2026-11-01 |
| D-003 | MVP scope: reservations and FAQ | Accepted | 2026-11-01 |
| D-004 | Technology stack | Accepted | 2026-11-01 |
| D-005 | Azerbaijani-first language strategy | Accepted | 2026-11-01 |
| D-006 | Latency targets | Accepted (as targets) | 2026-11-01 |
| D-007 | Modular monolith | Accepted | 2026-11-01 |
| D-008 | Provider selection deferred to Voice Lab | Accepted | 2026-11-01 |
| D-009 | Notion as project-management workspace | Accepted | 2026-11-01 |
| D-010 | Repository and commit conventions | Accepted | 2026-11-01 |
| D-011 | Azerbaijani evaluation preserves orthography | Accepted | 2026-11-01 |

---

## D-001 — Target market and product focus

**Context:** The initial product needs a narrow, testable market before expanding.

**Decision:** Build for restaurants in Azerbaijan, starting with Baku. Offer the
product as SaaS. The product is an Azerbaijani restaurant voice AI operator.

**Status:** Accepted.

**Consequences:**

- Discovery targets Baku restaurant owners and front-of-house staff.
- Azerbaijani language quality is a launch blocker, not a later enhancement.
- Pricing must be validated with local venues.
- Expansion to other verticals or countries is deferred.

## D-002 — Hybrid voice AI architecture

**Context:** End-to-end realtime models are attractive for latency but may not
support Azerbaijani well. Component pipelines offer control and provider choice.

**Decision:** Use a hybrid architecture with separate STT, dialog/LLM, and TTS
layers behind interfaces. Evaluate OpenAI Realtime as an alternative, not as the
default.

**Status:** Accepted.

**Consequences:**

- Every layer can be benchmarked and replaced independently.
- The system needs explicit latency budgets and orchestration.
- Adapter maintenance cost is accepted in exchange for flexibility.
- Final provider selection depends on Voice Lab evidence.

## D-003 — MVP scope: reservations and FAQ

**Context:** Restaurants have many possible automation needs; the first release
must be small enough to validate.

**Decision:** The MVP handles inbound reservation create/change/cancel and
approved FAQ, plus human handoff. Everything else is out of scope.

**Status:** Accepted.

**Consequences:**

- No payments, delivery, outbound calls, or complaint automation in the MVP.
- Reservation accuracy and FAQ correctness are the primary quality metrics.
- Scope changes require an update to this log and the PRD.

## D-004 — Technology stack

**Context:** The team needs a pragmatic stack that supports streaming audio, a
web dashboard, and relational data.

**Decision:**

- Python 3.11+ with FastAPI for the backend.
- PostgreSQL for persistence.
- Next.js for the venue dashboard.
- SIP trunk for telephony.
- Python tooling: pytest and Ruff.

**Status:** Accepted.

**Consequences:**

- The repository is a Python project with a future web app.
- Runtime dependencies are added only when their module is implemented.
- The SIP provider and hosting region remain open decisions.

## D-005 — Azerbaijani-first language strategy

**Context:** Translating an English-first assistant produces unnatural phrasing
and poor recognition of local names.

**Decision:** Design prompts, confirmations, error messages, and evaluation in
Azerbaijani first. Preserve Azerbaijani Latin characters exactly. Treat Russian
and English as optional fallbacks only if pilot evidence requires them.

**Status:** Accepted.

**Consequences:**

- Azerbaijani copy review is part of the definition of done for user-facing
  changes.
- Test corpora and FAQ content must be native Azerbaijani, not translated.
- Vendor language coverage must be verified before integration.
- Mixed-language behaviour is an explicit test case.

## D-006 — Latency targets

**Context:** Conversational delay is the main quality risk in voice AI.

**Decision:** Adopt product targets of median TTFA ≤ 700 ms, P95 ≤ 1,200 ms,
and a stretch median of 300–400 ms under ideal conditions. Measure at the
caller's audio boundary on the real SIP path.

**Status:** Accepted as targets. **Not measured.**

**Consequences:**

- Every stage must emit timing data.
- Reports include median and P95, never only best-case runs.
- Provider choices are evaluated against these targets.
- Missing the targets blocks the pilot gate unless explicitly waived.

## D-007 — Modular monolith

**Context:** The MVP is small, the team is small, and operational complexity
should stay low.

**Decision:** Build one deployable Python service with strict internal module
boundaries. Do not adopt microservices before the pilot demonstrates a need.

**Status:** Accepted.

**Consequences:**

- One deployment, one database, simpler debugging.
- Module boundaries are enforced by interfaces and review, not network calls.
- A future split is possible because providers and domain logic are isolated.

## D-008 — Provider selection deferred to Voice Lab

**Context:** Vendor claims about Azerbaijani support are not sufficient evidence.

**Decision:** Do not select STT, TTS, LLM, or realtime providers until the Voice
Lab completes its availability gate and benchmarks.

**Status:** Accepted.

**Consequences:**

- No vendor SDK is a hard dependency in the scaffold.
- The architecture must remain provider-agnostic.
- The pilot cannot start before a provider decision is recorded.

## D-009 — Notion as project-management workspace

**Context:** Tasks, discovery assets, and decisions need a shared workspace
outside the code repository.

**Decision:** Use the Notion AZ VOICE OPERATOR workspace for tasks, discovery
trackers, pilot metrics, and the roadmap. The repository holds engineering
documentation and code. Do not duplicate trackers in both places.

**Status:** Accepted.

**Consequences:**

- Task status is managed in Notion.
- Repository docs link to Notion instead of copying operational records.
- Decisions with architectural impact are still recorded here.

## D-010 — Repository and commit conventions

**Context:** The repository starts empty and needs consistent contributor rules.

**Decision:** Use `main` as the default branch, short-lived branches, and
Conventional Commits. Keep secrets out of Git. Do not push until the local
commit is verified. Use `AGENTS.md` as the contributor contract.

**Status:** Accepted.

**Consequences:**

- The initial commit is `chore: initialize AZ Voice Operator project`.
- The remote configuration is preserved as cloned.
- Generated audio, datasets, and environment files are ignored.

## D-011 — Azerbaijani evaluation preserves orthography

**Context:** STT scoring can hide Azerbaijani errors if diacritics are stripped or
letters are ASCII-folded. Reporting only one metric, or producing numbers from
unverified audio, makes vendor comparisons misleading and irreproducible.

**Decision:** Preserve `ə`, `ı`, `ö`, `ü`, `ğ`, `ş`, `ç` and their uppercase
forms in all evaluation. Never transliterate to English equivalents or use
compatibility normalization. Make normalization configurable and record it.
Report both WER and CER. Score names, dates, times, and numbers independently.
Retain original and normalized transcripts. Record dataset, audio, and config
hashes plus a code version. Refuse to produce a report when required audio is
missing or empty.

**Status:** Accepted.

**Consequences:**

- Evaluation code lives in `voice_lab/evaluation/` and is separate from the
  product runtime.
- Entity evaluation requires annotations; automatic extraction is not treated as
  ground truth.
- CER is reported, but no CER threshold is approved until real audio evidence
  exists.
- Synthetic fixtures may test code behaviour but can never support a benchmark
  claim.
- Reports with different normalization settings are not directly comparable
  unless the configuration difference is stated.

---

## Adding a decision

1. Copy the structure above and assign the next ID.
2. State the context and the forces at play.
3. Record the decision in one or two sentences.
4. Set a status and date.
5. List the consequences, including what becomes harder.
6. If superseding an earlier decision, update its status and link the new one.
7. Update affected documents (`PRD.md`, `ARCHITECTURE.md`, `ROADMAP.md`).
