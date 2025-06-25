from datetime import datetime, timedelta
from typing import List, Tuple, Optional
from dataclasses import dataclass

from .db_utils import execute_query, fetch_query
from .config_services import SPB, WORKDAY_DURATION_MINUTES


@dataclass
class AttendanceRecord:
    arrival_time: Optional[str]
    departure_time: Optional[str]
    status: Optional[str]
    custom_duration_minutes: Optional[int]
    
    @property
    def date(self) -> datetime:
        """Get the date of the record."""
        time_str = self.arrival_time or self.departure_time
        if time_str:
            return datetime.fromisoformat(time_str).replace(tzinfo=SPB)
        return datetime.now(SPB)


class AttendanceService:
    
    @staticmethod
    def initialize_db():
        """Initialize the database with required tables."""
        execute_query('''
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                arrival_time TEXT,
                departure_time TEXT,
                status TEXT DEFAULT NULL,
                custom_duration_minutes INTEGER DEFAULT NULL
            )
        ''')
    
    @staticmethod
    def record_arrival(user_id: int):
        """Record user arrival time."""
        now = datetime.now(SPB).strftime('%Y-%m-%d %H:%M:%S')
        execute_query(
            'INSERT INTO attendance (user_id, arrival_time) VALUES (?, ?)',
            (user_id, now)
        )
    
    @staticmethod
    def record_departure(user_id: int):
        """Record user departure time."""
        now = datetime.now(SPB).strftime('%Y-%m-%d %H:%M:%S')
        execute_query(
            'UPDATE attendance SET departure_time = ? WHERE user_id = ? AND departure_time IS NULL',
            (now, user_id)
        )
    
    @staticmethod
    def clear_today_records(user_id: int):
        """Clear all records for today for a specific user."""
        today = datetime.now(SPB).date()
        execute_query(
            'DELETE FROM attendance WHERE user_id = ? AND DATE(COALESCE(arrival_time, departure_time)) = ?',
            (user_id, today)
        )
    
    @staticmethod
    def clear_date_records(user_id: int, target_date: datetime):
        """Clear all records for a specific date for a user."""
        execute_query(
            'DELETE FROM attendance WHERE user_id = ? AND DATE(COALESCE(arrival_time, departure_time)) = ?',
            (user_id, target_date.date())
        )
    
    @staticmethod
    def add_status_record(user_id: int, status: str, custom_duration: Optional[int] = None):
        """Add a status-based record (vacation, leave, etc.)."""
        AttendanceService.clear_today_records(user_id)
        now = datetime.now(SPB).isoformat()
        
        execute_query(
            'INSERT INTO attendance (user_id, status, custom_duration_minutes, arrival_time) VALUES (?, ?, ?, ?)',
            (user_id, status, custom_duration, now)
        )
    
    @staticmethod
    def add_manual_complete_day(user_id: int):
        """Add a complete 8.5-hour work day record."""
        AttendanceService.clear_today_records(user_id)
        arrival = datetime.now(SPB)
        departure = arrival + timedelta(hours=8, minutes=30)
        
        execute_query(
            'INSERT INTO attendance (user_id, arrival_time, departure_time) VALUES (?, ?, ?)',
            (user_id, arrival.strftime('%Y-%m-%d %H:%M:%S'), departure.strftime('%Y-%m-%d %H:%M:%S'))
        )
    
    @staticmethod
    def get_period_records(user_id: int, start_date: datetime, end_date: Optional[datetime] = None) -> List[AttendanceRecord]:
        """Get attendance records for a specific period."""
        if end_date:
            query = '''
                SELECT arrival_time, departure_time, status, custom_duration_minutes
                FROM attendance
                WHERE user_id = ? AND DATE(COALESCE(arrival_time, departure_time)) BETWEEN ? AND ?
                ORDER BY COALESCE(arrival_time, departure_time)
            '''
            params = (user_id, start_date.date(), end_date.date())
        else:
            query = '''
                SELECT arrival_time, departure_time, status, custom_duration_minutes
                FROM attendance
                WHERE user_id = ? AND DATE(COALESCE(arrival_time, departure_time)) >= ?
                ORDER BY COALESCE(arrival_time, departure_time)
            '''
            params = (user_id, start_date.date())
        
        data = fetch_query(query, params)
        return [AttendanceRecord(*row) for row in data]
    
    @staticmethod
    def get_all_records(user_id: int) -> List[AttendanceRecord]:
        """Get all attendance records for a user."""
        data = fetch_query(
            'SELECT arrival_time, departure_time, status, custom_duration_minutes FROM attendance WHERE user_id = ? ORDER BY COALESCE(arrival_time, departure_time)',
            (user_id,)
        )
        return [AttendanceRecord(*row) for row in data]
    
    @staticmethod
    def add_manual_entry(user_id: int, date_str: str, arrival_str: str, departure_str: str) -> str:
        """Add a manual time entry."""
        try:
            arrival_time = datetime.strptime(f"{date_str} {arrival_str}", "%Y-%m-%d %H:%M:%S")
            departure_time = datetime.strptime(f"{date_str} {departure_str}", "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return "Неверный формат даты или времени. Используйте формат: Y-m-d H:M:S"
        
        # Clear all records for this date first to avoid duplicates
        AttendanceService.clear_date_records(user_id, arrival_time)
        
        # Add new record
        execute_query(
            'INSERT INTO attendance (user_id, arrival_time, departure_time) VALUES (?, ?, ?)',
            (user_id, arrival_time.strftime('%Y-%m-%d %H:%M:%S'), departure_time.strftime('%Y-%m-%d %H:%M:%S'))
        )
        return "Запись успешно добавлена!"
