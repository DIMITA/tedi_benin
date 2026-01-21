"""
Base connector class

All data source connectors should inherit from this base class.
"""
import requests
from abc import ABC, abstractmethod
from typing import Dict, List, Any
from app import db


class BaseConnector(ABC):
    """
    Abstract base class for all data connectors

    Implements the ETL pattern:
    - Extract (fetch): Get data from external source
    - Transform: Convert to TEDI schema
    - Load: Insert into database
    """

    def __init__(self, config=None, **kwargs):
        """
        Initialize connector

        Args:
            config: DataSourceConfig instance or dict with configuration
            **kwargs: Additional configuration parameters
        """
        self.config = config or {}
        self.session = requests.Session()

        # Set timeout
        self.timeout = kwargs.get('timeout', 30)

        # Set up authentication if provided
        self._setup_auth()

    def _setup_auth(self):
        """Set up authentication for API requests"""
        if isinstance(self.config, dict):
            api_key = self.config.get('api_key')
            auth_type = self.config.get('auth_type', 'none')

            if auth_type == 'api_key' and api_key:
                # Add API key to headers
                self.session.headers.update({
                    'Authorization': f'Bearer {api_key}'
                })
            elif auth_type == 'query_param' and api_key:
                # API key will be added to URL params
                self.api_key_param = api_key
        else:
            # config is a DataSourceConfig instance
            if hasattr(self.config, 'api_key') and self.config.api_key:
                if self.config.auth_type == 'api_key':
                    self.session.headers.update({
                        'Authorization': f'Bearer {self.config.api_key}'
                    })

    @abstractmethod
    def fetch(self) -> Any:
        """
        Fetch data from external source

        This method should be implemented by each connector to retrieve
        data from its specific source (API, CSV, database, etc.)

        Returns:
            Raw data from source (format depends on source type)
        """
        pass

    @abstractmethod
    def transform(self, raw_data: Any) -> List[Dict]:
        """
        Transform raw data to TEDI schema

        This method should be implemented by each connector to convert
        the source's data format into TEDI's standardized schema.

        Args:
            raw_data: Raw data returned from fetch()

        Returns:
            List of dictionaries in TEDI schema format
        """
        pass

    @abstractmethod
    def load(self, transformed_data: List[Dict]) -> Dict:
        """
        Load transformed data into database

        This method should be implemented by each connector to insert/update
        data in the appropriate TEDI database tables.

        Args:
            transformed_data: List of dictionaries in TEDI schema

        Returns:
            Dictionary with loading statistics:
            {
                'records_fetched': int,
                'records_added': int,
                'records_updated': int,
                'records_skipped': int,
                'metadata': dict
            }
        """
        pass

    def get_json(self, url: str, params: Dict = None, headers: Dict = None) -> Any:
        """
        Make GET request and return JSON response

        Args:
            url: URL to request
            params: Query parameters
            headers: Additional headers

        Returns:
            JSON response

        Raises:
            requests.HTTPError: If request fails
        """
        response = self.session.get(
            url,
            params=params,
            headers=headers,
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()

    def get_csv(self, url: str, params: Dict = None) -> str:
        """
        Make GET request and return CSV content

        Args:
            url: URL to request
            params: Query parameters

        Returns:
            CSV content as string
        """
        response = self.session.get(
            url,
            params=params,
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.text

    def bulk_upsert(self, model_class, records: List[Dict], unique_fields: List[str]) -> Dict:
        """
        Bulk insert or update records

        Args:
            model_class: SQLAlchemy model class
            records: List of dictionaries to insert/update
            unique_fields: List of field names that uniquely identify a record

        Returns:
            Dictionary with statistics:
            {
                'records_added': int,
                'records_updated': int,
                'records_skipped': int
            }
        """
        stats = {
            'records_added': 0,
            'records_updated': 0,
            'records_skipped': 0
        }

        for record_data in records:
            # Build filter for unique fields
            filters = {field: record_data[field] for field in unique_fields if field in record_data}

            # Check if record exists
            existing = model_class.query.filter_by(**filters).first()

            if existing:
                # Update existing record
                for key, value in record_data.items():
                    if hasattr(existing, key) and key not in unique_fields:
                        setattr(existing, key, value)
                stats['records_updated'] += 1
            else:
                # Create new record
                new_record = model_class(**record_data)
                db.session.add(new_record)
                stats['records_added'] += 1

        # Commit all changes
        db.session.commit()

        return stats

    def validate_required_fields(self, data: Dict, required_fields: List[str]) -> bool:
        """
        Validate that data contains all required fields

        Args:
            data: Dictionary to validate
            required_fields: List of required field names

        Returns:
            Boolean: True if all required fields present

        Raises:
            ValueError: If required fields are missing
        """
        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

        return True

    def clean_numeric(self, value: Any, default=None) -> float:
        """
        Clean and convert numeric value

        Args:
            value: Value to convert
            default: Default value if conversion fails

        Returns:
            Float value or default
        """
        if value is None:
            return default

        try:
            # Remove common non-numeric characters
            if isinstance(value, str):
                value = value.replace(',', '').replace(' ', '').strip()

            return float(value)
        except (ValueError, TypeError):
            return default

    def clean_string(self, value: Any, default='') -> str:
        """
        Clean string value

        Args:
            value: Value to clean
            default: Default value if None

        Returns:
            Cleaned string
        """
        if value is None:
            return default

        return str(value).strip()

    def rate_limit_wait(self, calls_per_second: float = 1.0):
        """
        Implement rate limiting

        Args:
            calls_per_second: Maximum calls per second
        """
        import time
        time.sleep(1.0 / calls_per_second)
