"""
ILOSTAT Connector

Fetches employment and labor statistics from the International Labour Organization (ILO).

API Documentation: https://ilostat.ilo.org/data/api/
Note: ILOSTAT uses the same Fenix platform as FAOSTAT
"""
from typing import List, Dict, Any
from app.connectors.base import BaseConnector
from app.models import EmploymentStats, JobCategory, Commune, DataSource
from app import db


class ILOSTATConnector(BaseConnector):
    """
    Connector for ILOSTAT API

    Fetches employment indicators including unemployment, labor force participation,
    informal employment, youth employment, and sectoral employment.
    """

    BASE_URL = "https://www.ilo.org/ilostat-files/WS/public/rest/dataflow/DF_EMP_TEMP_SEX_AGE_NB/latest"

    # ILOSTAT indicator codes (simplified - actual codes may vary)
    INDICATORS = {
        'unemployment_rate': 'UNE_DEAP_SEX_AGE_RT',
        'labor_force': 'EAP_TEAP_SEX_AGE_NB',
        'employment_total': 'EMP_TEMP_SEX_AGE_NB',
        'employment_agriculture': 'EMP_TEMP_SEX_ECO_NB',
        'employment_industry': 'EMP_TEMP_SEX_ECO_NB',
        'employment_services': 'EMP_TEMP_SEX_ECO_NB',
        'informal_employment': 'EMP_NIFL_SEX_ECO_NB',
        'youth_unemployment': 'UNE_DEAP_SEX_AGE_RT',
    }

    def __init__(self, country_code="BEN", years=None, **kwargs):
        """
        Initialize ILOSTAT connector

        Args:
            country_code: ISO3 country code (default: BEN for Benin)
            years: List of years to fetch (default: last 5 years)
            **kwargs: Additional configuration
        """
        super().__init__(**kwargs)

        self.country_code = country_code
        self.years = years or self._get_recent_years(5)

    def _get_recent_years(self, n=5):
        """Get last n years"""
        from datetime import datetime
        current_year = datetime.now().year
        return list(range(current_year - n, current_year))

    def fetch(self) -> Dict:
        """
        Fetch data from ILOSTAT API

        Returns:
            Dictionary with employment indicators
        """
        print(f"📥 Fetching ILOSTAT data for {self.country_code}, years: {self.years}")

        # ILOSTAT API structure is similar to FAOSTAT (both use Fenix)
        # For now, return a structured placeholder
        # TODO: Implement actual API calls once ILOSTAT API access is confirmed

        data = {
            'unemployment': self._fetch_indicator('unemployment_rate'),
            'labor_force': self._fetch_indicator('labor_force'),
            'employment_by_sector': self._fetch_sectoral_employment(),
            'informal_employment': self._fetch_indicator('informal_employment'),
            'youth_unemployment': self._fetch_indicator('youth_unemployment'),
        }

        return data

    def _fetch_indicator(self, indicator_key: str) -> List[Dict]:
        """
        Fetch specific indicator from ILOSTAT

        Args:
            indicator_key: Key from INDICATORS dict

        Returns:
            List of data records
        """
        # TODO: Implement actual ILOSTAT API call
        # The API structure is similar to FAOSTAT (Fenix platform)

        print(f"  Fetching {indicator_key}...")

        # Placeholder implementation
        # In production, this would make actual API calls like:
        # url = f"{self.BASE_URL}/data/{indicator_code}"
        # params = {'ref_area': self.country_code, 'time': ','.join(map(str, self.years))}
        # response = self.get_json(url, params=params)

        return []

    def _fetch_sectoral_employment(self) -> List[Dict]:
        """
        Fetch employment by economic sector

        Returns:
            List of sectoral employment records
        """
        print(f"  Fetching sectoral employment...")

        # TODO: Implement actual API call for sectoral employment
        # This would fetch employment data broken down by:
        # - Agriculture, forestry, fishing
        # - Industry (manufacturing, construction)
        # - Services

        return []

    def transform(self, raw_data: Dict) -> List[Dict]:
        """
        Transform ILOSTAT data to TEDI schema

        Args:
            raw_data: Raw data from fetch()

        Returns:
            List of dictionaries in TEDI schema
        """
        print("🔄 Transforming ILOSTAT data to TEDI schema")

        transformed = []

        # Process unemployment data
        for record in raw_data.get('unemployment', []):
            transformed.append({
                'indicator_type': 'unemployment',
                'job_category': 'All Sectors',
                'year': record.get('year'),
                'unemployment_rate': self.clean_numeric(record.get('value')),
                'is_youth': record.get('age_group') == '15-24',
            })

        # Process labor force data
        for record in raw_data.get('labor_force', []):
            transformed.append({
                'indicator_type': 'labor_force',
                'job_category': 'All Sectors',
                'year': record.get('year'),
                'labor_force': self.clean_numeric(record.get('value')),
            })

        # Process sectoral employment
        for record in raw_data.get('employment_by_sector', []):
            sector = record.get('sector', 'All Sectors')
            transformed.append({
                'indicator_type': 'employment',
                'job_category': sector,
                'year': record.get('year'),
                'total_employed': self.clean_numeric(record.get('value')),
            })

        # Process informal employment
        for record in raw_data.get('informal_employment', []):
            transformed.append({
                'indicator_type': 'informal',
                'job_category': record.get('sector', 'All Sectors'),
                'year': record.get('year'),
                'informal_employed': self.clean_numeric(record.get('value')),
            })

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
        print("💾 Loading ILOSTAT data into TEDI database")

        stats = {
            'records_fetched': len(transformed_data),
            'records_added': 0,
            'records_updated': 0,
            'records_skipped': 0,
            'metadata': {}
        }

        # Get ILOSTAT data source
        ilostat_source = DataSource.query.filter_by(name='ILOSTAT').first()
        if not ilostat_source:
            ilostat_source = DataSource(
                name='ILOSTAT',
                url='https://ilostat.ilo.org/',
                organization='International Labour Organization',
                source_type='external',
                is_active=True
            )
            db.session.add(ilostat_source)
            db.session.commit()

        # Get national-level commune
        national_commune = Commune.query.filter_by(name='National').first()
        if not national_commune:
            national_commune = Commune.query.first()

        if not national_commune:
            print("⚠️  No communes found in database")
            return stats

        for record in transformed_data:
            try:
                year = record.get('year')
                job_category_name = record.get('job_category', 'All Sectors')

                if not year:
                    stats['records_skipped'] += 1
                    continue

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
                    data_source_id=ilostat_source.id
                ).first()

                if existing:
                    # Update existing record
                    if 'unemployment_rate' in record:
                        existing.unemployment_rate = record['unemployment_rate']
                    if 'labor_force' in record:
                        existing.labor_force = int(record['labor_force'])
                    if 'total_employed' in record:
                        existing.total_employed = int(record['total_employed'])
                    if 'informal_employed' in record:
                        existing.informal_employed = int(record['informal_employed'])

                    existing.data_quality_score = 0.9  # ILOSTAT is highly reliable
                    stats['records_updated'] += 1
                else:
                    # Create new record
                    new_stat = EmploymentStats(
                        commune_id=national_commune.id,
                        job_category_id=job_category.id,
                        data_source_id=ilostat_source.id,
                        year=year,
                        unemployment_rate=record.get('unemployment_rate'),
                        labor_force=int(record['labor_force']) if record.get('labor_force') else None,
                        total_employed=int(record['total_employed']) if record.get('total_employed') else None,
                        informal_employed=int(record['informal_employed']) if record.get('informal_employed') else None,
                        data_quality_score=0.9,  # ILOSTAT is highly reliable
                        is_estimated=False
                    )
                    db.session.add(new_stat)
                    stats['records_added'] += 1

            except Exception as e:
                print(f"⚠️  Error loading record {record.get('job_category')}: {str(e)}")
                stats['records_skipped'] += 1
                continue

        # Commit all changes
        db.session.commit()

        print(f"✅ Loaded {stats['records_added']} new records, updated {stats['records_updated']}")
        return stats

    def _determine_sector(self, job_category_name: str) -> str:
        """Determine economic sector from job category"""
        name_lower = job_category_name.lower()

        if 'agriculture' in name_lower or 'farming' in name_lower or 'fishing' in name_lower:
            return 'primary'
        elif 'industry' in name_lower or 'manufacturing' in name_lower or 'construction' in name_lower:
            return 'secondary'
        elif 'service' in name_lower or 'commerce' in name_lower or 'trade' in name_lower:
            return 'tertiary'

        return 'tertiary'
