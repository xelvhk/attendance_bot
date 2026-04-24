from __future__ import annotations

from datetime import timedelta, timezone, tzinfo
import re

from .config_services import SPB
from .db_utils import execute_query, fetch_query

DEFAULT_OFFSET_MINUTES = int(SPB.utcoffset(None).total_seconds() // 60)
_OFFSET_PATTERN = re.compile(r"^([+-])(\d{1,2})(?::([0-5]\d))?$")


class UserTimezoneService:
    @staticmethod
    def initialize_db() -> None:
        execute_query(
            """
            CREATE TABLE IF NOT EXISTS user_settings (
                user_id INTEGER PRIMARY KEY,
                utc_offset_minutes INTEGER NOT NULL DEFAULT 180
            )
            """
        )

    @staticmethod
    def get_user_offset_minutes(user_id: int) -> int:
        UserTimezoneService.initialize_db()
        row = fetch_query(
            "SELECT utc_offset_minutes FROM user_settings WHERE user_id = ?",
            (user_id,),
        )
        if not row:
            return DEFAULT_OFFSET_MINUTES
        return int(row[0][0])

    @staticmethod
    def get_user_timezone(user_id: int) -> tzinfo:
        offset = UserTimezoneService.get_user_offset_minutes(user_id)
        return timezone(timedelta(minutes=offset))

    @staticmethod
    def set_user_timezone(user_id: int, offset_minutes: int) -> None:
        if offset_minutes < -12 * 60 or offset_minutes > 14 * 60:
            raise ValueError("UTC offset is out of supported range.")

        UserTimezoneService.initialize_db()
        execute_query(
            """
            INSERT INTO user_settings (user_id, utc_offset_minutes)
            VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET utc_offset_minutes = excluded.utc_offset_minutes
            """,
            (user_id, offset_minutes),
        )

    @staticmethod
    def parse_offset_text(value: str) -> int | None:
        value = value.strip().upper().replace("UTC", "")
        match = _OFFSET_PATTERN.match(value)
        if not match:
            return None

        sign, hours_text, minutes_text = match.groups()
        hours = int(hours_text)
        minutes = int(minutes_text or "0")
        if hours > 14:
            return None
        total = hours * 60 + minutes
        if sign == "-":
            total = -total
        if total < -12 * 60 or total > 14 * 60:
            return None
        return total

    @staticmethod
    def format_offset(offset_minutes: int) -> str:
        sign = "+" if offset_minutes >= 0 else "-"
        value = abs(offset_minutes)
        hours, minutes = divmod(value, 60)
        return f"UTC{sign}{hours:02d}:{minutes:02d}"
