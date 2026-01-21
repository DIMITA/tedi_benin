"""
Geographic models with PostGIS support
"""
from app import db
from app.models.base import BaseModel
from geoalchemy2 import Geometry
from geoalchemy2.shape import to_shape
import json


class Country(BaseModel):
    """Country model"""
    __tablename__ = 'countries'

    name = db.Column(db.String(100), nullable=False, unique=True)
    iso_code = db.Column(db.String(3), nullable=False, unique=True, index=True)
    iso_code_2 = db.Column(db.String(2), nullable=True)

    # Relationships
    regions = db.relationship('Region', back_populates='country', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Country {self.name} ({self.iso_code})>'


class Region(BaseModel):
    """Region/Department model"""
    __tablename__ = 'regions'

    name = db.Column(db.String(100), nullable=False)
    country_id = db.Column(db.Integer, db.ForeignKey('countries.id'), nullable=False, index=True)

    # Relationships
    country = db.relationship('Country', back_populates='regions')
    communes = db.relationship('Commune', back_populates='region', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Region {self.name}>'


class Commune(BaseModel):
    """Commune/Municipality model with PostGIS geometry"""
    __tablename__ = 'communes'

    name = db.Column(db.String(100), nullable=False)
    region_id = db.Column(db.Integer, db.ForeignKey('regions.id'), nullable=False, index=True)

    # PostGIS geometry field (polygon)
    geometry = db.Column(
        Geometry(geometry_type='MULTIPOLYGON', srid=4326),
        nullable=True
    )

    # Center point for quick map display
    center_lat = db.Column(db.Float, nullable=True)
    center_lon = db.Column(db.Float, nullable=True)

    # Additional properties
    population = db.Column(db.Integer, nullable=True)
    area_km2 = db.Column(db.Float, nullable=True)

    # Relationships
    region = db.relationship('Region', back_populates='communes')
    agri_stats = db.relationship('AgriStats', back_populates='commune', cascade='all, delete-orphan')

    # POST-MVP: New vertical relationships
    real_estate_stats = db.relationship('RealEstateStats', back_populates='commune', cascade='all, delete-orphan')
    employment_stats = db.relationship('EmploymentStats', back_populates='commune', cascade='all, delete-orphan')
    business_stats = db.relationship('BusinessStats', back_populates='commune', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Commune {self.name}>'

    def to_dict(self, include_geometry=False, exclude=None):
        """
        Convert to dictionary with optional geometry

        Args:
            include_geometry: Include GeoJSON geometry
            exclude: Fields to exclude

        Returns:
            Dictionary representation
        """
        data = super().to_dict(exclude=exclude)

        if include_geometry and self.geometry is not None:
            # Convert PostGIS geometry to GeoJSON
            shape = to_shape(self.geometry)
            data['geometry'] = json.loads(json.dumps(shape.__geo_interface__))
        else:
            # Remove geometry field
            data.pop('geometry', None)

        return data
