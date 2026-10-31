# Security and Privacy Policy

**Status:** Baseline policy for the project. Technical controls are planned until
the corresponding modules exist.
**Last updated:** 2026-11-01

> This document is not legal advice. Recording, retention, and cross-border data
> transfer rules must be reviewed by qualified counsel before the pilot.

## 1. Principles

- Collect the minimum data needed to answer a call and manage a reservation.
- Never commit secrets. Configuration comes from the environment or a secret
  manager.
- Treat caller audio, transcripts, names, and phone numbers as personal data.
- Make human handoff and data deletion possible by design.
- Prefer vendors with clear data-processing terms, regional processing options,
  and no training on customer data.
- Security review is a release gate, not a post-launch task.

## 2. Secrets management

| Rule | Detail |
| --- | --- |
| Never commit | API keys, tokens, passwords, private keys, connection strings |
| Local development | `.env` file, ignored by Git; `.env.example` holds placeholders |
| CI/CD | Provider secret store with masked variables |
| Production | Managed secret manager; no secrets in images or repositories |
| Rotation | Rotate on exposure and on a scheduled basis |
| Scanning | Run a secret scan before every push and in CI |

If a secret is exposed:

1. Revoke or rotate it immediately.
2. Remove it from the working tree and history if necessary.
3. Assess access logs for misuse.
4. Record the incident and the remediation.

## 3. Data classification

| Class | Examples | Handling |
| --- | --- | --- |
| Restricted | Vendor API keys, database credentials | Secret manager only; never logged |
| Confidential | Call recordings, transcripts, phone numbers, guest names | Encrypted at rest and in transit; restricted access |
| Internal | Venue configuration, FAQ drafts, metrics | Authenticated staff only |
| Public | Marketing copy, published menu content | No restrictions |

## 4. Call recording and consent

Recording is **not enabled** and must not be enabled until all of the following
are complete:

- Legal review of Azerbaijani recording and consent requirements.
- A consent script and caller notification approved for use.
- A documented retention period and deletion process.
- Vendor data-processing agreements covering audio and transcripts.
- Access controls and audit logging for recordings.

Planned defaults (proposed, pending legal review):

- Announce recording at the start of the call where required.
- Store recordings in encrypted object storage, not in the repository.
- Retain raw audio for the minimum period needed for quality review.
- Retain transcripts no longer than necessary for audit and improvement.
- Allow deletion on request where legally applicable.

## 5. Privacy requirements

- **Purpose limitation:** caller data is used only to handle the call, manage
  reservations, and improve quality under an approved policy.
- **Minimisation:** do not collect email, address, or payment data for a
  reservation unless the venue requires it.
- **Redaction:** mask phone numbers and names in logs and dashboards where full
  values are not needed.
- **Access:** role-based access; least privilege; no shared accounts.
- **Retention:** defined per data type before the pilot; enforced by scheduled
  deletion.
- **Vendor transfer:** document which vendor receives audio, text, or metadata,
  and where it is processed.
- **Model training:** do not allow vendors to train on customer data; verify
  contractual terms.

## 6. Application security (planned)

- Validate and bound all input: audio duration and size, phone format, party
  size, dates, and tool-call arguments.
- Authenticate dashboard and API access; authorise per venue.
- Use parameterised database queries only.
- Apply rate limits and abuse protection to public endpoints.
- Verify SIP signalling where the trunk supports it.
- Keep dependencies minimal and reviewed; enable automated vulnerability alerts.
- Run containers as non-root with read-only filesystems where possible.
- Use TLS for service traffic and SRTP for media where available.
- Do not expose internal provider credentials to the browser.

## 7. Logging and monitoring

- Log structured events, not raw audio or full transcripts, at INFO level.
- Include `call_id` for traceability; exclude credentials and full phone numbers.
- Restrict log access to the engineering team.
- Alert on authentication failures, unusual call volume, provider errors, and
  secret-scanning hits.
- Keep an audit trail for reservation writes and configuration changes.

## 8. Incident response

1. **Detect** — alert, report, or vendor notification.
2. **Contain** — revoke credentials, disable the affected path, isolate data.
3. **Assess** — scope, affected callers, legal notification obligations.
4. **Remediate** — fix the cause, rotate secrets, restore service.
5. **Record** — incident notes, timeline, and follow-up actions.
6. **Review** — blameless post-incident review within five working days.

Report suspected vulnerabilities privately to the maintainers. Do not publish
exploit details or caller data in a public issue.

## 9. Secure development

- Security impact is part of every pull request review.
- New dependencies require a reason and a licence/security check.
- Tests must not use production credentials or real caller data.
- Audio fixtures must be consented, licensed, or synthetic.
- CI runs linting, tests, and secret scanning.
- Production access requires explicit approval and is logged.

## 10. Open items

- Legal review of recording consent and retention.
- Vendor data-processing and residency review.
- Choice of secret manager.
- Authentication design for the venue dashboard.
- Data deletion workflow and verification.
- Incident contact list and escalation path.
