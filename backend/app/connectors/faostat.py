"""
FAOSTAT Connector

Fetches agricultural production data from FAO's Statistics Database.

API Documentation: http://www.fao.org/faostat/en/#data
"""
from typing import List, Dict, Any
from app.connectors.base import BaseConnector
from app.models import AgriStats, Crop, Commune, DataSource
from app.utils.data_quality import MultiSourceQualityScorer


class FAOSTATConnector(BaseConnector):
    """
    Connector for FAOSTAT API

    Fetches production, yield, and area data for agricultural crops.
    """

    BASE_URL = "https://fenixservices.fao.org/faostat/api/v1/en/data"

    # FAOSTAT domain codes
    DOMAIN_PRODUCTION = "QCL"  # Crops and livestock products

    # Indicator codes
    INDICATOR_PRODUCTION = "5510"  # Production (tonnes)
    INDICATOR_YIELD = "5419"       # Yield (hg/ha)
    INDICATOR_AREA = "5312"        # Area harvested (ha)

    def __init__(self, country_code="BJ", years=None, **kwargs):
        """
        Initialize FAOSTAT connector

        Args:
            country_code: ISO2 country code (default: BJ for Benin)
            years: List of years to fetch (default: last 3 years)
            **kwargs: Additional configuration
        """
        super().__init__(**kwargs)

        self.country_code = country_code
        self.years = years or self._get_recent_years(3)

    def _get_recent_years(self, n=3):
        """Get last n years"""
        from datetime import datetime
        current_year = datetime.now().year
        return list(range(current_year - n, current_year))

    def fetch(self) -> Dict:
        """
        Fetch data from FAOSTAT API

        Returns:
            Dictionary with production, yield, and area data
        """
        print(f"📥 Fetching FAOSTAT data for {self.country_code}, years: {self.years}")

        data = {
            'production': self._fetch_indicator(self.INDICATOR_PRODUCTION),
            'yield': self._fetch_indicator(self.INDICATOR_YIELD),
            'area': self._fetch_indicator(self.INDICATOR_AREA),
        }

        return data

    def _fetch_indicator(self, indicator_code: str) -> List[Dict]:
        """
        Fetch specific indicator from FAOSTAT

        Args:
            indicator_code: FAOSTAT indicator code

        Returns:
            List of data records
        """
        params = {
            'area': self.country_code,
            'element': indicator_code,
            'years': ','.join(str(y) for y in self.years),
            'domain_code': self.DOMAIN_PRODUCTION,
            'output_type': 'objects'  # Returns JSON objects instead of CSV
        }

        try:
            response = self.get_json(
                f"{self.BASE_URL}/{self.DOMAIN_PRODUCTION}",
                params=params
            )

            return response.get('data', [])

        except Exception as e:
            print(f"⚠️  Error fetching {indicator_code}: {str(e)}")
            return []

    def transform(self, raw_data: Dict) -> List[Dict]:
        """
        Transform FAOSTAT data to TEDI schema

        Args:
            raw_data: Raw data from fetch()

        Returns:
            List of dictionaries in TEDI schema
        """
        print("🔄 Transforming FAOSTAT data to TEDI schema")

        # Group data by crop and year
        grouped_data = {}

        for indicator_type, records in raw_data.items():
            for record in records:
                crop_name = record.get('Item')
                year = int(record.get('Year', 0))
                value = self.clean_numeric(record.get('Value'))

                if not crop_name or not year or value is None:
                    continue

                key = (crop_name, year)

                if key not in grouped_data:
                    grouped_data[key] = {
                        'crop_name': crop_name,
                        'year': year,
                        'fao_item_code': record.get('ItemCode')
                    }

                # Map indicator to TEDI field
                if indicator_type == 'production':
                    grouped_data[key]['production_tonnes'] = value
                elif indicator_type == 'yield':
                    # Convert from hg/ha to t/ha
                    grouped_data[key]['yield_tonnes_per_ha'] = value / 10000
                elif indicator_type == 'area':
                    grouped_data[key]['area_harvested_ha'] = value

        # Convert to list
        transformed = list(grouped_data.values())

        print(f"✅ Transformed {len(transformed)} records")
        return transformed

    def load(self, transformed_data: List[Dict]) -> Dict:
        """
        Load transformed data into TEDI database

        Args:
            transformed_data: List of dictionaries in TEDI schema

        Returns:
            Dictionary with loading statistics
        """
        print("💾 Loading data into TEDI database")

        stats = {
            'records_fetched': len(transformed_data),
            'records_added': 0,
            'records_updated': 0,
            'records_skipped': 0,
            'metadata': {}
        }

        # Get FAOSTAT data source
        fao_source = DataSource.query.filter_by(name='FAOSTAT').first()
        if not fao_source:
            # Create if doesn't exist
            fao_source = DataSource(
                name='FAOSTAT',
                url='https://www.fao.org/faostat/',
                organization='Food and Agriculture Organization',
                source_type='external',
                is_active=True
            )
            db.session.add(fao_source)
            db.session.commit()

        # Get national-level commune (for country-level data)
        national_commune = Commune.query.filter_by(name='National').first()
        if not national_commune:
            # Use first commune as fallback
            national_commune = Commune.query.first()

        if not national_commune:
            print("⚠️  No communes found in database")
            return stats

        for record in transformed_data:
            try:
                # Find or create crop
                crop = Crop.query.filter_by(name=record['crop_name']).first()
                if not crop:
                    crop = Crop(
                        name=record['crop_name'],
                        scientific_name=record['crop_name'],
                        category='other'
                    )
                    db.session.add(crop)
                    db.session.flush()

                # Check if record exists
                existing = AgriStats.query.filter_by(
                    commune_id=national_commune.id,
                    crop_id=crop.id,
                    year=record['year'],
                    data_source_id=fao_source.id
                ).first()

                if existing:
                    # Update existing
                    for key in ['production_tonnes', 'yield_tonnes_per_ha', 'area_harvested_ha']:
                        if key in record:
                            setattr(existing, key, record[key])

                    # Update quality score (FAOSTAT is reliable)
                    existing.data_quality_score = 0.9
                    stats['records_updated'] += 1
                else:
                    # Create new
                    new_stat = AgriStats(
                        commune_id=national_commune.id,
                        crop_id=crop.id,
                        data_source_id=fao_source.id,
                        year=record['year'],
                        production_tonnes=record.get('production_tonnes'),
                        yield_tonnes_per_ha=record.get('yield_tonnes_per_ha'),
                        area_harvested_ha=record.get('area_harvested_ha'),
                        data_quality_score=0.9,  # FAOSTAT is highly reliable
                        is_estimated=False
                    )
                    db.session.add(new_stat)
                    stats['records_added'] += 1

            except Exception as e:
                print(f"⚠️  Error loading record {record.get('crop_name')}: {str(e)}")
                stats['records_skipped'] += 1
                continue

        # Commit all changes
        db.session.commit()

        print(f"✅ Loaded {stats['records_added']} new records, updated {stats['records_updated']}")
        return stats
