"""
services/sources_service.py

Manages the trusted_sources table in PostgreSQL.

Table schema (run once in psql):

    CREATE TABLE trusted_sources (
        id         SERIAL PRIMARY KEY,
        name       VARCHAR(200) NOT NULL,
        domain     VARCHAR(200) NOT NULL UNIQUE,
        category   VARCHAR(50)  NOT NULL DEFAULT 'news',
        added_at   TIMESTAMP    NOT NULL DEFAULT NOW()
    );

Connection is read from the DATABASE_URL environment variable.
Format: postgresql://user:password@host:port/dbname
"""

import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv()

def _get_conn():
    """Open and return a database connection."""
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL not set in .env file.")
    return psycopg2.connect(url)


def get_all() -> list[dict]:
    conn = _get_conn()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT * FROM trusted_sources ORDER BY added_at DESC;")
            return [dict(row) for row in cur.fetchall()]
    finally:
        conn.close()


def create(name: str, domain: str, category: str) -> dict:
    conn = _get_conn()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                """
                INSERT INTO trusted_sources (name, domain, category)
                VALUES (%s, %s, %s)
                RETURNING *;
                """,
                (name, domain, category),
            )
            conn.commit()
            return dict(cur.fetchone())
    finally:
        conn.close()


def delete(source_id: int) -> bool:
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM trusted_sources WHERE id = %s RETURNING id;",
                (source_id,),
            )
            conn.commit()
            return cur.fetchone() is not None
    finally:
        conn.close()
