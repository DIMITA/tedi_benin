-- Initialize TEDI Database with PostGIS extension

-- Enable PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;

-- Verify PostGIS installation
SELECT PostGIS_Version();

-- Create schema for TEDI
CREATE SCHEMA IF NOT EXISTS tedi;

-- Grant privileges
GRANT ALL PRIVILEGES ON SCHEMA tedi TO tedi_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA tedi TO tedi_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA tedi TO tedi_user;

-- Set search path
ALTER DATABASE tedi_db SET search_path TO tedi, public;
