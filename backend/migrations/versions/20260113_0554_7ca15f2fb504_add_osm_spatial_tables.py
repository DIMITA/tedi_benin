"""add_osm_spatial_tables

Revision ID: 7ca15f2fb504
Revises: 3375de8c53eb
Create Date: 2026-01-13 05:54:58.642258

Adds spatial tables for OpenStreetMap data:
- osm_buildings: Building footprints and metadata
- osm_land_use: Land use polygons
- osm_amenities: Points of interest (schools, hospitals, markets, etc.)
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from geoalchemy2 import Geometry


# revision identifiers, used by Alembic.
revision = '7ca15f2fb504'
down_revision = '3375de8c53eb'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create osm_buildings table
    op.create_table(
        'osm_buildings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),

        # OSM metadata
        sa.Column('osm_id', sa.BigInteger(), nullable=False, index=True),
        sa.Column('osm_type', sa.String(20), nullable=True),  # node, way, relation
        sa.Column('osm_version', sa.Integer(), nullable=True),
        sa.Column('osm_timestamp', sa.DateTime(), nullable=True),

        # Building info
        sa.Column('building_type', sa.String(100), nullable=True),  # residential, commercial, school, hospital, etc.
        sa.Column('name', sa.String(200), nullable=True),
        sa.Column('name_fr', sa.String(200), nullable=True),
        sa.Column('addr_full', sa.Text(), nullable=True),
        sa.Column('addr_city', sa.String(100), nullable=True),

        # Geometry
        sa.Column('geometry', Geometry(geometry_type='GEOMETRY', srid=4326), nullable=True),
        sa.Column('centroid', Geometry(geometry_type='POINT', srid=4326), nullable=True),
        sa.Column('area_sqm', sa.Float(), nullable=True),

        # Building characteristics
        sa.Column('levels', sa.Integer(), nullable=True),  # Number of floors
        sa.Column('height', sa.Float(), nullable=True),  # Height in meters
        sa.Column('material', sa.String(50), nullable=True),  # concrete, brick, wood, etc.
        sa.Column('roof_material', sa.String(50), nullable=True),

        # Foreign keys
        sa.Column('commune_id', sa.Integer(), sa.ForeignKey('communes.id'), nullable=True, index=True),
        sa.Column('data_source_id', sa.Integer(), sa.ForeignKey('data_sources.id'), nullable=True),

        # Quality tracking
        sa.Column('data_quality_score', sa.Float(), nullable=True),
        sa.Column('is_verified', sa.Boolean(), default=False),

        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('osm_id', 'osm_type', name='uq_osm_building')
    )

    # Create spatial indexes for osm_buildings
    # Note: Geometry columns automatically create GIST indexes
    op.create_index('idx_osm_buildings_type', 'osm_buildings', ['building_type'])
    op.create_index('idx_osm_buildings_commune', 'osm_buildings', ['commune_id'])

    # Create osm_land_use table
    op.create_table(
        'osm_land_use',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),

        # OSM metadata
        sa.Column('osm_id', sa.BigInteger(), nullable=False, index=True),
        sa.Column('osm_type', sa.String(20), nullable=True),
        sa.Column('osm_version', sa.Integer(), nullable=True),
        sa.Column('osm_timestamp', sa.DateTime(), nullable=True),

        # Land use info
        sa.Column('land_use_type', sa.String(100), nullable=True),  # residential, commercial, industrial, agricultural, forest, etc.
        sa.Column('name', sa.String(200), nullable=True),
        sa.Column('name_fr', sa.String(200), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),

        # Geometry
        sa.Column('geometry', Geometry(geometry_type='GEOMETRY', srid=4326), nullable=True),
        sa.Column('centroid', Geometry(geometry_type='POINT', srid=4326), nullable=True),
        sa.Column('area_sqm', sa.Float(), nullable=True),
        sa.Column('perimeter_m', sa.Float(), nullable=True),

        # Foreign keys
        sa.Column('commune_id', sa.Integer(), sa.ForeignKey('communes.id'), nullable=True, index=True),
        sa.Column('data_source_id', sa.Integer(), sa.ForeignKey('data_sources.id'), nullable=True),

        # Quality tracking
        sa.Column('data_quality_score', sa.Float(), nullable=True),
        sa.Column('is_verified', sa.Boolean(), default=False),

        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('osm_id', 'osm_type', name='uq_osm_land_use')
    )

    # Create spatial indexes for osm_land_use
    # Note: Geometry columns automatically create GIST indexes
    op.create_index('idx_osm_land_use_type', 'osm_land_use', ['land_use_type'])
    op.create_index('idx_osm_land_use_commune', 'osm_land_use', ['commune_id'])

    # Create osm_amenities table
    op.create_table(
        'osm_amenities',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),

        # OSM metadata
        sa.Column('osm_id', sa.BigInteger(), nullable=False, index=True),
        sa.Column('osm_type', sa.String(20), nullable=True),
        sa.Column('osm_version', sa.Integer(), nullable=True),
        sa.Column('osm_timestamp', sa.DateTime(), nullable=True),

        # Amenity info
        sa.Column('amenity_type', sa.String(100), nullable=True),  # school, hospital, market, bank, restaurant, etc.
        sa.Column('category', sa.String(50), nullable=True),  # education, health, commercial, financial, etc.
        sa.Column('name', sa.String(200), nullable=True),
        sa.Column('name_fr', sa.String(200), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),

        # Contact info
        sa.Column('phone', sa.String(50), nullable=True),
        sa.Column('website', sa.String(500), nullable=True),
        sa.Column('opening_hours', sa.String(200), nullable=True),

        # Location
        sa.Column('geometry', Geometry(geometry_type='POINT', srid=4326), nullable=True),
        sa.Column('addr_full', sa.Text(), nullable=True),
        sa.Column('addr_city', sa.String(100), nullable=True),

        # Foreign keys
        sa.Column('commune_id', sa.Integer(), sa.ForeignKey('communes.id'), nullable=True, index=True),
        sa.Column('data_source_id', sa.Integer(), sa.ForeignKey('data_sources.id'), nullable=True),

        # Quality tracking
        sa.Column('data_quality_score', sa.Float(), nullable=True),
        sa.Column('is_verified', sa.Boolean(), default=False),

        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('osm_id', 'osm_type', name='uq_osm_amenity')
    )

    # Create spatial index for osm_amenities
    # Note: Geometry column automatically creates GIST index
    op.create_index('idx_osm_amenities_type', 'osm_amenities', ['amenity_type'])
    op.create_index('idx_osm_amenities_category', 'osm_amenities', ['category'])
    op.create_index('idx_osm_amenities_commune', 'osm_amenities', ['commune_id'])


def downgrade() -> None:
    # Drop indexes first
    op.drop_index('idx_osm_amenities_commune', table_name='osm_amenities')
    op.drop_index('idx_osm_amenities_category', table_name='osm_amenities')
    op.drop_index('idx_osm_amenities_type', table_name='osm_amenities')

    op.drop_index('idx_osm_land_use_commune', table_name='osm_land_use')
    op.drop_index('idx_osm_land_use_type', table_name='osm_land_use')

    op.drop_index('idx_osm_buildings_commune', table_name='osm_buildings')
    op.drop_index('idx_osm_buildings_type', table_name='osm_buildings')

    # Drop tables (GIST indexes on geometry columns will be dropped automatically)
    op.drop_table('osm_amenities')
    op.drop_table('osm_land_use')
    op.drop_table('osm_buildings')
