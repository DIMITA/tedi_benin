"""
Agriculture domain models
"""
from app import db
from app.models.base import BaseModel


class Crop(BaseModel):
    """Crop/Culture model"""
    __tablename__ = 'crops'

    name = db.Column(db.String(100), nullable=False, unique=True, index=True)
    name_fr = db.Column(db.String(100), nullable=True)  # French translation
    scientific_name = db.Column(db.String(200), nullable=True)
    category = db.Column(db.String(50), nullable=True)  # cereals, legumes, tubers, etc.
    fao_code = db.Column(db.String(20), nullable=True, index=True)  # FAO crop code

    # Relationships
    agri_stats = db.relationship('AgriStats', back_populates='crop', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Crop {self.name}>'


class AgriStats(BaseModel):
    """
    Agriculture statistics model
    Links commune + crop + year with production data
    """
    __tablename__ = 'agri_stats'

    # Foreign keys
    commune_id = db.Column(db.Integer, db.ForeignKey('communes.id'), nullable=False, index=True)
    crop_id = db.Column(db.Integer, db.ForeignKey('crops.id'), nullable=False, index=True)
    data_source_id = db.Column(db.Integer, db.ForeignKey('data_sources.id'), nullable=True)

    # Time dimension
    year = db.Column(db.Integer, nullable=False, index=True)

    # Production metrics
    production_tonnes = db.Column(db.Float, nullable=True)  # Total production in tonnes
    yield_tonnes_per_ha = db.Column(db.Float, nullable=True)  # Yield per hectare
    area_harvested_ha = db.Column(db.Float, nullable=True)  # Harvested area in hectares

    # Price metrics
    price_per_kg = db.Column(db.Float, nullable=True)  # Local price per kg
    price_currency = db.Column(db.String(3), default='XOF')  # Currency code

    # Quality indicators
    data_quality_score = db.Column(db.Float, nullable=True)  # 0-1 score
    is_estimated = db.Column(db.Boolean, default=False)  # True if data is estimated/interpolated

    # 🌾 LABELING INDICES (POST-MVP)
    crop_type = db.Column(db.String(50), nullable=True)  # cereals, tubers, cash_crops, vegetables, etc.
    geo_zone = db.Column(db.String(50), nullable=True)  # north, south, coastal, central
    climate_risk_level = db.Column(db.String(20), nullable=True)  # low, medium, high
    soil_quality_index = db.Column(db.Float, nullable=True)  # 0-100 index
    yield_estimation_class = db.Column(db.String(20), nullable=True)  # low, medium, high
    price_volatility_index = db.Column(db.Float, nullable=True)  # 0-100 index
    mechanization_level = db.Column(db.String(20), nullable=True)  # manual, semi_mechanized, mechanized

    # Composite unique constraint
    __table_args__ = (
        db.UniqueConstraint('commune_id', 'crop_id', 'year', name='uq_commune_crop_year'),
        db.Index('idx_commune_year', 'commune_id', 'year'),
        db.Index('idx_crop_year', 'crop_id', 'year'),
    )

    # Relationships
    commune = db.relationship('Commune', back_populates='agri_stats')
    crop = db.relationship('Crop', back_populates='agri_stats')
    data_source = db.relationship('DataSource', back_populates='agri_stats')  # Legacy: primary source

    # Multi-source support (POST-MVP)
    source_contributions = db.relationship('AgriStatsSourceContribution', back_populates='agri_stat', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<AgriStats {self.commune_id}/{self.crop_id}/{self.year}>'

    def to_dict(self, include_relations=False, exclude=None):
        """
        Convert to dictionary with optional relations

        Args:
            include_relations: Include related objects
            exclude: Fields to exclude

        Returns:
            Dictionary representation
        """
        data = super().to_dict(exclude=exclude)

        if include_relations:
            if self.commune:
                data['commune'] = {
                    'id': self.commune.id,
                    'name': self.commune.name
                }
            if self.crop:
                data['crop'] = {
                    'id': self.crop.id,
                    'name': self.crop.name
                }
            if self.data_source:
                data['data_source'] = {
                    'id': self.data_source.id,
                    'name': self.data_source.name
                }

        return data


class AgriStatsSourceContribution(BaseModel):
    """
    Multi-source contribution model for agriculture statistics
    Tracks which data sources contributed to a particular statistic and their weight
    """
    __tablename__ = 'agri_stats_source_contributions'

    # Foreign keys
    agri_stat_id = db.Column(db.Integer, db.ForeignKey('agri_stats.id'), nullable=False, index=True)
    data_source_id = db.Column(db.Integer, db.ForeignKey('data_sources.id'), nullable=False, index=True)

    # Contribution metadata
    contribution_weight = db.Column(db.Float, default=1.0)  # Weight of this source (0-1)
    confidence_score = db.Column(db.Float, nullable=True)  # Confidence in this source's data (0-1)
    is_primary = db.Column(db.Boolean, default=False)  # Is this the primary source?

    # Value tracking (for conflict resolution)
    source_value = db.Column(db.Float, nullable=True)  # Original value from this source
    deviation_from_final = db.Column(db.Float, nullable=True)  # Percentage deviation from final aggregated value

    # Composite unique constraint
    __table_args__ = (
        db.UniqueConstraint('agri_stat_id', 'data_source_id', name='uq_agristat_source'),
        db.Index('idx_agristat_source', 'agri_stat_id', 'data_source_id'),
    )

    # Relationships
    agri_stat = db.relationship('AgriStats', back_populates='source_contributions')
    data_source = db.relationship('DataSource')

    def __repr__(self):
        return f'<AgriStatsSourceContribution agri_stat={self.agri_stat_id} source={self.data_source_id}>'
