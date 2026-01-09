-- SavedAnalysis DuckDB Schema
-- Database: ~/.kittiwake/analyses.db
-- Version: 1.0
-- Created: 2026-01-09

CREATE TABLE IF NOT EXISTS saved_analyses (
    -- Primary key
    id INTEGER PRIMARY KEY,
    
    -- User-facing metadata
    name TEXT NOT NULL UNIQUE,  -- Analysis name (must be unique)
    description TEXT,            -- Optional description
    
    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    modified_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Analysis metrics
    operation_count INTEGER NOT NULL CHECK (operation_count >= 1 AND operation_count <= 1000),
    
    -- Dataset reference
    dataset_path TEXT NOT NULL,  -- Original dataset file path or URL
    
    -- Operations sequence (JSON array)
    operations JSON NOT NULL
);

-- Indexes for performance (SC-013: <200ms for 1000 analyses)
CREATE INDEX IF NOT EXISTS idx_analyses_name ON saved_analyses(name);
CREATE INDEX IF NOT EXISTS idx_analyses_created_at ON saved_analyses(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_analyses_modified_at ON saved_analyses(modified_at DESC);

-- Example operations JSON structure:
-- [
--   {
--     "operation_type": "filter",
--     "params": {"column": "age", "operator": ">", "value": 25},
--     "display": "Filter: age > 25"
--   },
--   {
--     "operation_type": "aggregate",
--     "params": {
--       "group_by_cols": ["category"],
--       "agg_col": "sales",
--       "agg_func": "sum"
--     },
--     "display": "Aggregate: sum(sales) by category"
--   }
-- ]

-- Validation constraints:
-- 1. name: 1-100 characters, no path separators (/, \)
-- 2. description: max 500 characters
-- 3. operation_count: 1-1000 operations
-- 4. operations: valid JSON array of operation objects
