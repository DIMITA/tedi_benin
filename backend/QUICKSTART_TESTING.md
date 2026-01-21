# Data Ingestion Scheduler - Quick Start Testing Guide

This guide walks you through testing the data ingestion scheduler system from scratch.

---

## Prerequisites

- Docker containers running (`tedi_backend`, `tedi_db`, `redis`)
- Database migrations applied
- Python environment with all dependencies installed

---

## Step 1: Initialize Data Sources and Dataset Versions

Run the setup script to create initial data:

```bash
docker exec -it tedi_backend python setup_scheduler_data.py
```

**What this does**:
- Creates 4 data sources: FAOSTAT, World Bank, ILOSTAT, OpenStreetMap
- Creates 4 datasets with versions linked to sources
- Schedules first checks in 5 minutes
- Displays summary and next steps

**Expected output**:
```
✅ Data sources setup complete: 4 new
✅ Dataset versions setup complete: 7 new versions created

📊 Active Data Sources: 4
  • FAOSTAT (quarterly)
  • World Bank (annual)
  • ILOSTAT (annual)
  • OpenStreetMap (monthly)
```

---

## Step 2: Verify Database Setup

Check that everything is in place:

```bash
docker exec -it tedi_backend python test_scheduler.py
```

**Expected tests to pass**:
- ✅ Database setup
- ✅ Task registration
- ✅ Celery configuration
- ✅ Sample data creation
- ✅ Scheduler logic
- ✅ Connector imports

If all tests pass, you're ready to start the scheduler!

---

## Step 3: Start Redis (if not running)

```bash
docker-compose up -d redis

# Verify Redis is running
docker exec -it redis redis-cli ping
# Should return: PONG
```

---

## Step 4: Start Celery Worker + Beat Scheduler

### Option A: Combined (Recommended for testing)

Start both worker and beat scheduler together:

```bash
docker exec -it tedi_backend celery -A celery_worker.celery_app worker --beat --loglevel=info
```

### Option B: Separate Processes (Production-like)

**Terminal 1 - Worker**:
```bash
docker exec -it tedi_backend celery -A celery_worker.celery_app worker --loglevel=info
```

**Terminal 2 - Beat Scheduler**:
```bash
docker exec -it tedi_backend celery -A celery_worker.celery_app beat --loglevel=info
```

### Option C: Background (Detached)

```bash
# Start worker in background
docker exec -d tedi_backend celery -A celery_worker.celery_app worker --loglevel=info --pidfile=/tmp/celery_worker.pid

# Start beat in background
docker exec -d tedi_backend celery -A celery_worker.celery_app beat --loglevel=info --pidfile=/tmp/celery_beat.pid

# View logs
docker logs -f tedi_backend | grep -E "Scheduler|celery"
```

**What to look for in logs**:
```
[2026-01-13 06:00:00,000: INFO/MainProcess] celery@hostname ready.
[2026-01-13 06:00:00,001: INFO/MainProcess] beat: Starting...
```

---

## Step 5: Test Manual Task Execution

Before waiting for automatic runs, test tasks manually:

### Test the Master Scheduler

```bash
docker exec -it tedi_backend python -c "
from app.tasks.scheduler import check_and_schedule_ingestions
result = check_and_schedule_ingestions()
print('Result:', result)
"
```

**Expected output**:
```
🔍 Checking for datasets that need updating at 2026-01-13 06:00:00
✅ Scheduled ingestion for FAOSTAT - auto_20260113
✅ Scheduled ingestion for World Bank - auto_20260113
📊 Scheduling complete: 7 tasks scheduled, 0 skipped, 0 errors
Result: {'checked': 7, 'scheduled': 7, 'skipped': 0, 'errors': 0}
```

### Test Individual Tasks

**Test FAOSTAT**:
```bash
docker exec -it tedi_backend python -c "
from celery_worker import celery_app
from app import create_app, db
from app.models import DatasetVersion

app = create_app()
with app.app_context():
    version = DatasetVersion.query.join(DatasetVersion.data_source).filter_by(name='FAOSTAT').first()
    if version:
        result = celery_app.send_task(
            'tasks.agriculture.ingest_faostat',
            kwargs={'dataset_version_id': version.id, 'data_source_id': version.data_source_id, 'country_code': 'BJ'}
        )
        print(f'Task ID: {result.id}')
        print('Check status with: celery_app.AsyncResult(task_id).state')
"
```

**Test World Bank**:
```bash
docker exec -it tedi_backend python -c "
from celery_worker import celery_app
from app import create_app, db
from app.models import DatasetVersion

app = create_app()
with app.app_context():
    version = DatasetVersion.query.join(DatasetVersion.data_source).filter_by(name='World Bank').first()
    if version:
        result = celery_app.send_task(
            'tasks.agriculture.ingest_worldbank',
            kwargs={'dataset_version_id': version.id, 'data_source_id': version.data_source_id, 'country_code': 'BJ'}
        )
        print(f'Task ID: {result.id}')
"
```

---

## Step 6: Monitor Task Execution

### View Ingestion Logs

```bash
docker exec -it tedi_backend python -c "
from app import create_app, db
from app.models import IngestionLog

app = create_app()
with app.app_context():
    logs = IngestionLog.query.order_by(IngestionLog.created_at.desc()).limit(10).all()
    print(f'\nRecent Ingestion Logs ({len(logs)}):')
    print('='*80)
    for log in logs:
        source = log.dataset_version.data_source if log.dataset_version else None
        print(f'{log.created_at} | {source.name if source else \"N/A\"} | {log.status}')
        if log.status == 'success':
            print(f'  ✅ Added: {log.records_added}, Updated: {log.records_updated}')
        elif log.status == 'failed':
            print(f'  ❌ Error: {log.error_message}')
        print()
"
```

### Check Dataset Version Status

```bash
docker exec -it tedi_backend python -c "
from app import create_app, db
from app.models import DatasetVersion

app = create_app()
with app.app_context():
    versions = DatasetVersion.query.filter_by(check_enabled=True).all()
    print(f'\nDataset Versions Status ({len(versions)}):')
    print('='*80)
    for v in versions:
        source = v.data_source
        print(f'{source.name if source else \"N/A\"}')
        print(f'  Last checked: {v.last_checked_at}')
        print(f'  Next check: {v.next_check_at}')
        print(f'  Reliability: {v.source_reliability_score}')
        print(f'  Failures: {v.consecutive_failures}')
        print()
"
```

---

## Step 7: Monitor with Flower (Optional)

Flower provides a web UI for monitoring Celery tasks.

**Install and start**:
```bash
pip install flower
celery -A celery_worker.celery_app flower
```

**Access**: http://localhost:5555

**Features**:
- View active/scheduled/completed tasks
- Monitor worker status
- See task execution time
- Inspect task results
- View broker queue sizes

---

## Step 8: Test Automatic Scheduling

Now that everything is running, the beat scheduler will automatically trigger `check_and_schedule_ingestions()` every 6 hours.

**Watch for automatic runs**:
```bash
docker logs -f tedi_backend | grep "check-datasets-for-updates"
```

**Expected log pattern**:
```
[2026-01-13 06:00:00] Task check-datasets-for-updates[abc123] received
[2026-01-13 06:00:01] 🔍 Checking for datasets that need updating
[2026-01-13 06:00:02] ✅ Scheduled ingestion for FAOSTAT
[2026-01-13 06:00:03] 📊 Scheduling complete: 7 tasks scheduled
[2026-01-13 06:00:04] Task check-datasets-for-updates[abc123] succeeded
```

---

## Step 9: Test Specific Scenarios

### Scenario 1: Test Checksum-Based Skip

Run the same task twice without data changes:

```bash
# First run - should ingest
docker exec -it tedi_backend python -c "from app.tasks.scheduler import check_and_schedule_ingestions; check_and_schedule_ingestions()"

# Second run (immediately after) - should skip
docker exec -it tedi_backend python -c "from app.tasks.scheduler import check_and_schedule_ingestions; check_and_schedule_ingestions()"
```

**Expected**: First run schedules tasks, second run skips (next_check_at not yet reached)

### Scenario 2: Test Circuit Breaker

Simulate 5 consecutive failures to trigger circuit breaker:

```bash
docker exec -it tedi_backend python -c "
from app import create_app, db
from app.models import DatasetVersion

app = create_app()
with app.app_context():
    version = DatasetVersion.query.first()
    if version:
        version.consecutive_failures = 5
        db.session.commit()
        print(f'Set {version.data_source.name} failures to 5')
        print(f'should_check() = {version.should_check()}')  # Should be False
"
```

**Expected**: `should_check()` returns `False`, scheduler skips this version

### Scenario 3: Test Reliability Score Calculation

```bash
docker exec -it tedi_backend python -c "
from app.tasks.scheduler import update_reliability_scores
result = update_reliability_scores()
print('Result:', result)
"
```

**Expected**: Reliability scores updated based on recent ingestion history

---

## Troubleshooting

### Issue: Tasks not running

**Check**:
1. Is Redis running? `docker exec redis redis-cli ping`
2. Is worker connected? Look for "celery@hostname ready" in logs
3. Is beat scheduler running? Look for "beat: Starting..." in logs

### Issue: Tasks failing immediately

**Check ingestion logs**:
```bash
docker exec -it tedi_backend python -c "
from app import create_app, db
from app.models import IngestionLog

app = create_app()
with app.app_context():
    failed = IngestionLog.query.filter_by(status='failed').order_by(IngestionLog.created_at.desc()).first()
    if failed:
        print('Latest failure:')
        print(f'Error: {failed.error_message}')
        print(f'Traceback: {failed.error_traceback}')
"
```

### Issue: No data being fetched

**Possible reasons**:
1. API keys not configured (for sources that need them)
2. Network issues (can't reach external APIs)
3. Incorrect country codes or parameters
4. API rate limits exceeded

**Solution**: Check connector logs and verify API accessibility

### Issue: Celery worker memory issues

**Solution**: Restart workers periodically
```bash
# Stop worker
docker exec tedi_backend pkill -f celery

# Start worker
docker exec -d tedi_backend celery -A celery_worker.celery_app worker --beat --loglevel=info
```

Or configure in `celeryconfig.py`:
```python
worker_max_tasks_per_child = 100  # Already configured
```

---

## Stopping the Scheduler

### Graceful shutdown

```bash
# If running in foreground, press Ctrl+C

# If running in background
docker exec tedi_backend pkill -TERM -f "celery.*worker"
docker exec tedi_backend pkill -TERM -f "celery.*beat"
```

### Check processes stopped

```bash
docker exec tedi_backend ps aux | grep celery
# Should show no celery processes
```

---

## Success Criteria

✅ **System is working correctly if**:
1. All tests pass in `test_scheduler.py`
2. Celery worker and beat scheduler start without errors
3. Manual scheduler run schedules tasks
4. Ingestion logs show successful executions
5. Dataset versions update `last_checked_at` and `next_check_at`
6. No error tracebacks in logs
7. Beat scheduler runs every 6 hours automatically

---

## Next Steps After Testing

Once basic testing is complete:

1. **Monitor for 24 hours**: Let the scheduler run and verify automatic executions
2. **Check data quality**: Verify ingested data in database tables
3. **Tune frequencies**: Adjust `update_frequency` for each source based on observation
4. **Add monitoring**: Set up alerts for failed ingestions
5. **Implement remaining connectors**: RCCM, Cadastre, Property Listings, etc.
6. **Production deployment**: Move to production environment with proper monitoring

---

## Quick Reference

### Start Everything
```bash
# Redis
docker-compose up -d redis

# Celery (combined)
docker exec -it tedi_backend celery -A celery_worker.celery_app worker --beat --loglevel=info
```

### Monitor
```bash
# Live logs
docker logs -f tedi_backend | grep -E "Scheduler|celery"

# Ingestion logs
docker exec -it tedi_backend python -c "from app import create_app, db; from app.models import IngestionLog; app=create_app(); app.app_context().push(); [print(f'{log.created_at} | {log.dataset_version.data_source.name} | {log.status}') for log in IngestionLog.query.order_by(IngestionLog.created_at.desc()).limit(10)]"
```

### Stop Everything
```bash
docker exec tedi_backend pkill -f celery
docker-compose stop redis
```

---

**Ready to start?** Run: `docker exec -it tedi_backend python setup_scheduler_data.py`
