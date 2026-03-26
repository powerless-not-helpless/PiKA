#!/usr/bin/env python3
# libby_watch.py — Libby's Inbox watchdog
# Monitors ./Library/Inbox/ and triggers ingestion on new file drops

import time
import sqlite3
import shutil
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# --- Paths ---
BASE_DIR = Path(__file__).parent.parent  # .scripts/ → PKA/
INBOX_DIR   = BASE_DIR / "Library" / "Inbox"
DOCS_DIR    = BASE_DIR / "Library" / "documents"
DB_PATH     = BASE_DIR / "data" / "pka.db"

# --- DB Setup ---
def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
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
    """)
    conn.commit()
    conn.close()

# --- Ingest a single file ---
def ingest_file(filepath: Path):
    filename = filepath.name

    conn = sqlite3.connect(DB_PATH)

    # Check if already queued/processing/done
    existing = conn.execute(
        "SELECT status FROM documents WHERE filename = ?", (filename,)
    ).fetchone()

    if existing:
        print(f"[Libby] Skipping {filename} — already {existing[0]}")
        conn.close()
        return

    # Lock it immediately
    conn.execute("""
        INSERT INTO documents (title, filename, status, source_path)
        VALUES (?, ?, 'processing', ?)
    """, (filepath.stem, filename, str(filepath)))
    conn.commit()

    try:
        # Read content (text files for now)
        content = ""
        if filepath.suffix in [".txt", ".md"]:
            content = filepath.read_text(encoding="utf-8", errors="ignore")
        else:
            content = f"[Binary file — {filepath.suffix} — manual review needed]"

        # Move to documents/
        dest = DOCS_DIR / filename
        shutil.move(str(filepath), str(dest))

        # Update record
        conn.execute("""
            UPDATE documents
            SET content = ?, status = 'done', source_path = ?, updated_at = CURRENT_TIMESTAMP
            WHERE filename = ?
        """, (content, str(dest), filename))
        conn.commit()

        print(f"[Libby] Ingested: {filename} → Library/documents/")

    except Exception as e:
        conn.execute("""
            UPDATE documents SET status = 'failed', updated_at = CURRENT_TIMESTAMP
            WHERE filename = ?
        """, (filename,))
        conn.commit()
        print(f"[Libby] Failed: {filename} — {e}")

    finally:
        conn.close()

# --- Watchdog Handler ---
class InboxHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        filepath = Path(event.src_path)
        # Ignore hidden files and lockfiles
        if filepath.name.startswith(".") or filepath.suffix == ".lock":
            return
        print(f"[Libby] Detected: {filepath.name}")
        time.sleep(0.5)  # brief pause — let the file finish writing
        ingest_file(filepath)

# --- Stale lock recovery ---
def recover_stale():
    conn = sqlite3.connect(DB_PATH)
    stale = conn.execute("""
        SELECT filename FROM documents
        WHERE status = 'processing'
        AND updated_at < datetime('now', '-10 minutes')
    """).fetchall()
    for (filename,) in stale:
        print(f"[Libby] Recovering stale: {filename}")
        conn.execute("""
            UPDATE documents SET status = 'queued', updated_at = CURRENT_TIMESTAMP
            WHERE filename = ?
        """, (filename,))
    conn.commit()
    conn.close()

# --- Main ---
if __name__ == "__main__":
    # Ensure dirs exist
    INBOX_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    init_db()
    recover_stale()

    handler = InboxHandler()
    observer = Observer()
    observer.schedule(handler, path=str(INBOX_DIR), recursive=False)
    observer.start()

    print(f"[Libby] Watching {INBOX_DIR} — ready.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("[Libby] Watchdog stopped.")

    observer.join()  
