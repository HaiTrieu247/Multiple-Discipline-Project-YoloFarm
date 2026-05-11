import os
import time
import sqlite3
from pathlib import Path
from typing import Any, Dict


class DBManager:
    def __init__(self, db_path: str | Path) -> None:
        self.db_path = str(db_path)
        self._ensure_directory_exists()

    def _ensure_directory_exists(self) -> None:
        directory = os.path.dirname(self.db_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path, timeout=30, check_same_thread=False)
        connection.row_factory = sqlite3.Row
        return connection

    def initialize_database(self) -> None:
        with self._connect() as conn:
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA synchronous = NORMAL;")
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS SensorHistory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    temperature REAL,
                    humidity REAL,
                    soil_moisture INTEGER,
                    light_level INTEGER,
                    pump_state INTEGER NOT NULL,
                    pump_mode TEXT NOT NULL,
                    humidity_threshold REAL NOT NULL
                )
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_timestamp ON SensorHistory(timestamp);"
            )
            conn.commit()

    def insert_sensor_history(self, data: Dict[str, Any]) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO SensorHistory (
                    timestamp,
                    temperature,
                    humidity,
                    soil_moisture,
                    light_level,
                    pump_state,
                    pump_mode,
                    humidity_threshold
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data.get("timestamp"),
                    data.get("temperature"),
                    data.get("humidity"),
                    data.get("soil_moisture"),
                    data.get("light_level"),
                    data.get("pump_state"),
                    data.get("pump_mode"),
                    data.get("humidity_threshold"),
                ),
            )
            conn.commit()

    def get_sensor_history(self, limit: int = 100, offset: int = 0) -> tuple[list[Dict[str, Any]], int]:
        """
        Lấy lịch sử sensor với phân trang.
        
        Args:
            limit: số record tối đa mỗi lần
            offset: vị trí bắt đầu
            
        Returns:
            (danh sách record, tổng số record)
        """
        with self._connect() as conn:
            total = conn.execute("SELECT COUNT(*) as cnt FROM SensorHistory").fetchone()["cnt"]
            rows = conn.execute(
                "SELECT * FROM SensorHistory ORDER BY timestamp DESC LIMIT ? OFFSET ?",
                (limit, offset),
            ).fetchall()
            
        records = [dict(row) for row in rows]
        return records, total

    def delete_old_records(self, days: int = 30) -> int:
        """Xóa các bản ghi SensorHistory cũ hơn một số ngày cho trước."""
        cutoff = time.time() - days * 86400
        with self._connect() as conn:
            cursor = conn.execute(
                "DELETE FROM SensorHistory WHERE timestamp < ?",
                (cutoff,),
            )
            conn.commit()
            return cursor.rowcount

