from __future__ import annotations

import unittest
from datetime import timedelta

from services.attendance_service import AttendanceRecord
from services.stats_service import StatsService


class StatsServiceTests(unittest.TestCase):
    def test_regular_workday_duration(self) -> None:
        record = AttendanceRecord(
            arrival_time="2026-04-24 09:00:00",
            departure_time="2026-04-24 18:00:00",
            status=None,
            custom_duration_minutes=None,
        )
        worked, expected = StatsService.calculate_work_duration(record)
        self.assertEqual(worked, timedelta(hours=9))
        self.assertEqual(expected, timedelta(hours=8, minutes=30))

    def test_vacation_has_no_expected_time(self) -> None:
        record = AttendanceRecord(
            arrival_time=None,
            departure_time=None,
            status="Отпуск",
            custom_duration_minutes=None,
        )
        worked, expected = StatsService.calculate_work_duration(record)
        self.assertEqual(worked, timedelta())
        self.assertEqual(expected, timedelta())

    def test_partial_leave_returns_worked_and_full_expected(self) -> None:
        record = AttendanceRecord(
            arrival_time=None,
            departure_time=None,
            status="УВС",
            custom_duration_minutes=360,
        )
        worked, expected = StatsService.calculate_work_duration(record)
        self.assertEqual(worked, timedelta(hours=6))
        self.assertEqual(expected, timedelta(hours=8, minutes=30))

    def test_monthly_balance_for_undertime(self) -> None:
        records = [
            AttendanceRecord(
                arrival_time="2026-04-24 09:00:00",
                departure_time="2026-04-24 16:00:00",
                status=None,
                custom_duration_minutes=None,
            )
        ]
        result = StatsService.calculate_monthly_balance(records)
        self.assertIn("Недоработка", result)

    def test_week_stats_contains_header(self) -> None:
        records = [
            AttendanceRecord(
                arrival_time="2026-04-24 09:00:00",
                departure_time="2026-04-24 18:00:00",
                status=None,
                custom_duration_minutes=None,
            )
        ]
        report = StatsService.generate_week_stats(records)
        self.assertIn("📊 Рабочая неделя", report)

    def test_export_records_to_csv_contains_header_and_values(self) -> None:
        records = [
            AttendanceRecord(
                arrival_time="2026-04-24 09:00:00",
                departure_time="2026-04-24 18:00:00",
                status=None,
                custom_duration_minutes=None,
            ),
            AttendanceRecord(
                arrival_time=None,
                departure_time=None,
                status="Отпуск",
                custom_duration_minutes=None,
            ),
        ]
        csv_text = StatsService.export_records_to_csv(records)

        self.assertIn("date,arrival_time,departure_time,status,custom_duration_minutes,worked_duration,expected_duration", csv_text)
        self.assertIn("2026-04-24,2026-04-24 09:00:00,2026-04-24 18:00:00,,", csv_text)
        self.assertIn(",,,Отпуск,,0:00:00,0:00:00", csv_text)


if __name__ == "__main__":
    unittest.main()
