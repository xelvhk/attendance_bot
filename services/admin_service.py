from aiogram.enums import ChatType

from .db_utils import execute_query, fetch_query


class AdminService:

    @staticmethod
    def initialize_db():
        execute_query(
            '''
            CREATE TABLE IF NOT EXISTS chats (
                chat_id INTEGER PRIMARY KEY,
                title TEXT,
                chat_type TEXT NOT NULL,
                is_enabled INTEGER NOT NULL DEFAULT 0,
                added_by_user_id INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            '''
        )
        execute_query(
            '''
            CREATE TABLE IF NOT EXISTS chat_admins (
                chat_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                role TEXT NOT NULL DEFAULT 'admin',
                added_by_user_id INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (chat_id, user_id)
            )
            '''
        )
        AdminService._migrate_chats_table()

    @staticmethod
    def _migrate_chats_table():
        columns = {
            column[1]
            for column in fetch_query('PRAGMA table_info(chats)')
        }
        if 'is_enabled' not in columns:
            execute_query('ALTER TABLE chats ADD COLUMN is_enabled INTEGER NOT NULL DEFAULT 0')
            execute_query(
                '''
                UPDATE chats
                SET is_enabled = CASE
                    WHEN chat_type = 'private' THEN 1
                    ELSE 0
                END
                '''
            )

    @staticmethod
    def ensure_chat(chat_id: int, title: str | None, chat_type: str, added_by_user_id: int | None = None):
        is_enabled = 1 if chat_type == ChatType.PRIVATE else 0
        execute_query(
            '''
            INSERT INTO chats (chat_id, title, chat_type, is_enabled, added_by_user_id)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(chat_id) DO UPDATE SET
                title = excluded.title,
                chat_type = excluded.chat_type
            ''',
            (chat_id, title, chat_type, is_enabled, added_by_user_id),
        )

    @staticmethod
    def enable_chat(chat_id: int):
        execute_query(
            'UPDATE chats SET is_enabled = 1 WHERE chat_id = ?',
            (chat_id,),
        )

    @staticmethod
    def disable_chat(chat_id: int):
        execute_query(
            'UPDATE chats SET is_enabled = 0 WHERE chat_id = ?',
            (chat_id,),
        )

    @staticmethod
    def is_chat_enabled(chat_id: int) -> bool:
        result = fetch_query(
            'SELECT is_enabled FROM chats WHERE chat_id = ? LIMIT 1',
            (chat_id,),
        )
        return bool(result and result[0][0])

    @staticmethod
    def add_chat_admin(chat_id: int, user_id: int, added_by_user_id: int | None = None, role: str = 'admin'):
        execute_query(
            '''
            INSERT INTO chat_admins (chat_id, user_id, role, added_by_user_id)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(chat_id, user_id) DO UPDATE SET
                role = excluded.role,
                added_by_user_id = excluded.added_by_user_id
            ''',
            (chat_id, user_id, role, added_by_user_id),
        )

    @staticmethod
    def remove_chat_admin(chat_id: int, user_id: int):
        execute_query(
            'DELETE FROM chat_admins WHERE chat_id = ? AND user_id = ?',
            (chat_id, user_id),
        )

    @staticmethod
    def is_chat_admin(chat_id: int, user_id: int) -> bool:
        result = fetch_query(
            'SELECT 1 FROM chat_admins WHERE chat_id = ? AND user_id = ? LIMIT 1',
            (chat_id, user_id),
        )
        return bool(result)

    @staticmethod
    def list_chat_admins(chat_id: int) -> list[tuple[int, str]]:
        rows = fetch_query(
            'SELECT user_id, role FROM chat_admins WHERE chat_id = ? ORDER BY created_at, user_id',
            (chat_id,),
        )
        return [(row[0], row[1]) for row in rows]

    @staticmethod
    def is_group_chat(chat_type: str) -> bool:
        return chat_type in {ChatType.GROUP, ChatType.SUPERGROUP}
