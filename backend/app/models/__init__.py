"""
Database models package
"""
from app.models.base import BaseModel
from app.models.geo import Country, Region, Commune
from app.models.agriculture import Crop, AgriStats, AgriStatsSourceContribution
from app.models.metadata import DataSource, DatasetVersion
from app.models.auth import ApiKey
from app.models.ingestion import IngestionLog, DataSourceConfig

# POST-MVP: New verticals
from app.models.realestate import PropertyType, RealEstateStats, RealEstateSourceContribution
from app.models.employment import JobCategory, EmploymentStats, EmploymentSourceContribution
from app.models.business import BusinessSector, BusinessStats, BusinessSourceContribution

__all__ = [
    'BaseModel',
    'Country',
    'Region',
    'Commune',
    'Crop',
    'AgriStats',
    'AgriStatsSourceContribution',
    'DataSource',
    'DatasetVersion',
    'IngestionLog',
    'DataSourceConfig',
    'ApiKey',
    # Real Estate
    'PropertyType',
    'RealEstateStats',
    'RealEstateSourceContribution',
    # Employment
    'JobCategory',
    'EmploymentStats',
    'EmploymentSourceContribution',
    # Business
    'BusinessSector',
    'BusinessStats',
    'BusinessSourceContribution',
]
