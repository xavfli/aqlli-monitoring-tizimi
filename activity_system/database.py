import csv
import sqlite3
from pathlib import Path

from .config import DATA_DIR, DATABASE_PATH, EXPORT_DIR

USE_MEMORY_DB = False
MEMORY_SESSIONS: list[dict] = []
MEMORY_STUDENT_RESULTS: list[dict] = []
MEMORY_STUDENT_ROSTER: list[dict] = []
MEMORY_CAMERA_SETTINGS: dict = {
    "id": 1,
    "room_name": "E 102 xona",
    "camera_index": -1,
    "camera_source": "",
    "notes": "",
}
MEMORY_UNIVERSITY_DB_SETTINGS: dict = {
    "id": 1,
    "db_type": "sqlite",
    "host": "",
    "port": "",
    "database_name": "",
    "username": "",
    "password": "",
    "student_table": "students",
    "student_id_column": "student_id",
    "student_name_column": "full_name",
    "group_column": "group_name",
    "notes": "",
}


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    global USE_MEMORY_DB
    DATA_DIR.mkdir(exist_ok=True)
    EXPORT_DIR.mkdir(exist_ok=True)
    try:
        with get_connection() as conn:
            conn.execute(
                """
            CREATE TABLE IF NOT EXISTS session_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_name TEXT NOT NULL,
                started_at TEXT NOT NULL,
                ended_at TEXT NOT NULL,
                duration_seconds REAL NOT NULL,
                total_frames INTEGER NOT NULL,
                face_frames INTEGER NOT NULL,
                average_detected_faces REAL NOT NULL DEFAULT 0,
                max_detected_faces INTEGER NOT NULL DEFAULT 0,
                absence_frames INTEGER NOT NULL,
                presence_ratio REAL NOT NULL,
                attention_ratio REAL NOT NULL,
                movement_ratio REAL NOT NULL,
                average_score REAL NOT NULL,
                    max_score REAL NOT NULL,
                    notes TEXT
                )
                """
            )
            conn.execute(
                """
            CREATE TABLE IF NOT EXISTS student_latest_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_name TEXT NOT NULL UNIQUE,
                session_id INTEGER,
                participant_id TEXT NOT NULL,
                average_score REAL NOT NULL,
                max_score REAL NOT NULL,
                presence_ratio REAL NOT NULL,
                phone_suspect INTEGER NOT NULL DEFAULT 0,
                question_gesture INTEGER NOT NULL DEFAULT 0,
                drowsy_suspect INTEGER NOT NULL DEFAULT 0,
                looking_away INTEGER NOT NULL DEFAULT 0,
                updated_at TEXT NOT NULL
            )
                """
            )
            conn.execute(
                """
            CREATE TABLE IF NOT EXISTS student_roster (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_name TEXT NOT NULL UNIQUE,
                group_name TEXT DEFAULT '',
                notes TEXT DEFAULT ''
            )
                """
            )
            conn.execute(
                """
            CREATE TABLE IF NOT EXISTS camera_settings (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                room_name TEXT NOT NULL DEFAULT 'E 102 xona',
                camera_index INTEGER NOT NULL DEFAULT -1,
                camera_source TEXT NOT NULL DEFAULT '',
                notes TEXT NOT NULL DEFAULT '',
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
                """
            )
            conn.execute(
                """
            INSERT OR IGNORE INTO camera_settings (
                id,
                room_name,
                camera_index,
                camera_source,
                notes
            )
            VALUES (1, 'E 102 xona', -1, '', '')
                """
            )
            conn.execute(
                """
            CREATE TABLE IF NOT EXISTS university_db_settings (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                db_type TEXT NOT NULL DEFAULT 'sqlite',
                host TEXT NOT NULL DEFAULT '',
                port TEXT NOT NULL DEFAULT '',
                database_name TEXT NOT NULL DEFAULT '',
                username TEXT NOT NULL DEFAULT '',
                password TEXT NOT NULL DEFAULT '',
                student_table TEXT NOT NULL DEFAULT 'students',
                student_id_column TEXT NOT NULL DEFAULT 'student_id',
                student_name_column TEXT NOT NULL DEFAULT 'full_name',
                group_column TEXT NOT NULL DEFAULT 'group_name',
                notes TEXT NOT NULL DEFAULT '',
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
                """
            )
            conn.execute(
                """
            INSERT OR IGNORE INTO university_db_settings (
                id,
                db_type,
                student_table,
                student_id_column,
                student_name_column,
                group_column
            )
            VALUES (1, 'sqlite', 'students', 'student_id', 'full_name', 'group_name')
                """
            )
    except sqlite3.Error:
        USE_MEMORY_DB = True


def insert_session(session_data: dict) -> int:
    if USE_MEMORY_DB:
        session_id = len(MEMORY_SESSIONS) + 1
        row = {"id": session_id, **session_data}
        MEMORY_SESSIONS.append(row)
        return session_id

    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO session_results (
                session_name,
                started_at,
                ended_at,
                duration_seconds,
                total_frames,
                face_frames,
                average_detected_faces,
                max_detected_faces,
                absence_frames,
                presence_ratio,
                attention_ratio,
                movement_ratio,
                average_score,
                max_score,
                notes
            )
            VALUES (
                :session_name,
                :started_at,
                :ended_at,
                :duration_seconds,
                :total_frames,
                :face_frames,
                :average_detected_faces,
                :max_detected_faces,
                :absence_frames,
                :presence_ratio,
                :attention_ratio,
                :movement_ratio,
                :average_score,
                :max_score,
                :notes
            )
            """,
            session_data,
        )
        return int(cursor.lastrowid)


def fetch_recent_sessions(limit: int = 20) -> list[dict]:
    if USE_MEMORY_DB:
        return list(reversed(MEMORY_SESSIONS[-limit:]))

    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM session_results
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [dict(row) for row in rows]


def fetch_summary() -> dict:
    if USE_MEMORY_DB:
        total_sessions = len(MEMORY_SESSIONS)
        if total_sessions == 0:
            return {
                "total_sessions": 0,
                "mean_score": 0,
                "mean_presence": 0,
                "best_score": 0,
            }
        mean_score = sum(row["average_score"] for row in MEMORY_SESSIONS) / total_sessions
        mean_presence = sum(row["presence_ratio"] for row in MEMORY_SESSIONS) / total_sessions
        best_score = max(row["max_score"] for row in MEMORY_SESSIONS)
        return {
            "total_sessions": total_sessions,
            "mean_score": mean_score,
            "mean_presence": mean_presence,
            "best_score": best_score,
        }

    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT
                COUNT(*) AS total_sessions,
                COALESCE(AVG(average_score), 0) AS mean_score,
                COALESCE(AVG(presence_ratio), 0) AS mean_presence,
                COALESCE(MAX(max_score), 0) AS best_score
            FROM session_results
            """
        ).fetchone()
    return dict(row)


def save_student_latest_results(session_id: int, participant_summary: list[dict], updated_at: str) -> None:
    named_rows = [row for row in participant_summary if row.get("assigned_name")]
    if USE_MEMORY_DB:
        global MEMORY_STUDENT_RESULTS
        existing = {row["student_name"]: row for row in MEMORY_STUDENT_RESULTS}
        for row in named_rows:
            existing[row["assigned_name"]] = {
                "student_name": row["assigned_name"],
                "session_id": session_id,
                "participant_id": row["participant_id"],
                "average_score": row.get("average_score", 0),
                "max_score": row.get("max_score", 0),
                "presence_ratio": row.get("presence_ratio", 0),
                "phone_suspect": row.get("event_counts", {}).get("phone_suspect", 0),
                "question_gesture": row.get("event_counts", {}).get("question_gesture", 0),
                "drowsy_suspect": row.get("event_counts", {}).get("drowsy_suspect", 0),
                "looking_away": row.get("event_counts", {}).get("looking_away", 0),
                "updated_at": updated_at,
            }
        MEMORY_STUDENT_RESULTS = list(existing.values())
        return

    with get_connection() as conn:
        for row in named_rows:
            conn.execute(
                """
                INSERT INTO student_latest_results (
                    student_name,
                    session_id,
                    participant_id,
                    average_score,
                    max_score,
                    presence_ratio,
                    phone_suspect,
                    question_gesture,
                    drowsy_suspect,
                    looking_away,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(student_name) DO UPDATE SET
                    session_id=excluded.session_id,
                    participant_id=excluded.participant_id,
                    average_score=excluded.average_score,
                    max_score=excluded.max_score,
                    presence_ratio=excluded.presence_ratio,
                    phone_suspect=excluded.phone_suspect,
                    question_gesture=excluded.question_gesture,
                    drowsy_suspect=excluded.drowsy_suspect,
                    looking_away=excluded.looking_away,
                    updated_at=excluded.updated_at
                """,
                (
                    row["assigned_name"],
                    session_id,
                    row["participant_id"],
                    row.get("average_score", 0),
                    row.get("max_score", 0),
                    row.get("presence_ratio", 0),
                    row.get("event_counts", {}).get("phone_suspect", 0),
                    row.get("event_counts", {}).get("question_gesture", 0),
                    row.get("event_counts", {}).get("drowsy_suspect", 0),
                    row.get("event_counts", {}).get("looking_away", 0),
                    updated_at,
                ),
            )


def fetch_student_latest_results(limit: int = 100) -> list[dict]:
    if USE_MEMORY_DB:
        rows = sorted(MEMORY_STUDENT_RESULTS, key=lambda row: row.get("updated_at", ""), reverse=True)
        return rows[:limit]

    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM student_latest_results
            ORDER BY updated_at DESC, student_name ASC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [dict(row) for row in rows]


def add_student_roster(student_name: str, group_name: str = "", notes: str = "") -> dict:
    student_name = student_name.strip()
    group_name = group_name.strip()
    notes = notes.strip()
    if USE_MEMORY_DB:
        for row in MEMORY_STUDENT_ROSTER:
            if row["student_name"].lower() == student_name.lower():
                return row
        row = {
            "id": len(MEMORY_STUDENT_ROSTER) + 1,
            "student_name": student_name,
            "group_name": group_name,
            "notes": notes,
        }
        MEMORY_STUDENT_ROSTER.append(row)
        return row

    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO student_roster (student_name, group_name, notes)
            VALUES (?, ?, ?)
            ON CONFLICT(student_name) DO UPDATE SET
                group_name=excluded.group_name,
                notes=excluded.notes
            """,
            (student_name, group_name, notes),
        )
        row = conn.execute(
            """
            SELECT *
            FROM student_roster
            WHERE student_name = ?
            """,
            (student_name,),
        ).fetchone()
    return dict(row)


def fetch_student_roster(limit: int = 500) -> list[dict]:
    if USE_MEMORY_DB:
        return sorted(MEMORY_STUDENT_ROSTER, key=lambda row: row["student_name"].lower())[:limit]

    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM student_roster
            ORDER BY student_name ASC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [dict(row) for row in rows]


def fetch_camera_settings() -> dict:
    if USE_MEMORY_DB:
        return dict(MEMORY_CAMERA_SETTINGS)

    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT *
            FROM camera_settings
            WHERE id = 1
            """
        ).fetchone()
    return dict(row) if row else {
        "id": 1,
        "room_name": "E 102 xona",
        "camera_index": -1,
        "camera_source": "",
        "notes": "",
    }


def save_camera_settings(
    room_name: str,
    camera_index: int,
    camera_source: str = "",
    notes: str = "",
) -> dict:
    room_name = room_name.strip() or "E 102 xona"
    camera_source = camera_source.strip()
    notes = notes.strip()
    if USE_MEMORY_DB:
        MEMORY_CAMERA_SETTINGS.update(
            {
                "room_name": room_name,
                "camera_index": camera_index,
                "camera_source": camera_source,
                "notes": notes,
            }
        )
        return dict(MEMORY_CAMERA_SETTINGS)

    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO camera_settings (
                id,
                room_name,
                camera_index,
                camera_source,
                notes,
                updated_at
            )
            VALUES (1, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(id) DO UPDATE SET
                room_name=excluded.room_name,
                camera_index=excluded.camera_index,
                camera_source=excluded.camera_source,
                notes=excluded.notes,
                updated_at=CURRENT_TIMESTAMP
            """,
            (room_name, camera_index, camera_source, notes),
        )
    return fetch_camera_settings()


def fetch_university_db_settings() -> dict:
    if USE_MEMORY_DB:
        return dict(MEMORY_UNIVERSITY_DB_SETTINGS)

    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT *
            FROM university_db_settings
            WHERE id = 1
            """
        ).fetchone()
    return dict(row) if row else dict(MEMORY_UNIVERSITY_DB_SETTINGS)


def save_university_db_settings(settings: dict) -> dict:
    db_type = (settings.get("db_type") or "sqlite").strip()
    host = (settings.get("host") or "").strip()
    port = str(settings.get("port") or "").strip()
    database_name = (settings.get("database_name") or "").strip()
    username = (settings.get("username") or "").strip()
    password = (settings.get("password") or "").strip()
    student_table = (settings.get("student_table") or "students").strip()
    student_id_column = (settings.get("student_id_column") or "student_id").strip()
    student_name_column = (settings.get("student_name_column") or "full_name").strip()
    group_column = (settings.get("group_column") or "group_name").strip()
    notes = (settings.get("notes") or "").strip()

    payload = {
        "id": 1,
        "db_type": db_type,
        "host": host,
        "port": port,
        "database_name": database_name,
        "username": username,
        "password": password,
        "student_table": student_table,
        "student_id_column": student_id_column,
        "student_name_column": student_name_column,
        "group_column": group_column,
        "notes": notes,
    }
    if USE_MEMORY_DB:
        MEMORY_UNIVERSITY_DB_SETTINGS.update(payload)
        return dict(MEMORY_UNIVERSITY_DB_SETTINGS)

    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO university_db_settings (
                id,
                db_type,
                host,
                port,
                database_name,
                username,
                password,
                student_table,
                student_id_column,
                student_name_column,
                group_column,
                notes,
                updated_at
            )
            VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(id) DO UPDATE SET
                db_type=excluded.db_type,
                host=excluded.host,
                port=excluded.port,
                database_name=excluded.database_name,
                username=excluded.username,
                password=excluded.password,
                student_table=excluded.student_table,
                student_id_column=excluded.student_id_column,
                student_name_column=excluded.student_name_column,
                group_column=excluded.group_column,
                notes=excluded.notes,
                updated_at=CURRENT_TIMESTAMP
            """,
            (
                db_type,
                host,
                port,
                database_name,
                username,
                password,
                student_table,
                student_id_column,
                student_name_column,
                group_column,
                notes,
            ),
        )
    return fetch_university_db_settings()


def export_sessions_csv() -> Path:
    rows = fetch_recent_sessions(limit=1000)
    export_path = EXPORT_DIR / "session_results.csv"
    fieldnames = [
        "id",
        "session_name",
        "started_at",
        "ended_at",
        "duration_seconds",
        "total_frames",
        "face_frames",
        "average_detected_faces",
        "max_detected_faces",
        "absence_frames",
        "presence_ratio",
        "attention_ratio",
        "movement_ratio",
        "average_score",
        "max_score",
        "notes",
    ]
    with export_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return export_path
