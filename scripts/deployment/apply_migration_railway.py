#!/usr/bin/env python3
"""
Apply investigations table migration to Railway PostgreSQL
"""
import sys

import psycopg2

# Railway PostgreSQL connection
DATABASE_URL = "postgresql://postgres:ymDpsVmsGYUCTVSNHJXVnHszSAKHCevH@centerbeam.proxy.rlwy.net:38094/railway"

SQL_MIGRATION = """
-- Create investigations table
CREATE TABLE IF NOT EXISTS investigations (
    id VARCHAR(36) PRIMARY KEY,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),

    -- User identification
    user_id VARCHAR(255) NOT NULL,
    session_id VARCHAR(255),

    -- Investigation details
    query TEXT NOT NULL,
    data_source VARCHAR(100) NOT NULL,

    -- Status tracking
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    current_phase VARCHAR(100),
    progress FLOAT DEFAULT 0.0,

    -- Results summary
    anomalies_found INTEGER DEFAULT 0,
    total_records_analyzed INTEGER DEFAULT 0,
    confidence_score FLOAT,

    -- JSON data (PostgreSQL JSONB)
    filters JSONB DEFAULT '{}'::jsonb,
    anomaly_types JSONB DEFAULT '[]'::jsonb,
    results JSONB DEFAULT '[]'::jsonb,
    investigation_metadata JSONB DEFAULT '{}'::jsonb,

    -- Text fields
    summary TEXT,
    error_message TEXT,

    -- Timing
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    processing_time_ms INTEGER
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_investigations_user_id ON investigations(user_id);
CREATE INDEX IF NOT EXISTS idx_investigations_session_id ON investigations(session_id);
CREATE INDEX IF NOT EXISTS idx_investigations_data_source ON investigations(data_source);
CREATE INDEX IF NOT EXISTS idx_investigations_status ON investigations(status);
CREATE INDEX IF NOT EXISTS idx_investigations_user_status ON investigations(user_id, status);
CREATE INDEX IF NOT EXISTS idx_investigations_created_at ON investigations(created_at);

-- Create alembic_version table if it doesn't exist
CREATE TABLE IF NOT EXISTS alembic_version (
    version_num VARCHAR(32) NOT NULL,
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

-- Record this migration
INSERT INTO alembic_version (version_num) VALUES ('0dba430d74c4')
ON CONFLICT (version_num) DO NOTHING;
"""


def main():
    print("=" * 80)
    print("Applying Migration to Railway PostgreSQL")
    print("=" * 80)
    print()

    try:
        # Connect to Railway PostgreSQL
        print("🔌 Connecting to Railway PostgreSQL...")
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = True
        cursor = conn.cursor()
        print("✅ Connected successfully!")
        print()

        # Execute migration
        print("🚀 Executing migration...")
        cursor.execute(SQL_MIGRATION)
        print("✅ Migration executed successfully!")
        print()

        # Verify table exists
        print("🔍 Verifying table creation...")
        cursor.execute(
            """
            SELECT COUNT(*) FROM information_schema.tables
            WHERE table_name = 'investigations'
        """
        )
        count = cursor.fetchone()[0]
        if count == 1:
            print("✅ Table 'investigations' exists!")
        else:
            print("❌ Table 'investigations' NOT found!")
            return 1
        print()

        # Count indexes
        print("🔍 Verifying indexes...")
        cursor.execute(
            """
            SELECT COUNT(*) FROM pg_indexes
            WHERE tablename = 'investigations'
        """
        )
        index_count = cursor.fetchone()[0]
        print(f"✅ {index_count} indexes created")
        print()

        # List indexes
        cursor.execute(
            """
            SELECT indexname FROM pg_indexes
            WHERE tablename = 'investigations'
            ORDER BY indexname
        """
        )
        indexes = cursor.fetchall()
        print("📋 Indexes:")
        for idx in indexes:
            print(f"   - {idx[0]}")
        print()

        # Verify alembic version
        print("🔍 Verifying Alembic version...")
        cursor.execute("SELECT version_num FROM alembic_version")
        version = cursor.fetchone()
        if version:
            print(f"✅ Alembic version: {version[0]}")
        else:
            print("❌ Alembic version NOT found!")
            return 1
        print()

        # Count records (should be 0)
        print("🔍 Counting records...")
        cursor.execute("SELECT COUNT(*) FROM investigations")
        record_count = cursor.fetchone()[0]
        print(f"✅ Current records: {record_count}")
        print()

        cursor.close()
        conn.close()

        print("=" * 80)
        print("✅ MIGRATION COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        print()
        print("Next steps:")
        print("1. Run: python test_production_chat.py")
        print("2. Verify Zumbi returns real data (not R$ 0.00)")
        print("3. Check Railway logs for any errors")
        print()

        return 0

    except Exception as e:
        print()
        print("=" * 80)
        print("❌ MIGRATION FAILED!")
        print("=" * 80)
        print()
        print(f"Error: {e}")
        print()
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
