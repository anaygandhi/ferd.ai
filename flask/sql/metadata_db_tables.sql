
/** file_metadata - table that contains the embeddings for each unique file path, along with other metadata. */ 
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

/** ignore_paths - table that defines which paths can be ignored when indexing. The "type" must be either "file" or "directory",
 * and wildcards are supported in the "path" */
CREATE TABLE IF NOT EXISTS ignore_paths (
    path TEXT PRIMARY KEY,
    type TEXT CHECK(type IN ('file', 'directory')) NOT NULL
);


/** Insert default values into ignore_paths table */
INSERT INTO ignore_paths (path, type) VALUES ('*/.*', 'directory')  -- Ignore hidden directories 
