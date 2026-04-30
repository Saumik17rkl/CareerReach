-- PostgreSQL initialization script for ReachBridge
-- This script sets up the database with optimized settings

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create indexes for better performance (will be created by SQLAlchemy)
-- These are here for reference and manual optimization if needed

-- Example manual indexes (uncomment if needed for performance tuning)
-- CREATE INDEX IF NOT EXISTS idx_contacts_email ON contacts(email);
-- CREATE INDEX IF NOT EXISTS idx_contacts_mobile ON contacts(mobile);
-- CREATE INDEX IF NOT EXISTS idx_contacts_sheet ON contacts(sheet);
-- CREATE INDEX IF NOT EXISTS idx_contacts_created_at ON contacts(created_at);

-- Set timezone
SET timezone = 'UTC';

-- Grant permissions (adjust as needed)
-- GRANT ALL PRIVILEGES ON DATABASE reachbridge TO reachbridge;
