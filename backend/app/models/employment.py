"""
Employment domain models
"""
from app import db
from app.models.base import BaseModel


class JobCategory(BaseModel):
    """Job category model (agriculture, services, industry, commerce, etc.)"""
    __tablename__ = 'job_categories'

    name = db.Column(db.String(100), nullable=False, unique=True, index=True)
    name_fr = db.Column(db.String(100), nullable=True)
    description = db.Column(db.Text, nullable=True)
    sector = db.Column(db.String(50), nullable=True)  # primary, secondary, tertiary

    # Relationships
    employment_stats = db.relationship('EmploymentStats', back_populates='job_category', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<JobCategory {self.name}>'


class EmploymentStats(BaseModel):
    """
    Employment statistics model
    Links commune + job category + time period with employment data
    """
    __tablename__ = 'employment_stats'

    # Foreign keys
    commune_id = db.Column(db.Integer, db.ForeignKey('communes.id'), nullable=False, index=True)
    job_category_id = db.Column(db.Integer, db.ForeignKey('job_categories.id'), nullable=False, index=True)
    data_source_id = db.Column(db.Integer, db.ForeignKey('data_sources.id'), nullable=True)

    # Time dimension
    year = db.Column(db.Integer, nullable=False, index=True)
    quarter = db.Column(db.Integer, nullable=True)  # 1-4 for quarterly data

    # Employment metrics
    total_employed = db.Column(db.Integer, nullable=True)  # Total number of people employed
    total_unemployed = db.Column(db.Integer, nullable=True)  # Number of unemployed
    labor_force = db.Column(db.Integer, nullable=True)  # Total labor force
    unemployment_rate = db.Column(db.Float, nullable=True)  # Percentage (0-100)
    participation_rate = db.Column(db.Float, nullable=True)  # Labor force participation rate (0-100)

    # Informal sector metrics
    informal_employed = db.Column(db.Integer, nullable=True)  # Number in informal sector
    informal_rate = db.Column(db.Float, nullable=True)  # Percentage (0-100)

    # Salary metrics
    median_salary = db.Column(db.Float, nullable=True)  # Median monthly salary
    min_salary = db.Column(db.Float, nullable=True)
    max_salary = db.Column(db.Float, nullable=True)
    currency = db.Column(db.String(3), default='XOF')

    # Demographics
    youth_employment = db.Column(db.Integer, nullable=True)  # 15-24 years
    female_employment = db.Column(db.Integer, nullable=True)

    # Quality indicators
    data_quality_score = db.Column(db.Float, nullable=True)  # 0-1 score
    is_estimated = db.Column(db.Boolean, default=False)

    # 💼 LABELING INDICES (POST-MVP)
    job_category_label = db.Column(db.String(50), nullable=True)  # agriculture, services, industry, commerce, education, health, etc.
    skill_level_index = db.Column(db.Float, nullable=True)  # 0-100 index (low skill to high skill)
    employment_pressure_index = db.Column(db.Float, nullable=True)  # 0-100 (low pressure = plenty of jobs, high = scarce)
    informality_rate_index = db.Column(db.Float, nullable=True)  # 0-100% (percentage of informal employment)
    salary_range_estimation = db.Column(db.String(20), nullable=True)  # low, medium, high, very_high

    # Composite unique constraint
    __table_args__ = (
        db.UniqueConstraint('commune_id', 'job_category_id', 'year', 'quarter', name='uq_commune_job_year_quarter'),
        db.Index('idx_commune_year_emp', 'commune_id', 'year'),
        db.Index('idx_job_year', 'job_category_id', 'year'),
    )

    # Relationships
    commune = db.relationship('Commune', back_populates='employment_stats')
    job_category = db.relationship('JobCategory', back_populates='employment_stats')
    data_source = db.relationship('DataSource', back_populates='employment_stats')

    # Multi-source support
    source_contributions = db.relationship('EmploymentSourceContribution', back_populates='employment_stat', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<EmploymentStats {self.commune_id}/{self.job_category_id}/{self.year}>'

    def to_dict(self, include_relations=False, exclude=None):
        """Convert to dictionary with optional relations"""
        data = super().to_dict(exclude=exclude)

        if include_relations:
            if self.commune:
                data['commune'] = {
                    'id': self.commune.id,
                    'name': self.commune.name
                }
            if self.job_category:
                data['job_category'] = {
                    'id': self.job_category.id,
                    'name': self.job_category.name
                }
            if self.data_source:
                data['data_source'] = {
                    'id': self.data_source.id,
                    'name': self.data_source.name
                }

        return data


class EmploymentSourceContribution(BaseModel):
    """
    Multi-source contribution model for employment statistics
    """
    __tablename__ = 'employment_source_contributions'

    # Foreign keys
    employment_stat_id = db.Column(db.Integer, db.ForeignKey('employment_stats.id'), nullable=False, index=True)
    data_source_id = db.Column(db.Integer, db.ForeignKey('data_sources.id'), nullable=False, index=True)

    # Contribution metadata
    contribution_weight = db.Column(db.Float, default=1.0)
    confidence_score = db.Column(db.Float, nullable=True)
    is_primary = db.Column(db.Boolean, default=False)

    # Value tracking
    source_value = db.Column(db.Float, nullable=True)
    deviation_from_final = db.Column(db.Float, nullable=True)

    # Composite unique constraint
    __table_args__ = (
        db.UniqueConstraint('employment_stat_id', 'data_source_id', name='uq_employment_source'),
        db.Index('idx_employment_source', 'employment_stat_id', 'data_source_id'),
    )

    # Relationships
    employment_stat = db.relationship('EmploymentStats', back_populates='source_contributions')
    data_source = db.relationship('DataSource')

    def __repr__(self):
        return f'<EmploymentSourceContribution emp_stat={self.employment_stat_id} source={self.data_source_id}>'
