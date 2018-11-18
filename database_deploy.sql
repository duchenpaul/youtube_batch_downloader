--
-- 
--
-- Text encoding used: System
--
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

-- Table: download_status
CREATE TABLE download_status (
    id            INTEGER,
    video_name    TEXT,
    resolution    TEXT,
    size          DOUBLE,
    status        TEXT,
    download_link TEXT,
    original_link TEXT
);


COMMIT TRANSACTION;
PRAGMA foreign_keys = on;
