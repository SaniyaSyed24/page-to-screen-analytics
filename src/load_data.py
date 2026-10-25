from __future__ import annotations

import sqlite3
from pathlib import Path
from urllib.parse import urlparse

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data" / "adaptations.csv"
DB_PATH = ROOT / "page_to_screen.db"
SCHEMA_PATH = ROOT / "sql" / "schema.sql"

REQUIRED = [
    "book_title", "tv_title", "book_source_url",
    "tv_source_url", "relationship_source_url",
]
OPTIONAL = [
    "author", "publication_year", "genre", "first_release_year",
    "end_year", "episode_count", "platform",
]
ALL_COLUMNS = REQUIRED + OPTIONAL


def optional_text(value):
    if pd.isna(value) or not str(value).strip():
        return None
    return str(value).strip()


def optional_int(value, field, row_num):
    if pd.isna(value) or not str(value).strip():
        return None
    try:
        number = float(str(value).strip())
        if not number.is_integer():
            raise ValueError
        return int(number)
    except (ValueError, TypeError):
        raise ValueError(f"Row {row_num}: {field} must be a whole number or blank.")


def valid_url(value):
    if pd.isna(value) or not str(value).strip():
        return False
    parsed = urlparse(str(value).strip())
    return parsed.scheme in ("http", "https") and bool(parsed.netloc)


def main():
    df = pd.read_csv(CSV_PATH, dtype=str)
    missing_cols = [col for col in ALL_COLUMNS if col not in df.columns]
    if missing_cols:
        raise ValueError(f"CSV is missing columns: {missing_cols}")

    errors = []
    seen = set()
    for idx, row in df.iterrows():
        row_num = idx + 2
        for col in REQUIRED:
            if pd.isna(row[col]) or not str(row[col]).strip():
                errors.append(f"Row {row_num}: {col} is required.")
        for col in ("book_source_url", "tv_source_url", "relationship_source_url"):
            if not valid_url(row[col]):
                errors.append(f"Row {row_num}: {col} must be an http(s) URL.")

        key = (
            str(row["book_title"]).strip().casefold(),
            str(row["tv_title"]).strip().casefold(),
            optional_text(row["author"]) or "",
        )
        if key in seen:
            errors.append(f"Row {row_num}: duplicate book/show/author combination.")
        seen.add(key)

        for col in ("publication_year", "first_release_year", "end_year", "episode_count"):
            try:
                value = optional_int(row[col], col, row_num)
                if value is not None:
                    if col == "episode_count" and value < 0:
                        errors.append(f"Row {row_num}: episode_count cannot be negative.")
                    if col != "episode_count" and not 1000 <= value <= 2100:
                        errors.append(f"Row {row_num}: {col} outside supported range 1000–2100.")
            except ValueError as exc:
                errors.append(str(exc))

    if errors:
        print("Validation failed:")
        for error in errors:
            print(f" - {error}")
        raise SystemExit(1)

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        # Rebuild derived tables from the CSV. This affects only this project's DB.
        conn.executescript("""
            DELETE FROM show_platforms;
            DELETE FROM adaptations;
            DELETE FROM platforms;
            DELETE FROM tv_shows;
            DELETE FROM books;
        """)

        for idx, row in df.iterrows():
            row_num = idx + 2
            pub_year = optional_int(row["publication_year"], "publication_year", row_num)
            release_year = optional_int(row["first_release_year"], "first_release_year", row_num)
            end_year = optional_int(row["end_year"], "end_year", row_num)
            episodes = optional_int(row["episode_count"], "episode_count", row_num)

            book_title = str(row["book_title"]).strip()
            author = optional_text(row["author"])
            conn.execute(
                """INSERT OR IGNORE INTO books
                   (title, author, publication_year, genre, book_source_url)
                   VALUES (?, ?, ?, ?, ?)""",
                (book_title, author, pub_year, optional_text(row["genre"]),
                 str(row["book_source_url"]).strip()),
            )
            book_id = conn.execute(
                """SELECT book_id FROM books
                   WHERE title = ? AND author IS ? AND publication_year IS ?""",
                (book_title, author, pub_year),
            ).fetchone()[0]

            show_title = str(row["tv_title"]).strip()
            conn.execute(
                """INSERT OR IGNORE INTO tv_shows
                   (title, first_release_year, end_year, episode_count, tv_source_url)
                   VALUES (?, ?, ?, ?, ?)""",
                (show_title, release_year, end_year, episodes,
                 str(row["tv_source_url"]).strip()),
            )
            show_id = conn.execute(
                "SELECT show_id FROM tv_shows WHERE title = ?", (show_title,)
            ).fetchone()[0]

            conn.execute(
                """INSERT OR IGNORE INTO adaptations
                   (book_id, show_id, relationship_source_url)
                   VALUES (?, ?, ?)""",
                (book_id, show_id, str(row["relationship_source_url"]).strip()),
            )

            platform = optional_text(row["platform"])
            if platform:
                conn.execute(
                    "INSERT OR IGNORE INTO platforms (platform_name) VALUES (?)",
                    (platform,),
                )
                platform_id = conn.execute(
                    "SELECT platform_id FROM platforms WHERE platform_name = ?",
                    (platform,),
                ).fetchone()[0]
                conn.execute(
                    "INSERT OR IGNORE INTO show_platforms (show_id, platform_id) VALUES (?, ?)",
                    (show_id, platform_id),
                )

        counts = {
            table: conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            for table in ("books", "tv_shows", "adaptations", "platforms")
        }

    print(f"Database created: {DB_PATH}")
    for table, count in counts.items():
        print(f"{table}: {count}")
    if not counts["adaptations"]:
        print("No sourced adaptation records yet; add rows to data/adaptations.csv.")


if __name__ == "__main__":
    main()
