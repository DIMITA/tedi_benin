"""
Data Ingestion models
"""
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB
from app import db
from app.models.base import BaseModel


class IngestionLog(BaseModel):
    """
    Detailed log of each ingestion attempt

    For auditing, debugging, and monitoring data pipeline health.
    """
    __tablename__ = 'ingestion_logs'

    # Link to dataset version
    dataset_version_id = db.Column(db.Integer, db.ForeignKey('dataset_versions.id'), nullable=False)
    dataset_version = db.relationship('DatasetVersion', backref='ingestion_logs')

    # Execution details
    task_id = db.Column(db.String(100), nullable=True)  # Celery task ID
    status = db.Column(db.String(20), nullable=False, index=True)  # pending, running, success, failed, skipped

    started_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    duration_seconds = db.Column(db.Float, nullable=True)

    # Results
    records_fetched = db.Column(db.Integer, default=0)
    records_added = db.Column(db.Integer, default=0)
    records_updated = db.Column(db.Integer, default=0)
    records_skipped = db.Column(db.Integer, default=0)

    # Change detection
    checksum_before = db.Column(db.String(64), nullable=True)
    checksum_after = db.Column(db.String(64), nullable=True)
    has_changes = db.Column(db.Boolean, default=False)

    # Error handling
    error_message = db.Column(db.Text, nullable=True)
    error_traceback = db.Column(db.Text, nullable=True)

    # Metadata
    ingestion_metadata = db.Column(JSONB, nullable=True)  # API response metadata, rate limits, etc.

    def __repr__(self):
        return f'<IngestionLog {self.status} for {self.dataset_version_id}>'

    @classmethod
    def create_log(cls, dataset_version_id, task_id=None):
        """Create new ingestion log"""
        log = cls(
            dataset_version_id=dataset_version_id,
            task_id=task_id,
            status='pending',
            started_at=datetime.utcnow()
        )
        db.session.add(log)
        db.session.commit()
        return log

    def mark_running(self):
        """Mark as running"""
        self.status = 'running'
        self.started_at = datetime.utcnow()
        db.session.commit()

    def mark_success(self, records_fetched=0, records_added=0, records_updated=0,
                    records_skipped=0, has_changes=False, checksum_after=None, ingestion_metadata=None):
        """Mark as successful"""
        now = datetime.utcnow()
        self.status = 'success'
        self.completed_at = now
        if self.started_at:
            self.duration_seconds = (now - self.started_at).total_seconds()

        self.records_fetched = records_fetched
        self.records_added = records_added
        self.records_updated = records_updated
        self.records_skipped = records_skipped
        self.has_changes = has_changes
        self.checksum_after = checksum_after

        if ingestion_metadata:
            self.ingestion_metadata = ingestion_metadata

        db.session.commit()

    def mark_failed(self, error_message, error_traceback=None):
        """Mark as failed"""
        now = datetime.utcnow()
        self.status = 'failed'
        self.completed_at = now
        if self.started_at:
            self.duration_seconds = (now - self.started_at).total_seconds()

        self.error_message = error_message
        self.error_traceback = error_traceback
        db.session.commit()

    def mark_skipped(self, reason):
        """Mark as skipped (no changes detected)"""
        now = datetime.utcnow()
        self.status = 'skipped'
        self.completed_at = now
        if self.started_at:
            self.duration_seconds = (now - self.started_at).total_seconds()

        self.ingestion_metadata = {'skip_reason': reason}
        db.session.commit()


class DataSourceConfig(BaseModel):
    """
    Configuration for external data sources

    Store API keys, endpoints, and other configuration per source.
    """
    __tablename__ = 'data_source_configs'

    # Source identification
    source_name = db.Column(db.String(100), nullable=False, unique=True, index=True)
    display_name = db.Column(db.String(200), nullable=False)
    source_type = db.Column(db.String(50), nullable=False)  # api, csv, xml, excel, scraping

    # API Configuration
    base_url = db.Column(db.String(500), nullable=True)
    api_key = db.Column(db.String(500), nullable=True)  # Encrypted in production
    api_secret = db.Column(db.String(500), nullable=True)

    # Connection settings
    timeout_seconds = db.Column(db.Integer, default=30)
    rate_limit_per_hour = db.Column(db.Integer, nullable=True)

    # Authentication
    auth_type = db.Column(db.String(50), nullable=True)  # none, api_key, oauth, basic
    auth_config = db.Column(JSONB, nullable=True)  # Flexible auth configuration

    # Status
    is_active = db.Column(db.Boolean, default=True, index=True)
    last_successful_connection = db.Column(db.DateTime, nullable=True)

    # Additional info
    description = db.Column(db.Text, nullable=True)
    documentation_url = db.Column(db.String(500), nullable=True)
    source_metadata = db.Column(JSONB, nullable=True)

    def __repr__(self):
        return f'<DataSourceConfig {self.source_name}>'
