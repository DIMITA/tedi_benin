"""
Main scheduler task

This task runs periodically (e.g., every 6 hours) and checks which
datasets need to be updated based on their schedule.
"""
from datetime import datetime
from app import celery, db
from app.models import DatasetVersion, DataSource


@celery.task(name='tasks.scheduler.check_and_schedule')
def check_and_schedule_ingestions():
    """
    Check all dataset versions and schedule ingestion tasks for those that need it

    This is the main scheduler task that should run periodically (e.g., every 6 hours).
    It queries all dataset versions, checks which ones need updating, and dispatches
    the appropriate ingestion tasks.

    Returns:
        Dictionary with scheduling statistics
    """
    print(f"🔍 Checking for datasets that need updating at {datetime.utcnow()}")

    # Get all dataset versions that need checking
    datasets_to_check = DatasetVersion.query.filter(
        DatasetVersion.check_enabled == True
    ).all()

    stats = {
        'checked': 0,
        'scheduled': 0,
        'skipped': 0,
        'errors': 0
    }

    for dataset_version in datasets_to_check:
        stats['checked'] += 1

        try:
            # Check if it's time to update
            if not dataset_version.should_check():
                stats['skipped'] += 1
                continue

            # Get data source info
            data_source = dataset_version.data_source
            if not data_source or not data_source.is_active:
                stats['skipped'] += 1
                continue

            # Dispatch appropriate task based on source name
            task_dispatched = dispatch_ingestion_task(dataset_version, data_source)

            if task_dispatched:
                stats['scheduled'] += 1
                print(f"✅ Scheduled ingestion for {data_source.name} - {dataset_version.version}")
            else:
                stats['skipped'] += 1
                print(f"⏭️  No task handler for {data_source.name}")

        except Exception as e:
            stats['errors'] += 1
            print(f"❌ Error checking {dataset_version.id}: {str(e)}")

    print(f"📊 Scheduling complete: {stats['scheduled']} tasks scheduled, {stats['skipped']} skipped, {stats['errors']} errors")
    return stats


def dispatch_ingestion_task(dataset_version, data_source):
    """
    Dispatch the appropriate ingestion task based on data source

    Args:
        dataset_version: DatasetVersion instance
        data_source: DataSource instance

    Returns:
        Boolean: True if task was dispatched
    """
    source_name = data_source.name.lower()
    version_name = dataset_version.version.lower()

    # Map source names to task names
    task_mapping = {
        # Agriculture
        'faostat': 'tasks.agriculture.ingest_faostat',
        'world_bank_agriculture': 'tasks.agriculture.ingest_worldbank',
        'copernicus_satellite': 'tasks.agriculture.ingest_satellite',
        'instad_agriculture': 'tasks.agriculture.ingest_local_surveys',

        # Real Estate
        'openstreetmap': 'tasks.realestate.ingest_osm',
        'cadastre_benin': 'tasks.realestate.ingest_cadastre',
        'property_listings': 'tasks.realestate.ingest_listings',
        'land_valuation': 'tasks.realestate.ingest_land_values',

        # Employment
        'ilostat': 'tasks.employment.ingest_ilostat',
        'world_bank_employment': 'tasks.employment.ingest_worldbank',
        'instad_employment': 'tasks.employment.ingest_local_surveys',
        'sectoral_employment': 'tasks.employment.ingest_sectoral_stats',

        # Business
        'rccm_benin': 'tasks.business.ingest_rccm',
        'world_bank_business': 'tasks.business.ingest_worldbank',
        'unido': 'tasks.business.ingest_unido',
        'sectoral_business': 'tasks.business.ingest_sectoral_stats',
        'trade_statistics': 'tasks.business.ingest_trade_data',
    }

    # Special handling for World Bank - determine vertical from version name
    if source_name == 'world bank':
        if 'agriculture' in version_name or 'agric' in version_name:
            task_name = 'tasks.agriculture.ingest_worldbank'
        elif 'employment' in version_name or 'labor' in version_name or 'labour' in version_name:
            task_name = 'tasks.employment.ingest_worldbank'
        elif 'business' in version_name or 'enterprise' in version_name:
            task_name = 'tasks.business.ingest_worldbank'
        else:
            return False
    else:
        # Get task name from mapping
        task_name = task_mapping.get(source_name)

    if task_name:
        # Dispatch task asynchronously
        celery.send_task(
            task_name,
            kwargs={
                'dataset_version_id': dataset_version.id,
                'data_source_id': data_source.id
            }
        )
        return True

    return False


@celery.task(name='tasks.scheduler.cleanup_old_logs')
def cleanup_old_ingestion_logs(days_to_keep=90):
    """
    Clean up old ingestion logs to prevent database bloat

    Args:
        days_to_keep: Number of days of logs to retain (default: 90)

    Returns:
        Integer: Number of logs deleted
    """
    from datetime import timedelta
    from app.models import IngestionLog

    cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)

    # Delete old logs
    deleted = IngestionLog.query.filter(
        IngestionLog.created_at < cutoff_date
    ).delete()

    db.session.commit()

    print(f"🗑️  Cleaned up {deleted} old ingestion logs (older than {days_to_keep} days)")
    return deleted


@celery.task(name='tasks.scheduler.update_reliability_scores')
def update_reliability_scores():
    """
    Update reliability scores for all data sources based on recent ingestion history

    Analyzes recent ingestion logs and calculates a reliability score based on:
    - Success rate
    - Consistency of updates
    - Error patterns

    Returns:
        Dictionary with update statistics
    """
    from app.models import IngestionLog

    print("📊 Updating reliability scores for all dataset versions")

    dataset_versions = DatasetVersion.query.filter(
        DatasetVersion.check_enabled == True
    ).all()

    stats = {
        'updated': 0,
        'unchanged': 0
    }

    for ds_version in dataset_versions:
        # Get recent logs (last 10)
        recent_logs = IngestionLog.query.filter_by(
            dataset_version_id=ds_version.id
        ).order_by(
            IngestionLog.created_at.desc()
        ).limit(10).all()

        if not recent_logs:
            continue

        # Calculate success rate
        success_count = sum(1 for log in recent_logs if log.status == 'success')
        total_count = len(recent_logs)
        success_rate = success_count / total_count if total_count > 0 else 0

        # Calculate average duration (for performance tracking)
        durations = [log.duration_seconds for log in recent_logs if log.duration_seconds]
        avg_duration = sum(durations) / len(durations) if durations else 0

        # Calculate reliability score (0.0 to 1.0)
        # Based on: 70% success rate + 20% consistency + 10% recency
        consistency_score = 1.0 - (ds_version.consecutive_failures / 5.0)  # Penalize failures
        recency_score = 1.0 if recent_logs[0].status == 'success' else 0.5  # Recent success important

        reliability_score = (
            success_rate * 0.7 +
            consistency_score * 0.2 +
            recency_score * 0.1
        )

        # Update dataset version
        old_score = ds_version.source_reliability_score or 0
        ds_version.source_reliability_score = round(reliability_score, 3)

        if abs(old_score - reliability_score) > 0.05:
            stats['updated'] += 1
        else:
            stats['unchanged'] += 1

    db.session.commit()

    print(f"✅ Reliability scores updated: {stats['updated']} changed, {stats['unchanged']} unchanged")
    return stats
