CREATE TABLE IF NOT EXISTS file_metadata (
    id INTEGER PRIMARY KEY,
    file_path TEXT UNIQUE,
    file_name TEXT,
    file_size INTEGER,
    file_sha256 TEXT,
    created TEXT,
    modified TEXT,
    embedding BLOB
);