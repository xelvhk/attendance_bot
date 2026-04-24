from __future__ import annotations

import unittest

from services.user_timezone_service import UserTimezoneService


class UserTimezoneServiceTests(unittest.TestCase):
    def test_parse_offset_accepts_short_and_full_formats(self) -> None:
        self.assertEqual(UserTimezoneService.parse_offset_text("+3"), 180)
        self.assertEqual(UserTimezoneService.parse_offset_text("UTC+03:30"), 210)
        self.assertEqual(UserTimezoneService.parse_offset_text("-5"), -300)

    def test_parse_offset_rejects_invalid_values(self) -> None:
        self.assertIsNone(UserTimezoneService.parse_offset_text("3"))
        self.assertIsNone(UserTimezoneService.parse_offset_text("UTC+15:00"))
        self.assertIsNone(UserTimezoneService.parse_offset_text("UTC+03:99"))

    def test_format_offset(self) -> None:
        self.assertEqual(UserTimezoneService.format_offset(180), "UTC+03:00")
        self.assertEqual(UserTimezoneService.format_offset(-330), "UTC-05:30")


if __name__ == "__main__":
    unittest.main()
