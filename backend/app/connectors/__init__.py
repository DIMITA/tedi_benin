"""
External data source connectors

Each connector implements the ETL pattern:
- Extract (fetch): Get data from external source
- Transform: Convert to TEDI schema
- Load: Insert into database
"""
from app.connectors.base import BaseConnector

__all__ = ['BaseConnector']
