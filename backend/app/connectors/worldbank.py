"""
World Bank Data Connector

Fetches economic and development indicators from World Bank API.

API Documentation: https://datahelpdesk.worldbank.org/knowledgebase/articles/889392
"""
from typing import List, Dict, Any
from app.connectors.base import BaseConnector


class WorldBankConnector(BaseConnector):
    """
    Connector for World Bank Data API

    Fetches development indicators for agriculture, employment, business, etc.
    """

    BASE_URL = "https://api.worldbank.org/v2"

    # World Bank indicator codes
    INDICATORS = {
        # Agriculture
        'agriculture_value_added': 'NV.AGR.TOTL.ZS',  # Agriculture value added (% of GDP)
        'cereal_yield': 'AG.YLD.CREL.KG',             # Cereal yield (kg per hectare)
        'arable_land': 'AG.LND.ARBL.ZS',              # Arable land (% of land area)

        # Employment
        'unemployment_rate': 'SL.UEM.TOTL.ZS',        # Unemployment (% of total labor force)
        'labor_force': 'SL.TLF.TOTL.IN',              # Labor force, total
        'employment_agriculture': 'SL.AGR.EMPL.ZS',   # Employment in agriculture (%)

        # Business
        'new_business_density': 'IC.BUS.NDNS.ZS',     # New business density (per 1000 people)
        'time_to_start_business': 'IC.REG.DURS',      # Time to start a business (days)
    }

    def __init__(self, country_code="BJ", indicators=None, years=None, **kwargs):
        """
        Initialize World Bank connector

        Args:
            country_code: ISO2 country code (default: BJ for Benin)
            indicators: List of indicator codes to fetch (default: all)
            years: List of years (default: last 5 years)
            **kwargs: Additional configuration
        """
        super().__init__(**kwargs)

        self.country_code = country_code
        self.indicators = indicators or list(self.INDICATORS.values())
        self.years = years or self._get_recent_years(5)

    def _get_recent_years(self, n=5):
        """Get last n years"""
        from datetime import datetime
        current_year = datetime.now().year
        return list(range(current_year - n, current_year))

    def fetch(self) -> Dict:
        """
        Fetch data from World Bank API

        Returns:
            Dictionary with indicator data
        """
        print(f"📥 Fetching World Bank data for {self.country_code}")

        all_data = {}

        for indicator_code in self.indicators:
            try:
                data = self._fetch_indicator(indicator_code)
                all_data[indicator_code] = data
            except Exception as e:
                print(f"⚠️  Error fetching {indicator_code}: {str(e)}")
                continue

        return all_data

    def _fetch_indicator(self, indicator_code: str) -> List[Dict]:
        """
        Fetch specific indicator from World Bank

        Args:
            indicator_code: World Bank indicator code

        Returns:
            List of data records
        """
        # Build date range
        date_range = f"{min(self.years)}:{max(self.years)}"

        url = f"{self.BASE_URL}/country/{self.country_code}/indicator/{indicator_code}"

        params = {
            'format': 'json',
            'date': date_range,
            'per_page': 1000  # Get all records
        }

        response = self.get_json(url, params=params)

        # World Bank returns [metadata, data]
        if isinstance(response, list) and len(response) > 1:
            return response[1] or []

        return []

    def transform(self, raw_data: Dict) -> List[Dict]:
        """
        Transform World Bank data to TEDI schema

        Args:
            raw_data: Raw data from fetch()

        Returns:
            List of dictionaries in TEDI schema
        """
        print("🔄 Transforming World Bank data to TEDI schema")

        transformed = []

        for indicator_code, records in raw_data.items():
            # Get indicator name
            indicator_name = self._get_indicator_name(indicator_code)

            for record in records:
                year = record.get('date')
                value = record.get('value')

                if year and value is not None:
                    transformed.append({
                        'indicator_code': indicator_code,
                        'indicator_name': indicator_name,
                        'year': int(year),
                        'value': float(value),
                        'country_code': record.get('countryiso3code'),
                        'country_name': record.get('country', {}).get('value'),
                    })

        print(f"✅ Transformed {len(transformed)} records")
        return transformed

    def _get_indicator_name(self, indicator_code: str) -> str:
        """Get human-readable indicator name"""
        for name, code in self.INDICATORS.items():
            if code == indicator_code:
                return name.replace('_', ' ').title()
        return indicator_code

    def load(self, transformed_data: List[Dict]) -> Dict:
        """
        Load transformed data into TEDI database

        Note: This is a generic loader. You might want to create
        specific loaders for different indicator types (agriculture,
        employment, business) that insert into the appropriate tables.

        Args:
            transformed_data: List of dictionaries in TEDI schema

        Returns:
            Dictionary with loading statistics
        """
        print("💾 Loading World Bank data into TEDI database")

        stats = {
            'records_fetched': len(transformed_data),
            'records_added': 0,
            'records_updated': 0,
            'records_skipped': 0,
            'metadata': {}
        }

        # Group by indicator type and call appropriate loader
        by_indicator = {}
        for record in transformed_data:
            indicator = record['indicator_code']
            if indicator not in by_indicator:
                by_indicator[indicator] = []
            by_indicator[indicator].append(record)

        # Route to appropriate loaders based on indicator
        for indicator_code, records in by_indicator.items():
            if indicator_code in ['NV.AGR.TOTL.ZS', 'AG.YLD.CREL.KG', 'AG.LND.ARBL.ZS']:
                # Agriculture indicators
                loader_stats = self._load_agriculture_indicators(records)
            elif indicator_code in ['SL.UEM.TOTL.ZS', 'SL.TLF.TOTL.IN', 'SL.AGR.EMPL.ZS']:
                # Employment indicators
                loader_stats = self._load_employment_indicators(records)
            elif indicator_code in ['IC.BUS.NDNS.ZS', 'IC.REG.DURS']:
                # Business indicators
                loader_stats = self._load_business_indicators(records)
            else:
                # Skip unknown indicators
                stats['records_skipped'] += len(records)
                continue

            # Aggregate stats
            stats['records_added'] += loader_stats.get('records_added', 0)
            stats['records_updated'] += loader_stats.get('records_updated', 0)

        print(f"✅ Loaded {stats['records_added']} new records, updated {stats['records_updated']}")
        return stats

    def _load_agriculture_indicators(self, records: List[Dict]) -> Dict:
        """
        Load agriculture-related indicators into AgriStats

        World Bank provides national-level data, so we store it against
        the 'National' commune.
        """
        from app.models import AgriStats, Crop, Commune, DataSource

        stats = {'records_added': 0, 'records_updated': 0}

        # Get World Bank data source
        wb_source = DataSource.query.filter_by(name='World Bank').first()
        if not wb_source:
            wb_source = DataSource(
                name='World Bank',
                url='https://data.worldbank.org/',
                organization='World Bank Group',
                source_type='external',
                is_active=True
            )
            db.session.add(wb_source)
            db.session.flush()

        # Get national-level commune for country data
        national_commune = self._get_national_commune()
        if not national_commune:
            return stats

        for record in records:
            try:
                indicator_name = record.get('indicator_name', '')
                year = record.get('year')
                value = record.get('value')

                if not year or value is None:
                    continue

                # Map indicator to crop/category
                crop_name = self._map_indicator_to_crop(indicator_name)
                if not crop_name:
                    continue

                # Find or create crop
                crop = Crop.query.filter_by(name=crop_name).first()
                if not crop:
                    crop = Crop(
                        name=crop_name,
                        scientific_name=crop_name,
                        category='aggregate'
                    )
                    db.session.add(crop)
                    db.session.flush()

                # Check if record exists
                existing = AgriStats.query.filter_by(
                    commune_id=national_commune.id,
                    crop_id=crop.id,
                    year=year,
                    data_source_id=wb_source.id
                ).first()

                if existing:
                    # Update based on indicator type
                    if 'yield' in indicator_name.lower():
                        existing.yield_tonnes_per_ha = value / 1000  # kg to tonnes
                    elif 'area' in indicator_name.lower() or 'land' in indicator_name.lower():
                        existing.area_harvested_ha = value
                    elif 'value added' in indicator_name.lower():
                        # Store as metadata or skip
                        pass

                    existing.data_quality_score = 0.8  # World Bank is reliable
                    stats['records_updated'] += 1
                else:
                    # Create new record
                    agri_stat = AgriStats(
                        commune_id=national_commune.id,
                        crop_id=crop.id,
                        data_source_id=wb_source.id,
                        year=year,
                        data_quality_score=0.8,
                        is_estimated=False
                    )

                    # Set appropriate field based on indicator
                    if 'yield' in indicator_name.lower():
                        agri_stat.yield_tonnes_per_ha = value / 1000  # kg to tonnes
                    elif 'area' in indicator_name.lower() or 'land' in indicator_name.lower():
                        agri_stat.area_harvested_ha = value

                    db.session.add(agri_stat)
                    stats['records_added'] += 1

            except Exception as e:
                print(f"⚠️  Error loading agriculture record: {str(e)}")
                continue

        db.session.commit()
        return stats

    def _load_employment_indicators(self, records: List[Dict]) -> Dict:
        """
        Load employment-related indicators into EmploymentStats

        World Bank provides national-level data.
        """
        from app.models import EmploymentStats, JobCategory, Commune, DataSource

        stats = {'records_added': 0, 'records_updated': 0}

        # Get World Bank data source
        wb_source = DataSource.query.filter_by(name='World Bank').first()
        if not wb_source:
            wb_source = DataSource(
                name='World Bank',
                url='https://data.worldbank.org/',
                organization='World Bank Group',
                source_type='external',
                is_active=True
            )
            db.session.add(wb_source)
            db.session.flush()

        # Get national-level commune
        national_commune = self._get_national_commune()
        if not national_commune:
            return stats

        for record in records:
            try:
                indicator_name = record.get('indicator_name', '')
                year = record.get('year')
                value = record.get('value')

                if not year or value is None:
                    continue

                # Determine job category from indicator
                job_category_name = self._map_indicator_to_job_category(indicator_name)

                # Find or create job category
                job_category = JobCategory.query.filter_by(name=job_category_name).first()
                if not job_category:
                    job_category = JobCategory(
                        name=job_category_name,
                        name_fr=job_category_name,
                        sector=self._determine_sector(job_category_name)
                    )
                    db.session.add(job_category)
                    db.session.flush()

                # Check if record exists
                existing = EmploymentStats.query.filter_by(
                    commune_id=national_commune.id,
                    job_category_id=job_category.id,
                    year=year,
                    data_source_id=wb_source.id
                ).first()

                if existing:
                    # Update based on indicator type
                    if 'unemployment' in indicator_name.lower():
                        existing.unemployment_rate = value
                    elif 'labor force' in indicator_name.lower() and 'participation' not in indicator_name.lower():
                        existing.labor_force = int(value)
                    elif 'participation' in indicator_name.lower():
                        existing.participation_rate = value
                    elif 'employment' in indicator_name.lower() and 'agriculture' in indicator_name.lower():
                        # Store sectoral employment percentage
                        pass

                    existing.data_quality_score = 0.8
                    stats['records_updated'] += 1
                else:
                    # Create new record
                    emp_stat = EmploymentStats(
                        commune_id=national_commune.id,
                        job_category_id=job_category.id,
                        data_source_id=wb_source.id,
                        year=year,
                        data_quality_score=0.8,
                        is_estimated=False
                    )

                    # Set appropriate field
                    if 'unemployment' in indicator_name.lower():
                        emp_stat.unemployment_rate = value
                    elif 'labor force' in indicator_name.lower() and 'participation' not in indicator_name.lower():
                        emp_stat.labor_force = int(value)
                    elif 'participation' in indicator_name.lower():
                        emp_stat.participation_rate = value

                    db.session.add(emp_stat)
                    stats['records_added'] += 1

            except Exception as e:
                print(f"⚠️  Error loading employment record: {str(e)}")
                continue

        db.session.commit()
        return stats

    def _load_business_indicators(self, records: List[Dict]) -> Dict:
        """
        Load business-related indicators into BusinessStats

        World Bank provides national-level data.
        """
        from app.models import BusinessStats, BusinessSector, Commune, DataSource

        stats = {'records_added': 0, 'records_updated': 0}

        # Get World Bank data source
        wb_source = DataSource.query.filter_by(name='World Bank').first()
        if not wb_source:
            wb_source = DataSource(
                name='World Bank',
                url='https://data.worldbank.org/',
                organization='World Bank Group',
                source_type='external',
                is_active=True
            )
            db.session.add(wb_source)
            db.session.flush()

        # Get national-level commune
        national_commune = self._get_national_commune()
        if not national_commune:
            return stats

        # Use general "All Sectors" category for national indicators
        sector = BusinessSector.query.filter_by(name='All Sectors').first()
        if not sector:
            sector = BusinessSector(
                name='All Sectors',
                name_fr='Tous les Secteurs',
                category='aggregate'
            )
            db.session.add(sector)
            db.session.flush()

        for record in records:
            try:
                indicator_name = record.get('indicator_name', '')
                year = record.get('year')
                value = record.get('value')

                if not year or value is None:
                    continue

                # Check if record exists
                existing = BusinessStats.query.filter_by(
                    commune_id=national_commune.id,
                    sector_id=sector.id,
                    year=year,
                    data_source_id=wb_source.id
                ).first()

                if existing:
                    # Update based on indicator type
                    if 'business density' in indicator_name.lower():
                        existing.business_density_index = value
                    elif 'time to start' in indicator_name.lower():
                        # Store as metadata or in separate field
                        pass
                    elif 'cost' in indicator_name.lower():
                        # Store as metadata
                        pass

                    existing.data_quality_score = 0.8
                    stats['records_updated'] += 1
                else:
                    # Create new record
                    biz_stat = BusinessStats(
                        commune_id=national_commune.id,
                        sector_id=sector.id,
                        data_source_id=wb_source.id,
                        year=year,
                        data_quality_score=0.8,
                        is_estimated=False
                    )

                    # Set appropriate field
                    if 'business density' in indicator_name.lower():
                        biz_stat.business_density_index = value

                    db.session.add(biz_stat)
                    stats['records_added'] += 1

            except Exception as e:
                print(f"⚠️  Error loading business record: {str(e)}")
                continue

        db.session.commit()
        return stats

    def _get_national_commune(self):
        """Get or create national-level commune for country data"""
        from app.models import Commune

        national = Commune.query.filter_by(name='National').first()
        if not national:
            # Try to get first commune as fallback
            national = Commune.query.first()
            if not national:
                print("⚠️  No communes found in database")
                return None

        return national

    def _map_indicator_to_crop(self, indicator_name: str) -> str:
        """Map World Bank indicator to crop name"""
        indicator_lower = indicator_name.lower()

        if 'cereal' in indicator_lower:
            return 'Cereals (Total)'
        elif 'agriculture' in indicator_lower or 'value added' in indicator_lower:
            return 'Agriculture (Aggregate)'
        elif 'arable' in indicator_lower or 'land' in indicator_lower:
            return 'Arable Land'

        return 'General Agriculture'

    def _map_indicator_to_job_category(self, indicator_name: str) -> str:
        """Map World Bank indicator to job category"""
        indicator_lower = indicator_name.lower()

        if 'agriculture' in indicator_lower:
            return 'Agriculture'
        elif 'industry' in indicator_lower:
            return 'Industry'
        elif 'services' in indicator_lower:
            return 'Services'
        elif 'women' in indicator_lower or 'female' in indicator_lower:
            return 'Women Employment'

        return 'All Sectors'

    def _determine_sector(self, job_category_name: str) -> str:
        """Determine economic sector from job category"""
        name_lower = job_category_name.lower()

        if 'agriculture' in name_lower:
            return 'primary'
        elif 'industry' in name_lower or 'manufacturing' in name_lower:
            return 'secondary'
        elif 'services' in name_lower or 'commerce' in name_lower:
            return 'tertiary'

        return 'tertiary'
