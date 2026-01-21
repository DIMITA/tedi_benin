"""
Base Celery task for data ingestion

Provides common functionality for all ingestion tasks:
- Logging
- Error handling
- Progress tracking
- Checksum calculation
"""
import hashlib
import json
import traceback
from datetime import datetime
from celery import Task
from app import db, celery
from app.models import DatasetVersion, IngestionLog


class BaseIngestionTask(Task):
    """
    Base class for all ingestion tasks

    Provides automatic logging, error handling, and progress tracking.
    """

    def __init__(self):
        super().__init__()
        self.ingestion_log_id = None
        self.dataset_version_id = None
        self._ingestion_log = None
        self._dataset_version = None

    def __call__(self, *args, **kwargs):
        """Wrap task execution in Flask app context"""
        from app import create_app
        app = create_app()
        with app.app_context():
            return super().__call__(*args, **kwargs)

    @property
    def ingestion_log(self):
        """Lazy-load ingestion log from database"""
        if self._ingestion_log is None and self.ingestion_log_id:
            self._ingestion_log = IngestionLog.query.get(self.ingestion_log_id)
        return self._ingestion_log

    @property
    def dataset_version(self):
        """Lazy-load dataset version from database"""
        if self._dataset_version is None and self.dataset_version_id:
            self._dataset_version = DatasetVersion.query.get(self.dataset_version_id)
        return self._dataset_version

    def before_start(self, task_id, args, kwargs):
        """Called before task execution"""
        from app import create_app
        app = create_app()

        with app.app_context():
            dataset_version_id = kwargs.get('dataset_version_id')
            self.dataset_version_id = dataset_version_id

            if dataset_version_id:
                # Load dataset version
                dataset_version = DatasetVersion.query.get(dataset_version_id)

                # Create ingestion log
                ingestion_log = IngestionLog.create_log(
                    dataset_version_id=dataset_version_id,
                    task_id=task_id
                )
                self.ingestion_log_id = ingestion_log.id

                if dataset_version:
                    ingestion_log.checksum_before = dataset_version.checksum
                    db.session.commit()

    def on_success(self, retval, task_id, args, kwargs):
        """Called when task succeeds"""
        from app import create_app
        app = create_app()

        with app.app_context():
            if self.ingestion_log_id:
                # Reload objects from database
                ingestion_log = IngestionLog.query.get(self.ingestion_log_id)
                dataset_version = DatasetVersion.query.get(self.dataset_version_id) if self.dataset_version_id else None

                if ingestion_log:
                    # Extract stats from return value
                    stats = retval or {}

                    ingestion_log.mark_success(
                        records_fetched=stats.get('records_fetched', 0),
                        records_added=stats.get('records_added', 0),
                        records_updated=stats.get('records_updated', 0),
                        records_skipped=stats.get('records_skipped', 0),
                        has_changes=stats.get('has_changes', False),
                        checksum_after=stats.get('checksum_after'),
                        ingestion_metadata=stats.get('metadata')
                    )

                    # Update dataset version
                    if dataset_version:
                        dataset_version.mark_checked(
                            has_changes=stats.get('has_changes', False),
                            new_checksum=stats.get('checksum_after'),
                            records_added=stats.get('records_added', 0),
                            records_updated=stats.get('records_updated', 0),
                            duration_seconds=ingestion_log.duration_seconds or 0
                        )

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Called when task fails"""
        from app import create_app
        app = create_app()

        with app.app_context():
            if self.ingestion_log_id:
                # Reload objects from database
                ingestion_log = IngestionLog.query.get(self.ingestion_log_id)
                dataset_version = DatasetVersion.query.get(self.dataset_version_id) if self.dataset_version_id else None

                if ingestion_log:
                    ingestion_log.mark_failed(
                        error_message=str(exc),
                        error_traceback=str(einfo)
                    )

                    # Update dataset version with error
                    if dataset_version:
                        dataset_version.mark_checked(error=exc)

    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """Called when task is retried"""
        from app import create_app
        app = create_app()

        with app.app_context():
            # Log retry attempt
            if self.ingestion_log_id:
                ingestion_log = IngestionLog.query.get(self.ingestion_log_id)
                if ingestion_log:
                    metadata = ingestion_log.ingestion_metadata or {}
                    metadata['retry_count'] = metadata.get('retry_count', 0) + 1
                    metadata['last_retry_at'] = datetime.utcnow().isoformat()
                    ingestion_log.ingestion_metadata = metadata
                    db.session.commit()

    @staticmethod
    def calculate_checksum(data):
        """
        Calculate SHA256 checksum of data

        Args:
            data: Dictionary or string to hash

        Returns:
            String: Hex digest of SHA256 hash
        """
        if isinstance(data, dict):
            # Convert dict to sorted JSON string for consistent hashing
            data = json.dumps(data, sort_keys=True)

        if isinstance(data, str):
            data = data.encode('utf-8')

        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def should_skip_ingestion(dataset_version, new_checksum):
        """
        Determine if ingestion should be skipped based on checksum

        Args:
            dataset_version: DatasetVersion instance
            new_checksum: New data checksum

        Returns:
            Boolean: True if should skip
        """
        if not dataset_version or not dataset_version.checksum:
            return False

        return dataset_version.checksum == new_checksum


@celery.task(bind=True, base=BaseIngestionTask, name='tasks.ingestion.generic')
def generic_ingestion_task(self, dataset_version_id, connector_class, **kwargs):
    """
    Generic ingestion task that works with any connector

    Args:
        dataset_version_id: ID of dataset version to update
        connector_class: Connector class to use for fetching data
        **kwargs: Additional arguments passed to connector

    Returns:
        Dictionary with ingestion statistics
    """
    self.ingestion_log.mark_running()

    try:
        # Initialize connector
        connector = connector_class(**kwargs)

        # Fetch data
        data = connector.fetch()

        # Calculate checksum
        new_checksum = self.calculate_checksum(data)

        # Check if we should skip
        if self.should_skip_ingestion(self.dataset_version, new_checksum):
            self.ingestion_log.mark_skipped('No changes detected (checksum match)')
            return {
                'has_changes': False,
                'records_fetched': 0,
                'records_added': 0,
                'records_updated': 0,
                'records_skipped': len(data) if isinstance(data, list) else 1,
                'checksum_after': new_checksum
            }

        # Transform data
        transformed_data = connector.transform(data)

        # Load to database
        stats = connector.load(transformed_data)

        # Add checksum to stats
        stats['checksum_after'] = new_checksum
        stats['has_changes'] = True

        return stats

    except Exception as e:
        # Log error and re-raise
        print(f"Ingestion failed: {str(e)}")
        traceback.print_exc()
        raise
