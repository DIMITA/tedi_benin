"""
OpenStreetMap (OSM) Connector

Fetches property and infrastructure data from OpenStreetMap API (Overpass API).

API Documentation: https://wiki.openstreetmap.org/wiki/Overpass_API
"""
from typing import List, Dict, Any
from app.connectors.base import BaseConnector
from app.models import Commune, DataSource
from app import db
from geoalchemy2.shape import from_shape
from shapely.geometry import shape


class OSMConnector(BaseConnector):
    """
    Connector for OpenStreetMap Overpass API

    Fetches building footprints, land use, and infrastructure data.
    """

    OVERPASS_URL = "https://overpass-api.de/api/interpreter"

    def __init__(self, country_code="BJ", bbox=None, **kwargs):
        """
        Initialize OSM connector

        Args:
            country_code: ISO2 country code (default: BJ for Benin)
            bbox: Bounding box [south, west, north, east] (default: Benin bbox)
            **kwargs: Additional configuration
        """
        super().__init__(**kwargs)

        self.country_code = country_code
        # Default bounding box for Benin
        self.bbox = bbox or [6.2, 0.77, 12.4, 3.85]  # [south, west, north, east]

    def fetch(self) -> Dict:
        """
        Fetch data from OpenStreetMap using Overpass API

        Returns:
            Dictionary with buildings, land use, and amenities data
        """
        print(f"📥 Fetching OpenStreetMap data for {self.country_code}")

        data = {
            'buildings': self._fetch_buildings(),
            'land_use': self._fetch_land_use(),
            'amenities': self._fetch_amenities(),
        }

        return data

    def _fetch_buildings(self) -> List[Dict]:
        """
        Fetch building footprints from OSM

        Returns:
            List of building records
        """
        # Overpass QL query for buildings
        query = f"""
        [out:json][timeout:60];
        (
          way["building"]({self.bbox[0]},{self.bbox[1]},{self.bbox[2]},{self.bbox[3]});
          relation["building"]({self.bbox[0]},{self.bbox[1]},{self.bbox[2]},{self.bbox[3]});
        );
        out geom;
        """

        try:
            response = self.session.post(
                self.OVERPASS_URL,
                data={'data': query},
                timeout=120  # Overpass can be slow
            )
            response.raise_for_status()
            result = response.json()

            return result.get('elements', [])

        except Exception as e:
            print(f"⚠️  Error fetching buildings: {str(e)}")
            return []

    def _fetch_land_use(self) -> List[Dict]:
        """
        Fetch land use data from OSM

        Returns:
            List of land use records
        """
        query = f"""
        [out:json][timeout:60];
        (
          way["landuse"]({self.bbox[0]},{self.bbox[1]},{self.bbox[2]},{self.bbox[3]});
          relation["landuse"]({self.bbox[0]},{self.bbox[1]},{self.bbox[2]},{self.bbox[3]});
        );
        out geom;
        """

        try:
            response = self.session.post(
                self.OVERPASS_URL,
                data={'data': query},
                timeout=120
            )
            response.raise_for_status()
            result = response.json()

            return result.get('elements', [])

        except Exception as e:
            print(f"⚠️  Error fetching land use: {str(e)}")
            return []

    def _fetch_amenities(self) -> List[Dict]:
        """
        Fetch amenities (schools, hospitals, markets, etc.) from OSM

        Returns:
            List of amenity records
        """
        query = f"""
        [out:json][timeout:60];
        (
          node["amenity"]({self.bbox[0]},{self.bbox[1]},{self.bbox[2]},{self.bbox[3]});
          way["amenity"]({self.bbox[0]},{self.bbox[1]},{self.bbox[2]},{self.bbox[3]});
        );
        out geom;
        """

        try:
            response = self.session.post(
                self.OVERPASS_URL,
                data={'data': query},
                timeout=120
            )
            response.raise_for_status()
            result = response.json()

            return result.get('elements', [])

        except Exception as e:
            print(f"⚠️  Error fetching amenities: {str(e)}")
            return []

    def transform(self, raw_data: Dict) -> List[Dict]:
        """
        Transform OSM data to TEDI schema

        Args:
            raw_data: Raw data from fetch()

        Returns:
            List of dictionaries in TEDI schema
        """
        print("🔄 Transforming OpenStreetMap data to TEDI schema")

        transformed = []

        # Process buildings
        for building in raw_data.get('buildings', []):
            tags = building.get('tags', {})

            # Extract geometry
            geometry = self._extract_geometry(building)

            if geometry:
                transformed.append({
                    'type': 'building',
                    'osm_id': building.get('id'),
                    'osm_type': building.get('type'),
                    'building_type': tags.get('building', 'yes'),
                    'name': tags.get('name'),
                    'addr_full': self._build_address(tags),
                    'geometry': geometry,
                    'levels': self.clean_numeric(tags.get('building:levels')),
                    'area_sqm': self._calculate_area(geometry),
                })

        # Process land use
        for land in raw_data.get('land_use', []):
            tags = land.get('tags', {})
            geometry = self._extract_geometry(land)

            if geometry:
                transformed.append({
                    'type': 'land_use',
                    'osm_id': land.get('id'),
                    'osm_type': land.get('type'),
                    'land_use_type': tags.get('landuse'),
                    'name': tags.get('name'),
                    'geometry': geometry,
                    'area_sqm': self._calculate_area(geometry),
                })

        # Process amenities
        for amenity in raw_data.get('amenities', []):
            tags = amenity.get('tags', {})
            geometry = self._extract_geometry(amenity)

            if geometry:
                transformed.append({
                    'type': 'amenity',
                    'osm_id': amenity.get('id'),
                    'osm_type': amenity.get('type'),
                    'amenity_type': tags.get('amenity'),
                    'name': tags.get('name'),
                    'geometry': geometry,
                })

        print(f"✅ Transformed {len(transformed)} records")
        return transformed

    def _extract_geometry(self, element: Dict) -> Dict:
        """Extract geometry from OSM element"""
        if element.get('type') == 'node':
            return {
                'type': 'Point',
                'coordinates': [element.get('lon'), element.get('lat')]
            }
        elif element.get('type') in ['way', 'relation']:
            # Extract coordinates from geometry
            if 'geometry' in element:
                coords = [[p.get('lon'), p.get('lat')] for p in element['geometry']]
                return {
                    'type': 'Polygon',
                    'coordinates': [coords]
                }

        return None

    def _build_address(self, tags: Dict) -> str:
        """Build full address from OSM tags"""
        parts = []

        if tags.get('addr:housenumber'):
            parts.append(tags['addr:housenumber'])
        if tags.get('addr:street'):
            parts.append(tags['addr:street'])
        if tags.get('addr:city'):
            parts.append(tags['addr:city'])

        return ', '.join(parts) if parts else None

    def _calculate_area(self, geometry: Dict) -> float:
        """
        Calculate approximate area in square meters

        Note: This is a rough approximation. For production, use PostGIS ST_Area.
        """
        # TODO: Use PostGIS for accurate area calculation
        return None

    def load(self, transformed_data: List[Dict]) -> Dict:
        """
        Load transformed data into TEDI database

        Uses PostGIS spatial tables to store OSM data:
        - osm_buildings: Building footprints
        - osm_land_use: Land use polygons
        - osm_amenities: Points of interest

        Args:
            transformed_data: List of dictionaries in TEDI schema

        Returns:
            Dictionary with loading statistics
        """
        print("💾 Loading OpenStreetMap data into TEDI database")
        from geoalchemy2.shape import from_shape
        from shapely.geometry import shape, Point
        from shapely.ops import transform
        import pyproj

        stats = {
            'records_fetched': len(transformed_data),
            'records_added': 0,
            'records_updated': 0,
            'records_skipped': 0,
            'metadata': {
                'building': 0,
                'land_use': 0,
                'amenity': 0
            }
        }

        # Get OSM data source
        osm_source = DataSource.query.filter_by(name='OpenStreetMap').first()
        if not osm_source:
            osm_source = DataSource(
                name='OpenStreetMap',
                url='https://www.openstreetmap.org/',
                organization='OpenStreetMap Foundation',
                source_type='external',
                is_active=True
            )
            db.session.add(osm_source)
            db.session.flush()

        for record in transformed_data:
            try:
                record_type = record.get('type')
                osm_id = record.get('osm_id')
                osm_type = record.get('osm_type')
                geometry_data = record.get('geometry')

                if not osm_id or not geometry_data:
                    stats['records_skipped'] += 1
                    continue

                # Convert GeoJSON to Shapely geometry
                geom = shape(geometry_data)

                # Convert to WKB for PostGIS using GeoAlchemy2
                geom_wkb = from_shape(geom, srid=4326)

                # Calculate centroid for non-point geometries
                centroid_wkb = None
                if record_type != 'amenity':
                    centroid = geom.centroid
                    centroid_wkb = from_shape(centroid, srid=4326)

                # Route to appropriate table
                if record_type == 'building':
                    stats_update = self._load_building(
                        record, osm_source.id, geom_wkb, centroid_wkb
                    )
                    stats['building'] += 1

                elif record_type == 'land_use':
                    stats_update = self._load_land_use(
                        record, osm_source.id, geom_wkb, centroid_wkb
                    )
                    stats['land_use'] += 1

                elif record_type == 'amenity':
                    stats_update = self._load_amenity(
                        record, osm_source.id, geom_wkb
                    )
                    stats['amenity'] += 1

                else:
                    stats['records_skipped'] += 1
                    continue

                # Update stats
                stats['records_added'] += stats_update.get('added', 0)
                stats['records_updated'] += stats_update.get('updated', 0)

            except Exception as e:
                print(f"⚠️  Error loading OSM record {record.get('osm_id')}: {str(e)}")
                stats['records_skipped'] += 1
                continue

        # Commit all changes
        db.session.commit()

        print(f"✅ Loaded {stats['records_added']} new records, updated {stats['records_updated']}")
        print(f"   - Buildings: {stats['metadata'].get('building', 0)}")
        print(f"   - Land use: {stats['metadata'].get('land_use', 0)}")
        print(f"   - Amenities: {stats['metadata'].get('amenity', 0)}")

        return stats

    def _load_building(self, record: Dict, data_source_id: int, geometry, centroid) -> Dict:
        """Load building record into osm_buildings table"""
        # Check if exists
        existing = db.session.execute(
            db.text("SELECT id FROM osm_buildings WHERE osm_id = :osm_id AND osm_type = :osm_type"),
            {'osm_id': record['osm_id'], 'osm_type': record['osm_type']}
        ).first()

        if existing:
            # Update existing
            db.session.execute(
                db.text("""
                    UPDATE osm_buildings
                    SET building_type = :building_type,
                        name = :name,
                        addr_full = :addr_full,
                        geometry = ST_GeomFromEWKB(:geometry),
                        centroid = ST_GeomFromEWKB(:centroid),
                        levels = :levels,
                        area_sqm = ST_Area(ST_GeomFromEWKB(:geometry)::geography),
                        data_source_id = :data_source_id,
                        data_quality_score = 0.7,
                        updated_at = NOW()
                    WHERE osm_id = :osm_id AND osm_type = :osm_type
                """),
                {
                    'building_type': record.get('building_type'),
                    'name': record.get('name'),
                    'addr_full': record.get('addr_full'),
                    'geometry': geometry.desc,
                    'centroid': centroid.desc if centroid else None,
                    'levels': record.get('levels'),
                    'data_source_id': data_source_id,
                    'osm_id': record['osm_id'],
                    'osm_type': record['osm_type']
                }
            )
            return {'added': 0, 'updated': 1}
        else:
            # Insert new
            db.session.execute(
                db.text("""
                    INSERT INTO osm_buildings (
                        osm_id, osm_type, building_type, name, addr_full,
                        geometry, centroid, levels, area_sqm,
                        data_source_id, data_quality_score, created_at, updated_at
                    ) VALUES (
                        :osm_id, :osm_type, :building_type, :name, :addr_full,
                        ST_GeomFromEWKB(:geometry),
                        ST_GeomFromEWKB(:centroid),
                        :levels,
                        ST_Area(ST_GeomFromEWKB(:geometry)::geography),
                        :data_source_id, 0.7, NOW(), NOW()
                    )
                """),
                {
                    'osm_id': record['osm_id'],
                    'osm_type': record['osm_type'],
                    'building_type': record.get('building_type'),
                    'name': record.get('name'),
                    'addr_full': record.get('addr_full'),
                    'geometry': geometry.desc,
                    'centroid': centroid.desc if centroid else None,
                    'levels': record.get('levels'),
                    'data_source_id': data_source_id
                }
            )
            return {'added': 1, 'updated': 0}

    def _load_land_use(self, record: Dict, data_source_id: int, geometry, centroid) -> Dict:
        """Load land use record into osm_land_use table"""
        # Check if exists
        existing = db.session.execute(
            db.text("SELECT id FROM osm_land_use WHERE osm_id = :osm_id AND osm_type = :osm_type"),
            {'osm_id': record['osm_id'], 'osm_type': record['osm_type']}
        ).first()

        if existing:
            # Update existing
            db.session.execute(
                db.text("""
                    UPDATE osm_land_use
                    SET land_use_type = :land_use_type,
                        name = :name,
                        geometry = ST_GeomFromEWKB(:geometry),
                        centroid = ST_GeomFromEWKB(:centroid),
                        area_sqm = ST_Area(ST_GeomFromEWKB(:geometry)::geography),
                        data_source_id = :data_source_id,
                        data_quality_score = 0.7,
                        updated_at = NOW()
                    WHERE osm_id = :osm_id AND osm_type = :osm_type
                """),
                {
                    'land_use_type': record.get('land_use_type'),
                    'name': record.get('name'),
                    'geometry': geometry.desc,
                    'centroid': centroid.desc if centroid else None,
                    'data_source_id': data_source_id,
                    'osm_id': record['osm_id'],
                    'osm_type': record['osm_type']
                }
            )
            return {'added': 0, 'updated': 1}
        else:
            # Insert new
            db.session.execute(
                db.text("""
                    INSERT INTO osm_land_use (
                        osm_id, osm_type, land_use_type, name,
                        geometry, centroid, area_sqm,
                        data_source_id, data_quality_score, created_at, updated_at
                    ) VALUES (
                        :osm_id, :osm_type, :land_use_type, :name,
                        ST_GeomFromEWKB(:geometry),
                        ST_GeomFromEWKB(:centroid),
                        ST_Area(ST_GeomFromEWKB(:geometry)::geography),
                        :data_source_id, 0.7, NOW(), NOW()
                    )
                """),
                {
                    'osm_id': record['osm_id'],
                    'osm_type': record['osm_type'],
                    'land_use_type': record.get('land_use_type'),
                    'name': record.get('name'),
                    'geometry': geometry.desc,
                    'centroid': centroid.desc if centroid else None,
                    'data_source_id': data_source_id
                }
            )
            return {'added': 1, 'updated': 0}

    def _load_amenity(self, record: Dict, data_source_id: int, geometry) -> Dict:
        """Load amenity record into osm_amenities table"""
        # Check if exists
        existing = db.session.execute(
            db.text("SELECT id FROM osm_amenities WHERE osm_id = :osm_id AND osm_type = :osm_type"),
            {'osm_id': record['osm_id'], 'osm_type': record['osm_type']}
        ).first()

        # Determine category from amenity type
        category = self._categorize_amenity(record.get('amenity_type', ''))

        if existing:
            # Update existing
            db.session.execute(
                db.text("""
                    UPDATE osm_amenities
                    SET amenity_type = :amenity_type,
                        category = :category,
                        name = :name,
                        geometry = ST_GeomFromEWKB(:geometry),
                        data_source_id = :data_source_id,
                        data_quality_score = 0.7,
                        updated_at = NOW()
                    WHERE osm_id = :osm_id AND osm_type = :osm_type
                """),
                {
                    'amenity_type': record.get('amenity_type'),
                    'category': category,
                    'name': record.get('name'),
                    'geometry': geometry.desc,
                    'data_source_id': data_source_id,
                    'osm_id': record['osm_id'],
                    'osm_type': record['osm_type']
                }
            )
            return {'added': 0, 'updated': 1}
        else:
            # Insert new
            db.session.execute(
                db.text("""
                    INSERT INTO osm_amenities (
                        osm_id, osm_type, amenity_type, category, name,
                        geometry, data_source_id, data_quality_score,
                        created_at, updated_at
                    ) VALUES (
                        :osm_id, :osm_type, :amenity_type, :category, :name,
                        ST_GeomFromEWKB(:geometry),
                        :data_source_id, 0.7, NOW(), NOW()
                    )
                """),
                {
                    'osm_id': record['osm_id'],
                    'osm_type': record['osm_type'],
                    'amenity_type': record.get('amenity_type'),
                    'category': category,
                    'name': record.get('name'),
                    'geometry': geometry.desc,
                    'data_source_id': data_source_id
                }
            )
            return {'added': 1, 'updated': 0}

    def _categorize_amenity(self, amenity_type: str) -> str:
        """Categorize amenity type into broader categories"""
        amenity_lower = amenity_type.lower() if amenity_type else ''

        if amenity_lower in ['school', 'college', 'university', 'kindergarten', 'library']:
            return 'education'
        elif amenity_lower in ['hospital', 'clinic', 'pharmacy', 'doctors']:
            return 'health'
        elif amenity_lower in ['restaurant', 'cafe', 'fast_food', 'bar', 'pub']:
            return 'food'
        elif amenity_lower in ['bank', 'atm', 'bureau_de_change']:
            return 'financial'
        elif amenity_lower in ['marketplace', 'supermarket', 'shop']:
            return 'commercial'
        elif amenity_lower in ['police', 'fire_station', 'post_office']:
            return 'public_service'
        elif amenity_lower in ['place_of_worship', 'community_centre']:
            return 'community'
        else:
            return 'other'
