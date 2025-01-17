import sqlite3
import sys
from datetime import datetime

CON = sqlite3.connect('standup-monkey.db', check_same_thread=False)
CURSOR = CON.cursor()
CON.set_trace_callback(print)


def create_tables_in_db():
    """
    Creates required tables.
    :return: None
    """
    CURSOR.execute(
        """
        CREATE TABLE IF NOT EXISTS standups
        (
            user_id     TEXT,
            date        TEXT,
            yesterday   TEXT,
            today       TEXT,
            blocker     TEXT,
            channel     TEXT,
            modified_at TEXT,
            UNIQUE(user_id, date)
        );
        """
    )


def drop_tables_in_db():
    """
    Drops tables from db.
    :return: None
    """
    CURSOR.execute(
        """
        DROP TABLE IF EXISTS standups;
        """
    )


def upsert_today_standup_status(user_id, channel=None, column_name=None, message=None):
    """
    Inserts today's standup status to database.
    :param message: Standup message to store
    :param column_name: Column name in which message needs to store
    :return: None
    """
    create_tables_in_db()
    today = datetime.today().strftime('%Y-%m-%d')
    now = datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
    CURSOR.execute(
        """
        INSERT INTO standups (
            user_id,
            date,
            {column_name}
            {channel}
            modified_at
        )
        VALUES (?, ?, ?, ?)
        ON CONFLICT(user_id, date) DO UPDATE SET
            {column_conflict_clause}
            {channel_conflict_clause}
        ;
        """.format(
            column_name=f'{column_name},' if column_name else '',
            channel=f'channel,' if channel else '',
            column_conflict_clause=f'{column_name}=excluded.{column_name}' if column_name else '',
            channel_conflict_clause='channel=excluded.channel' if channel else ''
        ),
        (user_id, today, channel, now) if channel else (user_id, today, message, now)
    )


def get_today_standup_status(user_id):
    """
    Gets today's standup status of user.
    :param user_id: User whom standup is being retrieved
    :return: Dict of values for today's standup
    """
    today = datetime.today().strftime('%Y-%m-%d')
    CURSOR.execute(
        """
        SELECT * FROM standups WHERE user_id=:user_id AND date=:today;
        """,
        {"user_id": user_id, "today": today}
    )
    return CURSOR.fetchone()


if __name__ == "__main__":
    if sys.argv[1] == "drop-tables":
        drop_tables_in_db()

    create_tables_in_db()
