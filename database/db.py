import sqlite3
from pathlib import Path
from typing import Any

SCHEMA = """
CREATE TABLE IF NOT EXISTS benchmarks (
 id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
 size INTEGER NOT NULL, distribution TEXT NOT NULL, seed INTEGER NOT NULL,
 repetitions INTEGER NOT NULL, workers INTEGER NOT NULL, cutoff INTEGER NOT NULL,
 single_time_ns INTEGER NOT NULL, parallel_time_ns INTEGER NOT NULL,
 speedup REAL, correct INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS player (id INTEGER PRIMARY KEY CHECK (id = 1), xp INTEGER NOT NULL DEFAULT 0);
INSERT OR IGNORE INTO player (id, xp) VALUES (1, 0);
CREATE TABLE IF NOT EXISTS achievements (key TEXT PRIMARY KEY, unlocked_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
"""


class Database:
    def __init__(self, path: str | Path):
        self.path = str(path)
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        connection.executescript(SCHEMA)
        return connection

    def add_benchmark(self, data: dict[str, Any]) -> int:
        with self.connect() as db:
            cursor = db.execute(
                """INSERT INTO benchmarks
                (size, distribution, seed, repetitions, workers, cutoff, single_time_ns,
                 parallel_time_ns, speedup, correct)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                tuple(data[key] for key in ("size", "distribution", "seed", "repetitions",
                    "workers", "cutoff", "single_time_ns", "parallel_time_ns", "speedup", "correct")),
            )
            return int(cursor.lastrowid)

    def history(self, limit: int = 100) -> list[dict[str, Any]]:
        with self.connect() as db:
            return [dict(row) for row in db.execute(
                "SELECT * FROM benchmarks ORDER BY id DESC LIMIT ?", (limit,))]

    def player(self) -> dict[str, Any]:
        with self.connect() as db:
            xp = int(db.execute("SELECT xp FROM player WHERE id=1").fetchone()["xp"])
            unlocked = [row["key"] for row in db.execute("SELECT key FROM achievements")]
        level = min(5, xp // 100 + 1)
        names = ["Rookie", "Sorter", "Algorithm Explorer", "Parallel Pioneer", "Merge Master"]
        return {"xp": xp, "level": level, "title": names[level - 1], "achievements": unlocked}

    def award(self, key: str, xp: int) -> bool:
        with self.connect() as db:
            exists = db.execute("SELECT 1 FROM achievements WHERE key=?", (key,)).fetchone()
            if exists:
                return False
            db.execute("INSERT INTO achievements(key) VALUES (?)", (key,))
            db.execute("UPDATE player SET xp=xp+? WHERE id=1", (xp,))
            return True
