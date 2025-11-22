# Database Backup & Recovery Strategy

**Version**: 1.0.0
**Last Updated**: 2025-01-24
**Owner**: DevOps Team
**Status**: Production

---

## Overview

This document defines the backup, recovery, and disaster recovery strategies for the Cidadão.AI backend database infrastructure.

## Infrastructure Summary

| Component | Technology | Environment | Backup Responsibility |
|-----------|------------|-------------|----------------------|
| **PostgreSQL** | Railway managed | Production | Railway automated + Manual |
| **Redis** | Railway managed | Production | RDB + AOF persistence |
| **SQLite** | Local file | Development | Git ignored (ephemeral) |

---

## PostgreSQL Backup Strategy

### Automated Backups (Railway)

Railway provides **automated daily backups** for PostgreSQL databases:

```yaml
Schedule: Daily at 03:00 UTC
Retention: 7 days (free tier) / 30 days (paid tier)
Location: Railway infrastructure (encrypted)
Recovery: Railway dashboard or CLI
```

#### Verify Automated Backups

```bash
# Check backup status via Railway CLI
railway status --service postgresql

# List available backups
railway backups list --database <database-id>

# Restore from backup
railway backups restore --database <database-id> --backup <backup-id>
```

### Manual Backup Strategy

**Frequency**: Weekly (Sundays at 02:00 UTC)
**Retention**: 30 days
**Storage**: External S3-compatible storage (Supabase Storage)

#### Manual Backup Script

```bash
#!/bin/bash
# scripts/backup/postgresql_backup.sh

set -e

# Configuration
BACKUP_DIR="/tmp/cidadao-ai-backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="cidadao_ai_pg_${TIMESTAMP}.sql.gz"
S3_BUCKET="cidadao-ai-backups"

# Get DATABASE_URL from Railway
export DATABASE_URL=$(railway variables get DATABASE_URL --service postgresql)

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Dump database with compression
echo "Creating PostgreSQL backup..."
pg_dump "$DATABASE_URL" | gzip > "$BACKUP_DIR/$BACKUP_FILE"

# Upload to S3-compatible storage (Supabase)
echo "Uploading to Supabase Storage..."
supabase storage upload backups "$BACKUP_DIR/$BACKUP_FILE"

# Verify backup integrity
echo "Verifying backup integrity..."
gzip -t "$BACKUP_DIR/$BACKUP_FILE"

# Cleanup local backup (keep only last 3)
cd "$BACKUP_DIR"
ls -t cidadao_ai_pg_*.sql.gz | tail -n +4 | xargs rm -f

echo "Backup completed: $BACKUP_FILE"
echo "Size: $(du -h "$BACKUP_DIR/$BACKUP_FILE" | cut -f1)"
```

#### Setup Automated Backups (Cron)

```bash
# Add to crontab
0 2 * * 0 /path/to/scripts/backup/postgresql_backup.sh >> /var/log/cidadao-ai-backup.log 2>&1
```

### Critical Data Exports

**Investigations**: Export to JSON daily

```sql
-- Export investigations to JSON
COPY (
    SELECT row_to_json(t)
    FROM (
        SELECT id, query, status, results, metadata, created_at
        FROM investigations
        WHERE created_at >= NOW() - INTERVAL '7 days'
    ) t
) TO '/tmp/investigations_backup.json';
```

**Agents Metadata**: Export weekly

```sql
-- Export agent pool state
COPY (
    SELECT * FROM agent_instances
) TO '/tmp/agent_instances_backup.csv' CSV HEADER;
```

---

## Redis Backup Strategy

### RDB Persistence (Snapshots)

Redis automatically creates point-in-time snapshots:

```redis
# redis.conf configuration (Railway default)
save 900 1        # Save if 1 key changed in 15 minutes
save 300 10       # Save if 10 keys changed in 5 minutes
save 60 10000     # Save if 10000 keys changed in 1 minute

dbfilename dump.rdb
dir /var/lib/redis
```

#### Manual RDB Snapshot

```bash
# Trigger immediate snapshot
redis-cli BGSAVE

# Check last save time
redis-cli LASTSAVE
```

### AOF (Append-Only File) Persistence

For critical cache data, enable AOF:

```redis
# Append-Only File for durability
appendonly yes
appendfilename "appendonly.aof"
appendfsync everysec  # Fsync every second (good compromise)
```

#### Backup Redis Data

```bash
#!/bin/bash
# scripts/backup/redis_backup.sh

REDIS_URL=$(railway variables get REDIS_URL --service redis)
BACKUP_DIR="/tmp/cidadao-ai-redis-backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p "$BACKUP_DIR"

# Trigger snapshot
redis-cli -u "$REDIS_URL" BGSAVE

# Wait for snapshot to complete
while [ $(redis-cli -u "$REDIS_URL" LASTSAVE) == $(redis-cli -u "$REDIS_URL" LASTSAVE) ]; do
    sleep 1
done

# Copy RDB file
scp railway:/var/lib/redis/dump.rdb "$BACKUP_DIR/dump_${TIMESTAMP}.rdb"

echo "Redis backup completed: dump_${TIMESTAMP}.rdb"
```

---

## Recovery Procedures

### PostgreSQL Recovery

#### Scenario 1: Data Corruption (Last Hour)

```bash
# 1. Stop application
railway down --service backend

# 2. Restore from latest Railway backup
railway backups restore --database <db-id> --backup latest

# 3. Verify data integrity
railway run --service postgresql psql -c "SELECT COUNT(*) FROM investigations;"

# 4. Restart application
railway up --service backend
```

#### Scenario 2: Accidental DELETE (Need Point-in-Time)

```bash
# 1. Identify backup before deletion
railway backups list --database <db-id>

# 2. Restore to temporary database
railway backups restore --database <db-id> --backup <backup-before-delete> --new-database temp_recovery

# 3. Export affected records
pg_dump -t investigations temp_recovery > recovery.sql

# 4. Import to production
psql "$DATABASE_URL" < recovery.sql

# 5. Drop temporary database
dropdb temp_recovery
```

#### Scenario 3: Complete Database Loss

```bash
# 1. Provision new PostgreSQL on Railway
railway provision postgresql

# 2. Restore from external backup (S3)
wget https://supabase-storage/backups/cidadao_ai_pg_latest.sql.gz
gunzip cidadao_ai_pg_latest.sql.gz

# 3. Import to new database
psql "$NEW_DATABASE_URL" < cidadao_ai_pg_latest.sql

# 4. Run migrations to latest
railway run --service backend alembic upgrade head

# 5. Verify data
railway run --service backend python scripts/verify_database.py

# 6. Update DATABASE_URL in Railway
railway variables set DATABASE_URL="$NEW_DATABASE_URL"
```

### Redis Recovery

#### Scenario 1: Cache Invalidation

```bash
# Simply flush cache (will rebuild)
redis-cli -u "$REDIS_URL" FLUSHALL

# Application will repopulate cache automatically
```

#### Scenario 2: Redis Instance Loss

```bash
# 1. Provision new Redis
railway provision redis

# 2. Restore from RDB backup (if needed)
scp dump_latest.rdb railway:/var/lib/redis/dump.rdb

# 3. Restart Redis
railway restart --service redis

# 4. Update REDIS_URL
railway variables set REDIS_URL="$NEW_REDIS_URL"
```

---

## Monitoring & Alerts

### Backup Health Checks

```yaml
# monitoring/backup_health.yml
alerts:
  - name: PostgreSQL Backup Failed
    condition: backup_age_hours > 48
    severity: critical
    action: Notify DevOps via Slack

  - name: Backup Size Anomaly
    condition: backup_size_deviation > 50%
    severity: warning
    action: Log for manual review

  - name: Redis Persistence Disabled
    condition: redis_rdb_last_save_age > 3600
    severity: high
    action: Check Redis configuration
```

### Automated Testing

```bash
# scripts/backup/test_restore.sh
# Run monthly to verify backup integrity

#!/bin/bash
set -e

echo "Testing PostgreSQL backup restore..."

# 1. Create test database
railway provision postgresql --name test-restore

# 2. Restore latest backup
railway backups restore --database test-restore --backup latest

# 3. Run integrity checks
railway run --service test-restore python scripts/db_integrity_check.py

# 4. Cleanup
railway down --service test-restore

echo "✅ Backup restore test completed successfully"
```

---

## Disaster Recovery Plan (DRP)

### Recovery Time Objective (RTO)

| Scenario | Target RTO | Procedure |
|----------|-----------|-----------|
| **Cache failure** | < 5 minutes | Provision new Redis, flush old cache |
| **Database corruption** | < 30 minutes | Restore from Railway automated backup |
| **Complete data loss** | < 2 hours | Restore from external S3 backup + migrations |
| **Region failure** | < 4 hours | Deploy to alternate region with latest backup |

### Recovery Point Objective (RPO)

- **PostgreSQL**: 24 hours (automated backups)
- **Redis**: Real-time (AOF) or last snapshot
- **Critical Investigations**: 7 days (external backups)

### Disaster Recovery Checklist

- [ ] Verify Railway backup status weekly
- [ ] Test external backup restore monthly
- [ ] Maintain off-site backup copy (S3/Supabase)
- [ ] Document all recovery procedures
- [ ] Train team on recovery processes
- [ ] Review DRP quarterly

---

## Best Practices

### Data Protection

1. **Immutable Backups**: External backups in S3 with versioning enabled
2. **Encryption**: All backups encrypted at rest and in transit
3. **Access Control**: Backup access limited to DevOps team (IAM roles)
4. **Audit Trail**: Log all backup and restore operations

### Cost Optimization

```yaml
Retention Policy:
  - Railway automated: 7 days (included)
  - External S3 backups:
      - Hot storage (S3 Standard): 30 days
      - Warm storage (S3 Glacier): 90 days
      - Cold storage (S3 Deep Archive): 1 year
```

### Compliance

- **LGPD**: Backups contain PII data - encrypt and restrict access
- **Audit**: Log all access to backup systems
- **Retention**: Delete backups after retention period (GDPR right to erasure)

---

## Operational Runbooks

### Weekly Backup Verification

```bash
# 1. Check last backup timestamp
railway backups list --database production | head -1

# 2. Verify backup size is within normal range
# Expected: 500MB - 2GB

# 3. Test sample restore to temp DB
railway backups restore --database production --backup latest --new-database temp_verify

# 4. Run data integrity check
railway run --service temp_verify python scripts/verify_data_integrity.py

# 5. Cleanup
railway down --service temp_verify
```

### Monthly Disaster Recovery Drill

```bash
# Full end-to-end recovery test
bash scripts/backup/disaster_recovery_drill.sh

# Expected result: Complete system restored in < 2 hours
```

---

## Contact Information

| Role | Name | Contact |
|------|------|---------|
| **Database Admin** | DevOps Team | devops@cidadao.ai |
| **On-Call Engineer** | Rotation | oncall@cidadao.ai |
| **Railway Support** | Railway Team | support@railway.app |

---

## Changelog

| Date | Version | Changes |
|------|---------|---------|
| 2025-01-24 | 1.0.0 | Initial backup strategy documentation |

---

## References

- [Railway Database Backups](https://docs.railway.app/databases/backups)
- [PostgreSQL Backup Best Practices](https://www.postgresql.org/docs/current/backup.html)
- [Redis Persistence](https://redis.io/docs/management/persistence/)
- [Supabase Storage](https://supabase.com/docs/guides/storage)
