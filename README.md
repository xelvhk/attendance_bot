# attendance_bot

Telegram bot for personal attendance and work-time tracking.

## Problem
Manual attendance tracking is noisy and error-prone. `attendance_bot` gives a lightweight Telegram interface to:
- mark arrival/departure
- save special day statuses (vacation, leave, shortened day)
- calculate weekly/monthly balance automatically

## Stack
- Python 3.10+
- Aiogram 3
- SQLite
- environs

## Quick Start
```bash
git clone https://github.com/xelvhk/attendance_bot.git
cd attendance_bot
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python main.py
```

## Environment
Create `.env` from `.env.example`:
```env
BOT_TOKEN=your_telegram_bot_token
```

## Architecture
- `main.py`: app bootstrap, bot/dispatcher startup
- `handlers/`: Telegram commands and message handlers
- `services/`: domain logic (attendance, stats, db)
- `config_data/`: config loading from env
- `keyboards/`, `lexicon/`: UI and localized texts

## Demo / Screenshots
- Demo chat flow: add screenshots to `docs/screenshots/` (placeholder)
- Suggested files: `start.png`, `week-stats.png`, `month-stats.png`

## Roadmap
- [ ] Export monthly report to CSV
- [ ] Add per-user timezone setting
- [ ] Add simple admin command for data backup
- [ ] Add pytest tests for `services/stats_service.py`

## CI
Minimal CI is configured in `.github/workflows/ci.yml`:
- install dependencies
- run syntax check (`python -m compileall`)
