from __future__ import annotations

import tempfile
import unittest
from datetime import datetime, timezone, timedelta
from pathlib import Path
from unittest.mock import patch

from services.attendance_service import AttendanceService
from services.db_utils import execute_query, fetch_query


class AttendanceServiceEdgeCasesTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp_dir = tempfile.TemporaryDirectory()
        self._db_path = str(Path(self._tmp_dir.name) / "attendance_test.db")
        patcher = patch("services.db_utils.DB_PATH", self._db_path)
        self._db_patcher = patcher
        self._db_patcher.start()
        AttendanceService.initialize_db()

    def tearDown(self) -> None:
        self._db_patcher.stop()
        self._tmp_dir.cleanup()

    def test_same_status_submit_is_idempotent_for_day(self) -> None:
        user_id = 101
        tz = timezone(timedelta(hours=3))

        AttendanceService.add_status_record(user_id, "Отпуск", user_tz=tz)
        AttendanceService.add_status_record(user_id, "Отпуск", user_tz=tz)

        rows = fetch_query(
            "SELECT status FROM attendance WHERE user_id = ?",
            (user_id,),
        )
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][0], "Отпуск")

    def test_conflicting_status_replaces_previous_same_day(self) -> None:
        user_id = 202
        tz = timezone(timedelta(hours=3))

        AttendanceService.add_status_record(user_id, "УВЦ", user_tz=tz)
        AttendanceService.add_status_record(user_id, "УВС", custom_duration=300, user_tz=tz)

        rows = fetch_query(
            "SELECT status, custom_duration_minutes FROM attendance WHERE user_id = ?",
            (user_id,),
        )
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][0], "УВС")
        self.assertEqual(rows[0][1], 300)

    def test_clear_today_records_uses_user_timezone_bucket(self) -> None:
        user_id = 303
        # Preload two local-date rows for the same user.
        execute_query(
            "INSERT INTO attendance (user_id, arrival_time) VALUES (?, ?)",
            (user_id, "2026-05-05 09:00:00"),
        )
        execute_query(
            "INSERT INTO attendance (user_id, arrival_time) VALUES (?, ?)",
            (user_id, "2026-05-06 09:00:00"),
        )

        class _FixedDateTime:
            @staticmethod
            def now(_tz):
                return datetime(2026, 5, 6, 10, 0, 0)

        with patch("services.attendance_service.datetime", _FixedDateTime):
            AttendanceService.clear_today_records(user_id, user_tz=timezone.utc)

        remaining = fetch_query(
            "SELECT DATE(arrival_time) FROM attendance WHERE user_id = ? ORDER BY arrival_time",
            (user_id,),
        )
        self.assertEqual(remaining, [("2026-05-05",)])


if __name__ == "__main__":
    unittest.main()
