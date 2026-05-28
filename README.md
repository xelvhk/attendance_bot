# attendance_bot

Telegram attendance bot for tracking work hours, statuses, and CSV export

Language: **English** | [Русский](README.ru.md)

## Problem
- This project solves a practical development or automation task.
- The goal is to provide a clear implementation that is easy to run and extend.

## Stack
- Primary language: Python
- Project-specific libraries and tools (see source files)

## Setup
```bash
git clone https://github.com/xelvhk/attendance_bot
cd attendance_bot
# install dependencies (if present)
# copy .env.example to .env (if present)
# run the project
```

## Architecture
- Entry points: application scripts and main modules in the repository root.
- Core logic: domain-specific modules grouped by responsibility.
- Data layer: local files/database/adapters depending on project scope.

## Demo
- Add screenshots/GIF or usage examples for key flows.
- If deployed, add production URL.

## Group support
- The bot keeps attendance per chat, so personal and group data are separated.
- Add the bot to a group and run `/setup_chat`.
- Until `/setup_chat` is executed, group attendance commands stay disabled.
- Useful group commands: `/in`, `/out`, `/mk`, `/uvc`, `/uvs 6`, `/short_day 7`, `/vacation`, `/personal_day`
- Statistics commands: `/week`, `/month`, `/balance`, `/all_stats`, `/manual 2024-12-31 09:00:00-18:00:00`
- Admin commands: `/chat_info`, `/chat_admins`, `/add_admin` in reply or `/add_admin <user_id>`, `/remove_admin` in reply or `/remove_admin <user_id>`, `/disable_chat`

## QA / Edge Cases
- Timezone and status transition checklist: [`docs/TIMEZONE_STATUS_EDGE_CASES.md`](./docs/TIMEZONE_STATUS_EDGE_CASES.md)

## Roadmap
- [x] Export monthly/all records to CSV (via `Экспорт CSV` button)
- [x] Add per-user timezone setting (`/tz +3`, `/tz UTC+03:00`)
- [x] Add simple admin command for data backup (spec: `docs/ADMIN_BACKUP_COMMAND_SPEC.md`)
- [x] Add unit tests for `services/stats_service.py`

## Status
Active development

## License
GNU AGPLv3. See [LICENSE](LICENSE).
