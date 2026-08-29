# attendance_bot

Telegram bot for recording work attendance, calculating time balances, and exporting attendance history to CSV. Data is stored in SQLite and isolated by Telegram chat, so the same bot can serve private chats and configured groups.

Language: **English** | [Русский](README.ru.md)

![Start screen](docs/screenshots/start.svg)

## Features

- Clock-in and clock-out records, sick leave, vacation, personal days, and shortened days.
- Weekly, monthly, balance, and full-history statistics.
- CSV export from the bot interface.
- Per-user UTC offset with `/tz`.
- Separate attendance data and administrators for each group chat.
- Group activation and administration with `/setup_chat`, `/add_admin`, `/remove_admin`, and `/disable_chat`.
- SQLite persistence and long-polling operation without a public HTTP endpoint.

## Stack

- Python 3.11
- aiogram 3
- SQLite
- environs
- `unittest` and GitHub Actions

## Quick start

```bash
git clone https://github.com/xelvhk/attendance_bot.git
cd attendance_bot
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python main.py
```

Configure `.env` before starting the bot:

```env
BOT_TOKEN=your_telegram_bot_token
ADMIN_IDS=123456789,987654321
DB_PATH=attendance.db
```

- `BOT_TOKEN` is required.
- `ADMIN_IDS` is an optional comma-separated list of global bot administrators.
- `DB_PATH` defaults to `attendance.db`.

## Group setup

Add the bot to a group and run `/setup_chat` as a Telegram group administrator. Until setup is complete, attendance commands stay disabled for that group.

Useful commands:

- Attendance: `/in`, `/out`, `/mk`, `/uvc`, `/uvs 6`, `/short_day 7`, `/vacation`, `/personal_day`.
- Statistics: `/week`, `/month`, `/balance`, `/all_stats`, `/manual 2024-12-31 09:00:00-18:00:00`.
- Administration: `/chat_info`, `/chat_admins`, `/add_admin`, `/remove_admin`, `/disable_chat`.

## Deploy to Amvera

The included [`amvera.yml`](amvera.yml) starts `main.py` and mounts persistent storage at `/data`.

1. Add `BOT_TOKEN` as a protected environment variable.
2. Optionally add `ADMIN_IDS`.
3. Set `DB_PATH=/data/attendance.db` so the database survives redeployments.
4. Deploy and confirm that the logs contain `Starting bot` without a configuration error.

The bot uses Telegram long polling. `containerPort` is a platform configuration value, not a public bot endpoint.

## Architecture

- `main.py` — application bootstrap, command registration, and polling.
- `handlers/` — user, group-admin, and fallback Telegram handlers.
- `services/` — attendance, statistics, timezone, chat administration, and SQLite access.
- `config_data/` — environment configuration loading.
- `keyboards/` and `lexicon/` — Russian UI controls and messages.
- `tests/` — service-level unit and edge-case tests.

## Quality checks

```bash
python -m compileall .
python -m unittest discover -s tests -p "test_*.py"
```

The same checks run in [GitHub Actions](.github/workflows/ci.yml). Additional operational documentation:

- [Timezone and status edge cases](docs/TIMEZONE_STATUS_EDGE_CASES.md)
- [Logging policy](docs/LOGGING_POLICY.md)
- [Planned backup command specification](docs/ADMIN_BACKUP_COMMAND_SPEC.md)

## Project status

Active development. CSV export and timezone support are implemented. The admin backup command described in the specification is not implemented yet.

## License

No license file is currently included. Unless a license is added, the repository remains all rights reserved by default.
