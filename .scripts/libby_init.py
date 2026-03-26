#!/usr/bin/env python3
# libby_init.py — Libby's database and folder bootstrapper
# Idempotent — safe to run multiple times.

import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent  # .scripts/ → PKA/
DB_PATH  = BASE_DIR / "data" / "pka.db"

FOLDERS = [
    BASE_DIR / "data",
    BASE_DIR / "Library" / "Inbox",
    BASE_DIR / "Library" / "documents",
    BASE_DIR / "Library" / "exports",
    BASE_DIR / "Library" / "index",
]

SCHEMA = [
    (
        "documents",
        """
        CREATE TABLE IF NOT EXISTS documents (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            title       TEXT,
            filename    TEXT UNIQUE,
            content     TEXT,
            summary     TEXT,
            tags        TEXT,
            source_path TEXT,
            status      TEXT DEFAULT 'queued',
            created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """,
    ),
    (
        "contacts",
        """
        CREATE TABLE IF NOT EXISTS contacts (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            name       TEXT NOT NULL,
            company    TEXT,
            role       TEXT,
            email      TEXT,
            phone      TEXT,
            notes      TEXT,
            tags       TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """,
    ),
    (
        "interactions",
        """
        CREATE TABLE IF NOT EXISTS interactions (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            contact_id INTEGER REFERENCES contacts(id),
            type       TEXT,
            summary    TEXT,
            date       DATETIME,
            agent_id   TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """,
    ),
    (
        "projects",
        """
        CREATE TABLE IF NOT EXISTS projects (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            title       TEXT NOT NULL,
            status      TEXT DEFAULT 'active',
            description TEXT,
            owner_agent TEXT,
            due_date    DATE,
            created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """,
    ),
    (
        "tasks",
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id   INTEGER REFERENCES projects(id),
            title        TEXT NOT NULL,
            status       TEXT DEFAULT 'open',
            assigned_to  TEXT,
            priority     TEXT DEFAULT 'normal',
            due_date     DATE,
            completed_at DATETIME,
            created_at   DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """,
    ),
    (
        "journal_entries",
        """
        CREATE TABLE IF NOT EXISTS journal_entries (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            type       TEXT,
            title      TEXT,
            content    TEXT,
            tags       TEXT,
            date       DATE,
            agent_id   TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """,
    ),
    (
        "agent_work_log",
        """
        CREATE TABLE IF NOT EXISTS agent_work_log (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id       TEXT NOT NULL,
            task_ref       TEXT,
            action         TEXT,
            input_summary  TEXT,
            output_summary TEXT,
            status         TEXT,
            timestamp      DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """,
    ),
    (
        "tags",
        """
        CREATE TABLE IF NOT EXISTS tags (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            name       TEXT UNIQUE NOT NULL,
            category   TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """,
    ),
    (
        "entity_links",
        """
        CREATE TABLE IF NOT EXISTS entity_links (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            source_type  TEXT NOT NULL,
            source_id    INTEGER NOT NULL,
            target_type  TEXT NOT NULL,
            target_id    INTEGER NOT NULL,
            relationship TEXT,
            created_at   DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """,
    ),
    (
        "documents_fts (FTS5)",
        """
        CREATE VIRTUAL TABLE IF NOT EXISTS documents_fts
        USING fts5(title, content, summary, tags, content=documents, content_rowid=id)
        """,
    ),
]


def main():
    print("[Libby Init] Starting...")

    # Create folders
    for folder in FOLDERS:
        folder.mkdir(parents=True, exist_ok=True)
        print(f"[Libby Init] ✓ Folder: {folder.relative_to(BASE_DIR)}")

    # Create / migrate database
    conn = sqlite3.connect(DB_PATH)
    try:
        for name, ddl in SCHEMA:
            conn.execute(ddl)
            print(f"[Libby Init] ✓ Table: {name}")
        conn.commit()
    finally:
        conn.close()

    print(f"[Libby Init] ✓ Database: {DB_PATH.relative_to(BASE_DIR)}")
    print("[Libby Init] Done — pka.db is ready.")


if __name__ == "__main__":
    main()
