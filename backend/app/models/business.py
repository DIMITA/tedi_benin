"""
Business domain models
"""
from app import db
from app.models.base import BaseModel


class BusinessSector(BaseModel):
    """Business sector model (agriculture, retail, services, manufacturing, etc.)"""
    __tablename__ = 'business_sectors'

    name = db.Column(db.String(100), nullable=False, unique=True, index=True)
    name_fr = db.Column(db.String(100), nullable=True)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(50), nullable=True)  # primary, secondary, tertiary

    # Relationships
    business_stats = db.relationship('BusinessStats', back_populates='sector', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<BusinessSector {self.name}>'


class BusinessStats(BaseModel):
    """
    Business statistics model
    Links commune + business sector + time period with business ecosystem data
    """
    __tablename__ = 'business_stats'

    # Foreign keys
    commune_id = db.Column(db.Integer, db.ForeignKey('communes.id'), nullable=False, index=True)
    sector_id = db.Column(db.Integer, db.ForeignKey('business_sectors.id'), nullable=False, index=True)
    data_source_id = db.Column(db.Integer, db.ForeignKey('data_sources.id'), nullable=True)

    # Time dimension
    year = db.Column(db.Integer, nullable=False, index=True)
    quarter = db.Column(db.Integer, nullable=True)  # 1-4 for quarterly data

    # Business metrics
    num_businesses = db.Column(db.Integer, nullable=True)  # Total number of registered businesses
    num_new_businesses = db.Column(db.Integer, nullable=True)  # New businesses this period
    num_closed_businesses = db.Column(db.Integer, nullable=True)  # Closed businesses
    business_birth_rate = db.Column(db.Float, nullable=True)  # Percentage (0-100)
    business_death_rate = db.Column(db.Float, nullable=True)  # Percentage (0-100)

    # Economic metrics
    total_revenue = db.Column(db.Float, nullable=True)  # Total sector revenue
    avg_revenue_per_business = db.Column(db.Float, nullable=True)
    total_employees = db.Column(db.Integer, nullable=True)  # Total employees in sector
    avg_employees_per_business = db.Column(db.Float, nullable=True)
    currency = db.Column(db.String(3), default='XOF')

    # Size distribution
    micro_businesses = db.Column(db.Integer, nullable=True)  # <10 employees
    small_businesses = db.Column(db.Integer, nullable=True)  # 10-49 employees
    medium_businesses = db.Column(db.Integer, nullable=True)  # 50-249 employees
    large_businesses = db.Column(db.Integer, nullable=True)  # 250+ employees

    # Formality metrics
    formal_businesses = db.Column(db.Integer, nullable=True)
    informal_businesses = db.Column(db.Integer, nullable=True)
    formality_rate = db.Column(db.Float, nullable=True)  # Percentage (0-100)

    # Quality indicators
    data_quality_score = db.Column(db.Float, nullable=True)  # 0-1 score
    is_estimated = db.Column(db.Boolean, default=False)

    # 🏢 LABELING INDICES (POST-MVP)
    business_density_index = db.Column(db.Float, nullable=True)  # 0-100 (businesses per 1000 population)
    sector_growth_score = db.Column(db.Float, nullable=True)  # 0-100 (growth rate normalized)
    economic_resilience_index = db.Column(db.Float, nullable=True)  # 0-100 (ability to withstand shocks)
    market_gap_indicator = db.Column(db.Float, nullable=True)  # 0-100 (unmet demand/opportunity score)

    # Additional contextual indices
    competition_intensity = db.Column(db.String(20), nullable=True)  # low, medium, high
    market_saturation = db.Column(db.String(20), nullable=True)  # undersaturated, balanced, saturated, oversaturated
    innovation_score = db.Column(db.Float, nullable=True)  # 0-100
    digital_adoption_rate = db.Column(db.Float, nullable=True)  # 0-100%

    # Composite unique constraint
    __table_args__ = (
        db.UniqueConstraint('commune_id', 'sector_id', 'year', 'quarter', name='uq_commune_sector_year_quarter'),
        db.Index('idx_commune_year_biz', 'commune_id', 'year'),
        db.Index('idx_sector_year', 'sector_id', 'year'),
    )

    # Relationships
    commune = db.relationship('Commune', back_populates='business_stats')
    sector = db.relationship('BusinessSector', back_populates='business_stats')
    data_source = db.relationship('DataSource', back_populates='business_stats')

    # Multi-source support
    source_contributions = db.relationship('BusinessSourceContribution', back_populates='business_stat', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<BusinessStats {self.commune_id}/{self.sector_id}/{self.year}>'

    def to_dict(self, include_relations=False, exclude=None):
        """Convert to dictionary with optional relations"""
        data = super().to_dict(exclude=exclude)

        if include_relations:
            if self.commune:
                data['commune'] = {
                    'id': self.commune.id,
                    'name': self.commune.name
                }
            if self.sector:
                data['sector'] = {
                    'id': self.sector.id,
                    'name': self.sector.name
                }
            if self.data_source:
                data['data_source'] = {
                    'id': self.data_source.id,
                    'name': self.data_source.name
                }

        return data


class BusinessSourceContribution(BaseModel):
    """
    Multi-source contribution model for business statistics
    """
    __tablename__ = 'business_source_contributions'

    # Foreign keys
    business_stat_id = db.Column(db.Integer, db.ForeignKey('business_stats.id'), nullable=False, index=True)
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
        db.UniqueConstraint('business_stat_id', 'data_source_id', name='uq_business_source'),
        db.Index('idx_business_source', 'business_stat_id', 'data_source_id'),
    )

    # Relationships
    business_stat = db.relationship('BusinessStats', back_populates='source_contributions')
    data_source = db.relationship('DataSource')

    def __repr__(self):
        return f'<BusinessSourceContribution biz_stat={self.business_stat_id} source={self.data_source_id}>'
