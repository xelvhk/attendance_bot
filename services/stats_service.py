from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from collections import defaultdict
import csv
import io

from .attendance_service import AttendanceRecord
from .config_services import SPB, STATUS_EMOJIS, WORKDAY_DURATION_MINUTES


class StatsService:
    
    @staticmethod
    def calculate_work_duration(record: AttendanceRecord) -> Tuple[timedelta, timedelta]:
        """Рассчитывает ожидаемое и фактически отработанное время."""
        # Vacation and personal days - no work required, no debt
        if record.status in ['Отпуск', 'Свой счёт']:
            return timedelta(), timedelta()
        
        # Full leave (УВЦ) - creates debt of full workday
        if record.status == 'УВЦ':
            return timedelta(), timedelta(hours=8, minutes=30)  # 0 worked, 8.5 expected = debt
        
        # Partial leave (УВС) - creates debt for the leave hours
        if record.status == 'УВС' and record.custom_duration_minutes:
            # User worked some hours, but took leave for remaining time
            worked = timedelta(minutes=record.custom_duration_minutes)
            expected = timedelta(hours=8, minutes=30)  # Still need to work full day
            return worked, expected
        
        # Short day with custom duration
        if record.status == 'короткий' and record.custom_duration_minutes:
            worked = timedelta(minutes=record.custom_duration_minutes)
            expected = worked  # For short days, expected equals worked
            return worked, expected
        
        # Regular workday
        if record.arrival_time and record.departure_time:
            arrival = datetime.fromisoformat(record.arrival_time).replace(tzinfo=SPB)
            departure = datetime.fromisoformat(record.departure_time).replace(tzinfo=SPB)
            worked = departure - arrival
            expected = timedelta(hours=8, minutes=30)
            return worked, expected
        
        return timedelta(), timedelta()
    
    @staticmethod
    def format_duration(td: timedelta) -> str:
        """Делает время читаемым и понятным."""
        if td.total_seconds() == 0:
            return "0:00:00"
        
        hours, remainder = divmod(int(td.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    
    @staticmethod
    def format_record_display(record: AttendanceRecord) -> str:
        """Форматирует одиночную запись для вывода."""
        date_str = record.date.strftime('%d.%m.%Y')
        
        # Vacation and personal days
        if record.status in ['Отпуск', 'Свой счёт'] and record.status in STATUS_EMOJIS:
            emoji = STATUS_EMOJIS[record.status]
            return f"{date_str}: {emoji} {record.status}"
        
        # Full leave (УВЦ) - shows debt
        if record.status == 'УВЦ':
            emoji = STATUS_EMOJIS.get(record.status, '🛑')
            return f"{date_str}: {emoji} {record.status} (надо отработать: 8:30:00)"
        
        # Partial leave (УВС) - shows worked time and remaining debt
        if record.status == 'УВС' and record.custom_duration_minutes:
            emoji = STATUS_EMOJIS.get(record.status, '⏳')
            worked = timedelta(minutes=record.custom_duration_minutes)
            debt = timedelta(hours=8, minutes=30) - worked
            return f"{date_str}: {emoji} Работал {StatsService.format_duration(worked)}, отработать надо: {StatsService.format_duration(debt)} (УВС)"
        
        # Short day
        if record.status == 'короткий' and record.custom_duration_minutes:
            emoji = STATUS_EMOJIS.get(record.status, '⏳')
            duration = timedelta(minutes=record.custom_duration_minutes)
            return f"{date_str}: {emoji} {StatsService.format_duration(duration)} (короткий день)"
        
        # Regular workday
        worked, _ = StatsService.calculate_work_duration(record)
        return f"{date_str}: {StatsService.format_duration(worked)}"
    
    @staticmethod
    def calculate_period_stats(records: List[AttendanceRecord]) -> Tuple[str, timedelta, timedelta]:
        """Подсчет статистики за период."""
        if not records:
            return "Нет данных за этот период.", timedelta(), timedelta()
        
        result_lines = []
        total_work = timedelta()
        total_expected = timedelta()
        
        for record in records:
            result_lines.append(StatsService.format_record_display(record))
            worked, expected = StatsService.calculate_work_duration(record)
            total_work += worked
            total_expected += expected
        
        result = "\n".join(result_lines)
        return result, total_work, total_expected
    
    @staticmethod
    def format_balance(total_work: timedelta, total_expected: timedelta) -> str:
        """Форматирует баланс отработанного времени."""
        delta = total_work - total_expected
        
        if delta.total_seconds() > 0:
            return f"<b>✅ Переработка: {StatsService.format_duration(delta)}</b>"
        elif delta.total_seconds() == 0:
            return "<b>✅ Всё чётко</b>"
        else:
            return f"<b>⚠️ Недоработка: {StatsService.format_duration(-delta)}</b>"
    
    @staticmethod
    def generate_week_stats(records: List[AttendanceRecord]) -> str:
        """Создает отчет за неделю."""
        if not records:
            return "Нет данных за эту неделю."
        
        result = "<b>📊 Рабочая неделя:</b>\n"
        stats, total_work, total_expected = StatsService.calculate_period_stats(records)
        result += stats + "\n\n"
        result += StatsService.format_balance(total_work, total_expected)
        
        return result
    
    @staticmethod
    def generate_month_stats(records: List[AttendanceRecord]) -> str:
        """Создает отчет за месяц."""
        if not records:
            return "Нет данных за этот месяц."
        
        # Get current month name
        current_month = datetime.now(SPB).strftime('%B %Y')
        result = f"<b>📆 {current_month}</b>\n"
        
        stats, total_work, total_expected = StatsService.calculate_period_stats(records)
        result += stats + "\n\n"
        result += StatsService.format_balance(total_work, total_expected)
        
        return result
    
    @staticmethod
    def generate_all_stats(records: List[AttendanceRecord]) -> List[str]:
        """Создает и группирует статистику по месяцам за все время."""
        if not records:
            return ["Нет данных."]
        
        monthly_data = defaultdict(list)
        
        # Group records by month
        for record in records:
            month_key = record.date.strftime("%B %Y")
            monthly_data[month_key].append(record)
        
        results = []
        for month, month_records in monthly_data.items():
            result = f"<b>{month}</b>\n"
            stats, total_work, total_expected = StatsService.calculate_period_stats(month_records)
            result += stats + "\n"
            result += StatsService.format_balance(total_work, total_expected)
            results.append(result.strip())
        
        return results
    
    @staticmethod
    def calculate_monthly_balance(records: List[AttendanceRecord]) -> str:
        """Высчитывает баланс времени за месяц."""
        total_work, total_expected = timedelta(), timedelta()
        
        for record in records:
            worked, expected = StatsService.calculate_work_duration(record)
            total_work += worked
            total_expected += expected
        
        delta = total_work - total_expected
        delta_minutes = int(delta.total_seconds() / 60)
        hours, minutes = divmod(abs(delta_minutes), 60)
        
        if delta_minutes > 0:
            return f"Переработка в этом месяце: {hours} часов {minutes} минут"
        elif delta_minutes < 0:
            return f"Недоработка в этом месяце: {hours} часов {minutes} минут"
        else:
            return "Все отработано в точности по графику!"

    @staticmethod
    def export_records_to_csv(records: List[AttendanceRecord]) -> str:
        """Export attendance records to CSV string."""
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(
            [
                "date",
                "arrival_time",
                "departure_time",
                "status",
                "custom_duration_minutes",
                "worked_duration",
                "expected_duration",
            ]
        )

        for record in records:
            worked, expected = StatsService.calculate_work_duration(record)
            writer.writerow(
                [
                    record.date.strftime("%Y-%m-%d"),
                    record.arrival_time or "",
                    record.departure_time or "",
                    record.status or "",
                    record.custom_duration_minutes
                    if record.custom_duration_minutes is not None
                    else "",
                    StatsService.format_duration(worked),
                    StatsService.format_duration(expected),
                ]
            )

        return output.getvalue()
