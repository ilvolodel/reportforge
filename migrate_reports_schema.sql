-- Migration: Drop old reports tables and let SQLAlchemy recreate them
-- Date: 2026-01-09
-- Reason: Reports schema was completely redesigned with snapshots, templates, and versioning

-- Drop old tables in correct order (respecting foreign keys)
DROP TABLE IF EXISTS report_versions CASCADE;
DROP TABLE IF EXISTS report_executive_summary CASCADE;
DROP TABLE IF EXISTS report_project_snapshots CASCADE;
DROP TABLE IF EXISTS report_templates CASCADE;
DROP TABLE IF EXISTS reports CASCADE;

-- Tables will be recreated by SQLAlchemy on next backend startup
