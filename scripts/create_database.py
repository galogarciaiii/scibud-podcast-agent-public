import sqlite3
from typing import Optional


def create_database() -> None:
    conn: Optional[sqlite3.Connection] = None
    try:
        conn = sqlite3.connect("podcast.db")
        cursor: sqlite3.Cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS episodes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                description TEXT,
                citations TEXT,
                persona TEXT,
                voice TEXT,
                script TEXT,
                season INTEGER,
                episode INTEGER,
                episode_type TEXT,
                pub_date TEXT,
                post TEXT,
                guid TEXT UNIQUE,
                file_size INTEGER
            );
        """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL UNIQUE,  -- Enforce title uniqueness
            authors TEXT,
            doi TEXT,
            abstract TEXT,
            full_text TEXT,
            submitted_date TEXT,
            url TEXT,
            full_text_locator TEXT,
            strategy TEXT,
            score INTEGER DEFAULT -1,
            score_justification TEXT,
            score_generated BOOLEAN DEFAULT 0,
            full_text_available BOOLEAN DEFAULT 0,
            described_in_podcast BOOLEAN DEFAULT 0
            );
        """
        )

        conn.commit()

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")

    finally:
        if conn is not None:
            conn.close()


if __name__ == "__main__":
    create_database()
