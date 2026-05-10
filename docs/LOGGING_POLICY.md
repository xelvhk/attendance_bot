# Logging Policy

## Goals

- Keep logs useful for debugging and operations.
- Avoid leaking secrets and personal data.
- Make incidents traceable across request boundaries.

## Log format

- Use structured logs (JSON-like key/value fields).
- Required base fields:
  - `timestamp`
  - `level`
  - `service`
  - `event`
  - `request_id` (when request-scoped)
  - `user_id` (masked/anonymized form if needed)

## Severity guidelines

- `DEBUG`: local troubleshooting details, disabled in production by default.
- `INFO`: expected state transitions and successful business actions.
- `WARNING`: recoverable anomalies, retries, degraded behavior.
- `ERROR`: failed operations requiring attention.
- `CRITICAL`: outage-level failures.

## Sensitive data rules

- Never log tokens, passwords, session secrets, or raw auth headers.
- Never log full personal payloads when a summary is enough.
- Redact or mask:
  - access tokens
  - phone/email if not needed for diagnosis
  - external provider credentials

## Event naming

- Prefer stable event ids, e.g.:
  - `task_created`
  - `task_completed`
  - `timezone_parse_failed`
  - `status_transition_invalid`
  - `sync_provider_error`

## Correlation and tracing

- Generate/pass `request_id` through all request handling layers.
- Propagate correlation id into integration calls where possible.
- Include integration target in logs (`provider`, `endpoint_alias`).

## Retention and rotation

- Keep local logs with rotation.
- Recommended baseline:
  - size-based rotation for active files
  - retention window: 14-30 days for operational logs

## Operational guardrails

- Production default log level: `INFO`.
- Enable `DEBUG` temporarily and explicitly for incident windows.
- Add log sampling for high-volume repetitive events if needed.

## Review checklist

- Do logs include enough context to reproduce failures?
- Are secrets and PII fully redacted?
- Are event names stable and searchable?
- Is `request_id` present in all request-scoped error logs?
