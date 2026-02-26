# PostgreSQL Backup and Restore Procedures

## Prerequisites
Ensure you have `pg_dump` and `pg_restore` installed and accessible.

## Backup Procedure
To create a logical backup of the ResilienceOps production database:

```bash
# 1. Set your connection string
export DATABASE_URL="postgresql://user:password@localhost:5432/resilienceops"

# 2. Run pg_dump to create a compressed backup file
pg_dump $DATABASE_URL -F c -f resilienceops_backup_$(date +%Y%m%d).dump
```

## Restore Procedure
To restore the database from a backup file:

```bash
# 1. Ensure the target database exists and is empty
export DATABASE_URL="postgresql://user:password@localhost:5432/resilienceops"

# 2. Run pg_restore
pg_restore -d $DATABASE_URL -1 resilienceops_backup_YYYYMMDD.dump
```
> Note: The `-1` flag ensures the restore happens in a single transaction, rolling back if any errors occur.

## Testing Recovery
This procedure was tested against PostgreSQL 15.
1. Insert test SLOs.
2. Run backup.
3. Drop database and recreate it.
4. Run restore.
5. Verify SLOs exist via `/api/v1/slos`.
