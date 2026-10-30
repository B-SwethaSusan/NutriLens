"""One-time fix: clears the stale per-account llm_model override saved in
the database before the multi-provider fix (it was hardcoded to
"mistral-small-latest" the first time each account used Chat/Diet Plan/
Settings, and that stored value kept being passed to whichever provider is
now active, including Gemini, which doesn't recognize Mistral's model
names).

The Python model (app/models/entities.py) now allows this column to be
NULL, but on SQLite that change doesn't retroactively alter a table that
already exists on disk — the column there still physically has a NOT NULL
constraint from before, so just writing None to it fails with
"IntegrityError: NOT NULL constraint failed". This script rebuilds the
user_settings table (SQLite) or drops the constraint directly (Postgres)
before clearing the values. Safe to run multiple times.

Usage:
    cd backend
    python scripts/reset_llm_model_override.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import text  # noqa: E402

from app.database.session import SessionLocal, engine  # noqa: E402

db = SessionLocal()
try:
    if engine.dialect.name == "sqlite":
        print("SQLite detected — rebuilding user_settings with a nullable llm_model column...")
        rows = db.execute(text("SELECT id, owner_id, chunk_size, chunk_overlap, top_k, temperature, embedding_model FROM user_settings")).fetchall()
        db.execute(text("ALTER TABLE user_settings RENAME TO user_settings_old"))
        db.execute(text(
            """
            CREATE TABLE user_settings (
                id VARCHAR(36) NOT NULL PRIMARY KEY,
                owner_id VARCHAR(36) NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
                chunk_size INTEGER NOT NULL,
                chunk_overlap INTEGER NOT NULL,
                top_k INTEGER NOT NULL,
                temperature FLOAT NOT NULL,
                llm_model VARCHAR(120),
                embedding_model VARCHAR(160) NOT NULL
            )
            """
        ))
        for row in rows:
            db.execute(
                text(
                    "INSERT INTO user_settings (id, owner_id, chunk_size, chunk_overlap, top_k, temperature, llm_model, embedding_model) "
                    "VALUES (:id, :owner_id, :chunk_size, :chunk_overlap, :top_k, :temperature, NULL, :embedding_model)"
                ),
                dict(row._mapping),
            )
        db.execute(text("DROP TABLE user_settings_old"))
        db.commit()
        print(f"Done. Rebuilt table, migrated {len(rows)} row(s), llm_model cleared on all of them.")
    else:
        print("Postgres detected — dropping the NOT NULL constraint and clearing stored values...")
        db.execute(text("ALTER TABLE user_settings ALTER COLUMN llm_model DROP NOT NULL"))
        result = db.execute(text("UPDATE user_settings SET llm_model = NULL WHERE llm_model IS NOT NULL"))
        db.commit()
        print(f"Done. {result.rowcount} row(s) updated.")
finally:
    db.close()
