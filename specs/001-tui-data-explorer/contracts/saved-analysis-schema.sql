-- SavedAnalysis Schema Version 1.0
-- Compatible with: kittiwake >=0.1.0
-- Database: DuckDB >=0.10.0
-- Location: ~/.kittiwake/analyses.db

-- Enable WAL mode for concurrent reads (research.md decision #5)
PRAGMA journal_mode=WAL;

-- Main table for saved analyses
CREATE TABLE IF NOT EXISTS saved_analyses (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    modified_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    operation_count INTEGER NOT NULL CHECK (operation_count >= 0),
    dataset_path TEXT NOT NULL,
    operations JSON NOT NULL  -- See operations-schema.json for structure
);

-- Indices for performance (SC-013: <200ms for 1000 analyses)
CREATE INDEX IF NOT EXISTS idx_saved_analyses_name 
    ON saved_analyses(name);

CREATE INDEX IF NOT EXISTS idx_saved_analyses_created_at 
    ON saved_analyses(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_saved_analyses_modified_at 
    ON saved_analyses(modified_at DESC);

-- Trigger to auto-update modified_at on UPDATE
CREATE OR REPLACE TRIGGER update_saved_analyses_modified_at
    BEFORE UPDATE ON saved_analyses
    FOR EACH ROW
    BEGIN
        UPDATE saved_analyses 
        SET modified_at = CURRENT_TIMESTAMP 
        WHERE id = OLD.id;
    END;

-- Validation: operation_count must match length of operations array
-- Note: DuckDB JSON functions can validate this at query time:
--   SELECT * FROM saved_analyses WHERE operation_count != json_array_length(operations);

-- Example queries for common operations:

-- List all analyses (sorted by most recent)
-- SELECT id, name, description, created_at, modified_at, operation_count, dataset_path
-- FROM saved_analyses
-- ORDER BY modified_at DESC;

-- Get analysis by name
-- SELECT * FROM saved_analyses WHERE name = ?;

-- Search analyses by description
-- SELECT * FROM saved_analyses 
-- WHERE description LIKE '%filter%' 
-- ORDER BY created_at DESC;

-- Count analyses
-- SELECT COUNT(*) FROM saved_analyses;

-- Get analyses for specific dataset
-- SELECT * FROM saved_analyses 
-- WHERE dataset_path = ? 
-- ORDER BY created_at DESC;

---

-- Schema Version Tracking (for future migrations)
CREATE TABLE IF NOT EXISTS schema_version (
    version TEXT PRIMARY KEY,
    applied_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

INSERT OR IGNORE INTO schema_version (version) VALUES ('1.0.0');

---

-- Performance Notes:
-- 1. idx_name enables O(log n) lookup for "load analysis by name" (FR-061)
-- 2. idx_created_at enables fast "list recent analyses" queries
-- 3. idx_modified_at enables "recently modified" sorting in UI
-- 4. WAL mode allows concurrent SELECT while INSERT/UPDATE/DELETE runs
-- 5. JSON column stores operations as array - see operations-schema.json
-- 6. Estimated row size: ~500 bytes (100 bytes metadata + 400 bytes JSON avg)
-- 7. 1000 analyses = ~500KB total, well within DuckDB's performance range

---

-- Maintenance Operations:

-- Vacuum database (optional, for disk space reclamation)
-- VACUUM;

-- Analyze for query optimizer statistics
-- ANALYZE saved_analyses;

-- Check for orphaned operations (operation_count mismatch)
-- SELECT id, name, operation_count, json_array_length(operations) as actual_count
-- FROM saved_analyses
-- WHERE operation_count != json_array_length(operations);

---

-- Backup & Restore:

-- Export all analyses to JSON
-- COPY (SELECT * FROM saved_analyses) TO '/path/to/backup.json' (FORMAT JSON);

-- Import from JSON
-- COPY saved_analyses FROM '/path/to/backup.json' (FORMAT JSON);

-- Export as CSV (for inspection)
-- COPY (SELECT id, name, description, created_at, modified_at, operation_count, dataset_path FROM saved_analyses) 
-- TO '/path/to/analyses.csv' (HEADER, DELIMITER ',');

---

-- Migration Notes:

-- Future schema changes should:
-- 1. Create new version file (e.g., schema-v2.sql)
-- 2. Include ALTER TABLE statements
-- 3. Update schema_version table
-- 4. Maintain backward compatibility for reading v1.0 data

-- Example future migration (NOT in v1.0):
-- ALTER TABLE saved_analyses ADD COLUMN tags JSON DEFAULT '[]';
-- INSERT INTO schema_version (version) VALUES ('1.1.0');
