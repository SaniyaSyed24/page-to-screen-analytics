PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS books (
    book_id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    author TEXT,
    publication_year INTEGER,
    genre TEXT,
    book_source_url TEXT NOT NULL,
    UNIQUE(title, author, publication_year)
);

CREATE TABLE IF NOT EXISTS tv_shows (
    show_id INTEGER PRIMARY KEY,
    title TEXT NOT NULL UNIQUE,
    first_release_year INTEGER,
    end_year INTEGER,
    episode_count INTEGER,
    tv_source_url TEXT NOT NULL,
    CHECK(first_release_year IS NULL OR first_release_year BETWEEN 1900 AND 2100),
    CHECK(end_year IS NULL OR end_year BETWEEN 1900 AND 2100),
    CHECK(episode_count IS NULL OR episode_count >= 0),
    CHECK(end_year IS NULL OR first_release_year IS NULL OR end_year >= first_release_year)
);

CREATE TABLE IF NOT EXISTS adaptations (
    adaptation_id INTEGER PRIMARY KEY,
    book_id INTEGER NOT NULL REFERENCES books(book_id),
    show_id INTEGER NOT NULL REFERENCES tv_shows(show_id),
    relationship_source_url TEXT NOT NULL,
    UNIQUE(book_id, show_id)
);

CREATE TABLE IF NOT EXISTS platforms (
    platform_id INTEGER PRIMARY KEY,
    platform_name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS show_platforms (
    show_id INTEGER NOT NULL REFERENCES tv_shows(show_id),
    platform_id INTEGER NOT NULL REFERENCES platforms(platform_id),
    PRIMARY KEY(show_id, platform_id)
);

CREATE INDEX IF NOT EXISTS idx_books_genre ON books(genre);
CREATE INDEX IF NOT EXISTS idx_books_publication_year ON books(publication_year);
CREATE INDEX IF NOT EXISTS idx_shows_first_release_year ON tv_shows(first_release_year);
CREATE INDEX IF NOT EXISTS idx_adaptations_book_id ON adaptations(book_id);
CREATE INDEX IF NOT EXISTS idx_adaptations_show_id ON adaptations(show_id);
