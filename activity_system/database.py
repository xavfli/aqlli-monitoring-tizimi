import csv
import sqlite3
from pathlib import Path

from .config import DATA_DIR, DATABASE_PATH, EXPORT_DIR

USE_MEMORY_DB = False
MEMORY_SESSIONS: list[dict] = []
MEMORY_STUDENT_RESULTS: list[dict] = []
MEMORY_PARTICIPANT_RESULTS: list[dict] = []
MEMORY_STUDENT_ROSTER: list[dict] = []
MEMORY_CAMERA_SETTINGS: dict = {
    "id": 1,
    "room_name": "Zoom demo darsi",
    "camera_index": -1,
    "camera_source": "screen:1",
    "zoom_link": "https://us05web.zoom.us/j/5336068317?pwd=i7Jcq4200iSXNHWvKpqEIW3BVsgAat.1",
    "zoom_meeting_id": "533 606 8317",
    "zoom_passcode": "1Xkpny",
    "notes": "Zoom oynasi asosiy monitorda ochiladi.",
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
            session_columns = {
                row["name"]
                for row in conn.execute("PRAGMA table_info(session_results)").fetchall()
            }
            if "average_detected_faces" not in session_columns:
                conn.execute(
                    "ALTER TABLE session_results ADD COLUMN average_detected_faces REAL NOT NULL DEFAULT 0"
                )
            if "max_detected_faces" not in session_columns:
                conn.execute(
                    "ALTER TABLE session_results ADD COLUMN max_detected_faces INTEGER NOT NULL DEFAULT 0"
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
            CREATE TABLE IF NOT EXISTS session_participant_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                participant_id TEXT NOT NULL,
                student_name TEXT NOT NULL DEFAULT '',
                average_score REAL NOT NULL,
                max_score REAL NOT NULL,
                presence_ratio REAL NOT NULL,
                frames INTEGER NOT NULL DEFAULT 0,
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
                room_name TEXT NOT NULL DEFAULT 'Zoom darsi',
                camera_index INTEGER NOT NULL DEFAULT -1,
                camera_source TEXT NOT NULL DEFAULT '',
                zoom_link TEXT NOT NULL DEFAULT '',
                zoom_meeting_id TEXT NOT NULL DEFAULT '',
                zoom_passcode TEXT NOT NULL DEFAULT '',
                notes TEXT NOT NULL DEFAULT '',
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
                """
            )
            columns = {
                row["name"]
                for row in conn.execute("PRAGMA table_info(camera_settings)").fetchall()
            }
            if "zoom_link" not in columns:
                conn.execute("ALTER TABLE camera_settings ADD COLUMN zoom_link TEXT NOT NULL DEFAULT ''")
            if "zoom_meeting_id" not in columns:
                conn.execute("ALTER TABLE camera_settings ADD COLUMN zoom_meeting_id TEXT NOT NULL DEFAULT ''")
            if "zoom_passcode" not in columns:
                conn.execute("ALTER TABLE camera_settings ADD COLUMN zoom_passcode TEXT NOT NULL DEFAULT ''")
            conn.execute(
                """
            INSERT OR IGNORE INTO camera_settings (
                id,
                room_name,
                camera_index,
                camera_source,
                zoom_link,
                zoom_meeting_id,
                zoom_passcode,
                notes
            )
            VALUES (
                1,
                'Zoom demo darsi',
                -1,
                'screen:1',
                'https://us05web.zoom.us/j/5336068317?pwd=i7Jcq4200iSXNHWvKpqEIW3BVsgAat.1',
                '533 606 8317',
                '1Xkpny',
                'Zoom oynasi asosiy monitorda ochiladi.'
            )
                """
            )
            conn.execute(
                """
            UPDATE camera_settings
            SET
                room_name = 'Zoom demo darsi',
                camera_index = -1,
                camera_source = 'screen:1',
                zoom_link = 'https://us05web.zoom.us/j/5336068317?pwd=i7Jcq4200iSXNHWvKpqEIW3BVsgAat.1',
                zoom_meeting_id = '533 606 8317',
                zoom_passcode = '1Xkpny',
                notes = 'Zoom oynasi asosiy monitorda ochiladi.',
                updated_at = CURRENT_TIMESTAMP
            WHERE id = 1
              AND COALESCE(zoom_link, '') = ''
                """
            )
            conn.execute(
                """
            UPDATE camera_settings
            SET
                room_name = 'Zoom darsi',
                camera_index = -1,
                camera_source = 'screen:1',
                zoom_link = '',
                zoom_meeting_id = '',
                zoom_passcode = '',
                notes = 'Zoom oynasi asosiy monitorda ochiladi.',
                updated_at = CURRENT_TIMESTAMP
            WHERE id = 1
              AND room_name = 'E 102 xona'
              AND camera_source = ''
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
            seed_default_demo_data(conn)
    except sqlite3.Error:
        USE_MEMORY_DB = True


def seed_default_demo_data(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        UPDATE camera_settings
        SET room_name = 'Zoom demo darsi'
        WHERE room_name LIKE '%Boburbek Nuriddinov%'
        """
    )
    conn.execute(
        """
        UPDATE session_participant_results
        SET student_name = 'Talaba 1'
        WHERE student_name = 'Boburbek Nuriddinov'
        """
    )
    conn.execute(
        """
        UPDATE session_participant_results
        SET student_name = 'Talaba 2'
        WHERE student_name = 'Asad'
        """
    )
    conn.execute(
        """
        UPDATE session_participant_results
        SET student_name = 'Talaba 3'
        WHERE student_name = 'Madina'
        """
    )
    conn.execute(
        """
        UPDATE student_latest_results
        SET student_name = 'Talaba 1'
        WHERE student_name = 'Boburbek Nuriddinov'
        """
    )
    conn.execute(
        """
        UPDATE student_latest_results
        SET student_name = 'Talaba 2'
        WHERE student_name = 'Asad'
        """
    )
    conn.execute(
        """
        UPDATE student_latest_results
        SET student_name = 'Talaba 3'
        WHERE student_name = 'Madina'
        """
    )
    existing = conn.execute(
        """
        SELECT COUNT(*) AS total
        FROM session_participant_results
        """
    ).fetchone()
    if existing and int(existing["total"]) > 0:
        return

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
            'Sessiya 1 - Zoom darsi',
            '2026-05-08 14:00:00',
            '2026-05-08 14:45:00',
            2700,
            1250,
            1114,
            2.4,
            3,
            136,
            89.12,
            76.40,
            58.75,
            78.60,
            94.20,
            'Default demo natija'
        )
        """
    )
    session_id = int(cursor.lastrowid)
    rows = [
        ("Talaba 1", 84.5, 94.2, 91.0, 0, 3, 0, 1),
        ("Talaba 2", 76.8, 88.4, 86.5, 1, 1, 0, 2),
        ("Talaba 3", 72.4, 83.0, 78.2, 0, 2, 1, 1),
    ]
    for index, row in enumerate(rows, start=1):
        conn.execute(
            """
            INSERT INTO session_participant_results (
                session_id,
                participant_id,
                student_name,
                average_score,
                max_score,
                presence_ratio,
                frames,
                phone_suspect,
                question_gesture,
                drowsy_suspect,
                looking_away,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, '2026-05-08 14:45:00')
            """,
            (
                session_id,
                f"Tinglovchi {index}",
                row[0],
                row[1],
                row[2],
                row[3],
                380 + (index * 20),
                row[4],
                row[5],
                row[6],
                row[7],
            ),
        )
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
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, '2026-05-08 14:45:00')
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
                row[0],
                session_id,
                f"Tinglovchi {index}",
                row[1],
                row[2],
                row[3],
                row[4],
                row[5],
                row[6],
                row[7],
            ),
        )


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


def save_session_participant_results(session_id: int, participant_summary: list[dict], updated_at: str) -> None:
    rows = [row for row in participant_summary if row.get("assigned_name") or row.get("display_name")]
    if USE_MEMORY_DB:
        global MEMORY_PARTICIPANT_RESULTS
        MEMORY_PARTICIPANT_RESULTS = [
            row for row in MEMORY_PARTICIPANT_RESULTS if row.get("session_id") != session_id
        ]
        for row in rows:
            event_counts = row.get("event_counts", {})
            MEMORY_PARTICIPANT_RESULTS.append(
                {
                    "id": len(MEMORY_PARTICIPANT_RESULTS) + 1,
                    "session_id": session_id,
                    "participant_id": row.get("participant_id", ""),
                    "student_name": row.get("assigned_name") or row.get("display_name", ""),
                    "average_score": row.get("average_score", 0),
                    "max_score": row.get("max_score", 0),
                    "presence_ratio": row.get("presence_ratio", 0),
                    "frames": row.get("frames", 0),
                    "phone_suspect": event_counts.get("phone_suspect", 0),
                    "question_gesture": event_counts.get("question_gesture", 0),
                    "drowsy_suspect": event_counts.get("drowsy_suspect", 0),
                    "looking_away": event_counts.get("looking_away", 0),
                    "updated_at": updated_at,
                }
            )
        return

    with get_connection() as conn:
        conn.execute("DELETE FROM session_participant_results WHERE session_id = ?", (session_id,))
        for row in rows:
            event_counts = row.get("event_counts", {})
            conn.execute(
                """
                INSERT INTO session_participant_results (
                    session_id,
                    participant_id,
                    student_name,
                    average_score,
                    max_score,
                    presence_ratio,
                    frames,
                    phone_suspect,
                    question_gesture,
                    drowsy_suspect,
                    looking_away,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session_id,
                    row.get("participant_id", ""),
                    row.get("assigned_name") or row.get("display_name", ""),
                    row.get("average_score", 0),
                    row.get("max_score", 0),
                    row.get("presence_ratio", 0),
                    row.get("frames", 0),
                    event_counts.get("phone_suspect", 0),
                    event_counts.get("question_gesture", 0),
                    event_counts.get("drowsy_suspect", 0),
                    event_counts.get("looking_away", 0),
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


def fetch_session_by_id(session_id: int) -> dict | None:
    if USE_MEMORY_DB:
        for row in MEMORY_SESSIONS:
            if row.get("id") == session_id:
                return dict(row)
        return None

    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT *
            FROM session_results
            WHERE id = ?
            """,
            (session_id,),
        ).fetchone()
    return dict(row) if row else None


def fetch_session_participant_results(session_id: int) -> list[dict]:
    if USE_MEMORY_DB:
        return [
            dict(row)
            for row in MEMORY_PARTICIPANT_RESULTS
            if row.get("session_id") == session_id
        ]

    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM session_participant_results
            WHERE session_id = ?
            ORDER BY average_score DESC, student_name ASC
            """,
            (session_id,),
        ).fetchall()
    return [dict(row) for row in rows]


def delete_session(session_id: int) -> None:
    if USE_MEMORY_DB:
        global MEMORY_SESSIONS, MEMORY_PARTICIPANT_RESULTS, MEMORY_STUDENT_RESULTS
        MEMORY_SESSIONS = [row for row in MEMORY_SESSIONS if row.get("id") != session_id]
        MEMORY_PARTICIPANT_RESULTS = [
            row for row in MEMORY_PARTICIPANT_RESULTS if row.get("session_id") != session_id
        ]
        MEMORY_STUDENT_RESULTS = [
            row for row in MEMORY_STUDENT_RESULTS if row.get("session_id") != session_id
        ]
        return

    with get_connection() as conn:
        conn.execute("DELETE FROM session_participant_results WHERE session_id = ?", (session_id,))
        conn.execute("DELETE FROM student_latest_results WHERE session_id = ?", (session_id,))
        conn.execute("DELETE FROM session_results WHERE id = ?", (session_id,))


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
        "room_name": "Zoom darsi",
        "camera_index": -1,
        "camera_source": "screen:1",
        "zoom_link": "",
        "zoom_meeting_id": "",
        "zoom_passcode": "",
        "notes": "Zoom oynasi asosiy monitorda ochiladi.",
    }


def save_camera_settings(
    room_name: str,
    camera_index: int,
    camera_source: str = "",
    zoom_link: str = "",
    zoom_meeting_id: str = "",
    zoom_passcode: str = "",
    notes: str = "",
) -> dict:
    room_name = room_name.strip() or "Zoom darsi"
    camera_source = camera_source.strip()
    zoom_link = zoom_link.strip()
    zoom_meeting_id = zoom_meeting_id.strip()
    zoom_passcode = zoom_passcode.strip()
    notes = notes.strip()
    if USE_MEMORY_DB:
        MEMORY_CAMERA_SETTINGS.update(
            {
                "room_name": room_name,
                "camera_index": camera_index,
                "camera_source": camera_source,
                "zoom_link": zoom_link,
                "zoom_meeting_id": zoom_meeting_id,
                "zoom_passcode": zoom_passcode,
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
                zoom_link,
                zoom_meeting_id,
                zoom_passcode,
                notes,
                updated_at
            )
            VALUES (1, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(id) DO UPDATE SET
                room_name=excluded.room_name,
                camera_index=excluded.camera_index,
                camera_source=excluded.camera_source,
                zoom_link=excluded.zoom_link,
                zoom_meeting_id=excluded.zoom_meeting_id,
                zoom_passcode=excluded.zoom_passcode,
                notes=excluded.notes,
                updated_at=CURRENT_TIMESTAMP
            """,
            (room_name, camera_index, camera_source, zoom_link, zoom_meeting_id, zoom_passcode, notes),
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
