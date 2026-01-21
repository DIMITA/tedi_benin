# Data Ingestion Scheduler - Setup Guide

## Overview

The TEDI platform uses **Celery** with **Celery Beat** to automatically fetch and update data from external sources on a schedule aligned with each source's actual update frequency.

**Core Principle**: TEDI does NOT do real-time data. It provides **indexed, reliable, versioned data** with frequencies aligned to source update patterns.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Celery Beat Scheduler (runs every 6 hours)                 │
│  └─ tasks.scheduler.check_and_schedule()                    │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  Master Scheduler Logic                                      │
│  • Queries dataset_versions where check_enabled = True      │
│  • Checks should_check() for each                           │
│  • Dispatches appropriate ingestion task                    │
└─────────────────────────────────────────────────────────────┘
                           │
         ┌─────────────────┼─────────────────┬──────────────┐
         ▼                 ▼                 ▼              ▼
    Agriculture      Real Estate       Employment      Business
    Tasks Queue      Tasks Queue       Tasks Queue     Tasks Queue
         │                 │                 │              │
         ▼                 ▼                 ▼              ▼
    FAOSTAT          OpenStreetMap      ILOSTAT         RCCM
    World Bank       Cadastre           World Bank      World Bank
    Satellite        Listings           Surveys         UNIDO
```

---

## System Components

### 1. Database Models

**DatasetVersion** (`app/models/metadata.py`):
- Tracks each dataset version
- Auto-scheduling fields: `last_checked_at`, `next_check_at`, `check_enabled`
- Reliability tracking: `source_reliability_score`, `consecutive_failures`
- Methods: `should_check()`, `calculate_next_check()`, `mark_checked()`

**IngestionLog** (`app/models/ingestion.py`):
- Detailed audit log of every ingestion attempt
- Tracks: status, duration, records added/updated, errors
- Checksum tracking for change detection

**DataSourceConfig** (`app/models/ingestion.py`):
- Configuration for external API connections
- Stores: API keys, base URLs, auth settings, rate limits

### 2. Task Infrastructure

**BaseIngestionTask** (`app/tasks/base.py`):
- Base class for all ingestion tasks
- Automatic ingestion logging
- Checksum-based change detection
- Error handling with retry logic

**Main Scheduler** (`app/tasks/scheduler.py`):
- `check_and_schedule()`: Master scheduler (runs every 6 hours)
- `cleanup_old_logs()`: Removes logs older than 90 days
- `update_reliability_scores()`: Calculates source reliability

### 3. Connectors (ETL Pattern)

**BaseConnector** (`app/connectors/base.py`):
- Abstract class implementing ETL pattern
- Methods: `fetch()`, `transform()`, `load()`
- Helpers: `get_json()`, `bulk_upsert()`, `clean_numeric()`

**Implemented Connectors**:
- `FAOSTATConnector`: Agriculture production data
- `WorldBankConnector`: Economic/development indicators
- `OSMConnector`: Building footprints and infrastructure

### 4. Task Modules

**Agriculture** (`app/tasks/agriculture.py`):
- `ingest_faostat`: Quarterly
- `ingest_worldbank_agriculture`: Annual
- `ingest_satellite_data`: Monthly (placeholder)
- `ingest_local_surveys`: On-event (placeholder)

**Real Estate** (`app/tasks/realestate.py`):
- `ingest_osm`: Monthly
- `ingest_cadastre`: Quarterly (placeholder)
- `ingest_listings`: Weekly (placeholder)
- `ingest_land_values`: Annual (placeholder)

**Employment** (`app/tasks/employment.py`):
- `ingest_ilostat`: Annual (placeholder)
- `ingest_worldbank_employment`: Annual
- `ingest_local_surveys`: On-event (placeholder)
- `ingest_sectoral_stats`: Quarterly (placeholder)

**Business** (`app/tasks/business.py`):
- `ingest_rccm`: Quarterly (placeholder)
- `ingest_worldbank_business`: Annual
- `ingest_unido`: Annual (placeholder)
- `ingest_sectoral_stats`: Quarterly (placeholder)
- `ingest_trade_data`: Quarterly (placeholder)

---

## Installation & Setup

### 1. Install Dependencies

Ensure Celery and Redis are installed:

```bash
# Already in requirements.txt
pip install celery[redis]
```

### 2. Start Redis

Celery requires a message broker (Redis):

```bash
# Using Docker (recommended)
docker-compose up -d redis

# Or install locally
sudo apt-get install redis-server
redis-server
```

### 3. Configure Celery

Configuration is in `app/celeryconfig.py`. Key settings:

```python
# Broker
broker_url = 'redis://localhost:6379/0'
result_backend = 'redis://localhost:6379/0'

# Beat schedule
beat_schedule = {
    'check-datasets-for-updates': {
        'task': 'tasks.scheduler.check_and_schedule',
        'schedule': timedelta(hours=6),
    },
    # ... maintenance tasks
}

# Task routing
task_routes = {
    'tasks.scheduler.*': {'queue': 'scheduler'},
    'tasks.agriculture.*': {'queue': 'agriculture'},
    'tasks.realestate.*': {'queue': 'realestate'},
    'tasks.employment.*': {'queue': 'employment'},
    'tasks.business.*': {'queue': 'business'},
}
```

### 4. Run Database Migration

Apply the ingestion scheduling migration:

```bash
docker exec -it tedi_backend flask db upgrade
```

This creates:
- `data_source_configs` table
- `ingestion_logs` table
- New columns in `dataset_versions`

---

## Running the Scheduler

### Option 1: Separate Workers (Production)

**Start the main scheduler worker**:
```bash
celery -A celery_worker.celery_app worker -Q scheduler --loglevel=info
```

**Start beat scheduler** (in separate terminal):
```bash
celery -A celery_worker.celery_app beat --loglevel=info
```

**Start vertical-specific workers** (optional, for scaling):
```bash
# Agriculture queue
celery -A celery_worker.celery_app worker -Q agriculture --loglevel=info

# Real Estate queue
celery -A celery_worker.celery_app worker -Q realestate --loglevel=info
```

### Option 2: Combined Worker (Development)

Run worker and beat scheduler together:

```bash
celery -A celery_worker.celery_app worker --beat --loglevel=info
```

### Option 3: Docker Compose (Recommended)

Add to `docker-compose.yml`:

```yaml
  celery_worker:
    build: ./backend
    command: celery -A celery_worker.celery_app worker --loglevel=info
    depends_on:
      - db
      - redis
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/tedi
      - CELERY_BROKER_URL=redis://redis:6379/0

  celery_beat:
    build: ./backend
    command: celery -A celery_worker.celery_app beat --loglevel=info
    depends_on:
      - db
      - redis
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/tedi
      - CELERY_BROKER_URL=redis://redis:6379/0
```

Then:
```bash
docker-compose up -d celery_worker celery_beat
```

---

## Usage

### 1. Create Data Sources

First, create `DataSource` records in the database:

```python
from app import create_app, db
from app.models import DataSource

app = create_app()
with app.app_context():
    # FAOSTAT
    faostat = DataSource(
        name='faostat',
        url='https://www.fao.org/faostat/',
        organization='Food and Agriculture Organization',
        source_type='external',
        update_frequency='quarterly',
        is_active=True
    )
    db.session.add(faostat)

    # World Bank
    wb = DataSource(
        name='world_bank_agriculture',
        url='https://data.worldbank.org/',
        organization='World Bank',
        source_type='external',
        update_frequency='annual',
        is_active=True
    )
    db.session.add(wb)

    db.session.commit()
```

### 2. Create Dataset Versions

Link datasets to data sources with scheduling:

```python
from app.models import DatasetVersion
from datetime import datetime, timedelta

# Create version for FAOSTAT agriculture data
faostat_version = DatasetVersion(
    dataset_id=1,  # Your agriculture dataset
    data_source_id=faostat.id,
    version='2024.Q1',
    check_enabled=True,  # Enable automatic checking
    next_check_at=datetime.utcnow() + timedelta(hours=1),  # Check in 1 hour
)
db.session.add(faostat_version)
db.session.commit()
```

### 3. Monitor Ingestion Logs

Check ingestion history:

```python
from app.models import IngestionLog

# Get recent logs
recent_logs = IngestionLog.query.order_by(
    IngestionLog.created_at.desc()
).limit(10).all()

for log in recent_logs:
    print(f"{log.started_at} - {log.dataset_version.data_source.name} - {log.status}")
    print(f"  Records: {log.records_added} added, {log.records_updated} updated")
    if log.error_message:
        print(f"  Error: {log.error_message}")
```

### 4. Manual Task Trigger

Trigger an ingestion task manually:

```python
from celery_worker import celery_app

# Trigger FAOSTAT ingestion
celery_app.send_task(
    'tasks.agriculture.ingest_faostat',
    kwargs={
        'dataset_version_id': 1,
        'data_source_id': 1,
        'country_code': 'BJ'
    }
)
```

Or using the scheduler:

```python
from app.tasks.scheduler import check_and_schedule_ingestions

# Run scheduler now
result = check_and_schedule_ingestions()
print(result)  # {'checked': 5, 'scheduled': 2, 'skipped': 3, 'errors': 0}
```

---

## Monitoring

### Celery Flower (Web UI)

Install and run Flower for monitoring:

```bash
pip install flower
celery -A celery_worker.celery_app flower
```

Access at: http://localhost:5555

### Check Task Status

```python
# In Python shell
from celery.result import AsyncResult

result = AsyncResult('task-id-here')
print(result.state)  # PENDING, STARTED, SUCCESS, FAILURE
print(result.result)  # Task return value
```

### View Active Workers

```bash
celery -A celery_worker.celery_app inspect active
celery -A celery_worker.celery_app inspect stats
```

---

## Frequency Alignment

| Vertical | Source | Frequency | Rationale |
|----------|--------|-----------|-----------|
| **Agriculture** | FAOSTAT | Quarterly | Updates 1-2x per year |
| | World Bank | Annual | Updates yearly |
| | Satellite (NDVI) | Monthly | Aggregate monthly data |
| | Local Surveys | On-event | Manual trigger |
| **Real Estate** | OpenStreetMap | Monthly | Active community updates |
| | Cadastre | Quarterly | Official updates are periodic |
| | Property Listings | Weekly | Price monitoring |
| **Employment** | ILOSTAT | Annual | Check semi-annually |
| | World Bank | Annual | Updates yearly |
| | Local Surveys | On-event | Manual trigger |
| **Business** | RCCM Registry | Quarterly | Official registry updates |
| | World Bank | Annual | Updates yearly |
| | UNIDO | Annual | Industrial statistics |

---

## Security Features

### Circuit Breaker

After 5 consecutive failures, automatic checking is disabled:

```python
if dataset_version.consecutive_failures >= 5:
    print("Circuit breaker activated - too many failures")
    # Manual intervention required
```

Re-enable by setting `consecutive_failures = 0`.

### Rate Limiting

Connectors implement rate limiting:

```python
connector.rate_limit_wait(calls_per_second=1.0)
```

### API Key Management

Store API keys in `DataSourceConfig`:

```python
config = DataSourceConfig(
    source_name='faostat',
    api_key='your-api-key',
    auth_type='api_key'
)
```

Never commit API keys to version control!

---

## Troubleshooting

### Tasks Not Running

1. Check Redis is running: `redis-cli ping`
2. Check workers are active: `celery -A celery_worker.celery_app inspect active`
3. Check beat scheduler is running: Look for "Scheduler: Sending due task" in logs

### No Changes Detected

This is normal! If checksum matches previous ingestion, the task returns:

```python
{'has_changes': False, 'records_skipped': 1}
```

### High Memory Usage

Set worker max tasks:

```python
# In celeryconfig.py
worker_max_tasks_per_child = 100  # Restart worker after 100 tasks
```

### Database Connection Issues

Ensure Flask app context:

```python
# celery_worker.py already handles this
class ContextTask(celery.Task):
    def __call__(self, *args, **kwargs):
        with flask_app.app_context():
            return self.run(*args, **kwargs)
```

---

## Next Steps

1. ✅ Database migration applied
2. ✅ Celery workers configured
3. ⏳ Create initial `DataSource` records
4. ⏳ Create `DatasetVersion` records with scheduling
5. ⏳ Test manual task execution
6. ⏳ Enable beat scheduler
7. ⏳ Monitor first automatic run
8. ⏳ Implement remaining connectors (ILOSTAT, RCCM, etc.)

---

## Reference Commands

```bash
# Start everything (development)
celery -A celery_worker.celery_app worker --beat --loglevel=info

# List registered tasks
python -c "from celery_worker import celery_app; print('\n'.join(sorted([t for t in celery_app.tasks.keys() if not t.startswith('celery.')])))"

# Run migration
docker exec -it tedi_backend flask db upgrade

# Check scheduler logs
docker logs -f tedi_backend | grep "Scheduler"

# Trigger scheduler manually
docker exec -it tedi_backend python -c "from app.tasks.scheduler import check_and_schedule_ingestions; print(check_and_schedule_ingestions())"
```

---

## Documentation References

- [Celery Documentation](https://docs.celeryproject.org/)
- [Celery Beat Scheduling](https://docs.celeryproject.org/en/stable/userguide/periodic-tasks.html)
- [Flask-Celery Integration](https://flask.palletsprojects.com/en/2.3.x/patterns/celery/)
- [TEDI Architecture Documentation](./DATA_INGESTION_SCHEDULER_SETUP.md)
