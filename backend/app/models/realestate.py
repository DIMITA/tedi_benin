"""
Real Estate domain models
"""
from app import db
from app.models.base import BaseModel


class PropertyType(BaseModel):
    """Property type model (residential, commercial, agricultural, industrial)"""
    __tablename__ = 'property_types'

    name = db.Column(db.String(100), nullable=False, unique=True, index=True)
    name_fr = db.Column(db.String(100), nullable=True)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(50), nullable=True)  # residential, commercial, agricultural, industrial, mixed

    # Relationships
    real_estate_stats = db.relationship('RealEstateStats', back_populates='property_type', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<PropertyType {self.name}>'


class RealEstateStats(BaseModel):
    """
    Real Estate statistics model
    Links commune + property type + time period with market data
    """
    __tablename__ = 'real_estate_stats'

    # Foreign keys
    commune_id = db.Column(db.Integer, db.ForeignKey('communes.id'), nullable=False, index=True)
    property_type_id = db.Column(db.Integer, db.ForeignKey('property_types.id'), nullable=False, index=True)
    data_source_id = db.Column(db.Integer, db.ForeignKey('data_sources.id'), nullable=True)

    # Time dimension
    year = db.Column(db.Integer, nullable=False, index=True)
    quarter = db.Column(db.Integer, nullable=True)  # 1-4 for quarterly data

    # Price metrics
    median_price = db.Column(db.Float, nullable=True)  # Median property price
    price_per_sqm = db.Column(db.Float, nullable=True)  # Price per square meter
    min_price = db.Column(db.Float, nullable=True)
    max_price = db.Column(db.Float, nullable=True)
    currency = db.Column(db.String(3), default='XOF')

    # Transaction metrics
    num_transactions = db.Column(db.Integer, nullable=True)  # Number of transactions
    transaction_volume = db.Column(db.Float, nullable=True)  # Total transaction volume in currency

    # Market metrics
    inventory_count = db.Column(db.Integer, nullable=True)  # Number of properties available
    days_on_market = db.Column(db.Float, nullable=True)  # Average days to sell/rent
    rental_yield = db.Column(db.Float, nullable=True)  # Annual rental yield percentage

    # Quality indicators
    data_quality_score = db.Column(db.Float, nullable=True)  # 0-1 score
    is_estimated = db.Column(db.Boolean, default=False)

    # 🏠 LABELING INDICES (POST-MVP)
    property_type_label = db.Column(db.String(50), nullable=True)  # residential, commercial, agricultural, industrial, mixed
    geo_zone = db.Column(db.String(50), nullable=True)  # urban, peri_urban, rural
    price_per_sqm_index = db.Column(db.Float, nullable=True)  # Normalized 0-100 index
    price_trend = db.Column(db.String(20), nullable=True)  # decreasing, stable, increasing, increasing_strong
    land_risk_level = db.Column(db.String(20), nullable=True)  # low, medium, high
    infrastructure_score = db.Column(db.Float, nullable=True)  # 0-100 (roads, water, electricity, internet)
    legal_clarity_index = db.Column(db.Float, nullable=True)  # 0-100 (title clarity, zoning, permits)
    development_potential = db.Column(db.String(20), nullable=True)  # low, medium, high, very_high

    # Composite unique constraint
    __table_args__ = (
        db.UniqueConstraint('commune_id', 'property_type_id', 'year', 'quarter', name='uq_commune_property_year_quarter'),
        db.Index('idx_commune_year_re', 'commune_id', 'year'),
        db.Index('idx_property_year', 'property_type_id', 'year'),
    )

    # Relationships
    commune = db.relationship('Commune', back_populates='real_estate_stats')
    property_type = db.relationship('PropertyType', back_populates='real_estate_stats')
    data_source = db.relationship('DataSource', back_populates='real_estate_stats')

    # Multi-source support
    source_contributions = db.relationship('RealEstateSourceContribution', back_populates='real_estate_stat', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<RealEstateStats {self.commune_id}/{self.property_type_id}/{self.year}>'

    def to_dict(self, include_relations=False, exclude=None):
        """Convert to dictionary with optional relations"""
        data = super().to_dict(exclude=exclude)

        if include_relations:
            if self.commune:
                data['commune'] = {
                    'id': self.commune.id,
                    'name': self.commune.name
                }
            if self.property_type:
                data['property_type'] = {
                    'id': self.property_type.id,
                    'name': self.property_type.name
                }
            if self.data_source:
                data['data_source'] = {
                    'id': self.data_source.id,
                    'name': self.data_source.name
                }

        return data


class RealEstateSourceContribution(BaseModel):
    """
    Multi-source contribution model for real estate statistics
    """
    __tablename__ = 'real_estate_source_contributions'

    # Foreign keys
    real_estate_stat_id = db.Column(db.Integer, db.ForeignKey('real_estate_stats.id'), nullable=False, index=True)
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
        db.UniqueConstraint('real_estate_stat_id', 'data_source_id', name='uq_realestate_source'),
        db.Index('idx_realestate_source', 'real_estate_stat_id', 'data_source_id'),
    )

    # Relationships
    real_estate_stat = db.relationship('RealEstateStats', back_populates='source_contributions')
    data_source = db.relationship('DataSource')

    def __repr__(self):
        return f'<RealEstateSourceContribution re_stat={self.real_estate_stat_id} source={self.data_source_id}>'
