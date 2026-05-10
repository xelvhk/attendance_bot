# Admin Backup Command Specification

## Goal

Provide a simple, safe admin command to create a restorable snapshot of attendance data.

## Command

- Name: `/backup`
- Access: admins only (chat/global admin policy already used by existing admin commands)
- Scope: current chat data by default

Optional argument:
- `/backup full` -> includes all chats (super-admin only, optional future extension)

## Output format

Backup artifact: ZIP archive with deterministic structure.

```text
backup/
  metadata.json
  attendance.db
  exports/
    records.csv
    stats_week.csv
    stats_month.csv
```

`metadata.json` fields:
- `backup_id`
- `created_at_utc`
- `created_by_user_id`
- `scope` (`chat` or `full`)
- `chat_id` (for chat scope)
- `schema_version`
- `record_counts`
- `checksum_sha256`

## Storage strategy

Default local path:
- `backups/YYYY/MM/attendance-backup-{backup_id}.zip`

Rules:
- Rotate old backups by retention policy (example: 30 days).
- Keep last N backups regardless of age (example: 10).
- Never overwrite existing artifact with same `backup_id`.

## Validation

After archive creation:
1. Verify ZIP integrity.
2. Verify checksum of embedded DB file.
3. Verify minimal restore test in memory/sandbox mode (optional in MVP but recommended).

## User-facing responses

Success:
- `Backup готов: <backup_id>. Файл сохранен и проверен.`

Failure:
- `Не удалось создать backup. Проверь права доступа и место на диске.`

## Security and privacy

- Backup command is admin-only.
- Do not include bot token or runtime secrets.
- Log only metadata and result status (no sensitive payloads).

## Restore path (MVP runbook)

Planned command:
- `/restore <backup_id>` (admin-only, explicit confirmation required)

MVP restore process:
1. Locate backup artifact by `backup_id`.
2. Validate archive and checksum.
3. Stop write operations (maintenance lock).
4. Replace DB snapshot.
5. Run post-restore sanity checks.
6. Unlock operations and return restore report.
