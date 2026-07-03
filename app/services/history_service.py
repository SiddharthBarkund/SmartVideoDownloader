"""
Smart Video Downloader — History Service
SQLite-backed download history with async operations via aiosqlite.
"""

import aiosqlite
from datetime import datetime, timezone

from app.config import DB_PATH
from app.utils.logger import get_logger

logger = get_logger("history_service")

_DB = str(DB_PATH)


async def init_db() -> None:
    """Create the history table if it does not exist."""
    async with aiosqlite.connect(_DB) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS downloads (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                title       TEXT NOT NULL,
                url         TEXT NOT NULL,
                thumbnail   TEXT,
                file_path   TEXT,
                file_size   INTEGER,
                format      TEXT,
                quality     TEXT,
                status      TEXT DEFAULT 'complete',
                downloaded_at TEXT NOT NULL
            )
        """)
        await db.commit()
    logger.info("Database initialized at %s", _DB)


async def add_record(
    title: str,
    url: str,
    thumbnail: str | None,
    file_path: str | None,
    file_size: int | None,
    fmt: str | None,
    quality: str | None,
) -> int:
    """Insert a new download record. Returns the row id."""
    now = datetime.now(timezone.utc).isoformat()
    async with aiosqlite.connect(_DB) as db:
        cursor = await db.execute(
            """INSERT INTO downloads
               (title, url, thumbnail, file_path, file_size, format, quality, status, downloaded_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, 'complete', ?)""",
            (title, url, thumbnail, file_path, file_size, fmt, quality, now),
        )
        await db.commit()
        record_id = cursor.lastrowid
    logger.info("History record added: #%d — %s", record_id, title)
    return record_id


async def get_all(search: str | None = None) -> list[dict]:
    """Retrieve all download records, optionally filtered by a search term."""
    async with aiosqlite.connect(_DB) as db:
        db.row_factory = aiosqlite.Row
        if search:
            rows = await db.execute_fetchall(
                "SELECT * FROM downloads WHERE title LIKE ? ORDER BY id DESC",
                (f"%{search}%",),
            )
        else:
            rows = await db.execute_fetchall(
                "SELECT * FROM downloads ORDER BY id DESC"
            )
    return [dict(row) for row in rows]


async def delete_record(record_id: int) -> bool:
    """Delete a single history record by id."""
    async with aiosqlite.connect(_DB) as db:
        cursor = await db.execute("DELETE FROM downloads WHERE id = ?", (record_id,))
        await db.commit()
        deleted = cursor.rowcount > 0
    if deleted:
        logger.info("History record #%d deleted", record_id)
    return deleted


async def clear_all() -> int:
    """Delete all history records. Returns the count of deleted rows."""
    async with aiosqlite.connect(_DB) as db:
        cursor = await db.execute("DELETE FROM downloads")
        await db.commit()
        count = cursor.rowcount
    logger.info("All history cleared (%d records)", count)
    return count
