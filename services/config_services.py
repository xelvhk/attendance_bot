from datetime import timedelta, timezone

# Timezone configuration
SPB = timezone(timedelta(hours=3))

# Work duration constants
WORKDAY_DURATION_MINUTES = 8 * 60 + 30  # 510 minutes (8.5 hours)

# Work status types
WORK_STATUSES = {
    'VACATION': 'Отпуск',
    'PERSONAL_DAY': 'Свой счёт',
    'FULL_LEAVE': 'УВЦ',
    'PARTIAL_LEAVE': 'УВС',
    'SHORT_DAY': 'короткий',
    'MANUAL_COMPLETE': 'МК'
}

# Status emojis
STATUS_EMOJIS = {
    'Отпуск': '🏖',
    'Свой счёт': '💸',
    'УВЦ': '🛑',
    'УВС': '⏳',
    'короткий': '⏳'
}
