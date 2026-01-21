"""
Data source metadata models
"""
from app import db
from app.models.base import BaseModel


class DataSource(BaseModel):
    """Data source metadata model"""
    __tablename__ = 'data_sources'

    name = db.Column(db.String(200), nullable=False, unique=True)
    url = db.Column(db.String(500), nullable=True)
    description = db.Column(db.Text, nullable=True)
    license = db.Column(db.String(100), nullable=True)  # e.g., "CC BY 4.0", "Open Data"
    organization = db.Column(db.String(200), nullable=True)  # e.g., "FAO", "World Bank"

    # Source type
    source_type = db.Column(
        db.String(50),
        nullable=False,
        default='external'
    )  # external, internal, computed

    # Contact & metadata
    contact_email = db.Column(db.String(200), nullable=True)
    last_updated = db.Column(db.Date, nullable=True)
    update_frequency = db.Column(db.String(50), nullable=True)  # daily, weekly, monthly, yearly

    # Status
    is_active = db.Column(db.Boolean, default=True)

    # Relationships
    dataset_versions = db.relationship('DatasetVersion', back_populates='data_source', cascade='all, delete-orphan')
    agri_stats = db.relationship('AgriStats', back_populates='data_source')

    # POST-MVP: New vertical relationships
    real_estate_stats = db.relationship('RealEstateStats', back_populates='data_source')
    employment_stats = db.relationship('EmploymentStats', back_populates='data_source')
    business_stats = db.relationship('BusinessStats', back_populates='data_source')

    def __repr__(self):
        return f'<DataSource {self.name}>'


class DatasetVersion(BaseModel):
    """
    Dataset version tracking model with automated ingestion scheduling

    Tracks dataset versions, checksums, and scheduling for automated data ingestion.
    """
    __tablename__ = 'dataset_versions'

    data_source_id = db.Column(db.Integer, db.ForeignKey('data_sources.id'), nullable=False, index=True)

    # Version info
    version = db.Column(db.String(50), nullable=False)
    release_date = db.Column(db.Date, nullable=False)

    # File metadata
    file_path = db.Column(db.String(500), nullable=True)  # Path to stored file
    file_size_bytes = db.Column(db.BigInteger, nullable=True)
    checksum = db.Column(db.String(64), nullable=True)  # SHA-256 checksum

    # Processing metadata
    records_count = db.Column(db.Integer, nullable=True)
    processing_status = db.Column(
        db.String(50),
        nullable=False,
        default='pending'
    )  # pending, processing, completed, failed
    processing_started_at = db.Column(db.DateTime, nullable=True)
    processing_completed_at = db.Column(db.DateTime, nullable=True)
    processing_errors = db.Column(db.Text, nullable=True)

    # Notes
    notes = db.Column(db.Text, nullable=True)

    # AUTO-INGESTION: Scheduling fields
    last_checked_at = db.Column(db.DateTime, nullable=True)  # Last time we checked for updates
    last_updated_at = db.Column(db.DateTime, nullable=True)  # Last time data actually changed
    next_check_at = db.Column(db.DateTime, nullable=True)  # Scheduled next check
    check_enabled = db.Column(db.Boolean, default=True, index=True)  # Enable/disable auto-check

    # AUTO-INGESTION: Reliability tracking
    source_reliability_score = db.Column(db.Float, nullable=True)  # 0.0 to 1.0
    consecutive_failures = db.Column(db.Integer, default=0)
    last_error = db.Column(db.Text, nullable=True)

    # AUTO-INGESTION: Ingestion stats
    last_ingestion_duration_seconds = db.Column(db.Float, nullable=True)
    last_records_added = db.Column(db.Integer, nullable=True)
    last_records_updated = db.Column(db.Integer, nullable=True)

    # Relationships
    data_source = db.relationship('DataSource', back_populates='dataset_versions')

    # Composite unique constraint
    __table_args__ = (
        db.UniqueConstraint('data_source_id', 'version', name='uq_source_version'),
    )

    def __repr__(self):
        return f'<DatasetVersion {self.data_source_id} v{self.version}>'

    def should_check(self):
        """Determine if it's time to check this dataset"""
        from datetime import datetime

        if not self.check_enabled:
            return False

        if self.consecutive_failures >= 5:
            # Stop checking after 5 consecutive failures
            return False

        if not self.next_check_at:
            return True

        return datetime.utcnow() >= self.next_check_at

    def calculate_next_check(self):
        """Calculate when to check next based on source's update_frequency"""
        from datetime import datetime, timedelta

        now = datetime.utcnow()

        if not self.data_source or not self.data_source.update_frequency:
            # Default to monthly if not specified
            return now + timedelta(days=30)

        frequency_map = {
            'daily': timedelta(days=1),
            'weekly': timedelta(weeks=1),
            'monthly': timedelta(days=30),
            'quarterly': timedelta(days=90),
            'annual': timedelta(days=365),
        }

        delta = frequency_map.get(self.data_source.update_frequency, timedelta(days=30))
        return now + delta

    def mark_checked(self, has_changes=False, new_checksum=None,
                    records_added=0, records_updated=0, duration_seconds=0, error=None):
        """Mark dataset as checked and optionally updated"""
        from datetime import datetime

        now = datetime.utcnow()
        self.last_checked_at = now

        if error:
            self.consecutive_failures += 1
            self.last_error = str(error)
        else:
            self.consecutive_failures = 0
            self.last_error = None

            if has_changes:
                self.last_updated_at = now
                if new_checksum:
                    self.checksum = new_checksum
                self.last_records_added = records_added
                self.last_records_updated = records_updated

            self.last_ingestion_duration_seconds = duration_seconds

        self.next_check_at = self.calculate_next_check()
        db.session.commit()
